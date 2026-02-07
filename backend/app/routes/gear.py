"""
Rutas para equipo (gear).
Endpoints CRUD: POST, GET, PUT, DELETE
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import GearCreate, GearUpdate, GearResponse
from app.services.gear_service import GearService

router = APIRouter(prefix="/api/v1/gear", tags=["Gear"])


@router.post("/", response_model=GearResponse, status_code=201)
async def create_gear(gear: GearCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo equipo (zapatillas, bicicleta, etc.).
    
    - **user_id**: ID del usuario propietario (requerido)
    - **name**: Nombre del equipo (requerido)
    - **gear_type**: Tipo de equipo: shoes, bike, helmet, etc. (requerido)
    - **brand**: Marca (opcional)
    - **model**: Modelo (opcional)
    - **primary**: Si es el equipo predeterminado (default: False)
    - **retired**: Si está retirado (default: False)
    """
    try:
        db_gear = GearService.create_gear(db, gear)
        return db_gear
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[GearResponse])
async def get_all_gear(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Obtener todo el equipo con paginación.
    
    - **skip**: Número de registros a saltar
    - **limit**: Número máximo de registros
    """
    gear = GearService.get_all_gear(db, skip=skip, limit=limit)
    return gear


@router.get("/{gear_id}", response_model=GearResponse)
async def get_gear(gear_id: int, db: Session = Depends(get_db)):
    """
    Obtener un equipo por ID.
    
    - **gear_id**: ID del equipo
    """
    gear = GearService.get_gear(db, gear_id)
    if not gear:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    return gear


@router.get("/user/{user_id}", response_model=list[GearResponse])
async def get_user_gear(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Obtener todo el equipo de un usuario.
    
    - **user_id**: ID del usuario
    - **skip**: Número de registros a saltar
    - **limit**: Número máximo de registros
    """
    gear = GearService.get_user_gear(db, user_id, skip=skip, limit=limit)
    return gear


@router.get("/user/{user_id}/primary", response_model=GearResponse)
async def get_user_primary_gear(user_id: int, db: Session = Depends(get_db)):
    """
    Obtener el equipo primario (predeterminado) de un usuario.
    
    - **user_id**: ID del usuario
    """
    gear = GearService.get_user_primary_gear(db, user_id)
    if not gear:
        raise HTTPException(
            status_code=404,
            detail="Este usuario no tiene equipo primario configurado"
        )
    return gear


@router.put("/{gear_id}", response_model=GearResponse)
async def update_gear(
    gear_id: int,
    gear_update: GearUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar un equipo.
    
    - **gear_id**: ID del equipo
    """
    gear = GearService.update_gear(db, gear_id, gear_update)
    if not gear:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    return gear


@router.delete("/{gear_id}", status_code=204)
async def delete_gear(gear_id: int, db: Session = Depends(get_db)):
    """
    Eliminar un equipo.
    
    Las actividades asociadas se desvincularan automáticamente.
    
    - **gear_id**: ID del equipo
    """
    success = GearService.delete_gear(db, gear_id)
    if not success:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    return None


@router.post("/{gear_id}/retire", response_model=GearResponse)
async def retire_gear(gear_id: int, db: Session = Depends(get_db)):
    """
    Marcar un equipo como retirado (sin eliminar datos históricos).
    
    - **gear_id**: ID del equipo
    """
    gear = GearService.retire_gear(db, gear_id)
    if not gear:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    return gear


@router.get("/{gear_id}/usage", response_model=dict)
async def get_gear_usage(gear_id: int, db: Session = Depends(get_db)):
    """
    Obtener estadísticas de uso de un equipo.
    
    Retorna:
    - total_distance: Distancia total en km
    - activity_count: Número de actividades
    - synced_distance: Distancia sincronizada desde Strava
    """
    usage = GearService.get_gear_usage(db, gear_id)
    if not usage:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    return usage


@router.get("/stats/count", response_model=dict)
async def get_gear_count(db: Session = Depends(get_db)):
    """Obtener el número total de equipo registrado."""
    count = db.query(GearService.Gear).count()
    return {"total_gear": count}
