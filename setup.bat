@echo off
echo.
echo ======================================
echo  External API Tester - Setup
echo ======================================
echo.

REM Check if .env exists
if exist .env (
    echo WARNING: .env file already exists!
    set /p "OVERWRITE=Do you want to overwrite it? (y/N): "
    if /i not "%OVERWRITE%"=="y" (
        echo.
        echo Setup cancelled. Keeping existing .env file.
        exit /b 1
    )
)

REM Copy env.example to .env
echo Copying env.example to .env...
copy env.example .env >nul 2>&1

if %errorlevel% equ 0 (
    echo.
    echo ✓ .env file created successfully!
    echo.
    echo OAuth2 credentials configured for all 6 environments:
    echo   - Capricorn API Trunk (Dev^)
    echo   - Capricorn Rapid Production
    echo   - Capricorn Standard Production
    echo   - Capricorn Rapid Stage
    echo   - Capricorn Standard Stage
    echo   - External API Local
    echo.
    echo Next steps:
    echo   1. (Optional^) Edit .env if you need to update credentials
    echo   2. Start the application:
    echo      - Development: wsl docker-compose -f docker-compose.dev.yml up --build
    echo      - Production:  wsl docker-compose up --build
    echo   3. Open: http://localhost:5000/test-runner
    echo.
    echo For more information, see ENV_SETUP_GUIDE.md
    echo.
) else (
    echo.
    echo ERROR: Failed to create .env file
    echo Make sure env.example exists in the current directory
    exit /b 1
)

