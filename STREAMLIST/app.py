"""Painel web de estudo para dados públicos da PIM-PF/SIDRA — layout de painel de KPI."""
import html
import sys
from pathlib import Path

import altair as alt
import pandas as pd
import requests
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from SRC.api import consultar_sidra  # Reutiliza o cliente HTTP existente

SETORES = {
    "Máquinas, aparelhos e materiais elétricos": "129336",
    "Máquinas e equipamentos": "129337",
    "Indústria geral": "129314",
    "Indústrias de transformação": "129316",
    "Veículos automotores, reboques e carrocerias": "129338",
    "Equipamentos de informática, eletrônicos e ópticos": "129335",
    "Produtos alimentícios": "129317",
    "Manutenção, reparação e instalação de máquinas": "129342",
}
# Nomes curtos só para caber nos gráficos e tabelas estreitos.
CURTOS = {
    "Máquinas, aparelhos e materiais elétricos": "Materiais elétricos",
    "Máquinas e equipamentos": "Máquinas e equip.",
    "Indústria geral": "Indústria geral",
    "Indústrias de transformação": "Transformação",
    "Veículos automotores, reboques e carrocerias": "Veículos",
    "Equipamentos de informática, eletrônicos e ópticos": "Informática e eletrônicos",
    "Produtos alimentícios": "Alimentícios",
    "Manutenção, reparação e instalação de máquinas": "Manutenção e instalação",
}
INDICADORES = {
    "Índice de produção física — sem ajuste sazonal": ("12606", "indice"),
    "Índice de produção física — com ajuste sazonal": ("12607", "indice"),
    "Variação mensal — com ajuste sazonal": ("11601", "percentual"),
    "Variação frente ao mesmo mês do ano anterior": ("11602", "percentual"),
    "Variação acumulada no ano": ("11603", "percentual"),
    "Variação acumulada em 12 meses": ("11604", "percentual"),
}

# Paleta do painel
BG, SURFACE, LINE = "#EEF2F5", "#FFFFFF", "#D9E0E6"
INK, MUTED, GRID = "#12263A", "#5B6B7B", "#E6EBF0"
TEAL, TEAL_D, TEAL_L = "#0F8B8D", "#0B6B6D", "#8FD0D1"
AMBER, AMBER_L = "#F2A900", "#F7CF6B"
UP, DOWN = "#15803D", "#C62828"

st.set_page_config(page_title="SIDRA | Inteligência Industrial", page_icon="🏭", layout="wide")

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap');
:root {color-scheme: light;}
html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {background:__BG__ !important;}
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stSidebar"] {color:__INK__ !important;}
[data-testid="stHeader"] {background:transparent !important;}
html, body, [class*="css"], .stMarkdown {font-family:'Inter',sans-serif;}
.block-container {max-width:1320px; padding:1.6rem 2rem 2.5rem;}
:where(.stApp) :where(p, li, label, h1, h2, h3, h4, h5, h6, summary, small) {color:__INK__ !important;}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * {color:__MUTED__ !important;}
a, a * {color:__TEAL_D__ !important;}
hr {border-color:__LINE__ !important;}

/* Barra lateral */
[data-testid="stSidebar"], [data-testid="stSidebar"] > div {background:__SURF__ !important;}
[data-testid="stSidebar"] {border-right:1px solid __LINE__;}
[data-testid="stSpinner"] * {color:__INK__ !important;}

