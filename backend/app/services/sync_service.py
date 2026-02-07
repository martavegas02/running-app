"""
Sync Service - Sincronización de Actividades con Strava API
"""
import httpx
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.database import User, Activity
from app.services.auth_service import AuthService

STRAVA_API_URL = "https://www.strava.com/api/v3"

class SyncService:
    """Servicio para sincronizar actividades desde Strava"""

    @staticmethod
    async def get_strava_activities(
        db: Session, 
        user_id: int, 
        per_page: int = 30, 
        page: int = 1,
        after: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Obtiene actividades del usuario desde Strava API.
        Ahora soporta el parámetro 'after' para sincronización incremental.
        """
        user = db.query(User).filter_by(id=user_id).first()
        
        if not user:
            raise ValueError("Usuario no encontrado")
        
        if not user.strava_access_token:
            raise ValueError("Usuario no tiene token de Strava vinculado")
        
        # Refrescar token si es necesario
        access_token = await AuthService.refresh_strava_token(db, user_id)
        
        if not access_token:
            raise ValueError("No se pudo refrescar el token de Strava")
        
        # Validar límites
        per_page = min(per_page, 200)
        
        params = {
            "page": page,
            "per_page": per_page,
        }
        # Si nos pasan un timestamp, filtramos por él
        if after:
            params["after"] = after
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(
                    f"{STRAVA_API_URL}/athlete/activities",
                    headers={"Authorization": f"Bearer {access_token}"},
                    params=params,
                )
                
                if response.status_code == 401:
                    # Token inválido, reintento con refresh forzado
                    new_token = await AuthService.refresh_strava_token(db, user_id)
                    if not new_token:
                        raise ValueError("Token expirado sin posibilidad de refresh")
                    
                    response = await client.get(
                        f"{STRAVA_API_URL}/athlete/activities",
                        headers={"Authorization": f"Bearer {new_token}"},
                        params=params,
                    )
                
                if response.status_code != 200:
                    raise ValueError(f"Error Strava API ({response.status_code}): {response.text}")
                
                activities = response.json()
                
                return {
                    "activities": activities,
                    "total_count": len(activities),
                    "page": page,
                    "per_page": per_page,
                    "has_more": len(activities) == per_page,
                }
                
        except httpx.TimeoutException:
            raise ValueError("Timeout conectando a Strava API")
        except Exception as e:
            raise ValueError(f"Error general Strava: {str(e)}")

    @staticmethod
    def create_activity_from_strava(
        db: Session, user_id: int, strava_activity: Dict[str, Any]
    ) -> Optional[Activity]:
        """Crea o ACTUALIZA una actividad en la BD."""
        
        # Verificar si existe
        existing = db.query(Activity).filter_by(
            strava_id=strava_activity.get("id")
        ).first()
        
        try:
            # Procesamos fechas con seguridad
            start_date_str = strava_activity.get("start_date", "")
            start_date_local_str = strava_activity.get("start_date_local", "")
            
            start_date = datetime.fromisoformat(start_date_str.replace("Z", "+00:00")) if start_date_str else datetime.utcnow()
            start_date_local = datetime.fromisoformat(start_date_local_str.replace("Z", "+00:00")) if start_date_local_str else datetime.utcnow()

            if existing:
                # Opcional: Actualizar datos si la actividad cambió en Strava
                # Por ahora retornamos None para indicar que no es nueva
                return None 
            
            # Crear nueva actividad
            db_activity = Activity(
                user_id=user_id,
                strava_id=strava_activity.get("id"),
                name=strava_activity.get("name", "Actividad sin nombre"),
                activity_type=strava_activity.get("type", "Run").lower(),
                description=strava_activity.get("description", ""),
                distance=strava_activity.get("distance", 0.0),
                duration=strava_activity.get("moving_time", 0),
                elevation_gain=strava_activity.get("total_elevation_gain", 0.0),
                average_speed=strava_activity.get("average_speed", 0.0),
                max_speed=strava_activity.get("max_speed", 0.0),
                average_heart_rate=strava_activity.get("average_heartrate"),
                max_heart_rate=strava_activity.get("max_heartrate"),
                average_cadence=strava_activity.get("average_cadence"),
                start_date=start_date,
                start_date_local=start_date_local,
                timezone=strava_activity.get("timezone", ""),
                gear_id=None,
                raw_data=strava_activity,
                synced_at=datetime.utcnow(),
            )
            
            db.add(db_activity)
            db.commit()
            db.refresh(db_activity)
            return db_activity
            
        except IntegrityError:
            db.rollback()
            return None # Ignorar duplicados concurrentes
        except Exception as e:
            db.rollback()
            raise ValueError(f"Error procesando actividad ID {strava_activity.get('id')}: {str(e)}")

    @staticmethod
    async def sync_user_activities(
        db: Session,
        user_id: int,
        per_page: int = 50,
        max_pages: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Sincroniza actividades.
        ESTRATEGIA:
        1. Pedimos las actividades más recientes (página 1).
        2. Si el usuario fuerza una sincronización completa (reset), bajamos todo.
        """
        page = 1
        total_new = 0
        total_existing = 0
        errors = []
        
        # IMPORTANTE: Para asegurar que cogemos actividades manuales antiguas,
        # lo mejor es NO usar 'after' si queremos un barrido completo,
        # o usar un 'after' muy antiguo (ej: hace 10 años) si queremos forzar.
        # Por defecto, Strava devuelve orden cronológico inverso (nuevas primero).
        
        # Para tu caso (actividad manual antigua no detectada), vamos a aumentar
        # la profundidad de búsqueda por defecto.
        if max_pages is None:
            max_pages = 10  # Buscamos hasta 10 páginas (500 actividades) por seguridad
        
        while True:
            if max_pages and page > max_pages:
                break
            
            try:
                # Llamada a la API
                result = await SyncService.get_strava_activities(
                    db, user_id, per_page, page
                )
                
                activities_data = result["activities"]
                
                if not activities_data:
                    break
                
                # Procesar lote
                items_processed_in_page = 0
                for item in activities_data:
                    try:
                        created = SyncService.create_activity_from_strava(db, user_id, item)
                        if created:
                            total_new += 1
                        else:
                            total_existing += 1
                        items_processed_in_page += 1
                    except Exception as e:
                        errors.append({"id": item.get("id"), "error": str(e)})
                
                # Actualizar última sincronización
                user = db.query(User).filter_by(id=user_id).first()
                if user:
                    user.last_sync = datetime.utcnow()
                    db.commit()
                
                # Condición de salida: Si Strava devuelve menos items de los pedidos, es la última página
                if len(activities_data) < per_page:
                    break
                
                page += 1
                
            except Exception as e:
                errors.append({"page": page, "error": str(e)})
                break
        
        return {
            "status": "success",
            "new": total_new,
            "existing": total_existing,
            "pages": page - 1,
            "errors": errors
        }

    @staticmethod
    async def get_user_sync_stats(db: Session, user_id: int) -> Dict[str, Any]:
        """Obtiene estadísticas rápidas"""
        user = db.query(User).filter_by(id=user_id).first()
        if not user: return {}
        
        count = db.query(Activity).filter_by(user_id=user_id).count()
        last_activity = db.query(Activity).filter_by(user_id=user_id).order_by(Activity.start_date.desc()).first()
        
        return {
            "total_activities": count,
            "last_sync": user.last_sync,
            "latest_activity_date": last_activity.start_date if last_activity else None
        }

    @staticmethod
    async def delete_all_synced_activities(db: Session, user_id: int) -> int:
        count = db.query(Activity).filter_by(user_id=user_id).delete()
        db.commit()
        return count