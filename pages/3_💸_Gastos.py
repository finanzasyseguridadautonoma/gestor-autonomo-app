import streamlit as st
import datetime
from supabase import create_client

st.set_page_config(page_title="Gastos", page_icon="💸")

if 'supabase' not in st.session_state:
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        st.session_state['supabase'] = create_client(url, key)
    except: st.error("Error conexión")

if 'user' not in st.session_state or st.session_state['user'] is None:
    st.warning("⚠️ Inicia sesión primero."); st.stop()

st.title("💸 Registrar Gastos")

with st.form("fg"):
    c1,c2 = st.columns(2)
    fecha = c1.date_input("Fecha")
    prov = c2.text_input("Proveedor")
    cat = st.selectbox("Categoría", ["Servicios", "Suministros", "Alquiler", "Herramientas", "Gestoría", "Otros"])
    c3,c4,c5 = st.columns(3)
    base = c3.number_input("Base (€)", step=10.0)
    iva = c4.selectbox("IVA %", [0,4,10,21], index=3)
    irpf = c5.selectbox("IRPF %", [0,7,15,19], index=0)
    
    if st.form_submit_button("Guardar Gasto"):
        c_iva = base * (iva/100)
        ret = base * (irpf/100)
        tot = base + c_iva - ret
        
        try:
            st.session_state['supabase'].table('gastos').insert({
                "user_id": st.session_state['user'].id,
                "fecha": str(fecha), "proveedor": prov, "categoria": cat,
                "base": base, "iva_pct": iva, "cuota_iva": c_iva, 
                "irpf_pct": irpf, "retencion": ret, "total": tot
            }).execute()
            st.success("✅ Gasto registrado")
            st.rerun()
        except Exception as e: st.error(f"Error: {e}")

st.divider()

client = st.session_state['supabase']
resp = client.table('gastos').select('*').eq('user_id', st.session_state['user'].id).execute()

if resp.data:
    st.dataframe(resp.data, use_container_width=True)
    
    st.markdown("---")
    st.subheader("🗑️ Borrar Gasto")
    opciones = [f"{row['id']} | {row['fecha']} - {row['proveedor']} ({row['total']} €)" for row in resp.data]
    col_del1, col_del2 = st.columns([3, 1])
    seleccion = col_del1.selectbox("Selecciona cuál borrar:", opciones, label_visibility="collapsed")
    
    if col_del2.button("Eliminar", type="primary"):
        id_borrar = seleccion.split(" | ")[0]
        client.table('gastos').delete().eq('id', id_borrar).execute()
        st.success("✅ Eliminado")
        st.rerun()
