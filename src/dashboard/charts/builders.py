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
    COL_ATUACAO_AREA,
    COL_FAIXA_CONCLUSAO,
    COL_POS,
    COL_SETOR_TRABALHO,
    COL_SITUACAO_MERCADO,
    COL_UF,
    GRAPHICS_HEIGHT,
    LONG_LABEL_THRESHOLD,
    THEME_OPTIONS,
)
from dashboard.services.aggregations import (
    COL_QUANTIDADE,
    COL_PERCENTUAL,
    COL_ROTULO_PERCENTUAL,
    format_percent_label,
    sort_faixas_cronologicamente,
)
from dashboard.services.geo import LAT_COLUMN, LON_COLUMN

COL_CATEGORIA_SITUACAO_SETOR = "Categoria Situação/Setor"
COL_COMBINACAO_COMPLETA = "Situação | Setor | Atuação"
COL_APELIDO = "Apelido"
COL_ROTULO_ORIGINAL_LONGO = "Rótulo original"


def _finalize_figure(fig: Figure, theme_name: str, height: int) -> Figure:
    """Aplica layout base e tema de forma centralizada."""

    fig.update_layout(margin=CHART_MARGIN, height=height)
    return apply_plotly_theme(fig, theme_name)


def _index_to_alias(index: int) -> str:
    """Converte índice numérico em apelido alfabético (a, b, ..., aa)."""

    aliases: list[str] = []
    current = index
    while current > 0:
        current, remainder = divmod(current - 1, 26)
        aliases.append(chr(97 + remainder))
    return "".join(reversed(aliases))


def _alias_to_index(alias: str) -> int:
    """Converte apelido alfabético (a, b, ..., aa) para índice numérico."""

    value = 0
    for char in alias:
        value = value * 26 + (ord(char.lower()) - 96)
    return value


def gerar_mapeamento_rotulos(
    df: pd.DataFrame,
    coluna: str,
    limite_caracteres: int = LONG_LABEL_THRESHOLD,
) -> dict[str, str]:
    """Gera mapeamento de rótulos longos para apelidos curtos e únicos."""

    values = sorted(
        df[coluna]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .tolist()
    )
    mapping: dict[str, str] = {}
    alias_index = 1
    for value in values:
        if len(value) > limite_caracteres:
            mapping[value] = _index_to_alias(alias_index)
            alias_index += 1
    return mapping


def aplicar_apelidos_rotulos(
    df: pd.DataFrame,
    coluna: str,
    limite_caracteres: int = LONG_LABEL_THRESHOLD,
) -> tuple[pd.DataFrame, str, pd.DataFrame, list[str]]:
    """Aplica apelidos na coluna-alvo e retorna legenda de apoio."""

    mapping = gerar_mapeamento_rotulos(df, coluna, limite_caracteres=limite_caracteres)
    output = df.copy()
    display_column = f"{coluna} (apelido)"
    output[display_column] = output[coluna].astype(str).replace(mapping)

    apelidos_ordenados = sorted(mapping.values(), key=_alias_to_index)
    valores_sem_apelido = sorted(
        [
            value
            for value in output[display_column].dropna().astype(str).drop_duplicates().tolist()
            if value not in apelidos_ordenados
        ]
    )
    ordem_display = apelidos_ordenados + valores_sem_apelido
    output[display_column] = pd.Categorical(
        output[display_column],
        categories=ordem_display,
        ordered=True,
    )

    legend = pd.DataFrame(
        {
            COL_APELIDO: list(mapping.values()),
            COL_ROTULO_ORIGINAL_LONGO: list(mapping.keys()),
        }
    ).sort_values(by=COL_APELIDO, key=lambda col: col.map(_alias_to_index))
    legend = legend.reset_index(drop=True)

    return output, display_column, legend, ordem_display


def _prepare_market_bar_data(df: pd.DataFrame) -> pd.DataFrame:
    """Prepara base consolidada para gráficos simples de atuação."""

    required_columns = [COL_SITUACAO_MERCADO, COL_SETOR_TRABALHO, COL_ATUACAO_AREA]
    valid_rows = df[required_columns].dropna().copy()
    if valid_rows.empty:
        return pd.DataFrame(
            columns=[
                COL_SITUACAO_MERCADO,
                COL_SETOR_TRABALHO,
                COL_ATUACAO_AREA,
                COL_QUANTIDADE,
                COL_CATEGORIA_SITUACAO_SETOR,
                COL_COMBINACAO_COMPLETA,
            ]
        )

    grouped = (
        valid_rows.groupby(required_columns, sort=False, dropna=False)
        .size()
        .reset_index(name=COL_QUANTIDADE)
    )
    grouped[COL_CATEGORIA_SITUACAO_SETOR] = (
        grouped[COL_SITUACAO_MERCADO].astype(str) + " • " + grouped[COL_SETOR_TRABALHO].astype(str)
    )
    grouped[COL_COMBINACAO_COMPLETA] = (
        grouped[COL_SITUACAO_MERCADO].astype(str)
        + " | "
        + grouped[COL_SETOR_TRABALHO].astype(str)
        + " | "
        + grouped[COL_ATUACAO_AREA].astype(str)
    )
    return grouped


