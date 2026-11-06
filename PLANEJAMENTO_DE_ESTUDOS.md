# Planejamento de Estudos — Pós em Data Science e Analytics (USP/ESALQ — 1º Semestre 2026)

*Documento mestre auditado e alinhado à [Ementa do Curso.pdf](file:///c:/Users/natan/Documents/Data%20Science/Ementa%20do%20Curso.pdf), aos scripts reais do repositório e à sua rotina diária. Referências gratuitas em português validadas em [REFERENCIAS_GRATUITAS_PT.md](file:///c:/Users/natan/Documents/Data%20Science/REFERENCIAS_GRATUITAS_PT.md).*

---

## 1. Regras de Ouro & Logística Real da Rotina

* **Janela Oficial de Estudo (Seg, Ter, Qui, Sex):** **`08h35 às 08h55` (20 minutos cravados)** — logo após deixar a esposa no metrô e chegar em casa às `08h30`, antes de iniciar o expediente às `09h00/09h30`.
* **Exceção de Quarta-feira (Dia Presencial + Muay Thai à noite):** Quarta-feira **não tem código local no PC**. A janela de 15–20 min (no almoço ou transporte) é reservada exclusivamente para **realizar a Prova EaD obrigatória da aula ao vivo de terça-feira** (conforme págs. 5, 10 e 14 da Ementa: *"as provas são disponibilizadas no dia seguinte à aula ao vivo"*) ou revisar flashcards no App Mobile ([rotina_mobile.html](file:///c:/Users/natan/Documents/Data%20Science/rotina_mobile.html)).
* **Regra do Piso Diário (20 min):** Meta cumprida = **20 minutos focados**. Se o dia estiver corrido, 20 min mantém a corrente viva. Se sobrar energia, avance para a coluna **+Energia**.
* **Micro-Ciclo de 20 Minutos (`2 - 13 - 3 - 2`):**
  1. **2 min (Setup):** Abrir o arquivo exato listado na tabela do dia e ler a meta;
  2. **13 min (Código Ativo):** Rodar, testar e modificar 1 bloco do script;
  3. **3 min (Validação):** Inspecionar a saída (`shape`, `head()`, métrica ROC/R², gráfico);
  4. **2 min (Feynman):** Escrever 1 frase simples resumindo o aprendizado no tracker/app e fechar às `08h55`.
* **Proibido "Modo Maratona":** Se perder 1 dia, **não tente compensar fazendo 2 horas no dia seguinte**. Apenas retome os 20 minutos do ponto onde parou.
* **Terça-feira é Sagrada (`19h00–22h30`):** Aula ao vivo do MBA tem prioridade absoluta sobre o backlog.

---

## 2. Mapa das 3 Fases até Engenharia de Dados (`06/11/2026` a `02/02/2027`)

| Fase | Período | Aulas ao Vivo (Terças) + Prova EaD (Quartas) | Foco do Backlog (Janela `08h35–08h55`) |
| :--- | :--- | :--- | :--- |
| **Fase 1** | `06/11` a `08/12/2026` | **BI I, II, III** (`10`, `17`, `24/11`) + **SNA I, II** (`01`, `08/12`) | Fechar **Data Wrangling** (5 scripts) + **Estatística** + **SVM** (4 scripts) + Semente APIs |
| **Fase 2** | `09/12/2026` a `19/01/2027` | *Recesso de Aulas ao Vivo da Pós* | **Árvores, Boosting & Redes** + **Crawlers** + **Text Mining/NLP** + **APIs & RAG (LLMs)** |
| **Fase 3** | `20/01` a `01/02/2027` | **Gestão da Mudança** (`20/01`) + **Metodologias Ágeis** (`26/01`) | **Pesquisa Operacional (PuLP)** + ** Deep Learning** + **Esquenta Engenharia de Dados (SQL/MER/DER/1FN-3FN)** |
| **Marco** | **`02/02/2027`** | **Início de Engenharia de Dados I (Ao Vivo)** | Backlog 100% zerado e base de SQL/Modelagem Relacional/APIs pronta |

---

## 3. FASE 1 — Cronograma Diário Detalhado (`06/11` a `08/12/2026`)

### Semana 1 (`06/11` a `10/11`) — Retomada Data Wrangling + Estatística + BI I
| Data | Dia | Janela & Contexto | Meta Piso (20 min — Obrigatório) | Se tiver +Energia (+15 a 30 min) | Arquivo Real / Referência |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **06/11** | Sex | `08h35` (Home + Pull) | **Data Wrangling II:** retomar vídeo do `35:40` / linha `262` e anotar onde parou | Rodar o próximo bloco de código do script | [`(1.1) Script Data Wrangling.py`](file:///c:/Users/natan/Documents/Data%20Science/Data%20Wrangling/Aula%201/%281.1%29%20Script%20Data%20Wrangling.py) |
| **07/11** | Sáb | Manhã (Pós-Corrida) | **Data Wrangling II (Prática):** testar `merge`/`join` e tratamento de `isna()`/`fillna()` | Rodar script do Banco Mundial (`WDI`) | [`(2.2) Script WDI World Bank.py`](file:///c:/Users/natan/Documents/Data%20Science/Data%20Wrangling/Aula%201/%282.2%29%20Script%20WDI%20World%20Bank.py) |
| **08/11** | Dom | Descanso | **Revisão de 15 min:** checar app mobile e planejar a semana | Descanso mental completo | [rotina_mobile.html](file:///c:/Users/natan/Documents/Data%20Science/rotina_mobile.html) |
| **09/11** | Seg | `08h35` (Home + Push/MT) | **Fundamentos de Estatística:** resolver 3 exercícios da lista em Excel (testes Z/t ou Qui-quadrado) | +2 exercícios ou 1 flashcard (p-valor / IC) | Pasta [`Fundamentos de Estatística`](file:///c:/Users/natan/Documents/Data%20Science/Fundamentos%20de%20Estat%C3%ADstica) |
| **10/11** | Ter | `19h00` (**Aula ao Vivo**) | **BI e Data Visualization I:** assistir aula ao vivo + reproduzir 1 gráfico no Power BI | 5 linhas Feynman: Fato vs. Dimensão vs. KPI | Guia FT Visual Vocabulary |

### Semana 2 (`11/11` a `17/11`) — Prova EaD BI I + CVM + SVM + BI II
| Data | Dia | Janela & Contexto | Meta Piso (20 min — Obrigatório) | Se tiver +Energia (+15 a 30 min) | Arquivo Real / Referência |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **11/11** | Qua | **Presencial** + MT | **PROVA EaD (BI I):** fazer a prova EaD disponibilizada pós-aula (sem código local hoje) | Revisar 1 anotação Feynman no celular | Portal do Aluno MBA USP |
| **12/11** | Qui | `08h35` (Home + Corrida/MT) | **Data Wrangling (CVM):** carga do dataset CVM, inspeção de tipos e filtros iniciais | Agrupamentos (`groupby`) e `merge` cadastral | [`(3.1) Script CVM.py`](file:///c:/Users/natan/Documents/Data%20Science/Data%20Wrangling/Aula%201/%283.1%29%20Script%20CVM.py) |
| **13/11** | Sex | `08h35` (Home + Pull) | **SVM (Admissão):** rodar `StandardScaler` + `SVC.fit()` e matriz de confusão | Testar mudança de kernel (`linear` vs `rbf`) | [`SVM - Admissão.py`](file:///c:/Users/natan/Documents/Data%20Science/SVM%20-%20Support%20Vector%20Machines/SVM%20-%20Admiss%C3%A3o.py) |
| **14/11** | Sáb | Manhã (Pós-Corrida) | **Semente APIs & LLMs:** ler e rodar células `[1]` e `[2]` (FinOps + conexão Gemini) | Inspecionar células `[3]` e `[4]` (leitura PDF) | [`script.py`](file:///c:/Users/natan/Documents/Data%20Science/Desenvolvimento%20de%20APIs%20e%20Integra%C3%A7%C3%A3o%20Pr%C3%A1tica%20de%20LLMs/aula-api-llm/script.py) |
| **15/11** | Dom | Descanso | **Revisão de 15 min:** checagem semanal no app | Descanso | [rotina_mobile.html](file:///c:/Users/natan/Documents/Data%20Science/rotina_mobile.html) |
| **16/11** | Seg | `08h35` (Home + Push/MT) | **Data Wrangling (Copa):** carga e transformação de variáveis do script Jogos da Copa | Criar 1 métrica agregada por seleção | [`(4.1) Script Jogos Copa.py`](file:///c:/Users/natan/Documents/Data%20Science/Data%20Wrangling/Aula%201/%284.1%29%20Script%20Jogos%20Copa.py) |
| **17/11** | Ter | `19h00` (**Aula ao Vivo**) | **BI e Data Visualization II:** assistir aula ao vivo + montar 1 filtro/medida DAX | Comparar evolução visual em relação à BI I | Power BI Desktop |

### Semana 3 (`18/11` a `24/11`) — Prova EaD BI II + Fechamento Data Wrangling + SVM Churn + BI III
| Data | Dia | Janela & Contexto | Meta Piso (20 min — Obrigatório) | Se tiver +Energia (+15 a 30 min) | Arquivo Real / Referência |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **18/11** | Qua | **Presencial** + MT | **PROVA EaD (BI II):** concluir prova EaD da aula de terça no almoço/transporte | Ler resumo de Data Wrangling no celular | Portal do Aluno MBA USP |
| **19/11** | Qui | `08h35` (Home + Corrida/MT) | **Data Wrangling (Streaming - Parte 1):** carga e limpeza do dataset de Streaming | Explorar valores ausentes e duplicados | [`(5.1) Script Streaming.py`](file:///c:/Users/natan/Documents/Data%20Science/Data%20Wrangling/Aula%202/%285.1%29%20Script%20Streaming.py) |
| **20/11** | Sex | `08h35` (Home + Pull) | **Data Wrangling (Streaming - Parte 2):** finalizar notebook e **declarar Data Wrangling 100% concluído!** | Fazer a Prova EaD pendente de Data Wrangling (se houver) | [`(5.4) Script Streaming.ipynb`](file:///c:/Users/natan/Documents/Data%20Science/Data%20Wrangling/Aula%202/%285.4%29%20Script%20Streaming.ipynb) |
| **21/11** | Sáb | Manhã (Pós-Corrida) | **SVM (Churn):** rodar pipeline de predição de Churn + curva ROC / AUC | Testar `GridSearchCV` para hiperparâmetros `C` e `gamma` | [`SVM - Churn.py`](file:///c:/Users/natan/Documents/Data%20Science/SVM%20-%20Support%20Vector%20Machines/SVM%20-%20Churn.py) |
| **22/11** | Dom | Descanso | **Revisão de 15 min:** atualizar progresso no banco SQLite / App | Descanso | `python scripts/study_tracker.py stats` |
| **23/11** | Seg | `08h35` (Home + Push/MT) | **Fundamentos de Estatística:** 3 exercícios práticos (Correlação de Pearson e Teste F) | 1 frase Feynman sobre p-valor vs nível de significância $\alpha$ | [` Apostila Fundamentos de Estatística.pdf`](file:///c:/Users/natan/Documents/Data%20Science/Fundamentos%20de%20Estat%C3%ADstica/Aula%201/Apostila%20Fundamentos%20de%20Estat%C3%ADstica.pdf) |
| **24/11** | Ter | `19h00` (**Aula ao Vivo**) | **BI e Data Visualization III:** aula ao vivo (fechamento do módulo de BI) | Salvar template final do Dashboard Power BI | Power BI Desktop |

### Semana 4 (`25/11` a `01/12`) — Prova EaD BI III + Fechamento SVM + SNA I
| Data | Dia | Janela & Contexto | Meta Piso (20 min — Obrigatório) | Se tiver +Energia (+15 a 30 min) | Arquivo Real / Referência |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **25/11** | Qua | **Presencial** + MT | **PROVA EaD (BI III):** realizar prova EaD de fechamento de BI | Revisar conceitos de hiperplano e margem (SVM) | Portal do Aluno MBA USP |
| **26/11** | Qui | `08h35` (Home + Corrida/MT) | **SVM (Segmentação):** rodar script de segmentação e analisar fronteira de decisão | Comparar acurácia treino vs teste (overfitting) | [`SVM - Segmentação.py`](file:///c:/Users/natan/Documents/Data%20Science/SVM%20-%20Support%20Vector%20Machines/SVM%20-%20Segmenta%C3%A7%C3%A3o.py) |
| **27/11** | Sex | `08h35` (Home + Pull) | **SVM (Vendas):** rodar script de Vendas e **declarar SVM 100% concluído!** | Anotar resumo Feynman comparando kernels Linear, Poly e RBF | [`SVM - Vendas.py`](file:///c:/Users/natan/Documents/Data%20Science/SVM%20-%20Support%20Vector%20Machines/SVM%20-%20Vendas.py) |
| **28/11** | Sáb | Manhã (Pós-Corrida) | **APIs & LLMs (Chunking + Embeddings):** rodar células `[5]` a `[7]` do script RAG | Testar consulta semântica no ChromaDB | [`script.py`](file:///c:/Users/natan/Documents/Data%20Science/Desenvolvimento%20de%20APIs%20e%20Integra%C3%A7%C3%A3o%20Pr%C3%A1tica%20de%20LLMs/aula-api-llm/script.py) |
| **29/11** | Dom | Descanso | **Revisão de 15 min:** planejamento da semana de SNA | Descanso | [rotina_mobile.html](file:///c:/Users/natan/Documents/Data%20Science/rotina_mobile.html) |
| **30/11** | Seg | `08h35` (Home + Push/MT) | **Estatística Espacial (Revisão Rápida):** ler conceitos de Shapefile, Raster e Índice de Moran (LISA) | Mapear 5 termos-chave da Ementa (pág. 2) | [Ementa do Curso.pdf](file:///c:/Users/natan/Documents/Data%20Science/Ementa%20do%20Curso.pdf) |
| **01/12** | Ter | `19h00` (**Aula ao Vivo**) | **Social Network Analysis (SNA) I:** assistir aula ao vivo (grafos, nós, arestas, centralidade) | Rodar grafo exemplo com `networkx` | Aula ao Vivo MBA |

### Semana 5 (`02/12` a `08/12`) — Prova EaD SNA I + Início Árvores + Fechamento Fase 1 (SNA II)
| Data | Dia | Janela & Contexto | Meta Piso (20 min — Obrigatório) | Se tiver +Energia (+15 a 30 min) | Arquivo Real / Referência |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **02/12** | Qua | **Presencial** + MT | **PROVA EaD (SNA I):** realizar prova EaD da aula de terça | Flashcard: Grau, Betweenness e Closeness Centrality | Portal do Aluno MBA USP |
| **03/12** | Qui | `08h35` (Home + Corrida/MT) | **Árvores de Decisão (Classificação):** rodar script de Árvore de Decisão (Gini / Entropia / Poda) | Visualizar árvore gerada e importância de variáveis | [`Aula_1_Árvores_de_Decisão.py`](file:///c:/Users/natan/Documents/Data%20Science/Arvores%20de%20Decis%C3%A3o/Aula%201/Aula_1_%C3%81rvores_de_Decis%C3%A3o.py) |
| **04/12** | Sex | `08h35` (Home + Pull) | **Árvores de Regressão:** rodar script de regressão por árvore e avaliar MSE/$R^2$ | Comparar árvore rasa vs árvore profunda (overfitting) | [`Aula_1_Árvores_de_Regressão.py`](file:///c:/Users/natan/Documents/Data%20Science/Arvores%20de%20Decis%C3%A3o/Aula%201/Aula_1_%C3%81rvores_de_Regress%C3%A3o.py) |
| **05/12** | Sáb | Manhã (Pós-Corrida) | **Revisão SNA I + Estatística:** revisar métricas de grafos da aula de terça + 3 exercícios de estatística | Checar todas as Provas EaD realizadas até aqui | Portal do Aluno |
| **06/12** | Dom | Descanso | **Revisão de 15 min:** preparar fechamento da Fase 1 | Descanso | [rotina_mobile.html](file:///c:/Users/natan/Documents/Data%20Science/rotina_mobile.html) |
| **07/12** | Seg | `08h35` (Home + Push/MT) | **Ensemble Models (Bagging & Random Forest):** rodar parte 1 do script de Ensemble | Anotar diferença Feynman: Bagging vs Boosting | [`Aula_2_Métodos_de_Ensemble.py`](file:///c:/Users/natan/Documents/Data%20Science/Arvores%20de%20Decis%C3%A3o/Aula%202/Aula_2_M%C3%A9todos_de_Ensemble.py) |
| **08/12** | Ter | `19h00` (**Aula ao Vivo**) | **Social Network Analysis (SNA) II:** última aula ao vivo antes do recesso de fim de ano! | Anotar síntese final de SNA | Aula ao Vivo MBA |

---

## 4. FASE 2 — Recesso da Pós: Ataque ao Backlog Técnico (`09/12/2026` a `19/01/2027`)

*Sem aulas ao vivo nas terças-feiras! Isso libera energia mental para zerar os módulos práticos mantendo os mesmos **20 min/dia** (`08h35–08h55`).*

### Bloco 2.1 — Ensemble, Boosting, Redes Neurais & Crawlers (`09/12` a `23/12`)
* **09/12 (Qua - Presencial):** **PROVA EaD (SNA II)** no almoço/transporte.
* **10/12 e 11/12 (Qui/Sex):** Finalizar [`Aula_2_Métodos_de_Ensemble.py`](file:///c:/Users/natan/Documents/Data%20Science/Arvores%20de%20Decis%C3%A3o/Aula%202/Aula_2_M%C3%A9todos_de_Ensemble.py) e rodar [`Aula_3_Boosting.py`](file:///c:/Users/natan/Documents/Data%20Science/Arvores%20de%20Decis%C3%A3o/Aula%203/Aula_3_Boosting.py) (já descompactado!).
* **12/12 (Sáb):** Rodar notebook [`Aula_3_Redes.ipynb`](file:///c:/Users/natan/Documents/Data%20Science/Arvores%20de%20Decis%C3%A3o/Aula%203/Aula_3_Redes.ipynb) — **Árvores, Redes e Ensemble 100% concluído!**
* **14/12 a 23/12 (Seg a Qua — 8 sessões de 20 min):**
  * **Coleta de Dados: Crawlers e Web Scraping** (Ementa pág. 3): protocolo HTTP (`GET`/`POST`), estrutura DOM/HTML, `requests` + `BeautifulSoup`, paginação e salvamento estruturado em CSV/SQLite.
* **24/12 e 25/12:** Folga total de Natal.

### Bloco 2.2 — Text Mining, NLP & APIs de LLMs (`26/12/2026` a `19/01/2027`)
* **26/12 a 06/01 (com folga em 31/12 e 01/01):**
  * **Text Mining & Sentiment Analysis:** rodar passo a passo os notebooks reais da pasta [`Text Mining`](file:///c:/Users/natan/Documents/Data%20Science/Text%20Mining):
    1. [`text_mining_aula_1.ipynb`](file:///c:/Users/natan/Documents/Data%20Science/Text%20Mining/text_mining_aula_1.ipynb) (Tokenização, Stopwords, Stemming/Lemmatization, TF-IDF);
    2. [`sentiment-analysis-2.ipynb`](file:///c:/Users/natan/Documents/Data%20Science/Text%20Mining/sentiment-analysis-2.ipynb) e [`sentiment-analysis-3.ipynb`](file:///c:/Users/natan/Documents/Data%20Science/Text%20Mining/sentiment-analysis-3.ipynb) (Polaridade, Naive Bayes, classificação de emoções);
    3. [`aula-3-ABSA-complementar.ipynb`](file:///c:/Users/natan/Documents/Data%20Science/Text%20Mining/aula-3-ABSA-complementar.ipynb) (Aspect-Based Sentiment Analysis).
* **07/01 a 19/01:**
  * **Desenvolvimento de APIs e Integração Prática de LLMs:** dominar a arquitetura completa que já está na sua pasta [`api`](file:///c:/Users/natan/Documents/Data%20Science/Desenvolvimento%20de%20APIs%20e%20Integra%C3%A7%C3%A3o%20Pr%C3%A1tica%20de%20LLMs/aula-api-llm/api):
    1. Contratos Pydantic em [`schemas.py`](file:///c:/Users/natan/Documents/Data%20Science/Desenvolvimento%20de%20APIs%20e%20Integra%C3%A7%C3%A3o%20Pr%C3%A1tica%20de%20LLMs/aula-api-llm/api/schemas.py);
    2. Pipeline de ingestão e busca vetorial em [`rag.py`](file:///c:/Users/natan/Documents/Data%20Science/Desenvolvimento%20de%20APIs%20e%20Integra%C3%A7%C3%A3o%20Pr%C3%A1tica%20de%20LLMs/aula-api-llm/api/rag.py);
    3. Endpoints FastAPI (`/health`, `/ingest`, `/ask`) e tratamento de erros em [`main.py`](file:///c:/Users/natan/Documents/Data%20Science/Desenvolvimento%20de%20APIs%20e%20Integra%C3%A7%C3%A3o%20Pr%C3%A1tica%20de%20LLMs/aula-api-llm/api/main.py);
    4. Subir servidor com `uvicorn` e testar via Swagger UI (`/docs`).

---

## 5. FASE 3 — Volta às Aulas + Preparação Direcionada para Engenharia de Dados (`20/01` a `02/02/2027`)

### Semana de `20/01` a `26/01` — Pesquisa Operacional (PuLP) + Deep Learning Base
* **20/01 (Ter - 19h00):** Aula ao vivo **Gestão da Mudança na Era Digital**.
* **21/01 (Qua - Presencial):** **PROVA EaD (Gestão da Mudança)** no almoço.
* **22/01 (Qui - 08h35):** **Pesquisa Operacional I:** rodar [`PuLP_Horas de Estudo.py`](file:///c:/Users/natan/Documents/Data%20Science/Pesquisa%20Organizacional/Aula%201/PuLP_Horas%20de%20Estudo.py) e [`PuLP_Venda de Livros.py`](file:///c:/Users/natan/Documents/Data%20Science/Pesquisa%20Organizacional/Aula%202/PuLP_Venda%20de%20Livros.py) (função objetivo, variáveis de decisão e restrições).
* **23/01 (Sex - 08h35):** **Pesquisa Operacional II:** rodar [`PuLP_Problema de Transporte.py`](file:///c:/Users/natan/Documents/Data%20Science/Pesquisa%20Organizacional/Aula%203/PuLP_Problema%20de%20Transporte.py) e [`PuLP_Corte Bobinas de Aço.py`](file:///c:/Users/natan/Documents/Data%20Science/Pesquisa%20Organizacional/Aula%201/PuLP_Corte%20Bobinas%20de%20A%C3%A7o.py).
* **24/01 (Sáb):** **Deep Learning I:** rodar [`Aula1_primeira_NN.ipynb`](file:///c:/Users/natan/Documents/Data%20Science/Deep%20Learning%20e%20IA/Aula1_primeira_NN.ipynb) (Feed-Forward, função de ativação, backpropagation e função custo).
* **26/01 (Ter - 19h00):** Aula ao vivo **Metodologias Ágeis** (Scrum, Kanban, Lean, Squads).

### Semana de `27/01` a `02/02` — Esquenta Oficial de Engenharia de Dados (Alinhado à Ementa Pág. 6)
*A ementa oficial da USP/ESALQ em Engenharia de Dados cobra **SGBD, SQL, MER/DER, Álgebra Relacional e Formas Normais (1FN, 2FN, 3FN)**. Esta semana prepara você exatamente para esses tópicos + integração Python:*

| Data | Dia | Meta de 20 Minutos (`08h35–08h55`) | Entregável Prático |
| :--- | :--- | :--- | :--- |
| **27/01** | Qua (Presencial) | **PROVA EaD (Metodologias Ágeis)** + Leitura dos conceitos de MER vs DER | Prova EaD concluída |
| **28/01** | Qui (`08h35`) | **Modelagem Relacional & Normalização:** revisar Entidade-Relacionamento (cardinalidade $1:1$, $1:N$, $N:M$) e aplicar **1FN, 2FN e 3FN** em uma tabela desnormalizada | Esquema de 3 tabelas normalizadas (`clientes`, `pedidos`, `itens`) |
| **29/01** | Sex (`08h35`) | **Álgebra Relacional & SQL Essencial:** praticar Seleção ($\sigma$), Projeção ($\pi$), Junção ($\bowtie$) equivalentes em SQL (`SELECT`, `WHERE`, `INNER/LEFT JOIN`, `GROUP BY`, `HAVING`) | Rodar 5 queries analíticas no banco [`study_tracker.db`](file:///c:/Users/natan/Documents/Data%20Science/database/study_tracker.db) |
| **30/01** | Sáb (Manhã) | **Mini-Pipeline End-to-End:** conectar script Python (Crawler ou API) salvando dados limpos via `pandas.to_sql()` em banco SQLite com chave primária/estrangeira | Script `etl_demo.py` funcional |
| **31/01** | Dom | Descanso e revisão leve | Pronto para a nova fase |
| **01/02** | Seg (`08h35`) | **Warm-up da Aula:** baixar slides/scripts de **Engenharia de Dados I** e testar ambiente SQL/Python | Ambiente 100% validado |
| **02/02** | **Ter (`19h00`)** | 🚀 **AULA AO VIVO: ENGENHARIA DE DADOS I** | Chegada com backlog zerado e base sólida! |

---

## 6. Radar de 2027 — Mapa dos Próximos Módulos da Ementa (Págs. 7 a 14)

Para você não ser pego de surpresa após Engenharia de Dados, aqui está como a sua base atual se conecta aos módulos avançados de 2027 da [Ementa do Curso.pdf](file:///c:/Users/natan/Documents/Data%20Science/Ementa%20do%20Curso.pdf):

1. **Módulo Não Supervisionado (Redução de Dimensionalidade & Agrupamentos):**
   * **Clustering** (K-Means e Hierárquico/Dendrograma) $\rightarrow$ usa padronização **Z-score** (vista em Estatística e SVM).
   * **Análise Fatorial e PCA** $\rightarrow$ usa matriz de correlação de **Pearson** e **Teste de Bartlett / KMO**.
   * **Anacor & MCA (Correspondência Simples e Múltipla)** $\rightarrow$ usa tabelas de contingência e **Teste Qui-Quadrado ($\chi^2$)** (visto em Fundamentos de Estatística).
2. **Módulo Supervisionado (Modelos Lineares Generalizados — GLM & Séries Temporais):**
   * **Regressão Simples e Múltipla (OLS):** $R^2$, Stepwise, multicolinearidade (VIF), normalidade dos resíduos (**Shapiro-Francia**) e transformação de **Box-Cox**.
   * **Regressão Logística Binária e Multinomial:** função sigmoide, máxima verossimilhança (Log-Likelihood), cutoff, **Curva ROC e Índice de Gini**.
   * **Dados de Contagem (Poisson, Binomial Negativa e Zero-Inflated/ZINB):** teste de superdispersão (*overdispersion*) de **Cameron & Trivedi**.
   * **Modelagem Multinível (HLM2 / HLM3):** efeitos fixos vs. efeitos aleatórios (dados aninhados/longitudinais).
   * **Séries Temporais:** decomposição, suavização exponencial (**Holt-Winters**) e modelos **ARIMA / SARIMA**.
3. **Tomada de Decisão, Big Data & Riscos:**
   * **Método AHP e AHP-Gaussiano** (Pesquisa Operacional / Multicritério), **Algoritmos Genéticos**, **Cloud/Spark (HDFS, MapReduce)**, **Gestão de Riscos (Basiléia III / Risco de Crédito)** e **LGPD**.
