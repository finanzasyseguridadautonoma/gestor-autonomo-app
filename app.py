import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Gestor Autónomo PRO", layout="wide", page_icon="💼")

# --- 2. CONEXIÓN A SUPABASE ---
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except:
        return None

supabase = init_supabase()

# --- 3. DISEÑO VISUAL (CSS PREMIUM) ---
st.markdown("""
    <style>
    /* FONDO AZUL FRESCO */
    .stApp { background-color: #E3F2FD; color: #0D47A1; }
    
    /* TARJETAS */
    div[data-testid="column"], div[data-testid="stMetric"], div[data-testid="stGraphViz"], div[data-testid="stDataFrame"] {
        background-color: #FFFFFF;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08); 
        border: 1px solid #BBDEFB;
    }
    
    /* COLORES DASHBOARD */
    div[data-testid="stMetric"]:nth-of-type(1) { border-top: 8px solid #2ECC71; } /* Verde */
    div[data-testid="stMetric"]:nth-of-type(2) { border-top: 8px solid #E74C3C; } /* Rojo */
    div[data-testid="stMetric"]:nth-of-type(3) { border-top: 8px solid #3498DB; } /* Azul */
    
    /* HUCHA HACIENDA DESTACADA */
    div[data-testid="stMetric"]:nth-of-type(4) {
        background: linear-gradient(135deg, #FFF9C4 0%, #FFFFFF 100%);
        border: 2px solid #FBC02D;
        box-shadow: 0 4px 15px rgba(251, 192, 45, 0.4);
        transform: scale(1.02);
    }
    div[data-testid="stMetric"]:nth-of-type(4) label { color: #F57F17 !important; font-weight: 900; }
    
    /* HERO SECTION (CABECERA DE ENTRADA) */
    .hero-box {
        background: linear-gradient(120deg, #1565C0 0%, #42A5F5 100%);
        padding: 50px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(21, 101, 192, 0.3);
    }

    /* BOTONES */
    .stButton > button {
        border-radius: 50px; font-weight: bold; border: 1px solid #1565C0;
        background-color: white; color: #1565C0; transition: all 0.3s;
    }
    .stButton > button:hover { background-color: #1565C0; color: white; transform: translateY(-2px); }
    
    /* CABECERAS PLANES */
    .plan-header {
        padding: 20px; border-radius: 12px 12px 0 0; color: white;
        text-align: center; font-weight: 800; font-size: 1.2em;
        margin: -21px -21px 20px -21px; text-transform: uppercase;
    }
    
    h1, h2, h3 { color: #0D47A1 !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. GESTIÓN DE SESIÓN Y DATOS ---
if 'user' not in st.session_state: st.session_state['user'] = None
if 'plan' not in st.session_state: st.session_state['plan'] = 'DEMO'
if 'navegacion' not in st.session_state: st.session_state['navegacion'] = "🏠 Dashboard"

# Inicializar vacíos por seguridad
if 'ingresos' not in st.session_state: 
    st.session_state['ingresos'] = pd.DataFrame(columns=['fecha', 'cliente', 'base', 'iva_pct', 'cuota_iva', 'irpf_pct', 'retencion', 'total'])
if 'gastos' not in st.session_state: 
    st.session_state['gastos'] = pd.DataFrame(columns=['fecha', 'proveedor', 'categoria', 'base', 'iva_pct', 'cuota_iva', 'irpf_pct', 'retencion', 'total'])

LIMITES = {'DEMO': 15, 'NORMAL': 20, 'PRO': 999999}

def cargar_datos():
    """Descarga datos de Supabase"""
    if st.session_state['user'] is None: return
    try:
        user_id = st.session_state['user']['id']
        
        # Cargar Plan
        try:
            resp_perfil = supabase.table('perfiles').select('plan').eq('id', user_id).execute()
            if resp_perfil.data: st.session_state['plan'] = resp_perfil.data[0]['plan']
        except: st.session_state['plan'] = 'DEMO'

        # Cargar Ingresos
        resp_ing = supabase.table('ingresos').select('*').eq('user_id', user_id).execute()
        st.session_state['ingresos'] = pd.DataFrame(resp_ing.data) if resp_ing.data else pd.DataFrame(columns=['fecha', 'cliente', 'base', 'iva_pct', 'cuota_iva', 'irpf_pct', 'retencion', 'total'])

        # Cargar Gastos
        resp_gas = supabase.table('gastos').select('*').eq('user_id', user_id).execute()
        st.session_state['gastos'] = pd.DataFrame(resp_gas.data) if resp_gas.data else pd.DataFrame(columns=['fecha', 'proveedor', 'categoria', 'base', 'iva_pct', 'cuota_iva', 'irpf_pct', 'retencion', 'total'])
    
    except Exception as e:
        st.error(f"Error cargando datos: {e}")

def check_limite():
    total = len(st.session_state['ingresos']) + len(st.session_state['gastos'])
    return total >= LIMITES.get(st.session_state['plan'], 15)

def ir_a_ingresos(): st.session_state['navegacion'] = "💰 Ingresos"
def ir_a_gastos(): st.session_state['navegacion'] = "💸 Gastos"

# --- 5. PANTALLA DE ENTRADA (LANDING PAGE) ---
def auth_page():
    # Hero Box
    st.markdown("""
        <div class="hero-box">
            <div style="font-size: 3.5em; font-weight: 900; margin-bottom: 15px;">Gestor Autónomo PRO</div>
            <div style="font-size: 1.5em; opacity: 0.95; font-weight: 300;">Tu fiscalidad bajo control. Fácil, visual y automático.</div>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if supabase is None:
            st.error("❌ Error de conexión: Revisa secrets.toml")
            return

        st.info("👋 **Bienvenido/a**. Inicia sesión para ver tus datos.")
        
        tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])
        with tab1:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Contraseña", type="password", key="login_pass")
            if st.button("🚀 ENTRAR", use_container_width=True):
                try:
                    resp = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state['user'] = resp.user
                    cargar_datos()
                    st.rerun()
                except Exception as e: st.error(f"Error: {e}")
        with tab2:
            email_reg = st.text_input("Email Nuevo", key="reg_email")
            pass_reg = st.text_input("Contraseña Nueva", type="password", key="reg_pass")
            if st.button("✨ CREAR CUENTA", use_container_width=True):
                try:
                    resp = supabase.auth.sign_up({"email": email_reg, "password": pass_reg})
                    st.success("¡Cuenta creada! Ya puedes iniciar sesión.")
                except Exception as e: st.error(f"Error: {e}")

    st.markdown("---")
    cA, cB, cC = st.columns(3)
    with cA: st.info("📊 **Visual e Intuitivo**\n\nMira tus impuestos en tiempo real con gráficas claras.")
    with cB: st.warning("⚡ **Cálculo Automático**\n\nOlvídate de calcular el IVA y el IRPF manual.")
    with cC: st.success("📱 **Multiplataforma**\n\nTus datos en la nube, accesibles desde móvil y PC.")

