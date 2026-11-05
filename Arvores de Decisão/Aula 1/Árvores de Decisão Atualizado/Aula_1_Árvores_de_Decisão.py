# -*- coding: utf-8 -*-

# Resolvendo um problema de Classificação


#%% Instalando os pacotes

## Executar na linha de comando do console (sem o #)

# pip install pandas
# pip install matplotlib
# pip install scikit-learn


#%% 1. Conhecendo os dados

import pandas as pd

#%% Leitura do dataset de doenças cardíacas a partir de um arquivo CSV armazenado em um repositório GitHub

df = pd.read_csv('https://raw.githubusercontent.com/vqrca/ml-datasets/refs/heads/main/Heart_Disease_Prediction.csv')

#%% Exibição das primeiras observações da base para verificar a estrutura dos dados e as variáveis disponíveis

pd.set_option('display.max_columns', None)
print(df.head())

#%% Identificação do número de registros e atributos presentes no conjunto de dados

df.shape

#%% Checando detalhes sobre os dados

df.info()

#%% Preparando os dados
# Aplicação do get_dummies nas colunas Chest pain type e Thallium

df_encoded = pd.get_dummies(df, columns=['Chest pain type', 'Thallium'], dtype=int)

df_encoded.head()

#%% 2. Treinando a árvore de decisão

#%% 2.1 Separando os dados em treino e teste

X = df_encoded.drop('Heart Disease', axis=1)
y = df_encoded['Heart Disease']

#%% 
X
#%%
y
#%% Separação dos dados em conjuntos de treinamento e teste

from sklearn.model_selection import train_test_split
X_treino, X_teste, y_treino, y_teste = train_test_split(X,
                                                        y, 
                                                        test_size=0.2,
                                                        stratify=y,
                                                        random_state=42)

#%% 2.2 Classificando com Decision Tree

from sklearn.tree import DecisionTreeClassifier

#%% Treinamento do modelo com os dados de treino

# Cria uma instância do Decision tree: dt
modelo_arvore = DecisionTreeClassifier(random_state=5389)

# Ajusta o classificador ao conjunto de treinamento
modelo_arvore.fit(X_treino, y_treino)

# Preve o Target do conjunto de teste
predicoes = modelo_arvore.predict(X_teste)

#%% Em predicoes temos as predições realizadas nos dados de teste

predicoes

#%% Podemos investigar as probabilidade calculadas para cada classe

# Calcula as probabilidades para cada classe
probabilidades = modelo_arvore.predict_proba(X_teste)

probabilidades

#%% 2.3 Analisando a árvore de decisão

import matplotlib.pyplot as plt
from sklearn.tree import plot_tree

plt.figure(figsize=(24, 12))

plot_tree(
    modelo_arvore,
    feature_names=X.columns,
    filled=True,
    rounded=True,
    #max_depth=3,
    fontsize=8,
    proportion=True,
    precision=2
)

plt.tight_layout()
plt.show()
#%% 3. Analisando as métricas de performance

#%% 3.1 Acurácia

from sklearn.metrics import accuracy_score

#%% Cálculo da proporção de previsões corretas realizadas pelo modelo no conjunto de teste

acuracia_teste = accuracy_score(y_teste, predicoes)
print(f'Acurácia nos dados de teste: {acuracia_teste:.2%}')
#%% Cálculo da proporção de previsões corretas realizadas pelo modelo no conjunto de treinamento

predicoes_treino = modelo_arvore.predict(X_treino)

acuracia_treino= accuracy_score(y_treino, predicoes_treino)
print(f'Acurácia nos dados de treino: {acuracia_treino:.2%}')


#%% 3.2 Relatório de Classificação

from sklearn.metrics import classification_report

#%% Cálculo das principais métricas de avaliação

# Gera um relatório de classificação
relatorio = classification_report(y_teste, predicoes)

print(relatorio)

#%% 3.3 Matriz de confusão

from sklearn.metrics import ConfusionMatrixDisplay

#%% Exibição da matriz de confusão

ConfusionMatrixDisplay.from_estimator(modelo_arvore, X_teste, y_teste);


#%% Matriz com valores normalizados e aplicação de paleta divergente monocromática

ConfusionMatrixDisplay.from_estimator(modelo_arvore, X_teste, y_teste,
                                      normalize = 'true',
                                      cmap = 'Blues');

#%% 3.4 Curva ROC


from sklearn.metrics import RocCurveDisplay


