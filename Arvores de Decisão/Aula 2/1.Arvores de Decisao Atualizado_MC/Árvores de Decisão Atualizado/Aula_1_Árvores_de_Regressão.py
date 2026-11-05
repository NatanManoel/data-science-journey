# -*- coding: utf-8 -*-

# Árvores de Decisão para Regressão
# Amazon Delivery Dataset


#%% Instalando os pacotes

## Executar na linha de comando do console (sem o #)

# pip install pandas
# pip install numpy
# pip install scikit-learn

#%% Importando os pacotes

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.tree import plot_tree
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.tree import DecisionTreeRegressor

#%% 1. Conhecendo os dados
#%%
# Importando o banco de dados Amazon Delivery Dataset

df = pd.read_csv(
    'https://raw.githubusercontent.com/vqrca/ml-datasets/'
    'refs/heads/main/amazon_delivery.csv'
)

#%%
# Visualizando as primeiras observações

pd.set_option('display.max_columns', None)
print(df.head())

#%%
# Identificando o número de registros e variáveis

df.shape

#%%

# Verificando a estrutura e os tipos das variáveis
df.info()

#%%

# Estatísticas descritivas das variáveis numéricas
df.describe()

#%% 2. Preparando os dados

# Limpeza: coordenadas fora da Índia, avaliações inválidas e dados ausentes
lat_min, lat_max = 6.0, 38.0
lon_min, lon_max = 67.0, 98.0

filtro = (
    df['Store_Latitude'].between(lat_min, lat_max)
    & df['Store_Longitude'].between(lon_min, lon_max)
    & df['Drop_Latitude'].between(lat_min, lat_max)
    & df['Drop_Longitude'].between(lon_min, lon_max)
    & df['Agent_Rating'].between(1.0, 5.0)
    & df['Agent_Rating'].notna()
    & df['Weather'].notna()
)

df_limpo = df[filtro].copy()
#%% Distância entre a loja e o cliente

# Calculando a distância em quilômetros por meio da fórmula de Haversine
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0  # Raio médio da Terra em quilômetros
    lat1, lon1, lat2, lon2 = map(
        np.radians,
        [lat1, lon1, lat2, lon2]
    )
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    )
    return 2 * R * np.arcsin(np.sqrt(a))


df_limpo['Distancia_km'] = haversine_km(
    df_limpo['Store_Latitude'],
    df_limpo['Store_Longitude'],
    df_limpo['Drop_Latitude'],
    df_limpo['Drop_Longitude']
)
print(df_limpo.head())
#%% Tempo de preparo do pedido

# Convertendo os horários para o formato de data e hora
df_limpo['Order_Time'] = pd.to_datetime(
    df_limpo['Order_Time'],
    format='%H:%M:%S',
    errors='coerce'
)

df_limpo['Pickup_Time'] = pd.to_datetime(
    df_limpo['Pickup_Time'],
    format='%H:%M:%S',
    errors='coerce'
)

# Calculando o intervalo entre o pedido e a retirada, em minutos
df_limpo['Tempo_Preparo_min'] = (
    df_limpo['Pickup_Time'] - df_limpo['Order_Time']
).dt.total_seconds() / 60

# Corrigindo os intervalos que atravessam a meia-noite
df_limpo.loc[
    df_limpo['Tempo_Preparo_min'] < 0,
    'Tempo_Preparo_min'
] += 24 * 60

print(df_limpo.head())
#%% Codificação das variáveis categóricas

df_encoded = pd.get_dummies(
    df_limpo,
    columns=['Weather', 'Traffic', 'Vehicle', 'Area', 'Category'],
    dtype=int,
)

df_encoded.head()
#%% 3. Treinando a árvore de decisão

#%% 3.1 Separando os dados em treino e teste

