"""Aplicação Streamlit do dashboard de egressos."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from dashboard.charts.builders import (
    plot_bar_percent,
    plot_geo,
    plot_pos_graduacao_por_faixa,
    plot_treemap,
)
from dashboard.charts.theme import (
    apply_streamlit_theme,
    get_theme,
    render_theme_toggle,
)
from dashboard.config import (
    CHART_COLORS_POS,
    COL_ANO,
    COL_ATUACAO_AREA,
    COL_FAIXA_CONCLUSAO,
    COL_POS,
    COL_SETOR_TRABALHO,
    COL_SITUACAO_MERCADO,
    COL_TRABALHANDO,
    DATA_FILE_PATH,
    GRAPHICS_HEIGHT,
    PAGE_ICON,
    PAGE_LAYOUT,
    PAGE_SIDEBAR_STATE,
    PAGE_TITLE,
    THEME_OPTIONS,
    UFRA_VERDE,
)
from dashboard.services.aggregations import prepare_percentual
from dashboard.services.data_loader import DataLoadError, anonymize_export_dataframe, load_egressos_data
from dashboard.services.filters import apply_filters, build_filter_options
from dashboard.services.geo import prepare_geo_data
from dashboard.services.metrics import compute_metrics
from dashboard.types import DashboardFilters, DashboardMetrics


def _configure_page() -> None:
    """Aplica configuração inicial do Streamlit."""

    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=PAGE_LAYOUT,
        initial_sidebar_state=PAGE_SIDEBAR_STATE,
    )


@st.cache_data
def _load_data_cached(csv_path: str) -> pd.DataFrame:
    """Carrega e coloca em cache os dados de egressos."""

    return load_egressos_data(csv_path)


def _format_tempo_medio(tempo_medio: float | None) -> str:
    """Formata o tempo médio em meses para exibição no KPI (Key Performance Indicators)."""

    if tempo_medio is None:
        return "0,0 meses"
    return f"{tempo_medio:.1f} meses".replace(".", ",")


def _render_header(theme_name: str) -> None:
    """Renderiza cabeçalho principal do dashboard."""

    theme_colors = THEME_OPTIONS[theme_name]
    st.markdown(
        f"""
        <div style="
            background-color:{UFRA_VERDE};
            padding:8px 15px;
            border-radius:8px;
            text-align:center;
            border:1px solid {theme_colors["divider"]};
        ">
            <h3 style="color:{theme_colors["header_text"]};margin-bottom:2px;">
                Egressos de Engenharia Ambiental - UFRA Capanema
            </h3>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")


def _render_filters_sidebar(df: pd.DataFrame) -> DashboardFilters:
    """Renderiza filtros laterais e retorna seleção atual."""

    options = build_filter_options(df)
    st.sidebar.header("🔍 Filtros")

    anos = options["anos"]
    ufs = options["ufs"]
    situacoes = options["situacoes"]
    pos_graduacao = options["pos_graduacao"]

    filtro_ano = st.sidebar.multiselect("Ano de Conclusão", anos, default=anos)
    filtro_uf = st.sidebar.multiselect("UF", ufs, default=ufs)
    filtro_situacao = st.sidebar.multiselect("Situação Profissional", situacoes, default=situacoes)
    filtro_pos = st.sidebar.multiselect("Pós-Graduação", pos_graduacao, default=pos_graduacao)

    render_theme_toggle()

    return DashboardFilters(
        anos=filtro_ano,
        ufs=filtro_uf,
        situacoes=filtro_situacao,
        pos_graduacao=filtro_pos,
    )


def _render_metrics(metrics: DashboardMetrics) -> None:
    """Renderiza os KPIs principais do dashboard."""

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total de Egressos", f"{metrics.total_egressos}")
    col2.metric(
        "Empregados",
        f"{metrics.total_empregados} ({metrics.percentual_empregados:.0f}%)"
        if metrics.total_egressos
        else "0",
    )
    col3.metric(
        "Atuando na Área",
        f"{metrics.total_atuando_na_area} ({metrics.percentual_atuando_na_area:.0f}%)"
        if metrics.total_egressos
        else "0",
    )
    col4.metric(
        "Tempo Médio até o 1º Emprego",
        _format_tempo_medio(metrics.tempo_medio_primeiro_emprego),
    )

    st.markdown("---")


