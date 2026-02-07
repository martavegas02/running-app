"""
Rutas para gestión de planes de entrenamiento.
Endpoints para crear, obtener, actualizar y regenerar planes.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import traceback
import math  # <--- IMPORTANTE: Necesario para la fórmula
from app.core.database import get_db
from app.services.planning_service import PlanningService

# IMPORTANTE: Asegúrate de que esta importación apunte a donde tienes definido tu modelo Activity
# Si tu archivo de modelos está en app/models.py, esto es correcto.
from app.models.database import Activity

router = APIRouter(prefix="/api/v1/planning", tags=["Training Plans"])

# --- FUNCIONES AUXILIARES PARA PREDICCIONES ---

def format_time(seconds: float) -> str:
    """Convierte segundos a formato HH:MM:SS o MM:SS"""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{int(h):d}:{int(m):02d}:{int(s):02d}"
    return f"{int(m):02d}:{int(s):02d}"

def format_pace(speed_ms: float) -> str:
    """Convierte m/s a min/km"""
    if speed_ms <= 0: return "0:00"
    seconds_per_km = 1000 / speed_ms
    m, s = divmod(seconds_per_km, 60)
    return f"{int(m)}:{int(s):02d}"

def riegel_prediction(time_t1: float, dist_d1: float, dist_d2: float) -> float:
    """
    Fórmula de Riegel: T2 = T1 * (D2 / D1)^1.06
    """
    if dist_d1 == 0: return 0
    return time_t1 * math.pow((dist_d2 / dist_d1), 1.06)

# --- ENDPOINTS EXISTENTES ---

@router.post("/generate-plan/{user_id}")
async def generate_training_plan(
    user_id: int,
    intensity_level: str = "beginner",
    db: Session = Depends(get_db),
):
    """
    Generar un nuevo plan de entrenamiento semanal.
    """
    try:
        result = PlanningService.generate_training_plan(
            db=db,
            user_id=user_id,
            intensity_level=intensity_level,
            training_days=["Monday", "Wednesday", "Saturday"],
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Error desconocido"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR en generate_training_plan: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/current-plan/{user_id}")
async def get_current_plan(user_id: int, db: Session = Depends(get_db)):
    """
    Obtener el plan actual de la semana para un usuario.
    """
    result = PlanningService.get_current_week_plan(db, user_id)
    
    if result["status"] == "not_found":
        raise HTTPException(status_code=404, detail="No hay plan para esta semana")
    
    return result["plan"]


@router.post("/skip-day/{session_id}")
async def skip_training_day(session_id: int, db: Session = Depends(get_db)):
    """
    Marcar un día como saltado y redistribuir el entrenamiento.
    """
    result = PlanningService.regenerate_plan_for_skipped_day(
        db=db,
        user_id=None,  # Se obtiene del session
        skipped_session_id=session_id,
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result.get("message"))
    
    return result


@router.post("/complete-session/{session_id}")
async def complete_training_session(
    session_id: int,
    actual_activity_id: int = None,
    db: Session = Depends(get_db),
):
    """
    Marcar una sesión como completada.
    """
    result = PlanningService.mark_session_completed(
        db=db,
        session_id=session_id,
        actual_activity_id=actual_activity_id,
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result.get("message"))
    
    return result

# --- NUEVOS ENDPOINTS DE PREDICCIÓN ---

@router.post("/predictions/calculate/{user_id}")
async def calculate_race_predictions(user_id: int, db: Session = Depends(get_db)):
    """
    Calcula predicciones de carrera basadas en el historial del usuario.
    """
    try:
        # 1. Obtener actividades del usuario
        activities = db.query(Activity).filter(Activity.user_id == user_id).all()
        
        if not activities:
            raise HTTPException(status_code=404, detail="El usuario no tiene actividades para analizar")

        # 2. Encontrar la "Mejor Actividad Base"
        # Filtramos actividades muy cortas (< 1km) o con datos erróneos
        valid_activities = [a for a in activities if a.distance > 1000 and a.average_speed > 0]
        
        if not valid_activities:
            # Si no hay válidas, devolvemos error o usamos la más larga disponible
            if activities:
                best_activity = max(activities, key=lambda x: x.distance)
            else:
                raise HTTPException(status_code=404, detail="No hay actividades válidas (>1km) para predecir")
        else:
            # De las válidas, tomamos la más rápida (mejor rendimiento relativo)
            best_activity = max(valid_activities, key=lambda x: x.average_speed)

        # Datos base (T1, D1)
        t1 = best_activity.duration  # segundos
        d1 = best_activity.distance  # metros

        # 3. Distancias objetivo (en metros)
        targets = {
            "5k": 5000,
            "10k": 10000,
            "half_marathon": 21097.5,
            "marathon": 42195
        }

        predictions = {}

        # 4. Calcular predicciones
        for key, d2 in targets.items():
            predicted_time_seconds = riegel_prediction(t1, d1, d2)
            
            # Calcular ritmo predicho (min/km)
            predicted_speed_ms = d2 / predicted_time_seconds
            
            predictions[key] = {
                "time": format_time(predicted_time_seconds),
                "pace": format_pace(predicted_speed_ms),
                "distance_meters": d2
            }

        return {
            "status": "success",
            "based_on_activity": {
                "name": best_activity.name,
                "date": best_activity.start_date,
                "distance": best_activity.distance,
                "pace": format_pace(best_activity.average_speed)
            },
            **predictions
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR calculando predicciones: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predictions/{user_id}")
async def get_predictions(user_id: int, db: Session = Depends(get_db)):
    """
    Obtiene las predicciones (reutiliza el cálculo).
    """
    return await calculate_race_predictions(user_id, db)