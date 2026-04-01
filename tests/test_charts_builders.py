"""Testes unitários para builders de gráficos."""

from __future__ import annotations

import sys
from pathlib import Path
import unittest

import pandas as pd
from plotly.graph_objects import Figure

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dashboard.charts.builders import (  # noqa: E402
    COL_APELIDO,
    COL_ROTULO_ORIGINAL_LONGO,
    aplicar_apelidos_rotulos,
    construir_figura_bar_agrupada,
    construir_figura_bar_empilhada,
    construir_figura_bar_horizontal,
    gerar_mapeamento_rotulos,
    plot_bar_percent,
    plot_geo,
    plot_pos_graduacao_por_faixa,
    plot_sunburst,
    plot_treemap,
)
from dashboard.config import (
    COL_ATUACAO_AREA,
    COL_FAIXA_CONCLUSAO,
    COL_POS,
    COL_SETOR_TRABALHO,
    COL_SITUACAO_MERCADO,
    COL_TRABALHANDO,
    COL_UF,
)
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
        self.df_atuacao = pd.DataFrame(
            {
                COL_SITUACAO_MERCADO: ["Servidor Público", "Servidor Público", "Empresário", "Empresário"],
                COL_SETOR_TRABALHO: ["Estatal", "Empresa Privada", "Empresa Própria", "Empresa Privada"],
                COL_ATUACAO_AREA: ["Sim", "Não", "Sim", "Não"],
                COL_TRABALHANDO: ["Sim", "Sim", "Sim", "Sim"],
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

    def test_plot_sunburst_returns_figure(self) -> None:
        """Builder de sunburst deve retornar figura com layout padrão."""

        df = pd.DataFrame(
            {
                "Situacao": ["Empregado"],
                "Setor": ["Privado"],
                "Atuacao": ["Sim"],
                COL_TRABALHANDO: ["Sim"],
            }
        )

        fig = plot_sunburst(
            df=df,
            path=["Situacao", "Setor", "Atuacao"],
            color=COL_TRABALHANDO,
            theme_name=self.theme_name,
        )
        self.assertIsInstance(fig, Figure)
        self.assertEqual(fig.layout.height, 300)

    def test_construir_figura_bar_empilhada_returns_figure(self) -> None:
        """Gráfico empilhado deve retornar figura e usar modo stack."""

        fig, legend = construir_figura_bar_empilhada(self.df_atuacao, self.theme_name)
        self.assertIsInstance(fig, Figure)
        self.assertIsInstance(legend, pd.DataFrame)
        self.assertEqual(fig.layout.height, 300)
        self.assertEqual(fig.layout.barmode, "stack")
        x_orders = list(fig.layout.xaxis.categoryarray or [])
        self.assertEqual(x_orders, sorted(x_orders))

    def test_construir_figura_bar_agrupada_returns_figure(self) -> None:
        """Gráfico agrupado deve retornar figura e usar modo group."""

        fig, legend = construir_figura_bar_agrupada(self.df_atuacao, self.theme_name)
        self.assertIsInstance(fig, Figure)
        self.assertIsInstance(legend, pd.DataFrame)
        self.assertEqual(fig.layout.height, 300)
        self.assertEqual(fig.layout.barmode, "group")

    def test_construir_figura_bar_horizontal_returns_figure(self) -> None:
        """Gráfico horizontal deve retornar figura com orientação horizontal."""

        fig, legend = construir_figura_bar_horizontal(self.df_atuacao, self.theme_name)
        self.assertIsInstance(fig, Figure)
        self.assertIsInstance(legend, pd.DataFrame)
        self.assertEqual(fig.layout.height, 300)
        self.assertTrue(all(trace.orientation == "h" for trace in fig.data))

    def test_gerar_mapeamento_rotulos_aplica_apenas_em_rotulos_longos(self) -> None:
        """Mapeamento deve criar apelidos só para rótulos acima do limite."""

        df = pd.DataFrame(
            {
                "descricao": [
                    "curto",
                    "Este é um rótulo extremamente longo para testar apelidos automáticos",
                ]
            }
        )
        mapping = gerar_mapeamento_rotulos(df, "descricao", limite_caracteres=20)

        self.assertEqual(len(mapping), 1)
        self.assertIn("Este é um rótulo extremamente longo para testar apelidos automáticos", mapping)
        self.assertEqual(mapping["Este é um rótulo extremamente longo para testar apelidos automáticos"], "a")

    def test_aplicar_apelidos_rotulos_retorna_legenda(self) -> None:
        """Aplicação de apelidos deve retornar coluna de exibição e legenda."""

        df = pd.DataFrame(
            {
                "descricao": [
                    "curto",
                    "Outro rótulo muito muito longo para virar apelido",
                ]
            }
        )
        transformed, display_col, legend, ordem_display = aplicar_apelidos_rotulos(
            df,
            "descricao",
            limite_caracteres=20,
        )

        self.assertIn(display_col, transformed.columns)
        self.assertIn(COL_APELIDO, legend.columns)
        self.assertIn(COL_ROTULO_ORIGINAL_LONGO, legend.columns)
        self.assertEqual(legend.iloc[0][COL_APELIDO], "a")
        self.assertEqual(ordem_display[0], "a")

    def test_construir_figura_bar_empilhada_forca_ordem_alfabetica_dos_apelidos(self) -> None:
        """Eixo X deve seguir a mesma ordem alfabética da legenda de apelidos."""

        df = pd.DataFrame(
            {
                COL_SITUACAO_MERCADO: [
                    "Situação de mercado com descrição muito longa C",
                    "Situação de mercado com descrição muito longa A",
                    "Situação de mercado com descrição muito longa B",
                ],
                COL_SETOR_TRABALHO: [
                    "Setor extremamente longo C",
                    "Setor extremamente longo A",
                    "Setor extremamente longo B",
                ],
                COL_ATUACAO_AREA: ["Sim", "Sim", "Sim"],
                COL_TRABALHANDO: ["Sim", "Sim", "Sim"],
            }
        )

        fig, legend = construir_figura_bar_empilhada(df, self.theme_name)
        category_array = list(fig.layout.xaxis.categoryarray or [])
        legend_aliases = legend[COL_APELIDO].tolist()

        self.assertEqual(category_array, legend_aliases)
        self.assertEqual(category_array, ["a", "b", "c"])


if __name__ == "__main__":
    unittest.main()