#%% Gera a curva ROC

# Gera a curva ROC
RocCurveDisplay.from_estimator(
    modelo_arvore,
    X_teste,
    y_teste
);


#%% 4. Controlando o overfitting


# Cria uma instância do Decision tree: dt
modelo_arvore_podada = DecisionTreeClassifier(random_state=5389, max_depth=3)

# Ajusta o classificador ao conjunto de treinamento
modelo_arvore_podada.fit(X_treino, y_treino)

# Preve o Target do conjunto de teste
predicoes_podada = modelo_arvore_podada.predict(X_teste)

#%% Preve o Target do conjunto de treinamento

# Preve o Target do conjunto de treinamento
predicoes_podada_treino = modelo_arvore_podada.predict(X_treino)

# Calcula a acurácia no conjunto de treinamento
acuracia_treino_podada = accuracy_score(y_treino, predicoes_podada_treino)
print(f'Acurácia nos dados de treino (max_depth=3): {acuracia_treino_podada:.2f}')

# Acurácia no conjunto de teste 
acuracia_teste_podada = accuracy_score(y_teste, predicoes_podada)
print(f'Acurácia nos dados de teste (max_depth=3): {acuracia_teste_podada:.2f}')

#%% Visualização da árvore podada

plt.figure(figsize=(24, 12))

plot_tree(
    modelo_arvore_podada,
    feature_names=X.columns,
    filled=True,
    rounded=True,
    max_depth=3,
    fontsize=8,
    proportion=True,
    precision=2
)

plt.tight_layout()
plt.show()

#%% Exibição da matriz de confusão

ConfusionMatrixDisplay.from_estimator(modelo_arvore_podada, X_teste, y_teste,
                                      normalize = 'true',
                                      cmap = 'Blues');

#%% 5. Aplicando a técnica de validação cruzada

#%% 5.1 Validação cruzada

from sklearn.model_selection import cross_val_score

#%% Avaliação do modelo em 5 partições da base de dados utilizando a acurácia como métrica de desempenho

modelo = DecisionTreeClassifier(random_state=5389, max_depth=3)
scores = cross_val_score(modelo, X, y, cv=5, scoring='accuracy')
scores

#%% Resumo do desempenho médio do modelo e da variabilidade dos resultados entre as partições

print("O resultado da validação cruzada é %0.2f%% acurácia com desvio padrão de %0.2f%%" 
      % (scores.mean() * 100, scores.std() * 100))

#%% 5.2 Validação cruzada estratificada

from sklearn.model_selection import StratifiedKFold, cross_val_score

#%% Avaliação do modelo em diferentes subconjuntos da base utilizando a acurácia como métrica de desempenho

validacao = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=5389
)

scores = cross_val_score(
    modelo_arvore_podada,
    X,
    y,
    cv=validacao,
    scoring='accuracy'
)

scores

#%% Resumo do desempenho médio do modelo e da variabilidade dos resultados entre as partições

print("O resultado da validação cruzada é %0.2f%% acurácia com desvio padrão de %0.2f%%" 
      % (scores.mean() * 100, scores.std() * 100))

#%% Importação da função cross_validate, utilizada para calcular diversas métricas durante a validação cruzada

from sklearn.model_selection import cross_validate


#%% Avaliação do modelo utilizando acurácia, precisão, recall e F1-score em diferentes partições da base de dados

resultado = cross_validate(
    modelo_arvore_podada,
    X,
    y,
    cv=5,
    scoring=['accuracy', 'precision_macro', 'recall_macro', 'f1_macro']
)

resultado

#%% Apresentação consolidada das métricas de desempenho obtidas durante a validação cruzada

resultados_metricas = pd.DataFrame({
    'Média': [
        resultado['test_accuracy'].mean(),
        resultado['test_precision_macro'].mean(),
        resultado['test_recall_macro'].mean(),
        resultado['test_f1_macro'].mean()
    ],
    'Desvio Padrão': [
        resultado['test_accuracy'].std(),
        resultado['test_precision_macro'].std(),
        resultado['test_recall_macro'].std(),
        resultado['test_f1_macro'].std()
    ]
},
index=['Acurácia', 'Precisão', 'Recall', 'F1-Score'])

# Aplicar formatação de porcentagem com duas casas decimais
resultados_metricas['Média'] = resultados_metricas['Média'].apply(lambda x: f'{x:.2%}')
resultados_metricas['Desvio Padrão'] = resultados_metricas['Desvio Padrão'].apply(lambda x: f'{x:.2%}')

