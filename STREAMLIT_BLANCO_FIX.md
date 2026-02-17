# ⚠️ SOLUCIÓN: App en Blanco en Streamlit Cloud

## El Problema
Cuando subes a Streamlit Cloud, la app sale en blanco porque:
1. No puede conectar al backend (`API_BASE_URL`)
2. El backend está alojado en local o en Docker interno
3. Falta configurar la URL en Streamlit Cloud Secrets

## La Solución

### ✅ Opción 1: Backend alojado en la nube (RECOMENDADO)
Si tu backend ya está en producción (ej. en Heroku, Railway, etc):

1. **Busca la URL de tu backend:**
   - Debe ser algo como: `https://tu-app-backend.herokuapp.com`
   - NO debe ser: `http://localhost:8000` 
   - NO debe ser: `http://running_analytics_backend:8000`

2. **Configura en Streamlit Cloud:**
   - Ve a tu app en [share.streamlit.io](https://share.streamlit.io)
   - Click derecha → "App settings" 
   - Abre la pestaña "Secrets" 
   - Pega esto (reemplaza la URL):
   ```toml
   API_BASE_URL = "https://tu-backend-url.com/api/v1"
   ```

3. **Sube los cambios a GitHub:**
   ```bash
   git add .
   git commit -m "Fix: Configurar API_BASE_URL para producción"
   git push
   ```

4. **Redeploy en Streamlit Cloud:**
   - Ve a tu app
   - Click en el menú (⋯ arriba a la derecha)
   - "Rerun" o "Manage app" → "Reboot"

### ✅ Opción 2: Usa un servicio externo para el backend
Si tu backend sigue en local, puedes:
- Usar **ngrok** para exponer tu servidor local:
  ```bash
  ngrok http 8000
  ```
  Te dará una URL como `https://xxxxx.ngrok.io`

- Luego configura esa URL en Streamlit Cloud Secrets

## Verificación Rápida

Cuando esté configurado correctamente, la app debería:
1. ✅ Ver la pantalla de login (no en blanco)
2. ✅ Ver mensaje "Conectar con Strava" si no hay usuarios
3. ✅ Ver lista de usuarios si existen

## Debug
Si aún sale en blanco:
1. Abre la consola del navegador (F12)
2. Ve a "Console" 
3. Copia cualquier error que veas
4. Esto te ayudará a identificar el problema
