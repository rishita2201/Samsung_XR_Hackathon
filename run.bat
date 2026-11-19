@echo off
REM Official Samsung Track 4 Run Script for Windows
REM Usage: run.bat <video.mp4> <out.json>
setlocal enabledelayedexpansion

if "%~2"=="" (
    echo Usage: run.bat ^<video.mp4^> ^<out.json^>
    exit /b 2
)

set DIR=%~dp0
call "%DIR%TEAM_ID\run.bat" "%~1" "%~2"
