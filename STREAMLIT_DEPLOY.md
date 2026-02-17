# Guía de Deployment en Streamlit Cloud

## Pasos para subir tu app a Streamlit Cloud

### 1. Conecta tu repositorio
1. Ve a [streamlit.io](https://streamlit.io/)
2. Haz clic en "Deploy" → "New app"
3. Selecciona tu repositorio de GitHub
4. Selecciona la rama `main` (o la que uses)
5. Establece la ruta: `frontend/app.py`

### 2. Configura los Secrets (IMPORTANTE ⚠️)
En tu dashboard de Streamlit Cloud, ve a:
- `App settings` (arriba a la derecha)
- `Secrets` 
- Agrega la siguiente configuración:

```toml
# .streamlit/secrets.toml
API_BASE_URL = "https://tu-backend-url.com/api/v1"
```

**Ejemplo para diferentes entornos:**
- **Local (Docker):** `http://running_analytics_backend:8000/api/v1`
- **Producción:** `https://tu-dominio.com/api/v1`

### 3. Problemas comunes

#### ❌ Página en blanco
- Verifica que `API_BASE_URL` esté configurado en Secrets
- Comprueba que tu backend sea accesible desde Internet
- Usa `st.write()` para debuguear

#### ❌ "No se pudo conectar al servidor"
- Confirma que la URL del backend sea correcta
- Verifica que CORS esté habilitado en tu backend
- Revisa los logs de tu backend

#### ❌ "No hay usuarios registrados"
- Primero debes iniciar sesión con Strava en tu backend
- El usuario se crea automáticamente al autenticar con Strava

### 4. Variables de entorno en Streamlit Cloud
Las variables se configuran en el archivo `.streamlit/secrets.toml` que se sincroniza automáticamente.
```
