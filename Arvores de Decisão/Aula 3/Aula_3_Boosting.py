# -*- coding: utf-8 -*-

# %%
# Aplicando a técnica de Boosting com XGBoost 

#%% Instalando os pacotes

## Executar na linha de comando do console (sem o #)

# pip install pandas
# pip install numpy
# pip install matplotlib
# pip install scikit-learn
# pip install xgboost==3.3.0

#%% Importações

import pandas as pd
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    ConfusionMatrixDisplay,
    roc_auc_score,
    RocCurveDisplay)
#%% Definição do random state

RANDOM_STATE = 7895

#%% 1. Carregando os dados

df = pd.read_csv('https://raw.githubusercontent.com/vqrca/ml-datasets/refs/heads/main/BankChurners_portugues.csv')

#%% Exibição das primeiras observações para verificar a estrutura dos dados e as variáveis disponíveis

pd.set_option('display.max_columns', None)
print(df.head())

#%% Checando detalhes sobre os dados

df.info()

#%% 2. Preparando os dados

colunas_categoricas = df.select_dtypes(include='object').columns

df[colunas_categoricas] = df[colunas_categoricas].astype('category')

#%% Verificando a alteração no tipo de dado object para category

df.info()

#%% 3. Separando os dados em treino e teste


X = df.drop(['Numero_Cliente', 'Target'], axis=1)
y = df['Target']

#%% 

X.head()

#%% 

y.head()

#%% Preparando o Target para o XGBoost

from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()

y = le.fit_transform(df['Target'])

#%% 

y

#%% Separação dos dados em conjuntos de treinamento e teste

X_treino, X_teste, y_treino, y_teste = train_test_split(
    X,
    y,
    test_size=0.2,
    stratify=y,
    random_state=RANDOM_STATE)

#%% 4. Treinamento com XGBoost

import xgboost as xgb

#%% 

modelo_xgboost = xgb.XGBClassifier(objective='binary:logistic',
                                   random_state=RANDOM_STATE
)
modelo_xgboost.fit(X_treino, y_treino)
predicoes = modelo_xgboost.predict(X_teste)

#%% Análise da acurácia: Comparação da acurácia entre treino e teste: verificando o overfitting

# Acurácia no teste
acuracia_teste = accuracy_score(y_teste, predicoes)
print(f'Acurácia do XGBoost nos dados de teste: {acuracia_teste:.2f}')

#%% Acurácia no treino

# Acurácia no treino
predicoes_treino = modelo_xgboost.predict(X_treino)
acuracia = accuracy_score(y_treino, predicoes_treino)
print(f'Acurácia do XGBoost nos dados de treino: {acuracia:.2f}')

#%% Relatório de métricas: Análise detalhada por classe: precisão, revocação e F1-score

report = classification_report(y_teste, predicoes)
print(report)

#%% Matriz de confusão: Distribuição dos acertos e erros por classe

ConfusionMatrixDisplay.from_estimator(modelo_xgboost,
                                      X_teste, y_teste,
                                      normalize = 'true',
                                      cmap = 'Blues',
                                      display_labels=['Ativo', 'Inativo']);

#%% Curva ROC: Análise da capacidade discriminativa: curva ROC e AUC

# Gera a curva ROC
RocCurveDisplay.from_estimator(
    modelo_xgboost,
    X_teste,
    y_teste
);

#%% 5. Realizando a validação cruzada

dmatrix = xgb.DMatrix(data=X, label=y)

params = {'objective': 'binary:logistic'}

cv_resultados = xgb.cv(dtrain=dmatrix, params=params, nfold=3,
                       num_boost_round=5, metrics='error',
                       as_pandas=True, seed=5678)

print(cv_resultados)
acuracia = 1 - cv_resultados['test-error-mean'].iloc[-1]
print(f'Acuracia: {acuracia}')

#%% Explorando a técnica de Early Stopping

params = {'objective': 'binary:logistic'}

cv_resultados = xgb.cv(dtrain=dmatrix, params=params, nfold=3,
                       num_boost_round=200, metrics='error',
                       as_pandas=True, seed=5678)

print(cv_resultados)
acuracia = 1 - cv_resultados['test-error-mean'].iloc[-1]
print(f'Acuracia: {acuracia}')


