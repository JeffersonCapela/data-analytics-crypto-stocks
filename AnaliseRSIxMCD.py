import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from ta.trend import MACD
from ta.momentum import RSIIndicator

# Função para baixar dados e analisar o ativo
def analisar_ativo(ticker):
    # Baixar os dados do ativo
    df = yf.download(ticker, start='2022-10-01', end='2024-10-01')
    df.reset_index(inplace=True)

    # Calcular o MACD
    macd = MACD(df['Close'], window_slow=26, window_fast=12, window_sign=9)
    df['MACD'] = macd.macd()
    df['Signal_Line'] = macd.macd_signal()
    df['MACD_Hist'] = macd.macd_diff()

    # Calcular o RSI
    rsi = RSIIndicator(df['Close'], window=14)
    df['RSI'] = rsi.rsi()

    # Plotar o gráfico do MACD e Histogram
    plt.figure(figsize=(14, 7))

    # Gráfico do MACD
    plt.subplot(2, 1, 1)
    plt.plot(df['Date'], df['MACD'], label='MACD', color='blue')
    plt.plot(df['Date'], df['Signal_Line'], label='Signal Line', color='red')
    
    # Gráfico do histograma
    plt.bar(df['Date'], df['MACD_Hist'], label='MACD Histogram', color='green', alpha=0.5)
    plt.title(f'MACD e Histogram para {ticker}')
    plt.xlabel('Data')
    plt.ylabel('Valores')
    plt.legend()

    # Gráfico do RSI
    plt.subplot(2, 1, 2)
    plt.plot(df['Date'], df['RSI'], label='RSI', color='orange')
    plt.axhline(70, linestyle='--', alpha=0.5, color='red')
    plt.axhline(30, linestyle='--', alpha=0.5, color='green')
    plt.title('RSI')
    plt.xlabel('Data')
    plt.ylabel('RSI')
    plt.legend()

    plt.tight_layout()
    plt.show()

# Lista de ativos para análise
ativos = ['AAPL34.SA', 'BTC-USD', 'ETH-USD']  # Adicione outros ativos que você deseja analisar

# Analisar cada ativo na lista
for ativo in ativos:
    analisar_ativo(ativo)
