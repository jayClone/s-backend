import socketio
from fastapi import FastAPI
from api.versions import router
from api.socket import sio_server

app = FastAPI()

# https://localhost:10007/api
app.include_router(router , tags=["/api"], prefix="/api")

sio_app = socketio.ASGIApp(
    socketio_server=sio_server,
    socketio_path='sockets',
    other_asgi_app=app
)
