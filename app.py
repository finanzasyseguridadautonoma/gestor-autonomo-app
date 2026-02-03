import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Gestor Autónomo PRO", layout="wide", page_icon="logo.jpg")

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

# --- 3. DISEÑO VISUAL (CSS PRO - MODO APP NATIVA) ---
st.markdown("""
    <style>
    /* IMPORTAR FUENTE MODERNA (INTER) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* QUITAR ELEMENTOS DE NAVEGADOR (HEADER, FOOTER, MENU) */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* FONDO Y COLOR GENERAL */
    .stApp { background-color: #F8FAFC; color: #1E293B; }
    
    /* REDUCIR ESPACIOS PARA MÓVIL */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    /* TARJETAS CON EFECTO "GLASS" */
    div[data-testid="column"], div[data-testid="stMetric"], div[data-testid="stDataFrame"] {
        background-color: #FFFFFF;
        border-radius: 16px;
        padding: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05); 
        border: none;
    }
    
    /* COLORES DASHBOARD */
    div[data-testid="stMetric"]:nth-of-type(1) { border-left: 6px solid #10B981; } 
    div[data-testid="stMetric"]:nth-of-type(2) { border-left: 6px solid #EF4444; } 
    div[data-testid="stMetric"]:nth-of-type(3) { border-left: 6px solid #3B82F6; } 
    
    /* HUCHA HACIENDA */
    div[data-testid="stMetric"]:nth-of-type(4) {
        background: linear-gradient(135deg, #FFFBEB 0%, #FFFFFF 100%);
        border: 2px solid #F59E0B;
    }
    div[data-testid="stMetric"]:nth-of-type(4) label { color: #D97706 !important; font-weight: 800; }
    
    /* HERO SECTION */
    .hero-box {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%);
        padding: 30px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(37, 99, 235, 0.3);
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
    
    .plan-header {
        padding: 15px; border-radius: 12px 12px 0 0; color: white;
        text-align: center; font-weight: 800; font-size: 1.1em;
        margin: -16px -16px 15px -16px; text-transform: uppercase; letter-spacing: 1px;
    }
    
    h1, h2, h3 { color: #1E293B !important; font-family: 'Inter', sans-serif; font-weight: 800; }
    </style>
""", unsafe_allow_html=True)

# --- 4. GESTIÓN DE SESIÓN ---
if 'user' not in st.session_state: st.session_state['user'] = None
if 'plan' not in st.session_state: st.session_state['plan'] = 'DEMO'
if 'navegacion' not in st.session_state: st.session_state['navegacion'] = "🏠 Dashboard"

if 'ingresos' not in st.session_state: 
    st.session_state['ingresos'] = pd.DataFrame(columns=['id', 'fecha', 'cliente', 'base', 'iva_pct', 'cuota_iva', 'irpf_pct', 'retencion', 'total'])
if 'gastos' not in st.session_state: 
    st.session_state['gastos'] = pd.DataFrame(columns=['id', 'fecha', 'proveedor', 'categoria', 'base', 'iva_pct', 'cuota_iva', 'irpf_pct', 'retencion', 'total'])

LIMITES = {'DEMO': 5, 'NORMAL': 20, 'PRO': 999999}

def cargar_datos():
    if st.session_state['user'] is None: return
    try:
        user_id = st.session_state['user'].id 
        try:
            resp_perfil = supabase.table('perfiles').select('plan').eq('id', user_id).execute()
            if resp_perfil.data: st.session_state['plan'] = resp_perfil.data[0]['plan']
        except: st.session_state['plan'] = 'DEMO'

        resp_ing = supabase.table('ingresos').select('*').eq('user_id', user_id).execute()
        st.session_state['ingresos'] = pd.DataFrame(resp_ing.data) if resp_ing.data else pd.DataFrame(columns=['id', 'fecha', 'cliente', 'base', 'iva_pct', 'cuota_iva', 'irpf_pct', 'retencion', 'total'])

        resp_gas = supabase.table('gastos').select('*').eq('user_id', user_id).execute()
        st.session_state['gastos'] = pd.DataFrame(resp_gas.data) if resp_gas.data else pd.DataFrame(columns=['id', 'fecha', 'proveedor', 'categoria', 'base', 'iva_pct', 'cuota_iva', 'irpf_pct', 'retencion', 'total'])
    except Exception as e:
        st.error(f"Error cargando datos: {e}")

