# 📊 Crypto Dashboard – Bitcoin & Ethereum (2015–2021)

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
📁 crypto-dashboard-eda
┣ 📄 dashboard.py # Código principal do Streamlit
┣ 📄 eda_notebook.ipynb # Análises exploratórias (Jupyter)
┣ 📄 Dataset_Criptomoedas.csv # Dataset usado (do Kaggle)
┣ 📄 requirements.txt # Dependências do projeto
┗ 📄 README.md # Documentação

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

1. Clone este repositório:
```bash
git clone https://github.com/seu-usuario/crypto-dashboard-eda.git
cd crypto-dashboard-eda
2. Crie e ative um ambiente virtual:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
3. Instale as dependências:
```bash
pip install -r requirements.txt
4. Execute o dashboard:
```bash
streamlit run dashboard.py

📌 Observações

Este projeto tem fins educacionais e não deve ser usado como ferramenta de investimento.
Os dados foram obtidos do Kaggle e abrangem o período de 2013–2021, com filtragem para 2015–2021 para permitir comparações justas entre as moedas.