def _render_charts(df_filtered: pd.DataFrame, theme_name: str) -> None:
    """Renderiza a grade principal de visualizações."""

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("🗺️ Distribuição Geográfica dos Egressos")
        df_brasil, df_exterior = prepare_geo_data(df_filtered)
        fig_geo = plot_geo(
            df_brasil=df_brasil,
            df_exterior=df_exterior,
            theme_name=theme_name,
            height=GRAPHICS_HEIGHT,
        )
        st.plotly_chart(fig_geo, use_container_width=True, config={"displayModeBar": False})

    with col_g2:
        st.subheader("💼 Situação Profissional x Atuação na Área")
        dados_situacao_atuacao = prepare_percentual(
            df_filtered,
            COL_TRABALHANDO,
            COL_ATUACAO_AREA,
        )
        fig_bar = plot_bar_percent(
            df_percentual=dados_situacao_atuacao,
            col_x=COL_TRABALHANDO,
            col_categoria=COL_ATUACAO_AREA,
            theme_name=theme_name,
            height=GRAPHICS_HEIGHT,
            color_discrete_sequence=CHART_COLORS_POS,
        )
        st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})

    col_g3, col_g4 = st.columns(2)

    with col_g3:
        st.subheader("🌳 Atuação dos Egressos")
        fig_treemap = plot_treemap(
            df=df_filtered,
            path=[COL_SITUACAO_MERCADO, COL_SETOR_TRABALHO, COL_ATUACAO_AREA],
            color=COL_TRABALHANDO,
            theme_name=theme_name,
            height=GRAPHICS_HEIGHT,
        )
        st.plotly_chart(fig_treemap, use_container_width=True, config={"displayModeBar": False})

    with col_g4:
        st.subheader("🎓 Pós-Graduação por Faixa de Conclusão")
        dados_pos = prepare_percentual(df_filtered, COL_FAIXA_CONCLUSAO, COL_POS)
        fig_pos = plot_pos_graduacao_por_faixa(
            df_percentual=dados_pos,
            theme_name=theme_name,
            height=GRAPHICS_HEIGHT,
        )
        st.plotly_chart(fig_pos, use_container_width=True, config={"displayModeBar": False})


def _render_export(df_filtered: pd.DataFrame) -> None:
    """Renderiza botão de exportação anonimizada."""

    st.subheader("📤 Exportar dados filtrados (anonimizados)")
    df_export = anonymize_export_dataframe(df_filtered)
    csv_data = df_export.to_csv(index=False, encoding="utf-8-sig")

    st.download_button(
        label="Baixar CSV filtrado (anonimizado)",
        data=csv_data,
        file_name="egressos_anonimizados.csv",
        mime="text/csv",
    )


def _render_footer(theme_name: str) -> None:
    """Renderiza rodapé institucional."""

    theme_colors = THEME_OPTIONS[theme_name]
    st.markdown(
        f"""
        <div style="text-align:center;color:{theme_colors["muted_text"]};padding:15px;margin-top:30px;font-size:13px">
            <b>Universidade Federal Rural da Amazônia - Campus Capanema</b><br>
            <a
                href="https://labtec.ufra.edu.br/"
                target="_blank"
                rel="noopener noreferrer"
                style="color:{theme_colors["muted_text"]};font-weight:700;text-decoration:underline;"
            >
                Laboratório de Tecnologias Computacionais (LabTec)
            </a><br>
            Desenvolvido em Python com Streamlit e Plotly | © {pd.Timestamp.now().year}
        </div>
        """,
        unsafe_allow_html=True,
    )


def main(data_path: str | Path = DATA_FILE_PATH) -> None:
    """Executa a aplicação principal do dashboard."""

    _configure_page()
    theme_name = get_theme()
    apply_streamlit_theme(theme_name)
    _render_header(theme_name)

    try:
        df = _load_data_cached(str(data_path))
    except DataLoadError as error:
        st.error(f"Erro ao carregar o arquivo CSV: {error}")
        st.stop()

    filters = _render_filters_sidebar(df)
    df_filtered = apply_filters(df, filters)
    metrics = compute_metrics(df_filtered)

    _render_metrics(metrics)
    _render_charts(df_filtered, theme_name)
    _render_export(df_filtered)
    _render_footer(theme_name)
