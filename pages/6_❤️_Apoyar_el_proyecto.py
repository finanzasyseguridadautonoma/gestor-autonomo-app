import streamlit as st

st.set_page_config(page_title="Apoyar el Proyecto", page_icon="❤️")

st.title("❤️ ¿Te ha sido útil esta herramienta?")

st.write("""
Mantener 'Gestor Autónomo PRO' activo y actualizado requiere tiempo y pagar los servidores.
La App es 100% gratuita para ti, pero si quieres invitarme a un café virtual y apoyar el desarrollo, 
la mejor forma es usar la herramienta que yo mismo uso para mis finanzas.
""")

st.divider()

# --- SECCIÓN REVOLUT ---
col_img, col_txt = st.columns([1, 2], gap="medium")

with col_img:
    st.image("revolut.jpg", use_container_width=True)

with col_txt:
    st.subheader("🏦 Revolut para Autónomos")
    st.write("""
    Es la cuenta que uso para separar el dinero de los impuestos. 
    Sin comisiones ocultas y con tarjetas virtuales para compras online seguras.
    """)
    
    # --- TU ENLACE AQUÍ ---
    mi_enlace = "https://revolut.com/referral/?referral-code=jmorilloarevalo!FEB1-26-AR-CH1H-CRY&geo-redirect"
    
    st.link_button("🎁 Abrir Cuenta Gratis y Apoyar", mi_enlace, type="primary")

st.info("""
**ℹ️ Para que tu apoyo cuente:**
1. Regístrate y valida tu identidad.
2. Pide la tarjeta física (¡importante!).
3. Haz 3 gastos normales con ella.
""")
