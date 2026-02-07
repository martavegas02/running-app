-- Script de inicialización de la base de datos
-- Running Analytics Hub

-- Extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    strava_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    profile_picture VARCHAR(500),
    strava_access_token VARCHAR(500),
    strava_refresh_token VARCHAR(500),
    strava_token_expires_at TIMESTAMP,
    strava_scope VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_sync TIMESTAMP
);

-- Tabla gear
CREATE TABLE IF NOT EXISTS gear (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    strava_id VARCHAR(100),
    name VARCHAR(255) NOT NULL,
    gear_type VARCHAR(50) NOT NULL,
    brand VARCHAR(255),
    model VARCHAR(255),
    description VARCHAR(1000),
    is_primary BOOLEAN DEFAULT FALSE,
    retired BOOLEAN DEFAULT FALSE,
    distance FLOAT DEFAULT 0,
    initial_purchase_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla activities
CREATE TABLE IF NOT EXISTS activities (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    strava_id BIGINT UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    description VARCHAR(2000),
    distance FLOAT NOT NULL,
    duration INTEGER NOT NULL,
    elevation_gain FLOAT,
    average_speed FLOAT,
    max_speed FLOAT,
    average_heart_rate FLOAT,
    max_heart_rate FLOAT,
    average_cadence FLOAT,
    start_date TIMESTAMP NOT NULL,
    start_date_local TIMESTAMP NOT NULL,
    timezone VARCHAR(100),
    weather VARCHAR(50),
    temperature FLOAT,
    humidity FLOAT,
    gear_id INTEGER REFERENCES gear(id),
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla sync_logs
CREATE TABLE IF NOT EXISTS sync_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    sync_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    message VARCHAR(500),
    activities_synced INTEGER DEFAULT 0,
    activities_skipped INTEGER DEFAULT 0,
    activities_failed INTEGER DEFAULT 0,
    error_details JSONB,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Tabla training_plans (Planes de entrenamiento generados por IA)
CREATE TABLE IF NOT EXISTS training_plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    week_start_date DATE NOT NULL,
    week_end_date DATE NOT NULL,
    intensity_level VARCHAR(20) NOT NULL,
    total_planned_km FLOAT,
    total_planned_duration INTEGER,
    training_days VARCHAR(50),
    goals TEXT,
    notes TEXT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_week UNIQUE(user_id, week_start_date)
);

-- Tabla training_sessions (Sesiones individuales del plan)
CREATE TABLE IF NOT EXISTS training_sessions (
    id SERIAL PRIMARY KEY,
    training_plan_id INTEGER NOT NULL REFERENCES training_plans(id) ON DELETE CASCADE,
    day_of_week VARCHAR(20) NOT NULL,
    date_scheduled DATE NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    planned_distance FLOAT,
    planned_duration INTEGER,
    planned_pace VARCHAR(50),
    intensity VARCHAR(20),
    description TEXT,
    warm_up TEXT,
    main_workout TEXT,
    cool_down TEXT,
    notes TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    completed BOOLEAN DEFAULT FALSE,
    actual_activity_id INTEGER REFERENCES activities(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para optimización
CREATE INDEX idx_users_strava_id ON users(strava_id);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_gear_user_id ON gear(user_id);
CREATE INDEX idx_gear_strava_id ON gear(strava_id);
CREATE INDEX idx_gear_type ON gear(gear_type);
CREATE INDEX idx_activities_user_id ON activities(user_id);
CREATE INDEX idx_activities_strava_id ON activities(strava_id);
CREATE INDEX idx_activities_type ON activities(activity_type);
CREATE INDEX idx_activities_start_date ON activities(start_date);
CREATE INDEX idx_activities_user_start_date ON activities(user_id, start_date);
CREATE INDEX idx_activities_user_type ON activities(user_id, activity_type);
CREATE INDEX idx_sync_logs_user_id ON sync_logs(user_id);
CREATE INDEX idx_sync_logs_status ON sync_logs(status);
CREATE INDEX idx_training_plans_user_id ON training_plans(user_id);
CREATE INDEX idx_training_plans_week_start ON training_plans(week_start_date);
CREATE INDEX idx_training_plans_status ON training_plans(status);
CREATE INDEX idx_training_sessions_plan_id ON training_sessions(training_plan_id);
CREATE INDEX idx_training_sessions_date ON training_sessions(date_scheduled);
CREATE INDEX idx_training_sessions_status ON training_sessions(status);

-- Tablas creadas exitosamente
\echo 'Database initialization completed successfully!'
