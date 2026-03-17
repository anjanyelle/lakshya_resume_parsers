@echo off
echo Starting Redis - Simple Method...
echo.

echo 1. Checking if Redis exists...
if exist "redis-server.exe" (
    echo ✅ Redis found! Starting server...
    start /B redis-server.exe
    echo ✅ Redis server started on port 6379
    echo 🎯 You can now upload resumes!
    goto :end
)

echo 2. Redis not found - please install manually
echo 💡 Download Redis from: https://github.com/microsoftarchive/redis/releases
echo 💡 Extract and run redis-server.exe
echo 💡 Or use Docker: docker run -d -p 6379:6379 redis:latest

:end
echo.
echo Press any key to continue...
pause
