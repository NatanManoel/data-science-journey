---
name: study-tracker
description: >-
  Gerencia e acompanha o plano de estudos de Data Science, Machine Learning e IA do usuário.
  Ative esta skill quando o usuário iniciar uma sessão de estudo, quiser registrar progresso,
  consultar o histórico e evolução na base de dados SQLite, checar as metas do dia,
  revisar anotações pelo método Feynman ou solicitar as melhores referências externas para os temas da grade.
---

# Study Tracker & Gestor de Aprendizado (MBA Data Science & IA)

Esta skill orienta o acompanhamento diário dos estudos com base no **princípio da constância inegociável (piso de 20 min/dia útil)**, registro de sessões na base de dados SQLite local, e fornecimento de referências padrão ouro da comunidade.

## Estrutura da Ferramenta

A base de dados de estudos está localizada em:
`database/study_tracker.db`

O script CLI de automação está disponível em:
[tracker.py](./scripts/tracker.py) (ou `scripts/study_tracker.py` na raiz do workspace).

---

## Procedimentos e Comandos

### 1. Iniciar o dia ou checar programação
Quando o usuário perguntar *"O que tenho para estudar hoje?"* ou *"Qual a meta de hoje?"*:
Execute:
```powershell
python scripts/study_tracker.py today
```
*Dica:* Pode-se passar `--date AAAA-MM-DD` para verificar datas futuras.

Apresente ao usuário:
1. A **Meta Piso (20 minutos)** do dia.
2. A **Meta +Energia** (caso tenha disposição extra sem mudar de tema).
3. A **Referência Externa Recomendada** para destravar rapidamente.

---

### 2. Registrar uma sessão de estudo concluída
Quando o usuário informar que concluiu o estudo ou relatar o que fez:
Solicite ou extraia da conversa:
- Disciplina (código: `data_wrangling`, `svm`, `estatistica`, `bi_dataviz`, `apis_llms`, etc.)
- Tempo em minutos (padrão: 20)
- Tópico estudado
- Resumo Feynman (1 a 3 frases explicando o conceito como se ensinasse a uma criança)
- Dificuldade sentida (1 a 5)
- Material consultado
- Onde parou / próximo passo

Execute o comando:
```powershell
python scripts/study_tracker.py log --disciplina "<codigo>" --minutos <minutos> --topico "<topico>" --feynman "<explicacao_simples>" --dificuldade <1_a_5> --material "<material>" --proximo "<onde_parou>"
```

---

### 3. Visualizar histórico e evolução
Quando o usuário pedir relatório de progresso ou evolução:
```powershell
python scripts/study_tracker.py stats
python scripts/study_tracker.py history --limit 5
```
Apresente uma síntese encorajadora com o total de horas acumuladas, sequência de dias e matérias mais estudadas.

---

### 4. Alavancas de Desbloqueio (Trava de Estudo)
Se o usuário estiver travado em um problema ou sem entender a teoria, nunca deixe-o passar mais de 10 minutos frustrado. Acione a **Alavanca de Desbloqueio**:

| Tema | Alavanca Imediata (5-15 min) |
|---|---|
| **Data Wrangling (Pandas/Joins)** | [Wes McKinney - Python for Data Analysis (Cap. 7 e 8)](https://wesmckinney.com/book/) |
| **Estatística / P-Value / Testes** | StatQuest no YouTube (Josh Starmer) playlist *Statistics Fundamentals* |
| **SVM (Margem, Hiperplano, Kernel)** | StatQuest: *Support Vector Machines* + Aurélien Géron (Hands-on ML Cap. 5) |
| **Árvores / Random Forest / XGBoost** | StatQuest: *Decision Trees* e *Random Forests* |
| **BI e Gráficos** | Consultar a tabela visual *Financial Times Visual Vocabulary* |
| **APIs e LLMs / RAG** | Documentação interativa FastAPI (`fastapi.tiangolo.com`) ou cursos de 1h de Andrew Ng |
| **Engenharia de Dados** | Livro *Designing Data-Intensive Applications* (Kleppmann) & *Data Engineering Zoomcamp* |

