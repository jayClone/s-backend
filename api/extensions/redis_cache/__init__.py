import uuid
from typing import Any, Optional
from fastapi import HTTPException
from api.db import redis_client
import redis.asyncio as redis

class Cache:
    @staticmethod
    async def store_with_unique_key(value: Any) -> str:
        """Store a value with a unique key and 15-minute expiration time"""
        try:
            try:
                await redis_client.ping()
            except redis.ConnectionError:
                raise HTTPException(
                    status_code=503,
                    detail="Redis service unavailable"
                )

            unique_key = str(uuid.uuid4())
            await redis_client.setex(unique_key, 900, value)  # 900 seconds = 15 minutes
            return unique_key

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to store value: {str(e)}"
            )

    @staticmethod
    async def setValue(key: str, value: Any, ttl: int = 900) -> None:
        """Set a value with a key and optional time-to-live (default 15 minutes)"""
        try:
            try:
                await redis_client.ping()
            except redis.ConnectionError:
                raise HTTPException(
                    status_code=503,
                    detail="Redis service unavailable"
                )

            await redis_client.setex(key, ttl, value)

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to set value: {str(e)}"
            )

    @staticmethod
    async def getValue(key: str) -> Optional[Any]:
        """Retrieve a value using its key and delete it after access"""
        try:
            try:
                await redis_client.ping()
            except redis.ConnectionError:
                raise HTTPException(
                    status_code=503,
                    detail="Redis service unavailable"
                )

            value = await redis_client.get(key)
            if value is None:
                raise HTTPException(
                    status_code=404,
                    detail="Key not found or expired"
                )

            # Convert value to string if it's bytes
            if isinstance(value, bytes):
                value = value.decode('utf-8')

            return value

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve value: {str(e)}"
            )

    @staticmethod
    async def deleteValue(key: str) -> None:
        """Delete a value using its key"""
        try:
            try:
                await redis_client.ping()
            except redis.ConnectionError:
                raise HTTPException(
                    status_code=503,
                    detail="Redis service unavailable"
                )

            result = await redis_client.delete(key)
            if result == 0:
                raise HTTPException(
                    status_code=404,
                    detail="Key not found"
                )

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete value: {str(e)}"
            )

    @staticmethod
    async def getValueDelete(key: str) -> Optional[Any]:
        """Retrieve a value using its key and delete it after access"""
        try:
            try:
                await redis_client.ping()
            except redis.ConnectionError:
                raise HTTPException(
                    status_code=503,
                    detail="Redis service unavailable"
                )

            value = await redis_client.get(key)
            if value is None:
                raise HTTPException(
                    status_code=404,
                    detail="Key not found or expired"
                )

            # Convert value to string if it's bytes
            if isinstance(value, bytes):
                value = value.decode('utf-8')

            # Delete the key after successful retrieval
            await redis_client.delete(key)

            return value

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve value: {str(e)}"
            )

    @staticmethod
    async def getKeysByPattern(pattern: str) -> list:
        """Get all keys matching a pattern"""
        try:
            try:
                await redis_client.ping()
            except redis.ConnectionError:
                raise HTTPException(
                    status_code=503,
                    detail="Redis service unavailable"
                )

            # Get keys matching the pattern
            keys = await redis_client.keys(pattern)
            
            # Convert bytes to strings if needed
            result = []
            for key in keys:
                if isinstance(key, bytes):
                    result.append(key.decode('utf-8'))
                else:
                    result.append(key)
                    
            return result

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get keys: {str(e)}"
            )