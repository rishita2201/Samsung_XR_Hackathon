@echo off
REM Official Samsung XR Hackathon Track 4 Windows Runner
REM Usage: run.bat <video.mp4> <out.json>
setlocal enabledelayedexpansion

if "%~2"=="" (
    echo Usage: run.bat ^<video.mp4^> ^<out.json^>
    exit /b 2
)

set DIR=%~dp0
set PYTHON_CMD=python

where python >nul 2>&1
if %errorlevel% neq 0 (
    if exist "%DIR%..\venv\Scripts\python.exe" (
        set PYTHON_CMD="%DIR%..\venv\Scripts\python.exe"
    ) else (
        echo ERROR: Python executable not found in PATH.
        exit /b 1
    )
)

%PYTHON_CMD% "%DIR%code\run_pipeline.py" --video "%~1" --out "%~2" --weights "%DIR%weights" --classes "%DIR%weights\supported_classes.json"
