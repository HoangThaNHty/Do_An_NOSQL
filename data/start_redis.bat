@echo off
REM ===================================================================
REM  Bat Redis Server (De tai 06)
REM  Redis 8.10.2 portable tai ve may, luu tai D:\Redis
REM
REM  Cach dung:  data\start_redis.bat
REM  Kiem tra:   D:\Redis\redis-cli.exe ping   -> phai tra ve PONG
REM ===================================================================
cd /d D:\Redis

REM Neu Redis da chay thi khong can bat lai
"D:\Redis\redis-cli.exe" ping >nul 2>&1
if not errorlevel 1 (
    echo.
    echo  Redis dang chay san ^(PONG^). Khong can bat lai.
    goto :ketthuc
)

echo.
echo  Dang bat Redis Server...
powershell -NoProfile -Command "Start-Process -FilePath 'D:\Redis\redis-server.exe' -ArgumentList 'redis.conf' -WorkingDirectory 'D:\Redis' -WindowStyle Hidden"
ping -n 4 127.0.0.1 >nul

:D:\Redis\redis-cli.exe ping
if errorlevel 1 (
    echo  [!] Redis chua len. Thu chay: D:\Redis\redis-server.exe redis.conf
) else (
    echo  [OK] Redis da chay tren port 6379.
)

:ketthuc
echo.
endlocal