#%% early_stopping_rounds=5

params = {'objective': 'binary:logistic'}

cv_resultados = xgb.cv(dtrain=dmatrix, params=params, nfold=3,
                       num_boost_round=200, early_stopping_rounds=5,
                       metrics='error', as_pandas=True, seed=5678)

print(cv_resultados)
acuracia = 1 - cv_resultados['test-error-mean'].iloc[-1]
print(f'Acuracia: {acuracia}')

#%% 6. Analisando a taxa de aprendizado

params = {'objective': 'binary:logistic',
          'learning_rate': 0.01}

cv_resultados = xgb.cv(dtrain=dmatrix, params=params, nfold=3,
                       num_boost_round=100,
                       metrics='error', as_pandas=True, seed=123)

print(cv_resultados)
acuracia = 1 - cv_resultados['test-error-mean'].iloc[-1]
print(f'Acuracia: {acuracia}')

#%% learning_rate = 0.1

params = {'objective': 'binary:logistic',
          'learning_rate': 0.1}

cv_resultados = xgb.cv(dtrain=dmatrix, params=params, nfold=3,
                       num_boost_round=100,
                       metrics='error', as_pandas=True, seed=123)

print(cv_resultados)
acuracia = 1 - cv_resultados['test-error-mean'].iloc[-1]
print(f'Acuracia: {acuracia}')

#%% learning_rate = 1

params = {'objective': 'binary:logistic',
          'learning_rate': 1}

cv_resultados = xgb.cv(dtrain=dmatrix, params=params, nfold=3,
                       num_boost_round=100,
                       metrics='error', as_pandas=True, seed=123)

print(cv_resultados)
acuracia = 1 - cv_resultados['test-error-mean'].iloc[-1]
print(f'Acuracia: {acuracia}')

#%% 7. Ajustando hiperparâmetros

params = {
    'learning_rate': [0.1, 0.2, 0.3],
    'max_depth': [5, 10, 15],
    'colsample_bytree': [0.5, 1.0],
    'n_estimators': [50, 100],
    'reg_lambda': [1, 5, 10],
    'reg_alpha':  [0, 0.1, 1],
    'gamma':      [0, 0.1, 1],
    'min_child_weight': [1, 5]
}

modelo_xgb = xgb.XGBClassifier(random_state=RANDOM_STATE)

random_search_cv = RandomizedSearchCV(estimator=modelo_xgb, param_distributions=params, n_iter=5, cv=4, scoring='recall',
                                      verbose=1, random_state=765)

random_search_cv.fit(X,y)

print('Melhores parametros encontrados: ', random_search_cv.best_params_)
print('Recall:', random_search_cv.best_score_)

#%% Analisando as métricas no teste após ajuste dos hiperparâmetros

modelo_xgboost_ajustado = random_search_cv.best_estimator_
predicoes_xgboost_ajustado = modelo_xgboost_ajustado.predict(X_teste)
acuracia = accuracy_score(y_teste, predicoes_xgboost_ajustado)
print(f"Acurácia do XGBoost ajustado nos dados de teste: {acuracia:.2%}")

#%% Analisando as métricas no treino após ajuste dos hiperparâmetros

predicoes_xgboost_ajustado_treino = modelo_xgboost_ajustado.predict(X_treino)
acuracia = accuracy_score(y_treino, predicoes_xgboost_ajustado_treino)
print(f"Acurácia do XGBoost ajustado nos dados de treino: {acuracia:.2%}")


#%% Classification report

report = classification_report(y_teste, predicoes_xgboost_ajustado)
print(report)

#%% Matriz de confusão

ConfusionMatrixDisplay.from_estimator(modelo_xgboost_ajustado,
                                      X_teste, y_teste,
                                      normalize = 'true', cmap = 'Blues',
                                      display_labels=['Ativo', 'Inativo']);

#%% Curva ROC

RocCurveDisplay.from_predictions(y_teste, predicoes_xgboost_ajustado,
                                 name='XGBoost ajustado');

#%% Importância das variáveis

importancias = (
    pd.Series(
        modelo_xgboost_ajustado.feature_importances_,
        index=X_treino.columns
    )
    .sort_values(ascending=False)
)

print(importancias.head(15))