def check_limite():
    total = len(st.session_state['ingresos']) + len(st.session_state['gastos'])
    return total >= LIMITES.get(st.session_state['plan'], 5)

def ir_a_ingresos(): st.session_state['navegacion'] = "💰 Ingresos"
def ir_a_gastos(): st.session_state['navegacion'] = "💸 Gastos"

# --- 5. PÁGINAS ---

def auth_page():
    st.markdown("""
        <div class="hero-box">
            <div style="font-size: 2.5em; font-weight: 900; margin-bottom: 10px;">Gestor Autónomo PRO</div>
            <div style="font-size: 1.2em; opacity: 0.95; font-weight: 300;">Tu fiscalidad bajo control.</div>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if supabase is None:
            st.error("❌ Error de conexión: Revisa secrets.toml")
            return

        st.info("👋 **Bienvenido/a**. Inicia sesión.")
        
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
    with cA: st.info("📊 **Visual**\n\nImpuestos en tiempo real.")
    with cB: st.warning("⚡ **Automático**\n\nSin cálculos manuales.")
    with cC: st.success("📱 **App**\n\nDesde cualquier lugar.")

def logout():
    supabase.auth.sign_out()
    st.session_state['user'] = None
    st.session_state['ingresos'] = pd.DataFrame()
    st.session_state['gastos'] = pd.DataFrame()
    st.rerun()

def pagina_dashboard():
    st.markdown(f"### 👋 Hola, **{st.session_state['user'].email}**")
    
    # --- AVISO INSTALACIÓN APP (TIP 1) ---
    with st.expander("📲 ¿Cómo instalar la App en tu móvil?"):
        st.info("""
        1. Pulsa en **Compartir** (iPhone) o los **3 puntitos** (Android).
        2. Elige **"Añadir a Pantalla de Inicio"**.
        3. ¡Listo! Se abrirá a pantalla completa.
        """)
    st.write("") 

    df_i = st.session_state.get('ingresos', pd.DataFrame())
    df_g = st.session_state.get('gastos', pd.DataFrame())

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
                     color_discrete_map={'Ingresos': '#10B981', 'Gastos': '#EF4444'})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Añade movimientos para ver la gráfica.")

    st.markdown("---")
    st.subheader("🏛️ Previsión Fiscal")
    t1, t2, t3 = st.columns(3)
    with t1: st.info(f"**MODELO 303 (IVA)**\n\n# {mod_303:.2f} €")
    with t2: st.warning(f"**MODELO 130 (IRPF)**\n\n# {mod_130:.2f} €")
    with t3: st.error(f"**MODELO 111 (Retenciones)**\n\n# {mod_111:.2f} €")

    st.markdown("---")
    st.subheader("⚡ Acciones Rápidas")
    b1, b2 = st.columns(2)
    b1.button("➕ NUEVO INGRESO", use_container_width=True, on_click=ir_a_ingresos)
    b2.button("➖ NUEVO GASTO", use_container_width=True, on_click=ir_a_gastos)

def pagina_ingresos():
    st.title("💰 Registrar Ingresos")
    if check_limite(): st.error("Límite alcanzado (Máx 5 en Demo).")
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
                    "user_id": st.session_state['user'].id, 
                    "fecha": str(fecha), "cliente": cli,
                    "base": base, "iva_pct": iva, "cuota_iva": c_iva, "irpf_pct": irpf, "retencion": ret, "total": tot
                }).execute()
                cargar_datos()
                st.rerun()
    
    df = st.session_state['ingresos']
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        st.markdown("---")
        st.subheader("🗑️ Borrar")
        opciones = [f"{row['id']} | {row['fecha']} - {row['cliente']} ({row['total']} €)" for index, row in df.iterrows()]
        col_del1, col_del2 = st.columns([3, 1])
        seleccion = col_del1.selectbox("Selecciona cuál borrar:", opciones, label_visibility="collapsed")
        if col_del2.button("Eliminar", type="primary"):
            id_borrar = seleccion.split(" | ")[0]
            try:
                supabase.table('ingresos').delete().eq('id', id_borrar).execute()
                st.success("✅ Eliminado."); cargar_datos(); st.rerun()
            except Exception as e: st.error(f"Error: {e}")

def pagina_gastos():
    st.title("💸 Registrar Gastos")
    if check_limite(): st.error("Límite alcanzado (Máx 5 en Demo).")
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
                    "user_id": st.session_state['user'].id,
                    "fecha": str(fecha), "proveedor": prov, "categoria": cat,
                    "base": base, "iva_pct": iva, "cuota_iva": c_iva, "irpf_pct": irpf, "retencion": ret, "total": tot
                }).execute()
                cargar_datos()
                st.rerun()

    df = st.session_state['gastos']
    st.dataframe(df, use_container_width=True)

    if not df.empty:
        st.markdown("---")
        st.subheader("🗑️ Borrar")
        opciones = [f"{row['id']} | {row['fecha']} - {row['proveedor']} ({row['total']} €)" for index, row in df.iterrows()]
        col_del1, col_del2 = st.columns([3, 1])
        seleccion = col_del1.selectbox("Selecciona cuál borrar:", opciones, label_visibility="collapsed")
        if col_del2.button("Eliminar", type="primary"):
            id_borrar = seleccion.split(" | ")[0]
            try:
                supabase.table('gastos').delete().eq('id', id_borrar).execute()
                st.success("✅ Eliminado."); cargar_datos(); st.rerun()
            except Exception as e: st.error(f"Error: {e}")

def pagina_planes():
    st.title("💎 Suscripción")
    
    # ⚠️ -------------------------------------------------------------
    # ⚠️ ZONA DE ENLACES (¡No borres las comillas!)
    LINK_NORMAL = "https://buy.stripe.com/fZu8wI2pT78CgHA9O9g7e04" 
    LINK_PRO    = "https://buy.stripe.com/PON_AQUI_TU_ENLACE_PRO"
    # ----------------------------------------------------------------

    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("""
            <div class="plan-header" style="background-color: #64748B;">🌱 GRATIS</div>
            <h2 style="text-align:center; color:#333;">0 €</h2>
            <hr>
            <ul style="list-style: none; padding:0; color: #4B5563;">
                <li>✅ 5 Registros prueba</li>
                <li>✅ Dashboard Básico</li>
                <li>❌ Soporte</li>
            </ul>
        """, unsafe_allow_html=True)
        if st.session_state['plan'] == 'DEMO': 
            st.button("PLAN ACTUAL", disabled=True, key="btn_free")

    with c2:
        st.markdown("""
            <div class="plan-header" style="background-color: #3B82F6;">🚀 NORMAL</div>
            <h2 style="text-align:center; color:#333;">4.99 €<small>/mes</small></h2>
            <center><span style="background-color:#E0F2F1; color:#00695C; padding: 2px 8px; border-radius:10px; font-size:0.8em;">🎁 3 DÍAS GRATIS</span></center>
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
            st.link_button("👉 SUSCRIBIRSE", "https://buy.stripe.com/8x23co9Sl8cG770gcxg7e09")

    with c3:
        st.markdown("""
            <div class="plan-header" style="background: linear-gradient(to right, #F59E0B, #D97706);">👑 PRO</div>
            <h2 style="text-align:center; color:#333;">11.99 €<small>/mes</small></h2>
            <center>
                <span style="background-color:#FFF3E0; color:#E65100; padding: 2px 8px; border-radius:10px; font-size:0.8em;">🎁 3 DÍAS GRATIS</span>
            </center>
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
            st.link_button("👉 SUSCRIBIRSE", "https://buy.stripe.com/aFa5kw1lP0Kebng5xTg7e08")
    
    st.write("")
    st.info("ℹ️ Tienes 3 días de prueba gratis. Cancela cuando quieras.")

# --- 6. CONTROLADOR PRINCIPAL BLINDADO ---
if st.session_state['user'] is None:
    auth_page()
else:
    if 'ingresos' not in st.session_state or st.session_state['ingresos'] is None:
        cargar_datos()

    with st.sidebar:
        st.write(f"Usuario: {st.session_state['user'].email}")
        opcion = st.radio("Menú", ["🏠 Dashboard", "💰 Ingresos", "💸 Gastos", "💎 Suscripción"], key='navegacion')
        
        # --- TIP 2: SOPORTE TÉCNICO ---
        st.markdown("---")
        st.caption("¿Necesitas ayuda?")
        st.markdown("📧 [Soporte Técnico](mailto:finanzasyseguridadautonoma@gmail.com)")
        st.markdown("---")
        # ------------------------------

        if st.button("Cerrar Sesión"): logout()

    if "Dashboard" in opcion: pagina_dashboard()
    elif "Ingresos" in opcion: pagina_ingresos()
    elif "Gastos" in opcion: pagina_gastos()
    elif "Suscripción" in opcion: pagina_planes()