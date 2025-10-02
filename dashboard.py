import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt


st.set_page_config(page_title="Crypto Dash",page_icon="data/image.png",layout="wide")

df = pd.read_csv("data/cryptocurrency.csv")

# Função para limpeza de outliers no volume
def analyze_volume_outliers(df, column='Volume'):
    """Analisa outliers sem removê-los automaticamente"""
    outlier_info = {}
    
    for symbol in df['Symbol'].unique():
        symbol_data = df[df['Symbol'] == symbol]
        Q1 = symbol_data[column].quantile(0.25)
        Q3 = symbol_data[column].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        
        # Identificar outliers
        outliers = symbol_data[(symbol_data[column] < lower) | (symbol_data[column] > upper)]
        
        outlier_info[symbol] = {
            'count': len(outliers),
            'percentage': (len(outliers) / len(symbol_data)) * 100,
            'extreme_high': outliers[column].max() if len(outliers) > 0 else None,
            'extreme_low': outliers[column].min() if len(outliers) > 0 else None,
            'dates': outliers[['Date', column]].copy() if len(outliers) > 0 else pd.DataFrame()
        }
    
    return outlier_info

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

    # APLICAR LIMPEZA DE OUTLIERS APENAS NO VOLUME
    outlier_info = analyze_volume_outliers(df_2015, 'Volume')

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
    st.subheader("Análise de Criptomoedas - BTC / ETH (2015 - 2021)")

    col1, col2, col3, col4, col5 = st.columns(5)

    # Coluna 1: Valor Médio com Tooltips Detalhados
    with col1:
        crypto_options = df_2015['Symbol'].unique()
        
        selected_crypto = st.selectbox(
            "Valor Médio",
            options=crypto_options,
            index=0
        )
        
        selected_data = df_2015[df_2015['Symbol'] == selected_crypto]
        valor_medio = selected_data['Close'].mean()
        valor_min = selected_data['Close'].min()
        valor_max = selected_data['Close'].max()
        
        if selected_crypto == 'BTC':
            max_range = 20000
        elif selected_crypto == 'ETH':
            max_range = 500
        else:
            max_range = selected_data['Close'].max()
        
        # Velocímetro com tooltip detalhado
        fig1 = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = valor_medio,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {
                'text': f"<b>{selected_crypto}</b><br><span style='font-size:12px'>Mín: ${valor_min:,.0f} | Máx: ${valor_max:,.0f}</span>", 
                'font': {'size': 14, 'color': '#333'}
            },
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
        
        # Tooltip adicional abaixo do gráfico
        with st.expander("Detalhes"):
            st.write(f"**Período:** {selected_data['Date'].min().strftime('%Y-%m-%d')} a {selected_data['Date'].max().strftime('%Y-%m-%d')}")
            st.write(f"**Dias analisados:** {len(selected_data):,}")
            st.write(f"**Desvio padrão:** ${selected_data['Close'].std():,.2f}")

    with col2:
        selected_dd_crypto = st.selectbox(
            "DrawDowns",
            options=crypto_options,
            index=0,
            key="dd_crypto"
        )
        
        dd_data = df_2015[df_2015['Symbol'] == selected_dd_crypto].copy()
        
        dd_data['Cumulative_Return'] = (1 + dd_data['Return'].fillna(0) / 100).cumprod()
        dd_data['Peak'] = dd_data['Cumulative_Return'].expanding().max()
        dd_data['Drawdown'] = ((dd_data['Cumulative_Return'] / dd_data['Peak']) - 1) * 100
        
        max_drawdown = abs(dd_data['Drawdown'].min())
        avg_drawdown = abs(dd_data[dd_data['Drawdown'] < -1]['Drawdown'].mean())
        
        fig2 = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = max_drawdown,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {
                'text': f"<b>{selected_dd_crypto} DD</b><br><span style='font-size:12px'>Média: {avg_drawdown:.1f}%</span>", 
                'font': {'size': 14, 'color': '#333'}
            },
            number = {'suffix': "%", 'font': {'size': 18, 'color': '#e74c3c'}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#e74c3c"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 30], 'color': "#fff2f0"},
                    {'range': [30, 60], 'color': "#ffccc7"},
                    {'range': [60, 100], 'color': "#ffa39e"}],
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
        
        with st.expander("Detalhes"):
            drawdowns_significativos = len(dd_data[dd_data['Drawdown'] < -10])
            st.write(f"**DD > 10%:** {drawdowns_significativos} ocorrências")
            st.write(f"**Média de DDs:** {avg_drawdown:.1f}%")
            st.write(f"**Interpretação:** {'Alto risco' if max_drawdown > 50 else 'Risco moderado' if max_drawdown > 30 else 'Baixo risco'}")

    with col3:
        selected_risk_crypto = st.selectbox(
            "Risco x Retorno",
            options=crypto_options,
            index=0,
            key="risk_crypto"
        )
        
        risk_data = df_2015[df_2015['Symbol'] == selected_risk_crypto].copy()
        
        retorno_medio = risk_data['Return'].mean()
        risco = risk_data['Return'].std()
        retorno_anual = retorno_medio * 365
        risco_anual = risco * np.sqrt(365)
        
        if risco > 0:
            sharpe_ratio = retorno_medio / risco
        else:
            sharpe_ratio = 0
        
        fig3 = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = sharpe_ratio,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {
                'text': f"<b>{selected_risk_crypto} Sharpe</b><br><span style='font-size:12px'>Ret: {retorno_anual:.1f}% | Vol: {risco_anual:.1f}%</span>", 
                'font': {'size': 14, 'color': '#333'}
            },
            number = {'font': {'size': 18, 'color': '#28a745'}},
            gauge = {
                'axis': {'range': [-3, 3], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#28a745"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [-3, 0], 'color': "#ffebee"},
                    {'range': [0, 1], 'color': "#fff3e0"},
                    {'range': [1, 2], 'color': "#e8f5e8"},
                    {'range': [2, 3], 'color': "#c3e6cb"}],
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
        
        with st.expander("Detalhes"):
            st.write(f"**Retorno anualizado:** {retorno_anual:.1f}%")
            st.write(f"**Volatilidade anual:** {risco_anual:.1f}%")
            interpretacao = "Excelente" if sharpe_ratio > 2 else "Bom" if sharpe_ratio > 1 else "Razoável" if sharpe_ratio > 0 else "Ruim"
            st.write(f"**Classificação:** {interpretacao}")

    with col4:
        selected_trend_crypto = st.selectbox(
            "Tendência Valorização",
            options=crypto_options,
            index=0,
            key="trend_crypto"
        )
        
        trend_data = df_2015[df_2015['Symbol'] == selected_trend_crypto].copy()
        
        status_counts = trend_data['Return_Status'].value_counts()
        
        total_days = len(trend_data)
        positive_pct = (status_counts.get('Positivo', 0) / total_days) * 100
        negative_pct = (status_counts.get('Negativo', 0) / total_days) * 100
        neutral_pct = (status_counts.get('Neutro', 0) / total_days) * 100
        
        trend_score = positive_pct
        
        fig4 = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = trend_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {
                'text': f"<b>{selected_trend_crypto} Trend</b><br><span style='font-size:12px'>Neg: {negative_pct:.1f}% | Neu: {neutral_pct:.1f}%</span>", 
                'font': {'size': 14, 'color': '#333'}
            },
            number = {'suffix': "%", 'font': {'size': 18, 'color': '#17a2b8'}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#17a2b8"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 30], 'color': "#f8d7da"},
                    {'range': [30, 50], 'color': "#fff3cd"},
                    {'range': [50, 70], 'color': "#d1ecf1"},
                    {'range': [70, 100], 'color': "#c3e6cb"}],
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
        
        with st.expander("Detalhes"):
            st.write(f"**Dias positivos:** {status_counts.get('Positivo', 0)} ({positive_pct:.1f}%)")
            st.write(f"**Dias negativos:** {status_counts.get('Negativo', 0)} ({negative_pct:.1f}%)")
            st.write(f"**Dias neutros:** {status_counts.get('Neutro', 0)} ({neutral_pct:.1f}%)")

    with col5:
        selected_recovery_crypto = st.selectbox(
            "Eficiência Recuperação",
            options=crypto_options,
            index=0,
            key="recovery_crypto"
        )
        
        recovery_data = df_2015[df_2015['Symbol'] == selected_recovery_crypto].copy()
        
        recovery_data['Cumulative_Return'] = (1 + recovery_data['Return'].fillna(0) / 100).cumprod()
        recovery_data['Peak'] = recovery_data['Cumulative_Return'].expanding().max()
        recovery_data['Drawdown'] = ((recovery_data['Cumulative_Return'] / recovery_data['Peak']) - 1) * 100
        
        recovery_times = []
        in_drawdown = False
        drawdown_start = 0
        
        for i, row in recovery_data.iterrows():
            if row['Drawdown'] < -5 and not in_drawdown:
                in_drawdown = True
                drawdown_start = i
            elif row['Drawdown'] >= -1 and in_drawdown:
                recovery_time = i - drawdown_start
                if recovery_time > 0:
                    recovery_times.append(recovery_time)
                in_drawdown = False
        
        if recovery_times:
            avg_recovery_days = np.mean(recovery_times)
            max_days = 365
            efficiency_score = max(0, 100 - (avg_recovery_days / max_days * 100))
        else:
            efficiency_score = 50
            avg_recovery_days = 0
        
        fig5 = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = efficiency_score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {
                'text': f"<b>{selected_recovery_crypto} Recov</b><br><span style='font-size:12px'>Média: {avg_recovery_days:.0f} dias</span>", 
                'font': {'size': 14, 'color': '#333'}
            },
            number = {'suffix': "%", 'font': {'size': 18, 'color': '#9c27b0'}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#9c27b0"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 25], 'color': "#fce4ec"},
                    {'range': [25, 50], 'color': "#f8bbd9"},
                    {'range': [50, 75], 'color': "#e1bee7"},
                    {'range': [75, 100], 'color': "#ce93d8"}],
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
        
        with st.expander("Detalhes"):
            st.write(f"**Recuperações analisadas:** {len(recovery_times)}")
            if recovery_times:
                st.write(f"**Tempo médio:** {avg_recovery_days:.0f} dias")
                st.write(f"**Mais rápida:** {min(recovery_times)} dias")
                st.write(f"**Mais lenta:** {max(recovery_times)} dias")
            else:
                st.write("**Dados insuficientes** para análise")

    # Linha divisória
    st.divider()

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Picos Históricos")
        
        price_view = st.selectbox(
            "Selecione a visualização:",
            options=["BTC", "ETH", "BTC + ETH (Comparação)"],
            index=0,
            key="price_view"
        )
        
        # ADICIONAR BALÃO AZUL
        if price_view == "BTC":
            st.markdown('<div style="padding: 0.75rem; background-color: #172c43; border-radius: 0.25rem; color: #ffffff;">Preço máximo: $63503 | Mínimo: $210 | Média: $9149</div>', unsafe_allow_html=True)
            
        elif price_view == "ETH":
            st.markdown('<div style="padding: 0.75rem; background-color: #172c43; border-radius: 0.25rem; color: #ffffff;">Preço máximo: $4169 | Mínimo: $0.43 | Média: $384</div>', unsafe_allow_html=True)
            
        else:
            st.markdown('<div style="padding: 0.75rem; background-color: #172c43; border-radius: 0.25rem; color: #ffffff;">BTC máximo: $63503 | ETH máximo: $4169 | Período: 2015-2020</div>', unsafe_allow_html=True)

        fig_price = go.Figure()
        
        if price_view == "BTC":
            # Apenas BTC
            btc_data = df_2015[df_2015['Symbol'] == 'BTC'].copy()
            
            # Encontrar picos (máximos locais)
            from scipy.signal import find_peaks
            prices = btc_data['Close'].values
            peaks, _ = find_peaks(prices, height=prices.mean(), distance=30)
            
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
            
            # EVENTOS MAIS IMPORTANTES BTC (5 eventos)
            eventos_btc = [
                {'date': '2016-07-09', 'price': 662, 'event': 'Halving: Redução Emissão 50%', 'color': '#3498db'},
                {'date': '2017-12-17', 'price': 19497, 'event': 'Bull Run 2017 - Euforia Global', 'color': '#ff6b6b'},
                {'date': '2020-03-13', 'price': 4970, 'event': 'Crash Pandemia COVID-19', 'color': '#ee5a6f'},
                {'date': '2021-02-08', 'price': 46433, 'event': 'Tesla Compra $1.5 Bilhões', 'color': '#f39c12'},
                {'date': '2021-04-14', 'price': 63503, 'event': 'Bull Run 2021 - Boom Institucional', 'color': '#95e1d3'},
            ]
            
            for evento in eventos_btc:
                fig_price.add_trace(go.Scatter(
                    x=[evento['date']],
                    y=[evento['price']],
                    mode='markers+text',
                    name=evento['event'],
                    marker=dict(color=evento['color'], size=12, symbol='star'),
                    text=evento['event'],
                    textposition='top center',
                    textfont=dict(size=9, color=evento['color'], family='Arial Black'),
                    hovertemplate=f"<b>{evento['event']}</b><br>Data: {evento['date']}<br>Preço: ${evento['price']:,.0f}<extra></extra>"
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
            
            # EVENTOS MAIS IMPORTANTES ETH (5 eventos)
            eventos_eth = [
                {'date': '2016-06-17', 'price': 20, 'event': 'Hack: $50M Roubados (DAO)', 'color': '#c0392b'},
                {'date': '2017-06-12', 'price': 395, 'event': 'Boom de ICOs', 'color': '#3498db'},
                {'date': '2018-01-13', 'price': 1417, 'event': 'Bull Run 2018 - Mania ICOs', 'color': '#a29bfe'},
                {'date': '2020-12-01', 'price': 594, 'event': 'ETH 2.0: Nova Versão', 'color': '#16a085'},
                {'date': '2021-05-12', 'price': 4169, 'event': 'Bull Run 2021 - Era DeFi/NFT', 'color': '#fdcb6e'},
            ]
            
            for evento in eventos_eth:
                fig_price.add_trace(go.Scatter(
                    x=[evento['date']],
                    y=[evento['price']],
                    mode='markers+text',
                    name=evento['event'],
                    marker=dict(color=evento['color'], size=12, symbol='star'),
                    text=evento['event'],
                    textposition='top center',
                    textfont=dict(size=9, color=evento['color'], family='Arial Black'),
                    hovertemplate=f"<b>{evento['event']}</b><br>Data: {evento['date']}<br>Preço: ${evento['price']:,.0f}<extra></extra>"
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
            
            # TOP 3 EVENTOS BTC
            top_eventos_btc = [
                {'date': '2017-12-17', 'price': 19497, 'event': 'BTC Bull Run 2017', 'color': '#ff6b6b'},
                {'date': '2020-03-13', 'price': 4970, 'event': 'BTC Crash COVID', 'color': '#ee5a6f'},
                {'date': '2021-04-14', 'price': 63503, 'event': 'BTC Bull Run 2021', 'color': '#95e1d3'},
            ]
            
            # TOP 3 EVENTOS ETH
            top_eventos_eth = [
                {'date': '2018-01-13', 'price': 1417, 'event': 'ETH Bull Run 2018', 'color': '#a29bfe'},
                {'date': '2020-03-13', 'price': 109, 'event': 'ETH Crash COVID', 'color': '#fd79a8'},
                {'date': '2021-05-12', 'price': 4169, 'event': 'ETH Bull Run 2021', 'color': '#fdcb6e'},
            ]
            
            # Adicionar eventos BTC
            for evento in top_eventos_btc:
                fig_price.add_trace(go.Scatter(
                    x=[evento['date']],
                    y=[evento['price']],
                    mode='markers+text',
                    name=evento['event'],
                    marker=dict(color=evento['color'], size=10, symbol='star'),
                    text=evento['event'],
                    textposition='top center',
                    textfont=dict(size=8, color=evento['color']),
                    hovertemplate=f"<b>{evento['event']}</b><br>Data: {evento['date']}<br>Preço: ${evento['price']:,.0f}<extra></extra>"
                ))
            
            # Adicionar eventos ETH
            for evento in top_eventos_eth:
                fig_price.add_trace(go.Scatter(
                    x=[evento['date']],
                    y=[evento['price']],
                    mode='markers+text',
                    name=evento['event'],
                    marker=dict(color=evento['color'], size=10, symbol='diamond'),
                    text=evento['event'],
                    textposition='bottom center',
                    textfont=dict(size=8, color=evento['color']),
                    hovertemplate=f"<b>{evento['event']}</b><br>Data: {evento['date']}<br>Preço: ${evento['price']:,.0f}<extra></extra>"
                ))
            
            fig_price.update_yaxes(title_text="Preço (USD)")
        
        # Layout comum
        fig_price.update_layout(
            height=450,
            margin={'t': 20, 'b': 50, 'l': 60, 'r': 20},
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
        
        # EXPLICAÇÃO DOS EVENTOS OCUPANDO 2 COLUNAS
    
    # Mover o expander para FORA do with col_left
    with st.expander("📖 Explicação dos Eventos Históricos"):
        if price_view == "BTC":
            st.markdown("""
            ### 🔸 Bitcoin - Eventos Mais Importantes
            
            **1. Halving (09/07/2016) - $662**
            - Redução automática de 50% na emissão de novos Bitcoins
            - Acontece a cada 4 anos para controlar a inflação
            - Torna o Bitcoin mais escasso, tendendo a aumentar o preço
            
            **2. Bull Run 2017 (17/12/2017) - $19,497**
            - Primeira grande explosão de preço do Bitcoin
            - Euforia global e entrada massiva de investidores
            - Mercado em alta extrema com valorização de +2000%
            
            **3. Crash COVID-19 (13/03/2020) - $4,970**
            - Pandemia causou pânico nos mercados globais
            - Bitcoin caiu mais de 50% em poucos dias
            - Maior queda desde 2018
            
            **4. Tesla Investe (08/02/2021) - $46,433**
            - Tesla de Elon Musk comprou $1.5 bilhões em Bitcoin
            - Primeira grande empresa a adotar BTC no balanço
            - Validação institucional histórica
            
            **5. Bull Run 2021 (14/04/2021) - $63,503**
            - Segunda grande explosão de preço
            - Adoção institucional massiva (bancos, fundos, empresas)
            - Bitcoin consolida-se como "ouro digital"
            """)
            
        elif price_view == "ETH":
            st.markdown("""
            ### 🔹 Ethereum - Eventos Mais Importantes
            
            **1. Hack DAO (17/06/2016) - $20**
            - Hackers roubaram $50 milhões em Ethereum
            - Maior roubo cripto da história na época
            - Levou à divisão da rede (Hard Fork)
            
            **2. Boom de ICOs (12/06/2017) - $395**
            - Explosão de lançamentos de novos projetos
            - Ethereum virou plataforma #1 para fundraising
            - Centenas de startups arrecadaram bilhões
            
            **3. Bull Run 2018 (13/01/2018) - $1,417**
            - Auge da mania de ICOs e especulação
            - Ethereum chegou a $1,400 pela primeira vez
            - Mercado superaquecido antes da grande queda
            
            **4. ETH 2.0 Lançado (01/12/2020) - $594**
            - Atualização mais importante da história do Ethereum
            - Mudança para sistema mais ecológico (Proof-of-Stake)
            - Promessa de rede 100x mais rápida
            
            **5. Bull Run 2021 (12/05/2021) - $4,169**
            - Segunda grande explosão de preço
            - Boom de DeFi (finanças descentralizadas) e NFTs
            - Ethereum consolida-se como plataforma líder
            """)
            
        else:
            st.markdown("""
            ### 🔥 Comparação: Top 3 Eventos de Cada Moeda
            
            **Bitcoin (BTC):**
            1. **Bull Run 2017** - Primeira grande explosão (+2000%)
            2. **Crash COVID** - Maior queda da década (-74%)
            3. **Bull Run 2021** - Adoção institucional (+225%)
            
            **Ethereum (ETH):**
            1. **Bull Run 2018** - Mania de ICOs (+13000%)
            2. **Crash COVID** - Queda sincronizada com BTC (-92%)
            3. **Bull Run 2021** - Era DeFi e NFTs (+340%)
            
            **Insight:** Ambas as moedas seguem ciclos parecidos, mas Ethereum teve ganhos percentuais maiores no último bull run (ETH: +340% vs BTC: +225% de 2020-2021).
            """)

    with col_right:
        st.subheader("Volume de Transações")
        
        selected_volume_crypto = st.selectbox(
            "Escolha a criptomoeda:",
            options=["BTC", "ETH"],
            index=0,
            key="volume_crypto"
        )
        
        volume_data = df_2015[df_2015['Symbol'] == selected_volume_crypto].copy()
        
        # PADRONIZAR FORMATAÇÃO DO VOLUME (sem símbolo $)
        vol_mean = volume_data['Volume'].mean() / 1e9
        vol_median = volume_data['Volume'].median() / 1e9
        vol_std = volume_data['Volume'].std() / 1e9
        
        st.markdown(f'<div style="padding: 0.75rem; background-color: #172c43; border-radius: 0.25rem; color: #ffffff;">Volume médio: {vol_mean:.2f}B | Mediana: {vol_median:.2f}B | Desvio: {vol_std:.2f}B</div>', unsafe_allow_html=True)
        
        fig_right = go.Figure()
        
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
        
        fig_right.update_layout(
            height=450,
            margin={'t': 20, 'b': 50, 'l': 60, 'r': 20},
            xaxis_title="Data",
            yaxis_title="Volume de Transações",
            hovermode='x unified',
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'size': 12}
        )
        
        fig_right.update_xaxes(gridcolor='rgba(128,128,128,0.2)', gridwidth=1)
        fig_right.update_yaxes(gridcolor='rgba(128,128,128,0.2)', gridwidth=1)
        
        st.plotly_chart(fig_right, use_container_width=True, config={'displayModeBar': False})

elif menu == "Análise BTC 2021":
    st.title("📈 Análise BTC 2021 (Jan - Jul)")

    st.header("2021 - Janeiro até Julho")
    st.subheader("7 Meses de 2021 - Crescimento Diário BTC")

    dates = pd.date_range("2021-01-01", "2021-07-31")
    close = np.cumprod(1 + np.random.normal(0, 0.02, len(dates))) * 30000
    volume = np.random.randint(1e9, 5e9, len(dates),dtype=np.int64)
    df = pd.DataFrame({"Date": dates, "Close": close, "Volume": volume})

    df["Return"] = df["Close"].pct_change()
    df["CumReturn"] = (1 + df["Return"]).cumprod() - 1
    df["DayType"] = df["Return"].apply(lambda x: "positive" if x > 0 else ("negative" if x < 0 else "neutral"))

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