"""Preparação de dados geográficos para gráficos do dashboard."""

from __future__ import annotations

import pandas as pd

from dashboard.config import COL_UF

LAT_COLUMN = "lat"
LON_COLUMN = "lon"
EXTERIOR_UFS = {"PT"}

UF_COORDS = {
    "AC": (-9.02, -70.81),
    "AL": (-9.57, -36.78),
    "AM": (-3.41, -65.85),
    "AP": (1.41, -51.60),
    "BA": (-12.97, -41.59),
    "CE": (-5.49, -39.32),
    "DF": (-15.82, -47.92),
    "ES": (-19.18, -40.30),
    "GO": (-15.82, -49.83),
    "MA": (-4.96, -45.27),
    "MT": (-12.68, -56.92),
    "MS": (-20.77, -54.78),
    "MG": (-18.51, -44.55),
    "PA": (-3.41, -52.05),
    "PB": (-7.23, -36.78),
    "PR": (-24.48, -51.86),
    "PE": (-8.81, -37.96),
    "PI": (-7.71, -42.72),
    "RJ": (-22.90, -43.17),
    "RN": (-5.79, -36.55),
    "RS": (-30.03, -51.21),
    "RO": (-11.50, -63.58),
    "RR": (2.73, -62.07),
    "SC": (-27.24, -50.21),
    "SP": (-22.90, -47.06),
    "SE": (-10.57, -37.38),
    "TO": (-10.17, -48.29),
    "PT": (38.7169, -9.1399),
}


def normalize_uf(df: pd.DataFrame, col_uf: str = COL_UF) -> pd.DataFrame:
    """Normaliza UF para caixa alta e remove espaços laterais."""

    normalized = df.copy()
    normalized[col_uf] = normalized[col_uf].astype(str).str.strip().str.upper()
    return normalized


def add_coordinates(df: pd.DataFrame, col_uf: str = COL_UF) -> pd.DataFrame:
    """Anexa latitude e longitude com base no mapeamento de UF."""

    enriched = df.copy()
    enriched[LAT_COLUMN] = enriched[col_uf].map(lambda uf: UF_COORDS.get(uf, (None, None))[0])
    enriched[LON_COLUMN] = enriched[col_uf].map(lambda uf: UF_COORDS.get(uf, (None, None))[1])
    return enriched


def prepare_geo_data(
    df: pd.DataFrame,
    col_uf: str = COL_UF,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separa dados geográficos entre Brasil e exterior."""

    enriched = add_coordinates(normalize_uf(df, col_uf=col_uf), col_uf=col_uf)
    valid_ufs = set(UF_COORDS.keys())

    df_brasil = enriched[enriched[col_uf].isin(valid_ufs - EXTERIOR_UFS)].copy()
    df_exterior = enriched[enriched[col_uf].isin(EXTERIOR_UFS)].copy()
    return df_brasil, df_exterior

