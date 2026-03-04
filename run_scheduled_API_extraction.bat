@echo off
title Multi-Broker API Extraction Bot - Automated Run
cd /d "C:\Users\mandinu.m\Documents\GitHub\Extraction_Bot"

REM Activate virtual environment
call venv\Scripts\activate.bat

echo.
echo ================================================================
echo   Multi-Broker API Extraction Bot - Automated Run
echo   %date% %time%
echo ================================================================
echo.

REM Log execution start
echo [%date% %time%] Scheduled multi-broker run started >> scheduled_extraction.log

REM Run the automated multi-broker API extraction
REM This will extract ALL available portals for ALL active brokers
python run_scheduled_api_extraction.py

REM Check for errors
if errorlevel 1 (
    echo.
    echo ================================================================
    echo   ERROR: Multi-Broker Extraction failed! Check logs for details.
    echo   %date% %time%
    echo ================================================================
    echo [%date% %time%] ERROR - Multi-broker extraction failed >> scheduled_extraction.log
    exit /b 1
) else (
    echo.
    echo ================================================================
    echo   Multi-Broker Extraction completed successfully.
    echo   %date% %time%
    echo ================================================================
    echo [%date% %time%] Completed successfully >> scheduled_extraction.log
)

exit /b 0
