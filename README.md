# 🌿 Dashboard de Egressos — Engenharia Ambiental (UFRA Capanema)

## 🎯 Sobre o Projeto

O **Dashboard de Egressos** é uma aplicação interativa desenvolvida em **Python** com **Streamlit** e **Plotly**, voltada à visualização e análise dos dados dos **egressos do curso de Engenharia Ambiental da UFRA — Campus Capanema**.

O painel tem como propósito divulgar, de forma acessível e visual, **onde e como nossos ex-alunos estão atuando**, destacando aspectos como:
- Situação profissional e atuação na área de formação;
- Continuidade acadêmica (pós-graduação);
- Distribuição geográfica dos egressos no Brasil e no exterior 🌎;
- Indicadores de empregabilidade e tempo até o primeiro emprego.

Além de fortalecer a identidade institucional, o projeto tem papel estratégico na **avaliação do curso**, **prestação de contas à comunidade acadêmica** e **incentivo aos atuais discentes**, mostrando o alcance da formação oferecida pela UFRA.

---

## 🧠 Tecnologias Utilizadas

O projeto foi desenvolvido em Python, adotando bibliotecas modernas e de código aberto:

| Categoria | Biblioteca | Finalidade |
|------------|-------------|-------------|
| Interface web | [**Streamlit**](https://streamlit.io/) | Criação do painel interativo |
| Visualização de dados | [**Plotly Express**](https://plotly.com/python/plotly-express/) | Geração dos gráficos e mapas |
| Manipulação de dados | [**Pandas**](https://pandas.pydata.org/) | Leitura, tratamento e filtragem da base de dados |
| Visualização global | [**Plotly Geo**](https://plotly.com/python/scatter-plots-on-maps/) | Plotagem de egressos por coordenadas (Brasil e exterior) |

---

## 🧩 Estrutura do Projeto

```
📁 dashboard-egressos/
│
├── 📂 src/
│   └── dashboard_egressos.py       # Código principal do painel Streamlit
│
├── 📂 database/
│   └── egressos_limpo.csv          # Base de dados tratada e anonimizada
│
├── 📄 README.md                    # Documentação do projeto
└── 📄 requirements.txt             # Dependências Python do ambiente
```

---

## ⚙️ Dependências e Ambiente

Crie e ative um ambiente virtual Python, depois instale as dependências listadas no arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

> 💡 Recomenda-se utilizar Python 3.10 ou superior.

---

## ▶️ Execução do Dashboard

Após configurar o ambiente e garantir que o arquivo `egressos_limpo.csv` esteja na pasta `database/`, execute o dashboard com:

```bash
streamlit run src/dashboard_egressos.py
```

O painel será iniciado no navegador padrão (geralmente em `http://localhost:8501`).

---

## 🗺️ Funcionalidades do Dashboard

- **Filtros dinâmicos** (ano, UF, situação profissional, pós-graduação);  
- **Indicadores (KPIs)** de empregabilidade e atuação na área;  
- **Mapa global interativo**, destacando inclusive egressos que estão no exterior (ex.: Portugal ⭐);  
- **Visualizações comparativas** com gráficos de barras, treemaps e histogramas;  
- **Exportação segura dos dados filtrados** em CSV **anonimizado** (sem nomes nem e-mails).

---

## 🛡️ Política de Dados

Para proteger a privacidade dos egressos, **nenhuma informação pessoal identificável** (como nome completo ou e-mail) é exibida ou disponibilizada para download.  
Todas as análises e visualizações são realizadas sobre dados **anonimizados e consolidados**.

---

## 👨‍💻 Autor e Orientação

**Prof. Dr. Anderson Soares**  
Campus da Universidade Federal Rural da Amazônia — UFRA Capanema  
📧 [andersonsoares@ufra.edu.br](mailto:anderson.soares@ufra.edu.br)

**Prof. Dr. Geraldo Melo**  
Campus da Universidade Federal Rural da Amazônia — UFRA Capanema  
📧 [geraldo.melo@ufra.edu.br](mailto:geraldo.melo@ufra.edu.br)

Projeto vinculado às ações de acompanhamento de egressos e fortalecimento institucional da UFRA.

---

## 🏛️ Licença

Este projeto é de uso **institucional da UFRA** e tem caráter **educacional e de divulgação científica**.  
O código pode ser reutilizado para fins acadêmicos, desde que mantidos os devidos créditos e respeitada a anonimização dos dados.

---

> Desenvolvido com 💚 Python, Streamlit e Plotly.  
> Laboratório de Tecnologias Computacionais ([**LabTec**](https://sites.google.com/view/gplabtec)) ([**Canal do LabTec**](https://www.youtube.com/@labtec_ufra))

## Estrutura refatorada (camadas leves)

A partir desta refatoracao, o dashboard passa a adotar uma organizacao em camadas leves:

```text
src/
  dashboard_egressos.py
  dashboard/
    app.py
    config.py
    types.py
    services/
      data_loader.py
      filters.py
      metrics.py
      aggregations.py
      geo.py
    charts/
      theme.py
      builders.py
tests/
  test_aggregations.py
  test_filters_metrics.py
  test_charts_builders.py
```

O comando de execucao permanece o mesmo:

```bash
streamlit run src/dashboard_egressos.py
```
