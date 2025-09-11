import pandas as pd
import streamlit as st

# ===============================
# 📊 CARREGAMENTO DO DATASET
# ===============================
df = pd.read_csv("../data/cryptocurrency.csv")

# ===============================
# 🔄 CONVERSÃO E PREPARAÇÃO DOS DADOS
# ===============================

# Precisa converter Date (object) --> Date (datetime)
df['Date'] = pd.to_datetime(df['Date'])

# Criar colunas Ano, Mês e Dia para facilitar filtros temporais
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Day'] = df['Date'].dt.day

# ===============================
# 📅 CRIAÇÃO DO DF_2015 (PERÍODO COMUM BTC/ETH)
# ===============================

# Encontrar intervalo comum entre moedas
start_date = df.groupby("Symbol")["Date"].min().max()  # maior data inicial (quando ETH foi criado)
end_date = df.groupby("Symbol")["Date"].max().min()    # menor data final (data comum mais recente)

# Filtrar dataset para período onde ambas as moedas existem
df_2015 = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]

# DF-2015 com erro no index - correção necessária
df_2015 = df_2015.reset_index(drop=True)  # reseta o índice antigo
df_2015["SNo"] = df_2015.index + 1

# ===============================
# 📈 CÁLCULO DE INDICADORES FINANCEIROS
# ===============================

# Cria coluna Retorno Diário - variação percentual do preço de fechamento
df['Return'] = df['Close'].pct_change() * 100

# Removendo NaN da Coluna 'Return' - primeiro dia não tem retorno calculável
df = df.dropna(subset=['Return']).reset_index(drop=True)

# ===============================
# 🎯 FUNCIONALIDADES DO DASHBOARD (TODO)
# ===============================

# TODO 1: Opção de escolher a data por dia mes e ano
# - Implementar seletores de data específicos
# - Permitir filtro por período customizado

# TODO 2: Opção de escolher qual cripto
# - Seletor entre BTC e ETH
# - REGRA: Bitcoin usar 'df', Ethereum usar 'df_2015'

# TODO 3: Usar somente anos inteiros
# - Filtrar apenas anos completos (2013-2020)
# - Excluir 2021 das comparações por estar incompleto

# TODO 4: Separar uma seção específica para ano de 2021(7 meses) onde teve maior movimentações de preço
# - Seção especial "Bull Run 2021"
# - Destacar que são apenas 7 meses de dados
# - Mostrar o período de maior volatilidade histórica

# ===============================
# 📊 GRÁFICOS E ANÁLISES (TODO)
# ===============================

# TODO: Gráfico Evolução temporal do preço (gráfico de linha com Close).
# - Linha temporal mostrando evolução do preço
# - Usar dados completos com destaque para períodos importantes

# TODO: Ciclos sazonais (ex: meses com maior valorização ou maior volume).
# - Análise mensal de performance
# - Identificar padrões sazonais de valorização

# TODO: Picos Históricos Reais
# - Marcar os ATH (All Time High) no gráfico
# - Identificar datas dos picos históricos

# TODO: Comparação por ano (2013–2021): qual ano teve maior crescimento?
# - Gráfico de barras com retorno anual
# - Usar apenas anos completos para comparação justa

# TODO: Outliers Encontrados
# - Identificar dias de maior volatilidade
# - Análise de eventos extremos de mercado

# TODO: Correlação entre volume e preço (ex: volume alto → queda ou alta?).
# - Scatter plot volume vs movimento de preço
# - Calcular correlação estatística

# ===============================
# 📋 REGRAS DE USO DOS DATASETS
# ===============================

# BITCOIN: usar dataset 'df'
# - Dados completos desde 2013
# - Para análises históricas do BTC

# ETHEREUM: usar dataset 'df_2015' 
# - Dados desde agosto/2015 (criação do ETH)
# - Para comparações BTC vs ETH no mesmo período
# - Garante comparação justa entre as moedas

# ===============================
# ⚠️ LIMITAÇÕES DOS DADOS
# ===============================

# ATENÇÃO: 2021 tem apenas 187 dias (jan-jul)
# - Não usar para comparações anuais
# - Criar seção separada para análise de 2021
# - Período de maior bull run histórico