/* Campos de seleção (inclui a lista suspensa, que fica fora do .stApp) */
[data-baseweb="select"] > div {background:__SURF__ !important; border:1px solid __LINE__ !important; border-radius:6px !important;}
[data-baseweb="select"] * {color:__INK__ !important;}
[data-baseweb="select"] svg {fill:__MUTED__ !important;}
[data-baseweb="popover"] > div, [data-baseweb="popover"] ul, [data-baseweb="popover"] li {background:__SURF__ !important; color:__INK__ !important;}
[data-baseweb="popover"] li:hover, [data-baseweb="popover"] li[aria-selected="true"] {background:#E3F1F2 !important;}

/* Slider */
[data-testid="stSlider"] [role="slider"] {background-color:__TEAL__ !important;}
[data-testid="stSlider"] [data-testid="stSliderThumbValue"],
[data-testid="stSlider"] [data-testid="stTickBarMin"],
[data-testid="stSlider"] [data-testid="stTickBarMax"] {color:__TEAL_D__ !important;}

/* Botões */
.stButton > button, .stDownloadButton > button {background:__SURF__ !important; color:__INK__ !important;
  border:1px solid __LINE__ !important; border-radius:6px;}
.stButton > button:hover, .stDownloadButton > button:hover {border-color:__TEAL__ !important;}
.stButton > button:hover p, .stDownloadButton > button:hover p {color:__TEAL_D__ !important;}

/* Expanders e avisos */
[data-testid="stExpander"] details {background:__SURF__ !important; border:1px solid __LINE__ !important; border-radius:6px !important;}
[data-testid="stExpander"] summary {background:__SURF__ !important; border-radius:6px;}
[data-testid="stExpander"] summary:hover {background:#F3F6F8 !important;}
[data-testid="stExpander"] summary svg {color:__MUTED__ !important; fill:__MUTED__ !important;}
[data-testid="stAlert"] * {color:__INK__ !important;}

/* Cabeçalho */
.hero {display:flex; align-items:center; gap:.7rem;}
.hero-dot {width:20px; height:20px; border-radius:50%; background:__TEAL__; box-shadow:0 0 0 4px #0F8B8D26; flex:none;}
.hero-line {width:54px; height:2px; background:__AMBER__; position:relative; flex:none;}
.hero-line::after {content:""; position:absolute; right:-2px; top:-4px; border-left:8px solid __AMBER__;
  border-top:5px solid transparent; border-bottom:5px solid transparent;}
.hero-title {font-family:'Space Mono',monospace; font-size:1.9rem; letter-spacing:.01em; color:__INK__ !important; line-height:1.2;}
.hero-sub {color:__MUTED__ !important; font-size:.88rem; margin:.5rem 0 1.1rem;}

/* Faixa de KPIs */
.kpi-row {display:flex; margin:.2rem 0 1.4rem;}
.kpi {flex:1; text-align:center; padding:.2rem .8rem; border-left:1px solid __LINE__; min-height:96px;}
.kpi:first-child {border-left:none;}
.kpi-label {font-size:1rem; color:__INK__ !important;}
.kpi-value {font-size:1.6rem; font-weight:700; margin-top:.1rem; color:__INK__ !important;}
.kpi-delta {font-size:.85rem; font-weight:700;}
.kpi-note {font-size:.7rem; color:__MUTED__ !important; margin-top:.1rem;}
.up {color:__UP__ !important;} .down {color:__DOWN__ !important;} .flat {color:__MUTED__ !important;}

/* Painéis brancos (identificados pelo marcador .panel-marker) */
div[data-testid="stVerticalBlock"]:has(> div > div[data-testid="stMarkdown"] .panel-marker) {
  background:__SURF__; border:1px solid __LINE__; border-radius:6px; padding:1rem 1.1rem 1.1rem;
  box-shadow:0 1px 3px rgba(18,38,58,.08); gap:.4rem;}
.panel-title {text-align:center; font-weight:700; font-size:1.15rem; color:__INK__ !important;}
.panel-title small {font-weight:400; font-size:.75rem; color:__MUTED__ !important; margin-left:.35rem;}
.panel-rule {position:relative; width:34%; height:1px; background:#C5CED7; margin:.5rem auto .6rem;}
.panel-rule::after {content:""; position:absolute; left:50%; top:-4px; width:7px; height:7px; background:__SURF__;
  border:1px solid #9AA8B5; border-radius:50%; transform:translateX(-50%);}
.panel-note {text-align:center; font-size:.72rem; color:__MUTED__ !important;}

/* Tabelas com células coloridas */
.dwrap {max-height:380px; overflow:auto; border:1px solid __LINE__; border-radius:6px;}
.dtable {width:100%; border-collapse:collapse; font-size:.85rem;}
.dtable th {background:#E9EEF2; font-weight:700; padding:.5rem .4rem; border-bottom:2px solid #CBD4DC; text-align:center;
  color:__INK__ !important; position:sticky; top:0;}
.dtable td {padding:.36rem .4rem; border-bottom:1px solid __GRID__; text-align:center; color:__INK__ !important; background:__SURF__;}
.dtable th:first-child, .dtable td:first-child {text-align:left; padding-left:.6rem;}
.dtable tr.sel td {background:#E3F1F2; font-weight:600;}
.pill {display:inline-block; min-width:78px; padding:2px 8px; border-radius:3px; font-weight:500; font-size:.8rem; color:__INK__ !important;}

@media (max-width:900px) {
  .kpi-row {flex-wrap:wrap; row-gap:1rem;}
  .kpi {flex:1 1 33%;}
  .hero-title {font-size:1.35rem;}
}
"""
TOKENS = {"__BG__": BG, "__SURF__": SURFACE, "__LINE__": LINE, "__INK__": INK, "__MUTED__": MUTED, "__GRID__": GRID,
          "__TEAL__": TEAL, "__TEAL_D__": TEAL_D, "__AMBER__": AMBER, "__UP__": UP, "__DOWN__": DOWN}
for _chave, _valor in TOKENS.items():
    CSS = CSS.replace(_chave, _valor)
st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


@st.cache_data(ttl=3600, show_spinner=False)
def buscar(setor: str, variavel: str, meses: int) -> tuple[pd.DataFrame, str]:
    # A URL é criada pela camada de API, nunca pelo frontend.
    dados = consultar_sidra(categoria=setor, variavel=variavel, meses=meses)
    if not isinstance(dados, list) or len(dados) < 2:
        return pd.DataFrame(), ""
    linhas = []
    for item in dados[1:]:
        periodo_cod = str(item.get("D3C", ""))
        valor = pd.to_numeric(item.get("V"), errors="coerce")
        if pd.isna(valor) or not (len(periodo_cod) == 6 and periodo_cod.isdigit()):
            continue
        linhas.append({"mes": pd.to_datetime(periodo_cod, format="%Y%m"),
                       "periodo": item.get("D3N", periodo_cod),
                       "valor": float(valor)})
    df = pd.DataFrame(linhas)
    if not df.empty:
        df = df.sort_values("mes").drop_duplicates("mes")
    return df, f"https://apisidra.ibge.gov.br/values/t/8888/n1/all/v/{variavel}/p/last%20{meses}/c544/{setor}"


# ---------- Helpers de formatação e componentes visuais ----------
def fmt(v: float) -> str:
    return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_sinal(v: float) -> str:
    return ("+" if v > 0 else "") + fmt(v)


def lerp_hex(c1: str, c2: str, t: float) -> str:
    t = max(0.0, min(1.0, t))
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(a, b))


def pill(texto: str, cor: str) -> str:
    return f'<span class="pill" style="background:{cor}">{html.escape(texto)}</span>'


def cor_delta(d: float, dmax: float) -> str:
    t = abs(d) / dmax if dmax else 0
    if d > 0:
        return lerp_hex("#E3F4E8", "#6FCF97", t)
    if d < 0:
        return lerp_hex("#FDE4E4", "#F28B8B", t)
    return "#E8EDF1"


def tabela_html(cabecalhos: list[str], linhas: list[list[str]], classes: list[str] | None = None) -> str:
    cab = "".join(f"<th>{html.escape(h)}</th>" for h in cabecalhos)
    corpo = ""
    for i, linha in enumerate(linhas):
        cls = f' class="{classes[i]}"' if classes and classes[i] else ""
        corpo += f"<tr{cls}>" + "".join(f"<td>{c}</td>" for c in linha) + "</tr>"
    return f'<table class="dtable"><thead><tr>{cab}</tr></thead><tbody>{corpo}</tbody></table>'


def kpi(rotulo: str, valor: str, delta: float | None = None, delta_txt: str = "", nota: str = "") -> str:
    delta_html = ""
    if delta is not None:
        seta, cls = ("▲", "up") if delta > 0 else ("▼", "down") if delta < 0 else ("■", "flat")
        delta_html = f'<div class="kpi-delta {cls}">{seta} {html.escape(delta_txt)}</div>'
    nota_html = f'<div class="kpi-note">{html.escape(nota)}</div>' if nota else ""
    return (f'<div class="kpi"><div class="kpi-label">{html.escape(rotulo)}</div>'
            f'<div class="kpi-value">{html.escape(valor)}</div>{delta_html}{nota_html}</div>')


def painel_cabecalho(titulo: str, sub: str = "") -> None:
    sub_html = f"<small>{html.escape(sub)}</small>" if sub else ""
    st.markdown(f'<span class="panel-marker"></span><div class="panel-title">{html.escape(titulo)}{sub_html}</div>'
                '<div class="panel-rule"></div>', unsafe_allow_html=True)


def estilizar(chart: alt.Chart | alt.LayerChart) -> alt.Chart | alt.LayerChart:
    return (chart.configure(background="transparent", font="Inter")
            .configure_view(strokeWidth=0)
            .configure_axis(labelColor=MUTED, titleColor=MUTED, gridColor=GRID, domainColor=LINE,
                            tickColor=LINE, labelFontSize=11)
            .configure_legend(labelColor=INK, labelFontSize=12, symbolType="square"))


# ---------- Cabeçalho ----------
st.markdown(
    '<div class="hero"><span class="hero-dot"></span><span class="hero-line"></span>'
    '<span class="hero-title">Painel de KPI da produção industrial</span></div>'
    '<div class="hero-sub">Dados públicos oficiais do IBGE (SIDRA) · PIM-PF, Pesquisa Industrial Mensal de Produção Física · Brasil</div>',
    unsafe_allow_html=True,
)
st.info("Este painel acompanha a atividade **dos setores industriais**, não a produção, vendas ou sensores de uma empresa específica.")

with st.sidebar:
    st.header("Configurar consulta")
    setor_nome = st.selectbox("Setor industrial", list(SETORES))
    indicador_nome = st.selectbox("Indicador", list(INDICADORES))
    meses = st.select_slider("Meses disponíveis mais recentes", options=[6, 12, 24, 36, 60], value=12)
    st.caption("A disponibilidade dos valores pode variar por setor e indicador. Dados publicados com defasagem.")
    if st.button("Atualizar dados", use_container_width=True):
        buscar.clear()

codigo_variavel, tipo = INDICADORES[indicador_nome]
try:
    with st.spinner("Consultando a API oficial do IBGE..."):
        df, url = buscar(SETORES[setor_nome], codigo_variavel, meses)
except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
    st.error(f"Não foi possível consultar os dados do SIDRA: {exc}")
    st.info("Verifique a internet, a disponibilidade da API e a combinação de indicador e categoria. Nenhum dado foi simulado.")
    st.stop()

if df.empty:
    st.warning("A consulta não retornou valores numéricos para esta combinação. Escolha outro indicador ou setor.")
    st.stop()

# ---------- Cálculos ----------
df = df.copy()
df["media_movel"] = df["valor"].rolling(3, min_periods=1).mean()
df["delta"] = df["valor"].diff()
ultimo = df.iloc[-1]
anterior = df.iloc[-2] if len(df) >= 2 else None
unidade = "%" if tipo == "percentual" else "pontos de índice"
suf = "%" if tipo == "percentual" else ""
suf_delta = " p.p." if tipo == "percentual" else " pontos"
i_max, i_min = df["valor"].idxmax(), df["valor"].idxmin()

# ---------- Faixa de KPIs ----------
d_ult = float(ultimo["valor"] - anterior["valor"]) if anterior is not None else None
kpis = [
    kpi("Último valor", f"{fmt(ultimo['valor'])}{suf}", d_ult,
        f"{fmt_sinal(d_ult)}{suf_delta}" if d_ult is not None else "", "vs. observação anterior"),
    kpi("Período de referência", ultimo["mes"].strftime("%m/%Y"), nota="mês da última observação"),
    kpi("Média do período", f"{fmt(df['valor'].mean())}{suf}", nota=f"últimos {len(df)} meses"),
    kpi("Máximo", f"{fmt(df.loc[i_max, 'valor'])}{suf}", nota=df.loc[i_max, "mes"].strftime("em %m/%Y")),
    kpi("Mínimo", f"{fmt(df.loc[i_min, 'valor'])}{suf}", nota=df.loc[i_min, "mes"].strftime("em %m/%Y")),
    kpi("Observações", str(len(df)), nota="meses com valor numérico"),
]
st.markdown(f'<div class="kpi-row">{"".join(kpis)}</div>', unsafe_allow_html=True)
st.caption(f"Setor: {setor_nome}  ·  Indicador: {indicador_nome}")

# ---------- Comparativo entre setores (mesmo indicador) ----------
def comparar_setores(variavel: str) -> pd.DataFrame:
    linhas = []
    for nome, cod in SETORES.items():
        try:
            d, _ = buscar(cod, variavel, 6)
        except (requests.RequestException, ValueError, KeyError, TypeError):
            continue
        if d.empty:
            continue
        ult = d.iloc[-1]
        ant = d.iloc[-2]["valor"] if len(d) >= 2 else None
        linhas.append({"setor": nome, "curto": CURTOS.get(nome, nome), "valor": float(ult["valor"]),
                       "delta": float(ult["valor"] - ant) if ant is not None else None,
                       "periodo": ult["mes"].strftime("%m/%Y"), "selecionado": nome == setor_nome})
    return pd.DataFrame(linhas)


with st.spinner("Comparando setores..."):
    df_set = comparar_setores(codigo_variavel)

# ---------- Linha 1: evolução · comparativo · distribuição ----------
col_a, col_b, col_c = st.columns([1.7, 1.15, 0.95], gap="medium")

with col_a:
    with st.container():
        painel_cabecalho("Evolução do indicador", f"valor e média móvel · {len(df)} meses")
        largura = max(3, int(520 / len(df)) - 2)
        escala = alt.Scale(domain=["Valor", "Média móvel (3 meses)"], range=[AMBER, TEAL])
        legenda = alt.Legend(orient="top", title=None)
        base = alt.Chart(df).encode(x=alt.X("mes:T", title=None,
                                             axis=alt.Axis(format="%m/%Y", labelAngle=-45, grid=False)))
        tip = [alt.Tooltip("mes:T", title="Mês", format="%m/%Y"),
               alt.Tooltip("valor:Q", title="Valor", format=",.2f"),
               alt.Tooltip("media_movel:Q", title="Média móvel (3m)", format=",.2f")]
        barras = (base.transform_calculate(serie="'Valor'")
                  .mark_bar(size=largura, cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
                  .encode(y=alt.Y("valor:Q", title=None), color=alt.Color("serie:N", scale=escala, legend=legenda),
                          tooltip=tip))
        linha = (base.transform_calculate(serie="'Média móvel (3 meses)'")
                 .mark_line(strokeWidth=2.5, point=alt.OverlayMarkDef(size=26, filled=True))
                 .encode(y=alt.Y("media_movel:Q", title=None),
                         color=alt.Color("serie:N", scale=escala, legend=legenda), tooltip=tip))
        st.altair_chart(estilizar((barras + linha).properties(height=300)), use_container_width=True, theme=None)

with col_b:
    with st.container():
        painel_cabecalho("Comparativo entre setores", "último valor")
        if df_set.empty:
            st.caption("Não foi possível obter os demais setores para este indicador.")
        else:
            tip_s = [alt.Tooltip("setor:N", title="Setor"), alt.Tooltip("periodo:N", title="Período"),
                     alt.Tooltip("valor:Q", title="Valor", format=",.2f")]
            barras_s = alt.Chart(df_set).mark_bar(cornerRadiusEnd=3, size=15).encode(
                y=alt.Y("curto:N", sort="-x", title=None,
                        axis=alt.Axis(labelLimit=150, ticks=False, domain=False, grid=False)),
                x=alt.X("valor:Q", title=None),
                color=alt.condition(alt.datum.selecionado, alt.value(TEAL), alt.value(AMBER)),
                tooltip=tip_s)
            rotulos = barras_s.mark_text(align="left", dx=4, fontSize=11).encode(
                text=alt.Text("valor:Q", format=",.1f"), color=alt.value(INK))
            st.altair_chart(estilizar((barras_s + rotulos).properties(height=alt.Step(26))),
                            use_container_width=True, theme=None)
            st.markdown('<div class="panel-note">Verde-água: setor selecionado</div>', unsafe_allow_html=True)

with col_c:
    with st.container():
        painel_cabecalho("Direção mensal")
        dif = df["valor"].diff().dropna()
        if dif.empty:
            st.caption("São necessárias ao menos duas observações.")
        else:
            contagem = pd.DataFrame({"situacao": ["Em alta", "Em queda", "Estável"],
                                     "n": [int((dif > 0).sum()), int((dif < 0).sum()), int((dif == 0).sum())]})
            pct_alta = contagem.loc[0, "n"] / contagem["n"].sum() * 100
            rosca = alt.Chart(contagem).mark_arc(innerRadius=52, outerRadius=88, stroke="#FFFFFF", strokeWidth=2).encode(
                theta="n:Q",
                color=alt.Color("situacao:N", legend=alt.Legend(orient="bottom", title=None),
                                scale=alt.Scale(domain=["Em alta", "Em queda", "Estável"],
                                                range=[TEAL, AMBER, TEAL_L])),
                tooltip=[alt.Tooltip("situacao:N", title="Situação"), alt.Tooltip("n:Q", title="Meses")])
            centro = alt.Chart(pd.DataFrame({"t": [f"{pct_alta:.0f}%"]})).mark_text(
                fontSize=26, fontWeight="bold", color=INK).encode(text="t:N")
            st.altair_chart(estilizar((rosca + centro).properties(height=240)), use_container_width=True, theme=None)
            st.markdown('<div class="panel-note">dos meses subiram frente à observação anterior</div>',
                        unsafe_allow_html=True)

# ---------- Linha 2: tabelas ----------
st.write("")
col_d, col_e = st.columns(2, gap="medium")

with col_d:
    with st.container():
        painel_cabecalho("Últimas observações", f"valor em {unidade}")
        recentes = df.tail(10).iloc[::-1]
        vmin, vmax = df["valor"].min(), df["valor"].max()
        dmax = df["delta"].abs().max() or 0
        linhas_t = []
        for _, r in recentes.iterrows():
            calor = lerp_hex("#FFF1C9", "#F7C948", (r["valor"] - vmin) / ((vmax - vmin) or 1))
            if pd.isna(r["delta"]):
                var_cel = "—"
            else:
                var_cel = pill(f"{fmt_sinal(r['delta'])}{suf_delta}", cor_delta(r["delta"], dmax))
            linhas_t.append([html.escape(str(r["periodo"])), pill(f"{fmt(r['valor'])}{suf}", calor), var_cel])
        st.markdown(tabela_html(["Período", "Valor", "Diferença p/ anterior"], linhas_t), unsafe_allow_html=True)

with col_e:
    with st.container():
        painel_cabecalho("Ranking de setores", "mesmo indicador")
        if df_set.empty:
            st.caption("Não foi possível obter os demais setores para este indicador.")
        else:
            rank = df_set.sort_values("valor", ascending=False).reset_index(drop=True)
            rmin, rmax = rank["valor"].min(), rank["valor"].max()
            dmax_s = rank["delta"].abs().max() or 0
            linhas_r, classes = [], []
            for _, r in rank.iterrows():
                calor = lerp_hex("#E3F4E8", "#6FCF97", (r["valor"] - rmin) / ((rmax - rmin) or 1))
                var_cel = "—" if pd.isna(r["delta"]) else pill(f"{fmt_sinal(r['delta'])}{suf_delta}",
                                                                 cor_delta(r["delta"], dmax_s))
                linhas_r.append([html.escape(r["curto"]), pill(f"{fmt(r['valor'])}{suf}", calor), var_cel,
                                 html.escape(r["periodo"])])
                classes.append("sel" if r["selecionado"] else "")
            st.markdown(tabela_html(["Setor", "Último valor", "Diferença p/ anterior", "Período"], linhas_r, classes),
                        unsafe_allow_html=True)

# ---------- Detalhes e documentação ----------
st.write("")
with st.expander("📖 Como interpretar este gráfico?"):
    if codigo_variavel == "12606":
        st.markdown("""**Eixo horizontal:** meses de referência. **Eixo vertical:** número-índice, com média de 2022 igual a 100.  
**Exemplo:** 110 significa um nível 10% acima do *nível médio de referência de 2022*, não crescimento de 10% desde o mês anterior.  
**Cuidado:** série sem ajuste sazonal; meses consecutivos podem refletir sazonalidade. Para crescimento mensal, utilize a variável 11601.""")
    elif codigo_variavel == "12607":
        st.markdown("**Índice dessazonalizado:** referência 2022 = 100, com ajuste para padrões sazonais. A diferença entre dois índices está em pontos de índice; não confunda com porcentagem.")
    elif codigo_variavel == "11601":
        st.markdown("**Variação mensal (%):** compara a produção com o mês imediatamente anterior, com ajuste sazonal. Valor positivo indica crescimento; negativo, retração.")
    elif codigo_variavel == "11602":
        st.markdown("**Variação interanual (%):** compara cada mês com o mesmo mês do ano anterior. Não é comparação com o mês anterior.")
    elif codigo_variavel == "11603":
        st.markdown("**Acumulado no ano (%):** compara o resultado acumulado desde janeiro com o mesmo intervalo do ano anterior.")
    else:
        st.markdown("**Acumulado em 12 meses (%):** compara os 12 meses encerrados no mês de referência com os 12 meses imediatamente anteriores.")
    st.caption("A média móvel de 3 meses é calculada aqui para suavizar o gráfico; os demais valores vêm direto da API. Resultados podem ser revisados pelo IBGE.")

with st.expander("📋 Tabela completa e download"):
    tabela = df[["periodo", "valor"]].rename(columns={"periodo": "Período", "valor": f"Valor ({unidade})"})
    linhas_c = [[html.escape(str(p)), fmt(v)] for p, v in zip(df["periodo"], df["valor"])]
    st.markdown('<div class="dwrap">' + tabela_html(["Período", f"Valor ({unidade})"], linhas_c) + "</div>",
                unsafe_allow_html=True)
    st.download_button("⬇️ Baixar tabela CSV", data=tabela.to_csv(index=False, sep=";").encode("utf-8-sig"),
                       file_name="sidra_industria.csv", mime="text/csv")

with st.expander("ℹ️ Dicionário dos dados"):
    st.markdown("""- **Setor industrial:** atividade econômica classificada segundo a CNAE 2.0. É um agregado setorial, não uma empresa.  
- **Período:** mês/ano a que a estatística se refere.  
- **Número-índice:** escala relativa em que 2022 = 100; não é quantidade de unidades fabricadas.  
- **Ajuste sazonal:** método estatístico para reduzir efeitos periódicos recorrentes.  
- **Variação percentual:** taxa informada diretamente pelo IBGE.  
- **Pontos percentuais (p.p.):** diferença entre duas taxas percentuais.  
- **Média móvel (3 meses):** média da observação com as duas anteriores; suaviza oscilações.  
- **PIM-PF:** pesquisa da produção física industrial; não mede telemetria, OEE ou manutenção preditiva.""")

st.divider()
st.caption("Fonte: IBGE · Sistema SIDRA · Tabela 8888 · Brasil. Dados consultados quando o aplicativo executa ou atualiza a consulta.")
st.markdown(f"[Abrir a consulta JSON utilizada]({url}) · [Tabela 8888 no SIDRA](https://sidra.ibge.gov.br/tabela/8888)")
