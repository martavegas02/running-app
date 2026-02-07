"""
Servicio de usuarios.
Contiene la lógica de negocio para CRUD de usuarios.
"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from app.models.database import User
from app.schemas import UserCreate, UserUpdate, UserResponse


class UserService:
    """Servicio para operaciones CRUD de usuarios."""

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """
        Crear un nuevo usuario.
        
        Args:
            db: Sesión de base de datos
            user_data: Datos del usuario a crear
            
        Returns:
            Usuario creado
            
        Raises:
            ValueError: Si el usuario ya existe (strava_id o username duplicado)
        """
        try:
            db_user = User(**user_data.dict())
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            raise ValueError("Usuario con ese strava_id o username ya existe")

    @staticmethod
    def get_user(db: Session, user_id: int) -> User:
        """Obtener un usuario por ID."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_strava_id(db: Session, strava_id: int) -> User:
        """Obtener un usuario por strava_id."""
        return db.query(User).filter(User.strava_id == strava_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User:
        """Obtener un usuario por username."""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100):
        """Obtener todos los usuarios con paginación."""
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
        """Actualizar un usuario."""
        db_user = UserService.get_user(db, user_id)
        if not db_user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        update_data['updated_at'] = datetime.utcnow()
        
        for key, value in update_data.items():
            setattr(db_user, key, value)
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Eliminar un usuario."""
        db_user = UserService.get_user(db, user_id)
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        return True

    @staticmethod
    def update_last_sync(db: Session, user_id: int) -> User:
        """Actualizar timestamp de última sincronización."""
        db_user = UserService.get_user(db, user_id)
        if not db_user:
            return None
        
        db_user.last_sync = datetime.utcnow()
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def count_users(db: Session) -> int:
        """Contar total de usuarios."""
        return db.query(User).count()
