import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# --- TUS ESTILOS ESPECÍFICOS DEL DASHBOARD ---
st.markdown("""
    <style>
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
    </style>
""", unsafe_allow_html=True)

# CONEXIÓN (Necesaria en cada página)
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except: return None

if 'supabase' not in st.session_state: st.session_state['supabase'] = init_supabase()

# SEGURIDAD
if 'user' not in st.session_state or st.session_state['user'] is None:
    st.warning("⚠️ Debes iniciar sesión en la página principal.")
    st.stop()

# --- TU LÓGICA DE DATOS Y CÁLCULOS ---
client = st.session_state['supabase']
user_id = st.session_state['user'].id

# Cargar Ingresos
resp_i = client.table('ingresos').select('*').eq('user_id', user_id).execute()
df_i = pd.DataFrame(resp_i.data) if resp_i.data else pd.DataFrame(columns=['base', 'cuota_iva', 'retencion', 'fecha'])

# Cargar Gastos
resp_g = client.table('gastos').select('*').eq('user_id', user_id).execute()
df_g = pd.DataFrame(resp_g.data) if resp_g.data else pd.DataFrame(columns=['base', 'cuota_iva', 'retencion', 'fecha'])

# CÁLCULOS EXACTOS
facturado = df_i['base'].sum() if not df_i.empty else 0.0
gastos = df_g['base'].sum() if not df_g.empty else 0.0

iva_rep = df_i['cuota_iva'].sum() if not df_i.empty else 0.0
iva_sop = df_g['cuota_iva'].sum() if not df_g.empty else 0.0

ret_sop = df_i['retencion'].sum() if not df_i.empty else 0.0
ret_prac = df_g['retencion'].sum() if not df_g.empty else 0.0

mod_303 = iva_rep - iva_sop
beneficio = facturado - gastos
mod_130 = (beneficio * 0.20) - ret_sop
if mod_130 < 0: mod_130 = 0
mod_111 = ret_prac
hucha = mod_303 + mod_130 + mod_111

# --- VISUALIZACIÓN ---
st.markdown(f"### 👋 Hola, **{st.session_state['user'].email}**")

# Tip de instalación
with st.expander("📲 ¿Cómo instalar la App en tu móvil?"):
    st.info("1. Pulsa en **Compartir** (iPhone) o los **3 puntitos** (Android).\n2. Elige **'Añadir a Pantalla de Inicio'**.")

st.write("") 

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
