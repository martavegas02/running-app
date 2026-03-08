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

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Running Analytics - Marta Vegas",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- VARIABLES DESDE SECRETS (MODO PORTAFOLIO) ---
# Esto elimina la dependencia de variables locales y usa la configuración de Streamlit Cloud
API_BASE_URL = st.secrets["API_BASE_URL"]
AUTO_LOGIN_USERNAME = st.secrets["AUTO_LOGIN_USERNAME"]
DB_PATH = "/tmp/shoes.db"  # Directorio con permisos de escritura en Streamlit Cloud

# --- INICIALIZACIÓN DE ESTADOS ---
if 'authenticated' not in st.session_state:
    st.session_state.update({
        'authenticated': False,
        'user_id': None,
        'username': None,
        'token': None,
        'auto_login_attempted': False,
        'current_section': "🏠 Dashboard",
        'data_synced': False
    })

# --- CSS PERSONALIZADO (TEMA OSCURO PROFESIONAL) ---
st.markdown("""
    <style>
        header[data-testid="stHeader"] { display: none !important; }
        .block-container { padding-top: 2rem !important; }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%); border-right: 2px solid #FF6B35; }
        .metric-card { background: linear-gradient(135deg, #1a1a2e 0%, #0f1419 100%); border-radius: 14px; padding: 25px; border-top: 4px solid #FF6B35; text-align: center; margin-bottom: 20px; }
        .metric-card .value { font-size: 2.2rem; font-weight: 800; color: #FF6B35 !important; }
        .prediction-card { background: #1a1a2e; border-radius: 16px; padding: 20px; border: 1px solid #3d3d5c; text-align: center; }
        .pred-time { color: #f5f5ff !important; font-size: 1.8rem; font-weight: 700; }
        .styled-table { width: 100%; border-collapse: separate; border-spacing: 0; border-radius: 12px; overflow: hidden; border: 1px solid #3d3d5c; }
        .styled-table thead tr { background: linear-gradient(135deg, #FF6B35 0%, #FF8F5E 100%); color: white; text-align: left; }
        .styled-table th, .styled-table td { padding: 12px 15px; color: #e0e0e8 !important; }
        .styled-table tbody tr { background-color: #1a1a2e; border-bottom: 1px solid #2d2d4a; }
        * { color: #e0e0e8 !important; }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE CONEXIÓN (CON TIMEOUTS PARA RENDER) ---
def login_user(username: str) -> bool:
    try:
        # Timeout de 60s para que la instancia gratuita de Render despierte
        response = requests.post(f"{API_BASE_URL}/auth/simple-login", params={"username": username}, timeout=60)
        if response.status_code == 200:
            data = response.json()
            st.session_state.update({
                'authenticated': True,
                'user_id': data['user']['id'],
                'username': data['user']['username'],
                'token': data['access_token']
            })
            return True
    except: pass
    return False

def sync_data(user_id):
    try: requests.post(f"{API_BASE_URL}/sync/activities?user_id={user_id}", timeout=180)
    except: pass

@st.cache_data(ttl=300)
def fetch_api(endpoint):
    try:
        r = requests.get(f"{API_BASE_URL}{endpoint}", timeout=30)
        return r.json() if r.status_code == 200 else None
    except: return None

# --- LÓGICA DE BASE DE DATOS (EQUIPO) ---
def init_shoes_db():
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS shoes (id TEXT PRIMARY KEY, brand TEXT, model TEXT, km REAL, limit_km REAL, status TEXT, img TEXT)')
    conn.commit(); conn.close()

def load_shoes():
    init_shoes_db(); conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute('SELECT * FROM shoes'); rows = c.fetchall(); conn.close()
    return {r[0]: {"brand": r[1], "model": r[2], "km": r[3], "limit": r[4], "status": r[5], "img": r[6]} for r in rows}

# --- AUTO-ACCESO (SIN LOGIN) ---
if not st.session_state.authenticated:
    with st.status("🚀 Sincronizando con el servidor de Render...", expanded=True) as status:
        if login_user(AUTO_LOGIN_USERNAME):
            status.update(label="✅ Perfil de atleta cargado", state="complete")
            if not st.session_state.data_synced:
                sync_data(st.session_state.user_id)
                st.session_state.data_synced = True
            st.rerun()
        else:
            st.error("📡 El servidor está despertando. Por favor, espera 30 segundos y recarga la página.")
            st.stop()

# --- SIDEBAR NAVEGACIÓN ---
with st.sidebar:
    st.markdown(f"👤 Atleta: **{st.session_state.username}**")
    st.divider()
    sections = ["🏠 Dashboard", "🔮 Predicciones", "📅 Plan de Entrenamiento", "📋 Actividades", "💪 Equipo"]
    for s in sections:
        if st.button(s, use_container_width=True, type="primary" if st.session_state.current_section == s else "secondary"):
            st.session_state.current_section = s
            st.rerun()

# --- CONTENIDO POR SECCIONES ---
user_id = st.session_state.user_id
section = st.session_state.current_section

# 1. DASHBOARD
if "Dashboard" in section:
    st.markdown("## 📈 DASHBOARD DE RENDIMIENTO")
    activities = fetch_api(f"/activities/user/{user_id}") or []
    runs = [a for a in activities if a.get('activity_type', '').lower() == 'run']
    
    if runs:
        total_dist = sum(a.get('distance', 0) for a in runs) / 1000
        total_time = sum(a.get('duration', 0) for a in runs) / 3600
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="metric-card"><h3>Carreras</h3><div class="value">{len(runs)}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><h3>Total KM</h3><div class="value">{total_dist:.1f}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-card"><h3>Horas</h3><div class="value">{total_time:.1f}</div></div>', unsafe_allow_html=True)
        
        df = pd.DataFrame(runs); df['start_date'] = pd.to_datetime(df['start_date'])
        st.markdown("### 📊 Evolución de Distancia")
        st.area_chart(df.set_index('start_date')['distance'] / 1000, color="#FF6B35")
    else: st.info("No hay actividades recientes.")

# 2. PREDICCIONES
elif "Predicciones" in section:
    st.markdown("## 🔮 PREDICCIONES DE CARRERA")
    preds = fetch_api(f"/planning/predictions/{user_id}")
    if preds:
        cols = st.columns(4)
        for i, (dist, key) in enumerate([("5K", "5k"), ("10K", "10k"), ("21K", "half_marathon"), ("42K", "marathon")]):
            d = preds.get(key, {})
            cols[i].markdown(f'<div class="prediction-card"><h4>{dist}</h4><div class="pred-time">{d.get("time","--")}</div><p>Ritmo: {d.get("pace","--")}</p></div>', unsafe_allow_html=True)
    else: st.warning("Datos insuficientes para generar predicciones.")

# 3. PLAN DE ENTRENAMIENTO
elif "Plan" in section:
    st.markdown("## 📅 PLANIFICACIÓN SEMANAL")
    plan = fetch_api(f"/planning/current-plan/{user_id}")
    if plan:
        for s in plan.get('sessions', []):
            with st.expander(f"🏃 {s['day']} - {s.get('planned_distance')} km"):
                st.write(f"**Objetivo:** {s.get('main_workout')}")
                st.write(f"**Ritmo objetivo:** {s.get('planned_pace')}")
    else: st.info("No tienes un plan activo para esta semana.")

# 4. ACTIVIDADES
elif "Actividades" in section:
    st.markdown("## 📋 HISTORIAL COMPLETO")
    activities = fetch_api(f"/activities/user/{user_id}") or []
    if activities:
        rows = "".join([f"<tr><td>{a['start_date'][:10]}</td><td>{a['name']}</td><td>{a['distance']/1000:.2f} km</td></tr>" for a in activities[:15]])
        st.markdown(f'<table class="styled-table"><thead><tr><th>Fecha</th><th>Nombre</th><th>Distancia</th></tr></thead><tbody>{rows}</tbody></table>', unsafe_allow_html=True)

# 5. EQUIPO (ZAPATILLAS)
elif "Equipo" in section:
    st.markdown("## 💪 MI EQUIPO")
    shoes = load_shoes()
    if shoes:
        cols = st.columns(3)
        for i, (sid, s) in enumerate(shoes.items()):
            with cols[i%3]:
                st.image(s['img'] or "https://via.placeholder.com/150", width=200)
                st.markdown(f"**{s['brand']} {s['model']}**")
                st.progress(min(s['km']/s['limit'], 1.0))
                st.write(f"{s['km']} / {s['limit']} km")
    else: st.info("Registra tus zapatillas para controlar su desgaste.")

# --- FOOTER ---
st.markdown("<br><hr><center><p style='color: #666;'>Running Analytics Hub | Portafolio Público</p></center>", unsafe_allow_html=True)