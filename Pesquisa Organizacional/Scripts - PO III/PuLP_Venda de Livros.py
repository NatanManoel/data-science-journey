# Instalar o PuLP
# Executar o seguinte comando diretamente no console: pip install pulp

#Importar a biblioteca PuLP
from pulp import *

# Definir o problema como de maximização
problema = LpProblem("Maximizacao_de_Lucro", LpMaximize)

# Definir as variáveis de decisão inteiras: L e M
L = LpVariable("L", lowBound=0, cat='Integer')  # L ≥ 0 e inteiro
M = LpVariable("M", lowBound=0, cat='Integer')  # M ≥ 0 e inteiro

# Definir a função objetivo: Max 6L + 7M
problema += 6 * L + 7 * M, "Funcao_Objetivo"

# Adicionar as restrições
problema += L + M <= 10, "Restricao_1"
problema += M <= 7, "Restricao_2"
problema += 6 * L + 2 * M >= 40, "Restricao_3"
problema += M >= 3, "Restricao_4"

# Resolver o problema
problema.solve()

# Exibir o status da solução
print("Status da Solução:", LpStatus[problema.status])

# Exibir os valores ótimos das variáveis
print("Valor ótimo de L:", L.varValue)
print("Valor ótimo de M:", M.varValue)

# Exibir o valor da função objetivo
print("Valor máximo da função objetivo:", value(problema.objective))
