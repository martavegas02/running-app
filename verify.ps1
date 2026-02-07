#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Script de verificación de la instalación de Running Analytics Hub

.DESCRIPTION
    Verifica que todos los componentes están correctamente instalados y configurados

.EXAMPLE
    .\verify.ps1
#>

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🏛️  Running Analytics Hub - Installation Verification      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$issues = 0

# ===== VERIFICACIONES =====

Write-Host "[*] VERIFICANDO COMPONENTES..." -ForegroundColor Yellow
Write-Host ""

# 1. Docker
Write-Host "[1] Verificando Docker..." -NoNewline
try {
    $dockerVersion = docker --version 2>$null
    if ($dockerVersion) {
        Write-Host " [OK]" -ForegroundColor Green
        Write-Host "   $dockerVersion" -ForegroundColor Green
    } else {
        throw "No Docker"
    }
} catch {
    Write-Host " [FAIL]" -ForegroundColor Red
    Write-Host "   Docker no está instalado o no está en el PATH" -ForegroundColor Red
    $issues++
}

# 2. Docker Compose
Write-Host "[2] Verificando Docker Compose..." -NoNewline
try {
    $composeVersion = docker-compose --version 2>$null
    if ($composeVersion) {
        Write-Host " [OK]" -ForegroundColor Green
        Write-Host "   $composeVersion" -ForegroundColor Green
    } else {
        throw "No Docker Compose"
    }
} catch {
    Write-Host " [FAIL]" -ForegroundColor Red
    Write-Host "   Docker Compose no está instalado" -ForegroundColor Red
    $issues++
}

Write-Host ""
Write-Host "[*] VERIFICANDO ESTRUCTURA DE ARCHIVOS..." -ForegroundColor Yellow
Write-Host ""

# Archivos críticos
$requiredFiles = @(
    "docker-compose.yml",
    ".env",
    ".env.example",
    ".gitignore",
    "README.md",
    "backend/Dockerfile",
    "backend/requirements.txt",
    "backend/app/main.py",
    "backend/app/models/database.py",
    "backend/app/core/database.py",
    "backend/database/init.sql",
    "frontend/Dockerfile",
    "frontend/requirements.txt",
    "frontend/app.py"
)

$fileCount = 0
foreach ($file in $requiredFiles) {
    $path = Join-Path "." $file
    if (Test-Path $path) {
        Write-Host "   [OK] $file" -ForegroundColor Green
        $fileCount++
    } else {
        Write-Host "   [FAIL] $file" -ForegroundColor Red
        $issues++
    }
}

Write-Host ""
Write-Host "   Archivos encontrados: $fileCount / $($requiredFiles.Count)" -ForegroundColor Yellow
Write-Host ""

# 3. .env configurado
Write-Host "[3] Verificando .env..." -NoNewline
try {
    if (Test-Path ".env") {
        $envContent = Get-Content ".env" -Raw
        if ($envContent -match "DATABASE_URL") {
            Write-Host " [OK]" -ForegroundColor Green
            Write-Host "   Variables de entorno configuradas" -ForegroundColor Green
        } else {
            throw "DATABASE_URL no encontrado"
        }
    } else {
        throw ".env no encontrado"
    }
} catch {
    Write-Host " [FAIL]" -ForegroundColor Red
    Write-Host "   $_" -ForegroundColor Red
    $issues++
}

Write-Host ""
Write-Host "[*] CONFIGURACIÓN DE PYTHON..." -ForegroundColor Yellow
Write-Host ""

# 4. Python en PATH
Write-Host "[4] Verificando Python..." -NoNewline
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3") {
        Write-Host " [OK]" -ForegroundColor Green
        Write-Host "   $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python 3 no encontrado"
    }
} catch {
    Write-Host " [WARN]" -ForegroundColor Yellow
    Write-Host "   Python no está en PATH (opcional para desarrollo con Docker)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($issues -eq 0) {
    Write-Host "[SUCCESS] TODO ESTA LISTO!" -ForegroundColor Green
    Write-Host ""
    Write-Host "[START] Para empezar:" -ForegroundColor Green
    Write-Host ""
    Write-Host "   1. Levanta los servicios:" -ForegroundColor Yellow
    Write-Host "      .\start.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "   2. Espera 10 segundos" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   3. Accede a los servicios:" -ForegroundColor Yellow
    Write-Host "      - API: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "      - Frontend: http://localhost:8501" -ForegroundColor Cyan
    Write-Host ""
} else {
    Write-Host "[ERROR] PROBLEMAS ENCONTRADOS: $issues" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor, resuelve los problemas marcados con [FAIL] antes de continuar." -ForegroundColor Red
    Write-Host ""
    Write-Host "[TIP] Sugerencias:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   - Instala Docker Desktop: https://www.docker.com/products/docker-desktop" -ForegroundColor White
    Write-Host "   - Verifica que Docker este en PATH: docker --version" -ForegroundColor White
    Write-Host "   - Reinicia PowerShell despues de instalar Docker" -ForegroundColor White
    Write-Host ""
}

Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
