import streamlit as st

st.set_page_config(page_title="Soporte", page_icon="📩")

st.title("📩 Soporte Técnico")

st.markdown("""
### ¿Necesitas ayuda?
Si tienes dudas sobre cómo usar la App, problemas con tu suscripción o sugerencias fiscales, estamos aquí.
""")

# --- TU CORREO VISIBLE ---
st.info("📧 Puedes escribirnos directamente a: **finanzasyseguridadautonoma@gmail.com**")

st.divider()

# --- FORMULARIO DE CONTACTO ---
st.write("O si prefieres, mándanos un mensaje rápido desde aquí:")

with st.form("form_soporte"):
    email_usuario = st.text_input("Tu Email (para contestarte)")
    asunto = st.selectbox("Asunto", ["Duda Técnica", "Problema con el Pago", "Sugerencia", "Otro"])
    mensaje = st.text_area("Cuéntanos qué pasa")
    
    enviar = st.form_submit_button("Enviar Mensaje")
    
    if enviar:
        # Aquí es visual, en el futuro podrías conectarlo para que te llegue un email real
        st.success("✅ Hemos recibido tu mensaje. Te contestaremos en menos de 24h.")
        st.balloons()
