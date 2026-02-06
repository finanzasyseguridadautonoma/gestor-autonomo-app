import streamlit as st
from supabase import create_client

# --- 1. CONFIGURACIÓN  ---
st.set_page_config(page_title="Gestor Autónomo PRO", layout="wide", page_icon="logo.jpg")

# --- 2. TUS ESTILOS CSS GENERALES (MEJORADOS) ---
st.markdown("""
    <style>
    /* IMPORTAR FUENTE MODERNA (INTER) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* OCULTAR ELEMENTOS NATIVOS */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* FONDO Y COLOR GENERAL */
    .stApp { background-color: #F8FAFC; color: #1E293B; }
    
    /* ESPACIADO */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
    }

    /* HERO SECTION (PANTALLA LOGIN) - CORREGIDO EL CENTRADO */
    .hero-box {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        padding: 20px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 0px; /* Quitamos margen para alinear con el banner */
        box-shadow: 0 10px 30px rgba(37, 99, 235, 0.3);
        
        /* TRUCOS PARA CENTRADO PERFECTO */
        height: 100%;       /* Intenta ocupar toda la altura */
        min-height: 220px;  /* Altura mínima para que coincida con el banner */
        display: flex;
        flex-direction: column;
        justify-content: center; /* Centra VERTICALMENTE */
        align-items: center;     /* Centra HORIZONTALMENTE */
    }
    
    /* BOTONES TIPO APP */
    .stButton > button {
        border-radius: 12px; font-weight: 600; border: none;
        background-color: #EFF6FF; color: #2563EB; 
        padding: 0.5rem 1rem; transition: all 0.2s;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .stButton > button:hover { 
        background-color: #2563EB; color: white; 
        box-shadow: 0 5px 15px rgba(37, 99, 235, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONEXIÓN A SUPABASE ---
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except:
        return None

if 'supabase' not in st.session_state:
    st.session_state['supabase'] = init_supabase()

# --- 4. GESTIÓN DE SESIÓN ---
if 'user' not in st.session_state: st.session_state['user'] = None

# --- 5. LÓGICA DE LOGIN ---
if st.session_state['user'] is None:
    
    # ---------------------------------------------------------
    # CABECERA ALINEADA: HERO + BANNER
    # ---------------------------------------------------------
    # Ajustamos gap="small" para que estén más juntitos si quieres
    col_hero, col_banner = st.columns([3, 1], gap="medium")

    with col_hero:
        st.markdown("""
            <div class="hero-box">
                <div style="font-size: 2.8em; font-weight: 900; line-height: 1.2;">Gestor Autónomo PRO</div>
                <div style="font-size: 1.2em; opacity: 0.95; font-weight: 300; margin-top: 10px;">Tu fiscalidad bajo control</div>
            </div>
        """, unsafe_allow_html=True)

    with col_banner:
        # Contenedor del Banner
        with st.container(border=True):
            st.caption("✨ **Recomendado**")
            # Usamos el link Web para evitar errores de archivo
            st.image("revolut.jpg", use_container_width=True)
            
            # TU ENLACE AQUÍ
            st.link_button(
                "🎁 Abrir Cuenta Gratis", 
                "https://revolut.com/referral/?referral-code=jmorilloarevalo!FEB1-26-AR-CH1H-CRY&geo-redirect", 
                type="primary", 
                use_container_width=True
            )
    
    # ---------------------------------------------------------

    st.write("") # Espacio separador
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.session_state['supabase'] is None:
            st.error("❌ Error de conexión: Revisa secrets.toml")
        else:
            tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])
            with tab1:
                email = st.text_input("Email", key="login_email")
                password = st.text_input("Contraseña", type="password", key="login_pass")
                if st.button("🚀 ENTRAR", use_container_width=True):
                    try:
                        resp = st.session_state['supabase'].auth.sign_in_with_password({"email": email, "password": password})
                        st.session_state['user'] = resp.user
                        st.rerun() 
                    except Exception as e: st.error(f"Error: {e}")
            with tab2:
                email_reg = st.text_input("Email Nuevo", key="reg_email")
                pass_reg = st.text_input("Contraseña Nueva", type="password", key="reg_pass")
                if st.button("✨ CREAR CUENTA", use_container_width=True):
                    try:
                        resp = st.session_state['supabase'].auth.sign_up({"email": email_reg, "password": pass_reg})
                        st.success("¡Cuenta creada! Ya puedes iniciar sesión.")
                    except Exception as e: st.error(f"Error: {e}")

    st.markdown("---")
    cA, cB, cC = st.columns(3)
    with cA: st.info("📊 **Visual**\n\nImpuestos en tiempo real.")
    with cB: st.warning("⚡ **Automático**\n\nSin cálculos manuales.")
    with cC: st.success("📱 **App**\n\nDesde cualquier lugar.")

else:
    # SI YA ESTÁ LOGUEADO -> REDIRIGIR AL DASHBOARD
    st.switch_page("pages/1_📊_Dashboard.py")
















