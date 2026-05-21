"""
PREFORTE · Dashboard de Marketing Organico
Entregable estatico — Periodo: 20 Feb – 19 May 2026
"""

import csv as csv_module
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from fpdf import FPDF

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PREFORTE · Marketing Feb–May 2026",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── PALETA CORPORATIVA PREFORTE ────────────────────────────────────────────────
C_GREEN  = "#00A859"   # Verde Sostenible (primario)
C_GREEN2 = "#1FE074"   # Verde Ecoforte  (acento)
C_GRAY   = "#6B7280"   # Gris Industrial
C_DARK   = "#1F2937"   # Texto principal
C_BG     = "#FFFFFF"   # Fondo blanco
C_BG2    = "#F0F4F3"   # Fondo secundario
C_BORDER = "#D1FAE5"   # Borde verde suave
C_FB     = "#1877F2"   # Facebook
C_IG     = "#E1306C"   # Instagram
C_SEQ    = [C_GREEN, C_GREEN2, "#059669", "#34D399", C_GRAY, "#9CA3AF"]

DAY_MAP = {
    "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miercoles",
    "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sabado", "Sunday": "Domingo",
}
DAY_ORDER = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]

LAYOUT = dict(
    plot_bgcolor=C_BG,
    paper_bgcolor=C_BG2,
    font=dict(color=C_DARK, family="Arial, sans-serif", size=12),
    margin=dict(t=40, b=20, l=10, r=10),
)

# ─── CSS CORPORATIVO — TEMA CLARO ────────────────────────────────────────────────
st.markdown(f"""
<style>
.stApp {{ background-color:{C_BG}; }}
[data-testid="stMetricValue"] {{ font-size:1.6rem!important; font-weight:800; color:{C_GREEN}; }}
[data-testid="stMetricLabel"] {{ font-size:.78rem; color:{C_GRAY}; font-weight:600; }}
div[data-testid="metric-container"] {{
    background:{C_BG}; border:1.5px solid {C_GREEN};
    border-top:4px solid {C_GREEN}; border-radius:8px;
    padding:14px 18px 10px; box-shadow:0 2px 8px rgba(0,168,89,.10);
}}
h1 {{ color:{C_DARK}; }}
h2, h3 {{ color:{C_GREEN}; }}
hr {{ border-color:{C_BORDER}; margin:1rem 0; }}
div[data-testid="stInfo"]    {{ border-left:4px solid {C_GREEN}; background:#f0fdf4; }}
div[data-testid="stSuccess"] {{ border-left:4px solid {C_GREEN2}; background:#f0fdf4; }}
div[data-testid="stWarning"] {{ border-left:4px solid #F59E0B; }}
section[data-testid="stSidebar"] > div {{
    background-color:{C_BG2}; border-right:2px solid {C_GREEN};
}}
</style>
""", unsafe_allow_html=True)

# ─── RUTAS ──────────────────────────────────────────────────────────────────────
ROOT     = Path(__file__).parent.parent
FB_FILE  = ROOT / "Feb-20-2026_May-19-2026_facebook.csv"
IG_FILE  = ROOT / "Feb-20-2026_May-19-2026_instagram.csv"
AUD_FILE = ROOT / "estadistica_de_la_audiencia.csv"


# ─── CLASIFICACION TEMATICA ──────────────────────────────────────────────────────
def categorize_theme(desc: str) -> str:
    d = str(desc).lower()
    if any(k in d for k in ["vigueta", "hormigon", "hormigón", "ultraforte", "pretensado",
                             "losa", "poste", "mezcla", "cotiz", "carboncure", "ecoforte",
                             "resistencia", "especificac", "m³"]):
        return "Producto / Tecnico"
    if any(k in d for k in ["tenis", "deporte", "atleta", "raqueta", "cosat", "ines", "inés",
                             "impulsa el deporte"]):
        return "Patrocinio Deportivo"
    if any(k in d for k in ["sostenib", "co2", "co₂", "reciclaje", "planeta",
                             "medioambiente", "carbono"]):
        return "Sostenibilidad"
    if any(k in d for k in ["aniversario", "fundaci", "felicidades", "celebramos",
                             "conmemor", "mujer", "trabajador", "madre", "padre",
                             "tierra", "8 de marzo", "26 de"]):
        return "Efemerides / Institucional"
    if any(k in d for k in ["obra", "proyecto", "edificio", "estructura",
                             "construye", "ingeniero", "arquitecto"]):
        return "Casos de Obra"
    return "Institucional / Branding"


# ─── LOADERS ────────────────────────────────────────────────────────────────────
@st.cache_data
def load_facebook() -> pd.DataFrame:
    df = pd.read_csv(FB_FILE, encoding="utf-8")
    df["Hora de publicacion"] = pd.to_datetime(
        df["Hora de publicación"], format="%m/%d/%Y %H:%M"
    )
    df["Dia semana"] = df["Hora de publicacion"].dt.day_name().map(DAY_MAP)
    df["Hora"]       = df["Hora de publicacion"].dt.hour
    df["Clics en el enlace"] = pd.to_numeric(
        df["Clics en el enlace"], errors="coerce"
    ).fillna(0)
    df["ER (%)"]  = (
        (df["Reacciones"] + df["Comentarios"] + df["Veces que se compartió"])
        / df["Alcance"] * 100
    ).round(2)
    df["CTR (%)"] = (df["Clics en el enlace"] / df["Alcance"] * 100).round(2)
    df["Tipo"] = (
        df["Tipo de publicación"]
        .str.replace("Fotos",  "Foto",  regex=False)
        .str.replace("Videos", "Video", regex=False)
    )
    df["Tematica"] = df["Descripción"].apply(categorize_theme)
    return df


@st.cache_data
def load_instagram() -> pd.DataFrame:
    df = pd.read_csv(IG_FILE, encoding="utf-8")
    df["Hora de publicacion"] = pd.to_datetime(
        df["Hora de publicación"], format="%m/%d/%Y %H:%M"
    )
    df["Dia semana"] = df["Hora de publicacion"].dt.day_name().map(DAY_MAP)
    df["Hora"]       = df["Hora de publicacion"].dt.hour
    df["ER (%)"] = (
        (df["Me gusta"] + df["Comentarios"] + df["Veces que se compartió"])
        / df["Alcance"] * 100
    ).round(2)
    df["Tipo"] = (
        df["Tipo de publicación"]
        .str.replace("Imagen de Instagram",    "Imagen",   regex=False)
        .str.replace("Reel de Instagram",      "Reel",     regex=False)
        .str.replace("Secuencia de Instagram", "Carrusel", regex=False)
    )
    df["Tematica"] = df["Descripción"].apply(categorize_theme)
    return df


