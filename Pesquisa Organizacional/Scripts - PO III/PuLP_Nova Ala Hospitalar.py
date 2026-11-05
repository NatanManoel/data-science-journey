# Instalar o PuLP
# Executar o seguinte comando diretamente no console: pip install pulp

# Importar a biblioteca PuLP
from pulp import *

# Definir o problema como de maximização
problema = LpProblem("Maximizar_Receita_Mensal", LpMaximize)

# Definir as variáveis de decisão: q1, q2 e q3 (número de quartos individuais, duplos e triplos)
q1 = LpVariable("q1", lowBound=0, cat="Integer")  # Quartos individuais (inteiros e ≥ 0)
q2 = LpVariable("q2", lowBound=0, cat="Integer")  # Quartos duplos (inteiros e ≥ 0)
q3 = LpVariable("q3", lowBound=0, cat="Integer")  # Quartos triplos (inteiros e ≥ 0)

# Definir a função objetivo: R = 7500*q1 + 6000*q2 + 4500*q3
problema += 7500*q1 + 6000*q2 + 4500*q3, "Receita_Total"

# Adicionar as restrições
problema += 10*q1 + 15*q2 + 18*q3 <= 1200, "Restricao_de_Area"         # Restrição de área total
problema += q1 + q2 + q3 <= 70, "Restricao_de_Capacidade"              # Restrição de número total de quartos
problema += q1 <= 30, "Restricao_de_Quartos_Individuais"              # Limite máximo de quartos individuais
problema += q1 + 2*q2 + 3*q3 >= 120, "Restricao_de_Ocupacao_Minima"   # Restrição de ocupação mínima

# Resolver o problema
problema.solve()

# Exibir o status da solução
print("Status da Solução:", LpStatus[problema.status])

# Exibir os valores ótimos das variáveis
print("Quantidade ótima de quartos individuais (q1):", q1.varValue)
print("Quantidade ótima de quartos duplos (q2):", q2.varValue)
print("Quantidade ótima de quartos triplos (q3):", q3.varValue)

# Exibir o valor máximo da função objetivo
print("Receita mensal máxima (R): R$", value(problema.objective))