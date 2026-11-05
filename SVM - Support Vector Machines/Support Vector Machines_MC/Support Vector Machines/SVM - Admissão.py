# -*- coding: utf-8 -*-

# MBA em Data Science e Analytics USP/ESALQ 
# Support Vector Machines (SVM)

# Prof. Dr. Wilson Tarantin Jr.

#%% Instalar os pacotes necessários (Executar no console sem #)

# pip install pandas
# pip install numpy
# pip install matplotlib
# pip install seaborn
# pip install scikit-learn

#%% Importando os pacotes

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import r2_score
from sklearn.inspection import permutation_importance

#%% Carregando o banco de dados

admissao = pd.read_excel('dados_admissao.xlsx')
# Fonte: adaptado de https://www.kaggle.com/datasets/mohansacharya/graduate-admissions
# Mohan S Acharya, Asfia Armaan, Aneeta S Antony: A Comparison of Regression Models for Prediction of Graduate Admissions, IEEE International Conference on Computational Intelligence in Data Science 2019

#%% Limpeza dos dados

# Remover colunas que não serão utilizadas
admissao.drop(columns=['Serial No.'], inplace=True)

#%% Estatísticas descritivas

# Variáveis métricas
print(admissao[['GRE', 'TOEFL', 'SOP', 'LOR', 'CGPA', 'Score']].describe())
print(admissao[['GRE', 'TOEFL', 'SOP', 'LOR', 'CGPA', 'Score']].corr())

# Variáveis categóricas
print(admissao['UniversityRating'].value_counts())
print(admissao['Research'].value_counts())

#%% Etapa de pré-processamento dos dados

## 1. Identificar os tipos de variáveis do banco de dados
# Nota: não especificar a variável target nas listas abaixo
metricas = ['GRE', 'TOEFL', 'SOP', 'LOR', 'CGPA']
categoricas = ['UniversityRating']
sem_preproc = ['Research'] 
# Nota: Research já é uma dummy

## 2. Criar uma função para transformar as variáveis
# Para variáveis métricas, vamos aplicar a padronização
# Para variáveis categóricas, vamos aplicar a dummização
pre_tratamento = ColumnTransformer(
    [('metr', StandardScaler(), metricas),
     ('categ', OneHotEncoder(drop='if_binary', handle_unknown='ignore', sparse_output=False), categoricas),
     ('sem', 'passthrough', sem_preproc)])
pre_tratamento.set_output(transform='pandas')

#%% Separando as variáveis Y e X

X = admissao.drop(columns=['Score'])
y = admissao['Score']

#%% Separando as amostras de treino e teste

# Vamos escolher 70% das observações para treino e 30% para teste
X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                    test_size=0.3, 
                                                    random_state=100)

#%% Aplicando o pré-processamento aos dados

# No banco de dados de treino
X_train_trat = pre_tratamento.fit_transform(X_train)

#%%############### Estimando o modelo SVR (Linear) ############################
###############################################################################

svr_linear = SVR(kernel='linear', C=1, epsilon=1)
svr_linear.fit(X_train_trat, y_train)

#%% Valores preditos pelo modelo linear

# Base de dados de treinamento
pred_linear_train = svr_linear.predict(X_train_trat)

#%% Avaliando o modelo (base de treino)

mse_train_linear = mean_squared_error(y_train, pred_linear_train)
mae_train_linear = mean_absolute_error(y_train, pred_linear_train)
r2_train_linear = r2_score(y_train, pred_linear_train)

print("Avaliação do Modelo Linear (Base de Treino)")
print(f"MSE: {mse_train_linear:.1f}")
print(f"RMSE: {np.sqrt(mse_train_linear):.1f}")
print(f"MAE: {mae_train_linear:.1f}")
print(f"R²: {r2_train_linear:.3f}")

#%%############### Estimando o modelo SVR (Polinomial) ########################
###############################################################################

svr_pol = SVR(kernel='poly', C=1, degree=2, coef0=0, epsilon=1)
svr_pol.fit(X_train_trat, y_train)

#%% Valores preditos pelo modelo polinomial

# Base de dados de treinamento
pred_pol_train = svr_pol.predict(X_train_trat)

#%% Avaliando o modelo (base de treino)

mse_train_pol = mean_squared_error(y_train, pred_pol_train)
mae_train_pol = mean_absolute_error(y_train, pred_pol_train)
r2_train_pol = r2_score(y_train, pred_pol_train)

print("Avaliação do Modelo Polinomial (Base de Treino)")
print(f"MSE: {mse_train_pol:.1f}")
print(f"RMSE: {np.sqrt(mse_train_pol):.1f}")
print(f"MAE: {mae_train_pol:.1f}")
print(f"R²: {r2_train_pol:.3f}")

#%%############### Estimando o modelo SVR (RBF) ###############################
###############################################################################

svr_rbf = SVR(kernel='rbf', C=1, gamma=1, epsilon=1)
svr_rbf.fit(X_train_trat, y_train)

#%% Valores preditos pelo modelo RBF

# Base de dados de treinamento
pred_rbf_train = svr_rbf.predict(X_train_trat)

#%% Avaliando o modelo (base de treino)

