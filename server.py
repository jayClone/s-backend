from fastapi.responses import JSONResponse
import uvicorn
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.extensions.ban import ipBan
from bind import sio_app
from api.models import init_models
from api.db import lifespan
import httpx
from dotenv import load_dotenv
import os

load_dotenv()

MODE = os.getenv("MODE", "prod").lower()

allow_origins = ["*"]

# Start DB Process and Model Loading...
app = FastAPI(lifespan=lifespan)
# app = FastAPI()

# Mount the static files
app.mount("/static", StaticFiles(directory='static'), name="static")
app.mount('/', app=sio_app)

logger = logging.getLogger("uvicorn.error")

class LogExceptionsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Exception occurred: {e}", exc_info=True)
            return PlainTextResponse(str(e), status_code=500)

app.add_middleware(LogExceptionsMiddleware)

if MODE != "dev":
    class NotFoundMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            response = await call_next(request)

            # Check if the response is a 404
            if response.status_code == 404:

                exempt_paths = [
                    "/favicon.ico",
                    "/robots.txt",
                ]

                # If the request path contains any exempt path, do not ban
                should_exempt = any(
                    exempt_path in request.url.path
                    for exempt_path in exempt_paths
                )

                if should_exempt:
                    # Log but don't ban for exempt paths
                    real_ip = request.headers.get("x-real-ip", "unknown")
                    logger.info(f"404 on exempt path (no ban): {request.url.path} | Real-IP={real_ip}")
                    return response

                # Capture client info
                real_ip = request.headers.get("x-real-ip", "unknown")
                forwarded_for = request.headers.get("x-forwarded-for", "unknown")
                user_agent = request.headers.get("user-agent", "unknown")

                # Log the 404 attempt
                logger.warning(f"404 Not Found (Middleware): {request.url.path} | Real-IP={real_ip}, X-Forwarded-For={forwarded_for}, User-Agent={user_agent}")
                
                # Send Discord notification
                webhook_url = os.getenv("DISCORD_SECURITY_WEBHOOK_URL")
                if webhook_url:
                    data = {
                        "content": (
                            "┌──────────────────────────────────────────────\n"
                            "│  🚨 Undefined Route Access Attempt! Ip Banned 🚨 \n"
                            "├───────────────┬──────────────────────────────\n"
                            f"│ `Route         `   │ `{request.url.path:<24}`\n"
                            f"│ `Real-IP       `   │ `{real_ip:<24}`\n"
                            f"│ `X-Forwarded   `   │ `{forwarded_for:<24}`\n"
                            f"│ `User-Agent    `   │ `{user_agent[:24]:<24}`\n"
                            "├──────────────────────────────────────────────\n"
                            f"```{real_ip}```"
                            "└──────────────────────────────────────────────"
                        )
                    }
                    try:
                        if real_ip != "unknown":
                            ipBan(real_ip)
                        async with httpx.AsyncClient() as client:
                            await client.post(webhook_url, json=data)
                    except Exception as discord_exc:
                        logger.error(f"Failed to send Discord webhook: {discord_exc}")

            return response

    # Add this middleware right after LogExceptionsMiddleware
    app.add_middleware(NotFoundMiddleware)

    @app.middleware("http")
    async def block_non_browser_user_agents(request: Request, call_next):
        try:
            user_agent = request.headers.get("user-agent", "").lower()
            custom_token = request.headers.get("x-useless", "")

            # Block specific dangerous/unwanted user agents
            if "keydrop.io" in user_agent or "zgrab" in user_agent:
                real_ip = request.headers.get("x-real-ip", "unknown")
                forwarded_for = request.headers.get("x-forwarded-for", "unknown")

                # Log the blocked user agent attempt
                logger.warning(f"Blocked malicious user agent: {user_agent} | Real-IP={real_ip}, X-Forwarded-For={forwarded_for}")

                # Send Discord notification for blocked user agent
                webhook_url = os.getenv("DISCORD_SECURITY_WEBHOOK_URL")
                if webhook_url:
                    data = {
                        "content": (
                            "┌──────────────────────────────────────────────\n"
                            "│  🚫 Banned Malicious User Agent! 🚫 \n"
                            "├───────────────┬──────────────────────────────\n"
                            f"│ `Route         `   │ `{request.url.path}`\n"
                            f"│ `User-Agent    `   │ `{user_agent}`\n"
                            f"│ `Real-IP       `   │ `{real_ip}`\n"
                            f"│ `X-Forwarded   `   │ `{forwarded_for}`\n"
                            "└──────────────────────────────────────────────"
                        )
                    }
                    try:
                        ipBan(real_ip)
                        async with httpx.AsyncClient() as client:
                            await client.post(webhook_url, json=data)
                    except Exception as discord_exc:
                        logger.error(f"Failed to send Discord webhook: {discord_exc}")
                return JSONResponse(
                    content={"detail": "Access denied"},
                    status_code=403
                )

            # Check if the user agent is a known browser or mobile agent
            allowed_agents = ["mozilla", "chrome", "safari", "firefox", "edge", "opera", "applewebkit", "trident", "msie", "mobile"]
            if not any(agent in user_agent for agent in allowed_agents):
                return JSONResponse(
                    content={"detail": "Access denied"},
                    status_code=403
                )

            response = await call_next(request)
            return response
        except Exception as e:
            print(f"Middleware Error: {e}")
            return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def start_server():
    init_models()
    uvicorn.run("server:app", port=10001, reload=(MODE == "dev"), host="0.0.0.0")

if __name__ == '__main__':
    start_server()