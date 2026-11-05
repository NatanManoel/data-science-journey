# MBA Data Science & IA — Planejamento de Estudos & Guia de Referências

> **Atualizado em:** 03/11/2026  
> **Objetivo:** Chegar em 19/01/2027 com backlog em dia; em 02/02 pronto para Engenharia de Dados e com base sólida para as aulas práticas de APIs e Integração de LLMs.  
> **Regra de Ouro da Constância:** **Piso de 20 min/dia útil.** Sem maratonas de compensação desordenada.

---

## 🎯 Regras de Execução & Constância (Ler quando desanimar)

1. **Piso inegociável:** Todo dia útil = **20 minutos**. Acabou o tempo? Pare. Conta como vitória conquistada.
2. **Se sobrar energia:** Continue até 45–60 min no **mesmo tema** (não pule de matéria no mesmo dia).
3. **Perdeu um dia:** No dia seguinte faça **somente** os 20 min programados para aquele dia. Não tente dobrar a carga.
4. **Perdeu 3+ dias:** Escolha apenas 1 script pontual para reativar o motor, não a pasta inteira.
5. **Estrutura da Sessão Padrão:** 
   - `10 min`: Alinhamento do objetivo / intuição rápida
   - `50 min`: Código / script cego
   - `20 min`: Análise de métricas / resultados
   - `10 min`: Síntese pelo Método Feynman (explicar em termos simples)

---

## 📅 FASE 1 — Até o Recesso (04/11 a 08/12/2026)

**Foco:** Aulas ao vivo das terças (BI e Social Network Analysis) + Avanço consistente no backlog de Data Wrangling e SVM.

### Calendário Detalhado Dia a Dia (Semanas 1 e 2 — Ajustado para início em 06/11)

#### 🔹 SEMANA 1 — Âncora: Data Wrangling II