# Separando as variáveis preditoras e a variável-alvo
# Identificadores, coordenadas e horários originais são removidos após a
# criação das variáveis Distancia_km e Tempo_Preparo_min
X = df_encoded.drop(
    [
        'Order_ID',
        'Store_Latitude',
        'Store_Longitude',
        'Drop_Latitude',
        'Drop_Longitude',
        'Order_Date',
        'Order_Time',
        'Pickup_Time',
        'Delivery_Time'
    ],
    axis=1
)

y = df_encoded['Delivery_Time']

#%%

X

#%%

y

#%%
# Dividindo os dados em conjuntos de treinamento e teste

X_treino, X_teste, y_treino, y_teste = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

#%% 3.2 Treinamento do modelo

# Criando e ajustando a árvore de regressão
modelo_arvore = DecisionTreeRegressor(random_state=5389)
modelo_arvore.fit(X_treino, y_treino)

# Realizando previsões para o conjunto de teste
predicoes = modelo_arvore.predict(X_teste)

predicoes

#%% 4. Analisando as métricas de performance

#%% 4.1 MAE — Erro Médio Absoluto

mae = mean_absolute_error(y_teste, predicoes)
print(f'MAE (Erro Médio Absoluto): {mae:.2f}')

#%% 4.2 MSE — Erro Quadrático Médio

mse = mean_squared_error(y_teste, predicoes)
print(f'MSE (Erro Quadrático Médio): {mse:.2f}')

#%% 4.3 RMSE — Raiz do Erro Quadrático Médio

rmse = np.sqrt(mse)
print(f'RMSE (Raiz do Erro Quadrático Médio): {rmse:.2f}')

#%% 4.4 R² — Coeficiente de Determinação

r2 = r2_score(y_teste, predicoes)
print(f'R² (Coeficiente de Determinação): {r2:.2f}')

#%%
# Consolidando as métricas do conjunto de teste
print('Avaliação do modelo — conjunto de teste')
print('-' * 45)
print(f'MAE  : {mae:.2f}')
print(f'MSE  : {mse:.2f}')
print(f'RMSE : {rmse:.2f}')
print(f'R²   : {r2:.2f}')

#%% 4.5 Comparando treino e teste — diagnóstico de overfitting

# Previsões no conjunto de treino
predicoes_treino = modelo_arvore.predict(X_treino)

# Métricas no conjunto de treino
rmse_treino = np.sqrt(mean_squared_error(y_treino, predicoes_treino))
r2_treino = r2_score(y_treino, predicoes_treino)

# Métricas do conjunto de teste, calculadas anteriormente
rmse_teste = rmse
r2_teste = r2

print(
    f'RMSE treino: {rmse_treino:.2f}  |  '
    f'RMSE teste: {rmse_teste:.2f}'
)
print(
    f'R²   treino: {r2_treino:.2f}  |  '
    f'R²   teste: {r2_teste:.2f}'
)

#%% 5. Controlando o overfitting

# Criando uma árvore com profundidade máxima de 10 níveis
modelo_arvore_podada = DecisionTreeRegressor(
    random_state=5389,
    max_depth=10
)

# Ajustando o modelo e realizando previsões para o conjunto de teste
modelo_arvore_podada.fit(X_treino, y_treino)
predicoes_podada = modelo_arvore_podada.predict(X_teste)

#%% 5.1 Métricas da árvore podada no conjunto de teste

mae_podada = mean_absolute_error(y_teste, predicoes_podada)
mse_podada = mean_squared_error(y_teste, predicoes_podada)
rmse_podada = np.sqrt(mse_podada)
r2_podada = r2_score(y_teste, predicoes_podada)

print('Avaliação da árvore podada (max_depth=10) — conjunto de teste')
print('-' * 60)
print(f'MAE  : {mae_podada:.2f}')
print(f'MSE  : {mse_podada:.2f}')
print(f'RMSE : {rmse_podada:.2f}')
print(f'R²   : {r2_podada:.2f}')

#%% 5.2 Comparação entre treino e teste após a poda

