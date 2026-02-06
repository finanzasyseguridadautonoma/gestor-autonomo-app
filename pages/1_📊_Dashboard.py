import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

# --- CSS PREMIUM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* FONDO DE LA APP (Un gris muy suave para que resalten las tarjetas blancas) */
    .stApp { background-color: #F8FAFC; }

    /* TARJETAS KPI (Las de arriba) */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    /* Colores bordes KPI */
    div[data-testid="metric-container"]:nth-of-type(1) { border-left: 5px solid #10B981; } /* Ingresos */
    div[data-testid="metric-container"]:nth-of-type(2) { border-left: 5px solid #EF4444; } /* Gastos */
    div[data-testid="metric-container"]:nth-of-type(3) { border-left: 5px solid #3B82F6; } /* Beneficio */
    
    /* HUCHA DESTACADA */
    div[data-testid="metric-container"]:nth-of-type(4) {
        background: linear-gradient(135deg, #FFFBEB 0%, #FFFFFF 100%);
        border: 2px solid #F59E0B;
    }
    div[data-testid="metric-container"]:nth-of-type(4) label { color: #D97706 !important; font-weight: 800; }
    div[data-testid="metric-container"]:nth-of-type(4) div[data-testid="stMetricValue"] { color: #D97706 !important; }

    /* TARJETAS FISCALES */
    .fiscal-card {
        background-color: white;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        text-align: center;
        margin-bottom: 15px;
        border: 1px solid #E2E8F0;
    }
    .fiscal-title { font-size: 0.8rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
    .fiscal-value { font-size: 1.8rem; font-weight: 800; color: #1E293B; }
    .fiscal-note { font-size: 0.75rem; color: #94A3B8; margin-top: 5px; }

    </style>
""", unsafe_allow_html=True)

# CONEXIÓN
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
    st.warning("⚠️ Debes iniciar sesión.")
    st.stop()

# --- LÓGICA DE DATOS ---
client = st.session_state['supabase']
user_id = st.session_state['user'].id

# Cargas de datos
resp_i = client.table('ingresos').select('*').eq('user_id', user_id).execute()
df_i = pd.DataFrame(resp_i.data) if resp_i.data else pd.DataFrame(columns=['base', 'cuota_iva', 'retencion', 'fecha'])

resp_g = client.table('gastos').select('*').eq('user_id', user_id).execute()
df_g = pd.DataFrame(resp_g.data) if resp_g.data else pd.DataFrame(columns=['base', 'cuota_iva', 'retencion', 'fecha'])

# Cálculos
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

# --- VISUALIZACIÓN PULIDA ---

# 1. Saludo limpio (Solo nombre, sin @gmail.com)
nombre_usuario = st.session_state['user'].email.split('@')[0].capitalize()

col_head, col_info = st.columns([3, 1])
with col_head:
    st.markdown(f"### 👋 Hola, **{nombre_usuario}**")
with col_info:
    with st.expander("📲 Instalar App"):
        st.caption("Añade a pantalla de inicio desde tu móvil.")

st.write("") 

# 2. KPIs con Emojis para mejor lectura
c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 Ingresos", f"{facturado:,.2f} €")
c2.metric("💸 Gastos", f"{gastos:,.2f} €")
c3.metric("🚀 Beneficio", f"{beneficio:,.2f} €")
c4.metric("🐷 HUCHA", f"{hucha:,.2f} €", delta="GUARDAR")

st.write("")
st.write("")

# 3. Layout Principal
col_main, col_side = st.columns([2.5, 1], gap="medium")

# --- GRÁFICO MEJORADO ---
with col_main:
    st.subheader("📊 Evolución Mensual")
    
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
        
        # COLORES MÁS MODERNOS
        fig = px.bar(chart_data, x='Mes', y='base', color='Tipo', barmode='group',
                     color_discrete_map={'Ingresos': '#10B981', 'Gastos': '#F43F5E'})
        
        # ESTILIZADO PROFUNDO DEL GRÁFICO
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title=None, # Quitar título eje X
            yaxis_title=None, # Quitar título eje Y
            showlegend=True,  # Mantener leyenda
            legend=dict(
                orientation="h", # Leyenda horizontal
                yanchor="bottom", y=1.02, 
                xanchor="right", x=1,
                title=None # Quitar título de leyenda
            ),
            margin=dict(l=0, r=0, t=20, b=0),
            height=320
        )
        # Quitar líneas feas
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor='#F1F5F9', zeroline=False)
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        # Mensaje vacío elegante
        st.info("Añade tu primera factura para ver el gráfico aquí.")

# --- TARJETAS FISCALES ---
with col_side:
    st.subheader("🏛️ Impuestos")
    
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
