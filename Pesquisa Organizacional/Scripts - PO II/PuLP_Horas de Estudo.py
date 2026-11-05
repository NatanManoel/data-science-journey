# Instalar o PuLP
# Executar o seguinte comando diretamente no console: pip install pulp

# Importar a biblioteca PuLP
from pulp import *

# Definir o problema como de maximização
prob = LpProblem("Maximizar_Media_Ponderada", LpMaximize)

# Definir as variáveis de decisão contínuas (maiores ou iguais a zero)
H1 = LpVariable("H1", lowBound=0, cat='Continuous')  # Horas H1
H2 = LpVariable("H2", lowBound=0, cat='Continuous')  # Horas H2

# Definir a função objetivo: maximizar L = (15*H1 + 20*H2)/8
prob += (15 * H1 + 20 * H2) / 8, "Lucro_Total"

# Adicionar as restrições
prob += H1 + H2 <= 30, "Restricao_Soma_Horas"       # Soma das horas não pode exceder 30
prob += H1 >= 10, "Restricao_Minima_H1"             # H1 deve ser no mínimo 10
prob += H2 >= 12.5, "Restricao_Minima_H2"           # H2 deve ser no mínimo 12,5

# Resolver o problema
prob.solve()

# Imprimir os resultados
print("Status da Solução:", LpStatus[prob.status])
print(f"Valor ótimo de H1 = {H1.varValue:.2f}")
print(f"Valor ótimo de H2 = {H2.varValue:.2f}")
print(f"Média Ponderada Máxima = {value(prob.objective):.2f}")