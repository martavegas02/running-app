"""
Servicio de planificación de entrenamiento inteligente.
Genera planes personalizados basados en historial de actividades.
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.database import TrainingPlan, TrainingSession, Activity, User
import traceback # Importante para ver errores en logs

class PlanningService:
    """Servicio para generar planes de entrenamiento inteligentes."""

    @staticmethod
    def get_user_activity_stats(db: Session, user_id: int) -> dict:
        """Obtener estadísticas de las actividades del usuario."""
        activities = db.query(Activity).filter(
            Activity.user_id == user_id,
            Activity.activity_type == "run"
        ).all()

        if not activities:
            return {
                "total_activities": 0,
                "average_distance_km": 0,
                "average_duration_minutes": 0,
                "average_pace_min_km": "N/A",
                "max_distance_km": 0,
                "total_distance_km": 0,
                "last_activity": None,
            }

        total_distance = sum(a.distance for a in activities)
        total_duration = sum(a.duration for a in activities)
        avg_distance = total_distance / len(activities) / 1000
        avg_duration = total_duration / len(activities) / 60
        max_distance = max(a.distance for a in activities) / 1000

        avg_speed = (total_distance / total_duration) if total_duration > 0 else 0
        avg_pace = (1000 / avg_speed / 60) if avg_speed > 0 else 0

        return {
            "total_activities": len(activities),
            "average_distance_km": round(avg_distance, 2),
            "average_duration_minutes": round(avg_duration, 2),
            "average_pace_min_km": f"{int(avg_pace)}:{int((avg_pace % 1) * 60):02d}",
            "max_distance_km": round(max_distance, 2),
            "total_distance_km": round(total_distance / 1000, 2),
            "last_activity": activities[-1].start_date.isoformat() if activities else None,
        }

    # --- NUEVO MÉTODO: JUEZ DE NIVEL ---
    @staticmethod
    def _determine_level_from_stats(stats: dict) -> str:
        """
        Clasifica al usuario automáticamente según su historial reciente.
        """
        # Si tiene muy pocas actividades, es principiante
        if stats["total_activities"] < 5:
            return "beginner"

        avg_dist = stats["average_distance_km"]
        
        # 1. PRINCIPIANTE: Media < 5km
        if avg_dist < 5.0:
            return "beginner"
        
        # 2. INTERMEDIO: Media entre 5km y 12km
        elif 5.0 <= avg_dist < 12.0:
            return "intermediate"
            
        # 3. PROFESIONAL (Advanced): Media > 12km
        else:
            return "advanced"

    @staticmethod
    def generate_training_plan(
        db: Session,
        user_id: int,
        training_days: list = None,
        intensity_level: str = "auto", # Default a AUTO para que decida el sistema
        start_date: datetime = None,
    ) -> dict:
        """Generar un plan de entrenamiento inteligente."""
        
        try:
            if training_days is None:
                training_days = ["Monday", "Wednesday", "Saturday"]
            
            if start_date is None:
                today = datetime.now()
                days_ahead = 0 - today.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                start_date = today + timedelta(days=days_ahead)

            # 1. Obtener estadísticas reales
            user_stats = PlanningService.get_user_activity_stats(db, user_id)
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                return {"status": "error", "message": "Usuario no encontrado"}

            # --- LÓGICA DE AUTO-DETECCIÓN ---
            final_level = intensity_level
            
            # Si el usuario pidió "auto" o "beginner" (para forzar update), recalculamos
            if intensity_level == "auto" or intensity_level == "beginner":
                detected_level = PlanningService._determine_level_from_stats(user_stats)
                # Aplicamos el nivel detectado
                final_level = detected_level

            # 2. Generar estructura del plan con el nivel FINAL
            plan_data = PlanningService._generate_intelligent_plan(
                stats=user_stats,
                training_days=training_days,
                intensity_level=final_level,
                week_start=start_date,
            )

            # 3. Guardar en BD
            training_plan = PlanningService._save_training_plan(
                db, user_id, start_date, plan_data, final_level
            )

            return {
                "status": "success",
                "plan_id": training_plan.id,
                "message": f"Plan generado nivel {final_level.upper()}",
                "plan": plan_data,
            }

        except Exception as e:
            traceback.print_exc()
            return {
                "status": "error",
                "message": f"Error: {str(e)}",
            }

    @staticmethod
    def _generate_intelligent_plan(stats, training_days, intensity_level, week_start):
        """Generar plan inteligente basado en estadísticas."""
        
        week_end = week_start + timedelta(days=6)
        
        # Ajuste de base según estadísticas
        if stats["total_activities"] == 0:
            base_distance = 5.0
        else:
            base_distance = stats["average_distance_km"]
            # Safety Cap: No subir más del 5% de la media, ni superar el 80% del máximo histórico
            base_distance = min(base_distance * 1.05, stats["max_distance_km"] * 0.8)
            # Mínimo de seguridad para que el plan no sea de 0km
            if base_distance < 2.0: base_distance = 2.0
        
        if stats["total_activities"] == 0:
            base_duration = 30
        else:
            base_duration = int(stats["average_duration_minutes"])
            if base_duration < 15: base_duration = 15
        
        sessions = []
        day_mapping = {
            "Monday": 0, "Tuesday": 1, "Wednesday": 2, 
            "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6
        }
        
        training_days_sorted = sorted(training_days, key=lambda x: day_mapping.get(x, 7))
        
        for idx, day_name in enumerate(training_days_sorted):
            day_num = day_mapping.get(day_name, 0)
            session_date = week_start + timedelta(days=day_num)
            
            # Asignación de roles según posición en la semana
            if idx == 0:
                intensity = "easy"
                distance_multiplier = 0.8
                pace_adjustment = 0.9
                description = "Carrera fácil de recuperación/técnica"
                main_workout = f"{int((base_duration * distance_multiplier))} min a ritmo conversacional"
            elif idx == len(training_days_sorted) - 1:
                intensity = "long_easy"
                distance_multiplier = 1.2 # Tirada larga
                pace_adjustment = 0.95
                description = "Tirada larga: Construcción de fondo"
                main_workout = f"{int(base_duration * distance_multiplier)} min a ritmo constante y cómodo"
            else:
                intensity = "moderate"
                distance_multiplier = 1.0
                pace_adjustment = 1.05 # Un poco más rápido
                description = "Carrera de calidad / Ritmo"
                main_workout = f"{int(base_duration)} min con cambios de ritmo si te sientes bien"
            
            # Ajuste extra si es Profesional/Advanced
            if intensity_level == "advanced":
                distance_multiplier *= 1.15 # 15% más de volumen para pros
            
            session_distance = base_distance * distance_multiplier
            session_duration = int(base_duration * distance_multiplier)
            
            # Cálculo de ritmos
            if stats["average_pace_min_km"] != "N/A":
                try:
                    parts = stats["average_pace_min_km"].split(":")
                    avg_pace_min = int(parts[0]) + int(parts[1]) / 60
                    # Si es advanced, exigimos más velocidad
                    if intensity_level == "advanced": pace_adjustment *= 1.05
                    
                    target_pace_min = avg_pace_min / pace_adjustment
                    session_pace = f"{int(target_pace_min)}:{int((target_pace_min % 1) * 60):02d} min/km"
                except:
                    session_pace = "Según sensaciones"
            else:
                session_pace = "6:00 min/km"
            
            session = {
                "day_of_week": day_name,
                "date": session_date.strftime("%Y-%m-%d"),
                "activity_type": "run",
                "planned_distance_km": round(session_distance, 1),
                "planned_duration_minutes": session_duration,
                "planned_pace": session_pace,
                "intensity": intensity,
                "description": description,
                "warm_up": "5-10 min trote muy suave",
                "main_workout": main_workout,
                "cool_down": "5 min caminar",
                "notes": PlanningService._get_session_notes(intensity),
            }
            sessions.append(session)
        
        total_km = sum(s["planned_distance_km"] for s in sessions)
        
        return {
            "week_number": 1,
            "intensity_level": intensity_level,
            "total_planned_km": round(total_km, 1),
            "goals": PlanningService._get_goals(intensity_level),
            "notes": PlanningService._get_plan_notes(intensity_level, stats),
            "sessions": sessions,
        }

    @staticmethod
    def _get_goals(intensity_level):
        """Obtener objetivos según nivel."""
        if intensity_level == "beginner":
            return "Mejorar resistencia de forma segura, construir hábito regular"
        elif intensity_level == "intermediate":
            return "Aumentar velocidad y resistencia progresivamente"
        else: # advanced
            return "NIVEL PROFESIONAL: Maximizar rendimiento y velocidad de competición."

    @staticmethod
    def _get_plan_notes(intensity_level, stats):
        """Obtener notas del plan."""
        notes = "Plan generado inteligentemente según tu historial. "
        
        if intensity_level == "beginner":
            notes += "Nivel: PRINCIPIANTE. Máximo 10% aumento por semana. Escucha tu cuerpo."
        elif intensity_level == "intermediate":
            notes += "Nivel: INTERMEDIO. Ya tienes base, ahora buscamos mejora de ritmo."
        else:
            notes += "Nivel: PROFESIONAL. Entrenamiento de alta carga y volumen."
            
        if stats["total_activities"] == 0:
            notes += " Sin historial: empieza lentamente."
        else:
            notes += f" Promedio actual: {stats['average_distance_km']}km por salida."
        
        return notes

    @staticmethod
    def _get_session_notes(intensity):
        """Obtener notas por sesión."""
        if intensity == "easy":
            return "Ritmo suave. Recuperación activa."
        elif intensity == "moderate":
            return "Zona de confort-dura. Mantén la técnica."
        elif intensity == "long_easy":
            return "Fondo físico. No te preocupes por la velocidad, solo termina."
        return "Escucha tu cuerpo."

    @staticmethod
    def _save_training_plan(db: Session, user_id: int, start_date: datetime, plan_data: dict, intensity_level: str):
        """Guardar el plan en la BD."""
        
        end_date = start_date + timedelta(days=6)
        
        # Eliminar plan existente para esa semana
        existing_plan = db.query(TrainingPlan).filter(
            TrainingPlan.user_id == user_id,
            TrainingPlan.week_start_date >= start_date - timedelta(days=1),
            TrainingPlan.week_start_date <= start_date + timedelta(days=1),
        ).first()
        
        if existing_plan:
            db.query(TrainingSession).filter(
                TrainingSession.training_plan_id == existing_plan.id
            ).delete()
            db.delete(existing_plan)
            db.flush()
        
        training_plan = TrainingPlan(
            user_id=user_id,
            week_start_date=start_date,
            week_end_date=end_date,
            intensity_level=intensity_level,
            total_planned_km=plan_data.get("total_planned_km", 0),
            training_days=", ".join([s["day_of_week"] for s in plan_data.get("sessions", [])]),
            goals=plan_data.get("goals", ""),
            notes=plan_data.get("notes", ""),
            status="active",
        )
        
        db.add(training_plan)
        db.flush()
        
        for session_data in plan_data.get("sessions", []):
            try:
                date_str = session_data.get("date", "")
                date_scheduled = datetime.strptime(date_str, "%Y-%m-%d").replace(hour=9, minute=0)
                
                session = TrainingSession(
                    training_plan_id=training_plan.id,
                    day_of_week=session_data.get("day_of_week", ""),
                    date_scheduled=date_scheduled,
                    activity_type=session_data.get("activity_type", "run"),
                    planned_distance=session_data.get("planned_distance_km", 0),
                    planned_duration=session_data.get("planned_duration_minutes", 0),
                    planned_pace=session_data.get("planned_pace", ""),
                    intensity=session_data.get("intensity", ""),
                    description=session_data.get("description", ""),
                    warm_up=session_data.get("warm_up", ""),
                    main_workout=session_data.get("main_workout", ""),
                    cool_down=session_data.get("cool_down", ""),
                    notes=session_data.get("notes", ""),
                    status="pending",
                )
                db.add(session)
            except Exception as e:
                print(f"Error en sesión: {e}")
                continue
        
        db.commit()
        db.refresh(training_plan)
        return training_plan

    @staticmethod
    def get_current_week_plan(db: Session, user_id: int) -> dict:
        """Obtener plan actual."""
        
        # Buscar plan de la semana actual o próxima semana
        plan = db.query(TrainingPlan).filter(
            TrainingPlan.user_id == user_id,
            TrainingPlan.status == "active",
        ).order_by(TrainingPlan.week_start_date.desc()).first()
        
        if not plan:
            return {"status": "not_found", "message": "Sin plan para esta semana"}
        
        sessions = db.query(TrainingSession).filter(
            TrainingSession.training_plan_id == plan.id
        ).order_by(TrainingSession.date_scheduled).all()
        
        return {
            "status": "success",
            "plan": {
                "id": plan.id,
                "week_start": plan.week_start_date.isoformat(),
                "week_end": plan.week_end_date.isoformat(),
                "intensity_level": plan.intensity_level,
                "goals": plan.goals,
                "notes": plan.notes,
                "total_planned_km": plan.total_planned_km,
                "sessions": [
                    {
                        "id": s.id,
                        "day": s.day_of_week,
                        "date": s.date_scheduled.isoformat(),
                        "activity_type": s.activity_type,
                        "planned_distance": s.planned_distance,
                        "planned_duration": s.planned_duration,
                        "planned_pace": s.planned_pace,
                        "intensity": s.intensity,
                        "description": s.description,
                        "main_workout": s.main_workout,
                        "status": s.status,
                        "completed": s.completed,
                        "notes": s.notes,
                        "warm_up": s.warm_up,
                        "cool_down": s.cool_down
                    }
                    for s in sessions
                ],
            },
        }

    @staticmethod
    def regenerate_plan_for_skipped_day(db: Session, user_id: int, skipped_session_id: int) -> dict:
        """Regenerar plan cuando se salta un día."""
        
        session = db.query(TrainingSession).filter(TrainingSession.id == skipped_session_id).first()
        
        if not session:
            return {"status": "error", "message": "Sesión no encontrada"}
        
        plan = session.plan
        session.status = "skipped"
        session.completed = False
        
        all_sessions = db.query(TrainingSession).filter(
            TrainingSession.training_plan_id == plan.id
        ).all()
        
        skipped_distance = session.planned_distance or 0
        
        if all_sessions:
            remaining = [s for s in all_sessions if s.id != skipped_session_id and s.status == "pending"]
            if remaining:
                # Repartir el 50% de la distancia perdida entre los días restantes
                extra = skipped_distance / len(remaining) * 0.5
                for s in remaining:
                    s.planned_distance = (s.planned_distance or 0) + extra
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Plan reajustado",
            "plan_id": plan.id,
        }

    @staticmethod
    def mark_session_completed(db: Session, session_id: int, actual_activity_id: int = None) -> dict:
        """Marcar sesión como completada."""
        
        session = db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
        
        if not session:
            return {"status": "error", "message": "Sesión no encontrada"}
        
        session.status = "completed"
        session.completed = True
        session.actual_activity_id = actual_activity_id
        session.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {"status": "success", "message": "Sesión completada"}