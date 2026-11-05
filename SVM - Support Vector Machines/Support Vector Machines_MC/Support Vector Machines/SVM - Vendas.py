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
from sklearn.metrics import confusion_matrix
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.metrics import accuracy_score
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score

#%% Carregando o banco de dados

# Treinar um modelo para identificar potenciais compradores de veículos
# Target: Purchased -> 1: comprou; 0 não comprou

# Importando os dados
dados = pd.read_csv('dados_carros.csv')

#%% Estatísticas descritivas

# Variáveis métricas
print(dados[['Age', 'AnnualSalary']].describe())

# Variáveis categóricas
print(dados['Purchased'].value_counts())
print(dados['Purchased'].value_counts(normalize=True))

print(dados['Gender'].value_counts())

#%% Vamos criar uma etapa para pré-processamento dos dados

## 1. Identificar os tipos de variáveis do banco de dados
# Nota: não especificar a variável target nas listas abaixo
metricas = ['Age', 'AnnualSalary']
categoricas = ['Gender']

## 2. Criar uma função para transformar as variáveis
# Para variáveis métricas, vamos aplicar a padronização
# Para variáveis categóricas, vamos aplicar a dummização
pre_tratamento = ColumnTransformer(
    [('metr', StandardScaler(), metricas),
     ('categ', OneHotEncoder(drop='if_binary', handle_unknown='ignore', sparse_output=False), categoricas)])
pre_tratamento.set_output(transform='pandas')

#%% Separação das bases de treino e teste

# Separando as variáveis Y e X
X = dados.drop(columns=['Purchased', 'User ID'])
y = dados['Purchased']

# Gerando os conjuntos de treinamento e testes (70% treino e 30% teste)
X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                    test_size=0.30,
                                                    stratify=y,
                                                    random_state=100)

#%% Aplicando o pré-processamento aos dados

# No banco de dados de treino
X_train_trat = pre_tratamento.fit_transform(X_train)

# No banco de dados de teste
X_test_trat = pre_tratamento.transform(X_test)

#%%############### Estimando o modelo SVM (Linear) ############################
###############################################################################

svm_linear = SVC(kernel='linear', C=1)
svm_linear.fit(X_train_trat, y_train)

#%% Categorias preditas pelo modelo linear

# Base de dados de treinamento
pred_linear_train = svm_linear.predict(X_train_trat)

# Base de dados de teste
pred_linear_test = svm_linear.predict(X_test_trat)

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

#%% Análise pela matriz de confusão (base de teste)

cm_linear_test = confusion_matrix(y_test, pred_linear_test)
cm_test_disp_linear = ConfusionMatrixDisplay(cm_linear_test)

plt.rcParams['figure.dpi'] = 600
cm_test_disp_linear.plot(colorbar=False, cmap='Blues')
plt.title('SVM Linear: Teste')
plt.xlabel('Predito (Modelo)')
plt.ylabel('Observado (Real)')
plt.show()

acc_linear_test = accuracy_score(y_test, pred_linear_test)
sens_linear_test = recall_score(y_test, pred_linear_test, pos_label=1)
espec_linear_test = recall_score(y_test, pred_linear_test, pos_label=0)
prec_linear_test = precision_score(y_test, pred_linear_test)

print("Avaliação do SVM Linear (Base de Teste)")
print(f"Acurácia: {acc_linear_test:.1%}")
print(f"Sensibilidade: {sens_linear_test:.1%}")
print(f"Especificidade: {espec_linear_test:.1%}")
print(f"Precision: {prec_linear_test:.1%}")

#%% Realizando previsões para novas observações

# Criando as informações para realizar previsões
observacao = pd.DataFrame({
    'Age': [40],
    'AnnualSalary': [110000],
    'Gender': ['Female']})

# Aplicando o pré-processamento
observacao_trat = pre_tratamento.transform(observacao)

# Previsão do SVC Linear
svm_linear.predict(observacao_trat)

#%% Notas

# Na primeira aplicação prática, utilizamos apenas o kernel linear
    # Nos próximos, vamos implementar também os kernels não lineares

# Aqui, também não buscamos os "melhores" hiperparâmetros
    # Faremos isso nas próximas aplicações práticas

#%% Fim!