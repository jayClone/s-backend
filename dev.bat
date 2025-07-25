@echo off
REM Check if network exists
docker network inspect shared_db_net >nul 2>&1
if errorlevel 1 (
    echo Creating shared network...
    docker network create shared_db_net
) else (
    echo Shared network already exists
)

docker compose -f compose.yaml -f compose.watch.yaml watch