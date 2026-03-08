from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routes import users, activities, gear, auth, sync, planning
from app.core.database import engine
from app.models.database import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Running Analytics API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas con prefijo
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(activities.router, prefix="/api/v1")
app.include_router(sync.router, prefix="/api/v1")
app.include_router(planning.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"status": "online", "message": "API Running Analytics"}

# Ruta de salud para Streamlit
@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy"}