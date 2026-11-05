# -*- coding: utf-8 -*-

# Métodos de Ensemble 

#%% Instalando os pacotes

## Executar na linha de comando do console (sem o #)

# pip install pandas
# pip install numpy
# pip install matplotlib
# pip install seaborn
# pip install scikit-learn

#%% Importações

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.base import clone
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    ConfusionMatrixDisplay,
    roc_auc_score,
    RocCurveDisplay,
    make_scorer,
)
#%% Definição do random state

RANDOM_STATE = 7895

#%% 1. Conhecendo os dados

df = pd.read_csv('https://raw.githubusercontent.com/vqrca/ml-datasets/refs/heads/main/BankChurners_portugues.csv')

#%% Exibição das primeiras observações para verificar a estrutura dos dados e as variáveis disponíveis

pd.set_option('display.max_columns', None)
print(df.head())

#%% Identificação do número de registros e atributos presentes no conjunto de dados

df.shape

#%% Verificação de dados duplicados a partir do identificador do cliente

print(f'Número de clientes duplicados: {df["Numero_Cliente"].duplicated().sum()}')

#%% Checando detalhes sobre os dados

df.info()


#%% Balanceamento da variável-alvo

contagem_target = df['Target'].value_counts()
proporcao_target = df['Target'].value_counts(normalize=True).mul(100).round(2)

pd.DataFrame({
    'Quantidade': contagem_target,
    'Percentual (%)': proporcao_target
})

#%% 2. Preparando os dados

colunas_categoricas = [
    'Genero',
    'Escolaridade',
    'Estado_Civil',
    'Faixa_Renda_Anual',
    'Categoria_Cartao'
]

# Transforma variáveis categóricas em variáveis binárias
encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
encoded_data = encoder.fit_transform(df[colunas_categoricas])
encoded_df = pd.DataFrame(encoded_data,
                          columns=encoder.get_feature_names_out(colunas_categoricas))

# Mantém o dataframe original mas remove as colunas categóricas que foram codificadas
df_encoded = pd.concat([df.drop(columns=colunas_categoricas), encoded_df],
                       axis=1)

df_encoded.head()

#%% 3. Separando os dados em treino e teste

X = df_encoded.drop(['Numero_Cliente', 'Target'], axis=1)
y = df_encoded['Target']

print(f'Formato de X: {X.shape}')
print(f'Formato de y: {y.shape}')

#%% Separação em treino (80%) e teste (20%), preservando a proporção original das classes com stratify=y

X_treino, X_teste, y_treino, y_teste = train_test_split(
    X, y,
    test_size=0.2,
    stratify=y,
    random_state=RANDOM_STATE
)

print(f'Treino: {X_treino.shape[0]} registros')
print(f'Teste:  {X_teste.shape[0]} registros')

#%% Verificando as porcentagens do target

pd.DataFrame({
    'Treino': y_treino.value_counts(normalize=True),
    'Teste':  y_teste.value_counts(normalize=True)
}).round(2)


#%% 4. Treinando e avaliando os modelos

#%% 4.1 Árvore de Decisão (baseline)

# Cria uma instância do Decision Tree
modelo_arvore = DecisionTreeClassifier(random_state=RANDOM_STATE)

# Ajusta o classificador ao conjunto de treinamento
modelo_arvore.fit(X_treino, y_treino)

# Prevê o Target do conjunto de teste
predicoes = modelo_arvore.predict(X_teste)

#%% Acurácia nos conjuntos de treino e teste

predicoes_treino = modelo_arvore.predict(X_treino)

acuracia_treino = accuracy_score(y_treino, predicoes_treino)
acuracia_teste  = accuracy_score(y_teste, predicoes)

print(f'Acurácia no treino: {acuracia_treino:.2%}')
print(f'Acurácia no teste:  {acuracia_teste:.2%}')

#%% Relatório de classificação — precisão, recall e F1 por classe

relatorio = classification_report(y_teste, predicoes)
print(relatorio)

#%% Matriz de confusão (normalizada por linha — mostra a taxa de acerto por classe real)

ConfusionMatrixDisplay.from_estimator(
    modelo_arvore, X_teste, y_teste,
    normalize='true', cmap='Blues'
);

#%% Curva ROC

RocCurveDisplay.from_estimator(
    modelo_arvore, X_teste, y_teste,
    pos_label='Inativo'
);

#%% 4.2 Floresta Aleatória

modelo_rf = RandomForestClassifier(random_state=RANDOM_STATE)

# Ajusta o classificador ao conjunto de treinamento
modelo_rf.fit(X_treino, y_treino)

# Prevê o Target do conjunto de teste
predicoes_rf = modelo_rf.predict(X_teste)

