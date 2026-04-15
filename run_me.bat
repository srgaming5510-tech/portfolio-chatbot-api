@echo off
TITLE Portfolio Chatbot Multi-Runner
SET BACKEND_PORT=8000
SET FRONTEND_PORT=8080

echo ====================================================
echo      SAAD'S PORTFOLIO AI CHATBOT SYSTEM
echo ====================================================
echo.

:: 1. Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment (.venv) not found!
    echo Please make sure .venv is created in this folder.
    pause
    exit /b
)

:: 2. Start Backend Server
echo [1/3] Starting Backend (FastAPI) on port %BACKEND_PORT%...
:: Using 'start' to run in a separate window so it doesn't block
start "Backend (Port %BACKEND_PORT%)" cmd /c ".venv\Scripts\python.exe chatbot.py"

:: 3. Start Frontend Server
echo [2/3] Starting Frontend (HTTP Server) on port %FRONTEND_PORT%...
start "Frontend (Port %FRONTEND_PORT%)" cmd /c ".venv\Scripts\python.exe -m http.server %FRONTEND_PORT%"

:: 4. Wait for AI Model Loading
echo [3/3] Initializing AI Models... Please wait (~15 seconds)
echo.
echo ====================================================
echo   BACKEND URL:  http://localhost:%BACKEND_PORT%
echo   FRONTEND URL: http://localhost:%FRONTEND_PORT%
echo ====================================================
echo.

:: Show a countdown in the terminal
for /l %%i in (15,-1,1) do (
   echo Loading... %%i seconds remaining
   timeout /t 1 >nul
)

:: 5. Open UI in browser
echo.
echo Opening UI in your default browser...
start http://localhost:%FRONTEND_PORT%

echo.
echo ====================================================
echo   SUCCESS: System is now running!
echo   Don't close the other two terminals.
echo ====================================================
echo.
pause