def logout():
    supabase.auth.sign_out()
    st.session_state['user'] = None
    st.session_state['ingresos'] = pd.DataFrame()
    st.session_state['gastos'] = pd.DataFrame()
    st.rerun()

# --- 6. PÁGINAS INTERNAS ---

def pagina_dashboard():
    st.markdown(f"### 👋 Hola, **{st.session_state['user'].email}**")
    
    df_i = st.session_state.get('ingresos', pd.DataFrame())
    df_g = st.session_state.get('gastos', pd.DataFrame())

    # Cálculos seguros
    facturado = df_i['base'].sum() if not df_i.empty and 'base' in df_i.columns else 0.0
    gastos = df_g['base'].sum() if not df_g.empty and 'base' in df_g.columns else 0.0
    
    iva_rep = df_i['cuota_iva'].sum() if not df_i.empty and 'cuota_iva' in df_i.columns else 0.0
    iva_sop = df_g['cuota_iva'].sum() if not df_g.empty and 'cuota_iva' in df_g.columns else 0.0
    
    ret_sop = df_i['retencion'].sum() if not df_i.empty and 'retencion' in df_i.columns else 0.0
    ret_prac = df_g['retencion'].sum() if not df_g.empty and 'retencion' in df_g.columns else 0.0
    
    mod_303 = iva_rep - iva_sop
    beneficio = facturado - gastos
    mod_130 = (beneficio * 0.20) - ret_sop
    if mod_130 < 0: mod_130 = 0
    mod_111 = ret_prac
    hucha = mod_303 + mod_130 + mod_111
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Ingresos", f"{facturado:.2f} €")
    c2.metric("Gastos", f"{gastos:.2f} €")
    c3.metric("Beneficio", f"{beneficio:.2f} €")
    c4.metric("🚨 HUCHA", f"{hucha:.2f} €", delta="GUARDAR")
    
    st.write("")
    
    # GRÁFICA
    st.subheader("📈 Evolución Mensual")
    chart_data = pd.DataFrame()
    if not df_i.empty and 'fecha' in df_i.columns:
        temp_i = df_i.copy()
        temp_i['Tipo'] = 'Ingresos'
        temp_i['Mes'] = pd.to_datetime(temp_i['fecha']).dt.strftime('%Y-%m')
        chart_data = pd.concat([chart_data, temp_i[['Mes', 'base', 'Tipo']]])
    if not df_g.empty and 'fecha' in df_g.columns:
        temp_g = df_g.copy()
        temp_g['Tipo'] = 'Gastos'
        temp_g['Mes'] = pd.to_datetime(temp_g['fecha']).dt.strftime('%Y-%m')
        chart_data = pd.concat([chart_data, temp_g[['Mes', 'base', 'Tipo']]])
        
    if not chart_data.empty:
        chart_data = chart_data.groupby(['Mes', 'Tipo'], as_index=False)['base'].sum()
        fig = px.bar(chart_data, x='Mes', y='base', color='Tipo', barmode='group',
                     color_discrete_map={'Ingresos': '#2ECC71', 'Gastos': '#E74C3C'})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Añade movimientos para ver la gráfica.")

    # IMPUESTOS
    st.markdown("---")
    st.subheader("🏛️ Previsión Fiscal Trimestral")
    t1, t2, t3 = st.columns(3)
    with t1: st.info(f"**MODELO 303 (IVA)**\n\n# {mod_303:.2f} €\n*(Lo que has cobrado de IVA menos lo que has pagado)*")
    with t2: st.warning(f"**MODELO 130 (IRPF)**\n\n# {mod_130:.2f} €\n*(20% de tu beneficio acumulado)*")
    with t3: st.error(f"**MODELO 111 (Retenciones)**\n\n# {mod_111:.2f} €\n*(IRPF retenido en facturas de profesionales)*")

    # ACCIONES RÁPIDAS
    st.markdown("---")
    st.subheader("⚡ Acciones Rápidas")
    b1, b2 = st.columns(2)
    b1.button("➕ AÑADIR NUEVO INGRESO", use_container_width=True, on_click=ir_a_ingresos)
    b2.button("➖ AÑADIR NUEVO GASTO", use_container_width=True, on_click=ir_a_gastos)

