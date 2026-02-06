import streamlit as st
from supabase import create_client

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Mi Perfil", page_icon="👤", layout="wide")

# --- 2. CSS PREMIUM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F8FAFC; }

    /* Tarjetas */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white;
        padding: 25px;
        border-radius: 16px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    /* Avatar Simulado */
    .avatar-circle {
        width: 100px; height: 100px;
        background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
        border-radius: 50%;
        color: white;
        display: flex; align-items: center; justify-content: center;
        font-size: 40px; font-weight: bold;
        margin: 0 auto 15px auto;
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONEXIÓN ---
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except: return None

if 'supabase' not in st.session_state: st.session_state['supabase'] = init_supabase()
if 'user' not in st.session_state or st.session_state['user'] is None:
    st.warning("⚠️ Inicia sesión primero.")
    st.stop()

# --- LÓGICA USUARIO ---
user = st.session_state['user']
email = user.email
inicial = email[0].upper()
nombre_usuario = email.split("@")[0].capitalize()

# --- 4. LAYOUT PERFIL ---
st.title("👤 Mi Perfil")
st.write("")

col_left, col_right = st.columns([1, 2], gap="large")

# --- COLUMNA IZQUIERDA: TARJETA RESUMEN ---
with col_left:
    with st.container(border=True):
        st.markdown(f'<div class="avatar-circle">{inicial}</div>', unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; margin:0;'>{nombre_usuario}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #64748B;'>{email}</p>", unsafe_allow_html=True)
        
        st.write("---")
        st.write("**Plan Actual:**")
        # Badge de plan PRO
        st.markdown("""
        <div style="background-color: #EFF6FF; color: #2563EB; padding: 8px; border-radius: 8px; text-align: center; font-weight: bold; border: 1px solid #BFDBFE;">
            ✨ GESTOR PRO
        </div>
        """, unsafe_allow_html=True)
        st.caption("Suscripción activa hasta 2025")
        
        st.write("")
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state['user'] = None
            st.switch_page("app.py")

# --- COLUMNA DERECHA: DATOS Y SEGURIDAD ---
with col_right:
    
    # SECCIÓN 1: DATOS PERSONALES
    st.subheader("📝 Datos de Facturación")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Nombre Completo", value=nombre_usuario)
            st.text_input("NIF / DNI", placeholder="12345678X")
        with c2:
            st.text_input("Dirección Fiscal", placeholder="Calle Ejemplo, 123")
            st.text_input("Código Postal", placeholder="28000")
            
        if st.button("💾 Actualizar Datos"):
            st.success("Datos guardados localmente (Simulación).")

    st.write("")
    
    # SECCIÓN 2: SEGURIDAD
    st.subheader("🔒 Seguridad")
    with st.container(border=True):
        st.write("Cambiar Contraseña")
        pass_new = st.text_input("Nueva Contraseña", type="password")
        pass_conf = st.text_input("Confirmar Contraseña", type="password")
        
        if st.button("🔄 Actualizar Contraseña"):
            if pass_new == pass_conf and len(pass_new) > 5:
                try:
                    st.session_state['supabase'].auth.update_user({"password": pass_new})
                    st.success("¡Contraseña actualizada correctamente!")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Las contraseñas no coinciden o son muy cortas.")
