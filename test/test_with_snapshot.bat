@echo off
REM Test the straightener with a specific snapshot

if "%~1"=="" (
    echo Usage: test_with_snapshot.bat ^<snapshot_name^>
    echo Example: test_with_snapshot.bat MH20EJ0364_20260106_010636.jpg
    echo.
    echo Or just drag and drop an image file onto this batch file!
    pause
    exit /b
)

echo ============================================================
echo  TESTING WITH: %~1
echo ============================================================
echo.
echo Activating conda environment: alpr_dev
echo.

call conda activate alpr_dev

echo.
echo Running edge-based plate straightener...
echo.

cd /d "%~dp0"

REM Check if the file is in the parent snapshots folder
if exist "..\snapshots\%~1" (
    python demo_straightener.py "..\snapshots\%~1"
) else if exist "%~1" (
    python demo_straightener.py "%~1"
) else (
    echo [ERROR] File not found: %~1
    echo.
    pause
    exit /b
)

echo.
echo ============================================================
echo Press any key to exit...
pause >nul
