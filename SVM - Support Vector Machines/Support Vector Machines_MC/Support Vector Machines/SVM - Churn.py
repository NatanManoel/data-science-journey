# -*- coding: utf-8 -*-

# MBA em Data Science e Analytics USP/ESALQ 
# Support Vector Machines (SVM)

# Prof. Dr. Wilson Tarantin Jr.

#%% Instalar os pacotes necessários (Executar no console sem #)

# pip install pandas
# pip install matplotlib
# pip install scikit-learn

#%% Importando os pacotes

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.metrics import accuracy_score
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.model_selection import GridSearchCV
from sklearn.inspection import permutation_importance

#%% Carregando o banco de dados

# Treinar um modelo para identificar a evasão de clientes
# Target: churn -> 1: deixou de ser cliente; 0 continua cliente

dados = pd.read_excel('dados_churn.xlsx')

#%% Estatísticas descritivas

# Variáveis métricas
print(dados[['idade', 'acessos', 'valor_medio_transacao']].describe())

# Variáveis categóricas
print(dados['churn'].value_counts())
print(dados['churn'].value_counts(normalize=True))

print(dados['sexo'].value_counts())
print(dados['cidade'].value_counts())
print(dados['plano'].value_counts())
print(dados['reclamacao'].value_counts())

#%% Vamos criar uma etapa para pré-processamento dos dados

## 1. Identificar os tipos de variáveis do banco de dados
# Nota: não especificar a variável target nas listas abaixo
metricas = ['idade', 'acessos', 'valor_medio_transacao']
categoricas = ['sexo', 'cidade', 'plano', 'reclamacao']

## 2. Criar uma função para transformar as variáveis
# Para variáveis métricas, vamos aplicar a padronização
# Para variáveis categóricas, vamos aplicar a dummização
pre_tratamento = ColumnTransformer(
    [('metr', StandardScaler(), metricas),
     ('categ', OneHotEncoder(drop='if_binary', handle_unknown='ignore', sparse_output=False), categoricas)])
pre_tratamento.set_output(transform='pandas')

#%% Separação das bases de treino e teste

# Separando as variáveis Y e X
X = dados.drop(columns=['churn'])
y = dados['churn']

# Gerando os conjuntos de treinamento e testes (70% treino e 30% teste)
X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                    test_size=0.30,
                                                    stratify=y,
                                                    random_state=100)

#%% Aplicando o pré-processamento aos dados

# No banco de dados de treino
X_train_trat = pre_tratamento.fit_transform(X_train)

# Nota: vamos treinar os modelos com vários kernels
# A avaliação final nos dados de teste será após seleção de hiperparâmetros 

#%%############### Estimando o modelo SVM (Linear) ############################
###############################################################################

svm_linear = SVC(kernel='linear', C=0.1)
svm_linear.fit(X_train_trat, y_train)

#%% Categorias preditas pelo modelo linear

# Base de dados de treinamento
pred_linear_train = svm_linear.predict(X_train_trat)

#%% Análise pela matriz de confusão (base de treino)

cm_linear_train = confusion_matrix(y_train, pred_linear_train)
cm_train_disp_linear = ConfusionMatrixDisplay(cm_linear_train)

plt.rcParams['figure.dpi'] = 600
cm_train_disp_linear.plot(colorbar=False, cmap='Blues')
plt.title('SVM Linear: Treino')
plt.xlabel('Predito (Modelo)')
plt.ylabel('Observado (Real)')
plt.show()

acc_linear_train = accuracy_score(y_train, pred_linear_train)
sens_linear_train = recall_score(y_train, pred_linear_train, pos_label=1)
espec_linear_train = recall_score(y_train, pred_linear_train, pos_label=0)
prec_linear_train = precision_score(y_train, pred_linear_train)

print("Avaliação do SVM Linear (Base de Treino)")
print(f"Acurácia: {acc_linear_train:.1%}")
print(f"Sensibilidade: {sens_linear_train:.1%}")
print(f"Especificidade: {espec_linear_train:.1%}")
print(f"Precision: {prec_linear_train:.1%}")