#%% Acurácia nos conjuntos de treino e teste (2)

predicoes_rf_treino = modelo_rf.predict(X_treino)

acuracia_rf_treino = accuracy_score(y_treino, predicoes_rf_treino)
acuracia_rf_teste  = accuracy_score(y_teste, predicoes_rf)

print(f'Acurácia no treino - Random Forest: {acuracia_rf_treino:.2%}')
print(f'Acurácia no teste - Random Forest:  {acuracia_rf_teste:.2%}')

#%% Relatório de classificação - Random Forest

relatorio_rf = classification_report(y_teste, predicoes_rf)
print(relatorio_rf)

#%% Matriz de confusão - Random Forest

ConfusionMatrixDisplay.from_estimator(
    modelo_rf, X_teste, y_teste,
    normalize='true', cmap='Blues'
);

#%% Curva ROC - Random Forest

RocCurveDisplay.from_estimator(
    modelo_rf, X_teste, y_teste,
    pos_label='Inativo'
);

#%% Se aumentarmos o número de árvores será que temos uma melhora?

modelo_rf_500 = RandomForestClassifier(random_state=RANDOM_STATE, n_estimators=500)

# Ajusta o classificador ao conjunto de treinamento
modelo_rf_500.fit(X_treino, y_treino)

# Prevê o Target do conjunto de teste
predicoes_rf_500 = modelo_rf_500.predict(X_teste)

#%% Relatório de classificação - Random Forest 500 árvores

relatorio_rf_500 = classification_report(y_teste, predicoes_rf_500)
print(relatorio_rf_500)


#%% 5. Ajuste de hiperparâmetros

scorer_recall = make_scorer(recall_score, pos_label='Inativo')

grade_parametros = {
    'n_estimators': [200, 500],
    'max_depth': [None, 15],
    'criterion': ['gini', 'entropy'],
}

modelo_rf_ajuste = RandomForestClassifier(random_state=RANDOM_STATE)

grid_search = GridSearchCV(
    estimator=modelo_rf_ajuste,
    param_grid=grade_parametros,
    cv=5,
    scoring=scorer_recall,          # ← usa o scorer com pos_label
    n_jobs=-1,
    verbose=1
)

grid_search.fit(X, y)

print(f"Melhores parâmetros encontrados: {grid_search.best_params_}")
print(f"Recall médio (validação cruzada): {grid_search.best_score_:.4f}")

#%% Resultados das combinações testadas, ordenados pelo desempenho médio

colunas_resultado = [
    'param_max_depth',
    'param_criterion',
    'param_n_estimators',
    'mean_test_score',
    'std_test_score',
    'rank_test_score'
]

resultados_cv = (
    pd.DataFrame(grid_search.cv_results_)[colunas_resultado]
    .sort_values('rank_test_score')
    .reset_index(drop=True)
)

resultados_cv

#%% 6. Reavaliando o modelo ajustado

grid_search.best_estimator_

#%% Treinando o modelo com os parâmetros encontrados

modelo_rf_ajustado = clone(grid_search.best_estimator_)
modelo_rf_ajustado.fit(X_treino, y_treino)

predicoes_rf_ajustado = modelo_rf_ajustado.predict(X_teste)

#%% Acurácia nos conjuntos de treino e teste do modelo ajustado

predicoes_rf_treino_ajustado = modelo_rf_ajustado.predict(X_treino)

acuracia_rf_treino_ajustado = accuracy_score(y_treino, predicoes_rf_treino_ajustado)
acuracia_rf_teste_ajustado  = accuracy_score(y_teste, predicoes_rf_ajustado)

print(f'Acurácia no treino: {acuracia_rf_treino_ajustado:.2%}')
print(f'Acurácia no teste:  {acuracia_rf_teste_ajustado:.2%}')

#%% Relatório de classificação do modelo ajustado

print(classification_report(y_teste, predicoes_rf_ajustado))

#%% Matriz de confusão do modelo ajustado

ConfusionMatrixDisplay.from_estimator(
    modelo_rf_ajustado, X_teste, y_teste,
    normalize='true', cmap='Blues'
);

#%% 7. Seleção de variáveis (Feature Selection)

#%% 7.1 Importância das variáveis

importancias = pd.Series(
    modelo_rf_ajustado.feature_importances_,
    index=X_treino.columns
).sort_values(ascending=False)

importancias

#%% Visualização das 10 variáveis mais importantes

top_10 = importancias.head(10).sort_values()

plt.figure(figsize=(10, 6))
top_10.plot(kind='barh', color='steelblue')

plt.title('Top 10 variáveis mais importantes — Random Forest ajustada')
plt.xlabel('Importância')
plt.ylabel('Variável')
plt.tight_layout()
plt.show()

