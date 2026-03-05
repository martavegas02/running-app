# 🔐 Configuración de Auto-Login en Streamlit Cloud

## ¿Qué es esto?

Has modificado tu app para que en **Streamlit Cloud** haga **login automático** sin mostrar pantalla de login. Así accederás directamente a tus datos.

---

## 📋 Pasos a seguir en Streamlit Cloud

### 1️⃣ Ve a tu aplicación en Streamlit Cloud
- Entra a https://share.streamlit.io/
- Busca tu aplicación `running-app-...`
- Haz clic en los **tres puntos** (⋮) en la esquina superior derecha

### 2️⃣ Accede a los Secrets
- Selecciona **⚙️ App settings** o **🔑 Secrets**
- Se abrirá un editor

### 3️⃣ Añade tu variable de auto-login

En la sección de **Secrets**, añade esta línea:

```
AUTO_LOGIN_USERNAME=tu_usuario
```

**Reemplaza `tu_usuario`** con el nombre de usuario con el que te registraste en tu aplicación.

**Ejemplo:**
```
AUTO_LOGIN_USERNAME=martavegas
```

### 4️⃣ Guarda y redeploy
- Haz clic en **Save** y **Rerun** 
- La app se reiniciará automáticamente
- ¡Ya debería mostrarte tus datos sin login! 🎉

---

## 🔒 Consideraciones de Seguridad

1. **Los Secrets son privados**: Solo tú puedes verlos, Streamlit no los expone
2. **No se guardan en código**: El `.env` local es solo para desarrollo
3. **Protegido por el usuario/contraseña del backend**: Aunque no veas login, el backend sigue valido el token

---

## ❓ ¿Qué pasa si sale error?

Si ves un error de "No se pudo iniciar sesión automática":

1. ✅ Verifica que el `AUTO_LOGIN_USERNAME` esté **exactamente igual** a tu usuario
2. ✅ Verifica que el backend API esté disponible
3. ✅ Intenta **desactivar el Secret** (comenta la línea) para volver al login normal

---

## 🚀 Para desarrollo local (opcional)

Si quieres probar auto-login en tu PC también:

1. Abre `.env`
2. Descomenta y rellena:
   ```
   AUTO_LOGIN_USERNAME=tu_usuario
   ```
3. Reinicia Streamlit:
   ```
   streamlit run frontend/app.py
   ```

---

## 📝 Variables disponibles

- `AUTO_LOGIN_USERNAME` → Username del usuario que loguearse automáticamente
- `API_BASE_URL` → URL del backend (por defecto: http://running_analytics_backend:8000/api/v1)

---

**¡Listo! 🎉** Tu app en la nube ahora mostrará directamente tus datos sin necesidad de login.
