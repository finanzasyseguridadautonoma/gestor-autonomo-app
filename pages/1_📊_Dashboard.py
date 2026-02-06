import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# --- CSS MEJORADO (ESTILO PREMIUM) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* TARJETAS KPI (Las de arriba) */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #F1F5F9;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    /* Colores específicos para cada métrica por orden */
    div[data-testid="metric-container"]:nth-of-type(1) { border-left: 5px solid #10B981; } /* Ingresos - Verde */
    div[data-testid="metric-container"]:nth-of-type(2) { border-left: 5px solid #EF4444; } /* Gastos - Rojo */
    div[data-testid="metric-container"]:nth-of-type(3) { border-left: 5px solid #3B82F6; } /* Beneficio - Azul */
    
    /* LA HUCHA (La 4ª métrica) - Destacada */
    div[data-testid="metric-container"]:nth-of-type(4) {
        background: linear-gradient(135deg, #FFFBEB 0%, #FFFFFF 100%);
        border: 2px solid #F59E0B;
    }
    div[data-testid="metric-container"]:nth-of-type(4) label { color: #D97706 !important; font-weight: 800; }
    div[data-testid="metric-container"]:nth-of-type(4) div[data-testid="stMetricValue"] { color: #D97706 !important; }

    /* TARJETAS FISCALES (Abajo) */
    .fiscal-card {
        background-color: white;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        text-align: center;
        margin-bottom: 10px;
    }
    .fiscal-title { font-size: 0.85rem; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }
    .fiscal-value { font-size: 2rem; font-weight: 800; color: #1E293B; }
    .fiscal-note { font-size: 0.8rem; color: #94A3B8; margin-top: 5px; }

    </style>
""", unsafe_allow_html=True)

# CONEXIÓN (TU CÓDIGO INTACTO)
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except: return None

if 'supabase' not in st.session_state: st.session_state['supabase'] = init_supabase()

# SEGURIDAD (TU CÓDIGO INTACTO)
if 'user' not in st.session_state or st.session_state['user'] is None:
    st.warning("⚠️ Debes iniciar sesión en la página principal.")
    st.stop()

# --- TU LÓGICA DE DATOS Y CÁLCULOS (INTACTA) ---
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

# --- VISUALIZACIÓN MEJORADA ---

# 1. Cabecera más limpia
col_head, col_info = st.columns([3, 1])
with col_head:
    st.markdown(f"### 👋 Hola, **{st.session_state['user'].email.split('@')[0]}**")
with col_info:
    # El expander lo hacemos más discreto
    with st.expander("📲 Instalar App"):
        st.caption("1. Pulsa Compartir/Opciones.\n2. 'Añadir a Pantalla de Inicio'.")

st.write("") 

# 2. KPIs (El CSS de arriba hace la magia aquí)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Ingresos", f"{facturado:,.2f} €")
c2.metric("Gastos", f"{gastos:,.2f} €")
c3.metric("Beneficio", f"{beneficio:,.2f} €")
c4.metric("🐷 HUCHA", f"{hucha:,.2f} €", delta="GUARDAR")

st.write("")
st.write("")

# 3. Estructura Principal: Gráfico (70%) + Previsión Fiscal (30%)
# Esto hace que se vea mucho más profesional que todo uno debajo de otro
col_main, col_side = st.columns([2.5, 1], gap="medium")

# --- COLUMNA IZQUIERDA: GRÁFICO ---
with col_main:
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
        
        # Gráfico estéticamente mejorado
        fig = px.bar(chart_data, x='Mes', y='base', color='Tipo', barmode='group',
                     color_discrete_map={'Ingresos': '#10B981', 'Gastos': '#EF4444'})
        
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(showgrid=True, gridcolor='#F1F5F9'), # Rejilla sutil
            xaxis=dict(showgrid=False),
            margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Añade movimientos para ver la gráfica.")

# --- COLUMNA DERECHA: TARJETAS FISCALES "BONITAS" ---
with col_side:
    st.subheader("🏛️ Impuestos")
    
    # Usamos HTML puro para controlar el diseño exacto
    st.markdown(f"""
    <div class="fiscal-card" style="border-top: 4px solid #3B82F6;">
        <div class="fiscal-title">Modelo 303 (IVA)</div>
        <div class="fiscal-value">{mod_303:,.2f} €</div>
        <div class="fiscal-note">Liquidación trimestral</div>
    </div>
    
    <div class="fiscal-card" style="border-top: 4px solid #F59E0B;">
        <div class="fiscal-title">Modelo 130 (IRPF)</div>
        <div class="fiscal-value">{mod_130:,.2f} €</div>
        <div class="fiscal-note">20% s/beneficio</div>
    </div>
    
    <div class="fiscal-card" style="border-top: 4px solid #EF4444;">
        <div class="fiscal-title">Modelo 111</div>
        <div class="fiscal-value">{mod_111:,.2f} €</div>
        <div class="fiscal-note">Retenciones practicadas</div>
    </div>
    """, unsafe_allow_html=True)
