import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import seaborn as sns
from ta import add_all_ta_features
import cvxpy as cp
from tabulate import tabulate
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from ta.trend import SMAIndicator, EMAIndicator, MACD
from ta.momentum import RSIIndicator

# Lista de ativos de ações e criptomoedas
ativos_acoes = ['AAPL34.SA', 'ITUB4.SA', 'BBDC4.SA', 'MGLU3.SA', 'PETR4.SA', 'VALE3.SA', 'WEGE3.SA', 'RADL3.SA', 'OIBR3.SA', 'SMAL11.SA']
ativos_criptos = ['BTC-USD', 'ETH-USD', 'XRP-USD', 'LTC-USD', 'ADA-USD', 'SOL-USD', 'BNB-USD', 'DOGE-USD', 'LINK-USD', 'DOT-USD']

#Função para ler os dados do arquivo CSV e fazer a análise

def analisar_ativo(ativo):
    if ativo in ativos_acoes:
        # Obter dados do Yahoo Finance para ações
        df = yf.download(ativo, start="2014-11-08", end="2024q-04-14")
    else:
        # Obter dados do Yahoo Finance para criptomoedas
        df = yf.download(ativo, start="2014-11-08", end="2024-04-14")

    # Adicionar as métricas técnicas usando a biblioteca TA
    df = add_all_ta_features(df, "Open", "High", "Low", "Close", "Volume", fillna=True)

    # Gráfico de linha do preço de fechamento (Close) diário
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df['Close'], label='Close', color='blue')
    plt.title(f'Desempenho Diário de "Close" - {ativo}')
    plt.xlabel('Data')
    plt.ylabel('Close')
    plt.legend()
    plt.show()

    # Análise mensal do preço de fechamento (Close)
    analise_mensal = df['Close'].resample('M').mean()

    # Gráfico de linha do preço de fechamento (Close) mensal
    plt.figure(figsize=(10, 6))
    analise_mensal.plot()
    plt.title(f'Análise Mensal de "Close" - {ativo}')
    plt.xlabel('Data')
    plt.ylabel('Média de "Close"')

    # Adicionar linhas de Fibonacci
    min_price = analise_mensal.min()
    max_price = analise_mensal.max()
    fibonacci_levels = [0, 0.236, 0.382, 0.618, 1]

    for level in fibonacci_levels:
        price = min_price + level * (max_price - min_price)
        plt.axhline(price, color='red', linestyle='--', alpha=0.5, label=f'Fib {int(level * 100)}%')

    plt.legend()
    plt.show()

    return df

# Dicionário para armazenar os DataFrames
dataframes_acoes = {}
dataframes_criptos = {}

# Loop para analisar todos os ativos de ações e criptomoedas na lista
for ativo in ativos_acoes:
    df = analisar_ativo(ativo)
    dataframes_acoes[ativo] = df

for ativo in ativos_criptos:
    df = analisar_ativo(ativo)
    dataframes_criptos[ativo] = df

# Análise de Markowitz para otimização de portfólio - Ações
# Combine os DataFrames de ações em um único DataFrame
df_acoes = pd.concat(dataframes_acoes.values(), axis=1)
df_acoes = df_acoes.dropna()

# Retornos diários de ações
returns_acoes = df_acoes['Close'].pct_change().dropna()

# Número de portfólios simulados
num_portfolios = 200

# Listas para armazenar resultados
results_acoes = np.zeros((3, num_portfolios))
risk_free_rate = 0.02

for i in range(num_portfolios):
    weights = np.random.random(len(returns_acoes.columns))
    weights /= weights.sum()
    
    # Retorno esperado
    portfolio_return = np.sum(returns_acoes.mean() * weights) * 252
    
    # Risco
    portfolio_stddev = np.sqrt(np.dot(weights.T, np.dot(returns_acoes.cov() * 252, weights)))
    
    # Índice de Sharpe
    results_acoes[0, i] = portfolio_return
    results_acoes[1, i] = portfolio_stddev
    results_acoes[2, i] = (portfolio_return - risk_free_rate) / portfolio_stddev

# Encontrar portfólio com o melhor Índice de Sharpe para ações
max_sharpe_idx_acoes = np.argmax(results_acoes[2])
best_sharpe_return_acoes = results_acoes[0, max_sharpe_idx_acoes]
best_sharpe_stddev_acoes = results_acoes[1, max_sharpe_idx_acoes]
best_sharpe_ratio_acoes = results_acoes[2, max_sharpe_idx_acoes]

# Análise de Markowitz para otimização de portfólio - Criptomoedas
# Combine os DataFrames de criptomoedas em um único DataFrame
df_criptos = pd.concat(dataframes_criptos.values(), axis=1)
df_criptos = df_criptos.dropna()

