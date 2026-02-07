@echo off
REM Script de verificacion de instalacion - Running Analytics Hub

cls
echo.
echo ============================================================
echo    Running Analytics Hub - Installation Verification
echo ============================================================
echo.

setlocal enabledelayedexpansion
set "issues=0"

REM Verificar Docker
echo [1] Verificando Docker...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo    [OK] Docker esta instalado
) else (
    echo    [FAIL] Docker no esta instalado
    set /a issues+=1
)

REM Verificar Docker Compose
echo [2] Verificando Docker Compose...
docker-compose --version >nul 2>&1
if %errorlevel% equ 0 (
    echo    [OK] Docker Compose esta instalado
) else (
    echo    [FAIL] Docker Compose no esta instalado
    set /a issues+=1
)

REM Verificar archivos criticos
echo [3] Verificando archivos...
if exist docker-compose.yml (
    echo    [OK] docker-compose.yml encontrado
) else (
    echo    [FAIL] docker-compose.yml no encontrado
    set /a issues+=1
)

if exist .env (
    echo    [OK] .env encontrado
) else (
    echo    [FAIL] .env no encontrado
    set /a issues+=1
)

if exist backend\Dockerfile (
    echo    [OK] backend/Dockerfile encontrado
) else (
    echo    [FAIL] backend/Dockerfile no encontrado
    set /a issues+=1
)

if exist backend\app\main.py (
    echo    [OK] backend/app/main.py encontrado
) else (
    echo    [FAIL] backend/app/main.py no encontrado
    set /a issues+=1
)

if exist frontend\app.py (
    echo    [OK] frontend/app.py encontrado
) else (
    echo    [FAIL] frontend/app.py no encontrado
    set /a issues+=1
)

echo.
echo ============================================================
echo.

if %issues% equ 0 (
    echo [SUCCESS] Todo esta listo!
    echo.
    echo [NEXT] Para empezar:
    echo.
    echo   1. Levanta los servicios:
    echo      docker-compose up -d
    echo.
    echo   2. Espera 10 segundos
    echo.
    echo   3. Accede a:
    echo      - API: http://localhost:8000/docs
    echo      - Frontend: http://localhost:8501
    echo.
) else (
    echo [ERROR] Problemas encontrados: %issues%
    echo.
    echo Por favor resuelve los problemas antes de continuar.
    echo.
    echo [TIP] Descarga Docker Desktop:
    echo      https://www.docker.com/products/docker-desktop
    echo.
)

echo ============================================================
echo.
pause
