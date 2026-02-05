import streamlit as st
import datetime
from supabase import create_client

st.set_page_config(page_title="Ingresos", page_icon="💰")

# CONEXIÓN
if 'supabase' not in st.session_state:
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        st.session_state['supabase'] = create_client(url, key)
    except: st.error("Error conexión")

if 'user' not in st.session_state or st.session_state['user'] is None:
    st.warning("⚠️ Inicia sesión primero."); st.stop()

st.title("💰 Registrar Ingresos")

# TU FORMULARIO
with st.form("fi"):
    c1,c2 = st.columns(2)
    fecha = c1.date_input("Fecha")
    cli = c2.text_input("Cliente")
    c3,c4,c5 = st.columns(3)
    base = c3.number_input("Base (€)", step=10.0)
    iva = c4.selectbox("IVA %", [0,4,10,21], index=3)
    irpf = c5.selectbox("IRPF %", [0,7,15], index=0)
    
    if st.form_submit_button("Guardar Factura"):
        # TUS CÁLCULOS
        c_iva = base * (iva/100)
        ret = base * (irpf/100)
        tot = base + c_iva - ret
        
        try:
            st.session_state['supabase'].table('ingresos').insert({
                "user_id": st.session_state['user'].id, 
                "fecha": str(fecha), "cliente": cli,
                "base": base, "iva_pct": iva, "cuota_iva": c_iva, 
                "irpf_pct": irpf, "retencion": ret, "total": tot
            }).execute()
            st.success("✅ Guardado correctamente")
            st.rerun()
        except Exception as e: st.error(f"Error: {e}")

st.divider()

# TU TABLA Y BORRADO
client = st.session_state['supabase']
resp = client.table('ingresos').select('*').eq('user_id', st.session_state['user'].id).execute()

if resp.data:
    st.dataframe(resp.data, use_container_width=True)
    
    st.markdown("---")
    st.subheader("🗑️ Borrar Factura")
    opciones = [f"{row['id']} | {row['fecha']} - {row['cliente']} ({row['total']} €)" for row in resp.data]
    col_del1, col_del2 = st.columns([3, 1])
    seleccion = col_del1.selectbox("Selecciona cuál borrar:", opciones, label_visibility="collapsed")
    
    if col_del2.button("Eliminar", type="primary"):
        id_borrar = seleccion.split(" | ")[0]
        client.table('ingresos').delete().eq('id', id_borrar).execute()
        st.success("✅ Eliminado")
        st.rerun()
