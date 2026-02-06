import streamlit as st
import pandas as pd
from supabase import create_client

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Configuración", page_icon="⚙️", layout="wide")

# --- 2. CSS PREMIUM ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #F8FAFC; }
    
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: white;
        padding: 25px;
        border-radius: 16px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
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

client = st.session_state['supabase']
user_id = st.session_state['user'].id

# --- 4. LAYOUT CONFIGURACIÓN ---
st.title("⚙️ Configuración")
st.write("Ajusta tus preferencias y gestiona tus datos.")
st.write("")

# Dividimos en 2 pestañas grandes
tab_fiscal, tab_datos = st.tabs(["🏛️ FISCALIDAD", "💾 MIS DATOS"])

# --- PESTAÑA 1: PREFERENCIAS FISCALES ---
with tab_fiscal:
    with st.container(border=True):
        st.write("### Valores por Defecto")
        st.caption("Estos valores aparecerán automáticamente cuando crees una factura.")
        
        c1, c2 = st.columns(2)
        with c1:
            st.number_input("IVA por defecto (%)", value=21, step=1)
        with c2:
            st.number_input("IRPF por defecto (%)", value=15, step=1)
            
        st.checkbox("Aplicar IRPF automáticamente en nuevos ingresos", value=True)
        
        st.write("")
        if st.button("Guardar Preferencias"):
            st.toast("Preferencias guardadas (Simulado)", icon="✅")

# --- PESTAÑA 2: EXPORTAR DATOS (IMPORTANTE) ---
with tab_datos:
    st.write("### 📤 Exportar Contabilidad")
    st.write("Descarga tus ingresos y gastos en formato Excel/CSV para enviarlos a tu gestor.")
    
    col_d1, col_d2 = st.columns(2)
    
    # LOGICA DE DESCARGA
    # 1. Traemos datos de Supabase
    try:
        ingresos_data = client.table("ingresos").select("*").eq("user_id", user_id).execute()
        gastos_data = client.table("gastos").select("*").eq("user_id", user_id).execute()
        
        df_ingresos = pd.DataFrame(ingresos_data.data) if ingresos_data.data else pd.DataFrame()
        df_gastos = pd.DataFrame(gastos_data.data) if gastos_data.data else pd.DataFrame()
        
    except:
        df_ingresos = pd.DataFrame()
        df_gastos = pd.DataFrame()

    with col_d1:
        with st.container(border=True):
            st.metric("Total Facturas Ingresos", len(df_ingresos))
            if not df_ingresos.empty:
                # Convertir a CSV
                csv_i = df_ingresos.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="⬇️ Descargar Ingresos (CSV)",
                    data=csv_i,
                    file_name='ingresos_gestor_pro.csv',
                    mime='text/csv',
                    use_container_width=True
                )
            else:
                st.info("No hay ingresos para exportar.")

    with col_d2:
        with st.container(border=True):
            st.metric("Total Tickets Gastos", len(df_gastos))
            if not df_gastos.empty:
                # Convertir a CSV
                csv_g = df_gastos.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="⬇️ Descargar Gastos (CSV)",
                    data=csv_g,
                    file_name='gastos_gestor_pro.csv',
                    mime='text/csv',
                    use_container_width=True
                )
            else:
                st.info("No hay gastos para exportar.")

    st.write("---")
    st.write("### 🚨 Zona de Peligro")
    with st.expander("Borrar todos mis datos"):
        st.error("Esta acción no se puede deshacer.")
        if st.button("🔥 ELIMINAR CUENTA Y DATOS", type="primary"):
            st.error("Por seguridad, contacta con soporte para borrar la cuenta.")