# Retornos diários de criptomoedas
returns_criptos = df_criptos['Close'].pct_change().dropna()

# Listas para armazenar resultados
results_criptos = np.zeros((3, num_portfolios))
risk_free_rate = 0.02

for i in range(num_portfolios):
    weights = np.random.random(len(returns_criptos.columns))
    weights /= weights.sum()
    
    # Retorno esperado
    portfolio_return = np.sum(returns_criptos.mean() * weights) * 252
    
    # Risco
    portfolio_stddev = np.sqrt(np.dot(weights.T, np.dot(returns_criptos.cov() * 252, weights)))
    
    # Índice de Sharpe
    results_criptos[0, i] = portfolio_return
    results_criptos[1, i] = portfolio_stddev
    results_criptos[2, i] = (portfolio_return - risk_free_rate) / portfolio_stddev

# Encontrar portfólio com o melhor Índice de Sharpe para criptomoedas
max_sharpe_idx_criptos = np.argmax(results_criptos[2])
best_sharpe_return_criptos = results_criptos[0, max_sharpe_idx_criptos]
best_sharpe_stddev_criptos = results_criptos[1, max_sharpe_idx_criptos]
best_sharpe_ratio_criptos = results_criptos[2, max_sharpe_idx_criptos]

# Combinando ações e criptomoedas
# Adicione retornos de criptomoedas à lista de ativos de ações
ativos_combinados = ativos_acoes + ativos_criptos
df_combinado = pd.concat([df_acoes['Close'], df_criptos['Close']], axis=1)
df_combinado.columns = ativos_combinados
returns_combinado = df_combinado.pct_change().dropna()

# Listas para armazenar resultados
results_combinado = np.zeros((3, num_portfolios))

for i in range(num_portfolios):
    weights = np.random.random(len(returns_combinado.columns))
    weights /= weights.sum()
    
    # Retorno esperado
    portfolio_return = np.sum(returns_combinado.mean() * weights) * 252
    
    # Risco
    portfolio_stddev = np.sqrt(np.dot(weights.T, np.dot(returns_combinado.cov() * 252, weights)))
    
    # Índice de Sharpe
    results_combinado[0, i] = portfolio_return
    results_combinado[1, i] = portfolio_stddev
    results_combinado[2, i] = (portfolio_return - risk_free_rate) / portfolio_stddev

# Encontrar portfólio com o melhor Índice de Sharpe para ações e criptomoedas combinadas
max_sharpe_idx_combinado = np.argmax(results_combinado[2])
best_sharpe_return_combinado = results_combinado[0, max_sharpe_idx_combinado]
best_sharpe_stddev_combinado = results_combinado[1, max_sharpe_idx_combinado]
best_sharpe_ratio_combinado = results_combinado[2, max_sharpe_idx_combinado]

# Plotar as três Fronteiras Eficientes de Markowitz
plt.figure(figsize=(10, 6))
plt.scatter(results_acoes[1, :], results_acoes[0, :], c=results_acoes[2, :], cmap='YlGnBu', marker='o', label='Ações')
plt.title('Fronteira Eficiente de Markowitz - Ações')
plt.xlabel('Volatilidade')
plt.ylabel('Retorno')
plt.colorbar(label='Índice de Sharpe')
plt.scatter(best_sharpe_stddev_acoes, best_sharpe_return_acoes, c='red', marker='*', s=100, label='Melhor Índice de Sharpe (Ações)')
plt.legend()
plt.show()

plt.figure(figsize=(10, 6))
plt.scatter(results_criptos[1, :], results_criptos[0, :], c=results_criptos[2, :], cmap='YlOrBr', marker='o', label='Criptomoedas')
plt.title('Fronteira Eficiente de Markowitz - Criptomoedas')
plt.xlabel('Volatilidade')
plt.ylabel('Retorno')
plt.colorbar(label='Índice de Sharpe')
plt.scatter(best_sharpe_stddev_criptos, best_sharpe_return_criptos, c='blue', marker='*', s=100, label='Melhor Índice de Sharpe (Criptomoedas)')
plt.legend()
plt.show()

plt.figure(figsize=(10, 6))
plt.scatter(results_combinado[1, :], results_combinado[0, :], c=results_combinado[2, :], cmap='YlGn', marker='o', label='Ações e Criptomoedas (Combinado)')
plt.title('Fronteira Eficiente de Markowitz - Ações e Criptomoedas (Combinado)')
plt.xlabel('Volatilidade')
plt.ylabel('Retorno')
plt.colorbar(label='Índice de Sharpe')
plt.scatter(best_sharpe_stddev_combinado, best_sharpe_return_combinado, c='green', marker='*', s=100, label='Melhor Índice de Sharpe (Combinado)')
plt.legend()
plt.show()


