import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt


st.set_page_config(page_title="Crypto Dash",page_icon="data/image.png",layout="wide")

df = pd.read_csv("data/cryptocurrency.csv")

menu = st.sidebar.radio(
    "📌 Navegação",
    ["Dashboard Principal", "Análise BTC 2021"]
)

if menu == "Dashboard Principal":
    st.title("📊 Dashboard Principal")

    # Converter Date (object) --> Date (datetime)
    df['Date'] = pd.to_datetime(df['Date'])

    # Encontrar intervalo comum entre moedas
    start_date = df.groupby("Symbol")["Date"].min().max()  # maior data inicial (quando ETH foi criado)
    end_date = df.groupby("Symbol")["Date"].max().min()    # menor data final (data comum mais recente)

    # Filtrar dataset para período onde ambas as moedas existem
    df_2015 = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)].copy()

    # Criar colunas temporais
    df_2015['Year'] = df_2015['Date'].dt.year
    df_2015['Month'] = df_2015['Date'].dt.month
    df_2015['Day'] = df_2015['Date'].dt.day

    # Criar coluna Retorno Diário - variação percentual do preço de fechamento
    df_2015['Return'] = df_2015.groupby('Symbol')['Close'].pct_change() * 100

    # Função para classificar retornos
    def classify_return(return_value):
        if pd.isna(return_value):
            return 'Neutro'
        elif return_value > 0:
            return 'Positivo'
        elif return_value < 0:
            return 'Negativo'
        else:
            return 'Neutro'

    # Aplicar classificação de retorno
    df_2015['Return_Status'] = df_2015['Return'].apply(classify_return)

    # Correção do index
    df_2015 = df_2015.reset_index(drop=True)
    df_2015["SNo"] = df_2015.index + 1

    # Pegar séries separadas (AMBAS do período filtrado)
    btc = df_2015[df_2015['Symbol'] == 'BTC'].copy()
    eth = df_2015[df_2015['Symbol'] == 'ETH'].copy()

    st.title("Crypto Dash EDA")
    st.subheader("Análise de Criptomoedas - BTC / ETH (2015 - 2020)")


    col1, col2, col3, col4, col5 = st.columns(5)

    # Coluna 1: Seletor de Criptomoeda e Valor Médio
    with col1:
        # Opções únicas de criptomoedas
        crypto_options = df_2015['Symbol'].unique()
        
        # Selectbox para escolher a criptomoeda
        selected_crypto = st.selectbox(
            "Valor Médio",
            options=crypto_options,
            index=0  # BTC como padrão
        )
        
        # Filtrar dados da cripto selecionada
        selected_data = df_2015[df_2015['Symbol'] == selected_crypto]
        valor_medio = selected_data['Close'].mean()
        
        # Definir limite máximo baseado na criptomoeda
        if selected_crypto == 'BTC':
            max_range = 20000
        elif selected_crypto == 'ETH':
            max_range = 500  # Reduzir para melhor visualização do ETH
        else:
            max_range = selected_data['Close'].max()  # Para outras criptos
        
        # Velocímetro com limites fixos
        fig1 = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = valor_medio,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'font': {'size': 16, 'color': '#333'}},
            number = {'prefix': "$", 'font': {'size': 18, 'color': '#1f77b4'}},
            gauge = {
                'axis': {'range': [0, max_range], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#1f77b4"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, max_range * 0.3], 'color': "#e6f3ff"},
                    {'range': [max_range * 0.3, max_range * 0.7], 'color': "#b3d9ff"},
                    {'range': [max_range * 0.7, max_range], 'color': "#80c0ff"}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': valor_medio}}))
        
        fig1.update_layout(
            height=200,
            margin={'t': 25, 'b': 25, 'l': 25, 'r': 25},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})


    with col2:
        # Selectbox para escolher a criptomoeda para drawdowns
        selected_dd_crypto = st.selectbox(
            "DrawDowns",
            options=crypto_options,
            index=0,  # BTC como padrão
            key="dd_crypto"
        )
        
        # Filtrar dados da cripto selecionada para drawdowns
        dd_data = df_2015[df_2015['Symbol'] == selected_dd_crypto].copy()
        
        # Calcular drawdowns
        dd_data['Cumulative_Return'] = (1 + dd_data['Return'].fillna(0) / 100).cumprod()
        dd_data['Peak'] = dd_data['Cumulative_Return'].expanding().max()
        dd_data['Drawdown'] = ((dd_data['Cumulative_Return'] / dd_data['Peak']) - 1) * 100
        
        # Máximo drawdown (valor absoluto para mostrar no velocímetro)
        max_drawdown = abs(dd_data['Drawdown'].min())
        
        # Velocímetro para DrawDown (mesmo estilo da coluna 1)
        fig2 = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = max_drawdown,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"{selected_dd_crypto} DD", 'font': {'size': 16, 'color': '#333'}},
            number = {'suffix': "%", 'font': {'size': 18, 'color': '#e74c3c'}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#e74c3c"},  # Vermelho para drawdown
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 30], 'color': "#fff2f0"},    # Leve
                    {'range': [30, 60], 'color': "#ffccc7"},   # Moderado
                    {'range': [60, 100], 'color': "#ffa39e"}], # Severo
                'threshold': {
                    'line': {'color': "darkred", 'width': 4},
                    'thickness': 0.75,
                    'value': max_drawdown}}))
        
        fig2.update_layout(
            height=200,
            margin={'t': 25, 'b': 25, 'l': 25, 'r': 25},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
        

    with col3:
        # Selectbox para escolher a criptomoeda para risco x retorno
        selected_risk_crypto = st.selectbox(
            "Risco x Retorno",
            options=crypto_options,
            index=0,  # BTC como padrão
            key="risk_crypto"
        )
        
        # Filtrar dados da cripto selecionada
        risk_data = df_2015[df_2015['Symbol'] == selected_risk_crypto].copy()
        
        # Calcular métricas de risco e retorno
        retorno_medio = risk_data['Return'].mean()  # Retorno médio diário
        risco = risk_data['Return'].std()  # Volatilidade (risco)
        
        # Calcular Sharpe Ratio (retorno/risco) - assumindo taxa livre de risco = 0
        if risco > 0:
            sharpe_ratio = retorno_medio / risco
        else:
            sharpe_ratio = 0
        
        # Velocímetro para Sharpe Ratio com escala REAL
        fig3 = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = sharpe_ratio,  # VALOR REAL, não escalado
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"{selected_risk_crypto} Sharpe", 'font': {'size': 16, 'color': '#333'}},
            number = {'font': {'size': 18, 'color': '#28a745'}},
            gauge = {
                'axis': {'range': [-3, 3], 'tickwidth': 1, 'tickcolor': "darkblue"},  # ESCALA REAL
                'bar': {'color': "#28a745"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [-3, 0], 'color': "#ffebee"},   # Negativo (ruim)
                    {'range': [0, 1], 'color': "#fff3e0"},    # Baixo
                    {'range': [1, 2], 'color': "#e8f5e8"},    # Bom  
                    {'range': [2, 3], 'color': "#c3e6cb"}],   # Excelente
                'threshold': {
                    'line': {'color': "green", 'width': 4},
                    'thickness': 0.75,
                    'value': sharpe_ratio}}))
        
        fig3.update_layout(
            height=200,
            margin={'t': 25, 'b': 25, 'l': 25, 'r': 25},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})


    with col4:
        # Selectbox para escolher a criptomoeda
        selected_trend_crypto = st.selectbox(
            "Tendência Valorização",
            options=crypto_options,
            index=0,  # BTC como padrão
            key="trend_crypto"
        )
        
        # Filtrar dados da cripto selecionada
        trend_data = df_2015[df_2015['Symbol'] == selected_trend_crypto].copy()
        
        # Contar retornos por status
        status_counts = trend_data['Return_Status'].value_counts()
        
        # Calcular percentuais
        total_days = len(trend_data)
        positive_pct = (status_counts.get('Positivo', 0) / total_days) * 100
        negative_pct = (status_counts.get('Negativo', 0) / total_days) * 100
        neutral_pct = (status_counts.get('Neutro', 0) / total_days) * 100
        
        # Usar percentual de dias positivos como indicador de tendência
        trend_score = positive_pct
        
        # Velocímetro para Tendência de Valorização (mesmo estilo das outras)
        fig4 = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = trend_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"{selected_trend_crypto} Trend", 'font': {'size': 16, 'color': '#333'}},
            number = {'suffix': "%", 'font': {'size': 18, 'color': '#17a2b8'}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#17a2b8"},  # Azul para tendência
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 30], 'color': "#f8d7da"},    # Baixa (mais dias negativos)
                    {'range': [30, 50], 'color': "#fff3cd"},   # Neutra
                    {'range': [50, 70], 'color': "#d1ecf1"},   # Boa
                    {'range': [70, 100], 'color': "#c3e6cb"}], # Excelente (mais dias positivos)
                'threshold': {
                    'line': {'color': "blue", 'width': 4},
                    'thickness': 0.75,
                    'value': trend_score}}))
        
        fig4.update_layout(
            height=200,
            margin={'t': 25, 'b': 25, 'l': 25, 'r': 25},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})


    with col5:
        # Selectbox para escolher a criptomoeda
        selected_recovery_crypto = st.selectbox(
            "Eficiência Recuperação",
            options=crypto_options,
            index=0,  # BTC como padrão
            key="recovery_crypto"
        )
        
        # Filtrar dados da cripto selecionada
        recovery_data = df_2015[df_2015['Symbol'] == selected_recovery_crypto].copy()
        
        # Calcular eficiência de recuperação
        # 1. Calcular retorno cumulativo e picos
        recovery_data['Cumulative_Return'] = (1 + recovery_data['Return'].fillna(0) / 100).cumprod()
        recovery_data['Peak'] = recovery_data['Cumulative_Return'].expanding().max()
        recovery_data['Drawdown'] = ((recovery_data['Cumulative_Return'] / recovery_data['Peak']) - 1) * 100
        
        # 2. Identificar períodos de drawdown e recuperação
        recovery_times = []
        in_drawdown = False
        drawdown_start = 0
        
        for i, row in recovery_data.iterrows():
            if row['Drawdown'] < -5 and not in_drawdown:  # Início de drawdown significativo (>5%)
                in_drawdown = True
                drawdown_start = i
            elif row['Drawdown'] >= -1 and in_drawdown:  # Recuperação (volta a menos de 1% do pico)
                recovery_time = i - drawdown_start
                if recovery_time > 0:
                    recovery_times.append(recovery_time)
                in_drawdown = False
        
        # 3. Calcular eficiência média de recuperação
        if recovery_times:
            avg_recovery_days = np.mean(recovery_times)
            # Converter para score de eficiência (menor tempo = maior eficiência)
            # Escala: 1-100 onde 100 = recuperação muito rápida
            max_days = 365  # Assumir 1 ano como tempo máximo razoável
            efficiency_score = max(0, 100 - (avg_recovery_days / max_days * 100))
        else:
            efficiency_score = 50  # Score neutro se não houver dados suficientes
        
        # Velocímetro para Eficiência de Recuperação
        fig5 = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = efficiency_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"{selected_recovery_crypto} Recov", 'font': {'size': 16, 'color': '#333'}},
            number = {'suffix': "%", 'font': {'size': 18, 'color': '#9c27b0'}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#9c27b0"},  # Roxo para eficiência de recuperação
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 25], 'color': "#fce4ec"},    # Baixa eficiência
                    {'range': [25, 50], 'color': "#f8bbd9"},   # Média baixa
                    {'range': [50, 75], 'color': "#e1bee7"},   # Boa
                    {'range': [75, 100], 'color': "#ce93d8"}], # Excelente
                'threshold': {
                    'line': {'color': "purple", 'width': 4},
                    'thickness': 0.75,
                    'value': efficiency_score}}))
        
        fig5.update_layout(
            height=200,
            margin={'t': 25, 'b': 25, 'l': 25, 'r': 25},
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})

    # Linha divisória
    st.divider()

    # Segunda linha - 2 gráficos grandes
    col_left, col_right = st.columns(2)

    # Gráfico da Esquerda: Preços Históricos com Picos
    with col_left:
        st.subheader("Picos Históricos")
        
        # Selectbox para escolher visualização
        price_view = st.selectbox(
            "Selecione a visualização:",
            options=["BTC", "ETH", "BTC + ETH (Comparação)"],
            index=0,  # BTC como padrão
            key="price_view"
        )
        
        fig_price = go.Figure()
        
        if price_view == "BTC":
            # Apenas BTC
            btc_data = df_2015[df_2015['Symbol'] == 'BTC'].copy()
            
            # Encontrar picos (máximos locais)
            from scipy.signal import find_peaks
            prices = btc_data['Close'].values
            peaks, _ = find_peaks(prices, height=prices.mean(), distance=30)  # Picos significativos
            
            # Linha principal do BTC
            fig_price.add_trace(go.Scatter(
                x=btc_data['Date'],
                y=btc_data['Close'],
                mode='lines',
                name='BTC',
                line=dict(color='#f7931a', width=2),
                hovertemplate='<b>BTC</b><br>Data: %{x}<br>Preço: $%{y:,.0f}<extra></extra>'
            ))
            
            # Marcar picos
            if len(peaks) > 0:
                fig_price.add_trace(go.Scatter(
                    x=btc_data.iloc[peaks]['Date'],
                    y=btc_data.iloc[peaks]['Close'],
                    mode='markers',
                    name='Picos BTC',
                    marker=dict(color='red', size=8, symbol='triangle-up'),
                    hovertemplate='<b>Pico BTC</b><br>Data: %{x}<br>Preço: $%{y:,.0f}<extra></extra>'
                ))
            
            fig_price.update_yaxes(title_text="Preço BTC (USD)")
            
        elif price_view == "ETH":
            # Apenas ETH
            eth_data = df_2015[df_2015['Symbol'] == 'ETH'].copy()
            
            # Encontrar picos
            from scipy.signal import find_peaks
            prices = eth_data['Close'].values
            peaks, _ = find_peaks(prices, height=prices.mean(), distance=30)
            
            # Linha principal do ETH
            fig_price.add_trace(go.Scatter(
                x=eth_data['Date'],
                y=eth_data['Close'],
                mode='lines',
                name='ETH',
                line=dict(color='#627eea', width=2),
                hovertemplate='<b>ETH</b><br>Data: %{x}<br>Preço: $%{y:,.0f}<extra></extra>'
            ))
            
            # Marcar picos
            if len(peaks) > 0:
                fig_price.add_trace(go.Scatter(
                    x=eth_data.iloc[peaks]['Date'],
                    y=eth_data.iloc[peaks]['Close'],
                    mode='markers',
                    name='Picos ETH',
                    marker=dict(color='red', size=8, symbol='triangle-up'),
                    hovertemplate='<b>Pico ETH</b><br>Data: %{x}<br>Preço: $%{y:,.0f}<extra></extra>'
                ))
            
            fig_price.update_yaxes(title_text="Preço ETH (USD)")
            
        else:  # BTC + ETH (Preços Reais - Eixo Único)
            # Dados do BTC e ETH
            btc_data = df_2015[df_2015['Symbol'] == 'BTC'].copy()
            eth_data = df_2015[df_2015['Symbol'] == 'ETH'].copy()
            
            # Calcular picos históricos para ambos
            btc_data['Peak'] = btc_data['Close'].expanding().max()
            btc_picos = btc_data[btc_data['Close'] == btc_data['Peak']]
            
            eth_data['Peak'] = eth_data['Close'].expanding().max()
            eth_picos = eth_data[eth_data['Close'] == eth_data['Peak']]
            
            # Linha BTC
            fig_price.add_trace(go.Scatter(
                x=btc_data['Date'],
                y=btc_data['Close'],
                mode='lines',
                name='BTC',
                line=dict(color='#f7931a', width=3),
                hovertemplate='<b>BTC</b><br>Data: %{x}<br>Preço: $%{y:,.0f}<extra></extra>'
            ))
            
            # Picos BTC
            fig_price.add_trace(go.Scatter(
                x=btc_picos['Date'],
                y=btc_picos['Close'],
                mode='markers',
                name='Picos BTC',
                marker=dict(color='#ff6b35', size=8, symbol='triangle-up'),
                hovertemplate='<b>Pico BTC</b><br>Data: %{x}<br>Preço: $%{y:,.0f}<extra></extra>'
            ))
            
            # Linha ETH
            fig_price.add_trace(go.Scatter(
                x=eth_data['Date'],
                y=eth_data['Close'],
                mode='lines',
                name='ETH',
                line=dict(color='#627eea', width=3),
                hovertemplate='<b>ETH</b><br>Data: %{x}<br>Preço: $%{y:,.0f}<extra></extra>'
            ))
            
            # Picos ETH
            fig_price.add_trace(go.Scatter(
                x=eth_picos['Date'],
                y=eth_picos['Close'],
                mode='markers',
                name='Picos ETH',
                marker=dict(color='#4a90e2', size=8, symbol='triangle-up'),
                hovertemplate='<b>Pico ETH</b><br>Data: %{x}<br>Preço: $%{y:,.0f}<extra></extra>'
            ))
            
            fig_price.update_yaxes(title_text="Preço (USD)")
        
        # Layout comum
        fig_price.update_layout(
            height=450,
            margin={'t': 20, 'b': 50, 'l': 60, 'r': 20},  # Margem direita normal
            xaxis_title="Data",
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'size': 12}
        )
        
        fig_price.update_xaxes(gridcolor='rgba(128,128,128,0.2)', gridwidth=1)
        fig_price.update_yaxes(gridcolor='rgba(128,128,128,0.2)', gridwidth=1)
        
        st.plotly_chart(fig_price, use_container_width=True, config={'displayModeBar': False})

    # Gráfico da Direita: Volume de Transações
    with col_right:
        st.subheader("Volume de Transações")
        
        # Selectbox para escolher a criptomoeda
        selected_volume_crypto = st.selectbox(
            "Escolha a criptomoeda:",
            options=["BTC", "ETH"],
            index=0,
            key="volume_crypto"
        )
        
        # Filtrar dados da cripto selecionada
        volume_data = df_2015[df_2015['Symbol'] == selected_volume_crypto].copy()
        
        # Criar gráfico apenas do volume
        fig_right = go.Figure()
        
        # Gráfico de volume (barras)
        fig_right.add_trace(
            go.Bar(
                x=volume_data['Date'],
                y=volume_data['Volume'],
                name='Volume',
                marker_color='#f7931a' if selected_volume_crypto == 'BTC' else '#627eea',
                opacity=0.7,
                hovertemplate=f'<b>{selected_volume_crypto} Volume</b><br>' +
                            'Data: %{x}<br>' +
                            'Volume: %{y:,.0f}<br>' +
                            '<extra></extra>'
            )
        )
        
        # Layout igual ao gráfico da esquerda
        fig_right.update_layout(
            height=450,  # MESMA ALTURA do gráfico da esquerda
            margin={'t': 20, 'b': 50, 'l': 60, 'r': 20},  # MESMAS MARGENS
            xaxis_title="Data",
            yaxis_title="Volume de Transações",
            hovermode='x unified',
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'size': 12}
        )
        
        # Grid igual ao da esquerda
        fig_right.update_xaxes(gridcolor='rgba(128,128,128,0.2)', gridwidth=1)
        fig_right.update_yaxes(gridcolor='rgba(128,128,128,0.2)', gridwidth=1)
        
        st.plotly_chart(fig_right, use_container_width=True, config={'displayModeBar': False})

    # ----------------------------------------------------------------------------------------------------- #

