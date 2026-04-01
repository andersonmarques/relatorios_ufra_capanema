"""Testes unitários para filtros e KPIs."""

from __future__ import annotations

import sys
from pathlib import Path
import unittest

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dashboard.config import (  # noqa: E402
    COL_ANO,
    COL_ATUACAO_AREA,
    COL_POS,
    COL_TEMPO_PRIMEIRO_EMPREGO,
    COL_TRABALHANDO,
    COL_UF,
)
from dashboard.services.filters import apply_filters  # noqa: E402
from dashboard.services.metrics import compute_metrics  # noqa: E402
from dashboard.types import DashboardFilters  # noqa: E402


class FiltersAndMetricsTestCase(unittest.TestCase):
    """Valida regras de filtragem e cálculo de métricas."""

    def setUp(self) -> None:
        """Cria base sintética para os testes."""

        self.df = pd.DataFrame(
            {
                COL_ANO: [2020, 2021, 2022],
                COL_UF: ["PA", "PA", "SP"],
                COL_TRABALHANDO: ["Sim", "Não", "Sim"],
                COL_POS: ["Sim", "Não", "Cursando"],
                COL_ATUACAO_AREA: ["Sim", "Não", "Não"],
                COL_TEMPO_PRIMEIRO_EMPREGO: [2, None, 10],
            }
        )

    def test_apply_filters_returns_expected_subset(self) -> None:
        """Filtro combinado deve retornar somente linhas compatíveis."""

        filtros = DashboardFilters(
            anos=[2020, 2021],
            ufs=["PA"],
            situacoes=["Sim", "Não"],
            pos_graduacao=["Sim", "Não"],
        )
        filtered = apply_filters(self.df, filtros)

        self.assertEqual(len(filtered), 2)
        self.assertTrue((filtered[COL_UF] == "PA").all())
        self.assertTrue(filtered[COL_ANO].isin([2020, 2021]).all())

    def test_compute_metrics_handles_values_and_nulls(self) -> None:
        """Métricas devem refletir totais e tempo médio com nulos."""

        metrics = compute_metrics(self.df)
        self.assertEqual(metrics.total_egressos, 3)
        self.assertEqual(metrics.total_empregados, 2)
        self.assertEqual(metrics.total_atuando_na_area, 1)
        self.assertAlmostEqual(metrics.percentual_empregados, 66.6666, places=2)
        self.assertAlmostEqual(metrics.percentual_atuando_na_area, 33.3333, places=2)
        self.assertAlmostEqual(metrics.tempo_medio_primeiro_emprego or 0.0, 6.0, places=2)

    def test_compute_metrics_empty_dataframe(self) -> None:
        """Dataframe vazio não deve gerar divisão por zero."""

        empty = self.df.iloc[0:0].copy()
        metrics = compute_metrics(empty)

        self.assertEqual(metrics.total_egressos, 0)
        self.assertEqual(metrics.total_empregados, 0)
        self.assertEqual(metrics.total_atuando_na_area, 0)
        self.assertEqual(metrics.percentual_empregados, 0.0)
        self.assertEqual(metrics.percentual_atuando_na_area, 0.0)
        self.assertIsNone(metrics.tempo_medio_primeiro_emprego)


if __name__ == "__main__":
    unittest.main()

