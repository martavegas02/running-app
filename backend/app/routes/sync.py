"""
Routes - Sincronización de Actividades con Strava
Endpoints: /sync/activities, /sync/stats, /sync/reset
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.sync_service import SyncService

router = APIRouter(prefix="/sync", tags=["Synchronization"])


@router.post("/activities")
async def sync_activities(
    user_id: int = Query(..., description="ID del usuario a sincronizar"),
    per_page: int = Query(50, ge=1, le=200, description="Actividades por página"),
    max_pages: Optional[int] = Query(None, ge=1, description="Máximo de páginas (None = todas)"),
    db: Session = Depends(get_db),
):
    """
    Sincroniza actividades desde Strava para un usuario
    
    Descarga todas (o un máximo de páginas) actividades del usuario desde Strava
    y las guarda en la base de datos. Detecta automáticamente duplicados.
    
    Args:
        user_id: ID del usuario (requerido)
        per_page: Actividades por página, máximo 200 (default: 50)
        max_pages: Máximo de páginas a sincronizar (default: todas)
        db: Sesión de base de datos
        
    Returns:
        Estadísticas de sincronización
        
    Raises:
        HTTPException 404: Si el usuario no existe
        HTTPException 401: Si no tiene token de Strava vinculado
        HTTPException 500: Si hay error en Strava API
        
    Examples:
        # Sincronizar con defaults (50 por página, todas las páginas)
        POST /sync/activities?user_id=1
        
        # Sincronizar solo primeras 100 actividades
        POST /sync/activities?user_id=1&per_page=100&max_pages=1
        
        # Sincronizar últimas 200 por página (máximo de Strava)
        POST /sync/activities?user_id=1&per_page=200
    """
    try:
        result = await SyncService.sync_user_activities(
            db, user_id, per_page, max_pages
        )
        
        return {
            **result,
            "message": "Sincronización completada exitosamente",
        }
        
    except ValueError as e:
        if "no encontrado" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        elif "token" in str(e).lower():
            raise HTTPException(status_code=401, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error durante sincronización: {str(e)}",
        )


@router.get("/stats")
async def get_sync_stats(
    user_id: int = Query(..., description="ID del usuario"),
    db: Session = Depends(get_db),
):
    """
    Obtiene estadísticas de sincronización del usuario
    
    Retorna información sobre:
    - Total de actividades sincronizadas
    - Última sincronización
    - Rango de fechas de actividades
    - Estado de conexión con Strava
    
    Args:
        user_id: ID del usuario (requerido)
        db: Sesión de base de datos
        
    Returns:
        Estadísticas de sincronización
        
    Raises:
        HTTPException 404: Si el usuario no existe
        
    Response Example:
        {
            "user_id": 1,
            "total_activities": 45,
            "last_sync": "2025-12-30T10:30:00",
            "strava_connected": true,
            "token_expires_at": "2025-12-31T15:30:00",
            "earliest_activity": "2024-01-15T08:00:00",
            "latest_activity": "2025-12-30T09:30:00",
            "data_range_days": 350
        }
    """
    try:
        stats = await SyncService.get_user_sync_stats(db, user_id)
        return stats
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estadísticas: {str(e)}",
        )


@router.post("/activities/reset")
async def reset_synced_activities(
    user_id: int = Query(..., description="ID del usuario"),
    db: Session = Depends(get_db),
):
    """
    Elimina todas las actividades sincronizadas del usuario
    
    WARNING: Esta acción es irreversible. Todas las actividades sincronizadas
    de este usuario serán eliminadas de la base de datos.
    
    Args:
        user_id: ID del usuario (requerido)
        db: Sesión de base de datos
        
    Returns:
        Cantidad de actividades eliminadas
        
    Raises:
        HTTPException 400: Si el usuario no tiene actividades
        HTTPException 500: Si hay error durante la eliminación
        
    Response Example:
        {
            "deleted_count": 45,
            "message": "45 actividades eliminadas correctamente",
            "user_id": 1,
            "warning": "Esta acción es irreversible"
        }
    """
    try:
        count = await SyncService.delete_all_synced_activities(db, user_id)
        
        if count == 0:
            return {
                "deleted_count": 0,
                "message": "El usuario no tiene actividades sincronizadas",
                "user_id": user_id,
            }
        
        return {
            "deleted_count": count,
            "message": f"{count} actividades eliminadas correctamente",
            "user_id": user_id,
            "warning": "Esta acción es irreversible",
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error eliminando actividades: {str(e)}",
        )


@router.get("/status")
async def get_sync_status(
    user_id: int = Query(..., description="ID del usuario"),
    db: Session = Depends(get_db),
):
    """
    Obtiene el estado de sincronización rápido del usuario
    
    Endpoint ligero para verificar si el usuario está conectado
    y cuándo fue la última sincronización.
    
    Args:
        user_id: ID del usuario (requerido)
        db: Sesión de base de datos
        
    Returns:
        Estado de sincronización
        
    Raises:
        HTTPException 404: Si el usuario no existe
        
    Response Example:
        {
            "user_id": 1,
            "is_connected": true,
            "last_sync": "2025-12-30T10:30:00",
            "token_expires_in_minutes": 125,
            "needs_refresh": false
        }
    """
    from datetime import datetime
    from app.models.database import User
    
    try:
        user = db.query(User).filter_by(id=user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        is_connected = bool(user.strava_access_token)
        
        # Calcular minutos hasta expiración
        token_expires_in_minutes = None
        needs_refresh = False
        
        if user.strava_token_expires_at:
            delta = user.strava_token_expires_at - datetime.utcnow()
            token_expires_in_minutes = int(delta.total_seconds() / 60)
            needs_refresh = token_expires_in_minutes < 60  # Refrescar si faltan menos de 1 hora
        
        return {
            "user_id": user_id,
            "is_connected": is_connected,
            "last_sync": user.last_sync,
            "token_expires_in_minutes": token_expires_in_minutes,
            "needs_refresh": needs_refresh,
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estado: {str(e)}",
        )
