# ============================================================
# DASHBOARD UFRA - EGRESSOS ENGENHARIA AMBIENTAL
# ============================================================
# Autor: Prof. Anderson Soares
# Campus: UFRA - Capanema
# Descrição:
# Painel interativo para visualização de dados dos egressos,
# com filtros, gráficos dinâmicos e anonimização total.
# ============================================================

import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.io as pio

# ------------------------------------------------------------
# 1. CONFIGURAÇÕES INICIAIS
# ------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard de Egressos - UFRA Capanema",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            min-width: 280px;
            max-width: 300px;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# Remover botão Deploy, menus e espaço superior
# ------------------------------------------------------------
custom_style = """
    <style>
        /* Remove menu do Streamlit (Deploy, Settings, etc.) */
        #MainMenu {visibility: hidden;}
        
        /* Remove rodapé padrão "Made with Streamlit" */
        footer {visibility: hidden;}
        
        /* Remove a barra superior branca */
        header {visibility: hidden;}
        
        /* Remove o espaço superior antes do cabeçalho */
        .block-container {padding-top: 0rem;}
        
        /* Remove apenas o botão Deploy (caso apareça isolado) */
        [data-testid="stDeployButton"] {display: none;}
    </style>
"""
st.markdown(custom_style, unsafe_allow_html=True)

# ------------------------------------------------------------

# pio.templates.default = "plotly_dark"
# Paleta institucional UFRA
UFRA_VERDE = "#006633"
UFRA_CINZA = "#F2F2F2"

# ------------------------------------------------------------
# 2. IMPORTAÇÃO DOS DADOS
# ------------------------------------------------------------
@st.cache_data
def carregar_dados():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "../database/egressos_limpo.csv")

    try:
        # Tenta leitura com diferentes separadores e codificações
        df = pd.read_csv(file_path, encoding="utf-8-sig", sep=",")
    except Exception:
        try:
            df = pd.read_csv(file_path, encoding="utf-8-sig", sep=";")
        except Exception as e:
            st.error(f"Erro ao carregar o arquivo CSV: {e}")
            st.stop()

    # Remover colunas sensíveis
    df = df.drop(columns=["Nome Completo"], errors="ignore")
    return df

df = carregar_dados()

# ------------------------------------------------------------
# 3. LAYOUT - CABEÇALHO
# ------------------------------------------------------------

st.markdown(f"""
    <div style="
        background-color:{UFRA_VERDE};
        padding:8px 15px;
        border-radius:8px;
        text-align:center;
    ">
        <h3 style="color:white;margin-bottom:2px;">
            Egressos de Engenharia Ambiental – UFRA Capanema
        </h3>
        <!--<p style="color:#cccccc;font-size:14px;">Painel de acompanhamento</p>-->
    </div>
""", unsafe_allow_html=True)

st.write("")

# ------------------------------------------------------------
# 4. FILTROS LATERAIS
# ------------------------------------------------------------
st.sidebar.header("🔍 Filtros")

anos = sorted(df["Ano de Saída/Conclusão do Curso"].unique())
ufs = sorted(df["UF"].unique())
situacoes = sorted(df["Você está trabalhando?"].unique())
pos_graduacao = sorted(df["Possui Pós-Graduação"].unique())

filtro_ano = st.sidebar.multiselect("Ano de Conclusão", anos, default=anos)
filtro_uf = st.sidebar.multiselect("UF", ufs, default=ufs)
filtro_situacao = st.sidebar.multiselect("Situação Profissional", situacoes, default=situacoes)
filtro_pos = st.sidebar.multiselect("Pós-Graduação", pos_graduacao, default=pos_graduacao)

# Aplicar filtros
df_filtro = df[
    (df["Ano de Saída/Conclusão do Curso"].isin(filtro_ano)) &
    (df["UF"].isin(filtro_uf)) &
    (df["Você está trabalhando?"].isin(filtro_situacao)) &
    (df["Possui Pós-Graduação"].isin(filtro_pos))
]

# ------------------------------------------------------------
# 5. KPIs - INDICADORES PRINCIPAIS
# ------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
total = len(df_filtro)
empregados = df_filtro[df_filtro["Você está trabalhando?"] == "Sim"]
na_area = empregados[empregados["O seu emprego é na área de formação?"] == "Sim"]
pos = df_filtro[df_filtro["Possui Pós-Graduação"].isin(["Sim", "Cursando"])]
tempo_medio = df_filtro["Quanto tempo, em meses, demorou para conseguir o primeiro emprego após concluir o curso?"].mean()

col1.metric("Total de Egressos", f"{total}")
col2.metric("Empregados", f"{len(empregados)} ({len(empregados)/total*100:.0f}%)" if total else "0")
col3.metric("Atuando na Área", f"{len(na_area)} ({len(na_area)/total*100:.0f}%)" if total else "0")
col4.metric("Tempo Médio até o 1º Emprego", f"{tempo_medio:.1f} meses")

