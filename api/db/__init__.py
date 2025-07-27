import os
from pymongo import MongoClient
import ssl
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
import asyncio
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from api.extensions.helper import service_name_identifier, custom_callback

# Initialize variables as None
client = None
db = None
session = None
redis_client = None

isMySqlAvailable = False
isMongoDBAvailable = False



load_dotenv()

# Redis Configuration
REDIS_URL = os.getenv('REDIS_HOST', 'redis://redis:6379')

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application"""
    
    try:
        # Initialize Redis connection
        redis_client_base = redis.from_url(
            REDIS_URL,
            encoding="utf8",
            decode_responses=True,
            socket_connect_timeout=5
        )

        # Initialize FastAPI Limiter
        await FastAPILimiter.init(
            redis=redis_client_base,
            identifier=service_name_identifier,
            http_callback=custom_callback,
        )

        yield

    except Exception as e:
        print(f"Failed to initialize Redis: {e}")
        if redis_client_base:
            await redis_client_base.close()
        raise
    finally:
        if redis_client_base:
            await redis_client_base.close()
            await FastAPILimiter.close()

def initRedis():
    global redis_client

    redis_client = redis.Redis(host="redis", port=6379, db=0)
    print("Initializing Redis...")
    # Check if Redis is available
    try:
        print("Redis connection established successfully")
    except redis.ConnectionError:
        print("Redis connection failed")
        raise
    except Exception as e:
        print(f"Error initializing Redis: {e}")

def init_db():
    """
    Initialize database connections based on the DB_TYPE environment variable.
    Supports MongoDB, MySQL, or both databases simultaneously.
    """
    print("\n" * 20) 
    print("*" * 50)
    print("*     Welcome to Farm Stack Backend Template     *")
    print("*" * 50)
    print("Initializing DB...")

    global client, db, session, isMySqlAvailable, isMongoDBAvailable

    # initialize Redis
    initRedis()

    DB_TYPE = os.getenv('DB_TYPE', 'mongodb')  # Default to MongoDB if not set
    print(f"Database type: {DB_TYPE}")

    if DB_TYPE in ['mongodb', 'both']:
        try:
            MONGO_SERVER_URL = os.getenv('MONGO_SERVER_URL')
            MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')

            if not MONGO_DB_NAME:
                raise ValueError("MONGO_DB_NAME environment variable is not set.")

            # Use default MongoClient for Atlas SRV URI
            client = MongoClient(MONGO_SERVER_URL)
            client.admin.command('ping')
            db = client[MONGO_DB_NAME]

            isMongoDBAvailable = True
            print("MongoDB connection established successfully")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            isMongoDBAvailable = False
            client = None
            db = None

    if DB_TYPE in ['mysql', 'both']:
        try:
            MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
            MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
            MYSQL_USER = os.getenv('MYSQL_USER', 'user')
            MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'password')
            MYSQL_DB_NAME = os.getenv('MYSQL_DB_NAME', 'dbname')

            MYSQL_SERVER_URL = f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB_NAME}"
            engine = create_engine(MYSQL_SERVER_URL)
            Session = sessionmaker(bind=engine)
            session = Session()
            isMySqlAvailable = True
            print("MySQL connection established successfully")
        except Exception as e:
            print(f"Error connecting to MySQL: {e}")
            isMySqlAvailable = False

    if DB_TYPE not in ['mongodb', 'mysql', 'both']:
        raise ValueError("Unsupported DB_TYPE. Please set DB_TYPE to 'mongodb', 'mysql', or 'both'.")

    # Return the database connection objects
init_db()