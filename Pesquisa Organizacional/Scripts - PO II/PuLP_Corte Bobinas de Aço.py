# Instalar o PuLP
# Executar o seguinte comando diretamente no console: pip install pulp

# Importar o PuLP
from pulp import *

# Definir o problema
prob = LpProblem("Corte_Bobinas", LpMaximize)

# Definir as variáveis de decisão
x = LpVariable("x", lowBound=0, cat='Continuous')  # Produção na máquina antiga
y = LpVariable("y", lowBound=0, cat='Continuous')  # Produção na máquina moderna

# Definir a função objetivo
prob += 0.3 * x + 0.5 * y, "Lucro_Total"

# Adicionar as restrições
prob += x <= 4000, "Capacidade_Maquina_Antiga"
prob += y <= 6000, "Capacidade_Maquina_Moderna"
prob += 0.003 * x + 0.002 * y <= 18, "Disponibilidade_Mao_de_Obra"

# Resolver o problema
prob.solve()

# Imprimir os resultados
print("Status:", LpStatus[prob.status])
print(f"Produção na Máquina Antiga (x) = {x.varValue:.2f} metros")
print(f"Produção na Máquina Moderna (y) = {y.varValue:.2f} metros")
print(f"Lucro Total = R$ {value(prob.objective):.2f}")