# ============================================================
# DASHBOARD UFRA - EGRESSOS ENGENHARIA AMBIENTAL
# ============================================================
# Autor: Prof. Anderson Soares
# Campus: UFRA - Capanema
# Descricao:
# Painel interativo para visualizacao de dados dos egressos,
# com filtros, graficos dinamicos e anonimização total.
# ============================================================

import os
import re
import pandas as pd
import streamlit as st
import plotly.express as px


# ------------------------------------------------------------
# 1. CONFIGURACOES INICIAIS
# ------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard de Egressos - UFRA Capanema",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Paleta institucional UFRA
UFRA_VERDE = "#006633"
UFRA_CINZA = "#F2F2F2"

# Nomes de colunas usados no dashboard
COL_NOME = "Nome Completo"
COL_ANO = "Ano de Saída/Conclusão do Curso"
COL_UF = "UF"
COL_TRABALHANDO = "Você está trabalhando?"
COL_ATUACAO_AREA = "O seu emprego é na área de formação?"
COL_POS = "Possui Pós-Graduação"
COL_FAIXA_CONCLUSAO = "Faixa de Conclusão"
COL_SITUACAO_MERCADO = "Qual a sua situação no mercado de trabalho?"
COL_SETOR_TRABALHO = "Qual o setor do seu trabalho?"
COL_TEMPO_PRIMEIRO_EMPREGO = (
    "Quanto tempo, em meses, demorou para conseguir o primeiro emprego após concluir o curso?"
)

THEME_OPTIONS = {
    "dark": {
        "app_bg": "#0E1117",
        "sidebar_bg": "#111111",
        "text": "#F5F5F5",
        "muted_text": "#B8BEC5",
        "divider": "#2B3138",
        "plot_bg": "#111111",
        "paper_bg": "#111111",
        "grid": "#3A3A3A",
        "axis_line": "#4B5563",
        "legend_bg": "rgba(17, 17, 17, 0.70)",
        "geo_land": "#1A1A1A",
        "geo_country": "#6B7280",
        "header_text": "#FFFFFF",
    },
    "light": {
        "app_bg": "#FFFFFF",
        "sidebar_bg": UFRA_CINZA,
        "text": "#1F2933",
        "muted_text": "#5C6670",
        "divider": "#D8DEE5",
        "plot_bg": "#FFFFFF",
        "paper_bg": "#FFFFFF",
        "grid": "#D8DEE5",
        "axis_line": "#AAB4BE",
        "legend_bg": "rgba(255, 255, 255, 0.90)",
        "geo_land": "#EEF2F4",
        "geo_country": "#8C98A4",
        "header_text": "#FFFFFF",
    },
}


def get_theme():
    if "dashboard_theme" not in st.session_state:
        st.session_state["dashboard_theme"] = "dark"
    if "theme_toggle" not in st.session_state:
        st.session_state["theme_toggle"] = st.session_state["dashboard_theme"] == "dark"

    st.session_state["dashboard_theme"] = "dark" if st.session_state["theme_toggle"] else "light"
    return st.session_state["dashboard_theme"]


