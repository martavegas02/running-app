#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Script para levantar Running Analytics Hub en Docker

.DESCRIPTION
    Levanta PostgreSQL, FastAPI Backend y Streamlit Frontend

.EXAMPLE
    .\start.ps1
#>

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🏛️ Running Analytics Hub - Docker Setup" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar Docker
Write-Host "✓ Verificando Docker..." -ForegroundColor Yellow
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "✗ Docker no está instalado o no está en el PATH" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Docker encontrado" -ForegroundColor Green

# Verificar Docker Compose
Write-Host "✓ Verificando Docker Compose..." -ForegroundColor Yellow
if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "✗ Docker Compose no está instalado" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Docker Compose encontrado" -ForegroundColor Green
Write-Host ""

# Levantar servicios
Write-Host "🚀 Levantando servicios..." -ForegroundColor Cyan
docker-compose up -d

Write-Host ""
Write-Host "⏳ Esperando a que los servicios estén listos..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Verificar estado
Write-Host ""
Write-Host "📊 Estado de los contenedores:" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✨ ¡Servicios levantados exitosamente!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Acceso a los servicios:" -ForegroundColor Yellow
Write-Host "  • API Backend:     http://localhost:8000" -ForegroundColor Cyan
Write-Host "  • API Swagger UI:  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  • API ReDoc:       http://localhost:8000/redoc" -ForegroundColor Cyan
Write-Host "  • Frontend:        http://localhost:8501" -ForegroundColor Cyan
Write-Host "  • Base de Datos:   localhost:5432" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Comandos útiles:" -ForegroundColor Yellow
Write-Host "  • Ver logs:        docker-compose logs -f" -ForegroundColor White
Write-Host "  • Detener:         docker-compose down" -ForegroundColor White
Write-Host "  • Borrar BD:       docker-compose down -v" -ForegroundColor White
Write-Host ""
