@echo off
REM ===================================================================
REM  Bat Redis Server (De tai 06 - Cache-Aside + Session Management)
REM  Dung khi may chua tu dong chay Redis (sau khi khoi dong lai may)
REM ===================================================================
cd /d D:\Redis
start "Redis Server" /min redis-server.exe redis.conf
echo.
echo  Redis dang khoi dong tren port 6379 ...
timeout /t 3 >nul
D:\Redis\redis-cli.exe ping
echo.
echo  Neu thay PONG -> Redis da san sang.
echo  Mo Redis Insight va ket noi localhost:6379 de xem giao dien.
pause
