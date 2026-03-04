@echo off
REM ══════════════════════════════════════════════════════════════════════════
REM Medical Insurance Portal API Extraction Bot - Scheduled Run
REM ══════════════════════════════════════════════════════════════════════════
REM This batch file runs the API extraction for ALL active brokers
REM Configured for Windows Task Scheduler - runs every Monday at 6:00 AM
REM ══════════════════════════════════════════════════════════════════════════

TITLE Medical API Extraction - Scheduled Run

ECHO ════════════════════════════════════════════════════════════════════════════
ECHO Medical Insurance Portal API Extraction Bot
ECHO Scheduled Run - %DATE% %TIME%
ECHO ════════════════════════════════════════════════════════════════════════════
ECHO.

REM Set Python path (adjust to your virtual environment)
SET PYTHON_PATH=%~dp0venv\Scripts\python.exe

REM Set project directory (current directory where batch file is located)
SET PROJECT_DIR=%~dp0

REM Navigate to project directory
cd /d "%PROJECT_DIR%"

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Log file with date
SET LOG_FILE=logs\scheduled_run_%DATE:~-4,4%%DATE:~-10,2%%DATE:~-7,2%.log

ECHO Starting extraction... >> "%LOG_FILE%"
ECHO ════════════════════════════════════════════════════════════════════════════ >> "%LOG_FILE%"
ECHO Date: %DATE% %TIME% >> "%LOG_FILE%"
ECHO ════════════════════════════════════════════════════════════════════════════ >> "%LOG_FILE%"
ECHO. >> "%LOG_FILE%"

REM Run extraction for ALL active brokers (defined in broker_config.py)
REM --mode=api: Use API extraction mode
REM --brokers=all: Process all enabled brokers from broker_config.py
REM --scheduled: Skip confirmation prompts (automated run)
"%PYTHON_PATH%" main.py --mode=api --brokers=all --scheduled >> "%LOG_FILE%" 2>&1

REM Check exit code
IF %ERRORLEVEL% EQU 0 (
    ECHO ════════════════════════════════════════════════════════════════════════════ >> "%LOG_FILE%"
    ECHO ✅ Extraction completed successfully >> "%LOG_FILE%"
    ECHO Exit Code: %ERRORLEVEL% >> "%LOG_FILE%"
    ECHO ════════════════════════════════════════════════════════════════════════════ >> "%LOG_FILE%"
    ECHO.
    ECHO ✅ Extraction completed successfully
    ECHO Full log: %LOG_FILE%
    EXIT /B 0
) ELSE (
    ECHO ════════════════════════════════════════════════════════════════════════════ >> "%LOG_FILE%"
    ECHO ❌ Extraction failed with error code %ERRORLEVEL% >> "%LOG_FILE%"
    ECHO ════════════════════════════════════════════════════════════════════════════ >> "%LOG_FILE%"
    ECHO.
    ECHO ❌ Extraction failed with error code %ERRORLEVEL%
    ECHO Check log file: %LOG_FILE%
    
    REM Optional: Send alert email on failure (uncomment if email service is configured)
    REM "%PYTHON_PATH%" src\services\email_notifications\send_error_alert.py --error=%ERRORLEVEL%
    
    EXIT /B %ERRORLEVEL%
)
