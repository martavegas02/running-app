#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Script para detener y limpiar Running Analytics Hub

.DESCRIPTION
    Detiene los contenedores y opcionalmente borra los volúmenes

.PARAMETER RemoveVolumes
    Si se proporciona, borra también los volúmenes (BD)

.EXAMPLE
    .\stop.ps1
    .\stop.ps1 -RemoveVolumes
#>

param(
    [switch]$RemoveVolumes
)

Write-Host "========================================" -ForegroundColor Yellow
Write-Host "⛔ Running Analytics Hub - Stopping Services" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

if ($RemoveVolumes) {
    Write-Host "⚠️  ADVERTENCIA: Se borrarán los volúmenes (BD incluida)" -ForegroundColor Red
    $confirmation = Read-Host "¿Estás seguro? (s/n)"
    
    if ($confirmation -eq "s") {
        Write-Host "🗑️  Deteniendo servicios y borrando volúmenes..." -ForegroundColor Yellow
        docker-compose down -v
        Write-Host "✓ Completado" -ForegroundColor Green
    } else {
        Write-Host "❌ Operación cancelada" -ForegroundColor Yellow
    }
} else {
    Write-Host "🛑 Deteniendo servicios..." -ForegroundColor Yellow
    docker-compose down
    Write-Host "✓ Completado" -ForegroundColor Green
    Write-Host ""
    Write-Host "💡 Tip: Los datos de la BD se conservan en los volúmenes" -ForegroundColor Cyan
    Write-Host "   Para borrar todo, ejecuta: .\stop.ps1 -RemoveVolumes" -ForegroundColor Cyan
}

Write-Host ""
