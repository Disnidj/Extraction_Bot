@echo off
title API Extraction Bot - Automated Run
cd /d "C:\Users\mandinu.m\Documents\GitHub\Extraction_Bot"

REM Activate virtual environment
call venv\Scripts\activate.bat

echo.
echo ================================================================
echo   API Extraction Bot - Automated Run
echo   %date% %time%
echo ================================================================
echo.

REM Log execution start
echo [%date% %time%] Scheduled run started >> scheduled_extraction.log

REM Run the automated API extraction
python run_scheduled_api_extraction.py

REM Check for errors
if errorlevel 1 (
    echo.
    echo ================================================================
    echo   ERROR: Extraction failed! Check logs for details.
    echo   %date% %time%
    echo ================================================================
    echo [%date% %time%] ERROR - Extraction failed >> scheduled_extraction.log
    exit /b 1
) else (
    echo.
    echo ================================================================
    echo   Extraction completed successfully.
    echo   %date% %time%
    echo ================================================================
    echo [%date% %time%] Completed successfully >> scheduled_extraction.log
)

exit /b 0
