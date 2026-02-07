"""
Rutas para usuarios.
Endpoints CRUD: POST, GET, PUT, DELETE
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas import UserCreate, UserUpdate, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo usuario.
    
    - **strava_id**: ID único de Strava (requerido)
    - **username**: Nombre de usuario único (requerido)
    - **email**: Email del usuario (opcional)
    - **access_token**: Token de acceso OAuth (requerido)
    """
    try:
        db_user = UserService.create_user(db, user)
        return db_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los usuarios con paginación.
    
    - **skip**: Número de registros a saltar (default: 0)
    - **limit**: Número máximo de registros (default: 100, máximo: 1000)
    """
    users = UserService.get_all_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Obtener un usuario por ID.
    
    - **user_id**: ID del usuario
    """
    user = UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.get("/by-username/{username}", response_model=UserResponse)
async def get_user_by_username(username: str, db: Session = Depends(get_db)):
    """
    Obtener un usuario por username.
    
    - **username**: Username del usuario
    """
    user = UserService.get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.get("/by-strava/{strava_id}", response_model=UserResponse)
async def get_user_by_strava_id(strava_id: int, db: Session = Depends(get_db)):
    """
    Obtener un usuario por strava_id.
    
    - **strava_id**: ID único de Strava
    """
    user = UserService.get_user_by_strava_id(db, strava_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualizar un usuario.
    
    - **user_id**: ID del usuario
    """
    user = UserService.update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Eliminar un usuario.
    
    ⚠️ Esto eliminará todas sus actividades y equipo asociado.
    
    - **user_id**: ID del usuario
    """
    success = UserService.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return None


@router.post("/{user_id}/sync", response_model=UserResponse)
async def update_last_sync(user_id: int, db: Session = Depends(get_db)):
    """
    Actualizar timestamp de última sincronización.
    
    - **user_id**: ID del usuario
    """
    user = UserService.update_last_sync(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.get("/stats/count", response_model=dict)
async def get_users_count(db: Session = Depends(get_db)):
    """Obtener el número total de usuarios registrados."""
    count = UserService.count_users(db)
    return {"total_users": count}
