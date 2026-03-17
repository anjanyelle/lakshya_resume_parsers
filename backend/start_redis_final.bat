@echo off
echo Starting Redis Server...
echo.

REM Try to find redis-server in common locations
if exist "C:\Program Files\Redis\redis-server.exe" (
    echo Found Redis in C:\Program Files\Redis\
    cd /d "C:\Program Files\Redis"
    start /B redis-server.exe
    echo Redis server started from C:\Program Files\Redis\
    goto :redis_running
)

if exist "C:\Program Files (x86)\Redis\redis-server.exe" (
    echo Found Redis in C:\Program Files (x86)\Redis\
    cd /d "C:\Program Files (x86)\Redis"
    start /B redis-server.exe
    echo Redis server started from C:\Program Files (x86)\Redis\
    goto :redis_running
)

if exist ".\redis\redis-server.exe" (
    echo Found Redis in .\redis\
    cd /d ".\redis"
    start /B redis-server.exe
    echo Redis server started from .\redis\
    goto :redis_running
)

echo Redis not found in common locations
echo Please install Redis manually
echo.
echo Download from: https://github.com/microsoftarchive/redis/releases
echo.

:redis_running
echo.
echo Redis server should be running on port 6379
echo.
echo Now upload resumes and check: python check_json_storage.py
echo.
pause
