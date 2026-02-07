"""
Auth Service - Manejo de autenticación OAuth con Strava
"""
import os
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.models.database import User
from app.schemas import UserCreate

# Configuración
STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI")
STRAVA_API_URL = "https://www.strava.com/api/v3"
STRAVA_OAUTH_URL = "https://www.strava.com/oauth/authorize"
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Servicio de autenticación OAuth con Strava"""

    @staticmethod
    def get_strava_oauth_url(state: Optional[str] = None) -> str:
        """
        Obtiene la URL de autorización de Strava
        
        Args:
            state: Token CSRF opcional para validación
            
        Returns:
            URL de autorización de Strava
        """
        params = {
            "client_id": STRAVA_CLIENT_ID,
            "redirect_uri": STRAVA_REDIRECT_URI,
            "response_type": "code",
            "scope": "read,activity:read_all",
            "approval_prompt": "auto",
        }
        
        if state:
            params["state"] = state
            
        param_str = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{STRAVA_OAUTH_URL}?{param_str}"

    @staticmethod
    async def exchange_code_for_token(code: str) -> Dict[str, Any]:
        """
        Intercambia el código de autorización por tokens
        
        Args:
            code: Código de autorización de Strava
            
        Returns:
            Dict con access_token, refresh_token, athlete info
            
        Raises:
            ValueError: Si el intercambio falla
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                STRAVA_TOKEN_URL,
                data={
                    "client_id": STRAVA_CLIENT_ID,
                    "client_secret": STRAVA_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                },
            )
            
            if response.status_code != 200:
                raise ValueError(f"Strava token exchange failed: {response.text}")
            
            return response.json()

    @staticmethod
    async def get_athlete_data(access_token: str) -> Dict[str, Any]:
        """
        Obtiene datos del atleta desde Strava
        
        Args:
            access_token: Token de acceso de Strava
            
        Returns:
            Dict con datos del atleta
            
        Raises:
            ValueError: Si la solicitud falla
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{STRAVA_API_URL}/athlete",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            
            if response.status_code != 200:
                raise ValueError(f"Failed to get athlete data: {response.text}")
            
            return response.json()

    @staticmethod
    def create_or_update_user(
        db: Session, strava_data: Dict[str, Any], tokens: Dict[str, str]
    ) -> User:
        """
        Crea o actualiza un usuario basado en datos de Strava
        
        Args:
            db: Sesión de base de datos
            strava_data: Datos del atleta de Strava
            tokens: Tokens de acceso y refresco
            
        Returns:
            Objeto User creado o actualizado
            
        Raises:
            ValueError: Si hay error en la creación
        """
        strava_id = strava_data.get("id")
        username = strava_data.get("username") or f"strava_{strava_id}"
        email = strava_data.get("email")
        first_name = strava_data.get("firstname", "")
        last_name = strava_data.get("lastname", "")
        
        # Buscar usuario existente
        existing_user = db.query(User).filter_by(strava_id=strava_id).first()
        
        if existing_user:
            # Actualizar tokens
            existing_user.strava_access_token = tokens.get("access_token")
            existing_user.strava_refresh_token = tokens.get("refresh_token")
            existing_user.strava_token_expires_at = datetime.utcnow() + timedelta(
                seconds=tokens.get("expires_in", 21600)
            )
            existing_user.strava_scope = tokens.get("scope", "read,activity:read_all")
            existing_user.last_sync = datetime.utcnow()
            
            db.commit()
            db.refresh(existing_user)
            return existing_user
        
        # Crear nuevo usuario
        try:
            db_user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                strava_id=strava_id,
                strava_access_token=tokens.get("access_token"),
                strava_refresh_token=tokens.get("refresh_token"),
                strava_token_expires_at=datetime.utcnow()
                + timedelta(seconds=tokens.get("expires_in", 21600)),
                strava_scope=tokens.get("scope", "read,activity:read_all"),
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
            
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Error al crear usuario: {str(e)}")

    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Crea un JWT access token
        
        Args:
            data: Datos a incluir en el token
            expires_delta: Tiempo de expiración opcional
            
        Returns:
            JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verifica y decodifica un JWT token
        
        Args:
            token: JWT token a verificar
            
        Returns:
            Dict con datos del token o None si es inválido
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None

    @staticmethod
    async def refresh_strava_token(db: Session, user_id: int) -> Optional[str]:
        """
        Refresca el token de Strava si ha expirado
        
        Args:
            db: Sesión de base de datos
            user_id: ID del usuario
            
        Returns:
            Nuevo access token o None si falla
        """
        user = db.query(User).filter_by(id=user_id).first()
        if not user or not user.strava_refresh_token:
            return None
        
        # Verificar si el token ha expirado
        if user.strava_token_expires_at and user.strava_token_expires_at > datetime.utcnow():
            return user.strava_access_token
        
        # Refrescar token
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    STRAVA_TOKEN_URL,
                    data={
                        "client_id": STRAVA_CLIENT_ID,
                        "client_secret": STRAVA_CLIENT_SECRET,
                        "grant_type": "refresh_token",
                        "refresh_token": user.strava_refresh_token,
                    },
                )
                
                if response.status_code != 200:
                    return None
                
                tokens = response.json()
                user.strava_access_token = tokens.get("access_token")
                user.strava_refresh_token = tokens.get("refresh_token")
                user.strava_token_expires_at = datetime.utcnow() + timedelta(
                    seconds=tokens.get("expires_in", 21600)
                )
                
                db.commit()
                return user.strava_access_token
                
        except Exception:
            return None

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica una contraseña contra su hash"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Genera un hash de contraseña"""
        return pwd_context.hash(password)
