# Instalar o PuLP
# Executar o seguinte comando diretamente no console: pip install pulp

# Importar a biblioteca PuLP
from pulp import *

# Criar o problema de minimização de custo
problema = LpProblem("Problema_de_Transporte", LpMinimize)

# Definir variáveis contínuas (R+)
x11 = LpVariable("x11", lowBound=0, cat='Continuous')  # CD1 → L1
x12 = LpVariable("x12", lowBound=0, cat='Continuous')  # CD1 → L2
x13 = LpVariable("x13", lowBound=0, cat='Continuous')  # CD1 → L3
x21 = LpVariable("x21", lowBound=0, cat='Continuous')  # CD2 → L1
x23 = LpVariable("x23", lowBound=0, cat='Continuous')  # CD2 → L3

# Variável inteira para transporte CD2 → L2 (em múltiplos de 7)
k = LpVariable("k", lowBound=0, cat='Integer')         # Número de cargas de 7 toneladas
x22 = 7 * k                                            # Quantidade enviada (CD2 → L2)

# Definir a função objetivo (custo total)
problema += (
    5 * x11 + 6 * x12 + 5 * x13 +
    5 * x21 + 7 * x22 + 7 * x23
), "Custo_Total"

# Restrições de oferta (capacidade dos CDs)
problema += x11 + x12 + x13 <= 40, "Oferta_CD1"
problema += x21 + x22 + x23 <= 60, "Oferta_CD2"

# Restrições de demanda (necessidades das lojas)
problema += x11 + x21 == 30, "Demanda_L1"
problema += x12 + x22 == 35, "Demanda_L2"
problema += x13 + x23 == 25, "Demanda_L3"

# Resolver o problema
problema.solve()

# Mostrar status da solução
print("Status da Solução:", LpStatus[problema.status])

# Imprimir os valores ótimos das variáveis
print("\nDistribuição ótima:")
print("CD1 → L1:", x11.varValue, "toneladas")
print("CD1 → L2:", x12.varValue, "toneladas")
print("CD1 → L3:", x13.varValue, "toneladas")
print("CD2 → L1:", x21.varValue, "toneladas")
print("CD2 → L2:", x22.value(), "toneladas (", k.varValue, "cargas de 7t )")
print("CD2 → L3:", x23.varValue, "toneladas")

# Imprimir o custo mínimo total
print("\nCusto mínimo total: R$", value(problema.objective))