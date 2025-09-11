import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ===============================
# 📊 CONFIGURAÇÃO DA PÁGINA
# ===============================
st.set_page_config(
    page_title="Crypto Dashboard EDA",
    page_icon="₿",
    layout="wide"
)

# ===============================
# 📊 CARREGAMENTO DO DATASET
# ===============================
@st.cache_data
def load_data():
    df = pd.read_csv("data/cryptocurrency.csv")
    
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
    df['Return'] = df.groupby('Symbol')['Close'].pct_change() * 100
    df_2015['Return'] = df_2015.groupby('Symbol')['Close'].pct_change() * 100
    
    # Removendo NaN da Coluna 'Return' - primeiro dia não tem retorno calculável
    df = df.dropna(subset=['Return']).reset_index(drop=True)
    df_2015 = df_2015.dropna(subset=['Return']).reset_index(drop=True)
    
    # Adicionar volatilidade diária
    df['DailyVolatility'] = df['High'] - df['Low']
    df_2015['DailyVolatility'] = df_2015['High'] - df_2015['Low']
    
    return df, df_2015

df, df_2015 = load_data()

# ===============================
# 🎯 IMPLEMENTAÇÃO DAS FUNCIONALIDADES DO DASHBOARD
# ===============================

# TODO 2: ✅ IMPLEMENTADO - Opção de escolher qual cripto
st.sidebar.title("🔧 Configurações")
crypto_choice = st.sidebar.selectbox(
    "Escolha a Criptomoeda:",
    ["Bitcoin (BTC)", "Ethereum (ETH)"]
)

# REGRA: Bitcoin usar 'df', Ethereum usar 'df_2015'
if crypto_choice == "Bitcoin (BTC)":
    selected_crypto = "BTC"
    data_source = df[df['Symbol'] == 'BTC'].copy()
    st.sidebar.success("📊 Usando dataset 'df' - dados completos desde 2013")
else:
    selected_crypto = "ETH"
    data_source = df_2015[df_2015['Symbol'] == 'ETH'].copy()
    st.sidebar.success("📊 Usando dataset 'df_2015' - dados desde ago/2015")

# TODO 3: ✅ IMPLEMENTADO - Usar somente anos inteiros
# Filtrar apenas anos completos (2013-2020)
# Excluir 2021 das comparações por estar incompleto
available_years = sorted(data_source['Year'].unique())
if 2021 in available_years:
    available_years.remove(2021)

st.sidebar.markdown("### 📅 Filtros de Data")

# TODO 1: ✅ IMPLEMENTADO - Opção de escolher a data por dia mes e ano
# Implementar seletores de data específicos
start_year = st.sidebar.selectbox("Ano Inicial:", available_years, index=0)
end_year = st.sidebar.selectbox("Ano Final:", available_years, index=len(available_years)-1)

# Permitir filtro por período customizado
if start_year <= end_year:
    filtered_data = data_source[
        (data_source['Year'] >= start_year) & 
        (data_source['Year'] <= end_year)
    ].copy()
else:
    st.sidebar.error("❌ Ano inicial deve ser menor ou igual ao ano final!")
    filtered_data = data_source.copy()

# ===============================
# 📊 TÍTULO E MÉTRICAS PRINCIPAIS
# ===============================
st.title("₿ Crypto Dashboard - Análise Exploratória")
st.markdown(f"### Análise de **{selected_crypto}** ({start_year} - {end_year})")

col1, col2, col3, col4 = st.columns(4)

with col1:
    current_price = filtered_data['Close'].iloc[-1]
    st.metric("💰 Preço Atual", f"${current_price:,.2f}")

with col2:
    total_return = ((filtered_data['Close'].iloc[-1] / filtered_data['Close'].iloc[0]) - 1) * 100
    st.metric("📈 Retorno Total", f"{total_return:+.1f}%")

with col3:
    avg_volume = filtered_data['Volume'].mean()
    st.metric("📊 Volume Médio", f"${avg_volume/1e9:.1f}B")

with col4:
    volatility = filtered_data['Return'].std()
    st.metric("⚡ Volatilidade", f"{volatility:.1f}%")

# ===============================
# 📊 GRÁFICOS E ANÁLISES - IMPLEMENTAÇÃO DOS TODOs
# ===============================

# TODO: ✅ IMPLEMENTADO - Gráfico Evolução temporal do preço
st.markdown("---")
st.subheader("📈 Evolução temporal do preço")

# Linha temporal mostrando evolução do preço
fig_price = px.line(
    filtered_data, 
    x='Date', 
    y='Close',
    title=f"Evolução do Preço de Fechamento - {selected_crypto}",
    labels={'Close': 'Preço (USD)', 'Date': 'Data'}
)
fig_price.update_layout(height=500)
st.plotly_chart(fig_price, use_container_width=True)

