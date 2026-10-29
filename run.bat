@echo off
setlocal

title MediRoute - Emergency Vehicle Dispatch Optimizer

echo =====================================================================
echo    MediRoute - Intelligent Emergency Vehicle Dispatch Optimizer
echo               Design and Analysis of Algorithms (DAA)
echo =====================================================================
echo.

cd /d "%~dp0"

:: 1. Check for Python installation
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not found on your system PATH.
    echo Please install Python 3.11 or 3.12 from https://www.python.org/
    echo and ensure "Add Python to PATH" is checked during installation.
    echo.
    pause
    exit /b 1
)

echo [OK] Python detected:
python --version
echo.

:: 2. Activate Virtual Environment if present
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment: .venv
    call .venv\Scripts\activate.bat
) else if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment: venv
    call venv\Scripts\activate.bat
)

echo =====================================================================
echo   Menu Options:
echo   [1] Launch MediRoute Dashboard (Default - opens browser automatically)
echo   [2] Run Automated Test Suite (pytest - 24 unit tests)
echo   [3] Install / Update Dependencies (requirements.txt)
echo   [4] Exit
echo =====================================================================
echo.

choice /C 1234 /T 4 /D 1 /M "Select an option [Auto-launching in 4 seconds]"

if errorlevel 4 goto EXIT_SCRIPT
if errorlevel 3 goto INSTALL_DEPS
if errorlevel 2 goto RUN_TESTS
if errorlevel 1 goto RUN_APP

:INSTALL_DEPS
echo.
echo [INFO] Installing required dependencies from requirements.txt...
python -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Dependency installation encountered errors.
    pause
    exit /b 1
)
echo [OK] Dependencies installed successfully.
echo.
goto RUN_APP

:RUN_TESTS
echo.
echo =====================================================================
echo   Running Pytest Suite (24 Algorithm & Simulation Tests)
echo =====================================================================
echo.
python -m pytest tests -v
echo.
echo Test run complete.
pause
exit /b 0

:RUN_APP
echo.
echo =====================================================================
echo   Starting MediRoute Emergency Dispatch Dashboard...
echo   Opening browser at: http://localhost:8501
echo.
echo   NOTE: Keep this console window open in the background!
echo         The web app runs as long as this window is open.
echo         To stop the server, press Ctrl+C in this window.
echo =====================================================================
echo.

:: Open default browser after 2 seconds
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://localhost:8501"

:: Start Streamlit server on Overview_Dashboard.py
python -m streamlit run Overview_Dashboard.py --server.headless false

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Application server stopped unexpectedly.
    pause
    exit /b 1
)

:EXIT_SCRIPT
exit /b 0
