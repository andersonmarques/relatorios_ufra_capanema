"""Testes unitários para builders de gráficos."""

from __future__ import annotations

import sys
from pathlib import Path
import unittest

import pandas as pd
from plotly.graph_objects import Figure

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dashboard.charts.builders import (  # noqa: E402
    plot_bar_percent,
    plot_geo,
    plot_pos_graduacao_por_faixa,
    plot_treemap,
)
from dashboard.config import COL_ATUACAO_AREA, COL_FAIXA_CONCLUSAO, COL_POS, COL_TRABALHANDO, COL_UF
from dashboard.services.aggregations import prepare_percentual
from dashboard.services.geo import LAT_COLUMN, LON_COLUMN


class ChartsBuildersTestCase(unittest.TestCase):
    """Valida consistência visual e tipos de retorno dos gráficos."""

    def setUp(self) -> None:
        """Monta datasets mínimos para os builders."""

        self.theme_name = "dark"
        self.df_percent = pd.DataFrame(
            {
                COL_TRABALHANDO: ["Sim", "Sim", "Não", "Não"],
                COL_ATUACAO_AREA: ["Sim", "Não", "Sim", "Não"],
            }
        )
        self.df_pos = pd.DataFrame(
            {
                COL_FAIXA_CONCLUSAO: ["2020-2024", "2020-2024", "2017-2019"],
                COL_POS: ["Sim", "Não", "Sim"],
            }
        )

    def test_plot_bar_percent_returns_figure_with_base_layout(self) -> None:
        """Builder de barras deve retornar figura com altura padronizada."""

        percentual = prepare_percentual(self.df_percent, COL_TRABALHANDO, COL_ATUACAO_AREA)
        fig = plot_bar_percent(
            df_percentual=percentual,
            col_x=COL_TRABALHANDO,
            col_categoria=COL_ATUACAO_AREA,
            theme_name=self.theme_name,
        )

        self.assertIsInstance(fig, Figure)
        self.assertEqual(fig.layout.height, 300)
        self.assertIn(fig.layout.yaxis.ticksuffix, (None, ""))

    def test_plot_pos_graduacao_por_faixa_returns_figure(self) -> None:
        """Builder de pós-graduação deve retornar figura válida."""

        percentual = prepare_percentual(self.df_pos, COL_FAIXA_CONCLUSAO, COL_POS)
        fig = plot_pos_graduacao_por_faixa(percentual, self.theme_name)
        self.assertIsInstance(fig, Figure)
        self.assertEqual(fig.layout.height, 300)

    def test_plot_geo_returns_figure_and_handles_exterior(self) -> None:
        """Builder de mapa deve montar figura mesmo com dados externos."""

        df_brasil = pd.DataFrame(
            {
                COL_UF: ["PA"],
                LAT_COLUMN: [-3.41],
                LON_COLUMN: [-52.05],
            }
        )
        df_exterior = pd.DataFrame(
            {
                COL_UF: ["PT"],
                LAT_COLUMN: [38.7169],
                LON_COLUMN: [-9.1399],
            }
        )

        fig = plot_geo(df_brasil=df_brasil, df_exterior=df_exterior, theme_name=self.theme_name)
        self.assertIsInstance(fig, Figure)
        self.assertGreaterEqual(len(fig.data), 1)

    def test_plot_treemap_returns_figure(self) -> None:
        """Builder de treemap deve retornar figura com layout padrão."""

        df = pd.DataFrame(
            {
                "Situacao": ["Empregado"],
                "Setor": ["Privado"],
                "Atuacao": ["Sim"],
                COL_TRABALHANDO: ["Sim"],
            }
        )

        fig = plot_treemap(
            df=df,
            path=["Situacao", "Setor", "Atuacao"],
            color=COL_TRABALHANDO,
            theme_name=self.theme_name,
        )
        self.assertIsInstance(fig, Figure)
        self.assertEqual(fig.layout.height, 300)


if __name__ == "__main__":
    unittest.main()

