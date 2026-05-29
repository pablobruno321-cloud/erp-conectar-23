@echo off
echo ============================================================
echo   Migrar datos locales a PostgreSQL (Neon / Render)
echo ============================================================
echo.
echo Pegá la DATABASE_URL de Neon cuando te la pida.
echo (La encontrás en neon.tech - Connection string)
echo.
set /p DATABASE_URL="DATABASE_URL: "
if "%DATABASE_URL%"=="" (
    echo ERROR: DATABASE_URL vacia
    pause
    exit /b 1
)
cd /d "%~dp0"
pip install psycopg2-binary pandas -q
python scripts\migrar_a_postgres.py
pause
