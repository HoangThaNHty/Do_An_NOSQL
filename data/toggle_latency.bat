@echo off
REM ===================================================================
REM  Bat / Tat che do MO PHONG DO TRE MANG (dung cho buoc demo trinh bay)
REM
REM  Cach dung:
REM      scripts\toggle_latency.bat on    -> doc DB goc cham hon ~200ms
REM      scripts\toggle_latency.bat off   -> do hieu nang that
REM
REM  Ly do: khi MongoDB nam o may khac, moi lan doc deu co do tre mang.
REM  Che do nay giu nguyen logic Cache-Aside, chi mo phong them do tre mang
REM  vao thoi diem doc DB goc (services/article_service.py).
REM ===================================================================
setlocal

if /I "%~1"=="on"  goto ON
if /I "%~1"=="off" goto OFF
echo Dung cach: scripts\toggle_latency.bat [on^|off]
exit /b 1

:ON
set NEW=200
set MSG=BAT - doc DB goc se cham ~200ms (nhu khi MongoDB o may khac)
goto APPLY

:OFF
set NEW=0
set MSG=TAT - do hieu nang that
goto APPLY

:APPLY
powershell -NoProfile -Command "$p='%~dp0..\.env'; $c=Get-Content $p -Raw; $c=[regex]::Replace($c,'SIMULATED_DB_LATENCY_MS=\d+','SIMULATED_DB_LATENCY_MS=%NEW%'); Set-Content -Path $p -Value $c -Encoding UTF8"
echo.
echo  %MSG%
echo  (Can restart app.py de ap dung thay doi)
endlocal
