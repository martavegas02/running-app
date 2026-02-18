import streamlit as st
import requests
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, timedelta
import os
import base64
import sqlite3
import json

# Configuración de la página
st.set_page_config(
    page_title="Running Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar sesión de autenticación
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.token = None

# CSS Profesional - Tema Oscuro
st.markdown("""
    <style>
        header[data-testid="stHeader"] { display: none !important; }
        .block-container { padding-top: 2rem !important; }
        [data-testid="stSidebarUserContent"] { padding-top: 2rem !important; color: #e0e0e8 !important; }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%); border-right: 2px solid #FF6B35; }
        .stButton > button { border-radius: 8px !important; font-weight: 600 !important; width: 100%; color: #ffffff !important; }
        button[kind="primary"] { background: linear-gradient(135deg, #FF6B35 0%, #FF8F5E 100%) !important; color: white !important; border: none !important; box-shadow: 0 4px 12px rgba(255, 107, 53, 0.2) !important; }
        button[kind="primary"]:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 20px rgba(255, 107, 53, 0.3) !important; }
        button[kind="secondary"] { background: transparent !important; color: #e0e0e8 !important; border: 1px solid #3d3d5c !important; box-shadow: none !important; }
        button[kind="secondary"]:hover { background: #2d2d4a !important; color: #FF6B35 !important; border-color: #FF6B35 !important; }
        ::-webkit-scrollbar { display: none !important; width: 0px !important; height: 0px !important; }
        * { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif; color: #e0e0e8 !important; }
        .main { background: #0f0f1e; color: #e0e0e8 !important; }
        body { color: #e0e0e8 !important; }
        h1 { color: #f5f5ff !important; font-size: 2.2rem !important; font-weight: 700 !important; letter-spacing: -0.5px; }
        h2 { color: #4db8a8 !important; font-size: 1.5rem !important; font-weight: 700 !important; margin-top: 1rem !important; text-transform: uppercase; }
        h3 { color: #e0e0e8 !important; font-weight: 600 !important; font-size: 1rem !important; }
        p { color: #d0d0d8 !important; }
        label { color: #e0e0e8 !important; }
        .stMarkdown { color: #e0e0e8 !important; }
        .metric-card { background: linear-gradient(135deg, #1a1a2e 0%, #0f1419 100%); border-radius: 14px; padding: 28px; box-shadow: 0 4px 16px rgba(255, 107, 53, 0.12); border-top: 4px solid #FF6B35; text-align: center; color: #e0e0e8 !important; }
        .metric-card .value { font-size: 2.5rem; font-weight: 800; color: #FF6B35 !important; margin: 16px 0 0 0; }
        .prediction-card { background: #1a1a2e; border-radius: 16px; padding: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.3); border: 1px solid #3d3d5c; text-align: center; transition: transform 0.2s; color: #e0e0e8 !important; }
        .prediction-card:hover { transform: scale(1.02); border-color: #FF6B35; box-shadow: 0 8px 24px rgba(255, 107, 53, 0.15); }
        .pred-distance { color: #4db8a8 !important; font-weight: 800; font-size: 1.2rem; margin-bottom: 10px; }
        .pred-time { color: #f5f5ff !important; font-size: 2rem; font-weight: 700; margin-bottom: 5px; }
        .pred-pace { color: #d0d0d8 !important; font-size: 0.9rem; font-weight: 500; background: #2d2d4a; padding: 4px 12px; border-radius: 20px; display: inline-block; }
        hr { border: none !important; height: 2px !important; background: #FF6B35 !important; margin: 2rem 0 !important; }
        .stSuccess { border-left: 4px solid #4db8a8 !important; color: #e0e0e8 !important; background-color: rgba(77, 184, 168, 0.1) !important; }
        .styled-table { width: 100%; border-collapse: separate; border-spacing: 0; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.3); border: 1px solid #3d3d5c; margin-bottom: 20px; font-size: 0.9rem; }
        .styled-table thead tr { background: linear-gradient(135deg, #FF6B35 0%, #FF8F5E 100%); color: #ffffff; text-align: left; }
        .styled-table th, .styled-table td { padding: 16px 24px; color: #e0e0e8 !important; }
        .styled-table tbody tr { border-bottom: 1px solid #2d2d4a; background-color: #1a1a2e; transition: all 0.2s; color: #e0e0e8 !important; }
        .styled-table tbody tr:nth-of-type(even) { background-color: #0f1419; }
        .styled-table tbody tr:last-of-type { border-bottom: 3px solid #FF6B35; }
        .styled-table tbody tr:hover { background-color: #2d3d4a; transform: scale(1.002); font-weight: 500; color: #FF6B35 !important; }
        .styled-table th { font-weight: 700; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 1px; color: #ffffff !important; }
        .stTextInput > div > div > input { background-color: #1a1a2e !important; color: #e0e0e8 !important; border: 1px solid #3d3d5c !important; }
        .stSelectbox > div > div > div > input { background-color: #1a1a2e !important; color: #e0e0e8 !important; border: 1px solid #3d3d5c !important; }
        .stSelectbox > div > div { background-color: #1a1a2e !important; color: #e0e0e8 !important; border: 1px solid #3d3d5c !important; }
        [data-baseweb="select"] input { background-color: #1a1a2e !important; color: #e0e0e8 !important; }
        [data-baseweb="select"] { color: #e0e0e8 !important; }
        [data-baseweb="select"] div { background-color: #1a1a2e !important; color: #e0e0e8 !important; }
        [data-baseweb="select"] [role="button"] { background-color: #1a1a2e !important; color: #e0e0e8 !important; border: 1px solid #3d3d5c !important; }
        [data-baseweb="popover"] { background-color: #1a1a2e !important; color: #e0e0e8 !important; }
        [data-baseweb="option"] { background-color: #1a1a2e !important; color: #e0e0e8 !important; }
        [data-baseweb="menu"] { background-color: #1a1a2e !important; }
        [data-baseweb="menu"] li { color: #e0e0e8 !important; background-color: #1a1a2e !important; }
        [data-baseweb="menu"] li:hover { background-color: #2d2d4a !important; color: #FF6B35 !important; }
        .stSelectbox { color: #e0e0e8 !important; }
        .stSelectbox div { background-color: #1a1a2e !important; }
        .stSelectbox input { color: #e0e0e8 !important; }
        .stRadio > div { color: #e0e0e8 !important; }
        .stMetric { color: #e0e0e8 !important; }
        /* Dropdown options styling */
        [data-testid="stSelectboxPopover"] { background-color: #1a1a2e !important; }
        [role="listbox"], [role="option"] { background-color: #1a1a2e !important; color: #e0e0e8 !important; }
    </style>
""", unsafe_allow_html=True)

# API URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://running_analytics_backend:8000/api/v1")

# Mostrar URL del API para debugging
if "localhost" not in API_BASE_URL and "running_analytics" not in API_BASE_URL:
    # En Streamlit Cloud - mostrar configuración
    st.sidebar.info(f"📡 API: {API_BASE_URL}")

# Función para verificar conexión
@st.cache_resource
def check_api_connection():
    """Verifica si el API está disponible"""
    try:
        response = requests.get(f"{API_BASE_URL}/users/", timeout=3)
        return response.status_code == 200
    except:
        return False

# --- FUNCIONES DE AUTENTICACIÓN ---
def login_user(username: str) -> bool:
    """
    Intenta autenticar al usuario con el backend
    """
    try:
        response = requests.post(
            f"{API_BASE_URL.replace('/api/v1', '')}/auth/simple-login",
            params={"username": username},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.authenticated = True
            st.session_state.user_id = data['user']['id']
            st.session_state.username = data['user']['username']
            st.session_state.token = data['access_token']
            return True
        else:
            return False
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return False

def get_strava_login_url() -> str:
    """
    Obtiene la URL de login de Strava
    """
    try:
        response = requests.get(
            f"{API_BASE_URL.replace('/api/v1', '')}/auth/strava/login",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('oauth_url', '')
    except:
        pass
    return ""

def logout_user():
    """
    Cierra la sesión del usuario
    """
    st.session_state.authenticated = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.token = None
    st.session_state.data_synced = False
    st.session_state.last_synced_user = None

def show_login_page():
    """
    Muestra la pantalla de login
    """
    st.markdown('<div class="title-section"><h1>🏃 Running Analytics</h1></div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div style="text-align: center; padding: 40px 20px;">
            <h2 style="color: #4db8a8; margin-bottom: 30px;">Bienvenido a tu plataforma de Running</h2>
            <p style="color: #d0d0d8; font-size: 1.1rem;">Inicia sesión para acceder a tu dashboard de análisis</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Obtener usuarios disponibles
    available_users = []
    connection_error = False
    try:
        response = requests.get(f"{API_BASE_URL}/users/", timeout=5)
        if response.status_code == 200:
            available_users = response.json()
    except Exception as e:
        connection_error = True
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Opción 1: Seleccionar usuario existente
        if available_users and not connection_error:
            st.markdown("### 👥 Usuarios Disponibles")
            user_options = {u['username']: u['id'] for u in available_users}
            
            selected_user = st.selectbox(
                "Selecciona un usuario",
                options=list(user_options.keys()),
                label_visibility="collapsed"
            )
            
            if st.button("📊 Acceder", use_container_width=True, type="primary"):
                with st.spinner("Verificando credenciales..."):
                    if login_user(selected_user):
                        st.success("✅ ¡Sesión iniciada correctamente!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ Error al iniciar sesión")
            
            st.divider()
        
        # Opción 2: Conectar con Strava
        st.markdown("### 🔗 Conectar con Strava")
        
        strava_url = get_strava_login_url()
        if strava_url:
            st.markdown(f"""
                <div style="text-align: center; padding: 10px;">
                    <a href="{strava_url}" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #FF6B35 0%, #FF8F5E 100%); color: white; padding: 12px 30px; border-radius: 8px; text-decoration: none; font-weight: 600; box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);">
                        🔐 Iniciar Sesión con Strava
                    </a>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ No se pudo conectar al servidor. Verifica la configuración del API.")
            
            # Mostrar configuración actual para debugging
            with st.expander("🔧 Información técnica"):
                st.code(f"API_BASE_URL = {API_BASE_URL}", language="python")
                st.info("En Streamlit Cloud, configura la variable API_BASE_URL en Secrets/Environment")
        
        # Si no hay usuarios disponibles
        if not available_users and not connection_error:
            st.info("📭 No hay usuarios registrados. Inicia sesión con Strava para crear tu perfil.")
    
    st.divider()
    st.markdown("""
        <div style="text-align: center; color: #999; padding: 40px 20px;">
            <p>📌 Usa Strava para crear tu cuenta y acceder a Running Analytics</p>
        </div>
    """, unsafe_allow_html=True)

# --- FUNCIONES API ---
@st.cache_data(ttl=300)
def get_users():
    try:
        response = requests.get(f"{API_BASE_URL}/users/", timeout=5)
        if response.status_code == 200: return response.json()
    except Exception as e: st.error(f"Error: {e}")
    return []

@st.cache_data(ttl=300)
def get_activities(user_id):
    try:
        response = requests.get(f"{API_BASE_URL}/activities/user/{user_id}", timeout=5)
        if response.status_code == 200: return response.json()
    except Exception as e: st.error(f"Error: {e}")
    return []

@st.cache_data(ttl=300)
def get_user_stats(user_id):
    try:
        response = requests.get(f"{API_BASE_URL}/activities/user/{user_id}/stats", timeout=5)
        if response.status_code == 200: return response.json()
    except Exception as e: st.error(f"Error: {e}")
    return {}

def get_training_plan(user_id):
    try:
        response = requests.get(f"{API_BASE_URL}/planning/current-plan/{user_id}", timeout=5)
        if response.status_code == 200: return response.json()
    except: pass
    return None

def generate_training_plan(user_id):
    """Generar plan forzando que sea para ESTA semana (Lunes actual)"""
    try:
        # 1. Calcular Lunes de ESTA semana (aunque sea Jueves)
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday()) # Lunes de esta semana
        start_date_str = start_of_week.strftime("%Y-%m-%d")
        
        # 2. Enviar parámetro explícito al backend
        url = f"{API_BASE_URL}/planning/generate-plan/{user_id}"
        params = {
            "intensity_level": "beginner",
            "start_date": start_date_str # <--- CLAVE PARA QUE NO SEA LA SIGUIENTE
        }
        
        response = requests.post(url, params=params, timeout=15)
        if response.status_code == 200: return response.json()
    except Exception as e: return {"status": "error", "message": str(e)}
    return {"status": "error", "message": "Error desconocido"}

def get_race_predictions(user_id):
    try:
        response = requests.get(f"{API_BASE_URL}/planning/predictions/{user_id}", timeout=10)
        if response.status_code == 200: return response.json()
    except: return None
    return None

def calculate_predictions(user_id):
    try:
        response = requests.post(f"{API_BASE_URL}/planning/predictions/calculate/{user_id}", timeout=20)
        if response.status_code == 200: return response.json()
    except Exception as e: return {"status": "error", "message": str(e)}
    return None

def sync_user_data_automatically(user_id):
    backend_host = "http://running_analytics_backend:8000"
    url = f"{backend_host}/sync/activities"
    try:
        payload = {"user_id": user_id}
        response = requests.post(url, json=payload, timeout=120)
        if response.status_code == 422:
            st.warning("⚠️ Probando método alternativo...")
            response = requests.post(f"{url}?user_id={user_id}", timeout=120)
        if response.status_code == 200: return True, "Sincronización exitosa"
        else: return False, f"Error {response.status_code}: {response.text}"
    except Exception as e: return False, f"Error de conexión: {str(e)}"

# ===== FUNCIÓN PARA IMAGEN LOCAL =====
@st.cache_data
def get_shoes_image_base64():
    """Obtiene imagen de zapatillas desde archivo o URL"""
    try:
        # Intenta cargar desde archivo local
        posibles_rutas = [
            os.path.join(os.path.dirname(__file__), "..", "imagen zapatos.webp"),
            "/app/imagen zapatos.webp",
            "imagen zapatos.webp",
        ]
        
        for img_path in posibles_rutas:
            if os.path.exists(img_path):
                try:
                    with open(img_path, "rb") as img_file:
                        data = base64.b64encode(img_file.read()).decode()
                        return f"data:image/webp;base64,{data}"
                except Exception as e:
                    continue
    except: pass
    
    # Si no encuentra archivo local, usa foto de Asics Cumulus 26
    return "https://images.runningwarehouse.com/products/800x600/ASICS-Cumulus-26.jpg"

shoes_img_base64 = get_shoes_image_base64()

# ===== BASE DE DATOS PARA ZAPATILLAS =====
DB_PATH = "/app/shoes.db" if os.path.exists("/app") else "shoes.db"

def init_shoes_db():
    """Inicializa la base de datos de zapatillas"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS shoes
                (id TEXT PRIMARY KEY, brand TEXT, model TEXT, color TEXT, 
                 km REAL, limit_km REAL, status TEXT, img TEXT)''')
    conn.commit()
    conn.close()

def save_shoe(shoe_id, brand, model, color, km, limit_km, status, img):
    """Guarda una zapatilla en la BD"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO shoes 
                (id, brand, model, color, km, limit_km, status, img)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (shoe_id, brand, model, color, km, limit_km, status, img))
    conn.commit()
    conn.close()

def load_shoes():
    """Carga todas las zapatillas desde la BD"""
    init_shoes_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM shoes')
    rows = c.fetchall()
    conn.close()
    
    shoes_dict = {}
    for row in rows:
        shoe_id, brand, model, color, km, limit_km, status, img = row
        shoes_dict[shoe_id] = {
            "id": shoe_id,
            "brand": brand,
            "model": model,
            "color": color,
            "km": km,
            "limit": limit_km,
            "status": status,
            "img": img
        }
    return shoes_dict

def update_shoe_km(shoe_id, km):
    """Actualiza los km de una zapatilla"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE shoes SET km = ? WHERE id = ?', (km, shoe_id))
    conn.commit()
    conn.close()

def update_shoe_status(shoe_id, status):
    """Actualiza el estado de una zapatilla"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE shoes SET status = ? WHERE id = ?', (status, shoe_id))
    conn.commit()
    conn.close()

# ===== HEADER =====
st.markdown('<div class="title-section"><h1>🏃 Running Analytics</h1></div>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Tu plataforma inteligente para analizar y mejorar tu rendimiento en running</p>', unsafe_allow_html=True)
st.divider()

# ===== SIDEBAR =====
with st.sidebar:
    # Botón de logout en la parte superior
    if st.session_state.authenticated:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"👤 **{st.session_state.username}**")
        with col2:
            if st.button("🚪", help="Cerrar sesión", use_container_width=False):
                logout_user()
                st.rerun()
        st.divider()
    
    st.markdown("### 🏠 HOME")
    #st.divider()
    
    # Usar el usuario autenticado en st.session_state
    user_id = st.session_state.user_id
    
    if user_id:
        st.markdown(f"<div style='padding: 12px 16px; background: #1a1a2e; border-radius: 8px; border: 1px solid #3d3d5c; color: #e0e0e8;'><span style='font-size: 0.85rem; color: #4db8a8;'>📍 Usuario Autenticado:</span><br><span style='font-size: 1.1rem; font-weight: 600;'>{st.session_state.username}</span></div>", unsafe_allow_html=True)
        
        if 'last_synced_user' not in st.session_state or st.session_state['last_synced_user'] != user_id:
            st.session_state['data_synced'] = False; st.session_state['last_synced_user'] = user_id; st.session_state['selected_user_id'] = user_id

        if not st.session_state.get('data_synced', False):
            with st.spinner(f"🔄 Buscando nuevas carreras..."):
                success, msg = sync_user_data_automatically(user_id)
                st.session_state['data_synced'] = True
                if success: st.toast("✅ Datos actualizados", icon="🏃"); st.cache_data.clear(); st.rerun()
                else: st.toast("❌ Error sincronizando", icon="⚠️")
    
    st.divider()
    st.markdown("### 📊 NAVEGACIÓN")
    
    # Inicializar sesión para la sección actual
    if 'current_section' not in st.session_state:
        st.session_state['current_section'] = "🏠 Dashboard"
    
    # CSS para los botones de navegación
    st.markdown("""
        <style>
            .nav-button { 
                display: block; 
                width: 100%; 
                padding: 14px 16px; 
                margin-bottom: 8px; 
                background: #1a1a2e; 
                border: 2px solid #3d3d5c; 
                border-radius: 10px; 
                color: #e0e0e8; 
                font-size: 0.95rem; 
                font-weight: 500; 
                cursor: pointer; 
                transition: all 0.3s ease; 
                text-align: left;
            }
            .nav-button:hover { 
                background: #2d2d4a; 
                border-color: #FF6B35; 
                color: #FF6B35; 
                transform: translateX(4px);
                box-shadow: 0 4px 12px rgba(255, 107, 53, 0.2);
            }
            .nav-button.active { 
                background: linear-gradient(135deg, #FF6B35 0%, #FF8F5E 100%); 
                border-color: #FF6B35; 
                color: #ffffff; 
                box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Botones de navegación
    nav_sections = ["🏠 Dashboard", "🔮 Predicciones", "📅 Plan de Entrenamiento", "📋 Actividades", "💪 Equipo"]
    
    col = st.columns(1)[0]
    for nav_section in nav_sections:
        is_active = nav_section == st.session_state['current_section']
        active_class = "nav-button active" if is_active else "nav-button"
        
        if st.button(nav_section, key=f"nav_{nav_section}", use_container_width=True):
            st.session_state['current_section'] = nav_section
            st.rerun()

# ===== CONTENIDO =====
# Verificar si el usuario está autenticado
if not st.session_state.authenticated:
    show_login_page()
else:
    user_id = st.session_state.user_id
    section = st.session_state['current_section']
    
    stats = get_user_stats(user_id)
    activities = get_activities(user_id)
    
    # --- DASHBOARD ---
    if "Dashboard" in section:
        st.markdown("## 📈 ESTADÍSTICAS DE RUNNING")
        runs = [a for a in activities if a.get('activity_type', '').lower() == 'run']
        total_dist = sum(a.get('distance', 0) for a in runs)
        total_time = sum(a.get('duration', 0) for a in runs)
        
        pace_fmt = f"{int((1000/(total_dist/total_time))//60)}:{int((1000/(total_dist/total_time))%60):02d} /km" if total_dist > 0 else "0:00 /km"
        
        c1, c2, c3, c4 = st.columns(4)
        for l, v, c in [("Total Carreras", len(runs), c1), ("Distancia", f"{total_dist/1000:.1f} km", c2), ("Tiempo", f"{total_time/3600:.1f} h", c3), ("Ritmo Medio", pace_fmt, c4)]:
            c.markdown(f"""<div class="metric-card"><h3>{l}</h3><div class="value">{v}</div></div>""", unsafe_allow_html=True)
        
        st.divider()
        if runs:
            st.markdown("## 📊 ANÁLISIS POR SEMANA")
            df = pd.DataFrame(runs); df['start_date'] = pd.to_datetime(df['start_date'])
            df['week'] = df['start_date'].dt.isocalendar().year.astype(str) + ' - Semana ' + df['start_date'].dt.strftime('%W')
            wd = df.groupby('week')['distance'].sum().reset_index().sort_values('week')
            wd['distance'] /= 1000
            st.bar_chart(wd.set_index('week')['distance'], color="#FF6B35")
            
            st.divider()
            st.markdown("## 🏁 ÚLTIMAS CARRERAS")
            df_disp = df[['name', 'distance', 'duration', 'average_speed', 'start_date']].head(10).copy()
            rows = ""
            for _, r in df_disp.iterrows():
                pace = f"{int((1000/r['average_speed'])//60)}:{int((1000/r['average_speed'])%60):02d} /km" if r['average_speed']>0 else "-"
                rows += f"<tr><td>{r['start_date'].strftime('%d %b %Y')}</td><td style='font-weight:600'>{r['name']}</td><td>{r['distance']/1000:.2f} km</td><td>{int(r['duration']//3600):02d}:{int((r['duration']%3600)//60):02d}:{int(r['duration']%60):02d}</td><td>{pace}</td></tr>"
            st.markdown(f"""<table class="styled-table"><thead><tr><th>📅 Fecha</th><th>🏃 Nombre</th><th>📏 Distancia</th><th>⏱️ Tiempo</th><th>⚡ Ritmo</th></tr></thead><tbody>{rows}</tbody></table>""", unsafe_allow_html=True)
        else: st.info("📭 Sin carreras.")

    # --- PREDICCIONES ---
    elif "Predicciones" in section:
        st.markdown("## 🔮 PREDICCIÓN DE CARRERAS")
        c1, c2 = st.columns([1, 3])
        if c1.button("⚡ Recalcular", use_container_width=True):
            calculate_predictions(user_id); st.rerun()
        
        preds = get_race_predictions(user_id)
        if preds:
            st.divider(); cols = st.columns(4)
            for i, r in enumerate([("5K", "5k"), ("10K", "10k"), ("Media", "half_marathon"), ("Maratón", "marathon")]):
                d = preds.get(r[1], {})
                cols[i].markdown(f"""<div class="prediction-card"><div class="pred-distance">{r[0]}</div><div class="pred-time">{d.get('time','--')}</div><div class="pred-pace">Ritmo: {d.get('pace','--')} /km</div></div>""", unsafe_allow_html=True)
        else: st.info("Pulsa recalcular.")

    # --- PLAN ENTRENAMIENTO ---
    elif "Plan de Entrenamiento" in section:
        st.markdown("## 📅 TU PLAN SEMANAL")
        c_main, c_side = st.columns([3, 1])
        with c_main:
            plan = get_training_plan(user_id)
            if plan:
                s_date = plan['week_start'].split('T')[0]
                e_date = (datetime.strptime(s_date, "%Y-%m-%d") + timedelta(days=6)).strftime("%Y-%m-%d")
                
                # HEADER SEMANA (HTML COMPACTADO)
                st.markdown(f"""<div style="background: linear-gradient(120deg, #1a1a2e 0%, #16213e 100%); border-radius: 16px; padding: 25px; border-left: 6px solid #FF6B35; box-shadow: 0 4px 15px rgba(255, 107, 53, 0.15); margin-bottom: 25px;"><div style="display: flex; justify-content: space-between;"><div><div style="font-size: 1.2rem; font-weight: 700; color: #f5f5ff;">🚀 Semana de {plan['intensity_level'].capitalize()}</div><div style="font-size: 0.9rem; color: #4db8a8;">📅 Del {s_date} al {e_date}</div></div><div style="text-align: right;"><div style="font-size: 1.5rem; font-weight: 800; color: #FF6B35;">{plan.get('total_planned_km', 0):.1f} km</div></div></div><div style="margin-top: 15px; background: rgba(255, 107, 53, 0.15); padding: 10px; border-radius: 8px; color: #FF8F5E; font-weight: 600;">🎯 Objetivo: {plan.get('goals', 'Constancia')}</div></div>""", unsafe_allow_html=True)

                for i, s in enumerate(plan.get('sessions', []), 1):
                    icon = "🟢" if s.get('intensity')=='easy' else "🔵" if s.get('intensity')=='long_easy' else "🔴"
                    with st.expander(f"{icon} {s['day']} | {s['activity_type'].upper()} - {s.get('planned_distance', 0)} km", expanded=(i==1)):
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Distancia", f"{s.get('planned_distance')} km")
                        c2.metric("Tiempo", f"{s.get('planned_duration')} min")
                        c3.metric("Ritmo", s.get('planned_pace', 'N/A'))
                        st.markdown(f"**Estructura:** Calentamiento: {s.get('warm_up','-')} -> Principal: {s.get('main_workout','-')} -> Enfriamiento: {s.get('cool_down','-')}")
            else:
                st.info("Sin plan activo.")

        with c_side:
            st.markdown("### ⚙️ Acciones")
            if st.button("✨ Generar Nuevo Plan (Esta Semana)", use_container_width=True, type="primary"):
                with st.spinner("Creando plan..."):
                    if generate_training_plan(user_id).get("status") == "success": st.success("¡Hecho!"); st.rerun()
                    else: st.error("Error")

    # --- ACTIVIDADES ---
    elif "Actividades" in section:
        st.markdown("## 📋 ANÁLISIS DE ACTIVIDADES")
        if activities:
            df = pd.DataFrame(activities)
            df['start_date'] = pd.to_datetime(df['start_date'])
            df = df.sort_values(by='start_date', ascending=False)
            all_runs = df[df['activity_type'].str.lower() == 'run'].copy()
            
            opts = {f"{r['start_date'].strftime('%d/%m')} | {r['name']}": i for i, r in df.iterrows()}
            sel_opt = st.selectbox("🔎 Selecciona actividad:", list(opts.keys()))
            act = df.loc[opts[sel_opt]]
            
            if act['activity_type'].lower() == 'run' and act['average_speed'] > 0:
                pace = f"{int((1000/act['average_speed'])//60)}:{int((1000/act['average_speed'])%60):02d} /km"
            else: pace = f"{act['average_speed']*3.6:.1f} km/h"
            
            # HTML COMPACTADO PARA EVITAR ERROR
            st.markdown(f"""<div style="background: linear-gradient(135deg, #1a1a2e 0%, #0f1419 100%); padding: 25px; border-radius: 16px; box-shadow: 0 4px 20px rgba(255, 107, 53, 0.15); border-left: 6px solid #FF6B35; margin-bottom: 20px;"><div style="font-size: 1.5rem; font-weight: 800; color: #f5f5ff;">{act['name']}</div><div style="color: #4db8a8; margin-bottom: 15px;">📅 {act['start_date'].strftime('%d %B %Y')}</div><div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px;"><div style="text-align: center; background: rgba(77, 184, 168, 0.1); padding: 10px; border-radius: 8px;"><div style="font-weight: 700; color: #FF6B35; font-size: 1.2rem;">{act['distance']/1000:.2f} km</div><div style="font-size: 0.8rem; color: #d0d0d8;">Distancia</div></div><div style="text-align: center; background: rgba(77, 184, 168, 0.1); padding: 10px; border-radius: 8px;"><div style="font-weight: 700; color: #FF6B35; font-size: 1.2rem;">{int(act['duration']//60)} min</div><div style="font-size: 0.8rem; color: #d0d0d8;">Tiempo</div></div><div style="text-align: center; background: rgba(77, 184, 168, 0.1); padding: 10px; border-radius: 8px;"><div style="font-weight: 700; color: #FF6B35; font-size: 1.2rem;">{pace}</div><div style="font-size: 0.8rem; color: #d0d0d8;">Ritmo</div></div><div style="text-align: center; background: rgba(77, 184, 168, 0.1); padding: 10px; border-radius: 8px;"><div style="font-weight: 700; color: #FF6B35; font-size: 1.2rem;">{int(act['distance']/1000*70)}</div><div style="font-size: 0.8rem; color: #d0d0d8;">Kcal</div></div></div></div>""", unsafe_allow_html=True)

            
            
            st.divider()
            st.markdown("### 📚 Historial")
            rows = ""
            for _, r in df.iterrows():
                rows += f"<tr><td>{r['start_date'].strftime('%d/%m')}</td><td>{r['name']}</td><td>{r['distance']/1000:.2f} km</td></tr>"
            st.markdown(f"""<table class="styled-table"><thead><tr><th>Fecha</th><th>Nombre</th><th>Distancia</th></tr></thead><tbody>{rows}</tbody></table>""", unsafe_allow_html=True)
        else: st.info("Sin actividades.")

    # --- EQUIPO ---
    elif "Equipo" in section:
        st.markdown("## 👟 GESTIÓN DE EQUIPO")
        
        # Cargar zapatillas desde la BD
        if 'shoes_db' not in st.session_state:
            db_shoes = load_shoes()
            # Si la BD está vacía, crear zapatilla por defecto
            if not db_shoes:
                default_shoe = {
                    "id": "asics_cumulus_26",
                    "brand": "Asics",
                    "model": "Cumulus 26",
                    "color": "Azul Marina",
                    "km": 0,
                    "limit": 1000,
                    "status": "active",
                    "img": shoes_img_base64
                }
                save_shoe(default_shoe["id"], default_shoe["brand"], default_shoe["model"], 
                         default_shoe["color"], default_shoe["km"], default_shoe["limit"],
                         default_shoe["status"], default_shoe["img"])
                db_shoes[default_shoe["id"]] = default_shoe
            st.session_state['shoes_db'] = db_shoes
        
        # Calcular km automáticamente desde las actividades
        total_km_shoes = 0
        if activities:
            for activity in activities:
                total_km_shoes += activity.get('distance', 0) / 1000
        
        # Actualizar los km en la BD de zapatillas (solo para Asics Cumulus 26 si es el calculado automáticamente)
        if 'asics_cumulus_26' in st.session_state['shoes_db']:
            st.session_state['shoes_db']['asics_cumulus_26']['km'] = round(total_km_shoes, 1)
            update_shoe_km("asics_cumulus_26", round(total_km_shoes, 1))

        with st.expander("➕ Añadir Nuevas Zapatillas"):
            c1, c2 = st.columns(2)
            nb = c1.text_input("Marca"); nm = c2.text_input("Modelo")
            c3, c4 = st.columns(2)
            nc = c3.text_input("Color"); nk = c4.number_input("KM Iniciales", min_value=0, value=0)
            c5, c6 = st.columns(2)
            nl = c5.number_input("Límite de km", min_value=100, value=800); ni = c6.text_input("URL Foto (Opcional)")
            
            if nb and nm: st.markdown(f"[Buscar foto en Google](https://www.google.com/search?tbm=isch&q={nb}+{nm}+running+shoe)")
            
            if st.button("Guardar"):
                if nb and nm:
                    shoe_id = nb.lower().replace(" ", "_") + "_" + nm.lower().replace(" ", "_")
                    new_shoe = {
                        "id": shoe_id,
                        "brand": nb,
                        "model": nm,
                        "color": nc,
                        "km": nk,
                        "limit": nl,
                        "status": "active",
                        "img": ni if ni else shoes_img_base64
                    }
                    # Guardar en BD
                    save_shoe(shoe_id, nb, nm, nc, nk, nl, "active", new_shoe["img"])
                    st.session_state['shoes_db'][shoe_id] = new_shoe
                    st.success(f"✅ {nb} {nm} añadida!")
                    st.rerun()

        st.subheader("🟢 En Uso")
        act_s = [s for s in st.session_state['shoes_db'].values() if s['status']=='active']
        if act_s:
            cols = st.columns(3)
            for i, s in enumerate(act_s):
                with cols[i%3]:
                    p = min(s['km']/s['limit'], 1.0)
                    clr = "#22c55e" if p < 0.5 else "#f97316" if p < 0.8 else "#ef4444"
                    
                    color_info = f" - {s.get('color', '')}" if s.get('color') else ""
                    gender_info = f" ({s.get('gender', 'Unisex')})" if s.get('gender') else ""
                    
                    st.markdown(f"""<div style="background: linear-gradient(135deg, #1a1a2e 0%, #0f1419 100%); padding: 20px; border-radius: 12px; border: 1px solid #3d3d5c; margin-bottom: 20px;"><div style="height: 140px; overflow: hidden; border-radius: 8px; margin-bottom: 10px; display: flex; align-items: center; justify-content: center; background: #0f0f1e;"><img src="{s['img']}" style="width: 100%; height: 100%; object-fit: contain;"></div><h3 style="margin:0; font-size:1.1rem; color: #f5f5ff;">{s['brand']} {s['model']}</h3><div style="font-size:0.75rem; color: #4db8a8; margin-top:4px;">{color_info}{gender_info}</div><div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-top:10px; color: #d0d0d8;"><span><strong>{s['km']}</strong> km</span><span>{s['limit']} km</span></div><div style="width:100%; background:#2d2d4a; height:8px; border-radius:4px; margin-top:5px;"><div style="width:{p*100}%; background:{clr}; height:8px; border-radius:4px;"></div></div></div>""", unsafe_allow_html=True)
                    
                    c_a, c_b = st.columns(2)
                    if c_a.button("+10km", key=f"a{s['id']}"): 
                        s['km'] += 10
                        update_shoe_km(s['id'], s['km'])
                        st.rerun()
                    if c_b.button("Retirar", key=f"r{s['id']}"): 
                        s['status'] = "retired"
                        update_shoe_status(s['id'], "retired")
                        st.rerun()
        else: st.info("Añade zapatillas.")

    st.divider()
    st.markdown("<div style='text-align: center; color: #999; padding: 20px;'><p>Running Analytics Hub v0.5</p></div>", unsafe_allow_html=True)