#%%############### Estimando o modelo SVM (Polinomial) ########################
###############################################################################

svm_pol = SVC(kernel='poly', degree=2, coef0=0, C=0.1, gamma=1)
svm_pol.fit(X_train_trat, y_train)

#%% Categorias preditas pelo modelo Polinomial

# Base de dados de treinamento
pred_pol_train = svm_pol.predict(X_train_trat)

#%% Análise pela matriz de confusão (base de treino)

cm_pol_train = confusion_matrix(y_train, pred_pol_train)
cm_train_disp_pol = ConfusionMatrixDisplay(cm_pol_train)

plt.rcParams['figure.dpi'] = 600
cm_train_disp_pol.plot(colorbar=False, cmap='gray')
plt.title('SVM Polinomial: Treino')
plt.xlabel('Predito (Modelo)')
plt.ylabel('Observado (Real)')
plt.show()

acc_pol_train = accuracy_score(y_train, pred_pol_train)
sens_pol_train = recall_score(y_train, pred_pol_train, pos_label=1)
espec_pol_train = recall_score(y_train, pred_pol_train, pos_label=0)
prec_pol_train = precision_score(y_train, pred_pol_train)

print("Avaliação do SVM Polinomial (Base de Treino)")
print(f"Acurácia: {acc_pol_train:.1%}")
print(f"Sensibilidade: {sens_pol_train:.1%}")
print(f"Especificidade: {espec_pol_train:.1%}")
print(f"Precision: {prec_pol_train:.1%}")

#%%############### Estimando o modelo SVM (RBF) ###############################
###############################################################################

svm_rbf = SVC(kernel='rbf', C=0.1, gamma=1)
svm_rbf.fit(X_train_trat, y_train)

#%% Categorias preditas pelo modelo RBF

# Base de dados de treinamento
pred_rbf_train = svm_rbf.predict(X_train_trat)

#%% Análise pela matriz de confusão (base de treino)

cm_rbf_train = confusion_matrix(y_train, pred_rbf_train)
cm_train_disp_rbf = ConfusionMatrixDisplay(cm_rbf_train)

plt.rcParams['figure.dpi'] = 600
cm_train_disp_rbf.plot(colorbar=False, cmap='Oranges')
plt.title('SVM RBF: Treino')
plt.xlabel('Predito (Modelo)')
plt.ylabel('Observado (Real)')
plt.show()

acc_rbf_train = accuracy_score(y_train, pred_rbf_train)
sens_rbf_train = recall_score(y_train, pred_rbf_train, pos_label=1)
espec_rbf_train = recall_score(y_train, pred_rbf_train, pos_label=0)
prec_rbf_train = precision_score(y_train, pred_rbf_train)

print("Avaliação do SVM RBF (Base de Treino)")
print(f"Acurácia: {acc_rbf_train:.1%}")
print(f"Sensibilidade: {sens_rbf_train:.1%}")
print(f"Especificidade: {espec_rbf_train:.1%}")
print(f"Precision: {prec_rbf_train:.1%}")

#%% Grid Search com validação cruzada

# Como há a validação cruzada, vamos unir o pré-processamento ao modelo
pipeline_svm = Pipeline([('pre_tratamento', pre_tratamento),
                         ('svm', SVC())])

# Especificar a lista de hiperparâmetros
param_grid = [
  {'svm__kernel': ['linear'], 'svm__C': [0.1, 1]},
  {'svm__kernel': ['poly'], 'svm__C': [0.1, 1], 'svm__degree': [2, 3], 'svm__coef0': [0, 1], 'svm__gamma': [0.1, 1]},
  {'svm__kernel': ['rbf'], 'svm__C': [0.1, 1], 'svm__gamma': [0.1, 1, 10]},
]

# Treinar os modelos para o grid search
model_grid = GridSearchCV(estimator = pipeline_svm, 
                          param_grid = param_grid,
                          scoring='accuracy', # pode alterar (ex.: recall, f1)
                          cv=5,
                          verbose=2)