st.markdown("---")
# ------------------------------------------------------------
# 6. VISUALIZAÇÕES PRINCIPAIS (em layout 2x2)
# ------------------------------------------------------------

# # Linha 1: Mapa + Situação Profissional
col1, col2 = st.columns(2)
GRAPHICS_HEIGHT = 300

with col1:
    st.subheader("🗺️ Distribuição Geográfica dos Egressos")

    # Normalizar valores da coluna UF
    df_filtro["UF"] = df_filtro["UF"].astype(str).str.strip().str.upper()

    # Dicionário de coordenadas (UFs e países)
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
        "PT": [38.7169, -9.1399],  # Portugal 🇵🇹
    }

    # Adicionar colunas de coordenadas
    df_filtro["lat"] = df_filtro["UF"].apply(lambda x: coords.get(x, [None, None])[0])
    df_filtro["lon"] = df_filtro["UF"].apply(lambda x: coords.get(x, [None, None])[1])

    # Separar Brasil e Exterior
    df_brasil = df_filtro[df_filtro["UF"].isin(coords.keys()) & (df_filtro["UF"] != "PT")]
    df_exterior = df_filtro[df_filtro["UF"] == "PT"]

    # Criar mapa base (Brasil + exterior)
    fig = px.scatter_geo(
        df_brasil.dropna(subset=["lat", "lon"]),
        lat="lat",
        lon="lon",
        color="UF",
        hover_name="UF",
        scope="world",
        title="",
        color_discrete_sequence=[UFRA_VERDE, "#94C973", "#B5DCC2"],
    )

    # Egresso internacional (Portugal)
    if not df_exterior.empty:
        fig.add_scattergeo(
            lat=df_exterior["lat"],
            lon=df_exterior["lon"],
            mode="markers+text",
            marker=dict(
                # size=6,
                symbol= "diamond",
                color="#FFD700",  # dourado
                line=dict(width=1, color="white")
            ),
            # text=["🌍 Egresso Internacional (Portugal)"],
            textposition="top center",
            name="Exterior",
        )

    # Ajustes de layout
    fig.update_geos(
        showcountries=True,
        showland=True,
        landcolor="#0D0D0D",
        countrycolor="gray",
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=20, b=0),
        height=GRAPHICS_HEIGHT,
        geo=dict(bgcolor="#111111"),
        paper_bgcolor="#111111",
        plot_bgcolor="#111111",
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col2:
    st.subheader("💼 Situação Profissional x Atuação na Área")
    fig_bar = px.histogram(
        df_filtro,
        x="Você está trabalhando?",
        color="O seu emprego é na área de formação?",
        barmode="group",
        text_auto=True,
        color_discrete_sequence=[UFRA_VERDE, "#94C973"],
        title=""
    )
    fig_bar.update_layout(
        margin=dict(l=0, r=0, t=20, b=0),
        height=GRAPHICS_HEIGHT,
        plot_bgcolor="#111111",
        paper_bgcolor='#111111'
    )
    st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

# Linha 2: Treemap + Pós-Graduação
col3, col4 = st.columns(2)

with col3:
    st.subheader("🌳 Atuação dos Egressos")
    fig_treemap = px.treemap(
        df_filtro,
        path=[
            "Qual a sua situação no mercado de trabalho?",
            "Qual o setor do seu trabalho?",
            "O seu emprego é na área de formação?",
        ],
        color="Você está trabalhando?",
        color_discrete_sequence=[UFRA_VERDE, "#94C973", "#B5DCC2"],
        title=""
    )
    fig_treemap.update_layout(
        margin=dict(l=0, r=0, t=20, b=0),
        height=GRAPHICS_HEIGHT,
        paper_bgcolor='#111111'
    )
    st.plotly_chart(fig_treemap, use_container_width=True, config={'displayModeBar': False})

with col4:
    st.subheader("🎓 Pós-Graduação por Faixa de Conclusão")
    fig_pg = px.histogram(
        df_filtro,
        x="Faixa de Conclusão",
        color="Possui Pós-Graduação",
        barmode="group",
        text_auto=True,
        color_discrete_sequence=[UFRA_VERDE, "#A5CFA3", "#D0E6C8"],
        title=""
    )
    fig_pg.update_layout(
        margin=dict(l=0, r=0, t=20, b=0),
        height=GRAPHICS_HEIGHT,
        plot_bgcolor="#111111",
        paper_bgcolor='#111111'
    )
    st.plotly_chart(fig_pg, use_container_width=True, config={'displayModeBar': False})


# ------------------------------------------------------------
# 7. EXPORTAÇÃO SEGURA (SEM NOMES)
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
# 8. RODAPÉ
# ------------------------------------------------------------
st.markdown(f"""
    <div style="text-align:center;color:gray;padding:15px;margin-top:30px;font-size:13px">
        <b>Universidade Federal Rural da Amazônia - Campus Capanema</b><br>
        Desenvolvido em Python com Streamlit e Plotly | © {pd.Timestamp.now().year}
    </div>
""", unsafe_allow_html=True)
