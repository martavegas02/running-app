from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Importar modelos y base de datos
from app.core.database import init_db, engine
from app.models.database import Base

# Importar routers
from app.routes import users, activities, gear, auth, sync, planning

# Crear tablas
Base.metadata.create_all(bind=engine)

# Inicializar FastAPI
app = FastAPI(
    title="Running Analytics Hub",
    description="API para sincronizar datos de Strava y generar análisis avanzados",
    version="0.2.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, cambiar a ["http://localhost:8501"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(activities.router)
app.include_router(gear.router)
app.include_router(sync.router)
app.include_router(planning.router)


# ===== RUTAS =====
@app.get("/", tags=["Health"])
async def root():
    """
    Endpoint raíz para verificar que la API está funcionando.
    """
    return {
        "message": "Bienvenido a Running Analytics Hub",
        "version": "0.1.0",
        "status": "online"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check de la API.
    """
    return {
        "status": "healthy",
        "message": "API is running"
    }


@app.get("/api/v1/", tags=["API"])
async def api_root():
    """
    Raíz de la API v1.
    """
    return {
        "message": "Running Analytics Hub API v1",
        "endpoints": {
            "users": "/api/v1/users",
            "activities": "/api/v1/activities",
            "gear": "/api/v1/gear",
            "sync": "/api/v1/sync",
            "analytics": "/api/v1/analytics"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
