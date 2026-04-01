"""Testes unitários para agregações percentuais."""

from __future__ import annotations

import sys
from pathlib import Path
import unittest

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dashboard.services.aggregations import (  # noqa: E402
    COL_PERCENTUAL,
    format_percent_label,
    prepare_percentual,
    sort_faixas_cronologicamente,
)


class AggregationsTestCase(unittest.TestCase):
    """Valida agregações e formatação percentual."""

    def test_format_percent_label_handles_integer_and_decimal(self) -> None:
        """Deve formatar inteiro sem decimal e decimal com vírgula."""

        self.assertEqual(format_percent_label(25.0), "25%")
        self.assertEqual(format_percent_label(25.54), "25,5%")

    def test_prepare_percentual_sum_is_approximately_100_by_group(self) -> None:
        """Soma dos percentuais por grupo de X deve totalizar 100%."""

        df = pd.DataFrame(
            {
                "x": ["A", "A", "A", "B", "B"],
                "categoria": ["Sim", "Não", "Sim", "Não", "Não"],
            }
        )
        grouped = prepare_percentual(df, "x", "categoria")

        totals = grouped.groupby("x")[COL_PERCENTUAL].sum().round(4)
        self.assertEqual(totals["A"], 100.0)
        self.assertEqual(totals["B"], 100.0)

    def test_sort_faixas_cronologicamente(self) -> None:
        """Faixas devem respeitar ordem cronológica pelo ano inicial."""

        series = pd.Series(["2020-2024", "2017-2019", "2014-2016"])
        ordered = sort_faixas_cronologicamente(series)
        self.assertEqual(ordered, ["2014-2016", "2017-2019", "2020-2024"])


if __name__ == "__main__":
    unittest.main()