#%% 7.2 Random Forest treinada apenas com as top-10 features

# 1) Seleciona os nomes das 10 features mais importantes
top10_features = importancias.head(10).index.tolist()
print('Top 10 features selecionadas:')
for i, feat in enumerate(top10_features, start=1):
    print(f'  {i:2d}. {feat}')

# 2) Filtra treino e teste para conter apenas essas colunas
X_treino_top10 = X_treino[top10_features]
X_teste_top10  = X_teste[top10_features]

print(f'\nFormato após seleção: treino {X_treino_top10.shape},teste {X_teste_top10.shape}')


#%% 3) Cria um NOVO estimador (clone) com a mesma configuração do modelo ajustado
#    Isso preserva o modelo_rf_ajustado intacto para a comparação final.
modelo_rf_fs = clone(grid_search.best_estimator_)

# 4) Treina o novo modelo apenas com as top-10 features
modelo_rf_fs.fit(X_treino_top10, y_treino)

# 5) Previsões
predicoes_rf_fs = modelo_rf_fs.predict(X_teste_top10)

#%% Acurácia com apenas 10 features

predicoes_rf_fs_treino = modelo_rf_fs.predict(X_treino_top10)

acuracia_fs_treino = accuracy_score(y_treino, predicoes_rf_fs_treino)
acuracia_fs_teste  = accuracy_score(y_teste, predicoes_rf_fs)

print(f'Acurácia no treino (top 10): {acuracia_fs_treino:.2%}')
print(f'Acurácia no teste  (top 10): {acuracia_fs_teste:.2%}')

#%% Relatório de classificação do modelo com feature selection

print(classification_report(y_teste, predicoes_rf_fs))

#%% Matriz de confusão do modelo com feature selection

ConfusionMatrixDisplay.from_estimator(
    modelo_rf_fs, X_teste_top10, y_teste,
    normalize='true', cmap='Blues'
);

#%% 8. Comparação final entre os modelos

avaliacoes = {
    'Decision Tree': {
        'modelo': modelo_arvore,
        'X_teste': X_teste,
    },
    'Random Forest': {
        'modelo': modelo_rf,
        'X_teste': X_teste,
    },
    'Random Forest ajustado': {
        'modelo': modelo_rf_ajustado,
        'X_teste': X_teste,
    },
    'Random Forest ajustado + Feature Selection': {
        'modelo': modelo_rf_fs,
        'X_teste': X_teste_top10,   # ← conjunto reduzido, específico deste modelo
    },
}

#%% 8.1 Curvas ROC comparadas

fig, ax = plt.subplots(figsize=(8, 6))

for nome, info in avaliacoes.items():
    RocCurveDisplay.from_estimator(
        info['modelo'],
        info['X_teste'],
        y_teste,
        name=nome,
        pos_label='Inativo',
        ax=ax
    )

ax.plot([0, 1], [0, 1], '--', color='grey', label='Classificador aleatório')
ax.set_title('Comparação das curvas ROC — todos os modelos')
ax.legend(loc='lower right')
plt.tight_layout()
plt.show()

#%% 8.2 Matrizes de confusão comparadas

fig, axes = plt.subplots(1, 4, figsize=(20, 5))

for ax, (nome, info) in zip(axes, avaliacoes.items()):
    ConfusionMatrixDisplay.from_estimator(
        info['modelo'],
        info['X_teste'],
        y_teste,
        display_labels=info['modelo'].classes_,
        normalize='true',
        cmap='Blues',
        ax=ax,
        colorbar=False
    )
    ax.set_title(nome, fontsize=11)
    ax.set_xlabel('Classe prevista')
    ax.set_ylabel('Classe real')

plt.tight_layout()
plt.show()


#%% 8.3 Tabela consolidada de métricas

resultados = []

for nome, info in avaliacoes.items():
    modelo = info['modelo']
    X_avaliar = info['X_teste']

    y_pred = modelo.predict(X_avaliar)
    y_prob = modelo.predict_proba(X_avaliar)[:, list(modelo.classes_).index('Inativo')]

    resultados.append({
        'Modelo': nome,
        'Accuracy':  accuracy_score(y_teste, y_pred),
        'Precision': precision_score(y_teste, y_pred, pos_label='Inativo'),
        'Recall':    recall_score(y_teste, y_pred, pos_label='Inativo'),
        'F1':        f1_score(y_teste, y_pred, pos_label='Inativo'),
        'ROC AUC':   roc_auc_score(y_teste == 'Inativo', y_prob),
    })

df_resultados = pd.DataFrame(resultados).set_index('Modelo').round(3)
df_resultados

