"""
Servicio de equipo (gear).
Contiene la lógica de negocio para CRUD de equipo.
"""

from sqlalchemy.orm import Session
from datetime import datetime
from app.models.database import Gear, User, Activity
from app.schemas import GearCreate, GearUpdate, GearResponse


class GearService:
    """Servicio para operaciones CRUD de equipo."""

    @staticmethod
    def create_gear(db: Session, gear_data: GearCreate) -> Gear:
        """
        Crear un nuevo equipo.
        
        Args:
            db: Sesión de base de datos
            gear_data: Datos del equipo
            
        Returns:
            Equipo creado
            
        Raises:
            ValueError: Si el usuario no existe
        """
        # Verificar que el usuario existe
        user = db.query(User).filter(User.id == gear_data.user_id).first()
        if not user:
            raise ValueError("Usuario no encontrado")
        
        db_gear = Gear(**gear_data.dict())
        db.add(db_gear)
        db.commit()
        db.refresh(db_gear)
        return db_gear

    @staticmethod
    def get_gear(db: Session, gear_id: int) -> Gear:
        """Obtener equipo por ID."""
        return db.query(Gear).filter(Gear.id == gear_id).first()

    @staticmethod
    def get_gear_by_strava_id(db: Session, strava_id: str) -> Gear:
        """Obtener equipo por strava_id."""
        return db.query(Gear).filter(Gear.strava_id == strava_id).first()

    @staticmethod
    def get_user_gear(db: Session, user_id: int, skip: int = 0, limit: int = 100):
        """
        Obtener todo el equipo de un usuario.
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            skip: Número de registros a saltar
            limit: Límite de registros
            
        Returns:
            Lista de equipo
        """
        return db.query(Gear).filter(
            Gear.user_id == user_id
        ).offset(skip).limit(limit).all()

    @staticmethod
    def get_user_primary_gear(db: Session, user_id: int) -> Gear:
        """Obtener el equipo primario (predeterminado) de un usuario."""
        return db.query(Gear).filter(
            Gear.user_id == user_id,
            Gear.primary == True
        ).first()

    @staticmethod
    def get_all_gear(db: Session, skip: int = 0, limit: int = 100):
        """Obtener todo el equipo (para administración)."""
        return db.query(Gear).offset(skip).limit(limit).all()

    @staticmethod
    def update_gear(db: Session, gear_id: int, gear_data: GearUpdate) -> Gear:
        """Actualizar equipo."""
        db_gear = GearService.get_gear(db, gear_id)
        if not db_gear:
            return None
        
        # Si se marca como primary, desmarcar otros
        if gear_data.primary:
            db.query(Gear).filter(
                Gear.user_id == db_gear.user_id,
                Gear.primary == True
            ).update({"primary": False})
        
        update_data = gear_data.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow()
        
        for key, value in update_data.items():
            setattr(db_gear, key, value)
        
        db.add(db_gear)
        db.commit()
        db.refresh(db_gear)
        return db_gear

    @staticmethod
    def delete_gear(db: Session, gear_id: int) -> bool:
        """Eliminar equipo."""
        db_gear = GearService.get_gear(db, gear_id)
        if not db_gear:
            return False
        
        # Disociar actividades
        db.query(Activity).filter(Activity.gear_id == gear_id).update({"gear_id": None})
        
        db.delete(db_gear)
        db.commit()
        return True

    @staticmethod
    def get_gear_usage(db: Session, gear_id: int) -> dict:
        """
        Obtener estadísticas de uso de un equipo.
        
        Returns:
            Dict con distance, activity_count, etc.
        """
        gear = GearService.get_gear(db, gear_id)
        if not gear:
            return None
        
        activities = db.query(Activity).filter(Activity.gear_id == gear_id).all()
        
        total_distance = sum(a.distance for a in activities) / 1000  # Convertir a km
        activity_count = len(activities)
        
        return {
            "gear_id": gear_id,
            "gear_name": gear.name,
            "total_distance": round(total_distance, 2),
            "activity_count": activity_count,
            "synced_distance": round(gear.distance / 1000, 2)  # Sincronizado desde Strava
        }

    @staticmethod
    def retire_gear(db: Session, gear_id: int) -> Gear:
        """Marcar equipo como retirado."""
        db_gear = GearService.get_gear(db, gear_id)
        if not db_gear:
            return None
        
        db_gear.retired = True
        db_gear.updated_at = datetime.utcnow()
        
        db.add(db_gear)
        db.commit()
        db.refresh(db_gear)
        return db_gear

    @staticmethod
    def count_user_gear(db: Session, user_id: int) -> int:
        """Contar equipo de un usuario."""
        return db.query(Gear).filter(Gear.user_id == user_id).count()
