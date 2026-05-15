"""
d3_components.py
────────────────
Componentes D3.js custom para incrustar en Streamlit via st.components.v1.html()

Uso:
    from d3_components import revenue_gap_chart, radial_cancel_clock, bump_chart_seasons

Cada función recibe un DataFrame ya filtrado y devuelve HTML+D3 listo para renderizar.
"""

import json
import pandas as pd


# ── Paleta coherente con tu style.css ──────────────────────────────────────
AZUL_IMPERIAL = "#1E3A8A"
AZUL_CLARO    = "#3B82F6"
GRIS_PREMIUM  = "#64748B"
ROJO_CANCEL   = "#EF4444"
VERDE         = "#10B981"
FONT          = "Plus Jakarta Sans, sans-serif"

MONTH_ORDER = ["January","February","March","April","May","June",
               "July","August","September","October","November","December"]
MONTH_ES    = {"January":"Ene","February":"Feb","March":"Mar","April":"Abr",
               "May":"May","June":"Jun","July":"Jul","August":"Ago",
               "September":"Sep","October":"Oct","November":"Nov","December":"Dic"}


# ══════════════════════════════════════════════════════════════════════════════
# 1. REVENUE GAP — Barra animada: ingreso esperado vs dinero perdido
# ══════════════════════════════════════════════════════════════════════════════
def revenue_gap_chart(df: pd.DataFrame, height: int = 320) -> str:
    """
    Barra horizontal apilada animada (D3 transition) por hotel.
    Verde = ingreso real | Rojo = dinero perdido por cancelaciones.
    """
    hoteles = df["hotel"].unique().tolist()
    data = []
    for h in hoteles:
        sub = df[df["hotel"] == h]
        esperado = float(sub["total_revenue"].sum())
        perdido  = float(sub["dinero_perdido"].sum())
        cobrado  = esperado - perdido
        data.append({
            "hotel":    h,
            "cobrado":  cobrado,
            "perdido":  perdido,
            "esperado": esperado,
            "pct_perdido": round(perdido / esperado * 100, 1) if esperado > 0 else 0
        })

    data_json = json.dumps(data)

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: {FONT}; background: #fff; padding: 16px; }}
  .chart-title {{
    font-size: 1.05rem; font-weight: 700; color: {AZUL_IMPERIAL};
    margin-bottom: 4px; font-family: 'Playfair Display', serif;
  }}
  .chart-sub {{
    font-size: 0.78rem; color: {GRIS_PREMIUM}; margin-bottom: 20px;
  }}
  .bar-label {{ font-size: 11px; fill: #475569; }}
  .bar-value {{ font-size: 12px; font-weight: 600; }}
  .legend {{ display: flex; gap: 20px; margin-top: 14px; }}
  .legend-item {{ display: flex; align-items: center; gap: 6px; font-size: 12px; color: #334155; }}
  .legend-dot {{ width: 12px; height: 12px; border-radius: 3px; flex-shrink: 0; }}
  .tooltip {{
    position: absolute; background: #0F172A; color: #fff;
    padding: 8px 12px; border-radius: 8px; font-size: 12px;
    pointer-events: none; opacity: 0; transition: opacity 0.2s;
    line-height: 1.6;
  }}
</style>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=Playfair+Display:wght@600&display=swap" rel="stylesheet">
</head>
<body>
<div class="chart-title">Ingreso Esperado vs. Dinero No Percibido</div>
<div class="chart-sub">Cada barra = 100% del ingreso potencial. El rojo representa lo perdido por cancelaciones.</div>
<div id="chart" style="position:relative;"></div>
<div class="legend">
  <div class="legend-item"><div class="legend-dot" style="background:{VERDE};"></div>Ingreso real</div>
  <div class="legend-item"><div class="legend-dot" style="background:{ROJO_CANCEL};"></div>Dinero no percibido</div>
</div>
<div class="tooltip" id="tooltip"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<script>
const data = {data_json};
const W = document.getElementById("chart").clientWidth || 560;
const barH = 54, gap = 28, padL = 130, padR = 90;
const H = data.length * (barH + gap) + 20;

const svg = d3.select("#chart").append("svg")
  .attr("width", W).attr("height", H);

const x = d3.scaleLinear().domain([0, 1]).range([padL, W - padR]);
const tooltip = document.getElementById("tooltip");

data.forEach((d, i) => {{
  const y0 = i * (barH + gap) + 10;
  const pctCob = d.cobrado / d.esperado;
  const pctPerd = d.perdido / d.esperado;

  // Etiqueta hotel
  svg.append("text")
    .attr("x", padL - 10).attr("y", y0 + barH / 2 + 4)
    .attr("text-anchor", "end")
    .attr("font-size", 13).attr("font-weight", 600)
    .attr("fill", "{AZUL_IMPERIAL}")
    .attr("font-family", "{FONT}")
    .text(d.hotel.length > 18 ? d.hotel.substring(0,18)+"…" : d.hotel);

  // Fondo gris claro (total)
  svg.append("rect")
    .attr("x", padL).attr("y", y0)
    .attr("width", W - padL - padR).attr("height", barH)
    .attr("rx", 8).attr("fill", "#F1F5F9");

  // Barra verde (cobrado) — animada desde 0
  const rCob = svg.append("rect")
    .attr("x", padL).attr("y", y0)
    .attr("width", 0).attr("height", barH)
    .attr("rx", 8).attr("fill", "{VERDE}")
    .style("cursor", "pointer");

  rCob.transition().duration(900).ease(d3.easeCubicOut)
    .attr("width", x(pctCob) - padL);

  // Barra roja (perdido) — animada desde borde del verde
  const rPerd = svg.append("rect")
    .attr("x", x(pctCob)).attr("y", y0)
    .attr("width", 0).attr("height", barH)
    .attr("rx", 8).attr("fill", "{ROJO_CANCEL}")
    .style("cursor", "pointer");

  rPerd.transition().duration(900).delay(200).ease(d3.easeCubicOut)
    .attr("width", x(pctPerd) - padL);

  // Etiqueta % perdido (aparece después)
  const lblPerd = svg.append("text")
    .attr("x", W - padR + 8)
    .attr("y", y0 + barH / 2 + 5)
    .attr("font-size", 13).attr("font-weight", 700)
    .attr("fill", "{ROJO_CANCEL}")
    .attr("font-family", "{FONT}")
    .attr("opacity", 0)
    .text(`-${{d.pct_perdido}}%`);

  lblPerd.transition().duration(400).delay(1000).attr("opacity", 1);

  // Etiqueta dinero real dentro de la barra
  const lblCob = svg.append("text")
    .attr("x", padL + 10).attr("y", y0 + barH / 2 + 5)
    .attr("font-size", 12).attr("font-weight", 600)
    .attr("fill", "#fff").attr("font-family", "{FONT}")
    .attr("opacity", 0)
    .text(`${{d.cobrado.toLocaleString("en-US", {{maximumFractionDigits:0}})}} cobrado`);

  lblCob.transition().duration(400).delay(1000).attr("opacity", 1);

  // Tooltip hover
  [rCob, rPerd].forEach(rect => {{
    rect.on("mousemove", function(event) {{
      tooltip.style.opacity = 1;
      tooltip.style.left = (event.offsetX + 12) + "px";
      tooltip.style.top  = (event.offsetY - 10) + "px";
      tooltip.innerHTML = `
        <b>${{d.hotel}}</b><br>
        Esperado: ${{d.esperado.toLocaleString("en-US", {{maximumFractionDigits:0}})}}<br>
        Cobrado: ${{d.cobrado.toLocaleString("en-US", {{maximumFractionDigits:0}})}}<br>
        No percibido: ${{d.perdido.toLocaleString("en-US", {{maximumFractionDigits:0}})}} (${{d.pct_perdido}}%)
      `;
    }}).on("mouseleave", () => {{ tooltip.style.opacity = 0; }});
  }});
}})
</script>
</body>
</html>
"""


# ══════════════════════════════════════════════════════════════════════════════
# 2. RADIAL CANCELLATION CLOCK — Reloj circular de cancelaciones por mes
# ══════════════════════════════════════════════════════════════════════════════
def radial_cancel_clock(df: pd.DataFrame, height: int = 420) -> str:
    """
    Gráfico radial (clock) que muestra la tasa de cancelación por mes.
    Cada "pétalo" apunta a las 12 posiciones del reloj (meses).
    Color intensidad = tasa de cancelación.
    """
    df["arrival_date_month"] = pd.Categorical(
        df["arrival_date_month"], categories=MONTH_ORDER, ordered=True
    )
    cancel_mes = (
        df.groupby("arrival_date_month", observed=True)["is_canceled"]
        .mean()
        .reindex(MONTH_ORDER)
        .fillna(0)
        .reset_index()
    )
    cancel_mes.columns = ["month", "rate"]
    cancel_mes["month_es"] = cancel_mes["month"].map(MONTH_ES)
    cancel_mes["rate_pct"] = (cancel_mes["rate"] * 100).round(1)

    data_json = cancel_mes[["month_es", "rate_pct"]].to_dict(orient="records")
    data_str  = json.dumps(data_json)

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: {FONT}; background: #fff; display: flex; flex-direction: column; align-items: center; padding: 16px; }}
  .chart-title {{ font-size: 1.05rem; font-weight: 700; color: {AZUL_IMPERIAL}; font-family: 'Playfair Display', serif; margin-bottom: 4px; text-align:center; }}
  .chart-sub   {{ font-size: 0.78rem; color: {GRIS_PREMIUM}; margin-bottom: 12px; text-align:center; }}
  .tooltip {{
    position: absolute; background: #0F172A; color: #fff;
    padding: 8px 12px; border-radius: 8px; font-size: 12px;
    pointer-events: none; opacity: 0; transition: opacity 0.15s;
  }}
</style>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=Playfair+Display:wght@600&display=swap" rel="stylesheet">
</head>
<body>
<div class="chart-title">Reloj de Cancelaciones por Mes</div>
<div class="chart-sub">Intensidad del color = tasa de cancelación. Hover para ver el porcentaje exacto.</div>
<div id="chart" style="position:relative;"></div>
<div class="tooltip" id="tooltip"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<script>
const data = {data_str};
const W = 380, H = 380, cx = W/2, cy = H/2;
const innerR = 55, outerR = 145;
const maxRate = d3.max(data, d => d.rate_pct);

const svg = d3.select("#chart").append("svg").attr("width", W).attr("height", H);
const tooltip = document.getElementById("tooltip");

// Color scale: blanco a azul imperial
const colorScale = d3.scaleLinear()
  .domain([0, maxRate])
  .range(["#DBEAFE", "{AZUL_IMPERIAL}"]);

const angleSlice = (2 * Math.PI) / 12;

// Círculos de referencia
[0.25, 0.5, 0.75, 1].forEach(t => {{
  svg.append("circle")
    .attr("cx", cx).attr("cy", cy)
    .attr("r", innerR + (outerR - innerR) * t)
    .attr("fill", "none").attr("stroke", "#E2E8F0").attr("stroke-width", 1);
}});

// Líneas radiales guía (12 meses)
data.forEach((d, i) => {{
  const angle = i * angleSlice - Math.PI / 2;
  svg.append("line")
    .attr("x1", cx + innerR * Math.cos(angle))
    .attr("y1", cy + innerR * Math.sin(angle))
    .attr("x2", cx + outerR * Math.cos(angle))
    .attr("y2", cy + outerR * Math.sin(angle))
    .attr("stroke", "#E2E8F0").attr("stroke-width", 1);
}});

// Pétalos (arcos)
const arc = d3.arc()
  .innerRadius(innerR)
  .startAngle((d, i) => i * angleSlice - angleSlice / 2 - Math.PI / 2)
  .endAngle((d, i)   => i * angleSlice + angleSlice / 2 - Math.PI / 2);

const petal = svg.selectAll(".petal")
  .data(data).enter()
  .append("path")
  .attr("transform", `translate(${{cx}},${{cy}})`)
  .attr("fill", d => colorScale(d.rate_pct))
  .attr("stroke", "#fff").attr("stroke-width", 2)
  .attr("d", d3.arc()
    .innerRadius(innerR)
    .outerRadius(innerR)  // empieza en 0
    .startAngle((d, i) => i * angleSlice - angleSlice / 2 - Math.PI / 2)
    .endAngle((d, i)   => i * angleSlice + angleSlice / 2 - Math.PI / 2)
  )
  .style("cursor", "pointer");

// Animación de entrada
petal.transition().duration(900).ease(d3.easeBounceOut)
  .attr("d", (d, i) => {{
    const r = innerR + (outerR - innerR) * (d.rate_pct / maxRate);
    return d3.arc()
      .innerRadius(innerR)
      .outerRadius(r)
      .startAngle(i * angleSlice - angleSlice / 2 - Math.PI / 2)
      .endAngle(i * angleSlice + angleSlice / 2 - Math.PI / 2)();
  }});

// Hover
petal
  .on("mousemove", function(event, d) {{
    d3.select(this).attr("opacity", 0.75);
    tooltip.style.opacity = 1;
    tooltip.style.left = (event.offsetX + 14) + "px";
    tooltip.style.top  = (event.offsetY - 10) + "px";
    tooltip.innerHTML = `<b>${{d.month_es}}</b><br>Cancelación: <b>${{d.rate_pct}}%</b>`;
  }})
  .on("mouseleave", function() {{
    d3.select(this).attr("opacity", 1);
    tooltip.style.opacity = 0;
  }});

// Etiquetas de mes (afuera)
data.forEach((d, i) => {{
  const angle  = i * angleSlice - Math.PI / 2;
  const labelR = outerR + 22;
  svg.append("text")
    .attr("x", cx + labelR * Math.cos(angle))
    .attr("y", cy + labelR * Math.sin(angle) + 4)
    .attr("text-anchor", "middle")
    .attr("font-size", 11).attr("font-weight", 600)
    .attr("fill", "#334155")
    .attr("font-family", "{FONT}")
    .text(d.month_es);
}});

// Círculo centro
svg.append("circle").attr("cx", cx).attr("cy", cy).attr("r", innerR - 4)
  .attr("fill", "#F8FAFC");
svg.append("text").attr("x", cx).attr("y", cy - 6)
  .attr("text-anchor","middle").attr("font-size", 12).attr("font-weight", 700)
  .attr("fill", "{AZUL_IMPERIAL}").attr("font-family", "{FONT}")
  .text("Cancel.");
svg.append("text").attr("x", cx).attr("y", cy + 12)
  .attr("text-anchor","middle").attr("font-size", 11)
  .attr("fill", "{GRIS_PREMIUM}").attr("font-family", "{FONT}")
  .text("por mes");
</script>
</body>
</html>
"""


# ══════════════════════════════════════════════════════════════════════════════
# 3. BUMP CHART — Ranking de reservaciones por estación a través del tiempo
# ══════════════════════════════════════════════════════════════════════════════
def bump_chart_seasons(df: pd.DataFrame, height: int = 340) -> str:
    """
    Bump chart: eje X = años, eje Y = posición (ranking) de cada estación
    según total de reservaciones. Las líneas se cruzan mostrando cambios de ranking.
    """
    if "estacion" not in df.columns:
        return "<p style='color:gray;font-size:13px;'>Columna 'estacion' no encontrada.</p>"

    df["arrival_date_year"] = df["arrival_date_year"].astype(int)
    grp = (
        df.groupby(["arrival_date_year", "estacion"])
        .size().reset_index(name="reservaciones")
    )
    años     = sorted(grp["arrival_date_year"].unique().tolist())
    estaciones = sorted(grp["estacion"].unique().tolist())

    # Calcular ranking por año (1 = más reservaciones)
    grp["rank"] = grp.groupby("arrival_date_year")["reservaciones"].rank(
        ascending=False, method="min"
    ).astype(int)

    # Pivot para D3
    pivot = {}
    for _, row in grp.iterrows():
        e = row["estacion"]
        a = int(row["arrival_date_year"])
        if e not in pivot:
            pivot[e] = {}
        pivot[e][a] = {"rank": int(row["rank"]), "res": int(row["reservaciones"])}

    data_json = json.dumps({"años": años, "estaciones": estaciones, "data": pivot})

    SEASON_COLORS_JS = {
        "Invierno": "#5DADE2",
        "Primavera": "#27AE60",
        "Verano":    "#F39C12",
        "Otoño":     "#E67E22",
    }
    # Para estaciones que no estén en el mapa, asignar colores del palette
    fallback = ["#1E3A8A","#3B82F6","#64748B","#6366F1","#0EA5E9"]
    colors_map = {}
    fi = 0
    for e in estaciones:
        colors_map[e] = SEASON_COLORS_JS.get(e, fallback[fi % len(fallback)])
        fi += 1
    colors_json = json.dumps(colors_map)

    n_ranks = len(estaciones)

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: {FONT}; background: #fff; padding: 16px; }}
  .chart-title {{ font-size: 1.05rem; font-weight: 700; color: {AZUL_IMPERIAL}; font-family: 'Playfair Display', serif; margin-bottom: 4px; }}
  .chart-sub   {{ font-size: 0.78rem; color: {GRIS_PREMIUM}; margin-bottom: 12px; }}
  .tooltip {{
    position: absolute; background: #0F172A; color: #fff;
    padding: 8px 12px; border-radius: 8px; font-size: 12px;
    pointer-events: none; opacity: 0; transition: opacity 0.15s;
    line-height: 1.6;
  }}
</style>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&family=Playfair+Display:wght@600&display=swap" rel="stylesheet">
</head>
<body>
<div class="chart-title">Ranking de Temporadas por Reservaciones</div>
<div class="chart-sub">Posición 1 = temporada con más reservaciones ese año. Las líneas muestran cambios de liderazgo.</div>
<div id="chart" style="position:relative;"></div>
<div class="tooltip" id="tooltip"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<script>
const raw     = {data_json};
const colors  = {colors_json};
const años    = raw.años;
const estaciones = raw.estaciones;
const pivot   = raw.data;

const W = (document.getElementById("chart").clientWidth || 560);
const H = {height};
const padL = 110, padR = 110, padT = 30, padB = 30;
const nRanks = {n_ranks};

const svg = d3.select("#chart").append("svg").attr("width", W).attr("height", H);
const tooltip = document.getElementById("tooltip");

const x = d3.scalePoint().domain(años).range([padL, W - padR]).padding(0.4);
const y = d3.scalePoint().domain(d3.range(1, nRanks + 1)).range([padT, H - padB]).padding(0.3);

// Líneas de guía horizontales
d3.range(1, nRanks + 1).forEach(r => {{
  svg.append("line")
    .attr("x1", padL).attr("x2", W - padR)
    .attr("y1", y(r)).attr("y2", y(r))
    .attr("stroke", "#F1F5F9").attr("stroke-width", 1);
  svg.append("text")
    .attr("x", padL - 10).attr("y", y(r) + 4)
    .attr("text-anchor","end").attr("font-size", 11).attr("fill","#94A3B8")
    .attr("font-family","{FONT}")
    .text(`#${{r}}`);
}});

// Etiquetas X (años)
años.forEach(a => {{
  svg.append("text")
    .attr("x", x(a)).attr("y", H - 6)
    .attr("text-anchor","middle").attr("font-size", 12).attr("font-weight", 600)
    .attr("fill", "{AZUL_IMPERIAL}").attr("font-family","{FONT}")
    .text(a);
}});

// Por cada estación: línea + puntos + etiquetas
estaciones.forEach(est => {{
  const col = colors[est] || "#64748B";
  const puntos = años
    .filter(a => pivot[est] && pivot[est][a])
    .map(a => ({{ año: a, rank: pivot[est][a].rank, res: pivot[est][a].res }}));

  if (puntos.length < 2) return;

  // Línea curva
  const lineGen = d3.line()
    .x(d => x(d.año))
    .y(d => y(d.rank))
    .curve(d3.curveCatmullRom.alpha(0.5));

  const path = svg.append("path")
    .datum(puntos)
    .attr("fill","none")
    .attr("stroke", col)
    .attr("stroke-width", 3)
    .attr("stroke-linecap","round")
    .attr("d", lineGen);

  // Animación de trazado
  const len = path.node().getTotalLength();
  path.attr("stroke-dasharray", len + " " + len)
      .attr("stroke-dashoffset", len)
    .transition().duration(1000).ease(d3.easeLinear)
      .attr("stroke-dashoffset", 0);

  // Puntos
  svg.selectAll(`.dot-${{est.replace(/\s+/g,"_")}}`)
    .data(puntos).enter()
    .append("circle")
    .attr("cx", d => x(d.año)).attr("cy", d => y(d.rank))
    .attr("r", 0)
    .attr("fill", col).attr("stroke","#fff").attr("stroke-width", 2)
    .style("cursor","pointer")
    .transition().duration(400).delay(1000).attr("r", 9);

  // Tooltip hover (después de la animación)
  setTimeout(() => {{
    svg.selectAll(`.dot-${{est.replace(/\s+/g,"_")}}`)
      .on("mousemove", function(event, d) {{
        tooltip.style.opacity = 1;
        tooltip.style.left = (event.offsetX + 14) + "px";
        tooltip.style.top  = (event.offsetY - 10) + "px";
        tooltip.innerHTML = `<b>${{est}}</b> — ${{d.año}}<br>Posición: <b>#${{d.rank}}</b><br>Reservas: <b>${{d.res.toLocaleString()}}</b>`;
      }})
      .on("mouseleave", () => {{ tooltip.style.opacity = 0; }});
  }}, 1100);

  // Etiqueta al final (derecha)
  const ultimo = puntos[puntos.length - 1];
  svg.append("text")
    .attr("x", x(ultimo.año) + 14)
    .attr("y", y(ultimo.rank) + 4)
    .attr("font-size", 12).attr("font-weight", 600)
    .attr("fill", col).attr("font-family","{FONT}")
    .text(est);
}});
</script>
</body>
</html>
"""