elif menu == "Análise BTC 2021":
    st.title("📈 Análise BTC 2021 (Jan - Jul)")

    # --- Título da seção ---
    st.header("2021 - Janeiro até Julho")
    st.subheader("7 Meses de 2021 - Crescimento Diário BTC")

    dates = pd.date_range("2021-01-01", "2021-07-31")
    close = np.cumprod(1 + np.random.normal(0, 0.02, len(dates))) * 30000
    volume = np.random.randint(1e9, 5e9, len(dates))
    df = pd.DataFrame({"Date": dates, "Close": close, "Volume": volume})

    # --- Cálculos principais ---
    df["Return"] = df["Close"].pct_change()
    df["CumReturn"] = (1 + df["Return"]).cumprod() - 1
    df["DayType"] = df["Return"].apply(lambda x: "positive" if x > 0 else ("negative" if x < 0 else "neutral"))

    # Seleção do usuário
    opcao = st.selectbox(
        "Escolha a análise:",
        [
            "Retornos Diários",
            "Retorno Acumulado",
            "Correlação Volume",
            "Contagem de Dias",
            "Outliers"
        ]
    )

    # --- Visualizações ---
    if opcao == "Retornos Diários":
        fig = px.bar(df, x="Date", y="Return", color=df["Return"] > 0,
                    color_discrete_map={True: "green", False: "red"},
                    title="Retorno Diário BTC (2021 Jan-Jul)")
        st.plotly_chart(fig, use_container_width=True)

    elif opcao == "Retorno Acumulado":
        fig = px.line(df, x="Date", y="CumReturn", title="Retorno Acumulado BTC (2021 Jan-Jul)")
        st.plotly_chart(fig, use_container_width=True)

    elif opcao == "Correlação Volume":
        corr1 = df["Volume"].corr(df["Return"].abs())
        corr2 = df["Volume"].corr(df["Close"])

        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=corr1,
            title={"text": "Volume × |Retorno|"},
            gauge={'axis': {'range': [-1, 1]}}
        ))
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=corr2,
            title={"text": "Volume × Preço"},
            gauge={'axis': {'range': [-1, 1]}},
            domain={'row': 1, 'column': 0}
        ))
        fig.update_layout(
            grid={'rows': 2, 'columns': 1, 'pattern': "independent"},
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)

    elif opcao == "Contagem de Dias":
        counts = df["DayType"].value_counts()
        fig = px.bar(counts, x=counts.index, y=counts.values,
                    title="Contagem de Dias (Positivos / Negativos / Neutros)",
                    color=counts.index,
                    color_discrete_map={"positive": "green", "negative": "red", "neutral": "gray"})
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(counts.rename("Quantidade"))

    elif opcao == "Outliers":
        df["zscore"] = (df["Return"] - df["Return"].mean())/df["Return"].std()
        outliers = df[np.abs(df["zscore"]) > 2]
        pct_outliers = len(outliers) / len(df) * 100

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pct_outliers,
            title={"text": "Outliers em Retornos (%)"},
            gauge={'axis': {'range': [0, 100]}}
        ))
        st.plotly_chart(fig, use_container_width=True)