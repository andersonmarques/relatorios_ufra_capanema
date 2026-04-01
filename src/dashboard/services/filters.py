"""Regras de filtragem e opções de filtros do dashboard."""

from __future__ import annotations

from typing import Any

import pandas as pd

from dashboard.config import COL_ANO, COL_POS, COL_TRABALHANDO, COL_UF
from dashboard.types import DashboardFilters


def _sorted_unique_values(series: pd.Series) -> list[Any]:
    """Retorna valores únicos não nulos ordenados de forma estável."""

    values = series.dropna().unique().tolist()
    try:
        return sorted(values)
    except TypeError:
        return sorted(values, key=lambda value: str(value))


def build_filter_options(df: pd.DataFrame) -> dict[str, list[Any]]:
    """Monta as opções exibidas nos filtros laterais."""

    return {
        "anos": _sorted_unique_values(df[COL_ANO]),
        "ufs": _sorted_unique_values(df[COL_UF]),
        "situacoes": _sorted_unique_values(df[COL_TRABALHANDO]),
        "pos_graduacao": _sorted_unique_values(df[COL_POS]),
    }


def apply_filters(df: pd.DataFrame, filters: DashboardFilters) -> pd.DataFrame:
    """Aplica os filtros selecionados e retorna o recorte resultante."""

    mask = (
        df[COL_ANO].isin(filters.anos)
        & df[COL_UF].isin(filters.ufs)
        & df[COL_TRABALHANDO].isin(filters.situacoes)
        & df[COL_POS].isin(filters.pos_graduacao)
    )
    return df[mask].copy()