resultados_metricas

#%% 6. Buscando melhores hiperparâmetros

from sklearn.model_selection import GridSearchCV

#%% Define a grade de hiperparâmetros que será testada

# Define a grade de hiperparâmetros que será testada
grade_parametros = {
    'max_depth': [3, 5, 7, 10],
    'min_samples_leaf': [1, 5, 10, 20],
    'criterion': ['gini', 'entropy']
}

# Cria uma instância da Árvore de Decisão
modelo_arvore_grid = DecisionTreeClassifier(random_state=5389)

# Configura o Grid Search
# Utiliza a acurácia como métrica de avaliação e validação cruzada com 5 partições
grid_search = GridSearchCV(
    estimator=modelo_arvore_grid,
    param_grid=grade_parametros,
    cv=5,
    scoring='accuracy',
    n_jobs=-1,
    verbose=1
)

# Executa a busca pelos melhores hiperparâmetros
grid_search.fit(X, y)

# Exibe os melhores hiperparâmetros encontrados e a melhor acurácia média
print(f"Melhores parâmetros encontrados: {grid_search.best_params_}")
print(f"Melhor acurácia média na validação cruzada: {grid_search.best_score_:.2f}")

#%% Exibindo o melhor estimador

grid_search.best_estimator_

#%% Apresentação das combinações testadas, juntamente com suas métricas de desempenho e classificação no ranking

colunas_resultado = [
    'param_max_depth',
    'param_min_samples_leaf',
    'param_criterion',
    'mean_test_score',
    'std_test_score',
    'rank_test_score'
]

resultados = (
    pd.DataFrame(grid_search.cv_results_)[colunas_resultado]
    .sort_values('rank_test_score')
    .reset_index(drop=True)
)

resultados

#%% Realização de previsões no conjunto de teste utilizando o modelo otimizado

# Criar uma instância do Decision tree
modelo_arvore_otimizada = DecisionTreeClassifier(random_state=5389, criterion='entropy', max_depth=3, min_samples_leaf=10)

# Ajustar o classificador ao conjunto de treinamento
modelo_arvore_otimizada.fit(X_treino, y_treino)

# Prever o Target do conjunto de teste
predicoes_otimizada = modelo_arvore_otimizada.predict(X_teste)

#%% Apresentação da estrutura final da árvore otimizada para análise e interpretação do modelo

plt.figure(figsize=(24, 12))

plot_tree(
    modelo_arvore_otimizada,
    feature_names=X.columns,
    filled=True,
    rounded=True,
    max_depth=3,
    fontsize=8,
    proportion=True,
    precision=2
)

plt.tight_layout()
plt.show()


#%% Apresentação do desempenho do modelo no conjunto de treinamento e teste

# Prever o Target do conjunto de treinamento
predicoes_treino_otimizada = modelo_arvore_otimizada.predict(X_treino)

# Calcular a acurácia no conjunto de treinamento
acuracia_treino_otimizada = accuracy_score(y_treino, predicoes_treino_otimizada )
print(f'Acurácia nos dados de treino (árvore ajustada): {acuracia_treino_otimizada:.2%}')

# Acurácia no conjunto de teste
acuracia_teste_otimizada  = accuracy_score(y_teste, predicoes_otimizada)
print(f'Acurácia nos dados de teste (árvore ajustada): {acuracia_teste_otimizada:.2%}')

#%% Exibição da matriz de confusão

ConfusionMatrixDisplay.from_estimator(modelo_arvore_otimizada,
                                      X_teste, y_teste,
                                      normalize = 'true',
                                      cmap = 'Blues');

#%% 7. Comparando os resultados

ax = RocCurveDisplay.from_estimator(
    modelo_arvore,
    X_teste,
    y_teste,
    name='Árvore inicial',
    pos_label='Presence'
).ax_

RocCurveDisplay.from_estimator(
    modelo_arvore_podada,
    X_teste,
    y_teste,
    name='Árvore podada',
    pos_label='Presence',
    ax=ax
)

RocCurveDisplay.from_estimator(
    modelo_arvore_otimizada,
    X_teste,
    y_teste,
    name='Árvore otimizada',
    pos_label='Presence',
    ax=ax
)

plt.plot([0, 1], [0, 1], '--', color='gray')
plt.legend()
plt.show()
