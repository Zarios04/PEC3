# ══════════════════════════════════════════════════════════════════════════════
# FASE 3 — Componentes D3.js
# Pega este bloque al FINAL de tu intento1.py (después de la última línea)
# Asegúrate de que d3_components.py esté en la misma carpeta.
# ══════════════════════════════════════════════════════════════════════════════

import streamlit.components.v1 as components
from d3_components import revenue_gap_chart, radial_cancel_clock, bump_chart_seasons

# ── Separador visual ──────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="
    border-top: 2px solid #E2E8F0;
    margin: 2rem 0 1.5rem 0;
    text-align: center;
    position: relative;
">
  <span style="
    position: absolute; top: -13px; left: 50%; transform: translateX(-50%);
    background: #fff; padding: 0 12px;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.72rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: 0.1em;
    color: #94A3B8;
  ">Visualizaciones avanzadas · D3.js</span>
</div>
""", unsafe_allow_html=True)

# ── 1. Revenue Gap ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Ingreso Esperado vs. Dinero No Percibido</div>',
            unsafe_allow_html=True)

components.html(
    revenue_gap_chart(df_interactivo),
    height=160 + len(df_interactivo["hotel"].unique()) * 90,
    scrolling=False,
)

st.markdown("<br>", unsafe_allow_html=True)

# ── 2. Radial Clock + Bump Chart (lado a lado) ─────────────────────────────────
st.markdown('<div class="section-header">Patrones Estacionales</div>',
            unsafe_allow_html=True)

col_rad, col_bump = st.columns(2)

with col_rad:
    components.html(
        radial_cancel_clock(df_interactivo),
        height=460,
        scrolling=False,
    )

with col_bump:
    components.html(
        bump_chart_seasons(df_interactivo),
        height=460,
        scrolling=False,
    )

# ── Footer D3 ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 2rem 0 1rem; font-size: 0.75rem; color: #CBD5E1;">
    Fase 3 completada · Streamlit + Plotly + D3.js v7 &nbsp;|&nbsp;
    Próximo: deploy en Streamlit Community Cloud
</div>
""", unsafe_allow_html=True)
