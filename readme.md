# 📊 Crypto Dashboard – Bitcoin & Ethereum (2015–2021)

![CI/CD Pipeline](https://github.com/kiovaz/crypto-dashboard-eda/workflows/CI%2FCD%20Pipeline/badge.svg)

Este projeto foi desenvolvido como parte de um trabalho acadêmico, com o objetivo de criar um **dashboard interativo** para análise exploratória de dados financeiros. O foco está nas criptomoedas **Bitcoin (BTC)** e **Ethereum (ETH)**, no período de 2015 a 2021.

---

## 🚀 Objetivos do Projeto
- Selecionar e justificar um dataset relevante do **Kaggle**.
- Realizar **análise exploratória de dados (EDA)** com `pandas`.
- Tratar dados faltantes, duplicados e padronizar colunas.
- Planejar e implementar um **dashboard interativo** usando `Streamlit` + `Plotly`.
- Criar visualizações claras e comparativas (preço, volume, marketcap).
- Implementar um **modelo simples de previsão de série temporal** para preços de criptomoedas.
- Documentar código, decisões e resultados.

---

## 📂 Estrutura do Projeto

```
📁 crypto-dashboard-eda/
├── 📄 dashboard.py          # Código principal do Streamlit
├── 📄 notebook.ipynb        # Análises exploratórias (Jupyter)
├── 📄 cryptocurrency.csv    # Dataset usado (do Kaggle)
├── 📄 requirements.txt      # Dependências do projeto
└── 📄 README.md            # Documentação
```

---

---

## 📊 Principais Funcionalidades

- **Filtros interativos**: escolha de moedas e período de análise.
- **Visualizações**:
  - Evolução do preço de fechamento.
  - Volume negociado ao longo do tempo.
  - Relação entre Market Cap e Preço.
- **Download de dados filtrados** em CSV.
- **Previsão simples de preços** usando séries temporais (modelo de baseline).

---

## 🔧 Tecnologias Utilizadas

- [Python 3.12](https://www.python.org/)
- [Pandas](https://pandas.pydata.org/)
- [Streamlit](https://streamlit.io/)
- [Plotly](https://plotly.com/python/)
- [Scikit-learn](https://scikit-learn.org/) (para modelo preditivo simples)

---

## 📅 Período da Análise

- Bitcoin: dados a partir de 2013
- Ethereum: dados a partir de 2015
- **Período em comum considerado: 2015 – 2021**

---

## 📖 Como Executar o Projeto

1. **Clone este repositório:**
   ```bash
   git clone https://github.com/kiovaz/crypto-dashboard-eda.git
   cd crypto-dashboard-eda
   ```

2. **Crie e ative um ambiente virtual:**
   ```bash
   python -m venv .venv
   
   # Linux/Mac
   source .venv/bin/activate
   
   # Windows
   .venv\Scripts\activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Execute o dashboard:**
   ```bash
   streamlit run dashboard.py
   ```

5. **Abra seu navegador** e acesse: `http://localhost:8501`

---

## 📌 Observações

- Os dados foram obtidos do **Kaggle** e abrangem o período de 2013–2021, com filtragem para 2015–2021 para permitir comparações justas entre as moedas.
- O dashboard é totalmente **interativo** e permite exploração visual dos dados.

---

## 🔄 CI/CD Pipeline

Este projeto utiliza GitHub Actions para garantir qualidade e segurança do código:

- ✅ **Lint**: Verificação de estilo de código com flake8 e black
- ✅ **Tests**: Validação de imports e sintaxe do dashboard
- ✅ **Security**: Scan de vulnerabilidades nas dependências
- ✅ **Automação**: Executa em cada push e pull request

O status do pipeline pode ser visualizado no badge acima.

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.