"""Cálculo dos KPIs exibidos no dashboard."""

from __future__ import annotations

import pandas as pd

from dashboard.config import COL_ATUACAO_AREA, COL_TEMPO_PRIMEIRO_EMPREGO, COL_TRABALHANDO
from dashboard.types import DashboardMetrics


def compute_metrics(df: pd.DataFrame) -> DashboardMetrics:
    """Calcula totais, percentuais e tempo médio até o primeiro emprego."""

    total = len(df)
    empregados = df[df[COL_TRABALHANDO] == "Sim"]
    na_area = empregados[empregados[COL_ATUACAO_AREA] == "Sim"]

    percentual_empregados = (len(empregados) / total * 100) if total else 0.0
    percentual_na_area = (len(na_area) / total * 100) if total else 0.0

    tempo_medio = pd.to_numeric(df[COL_TEMPO_PRIMEIRO_EMPREGO], errors="coerce").mean()
    tempo_medio_final = float(tempo_medio) if pd.notna(tempo_medio) else None

    return DashboardMetrics(
        total_egressos=total,
        total_empregados=len(empregados),
        percentual_empregados=percentual_empregados,
        total_atuando_na_area=len(na_area),
        percentual_atuando_na_area=percentual_na_area,
        tempo_medio_primeiro_emprego=tempo_medio_final,
    )