@st.cache_data
def load_audiencia() -> dict:
    with open(AUD_FILE, encoding="utf-16") as f:
        lines = [ln.rstrip("\n").rstrip("\r") for ln in f.readlines()]
    lines = [ln for ln in lines if ln.strip() and ln.strip() != "sep=,"]

    TITLES = {"Principales ciudades", "Edad y sexo", "Principales países"}
    sections: dict = {}
    current: str | None = None
    buf: list = []
    for line in lines:
        key = line.strip().strip('"')
        if key in TITLES:
            if current and buf:
                sections[current] = buf
            current, buf = key, []
        else:
            buf.append(line)
    if current and buf:
        sections[current] = buf

    result: dict = {}
    for sec, dkey, col in [
        ("Principales ciudades", "ciudades", "Ciudad"),
        ("Principales países",  "paises",   "Pais"),
    ]:
        if sec in sections:
            rows = list(csv_module.reader(sections[sec]))
            result[dkey] = pd.DataFrame({
                col: rows[0], "Porcentaje": [float(v) for v in rows[1]]
            })
    if "Edad y sexo" in sections:
        rows   = list(csv_module.reader(sections["Edad y sexo"]))
        df_age = pd.DataFrame(rows[1:], columns=["Edad", "Hombres", "Mujeres"])
        df_age["Hombres"] = pd.to_numeric(df_age["Hombres"])
        df_age["Mujeres"] = pd.to_numeric(df_age["Mujeres"])
        result["edad_sexo"] = df_age
    return result


