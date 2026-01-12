@echo off
REM Batch test multiple snapshots

echo ============================================================
echo  BATCH TEST - EDGE-BASED STRAIGHTENER
echo ============================================================
echo.
echo Activating conda environment: alpr_dev
echo.

call conda activate alpr_dev

echo.
echo Testing straightener on multiple snapshots...
echo.

cd /d "%~dp0"

REM Test with 5 different snapshots
for %%f in (..\snapshots\MH*.jpg) do (
    echo.
    echo ----------------------------------------
    echo Testing: %%~nxf
    echo ----------------------------------------
    python demo_straightener.py "%%f"
    echo.
    timeout /t 1 /nobreak >nul
)

echo.
echo ============================================================
echo All tests complete!
echo Press any key to exit...
pause >nul