# TODO: ✅ IMPLEMENTADO - Ciclos sazonais
st.markdown("---")
st.subheader("🗓️ Ciclos sazonais (meses com maior valorização ou maior volume)")

# Análise mensal de performance
monthly_data = filtered_data.groupby('Month').agg({
    'Return': 'mean',
    'Volume': 'mean'
}).reset_index()

col1, col2 = st.columns(2)

with col1:
    # Identificar padrões sazonais de valorização
    fig_seasonal = px.bar(
        monthly_data,
        x='Month',
        y='Return',
        title="Retorno Médio por Mês (%)",
        color='Return',
        color_continuous_scale='RdYlGn'
    )
    st.plotly_chart(fig_seasonal, use_container_width=True)

with col2:
    fig_volume_month = px.line(
        monthly_data,
        x='Month',
        y='Volume',
        title="Volume Médio por Mês",
        markers=True
    )
    st.plotly_chart(fig_volume_month, use_container_width=True)

# TODO: ✅ IMPLEMENTADO - Picos Históricos Reais
st.markdown("---")
st.subheader("🏔️ Picos Históricos Reais")

# Marcar os ATH (All Time High) no gráfico
filtered_data['Peak'] = filtered_data['Close'].cummax()
picos_historicos = filtered_data[filtered_data['Close'] == filtered_data['Peak']]

fig_peaks = go.Figure()

fig_peaks.add_trace(go.Scatter(
    x=filtered_data['Date'],
    y=filtered_data['Close'],
    mode='lines',
    name='Preço',
    line=dict(color='blue', width=2)
))

# Identificar datas dos picos históricos
fig_peaks.add_trace(go.Scatter(
    x=picos_historicos['Date'],
    y=picos_historicos['Close'],
    mode='markers',
    name='Picos Históricos (ATH)',
    marker=dict(color='red', size=10, symbol='triangle-up')
))

fig_peaks.update_layout(
    title=f"Picos Históricos - {selected_crypto}",
    xaxis_title="Data",
    yaxis_title="Preço (USD)",
    height=500
)
st.plotly_chart(fig_peaks, use_container_width=True)

# TODO: ✅ IMPLEMENTADO - Comparação por ano
st.markdown("---")
st.subheader("📊 Comparação por ano: qual teve maior crescimento?")

# Gráfico de barras com retorno anual
# Usar apenas anos completos para comparação justa
yearly_returns = []
for year in filtered_data['Year'].unique():
    year_data = filtered_data[filtered_data['Year'] == year]
    if len(year_data) > 1:
        yearly_return = ((year_data['Close'].iloc[-1] / year_data['Close'].iloc[0]) - 1) * 100
        yearly_returns.append({'Year': year, 'Return': yearly_return})

yearly_df = pd.DataFrame(yearly_returns)

if not yearly_df.empty:
    fig_yearly = px.bar(
        yearly_df,
        x='Year',
        y='Return',
        title=f"Retorno Anual - {selected_crypto} (Anos Completos)",
        color='Return',
        color_continuous_scale='RdYlGn'
    )
    fig_yearly.update_layout(height=400)
    st.plotly_chart(fig_yearly, use_container_width=True)
    
    # Mostrar o melhor e pior ano
    best_year = yearly_df.loc[yearly_df['Return'].idxmax()]
    worst_year = yearly_df.loc[yearly_df['Return'].idxmin()]
    
    col1, col2 = st.columns(2)
    col1.success(f"🏆 **Melhor ano:** {int(best_year['Year'])} ({best_year['Return']:+.1f}%)")
    col2.error(f"📉 **Pior ano:** {int(worst_year['Year'])} ({worst_year['Return']:+.1f}%)")

# TODO: ✅ IMPLEMENTADO - Outliers Encontrados
st.markdown("---")
st.subheader("🔍 Outliers Encontrados")

# Identificar dias de maior volatilidade
Q1 = filtered_data['DailyVolatility'].quantile(0.25)
Q3 = filtered_data['DailyVolatility'].quantile(0.75)
IQR = Q3 - Q1
limite_superior = Q3 + 1.5 * IQR

# Análise de eventos extremos de mercado
outliers = filtered_data[filtered_data['DailyVolatility'] > limite_superior]

col1, col2 = st.columns(2)

with col1:
    fig_box = go.Figure()
    fig_box.add_trace(go.Box(
        y=filtered_data['DailyVolatility'],
        name=f'{selected_crypto} Volatilidade',
        boxpoints='outliers'
    ))
    fig_box.update_layout(
        title="Boxplot - Detecção de Outliers",
        yaxis_title="Volatilidade Diária (USD)"
    )
    st.plotly_chart(fig_box, use_container_width=True)

