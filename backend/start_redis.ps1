# PowerShell script to start Redis
Write-Host "🔍 Starting Redis Server..." -ForegroundColor Green

# Check if Redis is already running
try {
    $redisProcess = Get-Process -Name "redis-server" -ErrorAction SilentlyContinue
    if ($redisProcess) {
        Write-Host "✅ Redis is already running (PID: $($redisProcess.Id))" -ForegroundColor Yellow
        Write-Host "🎯 You can now upload resumes!" -ForegroundColor Green
        exit 0
    }
} catch {
    # Redis not running, try to start it
    Write-Host "📥 Redis not found. Attempting to start..." -ForegroundColor Yellow
    
    # Try common Redis locations
    $redisPaths = @(
        "redis-server.exe",
        "C:\Program Files\Redis\redis-server.exe",
        "C:\Program Files (x86)\Redis\redis-server.exe",
        ".\redis\redis-server.exe"
    )
    
    $redisFound = $false
    foreach ($path in $redisPaths) {
        if (Test-Path $path) {
            Write-Host "✅ Found Redis at: $path" -ForegroundColor Green
            try {
                Start-Process -FilePath $path -WindowStyle Hidden
                Write-Host "🚀 Starting Redis server..." -ForegroundColor Green
                Start-Sleep -Seconds 3
                
                # Check if it started successfully
                $redisProcess = Get-Process -Name "redis-server" -ErrorAction SilentlyContinue
                if ($redisProcess) {
                    Write-Host "✅ Redis server started successfully!" -ForegroundColor Green
                    Write-Host "🎯 Redis running on port 6379" -ForegroundColor Green
                    Write-Host "💡 Now upload resumes and check processing!" -ForegroundColor Cyan
                    $redisFound = $true
                    break
                }
            } catch {
                Write-Host "❌ Failed to start Redis from: $path" -ForegroundColor Red
            }
        }
    }
    
    if (-not $redisFound) {
        Write-Host "❌ Redis not found in any location!" -ForegroundColor Red
        Write-Host "💡 Please install Redis from: https://github.com/microsoftarchive/redis/releases" -ForegroundColor Yellow
        Write-Host "💡 Or install with: choco install redis-64" -ForegroundColor Yellow
        Write-Host "💡 Or use Docker: docker run -d -p 6379:6379 redis:latest" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ Error: $($_)" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Script completed!" -ForegroundColor Green
