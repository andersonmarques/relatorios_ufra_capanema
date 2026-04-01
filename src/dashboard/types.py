"""Tipos de dados usados entre as camadas do dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DashboardFilters:
    """Representa os filtros selecionados no menu lateral."""

    anos: list[Any]
    ufs: list[Any]
    situacoes: list[Any]
    pos_graduacao: list[Any]


@dataclass(frozen=True)
class DashboardMetrics:
    """Representa os indicadores principais exibidos no topo do dashboard."""

    total_egressos: int
    total_empregados: int
    percentual_empregados: float
    total_atuando_na_area: int
    percentual_atuando_na_area: float
    tempo_medio_primeiro_emprego: float | None