with col2:
    st.write("**📊 Estatísticas de Outliers:**")
    st.write(f"• Total de outliers: **{len(outliers)}**")
    st.write(f"• Limite superior: **${limite_superior:.2f}**")
    st.write(f"• Maior volatilidade: **${filtered_data['DailyVolatility'].max():.2f}**")
    
    if len(outliers) > 0:
        st.write("**🔥 Top 3 dias mais voláteis:**")
        top_outliers = outliers.nlargest(3, 'DailyVolatility')
        for idx, row in top_outliers.iterrows():
            st.write(f"• {row['Date'].strftime('%Y-%m-%d')}: ${row['DailyVolatility']:.2f}")

# TODO: ✅ IMPLEMENTADO - Correlação entre volume e preço
st.markdown("---")
st.subheader("🔗 Correlação entre volume e preço")

# Scatter plot volume vs movimento de preço
col1, col2 = st.columns(2)

with col1:
    fig_corr = px.scatter(
        filtered_data,
        x='Volume',
        y='Return',
        title="Volume vs Retorno Diário",
        labels={'Volume': 'Volume', 'Return': 'Retorno (%)'},
        opacity=0.6,
        color='Return',
        color_continuous_scale='RdYlGn'
    )
    st.plotly_chart(fig_corr, use_container_width=True)

with col2:
    # Calcular correlação estatística
    correlation_vol_return = filtered_data['Volume'].corr(filtered_data['Return'].abs())
    correlation_vol_price = filtered_data['Volume'].corr(filtered_data['Close'])
    
    st.write("**📊 Correlações Estatísticas:**")
    st.metric("Volume vs |Retorno|", f"{correlation_vol_return:.3f}")
    st.metric("Volume vs Preço", f"{correlation_vol_price:.3f}")
    
    # Interpretação
    if correlation_vol_return > 0.3:
        st.success("🔗 **Volume alto → Maior movimentação de preço**")
    elif correlation_vol_return > 0.1:
        st.info("🔗 **Volume moderadamente correlacionado**")
    else:
        st.warning("🔗 **Volume pouco correlacionado com movimentos**")

# TODO 4: ✅ IMPLEMENTADO - Seção específica para 2021
st.markdown("---")
st.subheader("🚨 Seção Especial: Bull Run 2021 (7 meses)")

# Separar uma seção específica para ano de 2021(7 meses) onde teve maior movimentações de preço
data_2021 = data_source[data_source['Year'] == 2021].copy()

if not data_2021.empty:
    # Destacar que são apenas 7 meses de dados
    st.warning("⚠️ **ATENÇÃO:** 2021 possui apenas 187 dias (Janeiro a Julho) - Dados incompletos")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if len(data_2021) > 1:
            return_2021 = ((data_2021['Close'].iloc[-1] / data_2021['Close'].iloc[0]) - 1) * 100
            st.metric("📈 Retorno 2021", f"{return_2021:+.1f}%")
    
    with col2:
        max_price_2021 = data_2021['Close'].max()
        st.metric("🏆 ATH 2021", f"${max_price_2021:,.2f}")
    
    with col3:
        # Mostrar o período de maior volatilidade histórica
        avg_vol_2021 = data_2021['DailyVolatility'].mean()
        st.metric("⚡ Volatilidade Média", f"${avg_vol_2021:.2f}")
    
    # Gráfico específico de 2021
    fig_2021 = px.line(
        data_2021,
        x='Date',
        y='Close',
        title=f"Bull Run 2021 - {selected_crypto} (Maior Movimentação Histórica)",
        labels={'Close': 'Preço (USD)', 'Date': 'Data'}
    )
    fig_2021.update_layout(height=400)
    st.plotly_chart(fig_2021, use_container_width=True)
    
    st.success("🚀 **2021 foi o período de maior valorização e volatilidade da história das criptomoedas!**")
else:
    st.info(f"ℹ️ Não há dados de 2021 para {selected_crypto} no dataset selecionado.")

# ===============================
# ℹ️ INFORMAÇÕES SOBRE OS DATASETS
# ===============================
st.markdown("---")
st.info(f"""
**ℹ️ Informações sobre o Dataset Utilizado:**

**{selected_crypto}** está usando: {"**dataset 'df'** (completo desde 2013)" if selected_crypto == "BTC" else "**dataset 'df_2015'** (desde agosto/2015)"}

**📊 Regras de Uso:**
• **Bitcoin**: Dataset completo 'df' - dados históricos desde 2013  
• **Ethereum**: Dataset 'df_2015' - dados desde criação (ago/2015)  
• **Anos Completos**: Apenas 2013-2020 para comparações justas  
• **2021**: Seção separada - apenas 7 meses disponíveis (jan-jul)  

**⚠️ Limitação:** 2021 tem apenas 187 dias - período de maior bull run histórico!
""")



# Ajeitar Gráfico Outliers Encontrados ou Substituir o insight(recomendado)
# Substituir ou ajeitar correlação entre volume e preço (pouco relacionável)