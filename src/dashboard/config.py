"""Configuracoes centrais do dashboard de egressos."""

from __future__ import annotations

from pathlib import Path

# Configuracao da pagina Streamlit
PAGE_TITLE = "Dashboard de Egressos - UFRA Capanema"
PAGE_ICON = "🌿"
PAGE_LAYOUT = "wide"
PAGE_SIDEBAR_STATE = "expanded"

# Caminho padrao da base de dados
DATA_FILE_PATH = Path(__file__).resolve().parents[2] / "database" / "egressos_limpo.csv"

# Paleta institucional UFRA
UFRA_VERDE = "#006633"
UFRA_CINZA = "#F2F2F2"

# Nomes de colunas usados no dashboard
COL_NOME = "Nome Completo"
COL_EMAIL = "E-mail"
COL_ANO = "Ano de Saída/Conclusão do Curso"
COL_UF = "UF"
COL_TRABALHANDO = "Você está trabalhando?"
COL_ATUACAO_AREA = "O seu emprego é na área de formação?"
COL_POS = "Possui Pós-Graduação"
COL_FAIXA_CONCLUSAO = "Faixa de Conclusão"
COL_SITUACAO_MERCADO = "Qual a sua situação no mercado de trabalho?"
COL_SETOR_TRABALHO = "Qual o setor do seu trabalho?"
COL_TEMPO_PRIMEIRO_EMPREGO = (
    "Quanto tempo, em meses, demorou para conseguir o primeiro emprego após concluir o curso?"
)

SENSITIVE_COLUMNS = (COL_NOME, COL_EMAIL)

# Parametros de visualizacao
GRAPHICS_HEIGHT = 300
CHART_MARGIN = {"l": 0, "r": 0, "t": 20, "b": 0}
LONG_LABEL_THRESHOLD = 5

CHART_COLORS_BASE = [UFRA_VERDE, "#94C973", "#B5DCC2"]
CHART_COLORS_POS = [UFRA_VERDE, "#A5CFA3", "#D0E6C8"]
CHART_COLOR_EXTERIOR = "#FFD700"

THEME_OPTIONS = {
    "dark": {
        "app_bg": "#0E1117",
        "sidebar_bg": "#111111",
        "text": "#F5F5F5",
        "muted_text": "#B8BEC5",
        "divider": "#2B3138",
        "plot_bg": "#111111",
        "paper_bg": "#111111",
        "grid": "#3A3A3A",
        "axis_line": "#4B5563",
        "legend_bg": "rgba(17, 17, 17, 0.70)",
        "geo_land": "#1A1A1A",
        "geo_country": "#6B7280",
        "header_text": "#FFFFFF",
    },
    "light": {
        "app_bg": "#FFFFFF",
        "sidebar_bg": UFRA_CINZA,
        "text": "#1F2933",
        "muted_text": "#5C6670",
        "divider": "#D8DEE5",
        "plot_bg": "#FFFFFF",
        "paper_bg": "#FFFFFF",
        "grid": "#D8DEE5",
        "axis_line": "#AAB4BE",
        "legend_bg": "rgba(255, 255, 255, 0.90)",
        "geo_land": "#EEF2F4",
        "geo_country": "#8C98A4",
        "header_text": "#FFFFFF",
    },
}
