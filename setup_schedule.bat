@echo off
title Setup Scheduled Task - API Extraction Bot
cd /d "%~dp0"

echo.
echo ================================================================
echo   Setup: Weekly Scheduled Task
echo   API Extraction Bot - Every Monday at 07:00 AM
echo ================================================================
echo.
echo This will create a Windows Scheduled Task that runs
echo the API Extraction Bot every Monday at 07:00 AM.
echo.
echo Task details:
echo   Name     : API_Extraction_Weekly
echo   Schedule : Every Monday at 07:00 AM
echo   Script   : %~dp0run_scheduled_extraction.bat
echo.

choice /c YN /m "Do you want to create this scheduled task? (Y/N)"
if errorlevel 2 (
    echo Cancelled.
    exit /b 0
)

echo.
echo Creating scheduled task...

schtasks /create ^
    /tn "API_Extraction_Weekly" ^
    /tr "%~dp0run_scheduled_extraction.bat" ^
    /sc weekly ^
    /d MON ^
    /st 07:00 ^
    /rl HIGHEST ^
    /f

if errorlevel 1 (
    echo.
    echo ================================================================
    echo   ERROR: Failed to create scheduled task.
    echo   Try running this file as Administrator.
    echo ================================================================
    pause
    exit /b 1
)

echo.
echo ================================================================
echo   Scheduled task created successfully!
echo.
echo   Task Name : API_Extraction_Weekly
echo   Schedule  : Every Monday at 07:00 AM
echo.
echo   Useful commands:
echo   - View task   : schtasks /query /tn "API_Extraction_Weekly"
echo   - Run now     : schtasks /run /tn "API_Extraction_Weekly"
echo   - Delete task : schtasks /delete /tn "API_Extraction_Weekly" /f
echo ================================================================
echo.
pause
