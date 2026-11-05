# Instalar o PuLP
# Executar o seguinte comando diretamente no console: pip install pulp

#Importar a biblioteca PuLP
from pulp import *

# Inicializar o modelo
prob = LpProblem("Transporte_com_Transbordo_e_Ativacao", LpMinimize)

# Variáveis de transporte (CD → Loja)
x_cd1_l1 = LpVariable("CD1_L1", 0)
x_cd1_l2 = LpVariable("CD1_L2", 0)
x_cd1_l3 = LpVariable("CD1_L3", 0)
x_cd2_l1 = LpVariable("CD2_L1", 0)
k = LpVariable("k", lowBound=0, cat='Integer')  # múltiplos de 7
x_cd2_l2 = 7 * k
x_cd2_l3 = LpVariable("CD2_L3", 0)

# Variáveis de transporte via transbordo
x_cd1_t1 = LpVariable("CD1_T1", 0)
x_cd1_t2 = LpVariable("CD1_T2", 0)
x_cd2_t1 = LpVariable("CD2_T1", 0)
x_cd2_t2 = LpVariable("CD2_T2", 0)

x_t1_l1 = LpVariable("T1_L1", 0)
x_t1_l2 = LpVariable("T1_L2", 0)
x_t1_l3 = LpVariable("T1_L3", 0)

x_t2_l1 = LpVariable("T2_L1", 0)
x_t2_l2 = LpVariable("T2_L2", 0)
x_t2_l3 = LpVariable("T2_L3", 0)

# Variáveis binárias de ativação dos transbordos
y_t1 = LpVariable("Ativar_T1", cat='Binary')
y_t2 = LpVariable("Ativar_T2", cat='Binary')

# Função objetivo: custo de transporte + custo fixo de ativação
prob += (
    5*x_cd1_l1 + 6*x_cd1_l2 + 5*x_cd1_l3 +
    5*x_cd2_l1 + 7*x_cd2_l2 + 7*x_cd2_l3 +
    1*x_cd1_t1 + 5*x_cd1_t2 + 1*x_cd2_t1 + 3*x_cd2_t2 +
    2*(x_t1_l1 + x_t1_l2 + x_t1_l3) +
    1*x_t2_l1 + 3*x_t2_l2 + 1*x_t2_l3 +
    10*y_t1 + 10*y_t2
)

# Restrições de capacidade nos CDs
prob += x_cd1_l1 + x_cd1_l2 + x_cd1_l3 + x_cd1_t1 + x_cd1_t2 <= 40, "Capacidade_CD1"
prob += x_cd2_l1 + x_cd2_l2 + x_cd2_l3 + x_cd2_t1 + x_cd2_t2 <= 60, "Capacidade_CD2"

# Restrições de demanda nas lojas
prob += x_cd1_l1 + x_cd2_l1 + x_t1_l1 + x_t2_l1 == 30, "Demanda_L1"
prob += x_cd1_l2 + x_cd2_l2 + x_t1_l2 + x_t2_l2 == 35, "Demanda_L2"
prob += x_cd1_l3 + x_cd2_l3 + x_t1_l3 + x_t2_l3 == 25, "Demanda_L3"

# Fluxo nos transbordos (entrada = saída)
prob += x_cd1_t1 + x_cd2_t1 == x_t1_l1 + x_t1_l2 + x_t1_l3, "Fluxo_T1"
prob += x_cd1_t2 + x_cd2_t2 == x_t2_l1 + x_t2_l2 + x_t2_l3, "Fluxo_T2"

# Capacidade dos terminais (limitada a 50 se ativados)
prob += x_cd1_t1 + x_cd2_t1 <= 50 * y_t1, "Capacidade_T1"
prob += x_cd1_t2 + x_cd2_t2 <= 50 * y_t2, "Capacidade_T2"

# Resolver o modelo
prob.solve()

# Exibir resultados
print("Status:", LpStatus[prob.status])
print(f"\nCusto mínimo total: R$ {value(prob.objective):,.2f}")
for v in prob.variables():
    if v.varValue > 0:
        print(f"{v.name}: {v.varValue}")

print(f"CD2_L2:{7*k.varValue}")