def apply_streamlit_theme(theme):
    cores = THEME_OPTIONS[theme]
    st.markdown(
        f"""
        <style>
            #MainMenu {{visibility: hidden;}}
            footer {{visibility: hidden;}}
            header {{visibility: hidden;}}
            .block-container {{padding-top: 0rem;}}
            [data-testid="stDeployButton"] {{display: none;}}

            .stApp {{
                background-color: {cores["app_bg"]};
                color: {cores["text"]};
            }}

            [data-testid="stSidebar"] {{
                min-width: 280px;
                max-width: 300px;
                background-color: {cores["sidebar_bg"]};
                border-right: 1px solid {cores["divider"]};
            }}

            [data-testid="stSidebar"] * {{
                color: {cores["text"]};
            }}

            [data-testid="stMetricLabel"] p,
            [data-testid="stMetricValue"] {{
                color: {cores["text"]} !important;
            }}

            [data-testid="stMarkdownContainer"] p,
            [data-testid="stMarkdownContainer"] li,
            .stSubheader {{
                color: {cores["text"]};
            }}

            hr {{
                border-color: {cores["divider"]};
            }}

            .stDownloadButton button {{
                background-color: {UFRA_VERDE};
                color: #FFFFFF;
                border: 1px solid {UFRA_VERDE};
            }}

            .stDownloadButton button:hover {{
                background-color: #005529;
                color: #FFFFFF;
                border: 1px solid #005529;
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_plotly_theme(fig, theme):
    cores = THEME_OPTIONS[theme]
    treemap_text_color = "#FFFFFF" if theme == "dark" else "#102A1A"

    fig.update_layout(
        plot_bgcolor=cores["plot_bg"],
        paper_bgcolor=cores["paper_bg"],
        font=dict(color=cores["text"]),
        legend=dict(
            font=dict(color=cores["text"]),
            title=dict(font=dict(color=cores["text"])),
            bgcolor=cores["legend_bg"],
        ),
        xaxis=dict(
            title_font=dict(color=cores["text"]),
            tickfont=dict(color=cores["text"]),
            gridcolor=cores["grid"],
            zerolinecolor=cores["grid"],
            linecolor=cores["axis_line"],
        ),
        yaxis=dict(
            title_font=dict(color=cores["text"]),
            tickfont=dict(color=cores["text"]),
            gridcolor=cores["grid"],
            zerolinecolor=cores["grid"],
            linecolor=cores["axis_line"],
        ),
        hoverlabel=dict(
            bgcolor=cores["paper_bg"],
            font=dict(color=cores["text"]),
        ),
    )

    fig.update_coloraxes(
        colorbar=dict(
            tickfont=dict(color=cores["text"]),
            title=dict(font=dict(color=cores["text"])),
            bgcolor=cores["paper_bg"],
        )
    )

    # Mantem labels text_auto legiveis em ambos os temas.
    fig.update_traces(
        textposition="outside",
        textfont=dict(color=cores["text"]),
        cliponaxis=False,
        selector=dict(type="bar"),
    )
    fig.update_traces(
        textposition="outside",
        textfont=dict(color=cores["text"]),
        selector=dict(type="histogram"),
    )
    fig.update_traces(textfont=dict(color=treemap_text_color), selector=dict(type="treemap"))

    if any(getattr(trace, "type", "") in {"scattergeo", "choropleth"} for trace in fig.data):
        fig.update_geos(
            bgcolor=cores["plot_bg"],
            landcolor=cores["geo_land"],
            countrycolor=cores["geo_country"],
            coastlinecolor=cores["geo_country"],
            lakecolor=cores["plot_bg"],
        )

    return fig


def render_theme_toggle():
    st.sidebar.markdown("---")
    st.sidebar.caption("Aparência do dashboard")
    st.sidebar.toggle("Tema escuro", key="theme_toggle")


# ------------------------------------------------------------
# 2. IMPORTACAO DOS DADOS
# ------------------------------------------------------------
@st.cache_data
def carregar_dados():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "../database/egressos_limpo.csv")

    try:
        df = pd.read_csv(file_path, encoding="utf-8-sig", sep=",")
    except Exception:
        try:
            df = pd.read_csv(file_path, encoding="utf-8-sig", sep=";")
        except Exception as erro:
            st.error(f"Erro ao carregar o arquivo CSV: {erro}")
            st.stop()

    df = df.drop(columns=[COL_NOME], errors="ignore")
    return df


# ------------------------------------------------------------
# Funcoes auxiliares - Pos-Graduacao por faixa de conclusao
# ------------------------------------------------------------
def formatar_percentual_rotulo(valor):
    valor = round(float(valor), 1)
    if valor.is_integer():
        return f"{int(valor)}%"
    return f"{valor:.1f}%".replace(".", ",")


def extrair_ano_inicial_faixa(faixa):
    correspondencia = re.search(r"\d{4}", str(faixa))
    return int(correspondencia.group()) if correspondencia else float("inf")


def obter_ordem_cronologica_faixas(series_faixas):
    faixas_unicas = pd.Series(series_faixas).dropna().unique().tolist()
    return sorted(faixas_unicas, key=lambda faixa: (extrair_ano_inicial_faixa(faixa), str(faixa)))


def preparar_dados_pos_graduacao_por_faixa(df_base):
    dados_validos = df_base[[COL_FAIXA_CONCLUSAO, COL_POS]].dropna().copy()
    if dados_validos.empty:
        return pd.DataFrame(
            columns=[COL_FAIXA_CONCLUSAO, COL_POS, "Quantidade", "Percentual", "Rótulo Percentual"]
        )

    dados_agrupados = (
        dados_validos
        .groupby([COL_FAIXA_CONCLUSAO, COL_POS], sort=False, dropna=False)
        .size()
        .reset_index(name="Quantidade")
    )
    totais_por_faixa = dados_agrupados.groupby(COL_FAIXA_CONCLUSAO, sort=False)["Quantidade"].transform("sum")
    dados_agrupados["Percentual"] = (dados_agrupados["Quantidade"] / totais_por_faixa) * 100
    dados_agrupados["Rótulo Percentual"] = dados_agrupados["Percentual"].apply(formatar_percentual_rotulo)
    return dados_agrupados


def construir_figura_pos_graduacao_por_faixa(df_pos_agrupado, altura, tema):
    ordem_faixas = obter_ordem_cronologica_faixas(df_pos_agrupado[COL_FAIXA_CONCLUSAO])
    fig_pg = px.bar(
        df_pos_agrupado,
        x=COL_FAIXA_CONCLUSAO,
        y="Percentual",
        color=COL_POS,
        barmode="group",
        text="Rótulo Percentual",
        labels={"Percentual": "Percentual (%)"},
        category_orders={COL_FAIXA_CONCLUSAO: ordem_faixas},
        color_discrete_sequence=[UFRA_VERDE, "#A5CFA3", "#D0E6C8"],
        title="",
    )
    fig_pg.update_yaxes(range=[0, 110], ticksuffix="%")
    fig_pg.update_layout(margin=dict(l=0, r=0, t=20, b=0), height=altura)
    return apply_plotly_theme(fig_pg, tema)


THEME = get_theme()
THEME_COLORS = THEME_OPTIONS[THEME]
apply_streamlit_theme(THEME)

df = carregar_dados()

# ------------------------------------------------------------
# 3. LAYOUT - CABECALHO
# ------------------------------------------------------------
st.markdown(
    f"""
    <div style="
        background-color:{UFRA_VERDE};
        padding:8px 15px;
        border-radius:8px;
        text-align:center;
        border:1px solid {THEME_COLORS["divider"]};
    ">
        <h3 style="color:{THEME_COLORS["header_text"]};margin-bottom:2px;">
            Egressos de Engenharia Ambiental - UFRA Capanema
        </h3>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

# ------------------------------------------------------------
# 4. FILTROS LATERAIS
# ------------------------------------------------------------
st.sidebar.header("🔍 Filtros")

anos = sorted(df[COL_ANO].dropna().unique())
ufs = sorted(df[COL_UF].dropna().unique())
situacoes = sorted(df[COL_TRABALHANDO].dropna().unique())
pos_graduacao = sorted(df[COL_POS].dropna().unique())

filtro_ano = st.sidebar.multiselect("Ano de Conclusão", anos, default=anos)
filtro_uf = st.sidebar.multiselect("UF", ufs, default=ufs)
filtro_situacao = st.sidebar.multiselect("Situação Profissional", situacoes, default=situacoes)
filtro_pos = st.sidebar.multiselect("Pós-Graduação", pos_graduacao, default=pos_graduacao)

# Toggle no final do menu lateral
render_theme_toggle()

df_filtro = df[
    (df[COL_ANO].isin(filtro_ano))
    & (df[COL_UF].isin(filtro_uf))
    & (df[COL_TRABALHANDO].isin(filtro_situacao))
    & (df[COL_POS].isin(filtro_pos))
].copy()

# ------------------------------------------------------------
# 5. KPIs - INDICADORES PRINCIPAIS
# ------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
total = len(df_filtro)
empregados = df_filtro[df_filtro[COL_TRABALHANDO] == "Sim"]
na_area = empregados[empregados[COL_ATUACAO_AREA] == "Sim"]
tempo_medio = df_filtro[COL_TEMPO_PRIMEIRO_EMPREGO].mean()

tempo_medio_label = f"{tempo_medio:.1f} meses" if pd.notna(tempo_medio) else "0,0 meses"

col1.metric("Total de Egressos", f"{total}")
col2.metric("Empregados", f"{len(empregados)} ({len(empregados) / total * 100:.0f}%)" if total else "0")
col3.metric("Atuando na Área", f"{len(na_area)} ({len(na_area) / total * 100:.0f}%)" if total else "0")
col4.metric("Tempo Médio até o 1º Emprego", tempo_medio_label)

st.markdown("---")

# ------------------------------------------------------------
# 6. VISUALIZACOES PRINCIPAIS (layout 2x2)
# ------------------------------------------------------------
col_g1, col_g2 = st.columns(2)
GRAPHICS_HEIGHT = 300

with col_g1:
    st.subheader("🗺️ Distribuição Geográfica dos Egressos")

    df_filtro[COL_UF] = df_filtro[COL_UF].astype(str).str.strip().str.upper()

    coords = {
        "AC": [-9.02, -70.81], "AL": [-9.57, -36.78], "AM": [-3.41, -65.85],
        "AP": [1.41, -51.60], "BA": [-12.97, -41.59], "CE": [-5.49, -39.32],
        "DF": [-15.82, -47.92], "ES": [-19.18, -40.30], "GO": [-15.82, -49.83],
        "MA": [-4.96, -45.27], "MT": [-12.68, -56.92], "MS": [-20.77, -54.78],
        "MG": [-18.51, -44.55], "PA": [-3.41, -52.05], "PB": [-7.23, -36.78],
        "PR": [-24.48, -51.86], "PE": [-8.81, -37.96], "PI": [-7.71, -42.72],
        "RJ": [-22.90, -43.17], "RN": [-5.79, -36.55], "RS": [-30.03, -51.21],
        "RO": [-11.50, -63.58], "RR": [2.73, -62.07], "SC": [-27.24, -50.21],
        "SP": [-22.90, -47.06], "SE": [-10.57, -37.38], "TO": [-10.17, -48.29],
        "PT": [38.7169, -9.1399],
    }

    df_filtro["lat"] = df_filtro[COL_UF].apply(lambda uf: coords.get(uf, [None, None])[0])
    df_filtro["lon"] = df_filtro[COL_UF].apply(lambda uf: coords.get(uf, [None, None])[1])

    df_brasil = df_filtro[df_filtro[COL_UF].isin(coords.keys()) & (df_filtro[COL_UF] != "PT")]
    df_exterior = df_filtro[df_filtro[COL_UF] == "PT"]

    fig_geo = px.scatter_geo(
        df_brasil.dropna(subset=["lat", "lon"]),
        lat="lat",
        lon="lon",
        color=COL_UF,
        hover_name=COL_UF,
        scope="world",
        title="",
        color_discrete_sequence=[UFRA_VERDE, "#94C973", "#B5DCC2"],
    )

    if not df_exterior.empty:
        fig_geo.add_scattergeo(
            lat=df_exterior["lat"],
            lon=df_exterior["lon"],
            mode="markers+text",
            marker=dict(
                symbol="diamond",
                color="#FFD700",
                line=dict(width=1, color=THEME_COLORS["text"]),
            ),
            textposition="top center",
            name="Exterior",
        )

    fig_geo.update_geos(showcountries=True, showland=True)
    fig_geo.update_layout(margin=dict(l=0, r=0, t=20, b=0), height=GRAPHICS_HEIGHT)
    fig_geo = apply_plotly_theme(fig_geo, THEME)

    st.plotly_chart(fig_geo, use_container_width=True, config={"displayModeBar": False})

with col_g2:
    st.subheader("💼 Situação Profissional x Atuação na Área")
    fig_bar = px.histogram(
        df_filtro,
        x=COL_TRABALHANDO,
        color=COL_ATUACAO_AREA,
        barmode="group",
        text_auto=True,
        color_discrete_sequence=[UFRA_VERDE, "#94C973"],
        title="",
    )
    fig_bar.update_layout(margin=dict(l=0, r=0, t=20, b=0), height=GRAPHICS_HEIGHT)
    fig_bar = apply_plotly_theme(fig_bar, THEME)
    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

col_g3, col_g4 = st.columns(2)

with col_g3:
    st.subheader("🌳 Atuação dos Egressos")
    fig_treemap = px.treemap(
        df_filtro,
        path=[COL_SITUACAO_MERCADO, COL_SETOR_TRABALHO, COL_ATUACAO_AREA],
        color=COL_TRABALHANDO,
        color_discrete_sequence=[UFRA_VERDE, "#94C973", "#B5DCC2"],
        title="",
    )
    fig_treemap.update_layout(margin=dict(l=0, r=0, t=20, b=0), height=GRAPHICS_HEIGHT)
    fig_treemap = apply_plotly_theme(fig_treemap, THEME)
    st.plotly_chart(fig_treemap, use_container_width=True, config={"displayModeBar": False})

with col_g4:
    st.subheader("🎓 Pós-Graduação por Faixa de Conclusão")
    dados_pos_agrupados = preparar_dados_pos_graduacao_por_faixa(df_filtro)
    fig_pg = construir_figura_pos_graduacao_por_faixa(dados_pos_agrupados, GRAPHICS_HEIGHT, THEME)
    st.plotly_chart(fig_pg, use_container_width=True, config={"displayModeBar": False})


# ------------------------------------------------------------
# 7. EXPORTACAO SEGURA (SEM NOMES)
# ------------------------------------------------------------
st.subheader("📤 Exportar dados filtrados (anonimizados)")
df_export = df_filtro.drop(columns=["E-mail"], errors="ignore")
csv = df_export.to_csv(index=False, encoding="utf-8-sig")

st.download_button(
    label="Baixar CSV filtrado (anonimizado)",
    data=csv,
    file_name="egressos_anonimizados.csv",
    mime="text/csv",
)

# ------------------------------------------------------------
# 8. RODAPE
# ------------------------------------------------------------
st.markdown(
    f"""
    <div style="text-align:center;color:{THEME_COLORS["muted_text"]};padding:15px;margin-top:30px;font-size:13px">
        <b>Universidade Federal Rural da Amazônia - Campus Capanema</b><br>
        Desenvolvido em Python com Streamlit e Plotly | © {pd.Timestamp.now().year}
    </div>
    """,
    unsafe_allow_html=True,
)
