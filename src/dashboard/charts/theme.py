"""Tema visual para Streamlit e Plotly."""

from __future__ import annotations

from plotly.graph_objects import Figure
import streamlit as st

from dashboard.config import THEME_OPTIONS, UFRA_VERDE


def get_theme() -> str:
    """Recupera o tema atual no session_state."""

    if "dashboard_theme" not in st.session_state:
        st.session_state["dashboard_theme"] = "dark"
    if "theme_toggle" not in st.session_state:
        st.session_state["theme_toggle"] = st.session_state["dashboard_theme"] == "dark"

    st.session_state["dashboard_theme"] = "dark" if st.session_state["theme_toggle"] else "light"
    return st.session_state["dashboard_theme"]


def render_theme_toggle() -> None:
    """Renderiza o controle de tema no final da barra lateral."""

    st.sidebar.markdown("---")
    st.sidebar.caption("Aparência do dashboard")
    st.sidebar.toggle("Tema escuro", key="theme_toggle")


def get_streamlit_css(theme_name: str) -> str:
    """Gera o CSS customizado da aplicação para o tema selecionado."""

    colors = THEME_OPTIONS[theme_name]
    return f"""
    <style>
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        .block-container {{padding-top: 0rem;}}
        [data-testid="stDeployButton"] {{display: none;}}

        .stApp {{
            background-color: {colors["app_bg"]};
            color: {colors["text"]};
        }}

        [data-testid="stSidebar"] {{
            min-width: 280px;
            max-width: 300px;
            background-color: {colors["sidebar_bg"]};
            border-right: 1px solid {colors["divider"]};
        }}

        [data-testid="stSidebar"] * {{
            color: {colors["text"]};
        }}

        [data-testid="stMetricLabel"] p,
        [data-testid="stMetricValue"] {{
            color: {colors["text"]} !important;
        }}

        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li,
        .stSubheader {{
            color: {colors["text"]};
        }}

        hr {{
            border-color: {colors["divider"]};
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
    """


def apply_streamlit_theme(theme_name: str) -> None:
    """Aplica o CSS customizado no layout Streamlit."""

    st.markdown(get_streamlit_css(theme_name), unsafe_allow_html=True)


def apply_plotly_theme(fig: Figure, theme_name: str) -> Figure:
    """Aplica identidade visual do tema em figuras Plotly."""

    colors = THEME_OPTIONS[theme_name]
    treemap_text_color = "#FFFFFF" if theme_name == "dark" else "#102A1A"

    fig.update_layout(
        plot_bgcolor=colors["plot_bg"],
        paper_bgcolor=colors["paper_bg"],
        font=dict(color=colors["text"]),
        legend=dict(
            font=dict(color=colors["text"]),
            title=dict(font=dict(color=colors["text"])),
            bgcolor=colors["legend_bg"],
        ),
        xaxis=dict(
            title_font=dict(color=colors["text"]),
            tickfont=dict(color=colors["text"]),
            gridcolor=colors["grid"],
            zerolinecolor=colors["grid"],
            linecolor=colors["axis_line"],
        ),
        yaxis=dict(
            title_font=dict(color=colors["text"]),
            tickfont=dict(color=colors["text"]),
            gridcolor=colors["grid"],
            zerolinecolor=colors["grid"],
            linecolor=colors["axis_line"],
        ),
        hoverlabel=dict(
            bgcolor=colors["paper_bg"],
            font=dict(color=colors["text"]),
        ),
    )

    fig.update_coloraxes(
        colorbar=dict(
            tickfont=dict(color=colors["text"]),
            title=dict(font=dict(color=colors["text"])),
            bgcolor=colors["paper_bg"],
        )
    )

    fig.update_traces(
        textposition="outside",
        textfont=dict(color=colors["text"]),
        cliponaxis=False,
        selector=dict(type="bar"),
    )
    fig.update_traces(
        textposition="outside",
        textfont=dict(color=colors["text"]),
        selector=dict(type="histogram"),
    )
    fig.update_traces(textfont=dict(color=treemap_text_color), selector=dict(type="treemap"))

    if any(getattr(trace, "type", "") in {"scattergeo", "choropleth"} for trace in fig.data):
        fig.update_geos(
            bgcolor=colors["plot_bg"],
            landcolor=colors["geo_land"],
            countrycolor=colors["geo_country"],
            coastlinecolor=colors["geo_country"],
            lakecolor=colors["plot_bg"],
        )

    return fig

