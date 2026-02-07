from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://strava_user:strava_secure_pass_2025@localhost:5432/running_analytics"
)

# Crear el motor de base de datos
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Cambiar a True para ver las queries SQL en la consola
    pool_pre_ping=True,  # Verificar la conexión antes de usarla
    pool_size=10,
    max_overflow=20
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency para obtener una sesión de base de datos en FastAPI.
    Uso: def my_route(db: Session = Depends(get_db)):
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inicializar la base de datos creando todas las tablas.
    """
    from app.models.database import Base
    Base.metadata.create_all(bind=engine)
