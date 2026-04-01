"""Leitura e anonimização da base de egressos."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from dashboard.config import SENSITIVE_COLUMNS


class DataLoadError(RuntimeError):
    """Erro de leitura ou parse do arquivo de dados."""


def load_egressos_data(csv_path: str | Path) -> pd.DataFrame:
    """Carrega o CSV de egressos tentando separadores comuns."""

    path = Path(csv_path)
    if not path.exists():
        raise DataLoadError(f"Arquivo não encontrado: {path}")

    erros: list[str] = []
    for separador in (",", ";"):
        try:
            df = pd.read_csv(path, encoding="utf-8-sig", sep=separador)
            return anonymize_base_dataframe(df)
        except Exception as erro:  # pragma: no cover - cobertura de exceção agregada
            erros.append(f"sep='{separador}': {erro}")

    raise DataLoadError("Falha ao ler CSV. Tentativas: " + " | ".join(erros))


def anonymize_base_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Remove colunas sensíveis da base principal usada no dashboard."""

    return df.drop(columns=list(SENSITIVE_COLUMNS), errors="ignore").copy()


def anonymize_export_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Remove colunas sensíveis do dataframe usado na exportação."""

    return df.drop(columns=list(SENSITIVE_COLUMNS), errors="ignore").copy()

