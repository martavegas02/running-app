"""
Routes - Autenticación OAuth con Strava
Endpoints: /auth/strava/login, /auth/strava/callback, /auth/refresh, /auth/me
"""
import secrets
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.database import User
from app.services.auth_service import AuthService
from app.schemas import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Para almacenar estados CSRF en memoria (en producción usar Redis)
csrf_states = set()


@router.get("/strava/login")
async def strava_login():
    """
    Inicia el flujo de autenticación OAuth con Strava
    
    Redirige al usuario a Strava para autorización
    """
    state = secrets.token_urlsafe(32)
    csrf_states.add(state)
    
    oauth_url = AuthService.get_strava_oauth_url(state=state)
    
    return {
        "message": "Redirige a esta URL para autenticarte con Strava",
        "oauth_url": oauth_url,
    }


@router.get("/strava/callback")
async def strava_callback(
    code: str = Query(..., description="Código de autorización de Strava"),
    state: str = Query(..., description="Token CSRF para validación"),
    db: Session = Depends(get_db),
):
    """
    Callback de Strava después de autorización
    
    Intercambia el código por tokens y crea/actualiza el usuario
    
    Args:
        code: Código de autorización
        state: Token CSRF para validación
        db: Sesión de base de datos
        
    Returns:
        Access token JWT y datos del usuario
        
    Raises:
        HTTPException 400: Si la validación falla
        HTTPException 500: Si hay error en Strava
    """
    # Validar estado CSRF
    if state not in csrf_states:
        raise HTTPException(
            status_code=400,
            detail="Invalid state token. Posible ataque CSRF",
        )
    
    csrf_states.discard(state)
    
    try:
        # Intercambiar código por tokens
        tokens = await AuthService.exchange_code_for_token(code)
        
        # Obtener datos del atleta
        athlete_data = await AuthService.get_athlete_data(tokens["access_token"])
        
        # Crear o actualizar usuario
        user = AuthService.create_or_update_user(db, athlete_data, tokens)
        
        # Crear JWT token
        access_token = AuthService.create_access_token(
            data={"sub": str(user.id), "user_id": user.id}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse.from_orm(user),
            "message": "Autenticación exitosa",
        }
        
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error durante autenticación: {str(e)}",
        )


@router.post("/refresh")
async def refresh_access_token(
    user_id: int = Query(..., description="ID del usuario"),
    db: Session = Depends(get_db),
):
    """
    Refresca el token de acceso JWT
    
    También refresca el token de Strava si ha expirado
    
    Args:
        user_id: ID del usuario
        db: Sesión de base de datos
        
    Returns:
        Nuevo access token JWT
        
    Raises:
        HTTPException 404: Si el usuario no existe
    """
    user = db.query(User).filter_by(id=user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Refrescar token de Strava si es necesario
    new_strava_token = await AuthService.refresh_strava_token(db, user_id)
    
    # Crear nuevo JWT
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id), "user_id": user.id}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "strava_token_refreshed": new_strava_token is not None,
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: int = Query(..., description="ID del usuario desde JWT"),
    db: Session = Depends(get_db),
):
    """
    Obtiene datos del usuario autenticado
    
    Args:
        user_id: ID del usuario (obtenido del JWT)
        db: Sesión de base de datos
        
    Returns:
        Datos del usuario autenticado
        
    Raises:
        HTTPException 404: Si el usuario no existe
    """
    user = db.query(User).filter_by(id=user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return user


@router.post("/logout")
async def logout():
    """
    Endpoint para logout (invalida el token en el cliente)
    
    En un cliente, simplemente descartar el token JWT
    """
    return {
        "message": "Desconectado exitosamente",
        "action": "Elimina el token JWT del cliente",
    }


@router.get("/strava/token-status")
async def check_strava_token_status(
    user_id: int = Query(..., description="ID del usuario"),
    db: Session = Depends(get_db),
):
    """
    Verifica el estado del token de Strava
    
    Args:
        user_id: ID del usuario
        db: Sesión de base de datos
        
    Returns:
        Estado del token (válido, expirado, etc.)
        
    Raises:
        HTTPException 404: Si el usuario no existe
    """
    from datetime import datetime
    
    user = db.query(User).filter_by(id=user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if not user.strava_access_token:
        return {
            "status": "no_token",
            "message": "No hay token de Strava vinculado",
        }
    
    expires_at = user.strava_token_expires_at
    is_expired = expires_at and expires_at <= datetime.utcnow()
    
    return {
        "status": "expired" if is_expired else "valid",
        "expires_at": expires_at,
        "scope": user.strava_scope,
        "has_refresh_token": bool(user.strava_refresh_token),
    }