* **[ ] Sex 06/11 — Data Wrangling II (Retomada Oficial)**
  * **Meta Piso (20 min):** Abrir DW II a partir dos **35:40 / linha 262** (~15 min) + registrar onde parou no tracker.
  * **+Energia:** Avançar até o próximo bloco lógico de código.
  * 📚 **Referência Recomendada:** [Wes McKinney - Python for Data Analysis (Cap. 8: Data Wrangling: Join, Combine & Reshape)](https://wesmckinney.com/book/data-wrangling.html) | [Pandas Merge/Join Docs](https://pandas.pydata.org/docs/reference/api/pandas.merge.html).
  * 💡 *Dica:* Entenda a diferença prática entre `how='left'` e `how='inner'`.

* **[ ] Sáb 07/11 — Data Wrangling II (Prática de Joins e Limpeza)**
  * **Meta Piso (20 min):** Rodar e validar o trecho codificado ontem; executar joins e tratamento de valores ausentes (`fillna` / `dropna`).
  * **+Energia:** Resolver o exercício prático de limpeza proposto na aula.
  * 📚 **Referência Recomendada:** [Wes McKinney - Python for Data Analysis (Cap. 7: Data Cleaning and Preparation)](https://wesmckinney.com/book/data-cleaning.html).

* **[ ] Dom 08/11 — Consolidação & Planejamento (15 min)**
  * **Ação:** Marcar as tarefas concluídas na base de dados (`python scripts/study_tracker.py today`) ou folga merecida.

* **[ ] Seg 09/11 — Lista Estatística em Excel**
  * **Meta Piso (20 min):** Resolver de 3 a 5 exercícios da lista de estatística no Excel.
  * **+Energia:** +5 exercícios OU criar 1 flashcard conceitual (Média vs Mediana vs Desvio Padrão em distribuições assimétricas).
  * 📚 **Referência Recomendada:** Livro *Manual de Análise de Dados* (Fávero & Belfiore, p. 78 a 150) | [StatQuest: What is a P-Value and How to Test Hypotheses](https://statquest.org/) | Livro *Estatística Prática para Cientistas de Dados* (Bruce & Bruce, Cap. 1).

* **[ ] Ter 10/11 — BI I (Aula ao Vivo)**
  * **Meta Piso:** Assistir à aula ao vivo + reproduzir 1 visual / dashboard no mesmo dia.
  * **+Energia:** Escrever 5 linhas no método Feynman (diferença entre tabela fato vs dimensão e definição de KPIs).
  * 📚 **Referência Recomendada:** Livro *Storytelling com Dados* (Cole Nussbaumer Knaflic, Cap. 1: A Importância do Contexto e Cap. 2: Escolhendo o Visual Eficaz) | Guia *Financial Times Visual Vocabulary*.

---

#### 🔹 SEMANA 2 — Âncora: Data Wrangling III + BI

* **[ ] Qua 11/11 — Fechamento Data Wrangling II + Prática BI I**
  * **Meta Piso (20 min):** Finalizar o que restar do script da Aula II (Meta: checklist *DW II OK*).
  * **+Energia:** Recriar 1 gráfico da aula de BI I do zero, sem olhar a solução.
  * 📚 **Referência Recomendada:** [Pandas Merge Docs](https://pandas.pydata.org/docs/reference/api/pandas.merge.html).

* **[ ] Qui 12/11 — DW III (Dataset CVM)**
  * **Meta Piso (20 min):** Carga do dataset CVM + inspeção inicial (`.info()`, `.describe()`, verificação de nulos e tipos).
  * **+Energia:** Realizar o merge principal com dados cadastrais e filtragens.
  * 📚 **Referência Recomendada:** [Wes McKinney - Python for Data Analysis (Cap. 10: Data Aggregation & Group Operations)](https://wesmckinney.com/book/data-aggregation.html).

* **[ ] Sex 13/11 — SVM Churn (Script Cego Curto)**
  * **Meta Piso (20 min):** Pipeline de churn de clientes com SVM: normalização com `StandardScaler` e ajuste do modelo `SVC`.
  * **+Energia:** Experimentar otimização de hiperparâmetros com `GridSearchCV` (`C` e `gamma`).
  * 📚 **Referência Recomendada:** Aurélien Géron (Hands-On ML Cap. 5: Soft Margin Classification vs Hard Margin) | [An Introduction to Statistical Learning (ISLP - Cap. 9: Support Vector Machines)](https://www.statlearning.com/).

* **[ ] Sáb 14/11 — OPCIONAL: Semente APIs & LLMs (20 min)**
  * **Meta Piso (20 min):** Rodar células [1] e [2] do `script.py` (setup FinOps + Gemini/Chroma). Pasta: *Desenvolvimento de APIs e Integração Prática de LLMs/aula-api-llm*.
  * **+Energia:** Células [3] e [4] (extração do PDF da pasta `datasets/` e chunking).
  * 📚 **Referência Recomendada:** [Documentação Oficial FastAPI (First Steps)](https://fastapi.tiangolo.com/tutorial/first-steps/) | Curso Rápido DeepLearning.AI: *Building Systems with the ChatGPT API*.

* **[ ] Dom 15/11 — Planejamento Semanal (15 min)**
  * **Ação:** Atualizar status no banco de dados e descansar.

* **[ ] Seg 16/11 — Fechar DW III OU Síntese BI I**
  * **Meta Piso (20 min):** Concluir pendências de DW III OU redigir 10 linhas conceituais da aula de BI I.
  * **+Energia:** Abrir DW IV (Dataset Copa) e realizar o load de teste.

* **[ ] Ter 17/11 — BI II (Aula ao Vivo)**
  * **Meta Piso:** Assistir à aula ao vivo + 1 prática no software no mesmo dia.
  * **+Energia:** Comparar técnicas visuais com a aula BI I (o que foi aprimorado em densidade de informação).
  * 📚 **Referência Recomendada:** Cole Knaflic (Storytelling com Dados, Cap. 3: O Clutter é seu Inimigo - Eliminando Ruídos Visuais).

---

## 🏖️ FASE 2 — Recesso (09/12/2026 a 18/01/2027) — 6 Semanas

> **Princípio:** Uma âncora fixa por semana. Reduz o atrito de decisão mental. Todo dia: 20 min no tema da semana.

| Semana | Período | Âncora da Semana | Entrega Prática Esperada | Referências Essenciais de Apoio |
|---|---|---|---|---|
| **R1** | 09 a 15/12 | **Data Wrangling Completo** | Pipelines WDI, CVM, Copa e Streaming rodando redondos. | [Wes McKinney (Cap. 7, 8 e 10)](https://wesmckinney.com/book/) \| Kaggle Pandas Tutorials. |
| **R2** | 16 a 22/12 | **Crawlers + Text Mining + Aula Solta 1 APIs** | 1 spider/crawler funcional + análise de sentimentos (Aulas 1 e 2). Sáb 19/12: Aula solta 1 APIs (`script.py` [1] a [8]). | [Hugging Face NLP Course (Cap. 1-2)](https://huggingface.co/learn/nlp-course) \| Documentação do BeautifulSoup e Scrapy. |
| **R3** | 23 a 29/12 | **Semana Leve (Festas)** | Lista Excel estatística + 3 flashcards de decisão (quando usar cada teste). Carga reduzida permitida. | *Manual de Análise de Dados* (Fávero & Belfiore p. 78-487) \| StatQuest. |
| **R4** | 30/12 a 05/01 | **Pesquisa Operacional (PuLP) + Árvores & Ensembles** | 2 modelos no PuLP resolvidos + 1 Árvore de Decisão e 1 Random Forest/XGBoost rodando. | [PuLP Documentation (Casos de Otimização Linear)](https://coin-or.github.io/pulp/) \| Aurélien Géron (Cap. 6 e 7). |
| **R5** | 06 a 12/01 | **Deep Learning + SVM + Estatística Espacial** | 1 Rede Neural MLP básica + 2 casos de SVM revisados + Moran I / LISA no Espacial. | [3Blue1Brown: Neural Networks](https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi) \| [Geographic Data Science with Python](https://geographicdata.science/book/intro.html). |
| **R6** | 13 a 18/01 | **APIs & LLMs (RAG + FastAPI)** | Sáb 16/01: Aula solta 2 + `script.py` [9] a [13] (RAG e guardrails). Domingo: [14] a [18] com endpoint `/health` e `/query` respondendo. | [FastAPI Docs](https://fastapi.tiangolo.com) \| DeepLearning.AI: *LangChain & Vector Databases*. |

---

## 🚀 FASE 3 — Volta em 2027 & Preparação para Engenharia de Dados

* **19/01 e 26/01 — Metodologias Ágeis:**
  * Tema leve e prático. O estudo técnico diário de 20 min servirá para manutenção e refinamento do script RAG/FastAPI.
* **Semana 27/01 a 01/02 — Preparação Intensiva para Engenharia de Dados:**
  * Revisar: SQL avançado, conexões de banco em Python (`SQLAlchemy`), requisições e automação de ingestão.
  * 📚 **Referências Ouro:**
    * Livro *Designing Data-Intensive Applications* (Martin Kleppmann) — a maior autoridade mundial em arquitetura de dados.
    * [Data Engineering Zoomcamp (DataTalks.Club)](https://github.com/DataTalksClub/data-engineering-zoomcamp) — Repositório gratuito com módulos de Docker, Airflow, Spark e BigQuery.
    * [LeetCode 50 SQL Study Plan](https://leetcode.com/studyplan/top-sql-50/) — Para treinar Window Functions (`ROW_NUMBER`, `RANK`, `LEAD/LAG`) e CTEs.
* **02/02 — Início de Engenharia de Dados (Aula 1):**
  * Anotações ativas no mesmo dia + replay das demonstrações.
* **03/02 a 15/02 — Férias:**
  * Manter rigorosamente os 20 min/dia com replay da aula 02/02 e exercícios práticos para não quebrar o hábito.
* **16/02 e 23/02 — Engenharia de Dados (Aulas 2 e 3).**

---

## 🗄️ Como Registrar seus Estudos na Base de Dados

Você agora possui a ferramenta e a skill integradas. Para interagir com seu histórico:

```powershell
# 1. Ver a meta de hoje e referências sugeridas:
python scripts/study_tracker.py today

# 2. Registrar uma sessão de estudo:
python scripts/study_tracker.py log --disciplina "data_wrangling" --minutos 20 --topico "Joins e limpeza" --feynman "Entendi que inner join exclui nulos em ambas as chaves" --dificuldade 3 --material "Wes McKinney Cap. 8" --proximo "Linha 290 DW II"

# 3. Ver métricas de evolução, horas acumuladas e streak:
python scripts/study_tracker.py stats

# 4. Ver as últimas sessões registradas:
python scripts/study_tracker.py history
```

*Lembrete do MBA:* Dúvidas pedagógicas diretas do curso: `monitordsa@mbauspesalq.com`.