# ─── AUTENTICACIÓN ──────────────────────────────────────────────────────────────
_PASSWORD = "marketingpreforte"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    # Ocultar sidebar mientras no se autentique
    st.markdown(
        "<style>section[data-testid='stSidebar']{display:none!important;}</style>",
        unsafe_allow_html=True,
    )

    # ── Pantalla de login centrada ────────────────────────────────────────────
    st.markdown("<br><br>", unsafe_allow_html=True)

    _, center, _ = st.columns([1, 1.6, 1])
    with center:
        # Logo y título
        st.markdown(f"""
        <div style="text-align:center;padding:32px 36px 28px;
                    background:#fff;border:1.5px solid {C_GREEN};
                    border-top:5px solid {C_GREEN};border-radius:12px;
                    box-shadow:0 4px 20px rgba(0,168,89,.12);">
            <div style="font-size:2.8rem;">🏗️</div>
            <div style="color:{C_GREEN};font-weight:800;font-size:1.5rem;
                        letter-spacing:1px;margin:6px 0 2px;">PREFORTE</div>
            <div style="color:{C_GRAY};font-size:.82rem;margin-bottom:20px;">
                Dashboard de Marketing Organico · Feb–May 2026
            </div>
            <div style="color:{C_DARK};font-size:.9rem;margin-bottom:4px;
                        font-weight:600;">Acceso restringido</div>
            <div style="color:{C_GRAY};font-size:.78rem;">
                Ingresa la contraseña para ver el reporte
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        pwd = st.text_input(
            "Contraseña",
            type="password",
            placeholder="••••••••••••••••",
            label_visibility="collapsed",
        )
        login = st.button(
            "Ingresar al Dashboard",
            use_container_width=True,
            type="primary",
        )

        if login:
            if pwd == _PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            elif pwd == "":
                st.warning("Por favor ingresa la contraseña.")
            else:
                st.error("Contraseña incorrecta. Verifica e intenta de nuevo.")

        st.markdown(f"""
        <div style="text-align:center;margin-top:20px;color:{C_GRAY};font-size:.72rem;">
            🔒 Información confidencial · PREFORTE Pretensados y Hormigones S.A.
        </div>
        """, unsafe_allow_html=True)

    st.stop()   # Bloquea todo el resto del dashboard si no está autenticado


# ─── CARGA ──────────────────────────────────────────────────────────────────────
df_fb = load_facebook()
df_ig = load_instagram()
aud   = load_audiencia()

# ─── METRICAS PRE-CALCULADAS ─────────────────────────────────────────────────────
reach_fb   = int(df_fb["Alcance"].sum())
reach_ig   = int(df_ig["Alcance"].sum())
avg_r_fb   = df_fb["Alcance"].mean()
avg_r_ig   = df_ig["Alcance"].mean()
avg_er_fb  = df_fb["ER (%)"].mean()
avg_er_ig  = df_ig["ER (%)"].mean()
clics_fb   = int(df_fb["Clics en el enlace"].sum())
ctr_fb     = df_fb.loc[df_fb["Clics en el enlace"] > 0, "CTR (%)"].mean()

er_type_fb  = df_fb.groupby("Tipo")["ER (%)"].mean()
er_type_ig  = df_ig.groupby("Tipo")["ER (%)"].mean()
best_tp_fb  = er_type_fb.idxmax()
best_er_t_fb = er_type_fb.max()
best_tp_ig  = er_type_ig.idxmax()
best_er_t_ig = er_type_ig.max()

er_day_fb  = df_fb.groupby("Dia semana")["ER (%)"].mean()
er_day_ig  = df_ig.groupby("Dia semana")["ER (%)"].mean()
best_day   = er_day_fb.idxmax()
best_day_v = er_day_fb.max()

sc_pct   = float(aud["ciudades"].loc[aud["ciudades"]["Ciudad"].str.startswith("Santa Cruz"), "Porcentaje"].values[0])
lp_pct   = float(aud["ciudades"].loc[aud["ciudades"]["Ciudad"].str.startswith("La Paz"),     "Porcentaje"].values[0])
cbba_pct = float(aud["ciudades"].loc[aud["ciudades"]["Ciudad"].str.startswith("Cochabamba"), "Porcentaje"].values[0])
h2534    = float(aud["edad_sexo"].loc[aud["edad_sexo"]["Edad"] == "25-34", "Hombres"].values[0])
h3544    = float(aud["edad_sexo"].loc[aud["edad_sexo"]["Edad"] == "35-44", "Hombres"].values[0])
dm_pct   = h2534 + h3544

saves_ig = int(df_ig["Veces que se guardó"].sum())
top1_fb  = df_fb.nlargest(1, "ER (%)").iloc[0]


# ─── GENERADOR DE PDF (fpdf2) ────────────────────────────────────────────────────
def _t(s: str) -> str:
    """Sanitize text for fpdf2 core fonts (Latin-1 safe)."""
    return s.encode("latin-1", errors="replace").decode("latin-1")


def build_pdf() -> bytes:
    GREEN_RGB = (0, 168, 89)
    DARK_RGB  = (31, 41, 55)
    GRAY_RGB  = (107, 114, 128)
    WHITE_RGB = (255, 255, 255)
    LGRAY_RGB = (240, 244, 243)
    LGREEN_RGB = (240, 253, 244)
    LPINK_RGB  = (255, 240, 244)

    class PDF(FPDF):
        def header(self):
            self.set_fill_color(*GREEN_RGB)
            self.rect(0, 0, 210, 20, "F")
            self.set_font("Helvetica", "B", 13)
            self.set_text_color(*WHITE_RGB)
            self.set_xy(12, 4)
            self.cell(120, 7, _t("PREFORTE · Pretensados y Hormigones S.A."), ln=0)
            self.set_font("Helvetica", "", 8)
            self.set_xy(140, 5)
            self.cell(60, 5, _t("Marketing Organico | Feb-May 2026"), ln=0, align="R")
            self.set_xy(140, 11)
            self.cell(60, 5, _t("$0 USD — 100% organico"), ln=0, align="R")

        def footer(self):
            self.set_y(-12)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(*GRAY_RGB)
            self.cell(0, 5,
                _t(f"Pagina {self.page_no()}  |  PREFORTE Marketing Intelligence  |  Mayo 2026"),
                align="C",
            )

    pdf = PDF()
    pdf.set_margins(14, 26, 14)
    pdf.set_auto_page_break(auto=True, margin=16)

    W = 182  # ancho util (210 - 14*2)

    def section_title(title: str):
        pdf.ln(4)
        pdf.set_fill_color(*LGRAY_RGB)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(*GREEN_RGB)
        pdf.cell(W, 8, _t(title), fill=True, ln=1)
        pdf.set_text_color(*DARK_RGB)
        pdf.ln(2)

    def body(text: str, size: int = 10):
        pdf.set_font("Helvetica", "", size)
        pdf.set_text_color(*DARK_RGB)
        pdf.multi_cell(W, 5.5, _t(text))
        pdf.ln(1)

    def table_header(cols: list, widths: list):
        pdf.set_fill_color(*GREEN_RGB)
        pdf.set_text_color(*WHITE_RGB)
        pdf.set_font("Helvetica", "B", 10)
        for col, w in zip(cols, widths):
            pdf.cell(w, 7, _t(col), border=1, align="C", fill=True)
        pdf.ln()

    def table_row(cells: list, widths: list, fills=None):
        pdf.set_text_color(*DARK_RGB)
        pdf.set_font("Helvetica", "", 10)
        fills = fills or [False] * len(cells)
        for val, w, fill_rgb in zip(cells, widths, fills):
            if fill_rgb:
                pdf.set_fill_color(*fill_rgb)
            pdf.cell(w, 6.5, _t(str(val)), border=1, align="C", fill=bool(fill_rgb))
        pdf.ln()

    # ── PORTADA ──────────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.set_fill_color(*GREEN_RGB)
    pdf.rect(0, 0, 210, 60, "F")
    pdf.set_font("Helvetica", "B", 28)
    pdf.set_text_color(*WHITE_RGB)
    pdf.set_xy(0, 14)
    pdf.cell(210, 14, "PREFORTE", align="C", ln=1)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(210, 7, _t("Pretensados y Hormigones S.A."), align="C", ln=1)

    pdf.set_y(72)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(*GREEN_RGB)
    pdf.cell(W, 12, _t("REPORTE EJECUTIVO"), align="C", ln=1)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(W, 9, _t("Marketing Organico Digital"), align="C", ln=1)

    pdf.ln(6)
    pdf.set_fill_color(*LGRAY_RGB)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(*DARK_RGB)
    for line in [
        "Periodo analizado:   20 Febrero – 19 Mayo 2026",
        "Canales con datos:   Facebook (24 posts)  +  Instagram (24 posts)",
        "Canales auditados:   LinkedIn  ·  TikTok  ·  preforte.com.bo",
        "Inversion publicitaria:   $0 USD — analisis 100% organico",
        "Generado:   20 Mayo 2026",
    ]:
        pdf.cell(W, 8, _t(line), fill=True, ln=1)
        pdf.ln(1)

    # ── KPIs FB vs IG ────────────────────────────────────────────────────────────
    pdf.add_page()
    section_title("1.  INDICADORES CLAVE DE RENDIMIENTO — Facebook vs Instagram")

    body(
        f"PREFORTE genero un alcance organico acumulado de {reach_fb+reach_ig:,} personas "
        f"en el periodo (Facebook: {reach_fb:,} + Instagram: {reach_ig:,}) sin inversion en pauta. "
        f"Facebook supera a Instagram en alcance por post en {avg_r_fb/avg_r_ig:.1f}x, "
        f"posicionandose como el canal de difusion masiva. Instagram registra mayor engagement "
        f"relativo con {avg_er_ig:.2f}% de ER promedio vs {avg_er_fb:.2f}% en Facebook."
    )

    cols_k   = ["Metrica", "Facebook", "Instagram"]
    widths_k = [90, 46, 46]
    table_header(cols_k, widths_k)

    rows_kpi = [
        ("Posts analizados",          "24",                       "24"),
        ("Alcance total acumulado",   f"{reach_fb:,} personas",   f"{reach_ig:,} personas"),
        ("Alcance promedio / post",   f"{avg_r_fb:,.0f}",         f"{avg_r_ig:,.0f}"),
        ("Engagement Rate promedio",  f"{avg_er_fb:.2f} %",       f"{avg_er_ig:.2f} %"),
        ("Formato con mayor ER",      f"{best_tp_fb} ({best_er_t_fb:.1f}%)", f"{best_tp_ig} ({best_er_t_ig:.1f}%)"),
        ("Mejor dia de la semana",    best_day,                   er_day_ig.idxmax()),
        ("Clics en enlace (total)",   f"{clics_fb:,}",            "N/D"),
        ("CTR organico",              f"{ctr_fb:.2f} %",          "N/D"),
    ]
    for i, (m, fb, ig) in enumerate(rows_kpi):
        fill_bg = LGRAY_RGB if i % 2 == 0 else None
        table_row(
            [m, fb, ig],
            widths_k,
            fills=[fill_bg, LGREEN_RGB, LPINK_RGB],
        )

    pdf.ln(4)
    body(
        f"El post de mayor rendimiento individual en Facebook alcanzo un ER de "
        f"{top1_fb['ER (%)']:.2f}% con {int(top1_fb['Alcance']):,} personas de alcance. "
        f"Instagram registro {saves_ig} guardados totales, indicando que el contenido tecnico "
        f"visual es utilizado como referencia por ingenieros y constructores."
    )

    # ── AUDIENCIA ────────────────────────────────────────────────────────────────
    pdf.add_page()
    section_title("2.  PERFIL DE AUDIENCIA — Analisis Geografico y Demografico")

    body(
        f"El {dm_pct:.1f}% de la audiencia son hombres de 25-44 anos (25-34: {h2534}% / "
        f"35-44: {h3544}%), perfil que corresponde exactamente a jefes de obra, ingenieros "
        f"residentes y directores de proyecto en Bolivia. La audiencia es 92.4% boliviana, "
        f"con potencial de expansion en Chile (1.5%) y Paraguay (1.1%)."
    )

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*GREEN_RGB)
    pdf.cell(W, 7, _t("Principales Ciudades (% de audiencia)"), ln=1)
    cols_c   = ["Ciudad", "% Audiencia", "Observacion estrategica"]
    widths_c = [72, 28, 82]
    table_header(cols_c, widths_c)
    obs = {
        "Santa Cruz": "Base operativa — mercado primario",
        "La Paz":     "Mercado secundario de alto potencial",
        "Cochabamba": "Mercado secundario en expansion",
    }
    for i, row in aud["ciudades"].iterrows():
        city   = row["Ciudad"].replace(", Bolivia", "").replace(", Chile", " (Chile)")
        short  = city.split(",")[0]
        remark = obs.get(short, "Mercado de seguimiento")
        fill   = LGRAY_RGB if i % 2 == 0 else None
        table_row(
            [city, f"{row['Porcentaje']}%", remark],
            widths_c,
            fills=[fill, fill, fill],
        )

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*GREEN_RGB)
    pdf.cell(W, 7, _t("Distribucion por Edad y Sexo (% de audiencia total)"), ln=1)
    cols_a   = ["Rango Etario", "Hombres (%)", "Mujeres (%)", "Total (%)"]
    widths_a = [50, 44, 44, 44]
    table_header(cols_a, widths_a)
    for i, row in aud["edad_sexo"].iterrows():
        total = round(float(row["Hombres"]) + float(row["Mujeres"]), 1)
        fill  = LGRAY_RGB if i % 2 == 0 else None
        table_row(
            [row["Edad"], f"{row['Hombres']}%", f"{row['Mujeres']}%", f"{total}%"],
            widths_a,
            fills=[fill, LGREEN_RGB, LPINK_RGB, fill],
        )

    # ── RECOMENDACIONES ──────────────────────────────────────────────────────────
    pdf.add_page()
    section_title("3.  RECOMENDACIONES ESTRATEGICAS — Sector Construccion Bolivia")

    body(
        "Las siguientes recomendaciones se derivan exclusivamente de los datos organicos "
        "reales del periodo analizado y del perfil de audiencia verificado. "
        "Todas son ejecutables sin inversion publicitaria adicional."
    )

    recs = [
        (
            "REC. 1 — Serie de Videos Tecnicos B2B",
            f"Los {best_tp_fb.lower()}s en Facebook generan {best_er_t_fb:.2f}% ER "
            f"(vs promedio {avg_er_fb:.2f}%). Producir 4-6 clips de 60-90 seg mostrando: "
            f"montaje real de viguetas con datos de resistencia (kg/cm2), comparativa "
            f"Hormigon UltraForte vs convencional, testimonios de ingenieros clientes "
            f"en Santa Cruz y La Paz.",
            f"KPI objetivo: duplicar alcance promedio de {avg_r_fb:,.0f} a "
            f"{avg_r_fb*2:,.0f} personas/post en 60 dias. "
            f"Publicar cada {best_day} (dia de mayor engagement: {best_day_v:.2f}% ER).",
        ),
        (
            "REC. 2 — Activacion Regional La Paz + Cochabamba",
            f"La Paz ({lp_pct}%) y Cochabamba ({cbba_pct}%) suman {lp_pct+cbba_pct:.1f}% "
            f"de audiencia activa que no recibe contenido geo-especifico. "
            f"Crear posts con obras emblemáticas por ciudad, activar links de cotizacion "
            f"UTM por ciudad en todos los posts de producto, y producir contenido sobre "
            f"soluciones para zonas sismicas (La Paz) y expansion urbana (Cochabamba).",
            f"KPI objetivo: CTR organico regional > 2% en 45 dias. "
            f"Solicitudes de cotizacion desde web > 5/mes por ciudad.",
        ),
        (
            "REC. 3 — Parrilla Editorial B2B Semanal Fija",
            f"El perfil Hombres 25-44 ({dm_pct:.1f}% de audiencia) consume contenido "
            f"tecnico para tomar decisiones de compra. Implementar calendario semanal: "
            f"{best_day}: post tecnico (especificaciones, normas IBNORCA). "
            f"Miercoles: caso de exito con datos reales de obra. "
            f"Viernes: tip de construccion sostenible (Ecoforte, Carboncure). "
            f"En LinkedIn: 1 articulo tecnico mensual para posicionamiento como referente.",
            f"KPI objetivo: ER de {avg_er_fb:.2f}% → {best_er_t_fb:.1f}% en 60 dias. "
            f"LinkedIn: 2,376 → 3,000 seguidores en 90 dias.",
        ),
    ]

    for title, desc, kpi in recs:
        pdf.set_fill_color(*LGRAY_RGB)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*GREEN_RGB)
        pdf.cell(W, 8, _t(title), fill=True, ln=1)
        body(desc)
        pdf.set_font("Helvetica", "BI", 10)
        pdf.set_text_color(*GREEN_RGB)
        pdf.cell(W, 6, _t(kpi), ln=1)
        pdf.set_text_color(*DARK_RGB)
        pdf.ln(3)

    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(*GRAY_RGB)
    pdf.multi_cell(W, 5, _t(
        "Nota: Análisis basado unicamente en datos organicos de los archivos proporcionados. "
        "Auditoria cualitativa de LinkedIn y preforte.com.bo realizada en Mayo 2026. "
        "TikTok requiere sesion activa para extraccion de datos de perfil."
    ))

    return bytes(pdf.output())


# ─── GENERAR PDF ─────────────────────────────────────────────────────────────────
@st.cache_data
def get_pdf_bytes() -> bytes:
    return build_pdf()


pdf_bytes = get_pdf_bytes()


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:12px 0 18px;">
        <div style="font-size:2.2rem;">🏗️</div>
        <div style="color:{C_GREEN};font-weight:800;font-size:1.2rem;letter-spacing:1px;">PREFORTE</div>
        <div style="color:{C_GRAY};font-size:0.72rem;margin-top:2px;">
            Pretensados y Hormigones S.A.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<div style='color:{C_GRAY};font-size:.75rem;font-weight:700;'>PERIODO ANALIZADO</div>",
                unsafe_allow_html=True)
    st.caption("20 Feb – 19 May 2026 · 3 meses")

    st.markdown(f"<div style='color:{C_GRAY};font-size:.75rem;font-weight:700;margin-top:10px;'>DATOS REALES</div>",
                unsafe_allow_html=True)
    st.caption(f"📘 Facebook · 24 posts · {reach_fb:,} personas")
    st.caption(f"📸 Instagram · 24 posts · {reach_ig:,} personas")
    st.caption("💰 Inversion: $0 USD (organico)")

    st.divider()

    st.markdown(f"<div style='color:{C_GRAY};font-size:.75rem;font-weight:700;'>CANALES OFICIALES</div>",
                unsafe_allow_html=True)

    links = [
        ("🌐", "Sitio Web",  "https://www.preforte.com.bo"),
        ("📘", "Facebook",   "https://www.facebook.com/share/1Nrc39EvH1/?mibextid=wwXIfr"),
        ("📸", "Instagram",  "https://www.instagram.com/preforte.com.bo"),
        ("💼", "LinkedIn",   "https://www.linkedin.com/company/preforte-pretensados-y-hormigones-s-a/"),
        ("🎵", "TikTok",     "https://www.tiktok.com/@preforte.sa"),
    ]
    for icon, label, url in links:
        st.markdown(
            f'<a href="{url}" target="_blank" style="display:block;padding:5px 8px;'
            f'color:{C_DARK};text-decoration:none;border-radius:6px;font-size:.88rem;'
            f'background:{C_BG};border:1px solid {C_BORDER};margin-bottom:4px;">'
            f'{icon} {label}</a>',
            unsafe_allow_html=True,
        )

    st.divider()

    st.download_button(
        label="📄  Descargar Reporte PDF",
        data=pdf_bytes,
        file_name="PREFORTE_Reporte_Marketing_Mayo2026.pdf",
        mime="application/pdf",
        use_container_width=True,
        type="primary",
    )
    st.caption("Reporte ejecutivo estructurado con KPIs, audiencia y recomendaciones.")


# ─── HEADER ──────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="background:linear-gradient(135deg,{C_GREEN} 0%,#059669 100%);
            border-radius:12px;padding:20px 28px;margin-bottom:20px;">
  <h1 style="color:white;margin:0;font-size:1.6rem;">
      🏗️ &nbsp; PREFORTE · Dashboard de Marketing Organico
  </h1>
  <p style="color:rgba(255,255,255,.85);margin:6px 0 0;font-size:.92rem;">
      Periodo: <strong>20 Febrero – 19 Mayo 2026</strong> &nbsp;·&nbsp;
      Facebook + Instagram &nbsp;·&nbsp;
      <strong>$0 USD</strong> — 100% organico
  </p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "📊  Metricas de Canales",
    "👥  Perfil de Audiencia",
    "🎯  Estrategia y Recomendaciones",
])


# ══════════════════════════════════════════════════════════════════════════════════
# TAB 1 · METRICAS
# ══════════════════════════════════════════════════════════════════════════════════
with tab1:

    # ── KPIs ──────────────────────────────────────────────────────────────────────
    st.subheader("KPIs Principales — Periodo Feb–May 2026")
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("📘 Alcance Prom. FB",   f"{avg_r_fb:,.0f}",   "personas / post")
    k2.metric("📸 Alcance Prom. IG",   f"{avg_r_ig:,.0f}",   "personas / post")
    k3.metric("💚 Engagement FB",      f"{avg_er_fb:.2f} %", "promedio organico")
    k4.metric("💚 Engagement IG",      f"{avg_er_ig:.2f} %", "promedio organico")
    k5.metric("🔗 Clics Enlace FB",    f"{clics_fb:,}",      f"CTR {ctr_fb:.2f} %")

    st.divider()

    # ── Alcance acumulado + ER por tipo ───────────────────────────────────────────
    st.subheader("Facebook vs Instagram — Comparativa Directa")
    ca, cb = st.columns(2)

    with ca:
        # Alcance acumulado en el tiempo
        ts_fb = df_fb[["Hora de publicacion", "Alcance"]].sort_values("Hora de publicacion").copy()
        ts_fb["Acumulado"] = ts_fb["Alcance"].cumsum()
        ts_fb["Canal"]     = "Facebook"
        ts_ig = df_ig[["Hora de publicacion", "Alcance"]].sort_values("Hora de publicacion").copy()
        ts_ig["Acumulado"] = ts_ig["Alcance"].cumsum()
        ts_ig["Canal"]     = "Instagram"
        ts_all = pd.concat([ts_fb, ts_ig])

        fig_ts = px.line(
            ts_all, x="Hora de publicacion", y="Acumulado", color="Canal",
            color_discrete_map={"Facebook": C_FB, "Instagram": C_IG},
            markers=True, height=310,
            title="Alcance Organico Acumulado en el Tiempo",
        )
        fig_ts.update_layout(**LAYOUT,
                             xaxis_title="", yaxis_title="Personas alcanzadas",
                             legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig_ts, use_container_width=True)

    with cb:
        # ER promedio por canal y tipo
        df_er_cmp = pd.concat([
            er_type_fb.reset_index().rename(columns={"ER (%)": "ER"}).assign(Canal="Facebook"),
            er_type_ig.reset_index().rename(columns={"ER (%)": "ER"}).assign(Canal="Instagram"),
        ])
        fig_er = px.bar(
            df_er_cmp, x="Tipo", y="ER", color="Canal",
            barmode="group",
            color_discrete_map={"Facebook": C_FB, "Instagram": C_IG},
            text_auto=".1f", height=310,
            title="Engagement Rate por Tipo de Contenido",
        )
        fig_er.update_layout(**LAYOUT, xaxis_title="", yaxis_title="ER (%)",
                              legend=dict(orientation="h", y=1.12))
        fig_er.update_traces(textposition="outside")
        st.plotly_chart(fig_er, use_container_width=True)

    # Distribución de alcance (boxplot) + ER por hora
    cc, cd = st.columns(2)

    with cc:
        df_box = pd.concat([
            df_fb[["Alcance"]].assign(Canal="Facebook"),
            df_ig[["Alcance"]].assign(Canal="Instagram"),
        ])
        fig_box = px.box(
            df_box, x="Canal", y="Alcance", color="Canal", points="all",
            color_discrete_map={"Facebook": C_FB, "Instagram": C_IG},
            height=290, title="Distribucion de Alcance por Post",
        )
        fig_box.update_layout(**LAYOUT, showlegend=False, xaxis_title="")
        st.plotly_chart(fig_box, use_container_width=True)

    with cd:
        hr_fb = df_fb.groupby("Hora")["ER (%)"].mean().reset_index().assign(Canal="Facebook")
        hr_ig = df_ig.groupby("Hora")["ER (%)"].mean().reset_index().assign(Canal="Instagram")
        fig_hr = px.bar(
            pd.concat([hr_fb, hr_ig]), x="Hora", y="ER (%)", color="Canal",
            barmode="group",
            color_discrete_map={"Facebook": C_FB, "Instagram": C_IG},
            height=290, title="Engagement Rate por Hora del Dia",
        )
        fig_hr.update_layout(**LAYOUT, xaxis=dict(dtick=1, title="Hora"),
                              yaxis_title="ER (%)", legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig_hr, use_container_width=True)

    st.divider()

    # ── ER por Dia + Tipo individual ─────────────────────────────────────────────
    ce, cf = st.columns(2)

    with ce:
        st.subheader("Engagement por Dia de la Semana")
        erd_fb = er_day_fb.reset_index().rename(columns={"Dia semana": "Dia"})
        erd_ig = er_day_ig.reset_index().rename(columns={"Dia semana": "Dia"})

        fig_day = go.Figure()
        fig_day.add_trace(go.Scatter(
            x=erd_fb["Dia"], y=erd_fb["ER (%)"],
            mode="lines+markers+text", name="Facebook",
            line=dict(color=C_FB, width=2.5), marker=dict(size=9, color=C_FB),
            text=erd_fb["ER (%)"].round(1).astype(str) + "%",
            textposition="top center", textfont=dict(size=9),
        ))
        fig_day.add_trace(go.Scatter(
            x=erd_ig["Dia"], y=erd_ig["ER (%)"],
            mode="lines+markers+text", name="Instagram",
            line=dict(color=C_IG, width=2.5), marker=dict(size=9, color=C_IG),
            text=erd_ig["ER (%)"].round(1).astype(str) + "%",
            textposition="top center", textfont=dict(size=9),
        ))
        fig_day.update_layout(
            **LAYOUT, height=310,
            xaxis=dict(categoryorder="array", categoryarray=DAY_ORDER, title=""),
            yaxis_title="ER (%)",
            legend=dict(orientation="h", y=1.12),
        )
        st.plotly_chart(fig_day, use_container_width=True)

    with cf:
        st.subheader("Mix Tematico del Contenido")
        t_fb = (df_fb.groupby("Tematica", as_index=False)
                .agg(Posts=("Tematica", "count"), ER=("ER (%)", "mean"))
                .sort_values("Posts", ascending=True))
        fig_th = px.bar(
            t_fb, x="Posts", y="Tematica", orientation="h",
            color="ER", color_continuous_scale="Greens",
            text="Posts", height=310,
            title="Facebook — Posts por Tematica (color = ER%)",
        )
        fig_th.update_traces(texttemplate="%{text} posts", textposition="outside")
        fig_th.update_layout(**LAYOUT, coloraxis_colorbar=dict(title="ER %"), xaxis_title="Posts")
        st.plotly_chart(fig_th, use_container_width=True)

    st.divider()

    # ── Top 5 Posts ───────────────────────────────────────────────────────────────
    st.subheader("🏆 Top 5 Posts por Engagement Rate")
    t_fb_tab, t_ig_tab = st.tabs(["Facebook", "Instagram"])

    with t_fb_tab:
        cols_fb = ["Descripción", "Tipo", "Hora de publicacion",
                   "Alcance", "Reacciones", "Comentarios",
                   "Veces que se compartió", "Clics en el enlace", "ER (%)"]
        top5 = df_fb.nlargest(5, "ER (%)")[cols_fb].copy()
        top5["Descripción"]        = top5["Descripción"].str[:85] + "…"
        top5["Hora de publicacion"] = top5["Hora de publicacion"].dt.strftime("%d/%m/%Y %H:%M")
        st.dataframe(top5.reset_index(drop=True), use_container_width=True)

    with t_ig_tab:
        cols_ig = ["Descripción", "Tipo", "Hora de publicacion",
                   "Alcance", "Me gusta", "Comentarios",
                   "Veces que se compartió", "Veces que se guardó", "ER (%)"]
        top5 = df_ig.nlargest(5, "ER (%)")[cols_ig].copy()
        top5["Descripción"]        = top5["Descripción"].str[:85] + "…"
        top5["Hora de publicacion"] = top5["Hora de publicacion"].dt.strftime("%d/%m/%Y %H:%M")
        st.dataframe(top5.reset_index(drop=True), use_container_width=True)

    st.divider()

    # ── Mix Temático del Contenido ────────────────────────────────────────────────
    st.subheader("🗂️ Mix de Contenido Publicado — Analisis Tematico")
    st.caption(
        "Categorizacion automatica de los 24 posts de cada canal basada en palabras clave "
        "de las descripciones reales extraidas de los archivos CSV."
    )

    th_col1, th_col2 = st.columns(2)

    # Pre-calcular tematicas una sola vez
    t_fb_data = (df_fb.groupby("Tematica", as_index=False)
                 .agg(Posts=("Tematica", "count"), ER=("ER (%)", "mean"))
                 .sort_values("Posts", ascending=True))
    t_ig_data = (df_ig.groupby("Tematica", as_index=False)
                 .agg(Posts=("Tematica", "count"), ER=("ER (%)", "mean"))
                 .sort_values("Posts", ascending=True))

    with th_col1:
        fig_th_fb = px.bar(
            t_fb_data, x="Posts", y="Tematica", orientation="h",
            color="ER", color_continuous_scale="Greens",
            text="Posts", height=350,
            title="Facebook — Posts por Tematica (color = ER%)",
        )
        fig_th_fb.update_traces(texttemplate="%{text} posts", textposition="outside")
        fig_th_fb.update_layout(
            **LAYOUT,
            coloraxis_colorbar=dict(title="ER %"),
            xaxis_title="Cantidad de posts",
        )
        st.plotly_chart(fig_th_fb, use_container_width=True)

    with th_col2:
        fig_th_ig = px.bar(
            t_ig_data, x="Posts", y="Tematica", orientation="h",
            color="ER", color_continuous_scale="RdPu",
            text="Posts", height=350,
            title="Instagram — Posts por Tematica (color = ER%)",
        )
        fig_th_ig.update_traces(texttemplate="%{text} posts", textposition="outside")
        fig_th_ig.update_layout(
            **LAYOUT,
            coloraxis_colorbar=dict(title="ER %"),
            xaxis_title="Cantidad de posts",
        )
        st.plotly_chart(fig_th_ig, use_container_width=True)

    # Tabla resumen comparativa
    t_fb_tab2 = t_fb_data.rename(columns={"Posts": "Posts FB", "ER": "ER FB %"})
    t_fb_tab2["ER FB %"] = t_fb_tab2["ER FB %"].round(2)
    t_ig_tab2 = t_ig_data.rename(columns={"Posts": "Posts IG", "ER": "ER IG %"})
    t_ig_tab2["ER IG %"] = t_ig_tab2["ER IG %"].round(2)
    theme_summary = t_fb_tab2.merge(t_ig_tab2, on="Tematica", how="outer").fillna(0)
    theme_summary["Posts FB"] = theme_summary["Posts FB"].astype(int)
    theme_summary["Posts IG"] = theme_summary["Posts IG"].astype(int)
    st.dataframe(
        theme_summary.sort_values("Posts FB", ascending=False).reset_index(drop=True),
        use_container_width=True,
    )


# ══════════════════════════════════════════════════════════════════════════════════
# TAB 2 · AUDIENCIA
# ══════════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("Perfil de Audiencia · PREFORTE — Bolivia")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown(f"#### Principales Ciudades")
        df_cities = aud["ciudades"].copy()
        top5_c = df_cities.head(5).copy()
        otros  = round(df_cities.iloc[5:]["Porcentaje"].sum(), 1)
        if otros > 0:
            top5_c = pd.concat(
                [top5_c, pd.DataFrame([{"Ciudad": "Otras ciudades", "Porcentaje": otros}])],
                ignore_index=True,
            )
        greens = ["#00A859","#1FE074","#059669","#34D399","#6EE7B7","#A7F3D0"]
        fig_pie = px.pie(
            top5_c, names="Ciudad", values="Porcentaje",
            color_discrete_sequence=greens, hole=0.40, height=370,
        )
        fig_pie.update_traces(textposition="outside", textinfo="percent+label",
                              pull=[0.06, 0, 0, 0, 0, 0])
        fig_pie.update_layout(**LAYOUT, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

        fig_cbar = px.bar(
            df_cities, x="Porcentaje", y="Ciudad", orientation="h",
            color="Porcentaje", color_continuous_scale="Greens",
            text="Porcentaje", height=290,
        )
        fig_cbar.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_cbar.update_layout(**LAYOUT, yaxis=dict(autorange="reversed"),
                               coloraxis_showscale=False, xaxis_title="%")
        st.plotly_chart(fig_cbar, use_container_width=True)

    with col_b:
        st.markdown(f"#### Distribucion por Edad y Sexo")
        df_age = aud["edad_sexo"]
        fig_age = go.Figure()
        fig_age.add_trace(go.Bar(
            y=df_age["Edad"], x=df_age["Hombres"], name="Hombres",
            orientation="h", marker_color=C_FB,
            text=df_age["Hombres"].astype(str) + "%", textposition="outside",
        ))
        fig_age.add_trace(go.Bar(
            y=df_age["Edad"], x=df_age["Mujeres"], name="Mujeres",
            orientation="h", marker_color=C_IG,
            text=df_age["Mujeres"].astype(str) + "%", textposition="outside",
        ))
        fig_age.update_layout(
            **LAYOUT, barmode="group", height=360,
            xaxis_title="% de Audiencia",
            legend=dict(orientation="h", y=1.06),
        )
        st.plotly_chart(fig_age, use_container_width=True)

        st.info(
            f"**Tomador de decision B2B identificado**\n\n"
            f"Hombres 25–34 ({h2534}%) + 35–44 ({h3544}%) = **{dm_pct:.1f}%** del total. "
            f"Perfil exacto de jefes de obra, ingenieros residentes y directores de proyecto "
            f"en Bolivia. PREFORTE ya captura a su buyer persona con contenido 100% organico."
        )

        st.markdown("#### Principales Paises")
        fig_p = px.bar(
            aud["paises"].rename(columns={"Pais": "Pais"}).head(7),
            x="Pais", y="Porcentaje",
            color="Porcentaje", color_continuous_scale="Greens",
            text="Porcentaje", height=240,
        )
        fig_p.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_p.update_layout(**LAYOUT, coloraxis_showscale=False, xaxis_title="")
        st.plotly_chart(fig_p, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════════
# TAB 3 · ESTRATEGIA
# ══════════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Analisis Estrategico y Recomendaciones · PREFORTE")

    # ── Sección 0: Auditoría de Perfiles FB + IG ─────────────────────────────────
    st.markdown("### 0. Auditoria de Perfiles · Facebook e Instagram")
    st.caption(
        "Las paginas publicas de Meta requieren sesion activa para renderizar metricas de perfil. "
        "El analisis se basa en los 24 posts reales de cada canal (Feb–May 2026) "
        "extraidos de los archivos CSV."
    )

    # Pre-calcular tematicas para los cards de perfil
    t_fb_profile = (df_fb.groupby("Tematica", as_index=False)
                    .agg(Posts=("Tematica", "count"))
                    .sort_values("Posts", ascending=False))
    t_ig_profile = (df_ig.groupby("Tematica", as_index=False)
                    .agg(Posts=("Tematica", "count"))
                    .sort_values("Posts", ascending=False))

    p1, p2 = st.columns(2)

    with p1:
        mix_fb_lines = "\n".join(
            f"- {row['Tematica']}: {row['Posts']} posts"
            for _, row in t_fb_profile.iterrows()
        )
        st.info(
            f"**📘 Facebook · Preforte Pretensados y Hormigones S.A.**\n"
            f"`facebook.com/preforte`\n\n"
            f"**Datos del periodo analizado:**\n"
            f"- 24 posts · Foto ({int((df_fb['Tipo']=='Foto').sum())}) + Video ({int((df_fb['Tipo']=='Video').sum())})\n"
            f"- Alcance maximo individual: {int(df_fb['Alcance'].max()):,} personas\n"
            f"- Alcance total acumulado: {reach_fb:,} personas organicas\n"
            f"- Mejor ER individual: {top1_fb['ER (%)']:.2f}%\n\n"
            f"**Mix tematico detectado:**\n{mix_fb_lines}\n\n"
            f"**Fortaleza:** Copywriting con identidad de marca clara (valores, sostenibilidad).\n"
            f"**Brecha:** Solo {int((df_fb['Clics en el enlace']>0).sum())} de 24 posts tienen CTA con link de cotizacion."
        )

    with p2:
        mix_ig_lines = "\n".join(
            f"- {row['Tematica']}: {row['Posts']} posts"
            for _, row in t_ig_profile.iterrows()
        )
        st.info(
            f"**📸 Instagram · @preforte.com.bo**\n"
            f"`instagram.com/preforte.com.bo`\n\n"
            f"**Datos del periodo analizado:**\n"
            f"- 24 posts · Imagen ({int((df_ig['Tipo']=='Imagen').sum())}) + Reel ({int((df_ig['Tipo']=='Reel').sum())}) + Carrusel ({int((df_ig['Tipo']=='Carrusel').sum())})\n"
            f"- Alcance maximo individual: {int(df_ig['Alcance'].max()):,} personas\n"
            f"- Total guardados (saves): {saves_ig} — contenido de referencia tecnica\n"
            f"- Seguimientos generados: {int(df_ig['Seguimientos'].sum())} nuevos seguidores directos\n\n"
            f"**Mix tematico detectado:**\n{mix_ig_lines}\n\n"
            f"**Fortaleza:** Reels generan {best_er_t_ig:.2f}% ER — mayor que imagen y carrusel.\n"
            f"**Brecha:** Solo {int(df_ig['Veces que se compartió'].sum())} compartidos totales — baja viralidad B2B."
        )

    st.divider()

    # ── FB vs IG: contraste de canales ───────────────────────────────────────────
    st.markdown("### 1. Contraste Meta: Facebook vs Instagram")
    s1, s2 = st.columns(2)

    with s1:
        st.info(
            f"**📘 Facebook — Canal de Alcance y Contenido Tecnico**\n\n"
            f"Con **{avg_r_fb:,.0f} personas/post** de alcance promedio "
            f"({avg_r_fb/avg_r_ig:.1f}x mas que Instagram), Facebook es el canal donde "
            f"el contenido tecnico-comercial tiene mayor difusion. El formato "
            f"**{best_tp_fb}** lidera con **{best_er_t_fb:.2f}% ER**. "
            f"El CTR organico de **{ctr_fb:.2f}%** confirma intencion real de contacto. "
            f"Es el canal optimo para contenido de especificaciones tecnicas, comparativas "
            f"de resistencia y casos de obra con datos reales."
        )

    with s2:
        st.info(
            f"**📸 Instagram — Canal de Comunidad e Imagen Institucional**\n\n"
            f"Con **{avg_er_ig:.2f}% ER promedio** y los **{best_tp_ig}s** generando "
            f"**{best_er_t_ig:.2f}% ER**, Instagram funciona mejor para contenido "
            f"visual e institucional: obras esteticas, sostenibilidad, cultura corporativa "
            f"y reconocimiento de personas. Los **{saves_ig} guardados** en el periodo "
            f"indican que el contenido tecnico visual es usado como referencia por "
            f"arquitectos e ingenieros — alta intencion futura de compra."
        )

    # Mini-grafico comparativo
    df_cmp = pd.DataFrame({
        "Canal":   ["Facebook", "Instagram"],
        "Alcance Total (personas)": [reach_fb, reach_ig],
        "ER Promedio (%)": [round(avg_er_fb, 2), round(avg_er_ig, 2)],
    })
    g1, g2 = st.columns(2)
    with g1:
        fig_rc = px.bar(df_cmp, x="Canal", y="Alcance Total (personas)", color="Canal",
                        color_discrete_map={"Facebook": C_FB, "Instagram": C_IG},
                        text="Alcance Total (personas)", height=230)
        fig_rc.update_traces(texttemplate="%{text:,}", textposition="outside")
        fig_rc.update_layout(**LAYOUT, showlegend=False, xaxis_title="",
                             title="Alcance Total Acumulado")
        st.plotly_chart(fig_rc, use_container_width=True)
    with g2:
        fig_erc = px.bar(df_cmp, x="Canal", y="ER Promedio (%)", color="Canal",
                         color_discrete_map={"Facebook": C_FB, "Instagram": C_IG},
                         text="ER Promedio (%)", height=230)
        fig_erc.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        fig_erc.update_layout(**LAYOUT, showlegend=False, xaxis_title="",
                              title="Engagement Rate Promedio")
        st.plotly_chart(fig_erc, use_container_width=True)

    st.divider()

    # ── Auditoria canales complementarios ────────────────────────────────────────
    st.markdown("### Auditoria de Canales Complementarios")

    a1, a2 = st.columns(2)
    with a1:
        st.warning(
            "**💼 LinkedIn · 2,376 seguidores · Brechas detectadas**\n\n"
            "**Fortalezas:** Cadencia regular (post cada 3-7 dias), CTA hacia app TUPreforte, "
            "mensajes orientados a eficiencia operativa para constructoras.\n\n"
            "**Brechas:** Sin casos de estudio con datos reales, sin articulos tecnicos de "
            "liderazgo de opinion, contenido excesivamente promocional.\n\n"
            "**Accion:** 1 articulo tecnico/mes + showcase de proyectos con m², resistencias "
            "y plazo de entrega. Meta: 2,376 → 3,000 seguidores en 90 dias."
        )
    with a2:
        st.warning(
            "**🌐 preforte.com.bo · Embudo B2B — Brechas criticas**\n\n"
            "**Fortalezas:** 15+ proyectos en portfolio, certificacion IBNORCA NB 604:2023, "
            "WhatsApp como CTA principal, tecnologia CarbonCure/Ecoforte documentada.\n\n"
            "**Brechas:** Sin fichas tecnicas descargables (PDF con resistencias y dimensiones), "
            "sin formulario de cotizacion en homepage sin scroll, sin blog tecnico.\n\n"
            "**Accion:** Crear 'Biblioteca Tecnica' con PDFs de productos + formulario "
            "'Solicitar Cotizacion' visible en la primera pantalla del homepage."
        )

    st.divider()

    # ── Sección 2: TikTok vs Instagram Reels ─────────────────────────────────────
    st.markdown("### 2. El Rol de TikTok vs Instagram Reels")
    st.caption(
        "Analisis cualitativo — el perfil @preforte.sa en TikTok requiere JavaScript para "
        "renderizar. Se contrasta con el rendimiento real de Reels en Instagram."
    )

    er_reel = er_type_ig.get("Reel", 0)
    er_img  = er_type_ig.get("Imagen", 0)
    er_car  = er_type_ig.get("Carrusel", 0)

    tt1, tt2 = st.columns(2)

    with tt1:
        st.info(
            f"**🎵 TikTok @preforte.sa — Oportunidad de Alcance Masivo Organico**\n\n"
            f"TikTok distribuye contenido por **interes**, no por seguidores previos — "
            f"radicalmente distinto a Instagram donde el alcance depende de la base construida.\n\n"
            f"Para PREFORTE, TikTok permite llegar a **ingenieros y constructores jovenes (18-34)** "
            f"que no siguen paginas de materiales pero consumen contenido de obras e industria.\n\n"
            f"**Que publicar en TikTok:**\n"
            f"- Videos 15-30 seg: '¿Como se hace una vigueta pretensada?' (proceso en planta)\n"
            f"- Before/after de obras terminadas con materiales PREFORTE\n"
            f"- Control de calidad: romper probetas de hormigon (alto engagement en TikTok)\n"
            f"- 'Datos que no sabias del hormigon' — formato educativo rapido\n\n"
            f"**Hashtags objetivo:** #ConstruccionBolivia #Hormigon #Ingenieria #Viguetas"
        )

    with tt2:
        st.warning(
            f"**📱 Instagram Reels como puente hacia TikTok**\n\n"
            f"Rendimiento actual de Reels en Instagram: **{er_reel:.2f}% ER** "
            f"(vs Imagen {er_img:.2f}% · Carrusel {er_car:.2f}%). "
            f"El video corto ya supera a los formatos estaticos.\n\n"
            f"**Diferencia estrategica clave:**\n"
            f"- **Instagram Reels** → audiencia actual ya segmentada (B2B boliviano)\n"
            f"- **TikTok** → descubrimiento de nuevos usuarios que no conocen PREFORTE\n\n"
            f"**Produccion eficiente — 1 video, 3 formatos:**\n"
            f"1. Reel 30 seg (Instagram) — estetica y datos tecnicos\n"
            f"2. TikTok 15-20 seg — proceso y sorpresa visual\n"
            f"3. Video 60-90 seg (Facebook) — contexto tecnico completo\n\n"
            f"Esto maximiza el ROI de produccion sin triplicar el trabajo de contenido."
        )

    st.divider()

    # ── 3 Recomendaciones ─────────────────────────────────────────────────────────
    st.markdown("### 🎯 3 Recomendaciones Accionables · Sector Construccion Bolivia")
    r1, r2, r3 = st.columns(3)

    with r1:
        st.success(
            f"**📹 Rec. 1 — Serie de Videos Tecnicos**\n\n"
            f"Los **{best_tp_fb.lower()}s en Facebook** generan **{best_er_t_fb:.2f}% ER** "
            f"vs promedio de **{avg_er_fb:.2f}%**. Producir 4-6 clips de 60-90 seg:\n\n"
            f"- Montaje real de viguetas con datos de resistencia\n"
            f"- Hormigon UltraForte: comparativa vs convencional\n"
            f"- Testimonios de ingenieros clientes (SC + LP)\n\n"
            f"Publicar **cada {best_day}** ({best_day_v:.2f}% ER — pico semanal).\n\n"
            f"**KPI:** Alcance {avg_r_fb:,.0f} → {avg_r_fb*2:,.0f} personas/post en 60 dias."
        )
    with r2:
        st.success(
            f"**🏙️ Rec. 2 — Activacion Regional LP + CBBA**\n\n"
            f"La Paz (**{lp_pct}%**) + Cochabamba (**{cbba_pct}%**) = "
            f"**{lp_pct+cbba_pct:.1f}%** audiencia sin contenido geo-especifico:\n\n"
            f"- Posts con obras emblemáticas por ciudad\n"
            f"- Links de cotizacion UTM por ciudad en posts de producto\n"
            f"- Contenido sismico (LP) y expansion urbana (CBBA)\n"
            f"- Landing page 'Cotizar en La Paz / Cochabamba'\n\n"
            f"**KPI:** CTR regional > 2% · Formularios web > 5/mes por ciudad."
        )
    with r3:
        st.success(
            f"**📅 Rec. 3 — Parrilla Editorial B2B Semanal**\n\n"
            f"Hombres 25-44 = {dm_pct:.1f}% de audiencia. Calendario fijo:\n\n"
            f"- **{best_day}:** Post tecnico (normas IBNORCA, dosificaciones)\n"
            f"- **Miercoles:** Caso de exito con datos reales de obra\n"
            f"- **Viernes:** Tip sostenibilidad Ecoforte / Carboncure\n"
            f"- **LinkedIn:** 1 articulo tecnico mensual\n\n"
            f"**KPI:** ER de {avg_er_fb:.2f}% → {best_er_t_fb:.1f}% en 60 dias."
        )

    st.divider()
    st.caption(
        "Analisis generado a partir de datos organicos reales (Feb–May 2026) · "
        "PREFORTE Marketing Intelligence · 20 Mayo 2026"
    )
