"""
Rutas para actividades.
Endpoints CRUD: POST, GET, PUT, DELETE
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import ActivityCreate, ActivityResponse
from app.services.activity_service import ActivityService

router = APIRouter(prefix="/api/v1/activities", tags=["Activities"])


@router.post("/", response_model=ActivityResponse, status_code=201)
async def create_activity(activity: ActivityCreate, db: Session = Depends(get_db)):
    """
    Crear una nueva actividad.
    
    - **user_id**: ID del usuario propietario (requerido)
    - **strava_id**: ID único de Strava (requerido)
    - **name**: Nombre de la actividad (requerido)
    - **activity_type**: Tipo (run, walk, ride, etc.) (requerido)
    - **distance**: Distancia en metros (requerido)
    - **duration**: Duración en segundos (requerido)
    - **start_date**: Fecha y hora en UTC (requerido)
    """
    try:
        db_activity = ActivityService.create_activity(db, activity)
        return db_activity
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[ActivityResponse])
async def get_activities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Obtener todas las actividades con paginación.
    
    - **skip**: Número de registros a saltar
    - **limit**: Número máximo de registros
    """
    activities = ActivityService.get_all_activities(db, skip=skip, limit=limit)
    return activities


@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity(activity_id: int, db: Session = Depends(get_db)):
    """
    Obtener una actividad por ID.
    
    - **activity_id**: ID de la actividad
    """
    activity = ActivityService.get_activity(db, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    return activity


@router.get("/by-strava/{strava_id}", response_model=ActivityResponse)
async def get_activity_by_strava_id(strava_id: int, db: Session = Depends(get_db)):
    """
    Obtener una actividad por strava_id.
    
    - **strava_id**: ID único de Strava
    """
    activity = ActivityService.get_activity_by_strava_id(db, strava_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    return activity


@router.get("/user/{user_id}", response_model=list[ActivityResponse])
async def get_user_activities(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    activity_type: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    Obtener actividades de un usuario específico.
    
    - **user_id**: ID del usuario
    - **skip**: Número de registros a saltar
    - **limit**: Número máximo de registros
    - **activity_type**: Filtrar por tipo (opcional): run, walk, ride, etc.
    """
    activities = ActivityService.get_user_activities(
        db,
        user_id=user_id,
        skip=skip,
        limit=limit,
        activity_type=activity_type
    )
    return activities


@router.put("/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: int,
    activity_data: dict,
    db: Session = Depends(get_db)
):
    """
    Actualizar una actividad.
    
    - **activity_id**: ID de la actividad
    """
    activity = ActivityService.update_activity(db, activity_id, activity_data)
    if not activity:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    return activity


@router.delete("/{activity_id}", status_code=204)
async def delete_activity(activity_id: int, db: Session = Depends(get_db)):
    """
    Eliminar una actividad.
    
    - **activity_id**: ID de la actividad
    """
    success = ActivityService.delete_activity(db, activity_id)
    if not success:
        raise HTTPException(status_code=404, detail="Actividad no encontrada")
    return None


@router.get("/user/{user_id}/stats", response_model=dict)
async def get_user_activity_stats(user_id: int, db: Session = Depends(get_db)):
    """
    Obtener estadísticas de actividades de un usuario.
    
    Retorna:
    - total_distance: Distancia total en km
    - total_duration: Duración total en horas
    - activity_count: Número de actividades
    - average_speed: Velocidad promedio en m/s
    - max_speed: Velocidad máxima en m/s
    """
    stats = ActivityService.get_user_statistics(db, user_id)
    return stats


@router.get("/stats/count", response_model=dict)
async def get_activities_count(db: Session = Depends(get_db)):
    """Obtener el número total de actividades en la BD."""
    count = db.query(ActivityService.Activity).count()
    return {"total_activities": count}
