# 📚 Documentación de Endpoints CRUD - Running Analytics Hub

## 🚀 Acceso a la Documentación Interactiva

Una vez que levantes los servicios con `docker-compose up -d`, accede a:

- **Swagger UI** (Recomendado): http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

En Swagger UI puedes probar todos los endpoints directamente.

---

## 🔑 Base URL
```
http://localhost:8000/api/v1
```

---

## 👥 USUARIOS (Users)

### 1. Crear Usuario
```http
POST /users
Content-Type: application/json

{
  "strava_id": 12345678,
  "username": "john_runner",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "access_token": "abc123token456",
  "refresh_token": "refresh789",
  "token_expires_at": "2025-01-30T10:00:00"
}
```

**Respuesta (201):**
```json
{
  "id": 1,
  "strava_id": 12345678,
  "username": "john_runner",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "profile_picture": null,
  "created_at": "2025-12-30T10:00:00",
  "updated_at": "2025-12-30T10:00:00",
  "last_sync": null
}
```

---

### 2. Obtener Todos los Usuarios
```http
GET /users?skip=0&limit=100
```

**Query Parameters:**
- `skip` (int): Número de registros a saltar (default: 0)
- `limit` (int): Número máximo de registros (default: 100, máximo: 1000)

---

### 3. Obtener Usuario por ID
```http
GET /users/1
```

---

### 4. Obtener Usuario por Username
```http
GET /users/by-username/john_runner
```

---

### 5. Obtener Usuario por Strava ID
```http
GET /users/by-strava/12345678
```

---

### 6. Actualizar Usuario
```http
PUT /users/1
Content-Type: application/json

{
  "email": "newemail@example.com",
  "first_name": "Juan",
  "access_token": "new_token_xyz"
}
```

---

### 7. Eliminar Usuario (⚠️)
```http
DELETE /users/1
```

⚠️ **Cuidado**: Esto eliminará todas sus actividades y equipo.

---

### 8. Actualizar Last Sync
```http
POST /users/1/sync
```

Actualiza el timestamp de última sincronización.

---

### 9. Contar Usuarios
```http
GET /users/stats/count
```

**Respuesta:**
```json
{
  "total_users": 5
}
```

---

## 🏃 ACTIVIDADES (Activities)

### 1. Crear Actividad
```http
POST /activities
Content-Type: application/json

{
  "user_id": 1,
  "strava_id": 9876543210,
  "name": "Morning Run - Central Park",
  "activity_type": "run",
  "description": "Great run this morning!",
  "distance": 10000,
  "duration": 2400,
  "elevation_gain": 150,
  "average_speed": 4.17,
  "max_speed": 5.5,
  "average_heart_rate": 145,
  "max_heart_rate": 165,
  "average_cadence": 170,
  "start_date": "2025-12-30T06:00:00",
  "start_date_local": "2025-12-30T01:00:00",
  "timezone": "America/New_York",
  "weather": "Clear",
  "temperature": 15,
  "humidity": 60,
  "gear_id": 1,
  "raw_data": {}
}
```

---

### 2. Obtener Todas las Actividades
```http
GET /activities?skip=0&limit=100
```

---

### 3. Obtener Actividad por ID
```http
GET /activities/1
```

---

### 4. Obtener Actividad por Strava ID
```http
GET /activities/by-strava/9876543210
```

---

### 5. Obtener Actividades de un Usuario
```http
GET /activities/user/1?skip=0&limit=100&activity_type=run
```

**Query Parameters:**
- `activity_type` (str): Filtrar por tipo (run, walk, ride, etc.) - opcional

---

### 6. Actualizar Actividad
```http
PUT /activities/1
Content-Type: application/json

{
  "description": "Updated description",
  "name": "Morning Run - Updated"
}
```

---

### 7. Eliminar Actividad
```http
DELETE /activities/1
```

---

### 8. Obtener Estadísticas de Usuario
```http
GET /activities/user/1/stats
```

