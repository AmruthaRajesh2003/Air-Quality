@echo off
cd /d "%~dp0"
echo Starting Air Quality IoT System...
echo.

REM Start Flask API server in a new window using Anaconda Python
start "Air Quality API Server" cmd /k "C:\Users\ramru\AppData\Local\Programs\Python\Python313\python.exe api_server.py"

REM Small delay to let the API server start first
timeout /t 2 /nobreak > NUL

REM Start Streamlit dashboard using Anaconda's streamlit
echo Launching Streamlit dashboard...
"C:\Users\ramru\AppData\Local\Programs\Python\Python313\Scripts\streamlit.exe" run app.py
pause