# Gráfico de todas as carteiras dos outros gráficos
plt.figure(figsize=(10, 6))
plt.scatter(results_acoes[1, :], results_acoes[0, :], c=results_acoes[2, :], cmap='YlGnBu', marker='o', label='Ações')
plt.scatter(results_criptos[1, :], results_criptos[0, :], c=results_criptos[2, :], cmap='YlOrBr', marker='o', label='Criptomoedas')
plt.scatter(results_combinado[1, :], results_combinado[0, :], c=results_combinado[2, :], cmap='YlGn', marker='o', label='Ações e Criptomoedas (Combinado)')
plt.title('Todas as Carteiras')
plt.xlabel('Volatilidade')
plt.ylabel('Retorno')
plt.colorbar(label='Índice de Sharpe')
plt.scatter(best_sharpe_stddev_acoes, best_sharpe_return_acoes, c='red', marker='*', s=100, label='Melhor Índice de Sharpe (Ações)')
plt.scatter(best_sharpe_stddev_criptos, best_sharpe_return_criptos, c='blue', marker='*', s=100, label='Melhor Índice de Sharpe (Criptomoedas)')
plt.scatter(best_sharpe_stddev_combinado, best_sharpe_return_combinado, c='green', marker='*', s=100, label='Melhor Índice de Sharpe (Combinado)')
plt.legend()
plt.show()




# Dicionário para armazenar as variações percentuais
variacoes_percentuais = {}

# Calcular a variação percentual para cada ativo (ações e criptomoedas)
for ativo in ativos_acoes + ativos_criptos:
    if ativo in ativos_acoes:
        dataframe = dataframes_acoes[ativo]
    else:
        dataframe = dataframes_criptos[ativo]

    primeiro_close = dataframe['Close'].iloc[0]
    ultimo_close = dataframe['Close'].iloc[-1]
    variacao_percentual = ((ultimo_close - primeiro_close) / primeiro_close) * 100
    variacoes_percentuais[ativo] = variacao_percentual

# Organizar os ativos em ordem decrescente de variação percentual (ranking)
ranking_variacao = sorted(variacoes_percentuais.items(), key=lambda x: x[1], reverse=True)

# Criar uma tabela (DataFrame) com os resultados
import pandas as pd

ranking_df = pd.DataFrame(ranking_variacao, columns=['Ativo', 'Variação Percentual'])
ranking_df.set_index('Ativo', inplace=True)

# Imprimir a tabela de ranking
print(ranking_df)

# Plotar o gráfico de variação dos ativos
plt.figure(figsize=(10, 6))
colors = ['g' if v >= 0 else 'r' for v in ranking_df['Variação Percentual']]
ranking_df['Variação Percentual'].plot(kind='bar', color=colors)
plt.title('Variação Percentual dos Ativos')
plt.ylabel('Variação Percentual (%)')
plt.xticks(rotation=45)

# Exibir a tabela no console
print(tabulate(ranking_df, headers='keys', tablefmt='pretty'))

#Incluindo análisesRSI e MCD

# Função para baixar os dados e calcular RSI
def calcular_rsi(ativo):
    if ativo in ativos_acoes:
        df = yf.download(ativo, start="2014-11-08", end="2024-04-14")
    else:
        df = yf.download(ativo, start="2014-11-08", end="2024-04-14")

    # Calcular o RSI usando o preço de fechamento
    rsi = RSIIndicator(close=df['Close'], window=14)  # 14 períodos por padrão
    df['RSI'] = rsi.rsi()  # Adicionar a coluna RSI ao DataFrame

    # Plotar o gráfico de RSI
    plt.figure(figsize=(10, 6))
    plt.plot(df.index, df['RSI'], label='RSI', color='purple')
    plt.axhline(70, linestyle='--', alpha=0.5, color='red')  # Linha de sobrecompra
    plt.axhline(30, linestyle='--', alpha=0.5, color='green')  # Linha de sobrevenda
    plt.title(f'RSI de {ativo}')
    plt.xlabel('Data')
    plt.ylabel('RSI')
    plt.legend()
    plt.show()

    return df

# Dicionário para armazenar os DataFrames com o RSI
dataframes_acoes = {}
dataframes_criptos = {}

# Calcular o RSI para todos os ativos de ações
for ativo in ativos_acoes:
    df = calcular_rsi(ativo)
    dataframes_acoes[ativo] = df

# Calcular o RSI para todos os ativos de criptomoedas
for ativo in ativos_criptos:
    df = calcular_rsi(ativo)
    dataframes_criptos[ativo] = df