# Previsões e métricas no conjunto de treino
predicoes_podada_treino = modelo_arvore_podada.predict(X_treino)
rmse_podada_treino = np.sqrt(
    mean_squared_error(y_treino, predicoes_podada_treino)
)
r2_podada_treino = r2_score(y_treino, predicoes_podada_treino)

print(
    f'RMSE treino (podada): {rmse_podada_treino:.2f}  |  '
    f'RMSE teste (podada): {rmse_podada:.2f}'
)
print(
    f'R²   treino (podada): {r2_podada_treino:.2f}  |  '
    f'R²   teste (podada): {r2_podada:.2f}'
)

#%% Visualizando a árvore de decisão

#%% Visualizando a árvore de decisão

plt.figure(figsize=(24, 12))

plot_tree(
    modelo_arvore_podada,
    feature_names=X.columns,
    #max_depth=3,
    filled=True,
    rounded=True,
    fontsize=12,
    proportion=True,
    precision=2
)

plt.tight_layout()
plt.show()

#%% 6. Ajuste de hiperparâmetros com validação cruzada

# Definindo as combinações de hiperparâmetros
grade_parametros = {
    'max_depth': [5, 10, 15, 20],
    'min_samples_leaf': [1, 10, 50, 100],
    'criterion': ['squared_error', 'absolute_error']
}

#%% 6.2 Configurando o Grid Search com validação cruzada

# Criando uma instância da árvore de regressão
modelo_arvore_grid = DecisionTreeRegressor(random_state=5389)

# Utilizando RMSE como métrica e validação cruzada com cinco partições
grid_search = GridSearchCV(
    estimator=modelo_arvore_grid,
    param_grid=grade_parametros,
    cv=5,
    scoring='neg_root_mean_squared_error',
    n_jobs=-1,
    verbose=1
)

# Executando a busca pelos melhores hiperparâmetros
grid_search.fit(X_treino, y_treino)

print(f'Melhores parâmetros encontrados: {grid_search.best_params_}')
print(
    'Melhor RMSE médio na validação cruzada: '
    f'{-grid_search.best_score_:.3f}'
)

#%% 6.3 Treinando o modelo final com os melhores hiperparâmetros

# Extraindo os melhores hiperparâmetros
melhores_params = grid_search.best_params_

# Criando e treinando o modelo final
modelo_arvore_otimizada = DecisionTreeRegressor(
    random_state=5389,
    **melhores_params
)
modelo_arvore_otimizada.fit(X_treino, y_treino)

# Realizando previsões para o conjunto de teste
predicoes_otimizada = modelo_arvore_otimizada.predict(X_teste)

#%% 6.4 Avaliando o modelo final

# Métricas no conjunto de teste
mae_otim = mean_absolute_error(y_teste, predicoes_otimizada)
rmse_otim = np.sqrt(mean_squared_error(y_teste, predicoes_otimizada))
r2_otim = r2_score(y_teste, predicoes_otimizada)

# Métricas no conjunto de treino para verificar overfitting
predicoes_otim_treino = modelo_arvore_otimizada.predict(X_treino)
rmse_otim_treino = np.sqrt(
    mean_squared_error(y_treino, predicoes_otim_treino)
)
mae_otim_treino = mean_absolute_error(y_treino, predicoes_otim_treino)
r2_otim_treino = r2_score(y_treino, predicoes_otim_treino)

print('Árvore otimizada — desempenho final')
print('-' * 55)
print(
    f'R²   treino: {r2_otim_treino:.3f}  |  '
    f'R²   teste: {r2_otim:.3f}'
)
print(
    f'RMSE treino: {rmse_otim_treino:.2f}  |  '
    f'RMSE teste: {rmse_otim:.2f}'
)
print(
    f'MAE  treino : {mae_otim_treino:.2f}  |  '
    f'MAE  teste : {mae_otim:.2f}'
)