model_grid.fit(X_train, y_train) 
# Note que não estamos pré-processando previamente
# O pré-processamento ocorre dentro do pipeline

# Verificando os melhores parâmetros obtidos
print(model_grid.best_params_)

# Verificando a avaliação média do melhor modelo
print(f"Acurácia Média: {model_grid.best_score_:.2%}")

# Gerando o modelo com os melhores hiperparâmetros
svm_best = model_grid.best_estimator_

# Valores preditos nas bases de treino e teste
pred_grid_train = svm_best.predict(X_train)
pred_grid_test = svm_best.predict(X_test)

#%% Análise pela matriz de confusão (base de treino)

cm_grid_train = confusion_matrix(y_train, pred_grid_train)
cm_train_disp_grid = ConfusionMatrixDisplay(cm_grid_train)

plt.rcParams['figure.dpi'] = 600
cm_train_disp_grid.plot(colorbar=False, cmap='Greens')
plt.title('SVM Grid: Treino')
plt.xlabel('Predito (Modelo)')
plt.ylabel('Observado (Real)')
plt.show()

acc_grid_train = accuracy_score(y_train, pred_grid_train)
sens_grid_train = recall_score(y_train, pred_grid_train, pos_label=1)
espec_grid_train = recall_score(y_train, pred_grid_train, pos_label=0)
prec_grid_train = precision_score(y_train, pred_grid_train)

print("Avaliação do SVM Grid (Base de Treino)")
print(f"Acurácia: {acc_grid_train:.1%}")
print(f"Sensibilidade: {sens_grid_train:.1%}")
print(f"Especificidade: {espec_grid_train:.1%}")
print(f"Precision: {prec_grid_train:.1%}")

#%% Análise pela matriz de confusão (base de teste)

cm_grid_test = confusion_matrix(y_test, pred_grid_test)
cm_test_disp_grid = ConfusionMatrixDisplay(cm_grid_test)

plt.rcParams['figure.dpi'] = 600
cm_test_disp_grid.plot(colorbar=False, cmap='Greens')
plt.title('SVM Grid: Teste')
plt.xlabel('Predito (Modelo)')
plt.ylabel('Observado (Real)')
plt.show()

acc_grid_test = accuracy_score(y_test, pred_grid_test)
sens_grid_test = recall_score(y_test, pred_grid_test, pos_label=1)
espec_grid_test = recall_score(y_test, pred_grid_test, pos_label=0)
prec_grid_test = precision_score(y_test, pred_grid_test)

print("Avaliação do SVM Grid (Base de Teste)")
print(f"Acurácia: {acc_grid_test:.1%}")
print(f"Sensibilidade: {sens_grid_test:.1%}")
print(f"Especificidade: {espec_grid_test:.1%}")
print(f"Precision: {prec_grid_test:.1%}")

#%% Importância das variáveis preditoras no modelo

# Interpretando as variáveis no modelo final (não faremos mais treinamentos)

result = permutation_importance(svm_best, X_test, y_test, 
                                n_repeats=10, 
                                scoring='accuracy',
                                random_state=100)

sort_importances = result.importances_mean.argsort()

importances = pd.DataFrame(result.importances[sort_importances].T,
                           columns=X_test.columns[sort_importances])

# Plotar no gráfico
plt.rcParams['figure.dpi'] = 600
importances.plot.box(vert=False, whis=1.5)
plt.title('Permutation Importances')
plt.xlabel('Redução na Acurácia')
plt.axvline(x=0, color='gray', linestyle=':')
plt.show()

#%% Realizando previsões para novas observações

# Aqui não precisamos transforar as variáveis, pois o pipeline fará isso
novo_cliente = pd.DataFrame({'idade': [30],
                             'acessos': [10],
                             'valor_medio_transacao': [3000],
                             'sexo': ['masculino'],
                             'cidade': ['capital'],
                             'plano': ['sem'],
                             'reclamacao': ['sim']})

# Previsão do modelo final
svm_best.predict(novo_cliente)

#%% Fim!