@echo off
REM Batch script to test the Edge-Based Plate Straightener

echo ============================================================
echo  EDGE-BASED PLATE STRAIGHTENER TEST
echo ============================================================
echo.
echo Activating conda environment: alpr_dev
echo.

call conda activate alpr_dev

echo.
echo Running edge-based plate straightener demo...
echo.

cd /d "%~dp0"
python demo_straightener.py "C:\Users\maazs\Pictures\Screenshots\Screenshot 2026-01-06 010749.png"

echo.
echo ============================================================
echo Press any key to exit...
pause >nul
