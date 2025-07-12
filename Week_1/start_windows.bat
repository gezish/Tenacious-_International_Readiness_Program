@echo off
echo Starting AI Shopping Assistant MVP...
echo.
echo Starting Mock E-commerce APIs...
start "Mock APIs" python mock_apis.py
timeout /t 3 /nobreak >nul
echo.
echo Starting Shopping Assistant Web Interface...
start "Shopping Assistant" python web_interface.py
timeout /t 3 /nobreak >nul
echo.
echo Opening web interface...
start http://localhost:8016
echo.
echo Shopping Assistant is starting up!
echo Mock APIs: http://localhost:8015
echo Web Interface: http://localhost:8016
echo.
pause