def pagina_ingresos():
    st.title("💰 Registrar Ingresos")
    if check_limite(): st.error("Límite alcanzado.")
    else:
        with st.form("fi"):
            c1,c2 = st.columns(2)
            fecha = c1.date_input("Fecha")
            cli = c2.text_input("Cliente")
            c3,c4,c5 = st.columns(3)
            base = c3.number_input("Base", step=10.0)
            iva = c4.selectbox("IVA", [0,4,10,21], index=3)
            irpf = c5.selectbox("IRPF", [0,7,15], index=0)
            if st.form_submit_button("Guardar"):
                c_iva = base * (iva/100)
                ret = base * (irpf/100)
                tot = base + c_iva - ret
                supabase.table('ingresos').insert({
                    "user_id": st.session_state['user']['id'], "fecha": str(fecha), "cliente": cli,
                    "base": base, "iva_pct": iva, "cuota_iva": c_iva, "irpf_pct": irpf, "retencion": ret, "total": tot
                }).execute()
                cargar_datos()
                st.rerun()
    st.dataframe(st.session_state['ingresos'], use_container_width=True)

def pagina_gastos():
    st.title("💸 Registrar Gastos")
    if check_limite(): st.error("Límite alcanzado.")
    else:
        with st.form("fg"):
            c1,c2 = st.columns(2)
            fecha = c1.date_input("Fecha")
            prov = c2.text_input("Proveedor")
            cat = st.selectbox("Categoría", ["Servicios", "Suministros", "Alquiler"])
            c3,c4,c5 = st.columns(3)
            base = c3.number_input("Base", step=10.0)
            iva = c4.selectbox("IVA", [0,4,10,21], index=3)
            irpf = c5.selectbox("IRPF", [0,7,15,19], index=0)
            if st.form_submit_button("Guardar"):
                c_iva = base * (iva/100)
                ret = base * (irpf/100)
                tot = base + c_iva - ret
                supabase.table('gastos').insert({
                    "user_id": st.session_state['user']['id'], "fecha": str(fecha), "proveedor": prov, "categoria": cat,
                    "base": base, "iva_pct": iva, "cuota_iva": c_iva, "irpf_pct": irpf, "retencion": ret, "total": tot
                }).execute()
                cargar_datos()
                st.rerun()
    st.dataframe(st.session_state['gastos'], use_container_width=True)

