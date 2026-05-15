import streamlit as st
import pandas as pd
import os
import plotly.express as px
import streamlit.components.v1 as components
from d3_components import revenue_gap_chart, radial_cancel_clock, bump_chart_seasons

# Configuración inicial de la aplicación
st.set_page_config(
    page_title="Estudio de dos Hoteles en Portugal",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Carga de datos
MONTH_ORDER = ["January","February","March","April","May","June","July","August","September","October","November","December"]
MONTH_ES = {"January":"Ene","February":"Feb","March":"Mar","April":"Abr","May":"May","June":"Jun","July":"Jul","August":"Ago","September":"Sep","October":"Oct","November":"Nov","December":"Dic"}

FILE_PATH = "Datos_procesados_python.xlsx"

@st.cache_data
def load_data(path):
    df = pd.read_excel(path)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    df["arrival_date_month"] = pd.Categorical(df["arrival_date_month"], categories=MONTH_ORDER, ordered=True)
    df["mes_corto"] = df["arrival_date_month"].map(MONTH_ES)
    noches = df["stays_in_weekend_nights"] + df["stays_in_week_nights"]
    df["total_revenue"] = df["adr"] * noches.clip(lower=0)
    df["dinero_perdido"] = df["total_revenue"] * df["is_canceled"]
    df["estado"] = df["is_canceled"].map({0: "Confirmada", 1: "Cancelada"})
    df["año"] = df["arrival_date_year"].astype(str)
    return df

try:
    df = load_data(FILE_PATH)
except FileNotFoundError:
    st.error(f"❌ No se encontró el archivo '{FILE_PATH}'.")
    st.stop()

lista_hoteles = sorted(df["hotel"].unique())
hotel_1 = lista_hoteles[0] if len(lista_hoteles) > 0 else "Hotel 1"
hotel_2 = lista_hoteles[1] if len(lista_hoteles) > 1 else "Hotel 2"

if "vista_activa" not in st.session_state:
    st.session_state.vista_activa = "Global"

# Título y subtítulo centrado
st.markdown("""
<div class="hero-box">
    <h1 class="hero-title">Estudio de dos Hoteles en Portugal</h1>
    <p class="hero-subtitle">
        Un análisis visual diseñado para comprender a fondo la dinámica de las reservas, 
        los patrones estacionales de cancelación y el comportamiento de los ingresos, 
        entre el 2015 y 2017.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.1rem; color: #475569; max-width: 800px; margin: 0 auto 30px auto; text-align: center; line-height: 1.6;">
    La industria hotelera se enfrenta a un riesgo financiero constante: las reservas canceladas. 
    Se busca explorar la dinámica de dos propiedades en Portugal (City Hotel y Resort Hotel) 
    entre 2015 y 2017. Con el objetivo de identificar patrones de comportamiento, cuantificar el impacto 
    financiero real en ese periodo de tiempo y descubrir oportunidades estratégicas para mitigar estas pérdidas.
</div>
""", unsafe_allow_html=True)

# Distribución de botones estilo Boceto Paint
st.markdown('<div class="navigation-grid">', unsafe_allow_html=True)

is_global_active = st.session_state.vista_activa == "Global"
if st.button(
    " Ver Completo (Global)", 
    key="btn_nav_global", 
    use_container_width=True,
    type="primary" if is_global_active else "secondary"
):
    st.session_state.vista_activa = "Global"
    st.rerun()

st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    is_h1_active = st.session_state.vista_activa == "Hotel 1"
    if st.button(f" {hotel_1}", key="btn_nav_h1", use_container_width=True, type="primary" if is_h1_active else "secondary"):
        st.session_state.vista_activa = "Hotel 1"
        st.rerun()

with c2:
    is_comp_active = st.session_state.vista_activa == "Comparativa"
    if st.button(" Comparativa de KPIs", key="btn_nav_comp", use_container_width=True, type="primary" if is_comp_active else "secondary"):
        st.session_state.vista_activa = "Comparativa"
        st.rerun()

with c3:
    is_h2_active = st.session_state.vista_activa == "Hotel 2"
    if st.button(f" {hotel_2}", key="btn_nav_h2", use_container_width=True, type="primary" if is_h2_active else "secondary"):
        st.session_state.vista_activa = "Hotel 2"
        st.rerun()

# Barra de filtro temporales

if "años_activos" not in st.session_state:
    st.session_state.años_activos = sorted(list(df["año"].unique()))

if "estaciones_activas" not in st.session_state:
    st.session_state.estaciones_activas = sorted(list(df["estacion"].unique()))

with st.sidebar:
    st.markdown("<h2 style='font-family: \"Playfair Display\", serif; color: #1E3A8A; font-size: 1.6rem; margin-bottom: 25px;'>Filtros Globales </h2>", unsafe_allow_html=True)
    
    # FILTRO: AÑOS
    st.markdown("<div style='font-family: \"Plus Jakarta Sans\"; font-weight: 700; color: #1E3A8A; font-size: 0.9rem; margin-bottom: 6px;'>AÑO:</div>", unsafe_allow_html=True)
    años_disponibles = sorted(list(df["año"].unique()))
    
    for año in años_disponibles:
        es_activo = año in st.session_state.años_activos
        todos_activos = len(st.session_state.años_activos) == len(años_disponibles)

        if st.button(
            f"📅 {año}", 
            key=f"btn_filtro_año_{año}", 
            type="primary" if es_activo else "secondary", 
            use_container_width=True # Estira el botón al ancho total de la barra lateral
        ):
            if todos_activos:
                st.session_state.años_activos = [año]
            else:
                if not es_activo:
                    st.session_state.años_activos.append(año)
                else:
                    st.session_state.años_activos = años_disponibles.copy()
            st.rerun()

    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

    # FILTRO: ESTACIONES 
    st.markdown("<div style='font-family: \"Plus Jakarta Sans\"; font-weight: 700; color: #1E3A8A; font-size: 0.9rem; margin-bottom: 6px;'>ESTACIÓN:</div>", unsafe_allow_html=True)
    estaciones_disponibles = sorted(list(df["estacion"].unique()))
    
    for estacion in estaciones_disponibles:
        es_activa = estacion in st.session_state.estaciones_activas
        todas_activas = len(st.session_state.estaciones_activas) == len(estaciones_disponibles)
        
        if st.button(
            estacion, 
            key=f"btn_filtro_est_{estacion}", 
            type="primary" if es_activa else "secondary", 
            use_container_width=True
        ):
            if todas_activas:
                st.session_state.estaciones_activas = [estacion]
            else:
                if not es_activa:
                    st.session_state.estaciones_activas.append(estacion)
                else:
                    st.session_state.estaciones_activas = estaciones_disponibles.copy()
            st.rerun()

    st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

# Data Frame interactivo final 
df_interactivo = df[
    (df["año"].isin(st.session_state.años_activos)) & 
    (df["estacion"].isin(st.session_state.estaciones_activas))
]

def renderizar_6_kpis(dataframe_filtrado):
    total_res   = len(dataframe_filtrado)
    total_rev   = dataframe_filtrado["total_revenue"].sum()
    tasa_cancel = dataframe_filtrado["is_canceled"].mean() * 100
    adr_prom    = dataframe_filtrado["adr"].mean()
    lead_prom   = dataframe_filtrado["lead_time"].mean()
    noches_prom = (dataframe_filtrado["stays_in_weekend_nights"] + dataframe_filtrado["stays_in_week_nights"]).mean()

    metrics = [
        ("Reservaciones",    f"{total_res:,}",          "total"),
        ("Ingresos totales Esperados", f"${total_rev:,.0f}",      "revenue"),
        ("Tasa cancelación", f"{tasa_cancel:.1f}%",       "cancel"),
        ("ADR promedio",     f"${adr_prom:,.2f}",       "adr"),
        ("Anticipación",     f"{lead_prom:.0f} días",    "lead"),
        ("Noches promedio",  f"{noches_prom:.1f}",       "nights"),
    ]
    
    columnas = st.columns(6)
    for i, (label, val, cls) in enumerate(metrics):
        columnas[i].markdown(
            f'<div class="kpi-card kpi-{cls}"><div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{val}</div></div>',
            unsafe_allow_html=True
        )

# Renderizado de vistas
vista = st.session_state.vista_activa

if vista == "Global":
    st.markdown('<div class="section-header">Métricas Consolidadas (Ambos Hoteles)</div>', unsafe_allow_html=True)
    renderizar_6_kpis(df_interactivo)

elif vista == "Hotel 1":
    df_h1 = df_interactivo[df_interactivo["hotel"] == hotel_1]
    st.markdown(f'<div class="section-header">Rendimiento Operacional: {hotel_1}</div>', unsafe_allow_html=True)
    renderizar_6_kpis(df_h1)

elif vista == "Hotel 2":
    df_h2 = df_interactivo[df_interactivo["hotel"] == hotel_2]
    st.markdown(f'<div class="section-header">Rendimiento Operacional: {hotel_2}</div>', unsafe_allow_html=True)
    renderizar_6_kpis(df_h2)

elif vista == "Comparativa":
    st.markdown('<div class="section-header">Comparativa Directa Frente a Frente</div>', unsafe_allow_html=True)
    
    col_izq, col_der = st.columns(2)
    
    with col_izq:
        st.markdown(f'<h3 class="comparison-title"> {hotel_1}</h3>', unsafe_allow_html=True)
        df_A = df_interactivo[df_interactivo["hotel"] == hotel_1]
        sub1, sub2 = st.columns(2)
        sub1.markdown(f'<div class="kpi-card"><div class="kpi-label">Reservas</div><div class="kpi-value">{len(df_A):,}</div></div>', unsafe_allow_html=True)
        sub2.markdown(f'<div class="kpi-card kpi-revenue"><div class="kpi-label">Ingresos totales Esperados</div><div class="kpi-value">${df_A["total_revenue"].sum():,.0f}</div></div>', unsafe_allow_html=True)
        sub1.markdown(f'<div class="kpi-card kpi-cancel"><div class="kpi-label">Cancelaciones</div><div class="kpi-value">{df_A["is_canceled"].mean()*100:.1f}%</div></div>', unsafe_allow_html=True)
        sub2.markdown(f'<div class="kpi-card kpi-adr"><div class="kpi-label">ADR Promedio</div><div class="kpi-value">${df_A["adr"].mean():,.2f}</div></div>', unsafe_allow_html=True)
        sub_c5, sub_c6 = st.columns(2)
        sub_c5.markdown(f'<div class="kpi-card kpi-lead"><div class="kpi-label">Anticipación</div><div class="kpi-value">{df_A["lead_time"].mean():.0f} días</div></div>', unsafe_allow_html=True)
        sub_c6.markdown(f'<div class="kpi-card kpi-nights"><div class="kpi-label">Noches Prom.</div><div class="kpi-value">{(df_A["stays_in_weekend_nights"] + df_A["stays_in_week_nights"]).mean():.1f}</div></div>', unsafe_allow_html=True)
    with col_der:
        st.markdown(f'<h3 class="comparison-title"> {hotel_2}</h3>', unsafe_allow_html=True)
        df_B = df_interactivo[df_interactivo["hotel"] == hotel_2]
        sub3, sub4 = st.columns(2)
        sub3.markdown(f'<div class="kpi-card"><div class="kpi-label">Reservas</div><div class="kpi-value">{len(df_B):,}</div></div>', unsafe_allow_html=True)
        sub4.markdown(f'<div class="kpi-card kpi-revenue"><div class="kpi-label">Ingresos totales Esperados</div><div class="kpi-value">${df_B["total_revenue"].sum():,.0f}</div></div>', unsafe_allow_html=True)
        sub3.markdown(f'<div class="kpi-card kpi-cancel"><div class="kpi-label">Cancelaciones</div><div class="kpi-value">{df_B["is_canceled"].mean()*100:.1f}%</div></div>', unsafe_allow_html=True)
        sub4.markdown(f'<div class="kpi-card kpi-adr"><div class="kpi-label">ADR Promedio</div><div class="kpi-value">${df_B["adr"].mean():,.2f}</div></div>', unsafe_allow_html=True)
        sub_c7, sub_c8 = st.columns(2)
        sub_c7.markdown(f'<div class="kpi-card kpi-lead"><div class="kpi-label">Anticipación</div><div class="kpi-value">{df_B["lead_time"].mean():.0f} días</div></div>', unsafe_allow_html=True)
        sub_c8.markdown(f'<div class="kpi-card kpi-nights"><div class="kpi-label">Noches Prom.</div><div class="kpi-value">{(df_B["stays_in_weekend_nights"] + df_B["stays_in_week_nights"]).mean():.1f}</div></div>', unsafe_allow_html=True)

# Nuevo 
st.markdown("""
<div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.05rem; color: #334155; margin-bottom: 20px; line-height: 1.6; border-left: 4px solid #1E3A8A; padding-left: 15px;">
    <strong>Del volumen al valor:</strong> Una alta tasa de cancelación es preocupante, pero su verdadero peso 
    se entiende al traducirla a dinero. Al proyectar la tarifa promedio diaria (ADR) por las noches de estadía planeadas, 
    podemos dimensionar el capital exacto que la operación dejó de percibir.
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-header">¿Cuanto se dejo de percibir por el % de cancelaciones? </div>', unsafe_allow_html=True)

components.html(
    revenue_gap_chart(df_interactivo),
    height=160 + len(df_interactivo["hotel"].unique()) * 90,
    scrolling=False,
)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown('<div class="section-header">¿Quienes son los que mas cancelan?</div>', unsafe_allow_html=True)
# Grafica 1

grafico_df_canceled_persona = (
    df_interactivo.groupby(["hotel", "tipo_visitante"])["is_canceled"]
    .sum()
    .reset_index()
)

grafico_df_canceled_persona["porcentaje"] = (
    grafico_df_canceled_persona.groupby("hotel")["is_canceled"]
    .transform(lambda x: x / x.sum() * 100)
)

colores_visita = {
    "Local": "#1E3A8A",        
    "Extranjero": "#64748B"     
}

fig_canceled_persona = px.bar(
    grafico_df_canceled_persona,
    x="hotel",
    y="is_canceled",
    color="tipo_visitante",
    barmode="group",
    text ="porcentaje" ,  
    color_discrete_map=colores_visita,
    labels={
        "hotel": "Tipo de Hotel",
        "is_canceled": "Total Cancelaciones",
        "tipo_visitante": "Tipo Visitante"
    },
)

fig_canceled_persona.update_layout(
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    
    font=dict(
        family="'Plus Jakarta Sans', sans-serif",
        size=13,
        color="#000000"
    ),
    
    title={
        'text': "Cancelaciones por Hotel y Tipo de Visitante",
        'x': 0.5,
        'xanchor': 'center',
        'font': dict(
            family="'Playfair Display', serif",
            size=22,
            color="#1E3A8A" # Azul Imperial
        )
    },
    
    legend=dict(
        title_font_family="'Plus Jakarta Sans', sans-serif",
        font_size=12,
        bgcolor="rgba(255,255,255,0)" 
    ),
    
    # Márgenes internos óptimos
    margin=dict(t=70, b=50, l=60, r=20),
    bargap=0.25,  
    bargroupgap=0.05 
)

fig_canceled_persona.update_yaxes(
    showgrid=True,
    gridcolor="#E2E8F0", 
    zeroline=True,
    zerolinecolor="#E2E8F0",
    tickformat=",",
    tickfont=dict(color="#475569", size=11),      
    title=dict(font=dict(color="#000000", size=13))
)
fig_canceled_persona.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="inside",              
    insidetextanchor="middle",          
    textfont=dict(
        family="'Plus Jakarta Sans', sans-serif", 
        size=13, 
        color="#FFFFFF"                 
    )
)
fig_canceled_persona.update_xaxes(
    showgrid=False,
    tickfont=dict(color="#475569", size=12),      
    title=dict(font=dict(color="#000000", size=13))
)

# Grafico 2

grafico_df_canceled_valor = (
    df_interactivo.groupby(["hotel", "tipo_visitante"])["dinero_perdido"]
    .sum()
    .reset_index()
)

grafico_df_canceled_valor["porcentaje"] = (
    grafico_df_canceled_valor.groupby("hotel")["dinero_perdido"]
    .transform(lambda x: x / x.sum() * 100)
)


fig_canceled_valor = px.bar(
    grafico_df_canceled_valor,
    x="hotel",
    y="dinero_perdido",         
    color="tipo_visitante",
    barmode="stack",
    text="porcentaje",                   
    color_discrete_map=colores_visita,
    labels={
        "hotel": "Tipo de Hotel",
        "dinero_perdido": "Proporción de Ingresos No Percibidos", 
        "tipo_visitante": "Tipo Visitante"
    },
)

fig_canceled_valor.update_layout(
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    barnorm="percent", 
    
    font=dict(
        family="'Plus Jakarta Sans', sans-serif",
        size=13,
        color="#000000"
    ),
    
    title={
        'text': "Distribución de Ingresos No Percibidos por Tipo de Visitante", 
        'x': 0.5,
        'xanchor': 'center',
        'font': dict(
            family="'Playfair Display', serif",
            size=22,
            color="#1E3A8A" 
        )
    },
    
    legend=dict(
        font=dict(color="#000000", size=12),
        title=dict(font=dict(color="#1E3A8A")),
        bgcolor="rgba(255,255,255,0)" 
    ),
    
    margin=dict(t=70, b=50, l=70, r=20),
    bargap=0.40,  # Hacemos las barras un poco más estilizadas (más angostas)
)


fig_canceled_valor.update_yaxes(
    showgrid=True,
    gridcolor="#E2E8F0", 
    zeroline=True,
    zerolinecolor="#E2E8F0",
    tickformat=".0f",                         
    ticksuffix="%",
    range=[0, 100],                           
    tickfont=dict(color="#475569", size=11),      
    title=dict(text="% del Total No Percibido", font=dict(color="#000000", size=13)) 
)

fig_canceled_valor.update_xaxes(
    showgrid=False,
    tickfont=dict(color="#475569", size=12),      
    title=dict(font=dict(color="#000000", size=13))
)

fig_canceled_valor.update_traces(
    texttemplate="%{text:.1f}%",
    textposition="inside",              
    insidetextanchor="middle",          
    textfont=dict(
        family="'Plus Jakarta Sans', sans-serif", 
        size=13, 
        color="#FFFFFF"                 
    )
)


col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(
        fig_canceled_persona,
        use_container_width=True,
        theme=None
    )

with col2:
    st.plotly_chart(
        fig_canceled_valor,
        use_container_width=True,
        theme=None
    )

st.markdown("""
<div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.05rem; color: #334155; margin-bottom: 20px; line-height: 1.6; border-left: 4px solid #1E3A8A; padding-left: 15px;">
    <strong>Identificando la raíz del problema:</strong> Es de vital identificar quiénes estan causando la perdida de dinero.
        </em> Analizar el mercado de origen y el tipo de paquete turístico 
    adquirido nos permite focalizar campañas de marketing y endurecer políticas de cancelación donde es estrictamente necesario.
</div>
""", unsafe_allow_html=True)

# Grafico Mercado, cancelacion
grafico_df_canceled_Mercado = (
    df_interactivo.groupby(["hotel", "market_segment"])["dinero_perdido"]
    .sum()
    .reset_index()
)

grafico_df_canceled_Mercado["porcentaje"] = (
    grafico_df_canceled_Mercado.groupby("hotel")["dinero_perdido"]
    .transform(lambda x: x / x.sum() * 100)
)

colores_mercado = {
    "Online TA": "#1E3A8A",       # Azul Imperial Principal
    "Offline TA/TO": "#3B82F6",   # Azul Claro Corporativo
    "Groups": "#64748B",          # Gris Premium
    "Direct": "#475569",          # Slate Oscuro
    "Corporate": "#94A3B8",       # Slate Claro
    "Complementary": "#CBD5E1",   # Gris Suave
    "Aviation": "#334155"         # Azul Noche Oscuro
}

# Creamos el Treemap definiendo la jerarquía en 'path'
fig_canceled_Mercado = px.treemap(
    grafico_df_canceled_Mercado,
    path=["hotel", "market_segment"],   # 🌟 Jerarquía: Hotel -> Segmento
    values="dinero_perdido",            # El tamaño del recuadro depende del dinero perdido
    color="market_segment",
    color_discrete_map=colores_mercado,
    custom_data=["porcentaje"],         # Guardamos el % para la etiqueta
    labels={
        "hotel": "Tipo de Hotel",
        "dinero_perdido": "Ingresos No Percibidos", 
        "market_segment": "Segmento del mercado"
    },
)

fig_canceled_Mercado.update_layout(
    paper_bgcolor="#FFFFFF",
    font=dict(
        family="'Plus Jakarta Sans', sans-serif",
        size=13,
        color="#000000"
    ),
    title={
        'text': "Distribución de Ingresos No Percibidos por Segmento de Mercado", 
        'x': 0.5,
        'xanchor': 'center',
        'font': dict(
            family="'Playfair Display', serif",
            size=20,
            color="#1E3A8A" 
        )
    },
    margin=dict(t=70, b=20, l=20, r=20),
)

fig_canceled_Mercado.update_traces(
    texttemplate="<b>%{label}</b><br>%{customdata[0]:.1f}%",
    textposition="middle center",  # 🌟 CAMBIADO AQUÍ
    textfont=dict(
        family="'Plus Jakarta Sans', sans-serif", 
        size=13
    )
)


# ─── TREEMAP 2: TIPO DE RESERVA ──────────────────────────────────────────────
grafico_df_canceled_tipo = (
    df_interactivo.groupby(["hotel", "tipo"])["dinero_perdido"]
    .sum()
    .reset_index()
)

grafico_df_canceled_tipo["porcentaje"] = (
    grafico_df_canceled_tipo.groupby("hotel")["dinero_perdido"]
    .transform(lambda x: x / x.sum() * 100)
)

colores_tipo = {
    "work+rest": "#1E3A8A",       
    "rest": "#3B82F6",   
    "work": "#64748B",          
    "package": "#475569",          
    "weekend": "#94A3B8"       
}

fig_canceled_tipo = px.treemap(
    grafico_df_canceled_tipo,
    path=["hotel", "tipo"],             # 🌟 Jerarquía: Hotel -> Tipo
    values="dinero_perdido",
    color="tipo",
    color_discrete_map=colores_tipo,
    custom_data=["porcentaje"],
    labels={
        "hotel": "Tipo de Hotel",
        "dinero_perdido": "Ingresos No Percibidos", 
        "tipo": "Tipo de Reserva"
    },
)

fig_canceled_tipo.update_layout(
    paper_bgcolor="#FFFFFF",
    font=dict(
        family="'Plus Jakarta Sans', sans-serif",
        size=13,
        color="#000000"
    ),
    title={
        'text': "Distribución de Ingresos No Percibidos por Tipo de Reserva", 
        'x': 0.5,
        'xanchor': 'center',
        'font': dict(
            family="'Playfair Display', serif",
            size=20,
            color="#1E3A8A" 
        )
    },
    margin=dict(t=70, b=20, l=20, r=20),
)

fig_canceled_tipo.update_traces(
    texttemplate="<b>%{label}</b><br>%{customdata[0]:.1f}%",
    textposition="middle center",  # 🌟 CAMBIADO AQUÍ
    textfont=dict(
        family="'Plus Jakarta Sans', sans-serif", 
        size=13
    )
)


# ─── RENDERIZADO EN COLUMNAS FRENTE A FRENTE ─────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(
        fig_canceled_Mercado,
        use_container_width=True,
        theme=None
    )

with col2:
    st.plotly_chart(
        fig_canceled_tipo,
        use_container_width=True,
        theme=None
    )

# 3er Grafico 
st.markdown("""
<div style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.05rem; color: #334155; margin-bottom: 20px; line-height: 1.6; border-left: 4px solid #1E3A8A; padding-left: 15px;">
    <strong>Comportamiento a través del tiempo:</strong> Finalmente, para aprender del pasado, debemos mirar el comportamiento histórico. 
    Suavizar los datos en promedios mensuales nos revela los picos de estrés operativo.para ajustar las estrategias de manera inteligente según la temporada.
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-header">Evolución Temporal Mensual por Tipo de Hotel</div>', unsafe_allow_html=True)

# 1. Aseguramos que la columna 'dia' sea reconocida como fecha por Pandas
df_interactivo["dia_datetime"] = pd.to_datetime(df_interactivo["dia"], format="%d/%m/%Y", errors="coerce")

# 2. Paso A: Agrupamos por día exacto para obtener los totales absolutos por día
df_diario = (
    df_interactivo.groupby(["dia_datetime", "hotel"])
    .agg(
        Total_Reservas=("is_canceled", "count"),
        Cancelaciones=("is_canceled", "sum")
    )
    .reset_index()
)

# 3. Paso B: Creamos la columna truncada al primer día de cada mes (Año-Mes)
df_diario["mes_año"] = df_diario["dia_datetime"].dt.to_period("M").dt.to_timestamp()

# 4. Paso C: Agrupamos mensualmente sacando el PROMEDIO de los comportamientos diarios
grafico_df_mensual = (
    df_diario.groupby(["mes_año", "hotel"])
    .agg(
        Promedio_Reservas=("Total_Reservas", "mean"),
        Promedio_Cancelaciones=("Cancelaciones", "mean")
    )
    .reset_index()
    .sort_values("mes_año")
)

# Mapeo de tus colores ejecutivos
colores_hotel = {
    hotel_1: "#1E3A8A",  # Azul Imperial
    hotel_2: "#64748B"   # Gris Premium
}

# ─── GRÁFICO 1: PROMEDIO MENSUAL DE RESERVAS (LÍNEAS) ──────────────────────
fig_reservas_tiempo = px.line(
    grafico_df_mensual,
    x="mes_año",
    y="Promedio_Reservas",
    color="hotel",
    color_discrete_map=colores_hotel,
    labels={"mes_año": "Fecha", "Promedio_Reservas": "Promedio Diario", "hotel": "Hotel"}
)

fig_reservas_tiempo.update_layout(
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font=dict(family="'Plus Jakarta Sans', sans-serif", size=13, color="#000000"),
    title={
        'text': "Promedio Diario de Reservas por Mes", 
        'x': 0.5,
        'xanchor': 'center',
        'font': dict(family="'Playfair Display', serif", size=18, color="#1E3A8A") 
    },
    legend=dict(font=dict(size=11), bgcolor="rgba(255,255,255,0)"),
    margin=dict(t=70, b=50, l=60, r=20),
)


fig_reservas_tiempo.update_traces(line=dict(width=3), mode="lines+markers", marker=dict(size=6))

fig_reservas_tiempo.update_yaxes(
    showgrid=True, gridcolor="#E2E8F0", zeroline=True, zerolinecolor="#E2E8F0",
    tickformat=".1f", # Muestra un decimal dado que es un promedio flotante
    tickfont=dict(color="#475569", size=11),
    title=dict(text="Reservas Promedio / Día", font=dict(color="#000000", size=13))
)

fig_reservas_tiempo.update_xaxes(
    showgrid=False, tickfont=dict(color="#475569", size=12),
    dtick="M2",         # Coloca una etiqueta en el eje X cada 2 meses para mantener la limpieza
    tickformat="%b %Y", # Formato corto en español (ej: Ene 2016)
    title=dict(font=dict(color="#000000", size=13))
)


# ─── GRÁFICO 2: PROMEDIO MENSUAL DE CANCELACIONES (LÍNEAS) ─────────────────
fig_cancel_tiempo = px.line(
    grafico_df_mensual,
    x="mes_año",
    y="Promedio_Cancelaciones",
    color="hotel",
    color_discrete_map=colores_hotel,
    labels={"mes_año": "Fecha", "Promedio_Cancelaciones": "Promedio Diario", "hotel": "Hotel"}
)

fig_cancel_tiempo.update_layout(
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    font=dict(family="'Plus Jakarta Sans', sans-serif", size=13, color="#000000"),
    title={
        'text': "Promedio Diario de Cancelaciones por Mes", 
        'x': 0.5,
        'xanchor': 'center',
        'font': dict(family="'Playfair Display', serif", size=18, color="#1E3A8A") 
    },
    legend=dict(font=dict(size=11), bgcolor="rgba(255,255,255,0)"),
    margin=dict(t=70, b=50, l=60, r=20),
)

fig_cancel_tiempo.update_traces(line=dict(width=3), mode="lines+markers", marker=dict(size=6))

fig_cancel_tiempo.update_yaxes(
    showgrid=True, gridcolor="#E2E8F0", zeroline=True, zerolinecolor="#E2E8F0",
    tickformat=".1f", 
    tickfont=dict(color="#475569", size=11),
    title=dict(text="Cancelaciones Promedio / Día", font=dict(color="#000000", size=13))
)

fig_cancel_tiempo.update_xaxes(
    showgrid=False, tickfont=dict(color="#475569", size=12),
    dtick="M2",
    tickformat="%b %Y",
    title=dict(font=dict(color="#000000", size=13))
)


# ─── RENDERIZADO LADO A LADO (COLUMNAS) ──────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_reservas_tiempo, use_container_width=True, theme=None)

with col2:
    st.plotly_chart(fig_cancel_tiempo, use_container_width=True, theme=None)

# ══════════════════════════════════════════════════════════════════════════════
# FASE 3 — Componentes D3.js

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
st.markdown("""
<div style="margin-top: 60px; padding: 30px 20px; background-color: #F8FAFC; border-radius: 12px; border-top: 4px solid #1E3A8A; text-align: center; font-family: 'Plus Jakarta Sans', sans-serif;">
    <h3 style="font-family: 'Playfair Display', serif; color: #1E3A8A; font-size: 1.6rem; margin-bottom: 15px;">Conclusión</h3>
    <p style="font-size: 1.05rem; color: #475569; line-height: 1.6; max-width: 850px; margin: 0 auto;">
Al analizar los resultados, se demuestra que las cancelaciones son eventos que siguen patrones y <strong>comportamientos predecibles</strong>,
relacionados con, el segmento de mercado y la estacionalidad; al identificar estas frecuencias,
la gerencia hotelera debe buscar estrategias que cambien la fuga de capital por una oportunidad de negocio,
al implementar políticas de cancelación mas estrictas en reservas de agencias Online, y ajustar precios y sobreventas en determinados meses.
    </p>

</div>
""", unsafe_allow_html=True)