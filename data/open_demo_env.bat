@echo off
REM ===================================================================
REM  MO TOAN BO MOI TRUONG DEMO (De tai 06)
REM  1 click se: bat MongoDB - bat Redis - mo MongoDB Compass
REM                 - mo Redis Insight - mo web + bang dieu khien cache
REM
REM  Cach dung:  data\open_demo_env.bat
REM ===================================================================
setlocal
cd /d "%~dp0.."
title Demo moi truong - De tai 06

echo.
echo  ============================================================
echo    De tai 06 - Cache-Aside ^& Session Management
echo    Mo moi truong demo
echo  ============================================================
echo.

REM ---------- 1. MongoDB ----------
echo [1/5] Kiem tra MongoDB...
sc query MongoDB | find "RUNNING" >nul
if errorlevel 1 (
    echo      MongoDB dang dung - khoi dong...
    net start MongoDB >nul 2>&1
    timeout /t 3 >nul
) else (
    echo      MongoDB: Running ^(OK^)
)

REM ---------- 2. Redis ----------
echo [2/5] Kiem tra Redis...
"D:\Redis\redis-cli.exe" ping >nul 2>&1
if errorlevel 1 (
    echo      Redis dang dung - khoi dong...
    start "Redis Server" /min "D:\Redis\redis-server.exe" "D:\Redis\redis.conf"
    timeout /t 3 >nul
) else (
    echo      Redis: PONG ^(OK^)
)

REM ---------- 3. MongoDB Compass ----------
echo [3/5] Mo MongoDB Compass...
if exist "C:\Users\ASUS\AppData\Local\MongoDBCompass\MongoDBCompass.exe" (
    start "MongoDB Compass" "C:\Users\ASUS\AppData\Local\MongoDBCompass\MongoDBCompass.exe"
    echo      OK
) else (
    echo      [!] Khong tim thay - mo tu Start Menu: MongoDB Compass
)

REM ---------- 4. Redis Insight ----------
echo [4/5] Mo Redis Insight...
if exist "C:\Users\ASUS\AppData\Local\Programs\Redis Insight\Redis Insight.exe" (
    start "Redis Insight" "C:\Users\ASUS\AppData\Local\Programs\Redis Insight\Redis Insight.exe"
    echo      OK
) else (
    echo      [!] Khong tim thay - mo tu Start Menu: Redis Insight
)

REM ---------- 5. Trinh duyet ----------
echo [5/5] Mo trinh duyet...
start "" "http://127.0.0.1:5000/"
timeout /t 1 >nul
start "" "http://127.0.0.1:5000/admin/cache"

echo.
echo  ============================================================
echo   Da mo xong. Neu web bao loi, chay:
echo       .venv\Scripts\python app.py
echo.
echo   MongoDB Compass : ket noi  mongodb://127.0.0.1:27017
echo   Redis Insight   : ket noi  127.0.0.1 : 6379  (database 0)
echo  ============================================================
echo.
endlocal
