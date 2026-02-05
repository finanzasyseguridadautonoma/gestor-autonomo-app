import streamlit as st

st.set_page_config(page_title="Suscripción", page_icon="💎")

# --- TUS ESTILOS EXACTOS DE PLANES ---
st.markdown("""
<style>
    .plan-header {
        padding: 15px; border-radius: 12px 12px 0 0; color: white;
        text-align: center; font-weight: 800; font-size: 1.1em;
        margin: -16px -16px 15px -16px; text-transform: uppercase; letter-spacing: 1px;
    }
    .stButton > button { width: 100%; }
</style>
""", unsafe_allow_html=True)

st.title("💎 Suscripción")

# ⚠️ ENLACES STRIPE (PON LOS TUYOS)
LINK_NORMAL = "https://buy.stripe.com/..." 
LINK_PRO    = "https://buy.stripe.com/..."

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
        <div class="plan-header" style="background-color: #64748B;">🌱 GRATIS</div>
        <h2 style="text-align:center;">0 €</h2>
        <hr>
        <ul style="list-style: none; padding:0; color: #4B5563;">
            <li>✅ 5 Registros prueba</li>
            <li>✅ Dashboard Básico</li>
            <li>❌ Soporte</li>
        </ul>
    """, unsafe_allow_html=True)
    st.button("PLAN ACTUAL", disabled=True, key="btn_free")

with c2:
    st.markdown("""
        <div class="plan-header" style="background-color: #3B82F6;">🚀 NORMAL</div>
        <h2 style="text-align:center;">4.99 €<small>/mes</small></h2>
        <center><span style="background-color:#E0F2F1; color:#00695C; padding: 2px 8px; border-radius:10px; font-size:0.8em;">🎁 3 DÍAS GRATIS</span></center>
        <hr>
        <ul style="list-style: none; padding:0; color: #4B5563;">
            <li>✅ <b>20 Registros/mes</b></li>
            <li>✅ Dashboard Completo</li>
            <li>✅ Soporte Email</li>
        </ul>
    """, unsafe_allow_html=True)
    st.link_button("👉 SUSCRIBIRSE", "https://buy.stripe.com/8x23co9Sl8cG770gcxg7e09")

with c3:
    st.markdown("""
        <div class="plan-header" style="background: linear-gradient(to right, #F59E0B, #D97706);">👑 PRO</div>
        <h2 style="text-align:center;">11.99 €<small>/mes</small></h2>
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
    st.link_button("👉 SUSCRIBIRSE", "https://buy.stripe.com/aFa5kw1lP0Kebng5xTg7e08")

st.write("")
st.info("ℹ️ Tienes 3 días de prueba gratis. Cancela cuando quieras.")
