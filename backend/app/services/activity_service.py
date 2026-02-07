"""
Servicio de actividades.
Contiene la lógica de negocio para CRUD de actividades.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from app.models.database import Activity, User
from app.schemas import ActivityCreate, ActivityResponse


class ActivityService:
    """Servicio para operaciones CRUD de actividades."""

    @staticmethod
    def create_activity(db: Session, activity_data: ActivityCreate) -> Activity:
        """
        Crear una nueva actividad.
        
        Args:
            db: Sesión de base de datos
            activity_data: Datos de la actividad
            
        Returns:
            Actividad creada
            
        Raises:
            ValueError: Si la actividad ya existe (strava_id duplicado)
        """
        # Verificar que el usuario existe
        user = db.query(User).filter(User.id == activity_data.user_id).first()
        if not user:
            raise ValueError("Usuario no encontrado")
        
        try:
            db_activity = Activity(**activity_data.dict())
            db.add(db_activity)
            db.commit()
            db.refresh(db_activity)
            return db_activity
        except IntegrityError:
            db.rollback()
            raise ValueError("Actividad con ese strava_id ya existe")

    @staticmethod
    def get_activity(db: Session, activity_id: int) -> Activity:
        """Obtener una actividad por ID."""
        return db.query(Activity).filter(Activity.id == activity_id).first()

    @staticmethod
    def get_activity_by_strava_id(db: Session, strava_id: int) -> Activity:
        """Obtener una actividad por strava_id."""
        return db.query(Activity).filter(Activity.strava_id == strava_id).first()

    @staticmethod
    def get_user_activities(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        activity_type: str = None
    ):
        """
        Obtener actividades de un usuario con paginación.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            skip: Número de registros a saltar
            limit: Límite de registros
            activity_type: Filtrar por tipo de actividad (opcional)
            
        Returns:
            Lista de actividades
        """
        query = db.query(Activity).filter(Activity.user_id == user_id)
        
        if activity_type:
            query = query.filter(Activity.activity_type == activity_type)
        
        return query.order_by(Activity.start_date.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_all_activities(db: Session, skip: int = 0, limit: int = 100):
        """Obtener todas las actividades (para administración)."""
        return db.query(Activity).order_by(Activity.start_date.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_activity(db: Session, activity_id: int, activity_data: dict) -> Activity:
        """Actualizar una actividad."""
        db_activity = ActivityService.get_activity(db, activity_id)
        if not db_activity:
            return None
        
        activity_data['updated_at'] = datetime.utcnow()
        
        for key, value in activity_data.items():
            if value is not None:
                setattr(db_activity, key, value)
        
        db.add(db_activity)
        db.commit()
        db.refresh(db_activity)
        return db_activity

    @staticmethod
    def delete_activity(db: Session, activity_id: int) -> bool:
        """Eliminar una actividad."""
        db_activity = ActivityService.get_activity(db, activity_id)
        if not db_activity:
            return False
        
        db.delete(db_activity)
        db.commit()
        return True

    @staticmethod
    def get_user_statistics(db: Session, user_id: int) -> dict:
        """
        Obtener estadísticas básicas de las actividades de un usuario.
        
        Returns:
            Dict con total_distance, total_duration, activity_count, etc.
        """
        from sqlalchemy import func
        
        activities = db.query(Activity).filter(Activity.user_id == user_id).all()
        
        if not activities:
            return {
                "total_distance": 0,
                "total_duration": 0,
                "activity_count": 0,
                "average_speed": 0,
                "max_speed": 0
            }
        
        total_distance = sum(a.distance for a in activities) / 1000  # Convertir a km
        total_duration = sum(a.duration for a in activities) / 3600  # Convertir a horas
        activity_count = len(activities)
        average_speed = sum(a.average_speed for a in activities if a.average_speed) / activity_count if activity_count > 0 else 0
        max_speed = max(a.max_speed for a in activities if a.max_speed) if any(a.max_speed for a in activities) else 0
        
        return {
            "total_distance": round(total_distance, 2),
            "total_duration": round(total_duration, 2),
            "activity_count": activity_count,
            "average_speed": round(average_speed, 2),
            "max_speed": round(max_speed, 2)
        }

    @staticmethod
    def count_user_activities(db: Session, user_id: int) -> int:
        """Contar actividades de un usuario."""
        return db.query(Activity).filter(Activity.user_id == user_id).count()