**Respuesta:**
```json
{
  "total_distance": 125.5,
  "total_duration": 15.5,
  "activity_count": 12,
  "average_speed": 4.2,
  "max_speed": 5.8
}
```

---

## 👟 EQUIPO (Gear)

### 1. Crear Equipo
```http
POST /gear
Content-Type: application/json

{
  "user_id": 1,
  "strava_id": "b987654321",
  "name": "Nike Vaporfly 3",
  "gear_type": "shoes",
  "brand": "Nike",
  "model": "Vaporfly 3",
  "description": "Racing shoes for marathons",
  "primary": true,
  "retired": false,
  "distance": 0,
  "initial_purchase_date": "2025-06-01T00:00:00"
}
```

---

### 2. Obtener Todo el Equipo
```http
GET /gear?skip=0&limit=100
```

---

### 3. Obtener Equipo por ID
```http
GET /gear/1
```

---

### 4. Obtener Equipo de un Usuario
```http
GET /gear/user/1?skip=0&limit=100
```

---

### 5. Obtener Equipo Primario de Usuario
```http
GET /gear/user/1/primary
```

---

### 6. Actualizar Equipo
```http
PUT /gear/1
Content-Type: application/json

{
  "primary": false,
  "distance": 500000
}
```

⚠️ Si estableces `primary: true`, todos los demás equipos del usuario se marcarán como no primarios.

---

### 7. Eliminar Equipo
```http
DELETE /gear/1
```

---

### 8. Marcar Equipo como Retirado
```http
POST /gear/1/retire
```

Esto mantiene los datos históricos pero marca el equipo como ya no en uso.

---

### 9. Obtener Uso de Equipo
```http
GET /gear/1/usage
```

**Respuesta:**
```json
{
  "gear_id": 1,
  "gear_name": "Nike Vaporfly 3",
  "total_distance": 245.5,
  "activity_count": 18,
  "synced_distance": 245.5
}
```

---

## 🧪 Ejemplos Prácticos con cURL

### Crear Usuario
```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "strava_id": 12345678,
    "username": "john_runner",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "access_token": "abc123token"
  }'
```

### Obtener Usuario
```bash
curl http://localhost:8000/api/v1/users/1
```

### Crear Actividad
```bash
curl -X POST http://localhost:8000/api/v1/activities \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "strava_id": 9876543210,
    "name": "Morning Run",
    "activity_type": "run",
    "distance": 10000,
    "duration": 2400,
    "start_date": "2025-12-30T06:00:00",
    "start_date_local": "2025-12-30T01:00:00"
  }'
```

### Obtener Actividades de Usuario
```bash
curl http://localhost:8000/api/v1/activities/user/1
```

### Crear Equipo
```bash
curl -X POST http://localhost:8000/api/v1/gear \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "name": "Nike Vaporfly 3",
    "gear_type": "shoes",
    "brand": "Nike",
    "primary": true
  }'
```

---

## 🔍 Códigos de Estado HTTP

| Código | Significado |
|--------|-------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado exitosamente |
| 204 | No Content - Operación exitosa, sin contenido |
| 400 | Bad Request - Datos inválidos |
| 404 | Not Found - Recurso no encontrado |
| 500 | Internal Server Error - Error del servidor |

---

## 📊 Formato de Datos

### DateTime
Todos los timestamps están en formato ISO 8601 UTC:
```
2025-12-30T10:00:00
```

### Distancia
Se almacena en **metros** en la BD, pero se retorna en **km** en las estadísticas.

### Duración
Se almacena en **segundos** en la BD, pero se retorna en **horas** en las estadísticas.

### Velocidad
Se almacena en **m/s** (metros por segundo).

---

## ⚙️ Próximas Adiciones

Los siguientes endpoints están plaqueados para los próximos sprints:

- `POST /sync/strava` - Sincronizar datos desde Strava
- `GET /analytics/` - Análisis avanzados
- `POST /auth/strava` - Autenticación OAuth
- `GET /reports/` - Generación de reportes

---

**Versión**: 0.1.0
**Última actualización**: 30/12/2025
**Estado**: ✅ Endpoints CRUD completados
