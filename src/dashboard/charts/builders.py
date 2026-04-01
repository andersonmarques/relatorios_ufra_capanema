"""Builders reutilizáveis de gráficos Plotly."""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure

from dashboard.charts.theme import apply_plotly_theme
from dashboard.config import (
    CHART_COLOR_EXTERIOR,
    CHART_COLORS_BASE,
    CHART_COLORS_POS,
    CHART_MARGIN,
    COL_FAIXA_CONCLUSAO,
    COL_POS,
    COL_UF,
    GRAPHICS_HEIGHT,
    THEME_OPTIONS,
)
from dashboard.services.aggregations import (
    COL_PERCENTUAL,
    COL_ROTULO_PERCENTUAL,
    sort_faixas_cronologicamente,
)
from dashboard.services.geo import LAT_COLUMN, LON_COLUMN


def _finalize_figure(fig: Figure, theme_name: str, height: int) -> Figure:
    """Aplica layout base e tema de forma centralizada."""

    fig.update_layout(margin=CHART_MARGIN, height=height)
    return apply_plotly_theme(fig, theme_name)


def plot_bar_percent(
    df_percentual: pd.DataFrame,
    col_x: str,
    col_categoria: str,
    theme_name: str,
    height: int = GRAPHICS_HEIGHT,
    category_orders: dict[str, list[Any]] | None = None,
    color_discrete_sequence: list[str] | None = None,
) -> Figure:
    """Gera gráfico de barras com percentual por categoria."""

    kwargs: dict[str, Any] = {}
    if category_orders is not None:
        kwargs["category_orders"] = category_orders
    if color_discrete_sequence is not None:
        kwargs["color_discrete_sequence"] = color_discrete_sequence

    fig = px.bar(
        df_percentual,
        x=col_x,
        y=COL_PERCENTUAL,
        color=col_categoria,
        barmode="group",
        text=COL_ROTULO_PERCENTUAL,
        labels={COL_PERCENTUAL: "Percentual"},
        title="",
        **kwargs,
    )
    fig.update_yaxes(range=[0, 110], title_text="Percentual")
    return _finalize_figure(fig, theme_name, height)


def plot_pos_graduacao_por_faixa(
    df_percentual: pd.DataFrame,
    theme_name: str,
    height: int = GRAPHICS_HEIGHT,
) -> Figure:
    """Gera gráfico de pós-graduação por faixa de conclusão."""

    ordem_faixas = sort_faixas_cronologicamente(df_percentual[COL_FAIXA_CONCLUSAO])
    return plot_bar_percent(
        df_percentual=df_percentual,
        col_x=COL_FAIXA_CONCLUSAO,
        col_categoria=COL_POS,
        theme_name=theme_name,
        height=height,
        category_orders={COL_FAIXA_CONCLUSAO: ordem_faixas},
        color_discrete_sequence=CHART_COLORS_POS,
    )


def plot_geo(
    df_brasil: pd.DataFrame,
    df_exterior: pd.DataFrame,
    theme_name: str,
    col_uf: str = COL_UF,
    height: int = GRAPHICS_HEIGHT,
) -> Figure:
    """Gera mapa geográfico com destaque opcional para exterior."""

    fig = px.scatter_geo(
        df_brasil.dropna(subset=[LAT_COLUMN, LON_COLUMN]),
        lat=LAT_COLUMN,
        lon=LON_COLUMN,
        color=col_uf,
        hover_name=col_uf,
        scope="world",
        title="",
        color_discrete_sequence=CHART_COLORS_BASE,
    )

    if not df_exterior.empty:
        text_color = THEME_OPTIONS[theme_name]["text"]
        fig.add_scattergeo(
            lat=df_exterior[LAT_COLUMN],
            lon=df_exterior[LON_COLUMN],
            mode="markers+text",
            marker=dict(
                symbol="diamond",
                color=CHART_COLOR_EXTERIOR,
                line=dict(width=1, color=text_color),
            ),
            textposition="top center",
            name="Exterior",
        )

    fig.update_geos(showcountries=True, showland=True)
    return _finalize_figure(fig, theme_name, height)


def plot_treemap(
    df: pd.DataFrame,
    path: list[str],
    color: str,
    theme_name: str,
    height: int = GRAPHICS_HEIGHT,
) -> Figure:
    """Gera treemap para distribuição hierárquica."""

    fig = px.treemap(
        df,
        path=path,
        color=color,
        color_discrete_sequence=CHART_COLORS_BASE,
        title="",
    )
    return _finalize_figure(fig, theme_name, height)

