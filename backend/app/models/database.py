from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, Index, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """
    Modelo de usuario.
    Almacena la información del atleta de Strava conectado.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    strava_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    profile_picture = Column(String(500), nullable=True)
    
    # Tokens OAuth de Strava
    strava_access_token = Column(String(500), nullable=True)
    strava_refresh_token = Column(String(500), nullable=True)
    strava_token_expires_at = Column(DateTime, nullable=True)
    strava_scope = Column(String(255), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sync = Column(DateTime, nullable=True)
    
    # Relaciones
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")
    gear = relationship("Gear", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.username}>"


class Activity(Base):
    """
    Modelo de actividades (carreras).
    Almacena los datos sincronizados desde Strava.
    """
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    strava_id = Column(BigInteger, unique=True, nullable=False, index=True)
    
    # Información básica
    name = Column(String(500), nullable=False)
    activity_type = Column(String(50), nullable=False, index=True)  # run, walk, ride, etc.
    description = Column(String(2000), nullable=True)
    
    # Datos de la actividad
    distance = Column(Float, nullable=False)  # en metros
    duration = Column(Integer, nullable=False)  # en segundos
    elevation_gain = Column(Float, nullable=True)  # en metros
    average_speed = Column(Float, nullable=True)  # m/s
    max_speed = Column(Float, nullable=True)  # m/s
    average_heart_rate = Column(Float, nullable=True)
    max_heart_rate = Column(Float, nullable=True)
    average_cadence = Column(Float, nullable=True)
    
    # Ubicación y tiempo
    start_date = Column(DateTime, nullable=False, index=True)
    start_date_local = Column(DateTime, nullable=False)
    timezone = Column(String(100), nullable=True)
    
    # Condiciones
    weather = Column(String(50), nullable=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    
    # Equipo
    gear_id = Column(Integer, ForeignKey("gear.id"), nullable=True)
    
    # Raw data de Strava (para auditoría y análisis futuro)
    raw_data = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    synced_at = Column(DateTime, default=datetime.utcnow)
    
    # Índices para búsquedas rápidas
    __table_args__ = (
        Index('idx_user_start_date', 'user_id', 'start_date'),
        Index('idx_user_activity_type', 'user_id', 'activity_type'),
        Index('idx_start_date', 'start_date'),
    )
    
    # Relaciones
    user = relationship("User", back_populates="activities")
    gear_rel = relationship("Gear", back_populates="activities")
    
    def __repr__(self):
        return f"<Activity {self.name} - {self.start_date}>"


class Gear(Base):
    """
    Modelo de equipamiento (zapatillas, bicicletas, etc.).
    Permite rastrear el desgaste por modelo.
    """
    __tablename__ = "gear"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    strava_id = Column(String(100), nullable=True, index=True)
    
    # Información del equipo
    name = Column(String(255), nullable=False)
    gear_type = Column(String(50), nullable=False, index=True)  # shoes, bike, etc.
    brand = Column(String(255), nullable=True)
    model = Column(String(255), nullable=True)
    description = Column(String(1000), nullable=True)
    
    # Datos de desgaste
    is_primary = Column(Boolean, default=False)
    retired = Column(Boolean, default=False)
    distance = Column(Float, default=0)  # en metros (sincronizado de Strava)
    initial_purchase_date = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", back_populates="gear")
    activities = relationship("Activity", back_populates="gear_rel")
    
    def __repr__(self):
        return f"<Gear {self.name}>"


class SyncLog(Base):
    """
    Modelo para auditar las sincronizaciones con Strava.
    Útil para debugging y para saber si hubo errores.
    """
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Información del sync
    sync_type = Column(String(50), nullable=False)  # full, incremental, gear, etc.
    status = Column(String(20), nullable=False)  # success, error, warning
    message = Column(String(500), nullable=True)
    
    # Estadísticas
    activities_synced = Column(Integer, default=0)
    activities_skipped = Column(Integer, default=0)
    activities_failed = Column(Integer, default=0)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Error handling
    error_details = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<SyncLog {self.sync_type} - {self.status}>"


class TrainingPlan(Base):
    """
    Modelo de plan de entrenamiento generado por IA.
    Cada usuario puede tener un plan activo por semana.
    """
    __tablename__ = "training_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Información de la semana
    week_start_date = Column(DateTime, nullable=False)
    week_end_date = Column(DateTime, nullable=False)
    
    # Datos del plan
    intensity_level = Column(String(20), nullable=False)  # beginner, intermediate, advanced
    total_planned_km = Column(Float, nullable=True)
    total_planned_duration = Column(Integer, nullable=True)  # en segundos
    training_days = Column(String(50), nullable=True)  # "Monday, Wednesday, Saturday"
    goals = Column(String(1000), nullable=True)
    notes = Column(String(2000), nullable=True)
    
    # Estado
    status = Column(String(20), default="active")  # active, completed, archived
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", backref="training_plans")
    sessions = relationship("TrainingSession", back_populates="plan", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TrainingPlan Week {self.week_start_date}>"


class TrainingSession(Base):
    """
    Modelo para cada sesión de entrenamiento dentro de un plan.
    Representa un día específico de entrenamiento.
    """
    __tablename__ = "training_sessions"

    id = Column(Integer, primary_key=True, index=True)
    training_plan_id = Column(Integer, ForeignKey("training_plans.id"), nullable=False, index=True)
    
    # Información del día
    day_of_week = Column(String(20), nullable=False)  # Monday, Wednesday, Saturday
    date_scheduled = Column(DateTime, nullable=False)
    
    # Datos planeados
    activity_type = Column(String(50), nullable=False)  # run, walk, etc.
    planned_distance = Column(Float, nullable=True)  # en km
    planned_duration = Column(Integer, nullable=True)  # en minutos
    planned_pace = Column(String(50), nullable=True)  # e.g., "6:30 min/km"
    intensity = Column(String(20), nullable=True)  # easy, tempo, hard, recovery
    
    # Detalles de la sesión
    description = Column(String(1000), nullable=True)
    warm_up = Column(String(500), nullable=True)
    main_workout = Column(String(1000), nullable=True)
    cool_down = Column(String(500), nullable=True)
    notes = Column(String(500), nullable=True)
    
    # Estado
    status = Column(String(20), default="pending")  # pending, skipped, completed
    completed = Column(Boolean, default=False)
    actual_activity_id = Column(Integer, ForeignKey("activities.id"), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    plan = relationship("TrainingPlan", back_populates="sessions")
    actual_activity = relationship("Activity")
    
    def __repr__(self):
        return f"<TrainingSession {self.day_of_week} - {self.activity_type}>"




