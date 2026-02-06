import streamlit as st
from supabase import create_client

# --- 1. CONFIGURACIÓN  ---
st.set_page_config(page_title="Gestor Autónomo PRO", layout="wide", page_icon="logo.jpg")

# --- 2. TUS ESTILOS CSS GENERALES ---
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
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    /* HERO SECTION (CABECERA) */
    .hero-box {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        padding: 40px 20px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 40px; 
        box-shadow: 0 10px 30px rgba(37, 99, 235, 0.2);
    }
    
    /* BOTONES TIPO APP (ESTILO MEJORADO) */
    .stButton > button {
        border-radius: 12px; font-weight: 600; border: none;
        background-color: #EFF6FF; color: #2563EB; 
        padding: 0.6rem 1rem; transition: all 0.2s;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        /* Width 100% se maneja ahora con use_container_width en el código Python */
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

# --- 5. LÓGICA DE PANTALLA PRINCIPAL ---
if st.session_state['user'] is None:
    
    # ---------------------------------------------------------
    # A. CABECERA (HERO BOX)
    # ---------------------------------------------------------
    c_left, c_hero, c_right = st.columns([1, 6, 1]) 
    
    with c_hero:
        st.markdown("""
            <div class="hero-box">
                <div style="font-size: 3em; font-weight: 800; margin-bottom: 10px; letter-spacing: -1px;">
                    Gestor Autónomo PRO
                </div>
                <div style="font-size: 1.3em; opacity: 0.9; font-weight: 300;">
                    Tu fiscalidad bajo control.
                </div>
            </div>
        """, unsafe_allow_html=True)

    # ---------------------------------------------------------
    # B. CUERPO TRIPARTITO: VENTAJAS | LOGIN | BANNER
    # ---------------------------------------------------------
    col_izq, col_login, col_der = st.columns([1, 2.2, 1], gap="large")

    # --- 1. IZQUIERDA: VENTAJAS ---
    with col_izq:
        st.write("") 
        st.write("") 
        st.write("")
        st.write("") 
        st.markdown("""
        <div style="color: #475569; padding-left: 10px;">
            <h3 style="color: #1E293B; font-size: 1.4em;">¿Por qué PRO?</h3>
            <div style="margin-bottom: 15px;">
                <strong>✅ Todo Automático</strong><br>
                <span style="font-size: 0.9em;">Olvídate de Excel.</span>
            </div>
            <div style="margin-bottom: 15px;">
                <strong>📊 Visual</strong><br>
                <span style="font-size: 0.9em;">Gráficos en tiempo real.</span>
            </div>
            <div>
                <strong>🔒 Seguro</strong><br>
                <span style="font-size: 0.9em;">Datos encriptados.</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- 2. CENTRO: LOGIN (CON EFECTO CARGA) ---
    with col_login:
        if st.session_state['supabase'] is None:
            st.error("❌ Error de conexión: Revisa secrets.toml")
        else:
            with st.container(border=True):
                st.write("") 
                st.markdown("<h3 style='text-align: center; color: #1E293B; margin: 0;'>Bienvenido 👋</h3>", unsafe_allow_html=True)
                st.write("") 
                
                tab1, tab2 = st.tabs(["Iniciar Sesión", "Crear Cuenta"])
                
                with tab1:
                    st.write("")
                    email = st.text_input("Email", key="login_email")
                    password = st.text_input("Contraseña", type="password", key="login_pass")
                    st.write("") 
                    
                    if st.button("🚀 ENTRAR", use_container_width=True):
                        # SPINNER DE CARGA
                        with st.spinner("🔐 Verificando credenciales..."):
                            try:
                                resp = st.session_state['supabase'].auth.sign_in_with_password({"email": email, "password": password})
                                st.session_state['user'] = resp.user
                                st.rerun()
                            except Exception as e: 
                                st.error("Usuario o contraseña incorrectos")
            
                with tab2:
                    st.write("")
                    email_reg = st.text_input("Email Nuevo", key="reg_email")
                    pass_reg = st.text_input("Contraseña Nueva", type="password", key="reg_pass")
                    st.write("")
                    
                    if st.button("✨ REGISTRARME", use_container_width=True):
                        # SPINNER DE CARGA
                        with st.spinner("📩 Creando tu cuenta..."):
                            try:
                                resp = st.session_state['supabase'].auth.sign_up({"email": email_reg, "password": pass_reg})
                                st.success("¡Cuenta creada! Revisa tu email.")
                            except Exception as e: st.error(f"Error: {e}")
                
                st.write("") 

    # --- 3. DERECHA: BANNER REVOLUT ---
    with col_der:
        st.write("") 
        st.write("") 
        st.write("") 
        st.write("") 

        with st.container(border=True):
            st.caption("✨ **Recomendado**")
            st.image("revolut.jpg", use_container_width=True)
            
            st.markdown("""
            <div style="font-size: 0.85em; color: #64748B; margin-bottom: 15px; line-height: 1.4;">
            La cuenta business que uso para separar impuestos y gastos.
            </div>
            """, unsafe_allow_html=True)
            
            # --- ¡PEGA TU ENLACE AQUÍ! ---
            st.link_button(
                "🎁 Cuenta Gratis", 
                "https://revolut.com/referral/?referral-code=jmorilloarevalo!FEB1-26-AR-CH1H-CRY&geo-redirect", 
                type="primary", 
                use_container_width=True
            )

    # ---------------------------------------------------------
    # C. PIE DE PÁGINA
    # ---------------------------------------------------------
    st.markdown("<br><br><hr>", unsafe_allow_html=True)
    cA, cB, cC = st.columns(3)
    with cA: st.info("📊 **Visual**\n\nImpuestos en tiempo real.")
    with cB: st.warning("⚡ **Automático**\n\nSin cálculos manuales.")
    with cC: st.success("📱 **App**\n\nDesde cualquier lugar.")

else:
    # SI YA ESTÁ LOGUEADO -> REDIRIGIR
    st.switch_page("pages/1_📊_Dashboard.py")



