def _build_hierarchical_figure(
    df: pd.DataFrame,
    path: list[str],
    color: str,
    chart_type: str,
) -> Figure:
    """Cria figura hierárquica (treemap ou sunburst) com parâmetros comuns."""

    if chart_type == "treemap":
        return px.treemap(
            df,
            path=path,
            color=color,
            color_discrete_sequence=CHART_COLORS_BASE,
            title="",
        )
    if chart_type == "sunburst":
        return px.sunburst(
            df,
            path=path,
            color=color,
            color_discrete_sequence=CHART_COLORS_BASE,
            title="",
        )
    raise ValueError(f"Tipo de gráfico hierárquico inválido: {chart_type}")


def construir_figura_bar_empilhada(
    df: pd.DataFrame,
    theme_name: str,
    height: int = GRAPHICS_HEIGHT,
) -> tuple[Figure, pd.DataFrame]:
    """Constrói barras empilhadas (%) e retorna legenda de apelidos."""

    grouped = _prepare_market_bar_data(df)
    grouped, display_col, legend, ordem_display = aplicar_apelidos_rotulos(
        grouped,
        COL_CATEGORIA_SITUACAO_SETOR,
    )
    grouped = grouped.sort_values(by=display_col)
    totals = grouped.groupby(COL_CATEGORIA_SITUACAO_SETOR, sort=False)[COL_QUANTIDADE].transform("sum")
    grouped[COL_PERCENTUAL] = (grouped[COL_QUANTIDADE] / totals) * 100
    grouped[COL_ROTULO_PERCENTUAL] = grouped[COL_PERCENTUAL].apply(format_percent_label)

    fig = px.bar(
        grouped,
        x=display_col,
        y=COL_PERCENTUAL,
        color=COL_ATUACAO_AREA,
        barmode="stack",
        text=COL_ROTULO_PERCENTUAL,
        labels={COL_PERCENTUAL: "Percentual"},
        color_discrete_sequence=CHART_COLORS_BASE,
        category_orders={display_col: ordem_display},
        hover_data={
            COL_CATEGORIA_SITUACAO_SETOR: True,
            display_col: False,
        },
        title="",
    )
    fig.update_yaxes(range=[0, 110], title_text="Percentual")
    fig.update_xaxes(title_text="Situação e setor", tickangle=-30)

    fig = _finalize_figure(fig, theme_name, height)
    fig.update_traces(textposition="inside", selector=dict(type="bar"))
    return fig, legend


def construir_figura_bar_agrupada(
    df: pd.DataFrame,
    theme_name: str,
    height: int = GRAPHICS_HEIGHT,
) -> tuple[Figure, pd.DataFrame]:
    """Constrói barras agrupadas e retorna legenda de apelidos."""

    grouped = _prepare_market_bar_data(df)
    grouped, display_col, legend, ordem_display = aplicar_apelidos_rotulos(
        grouped,
        COL_CATEGORIA_SITUACAO_SETOR,
    )
    grouped = grouped.sort_values(by=display_col)
    fig = px.bar(
        grouped,
        x=display_col,
        y=COL_QUANTIDADE,
        color=COL_ATUACAO_AREA,
        barmode="group",
        text=COL_QUANTIDADE,
        labels={COL_QUANTIDADE: "Quantidade"},
        color_discrete_sequence=CHART_COLORS_BASE,
        category_orders={display_col: ordem_display},
        hover_data={
            COL_CATEGORIA_SITUACAO_SETOR: True,
            display_col: False,
        },
        title="",
    )
    fig.update_xaxes(title_text="Situação e setor", tickangle=-30)
    return _finalize_figure(fig, theme_name, height), legend


def construir_figura_bar_horizontal(
    df: pd.DataFrame,
    theme_name: str,
    height: int = GRAPHICS_HEIGHT,
) -> tuple[Figure, pd.DataFrame]:
    """Constrói barras horizontais e retorna legenda de apelidos."""

    grouped = _prepare_market_bar_data(df).sort_values(COL_QUANTIDADE, ascending=False).copy()
    grouped, display_col, legend, _ = aplicar_apelidos_rotulos(grouped, COL_COMBINACAO_COMPLETA)
    ordered_labels = grouped[display_col].tolist()
    dynamic_height = max(height, 70 + 26 * len(grouped.index))

    fig = px.bar(
        grouped,
        x=COL_QUANTIDADE,
        y=display_col,
        color=COL_ATUACAO_AREA,
        orientation="h",
        text=COL_QUANTIDADE,
        labels={
            COL_QUANTIDADE: "Quantidade",
            display_col: "Situação, setor e atuação",
        },
        color_discrete_sequence=CHART_COLORS_BASE,
        category_orders={display_col: list(reversed(ordered_labels))},
        hover_data={
            COL_COMBINACAO_COMPLETA: True,
            display_col: False,
        },
        title="",
    )
    fig.update_yaxes(title_text="Situação, setor e atuação")
    return _finalize_figure(fig, theme_name, dynamic_height), legend


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

    fig = _build_hierarchical_figure(
        df=df,
        path=path,
        color=color,
        chart_type="treemap",
    )
    return _finalize_figure(fig, theme_name, height)


def plot_sunburst(
    df: pd.DataFrame,
    path: list[str],
    color: str,
    theme_name: str,
    height: int = GRAPHICS_HEIGHT,
) -> Figure:
    """Gera sunburst para distribuição hierárquica."""

    fig = _build_hierarchical_figure(
        df=df,
        path=path,
        color=color,
        chart_type="sunburst",
    )
    return _finalize_figure(fig, theme_name, height)
