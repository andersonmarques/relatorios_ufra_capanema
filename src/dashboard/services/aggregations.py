"""Agregações para gráficos e utilitários de formatação."""

from __future__ import annotations

import re
from typing import Any

import pandas as pd

COL_QUANTIDADE = "Quantidade"
COL_PERCENTUAL = "Percentual"
COL_ROTULO_PERCENTUAL = "Rotulo Percentual"


def format_percent_label(value: float) -> str:
    """Formata percentual para rótulo curto em pt-BR."""

    rounded = round(float(value), 1)
    if rounded.is_integer():
        return f"{int(rounded)}%"
    return f"{rounded:.1f}%".replace(".", ",")


def extract_start_year_from_range(value: Any) -> int | float:
    """Extrai o ano inicial de uma faixa textual."""

    match = re.search(r"\d{4}", str(value))
    return int(match.group()) if match else float("inf")


def sort_faixas_cronologicamente(series_faixas: pd.Series) -> list[Any]:
    """Ordena faixas de conclusão pela primeira ocorrência de ano na string."""

    unique_values = pd.Series(series_faixas).dropna().unique().tolist()
    return sorted(
        unique_values,
        key=lambda faixa: (extract_start_year_from_range(faixa), str(faixa)),
    )


def prepare_percentual(df: pd.DataFrame, col_x: str, col_categoria: str) -> pd.DataFrame:
    """Agrupa por duas colunas e calcula percentual dentro de cada valor de X."""

    required_columns = [col_x, col_categoria]
    valid_rows = df[required_columns].dropna().copy()
    if valid_rows.empty:
        return pd.DataFrame(
            columns=[
                col_x,
                col_categoria,
                COL_QUANTIDADE,
                COL_PERCENTUAL,
                COL_ROTULO_PERCENTUAL,
            ]
        )

    grouped = (
        valid_rows.groupby([col_x, col_categoria], sort=False, dropna=False)
        .size()
        .reset_index(name=COL_QUANTIDADE)
    )

    total_por_x = grouped.groupby(col_x, sort=False)[COL_QUANTIDADE].transform("sum")
    grouped[COL_PERCENTUAL] = (grouped[COL_QUANTIDADE] / total_por_x) * 100
    grouped[COL_ROTULO_PERCENTUAL] = grouped[COL_PERCENTUAL].apply(format_percent_label)
    return grouped