def pagina_planes():
    st.title("💎 Suscripción")
    
    # -------------------------------------------------------------
    # ⚠️ PEGA AQUÍ TUS ENLACES DE STRIPE (CON PRUEBA GRATUITA 7 DÍAS)
    LINK_NORMAL = "https://buy.stripe.com/test_PON_AQUI_TU_ENLACE_NORMAL"
    LINK_PRO    = "https://buy.stripe.com/test_PON_AQUI_TU_ENLACE_PRO"
    # -------------------------------------------------------------

    c1, c2, c3 = st.columns(3)
    
    # PLAN GRATIS
    with c1:
        st.markdown("""
            <div class="plan-header" style="background-color: #64748B;">🌱 GRATIS</div>
            <h2 style="text-align:center; color:#333;">0 €</h2>
            <hr>
            <ul style="list-style: none; padding:0; color: #4B5563;">
                <li>✅ 15 Registros prueba</li>
                <li>✅ Dashboard Básico</li>
                <li>❌ Soporte</li>
            </ul>
        """, unsafe_allow_html=True)
        if st.session_state['plan'] == 'DEMO':
            st.button("PLAN ACTUAL", disabled=True, key="btn_free")
    
    # PLAN NORMAL
    with c2:
        st.markdown("""
            <div class="plan-header" style="background-color: #3B82F6;">🚀 NORMAL</div>
            <h2 style="text-align:center; color:#333;">4.99 €<small>/mes</small></h2>
            <center><span style="background-color:#E0F2F1; color:#00695C; padding: 2px 8px; border-radius:10px; font-size:0.8em;">🎁 7 DÍAS GRATIS</span></center>
            <hr>
            <ul style="list-style: none; padding:0; color: #4B5563;">
                <li>✅ <b>20 Registros/mes</b></li>
                <li>✅ Dashboard Completo</li>
                <li>✅ Soporte Email</li>
            </ul>
        """, unsafe_allow_html=True)
        if st.session_state['plan'] == 'NORMAL':
            st.button("✅ TU PLAN ACTUAL", disabled=True)
        else:
            st.link_button("👉 SUSCRIBIRSE", "https://buy.stripe.com/bJe14g0hL3Wq9f86BXg7e02")

    # PLAN PRO
    with c3:
        st.markdown("""
            <div class="plan-header" style="background: linear-gradient(to right, #F59E0B, #D97706);">👑 PRO</div>
            <h2 style="text-align:center; color:#333;">11.99 €<small>/mes</small></h2>
            <center><span style="background-color:#FFF3E0; color:#E65100; padding: 2px 8px; border-radius:10px; font-size:0.8em;">🎁 7 DÍAS GRATIS</span></center>
            <hr>
            <ul style="list-style: none; padding:0; color: #4B5563;">
                <li>🔥 <b>ILIMITADO</b></li>
                <li>🔥 <b>Gestor Personal</b></li>
                <li>✅ Soporte Email</li>
            </ul>
        """, unsafe_allow_html=True)
        if st.session_state['plan'] == 'PRO':
            st.button("✅ TU PLAN ACTUAL", disabled=True)
        else:
            st.link_button("👉 SUSCRIBIRSE", "https://buy.stripe.com/fZucMYaWp50u1MGgcxg7e01")

    st.write("")
    st.info("ℹ️ **Sin compromiso:** Tienes 7 días de prueba gratis. Puedes cancelar cuando quieras antes de que termine el periodo.")

# --- 7. CONTROLADOR PRINCIPAL BLINDADO ---
if st.session_state['user'] is None:
    auth_page()
else:
    # SEGURIDAD: Verificar datos
    if 'ingresos' not in st.session_state or st.session_state['ingresos'] is None:
        cargar_datos()

    with st.sidebar:
        st.write(f"Usuario: {st.session_state['user'].email}")
        opcion = st.radio("Menú", ["🏠 Dashboard", "💰 Ingresos", "💸 Gastos", "💎 Suscripción"], key='navegacion')
        if st.button("Cerrar Sesión"): logout()

    if "Dashboard" in opcion: pagina_dashboard()
    elif "Ingresos" in opcion: pagina_ingresos()
    elif "Gastos" in opcion: pagina_gastos()
    elif "Suscripción" in opcion: pagina_planes()