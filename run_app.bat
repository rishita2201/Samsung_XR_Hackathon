@echo off
setlocal
echo ====================================================================
echo  MOMENTIQ - Intelligent First-Person Video Understanding & Highlights
echo  Samsung XR Hackathon 2026 - Track 4
echo ====================================================================
echo.

set PYTHON_CMD=python
if exist "venv\Scripts\python.exe" (
    set PYTHON_CMD="venv\Scripts\python.exe"
)

echo Starting MOMENTIQ unified server (API + Frontend) on port 8000...
echo Open your browser to: http://127.0.0.1:8000
echo.

cd backend
..\%PYTHON_CMD% -m uvicorn app.main:app --host 127.0.0.1 --port 8000
cd ..
pause