mse_train_rbf = mean_squared_error(y_train, pred_rbf_train)
mae_train_rbf = mean_absolute_error(y_train, pred_rbf_train)
r2_train_rbf = r2_score(y_train, pred_rbf_train)

print("Avaliação do Modelo RBF (Base de Treino)")
print(f"MSE: {mse_train_rbf:.1f}")
print(f"RMSE: {np.sqrt(mse_train_rbf):.1f}")
print(f"MAE: {mae_train_rbf:.1f}")
print(f"R²: {r2_train_rbf:.3f}")

#%% Grid Search

# Como há a validação cruzada, vamos unir o pré-processamento ao modelo
pipeline_svm = Pipeline([('pre_tratamento', pre_tratamento),
                         ('svm', SVR())])

# Especificar a lista de hiperparâmetros
param_grid = [
  {'svm__kernel': ['linear'], 'svm__C': [0.1, 1, 10], 'svm__epsilon': [0.1, 1, 2]},
  {'svm__kernel': ['poly'], 'svm__C': [0.1, 1, 10], 'svm__degree': [2, 3, 4, 5], 'svm__coef0': [0, 1, 2], 'svm__epsilon': [0.1, 1, 2]},
  {'svm__kernel': ['rbf'], 'svm__C': [0.1, 1, 10], 'svm__gamma': [0.01, 1, 10], 'svm__epsilon': [0.1, 1, 2]},
]

# Treinar os modelos para o grid search
model_grid = GridSearchCV(estimator = pipeline_svm, 
                          param_grid = param_grid,
                          scoring='neg_mean_squared_error',
                          cv=5,
                          verbose=2)

model_grid.fit(X_train, y_train)
# Note que não estamos pré-processando previamente
# O pré-processamento ocorre dentro do pipeline

# Verificando os melhores parâmetros obtidos
print(model_grid.best_params_)

# Verificando a avaliação média do melhor modelo
print(f"MSE Médio: {-model_grid.best_score_:.4}")

# Gerando o modelo com os melhores hiperparâmetros
svr_best = model_grid.best_estimator_

# Valores preditos nas bases de treino e teste
pred_grid_train = svr_best.predict(X_train)
pred_grid_test = svr_best.predict(X_test)

#%% Avaliando o modelo (base de treino)

mse_train_grid = mean_squared_error(y_train, pred_grid_train)
mae_train_grid = mean_absolute_error(y_train, pred_grid_train)
r2_train_grid = r2_score(y_train, pred_grid_train)

print("Avaliação do Modelo Pós Grid (Base de Treino)")
print(f"MSE: {mse_train_grid:.1f}")
print(f"RMSE: {np.sqrt(mse_train_grid):.1f}")
print(f"MAE: {mae_train_grid:.1f}")
print(f"R²: {r2_train_grid:.3f}")

#%% Avaliando o modelo (base de testes)

mse_test_grid = mean_squared_error(y_test, pred_grid_test)
mae_test_grid = mean_absolute_error(y_test, pred_grid_test)
r2_test_grid = r2_score(y_test, pred_grid_test)

print("Avaliação do Modelo Pós Grid (Base de Teste)")
print(f"MSE: {mse_test_grid:.1f}")
print(f"RMSE: {np.sqrt(mse_test_grid):.1f}")
print(f"MAE: {mae_test_grid:.1f}")
print(f"R²: {r2_test_grid:.3f}")

#%% Importância das variáveis preditoras no modelo

result = permutation_importance(svr_best, X_test, y_test, 
                                n_repeats=10, 
                                scoring='neg_mean_squared_error',
                                random_state=100)

sort_importances = result.importances_mean.argsort()

importances = pd.DataFrame(result.importances[sort_importances].T,
                           columns=X_test.columns[sort_importances])

# Plotar no gráfico
plt.rcParams['figure.dpi'] = 600
importances.plot.box(vert=False, whis=1.5)
plt.title('Permutation Importances')
plt.xlabel('Aumento no MSE')
plt.axvline(x=0, color='gray', linestyle=':')
plt.show()

#%% Gráfico fitted values

# Valores preditos pelo modelo para as observações da amostra de teste (grid)
graph = pd.DataFrame({'Score': y_test,
                      'Pred_Grid': pred_grid_test})

plt.figure(dpi=600)
sns.scatterplot(graph, x='Score', y='Pred_Grid', color='orange')
plt.title('Analisando as Previsões', fontsize=10)
plt.xlabel('Score Observado', fontsize=10)
plt.ylabel('Score Previsto pelo Modelo', fontsize=10)
plt.axline((25, 25), (max(admissao['Score']), max(admissao['Score'])), linewidth=1, color='grey')
plt.show()

#%% Realizando previsões para novas observações

# Note que as variáveis métricas são padronizadas
novo_aluno = pd.DataFrame({'GRE': [330],
                           'TOEFL': [115],
                           'SOP': [5],
                           'LOR': [5],
                           'CGPA': [9.8],
                           'Research': [1],
                           'UniversityRating': [1]})

# Previsão do modelo final
print(f"Score Previsto: {svr_best.predict(novo_aluno)[0]:.2f}")

#%% Fim!