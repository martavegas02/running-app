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
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Running Analytics - Marta Vegas",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- VARIABLES DESDE SECRETS ---
# Forzamos el uso de las credenciales de Streamlit Cloud
API_BASE_URL = st.secrets.get("API_BASE_URL", "https://irunning-app-7mdo.onrender.com/api/v1")
AUTO_LOGIN_USERNAME = st.secrets.get("AUTO_LOGIN_USERNAME", "martavegas02")
DB_PATH = "/tmp/shoes.db"  # Ruta con permisos de escritura en la nube

# --- INICIALIZACIÓN DE SESIÓN ---
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

# --- CSS PERSONALIZADO ---
st.markdown("""
    <style>
        header[data-testid="stHeader"] { display: none !important; }
        .block-container { padding-top: 2rem !important; }
        [data-testid="stSidebar"] { background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%); border-right: 2px solid #FF6B35; }
        .metric-card { background: linear-gradient(135deg, #1a1a2e 0%, #0f1419 100%); border-radius: 14px; padding: 25px; border-top: 4px solid #FF6B35; text-align: center; margin-bottom: 20px; }
        .metric-card .value { font-size: 2.2rem; font-weight: 800; color: #FF6B35 !important; }
        .styled-table { width: 100%; border-collapse: separate; border-spacing: 0; border-radius: 12px; overflow: hidden; border: 1px solid #3d3d5c; }
        .styled-table thead tr { background: linear-gradient(135deg, #FF6B35 0%, #FF8F5E 100%); color: white; text-align: left; }
        .styled-table th, .styled-table td { padding: 12px 15px; color: #e0e0e8 !important; }
        .styled-table tbody tr { background-color: #1a1a2e; border-bottom: 1px solid #2d2d4a; }
        * { color: #e0e0e8 !important; }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES API (CON TIMEOUTS PARA RENDER) ---
def login_user(username: str) -> bool:
    try:
        # Timeout de 60s para que Render despierte
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
    try:
        requests.post(f"{API_BASE_URL}/sync/activities?user_id={user_id}", timeout=180)
        return True
    except: return False

@st.cache_data(ttl=300)
def fetch_api(endpoint):
    try:
        r = requests.get(f"{API_BASE_URL}{endpoint}", timeout=30)
        return r.json() if r.status_code == 200 else None
    except: return None

# --- LÓGICA DE BASE DE DATOS LOCAL (ZAPATILLAS) ---
def init_shoes_db():
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS shoes (id TEXT PRIMARY KEY, brand TEXT, model TEXT, km REAL, limit_km REAL, status TEXT, img TEXT)')
    conn.commit(); conn.close()

def load_shoes():
    init_shoes_db(); conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute('SELECT * FROM shoes'); rows = c.fetchall(); conn.close()
    return {r[0]: {"brand": r[1], "model": r[2], "km": r[3], "limit": r[4], "status": r[5], "img": r[6]} for r in rows}

# --- LÓGICA DE ACCESO AUTOMÁTICO ---
if not st.session_state.authenticated:
    with st.status("🚀 Conectando con el servidor de Render...", expanded=True) as status:
        if login_user(AUTO_LOGIN_USERNAME):
            status.update(label="✅ Perfil de atleta cargado", state="complete")
            st.rerun()
        else:
            # Reintento automático si el servidor sigue durmiendo
            time.sleep(10)
            st.rerun()

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"👤 Atleta: **{st.session_state.username}**")
    if st.button("🔄 Sincronizar Strava"):
        with st.spinner("Buscando nuevas carreras..."):
            if sync_data(st.session_state.user_id):
                st.cache_data.clear()
                st.success("¡Datos actualizados!")
                st.rerun()

    st.divider()
    sections = ["🏠 Dashboard", "🔮 Predicciones", "📅 Plan de Entrenamiento", "📋 Actividades", "💪 Equipo"]
    for s in sections:
        if st.button(s, use_container_width=True, type="primary" if st.session_state.current_section == s else "secondary"):
            st.session_state.current_section = s
            st.rerun()

# --- CONTENIDO ---
user_id = st.session_state.user_id
section = st.session_state.current_section

if "Dashboard" in section:
    st.markdown("## 📈 ESTADÍSTICAS GENERALES")
    activities = fetch_api(f"/activities/user/{user_id}") or []
    runs = [a for a in activities if a.get('activity_type', '').lower() == 'run']
    
    if runs:
        total_dist = sum(a.get('distance', 0) for a in runs) / 1000
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="metric-card"><h3>Total Carreras</h3><div class="value">{len(runs)}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><h3>Kilómetros Totales</h3><div class="value">{total_dist:.1f} km</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-card"><h3>Atleta</h3><div class="value">{st.session_state.username}</div></div>', unsafe_allow_html=True)
        
        df = pd.DataFrame(runs); df['start_date'] = pd.to_datetime(df['start_date'])
        st.area_chart(df.set_index('start_date')['distance'] / 1000, color="#FF6B35")
    else: st.info("Usa el botón lateral para sincronizar tus carreras.")

elif "Predicciones" in section:
    st.markdown("## 🔮 ESTIMACIÓN DE TIEMPOS")
    preds = fetch_api(f"/planning/predictions/{user_id}")
    if preds:
        cols = st.columns(4)
        for i, (dist, key) in enumerate([("5K", "5k"), ("10K", "10k"), ("21K", "half_marathon"), ("42K", "marathon")]):
            d = preds.get(key, {})
            cols[i].markdown(f'<div class="metric-card"><h3>{dist}</h3><div class="value" style="font-size:1.5rem">{d.get("time","--")}</div></div>', unsafe_allow_html=True)
    else: st.warning("No hay suficientes datos para predecir tiempos.")

elif "Actividades" in section:
    st.markdown("## 📋 HISTORIAL DE CARRERAS")
    activities = fetch_api(f"/activities/user/{user_id}") or []
    if activities:
        df_act = pd.DataFrame(activities)
        st.dataframe(df_act[['start_date', 'name', 'distance', 'duration']], use_container_width=True)

elif "Equipo" in section:
    st.markdown("## 💪 GESTIÓN DE ZAPATILLAS")
    shoes = load_shoes()
    if shoes:
        cols = st.columns(3)
        for i, (sid, s) in enumerate(shoes.items()):
            with cols[i%3]:
                st.markdown(f'<div class="metric-card"><h3>{s["brand"]}</h3><p>{s["model"]}</p></div>', unsafe_allow_html=True)
                st.progress(min(s['km']/s['limit'], 1.0))
    else: st.info("Registra tu equipo en la base de datos.")

st.markdown("<center><p style='color: #666;'>Running Analytics Hub | Portafolio Público v1.0</p></center>", unsafe_allow_html=True)