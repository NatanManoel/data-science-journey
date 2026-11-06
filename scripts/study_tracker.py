"""
Study Tracker & Evolution Database for MBA Data Science & AI.
Gerencia o progresso diário, sessões de estudo (regra de 20 min),
resumos no método Feynman e métricas de evolução.
"""

import sys
import os
import sqlite3
import argparse
from datetime import datetime, date

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database", "study_tracker.db"))

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS disciplinas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT UNIQUE NOT NULL,
        nome TEXT NOT NULL,
        categoria TEXT NOT NULL,
        status TEXT DEFAULT 'Pendente',
        horas_meta REAL DEFAULT 15.0,
        referencias_chave TEXT
    );

    CREATE TABLE IF NOT EXISTS sessoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        disciplina_id INTEGER NOT NULL,
        data TEXT NOT NULL,
        duracao_min INTEGER DEFAULT 20,
        topico TEXT NOT NULL,
        feynman_resumo TEXT,
        dificuldade INTEGER CHECK(dificuldade BETWEEN 1 AND 5),
        material_utilizado TEXT,
        proximo_passo TEXT,
        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (disciplina_id) REFERENCES disciplinas(id)
    );

    CREATE TABLE IF NOT EXISTS cronograma (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fase TEXT NOT NULL,
        data_prevista TEXT NOT NULL,
        dia_semana TEXT,
        disciplina_codigo TEXT NOT NULL,
        meta_dia TEXT NOT NULL,
        meta_energia TEXT,
        referencia_sugerida TEXT,
        concluido BOOLEAN DEFAULT 0,
        data_conclusao TEXT
    );

    CREATE VIEW IF NOT EXISTS vw_resumo_disciplinas AS
    SELECT 
        d.id,
        d.codigo,
        d.nome,
        d.categoria,
        d.status,
        COUNT(s.id) AS total_sessoes,
        COALESCE(SUM(s.duracao_min), 0) AS total_minutos,
        ROUND(COALESCE(SUM(s.duracao_min), 0) / 60.0, 2) AS total_horas,
        ROUND(AVG(s.dificuldade), 1) AS media_dificuldade,
        MAX(s.data) AS ultima_sessao
    FROM disciplinas d
    LEFT JOIN sessoes s ON d.id = s.disciplina_id
    GROUP BY d.id;
    """)

    # Seed disciplinas completas da Ementa (atuais + radar 2027)
    disciplinas_iniciais = [
        ("data_wrangling", "Data Wrangling", "Engenharia & Dados", "Em Andamento", 20.0, 
         "Scripts: (1.1) DW, (2.2) WDI, (3.1) CVM, (4.1) Copa, (5.1) Streaming | Livro: Wes McKinney Cap. 7-8"),
        ("estatistica", "Fundamentos de Estatística", "Fundamentos", "Em Andamento", 25.0, 
         "Fávero & Belfiore (Manual de Análise de Dados) | Playlist Fernanda Maciel | StatQuest"),
        ("svm", "Support Vector Machines (SVM)", "Machine Learning", "Em Andamento", 15.0, 
         "Scripts: Admissão, Churn, Segmentação, Vendas | Aurélien Géron Cap. 5 | Didática Tech ML"),
        ("arvores_ensemble", "Árvores, Redes & Ensemble Models", "Machine Learning", "Pendente", 20.0, 
         "Scripts: Aula_1_Árvores, Aula_2_Ensemble, Aula_3_Boosting, Aula_3_Redes | Géron Cap. 6-7"),
        ("bi_dataviz", "BI e Data Visualization", "Analytics & Negócios", "Em Andamento", 15.0, 
         "Aulas Ao Vivo (10, 17, 24/11) + Provas EaD às quartas | Curso Power BI Data Science Academy"),
        ("social_network", "Social Network Analysis (SNA)", "Analytics & Negócios", "Pendente", 10.0, 
         "Aulas Ao Vivo (01 e 08/12) + Provas EaD às quartas | NetworkX & Barabási (Network Science)"),
        ("crawlers", "Coleta de Dados: Crawlers & Scraping", "Engenharia & Dados", "Pendente", 12.0, 
         "HTTP GET/POST, DOM/HTML, BeautifulSoup4, paginação e persistência SQLite/CSV"),
        ("text_mining_nlp", "Text Mining, Sentiment Analysis & NLP", "IA & NLP", "Pendente", 15.0, 
         "Notebooks: text_mining_aula_1, sentiment-analysis-2 e 3, aula-3-ABSA | Playlist NLP USP"),
        ("apis_llms", "Desenvolvimento de APIs & Integração de LLMs", "Engenharia & IA", "Em Andamento", 20.0, 
         "Arquivos: script.py, api/schemas.py, api/rag.py, api/main.py | FastAPI PT-BR Docs"),
        ("pesquisa_operacional", "Pesquisa Operacional & Otimização", "Fundamentos", "Pendente", 15.0, 
         "Scripts PuLP: Horas de Estudo, Venda de Livros, Problema de Transporte, Bobinas de Aço"),
        ("deep_learning", "Deep Learning e IA", "Machine Learning", "Pendente", 25.0, 
         "Notebook: Aula1_primeira_NN.ipynb | 3Blue1Brown PT-BR | Deep Learning Book Brasil"),
        ("estatistica_espacial", "Análise Estatística Espacial", "Fundamentos", "Pendente", 10.0, 
         "Shapefiles, Dados Raster, Índice de Moran Global/Local (LISA) | GeoPandas & PySAL"),
        ("engenharia_dados", "Engenharia de Dados (SQL, MER/DER, 1FN-3FN)", "Engenharia & Dados", "Pendente", 30.0, 
         "Ementa Pág. 6: SGBD, SQL, MER/DER, Álgebra Relacional, Normalização 1FN-3FN | Curso SQL Téo Me Why"),
        ("metodologias_ageis", "Gestão da Mudança & Metodologias Ágeis", "Gestão & Negócios", "Pendente", 8.0, 
         "Aulas Ao Vivo (20/01 e 26/01) + Provas EaD | Scrum, Kanban, Lean, Squads"),
        ("nao_supervisionado_2027", "Módulo 2027: Clustering, PCA/Fatorial & Anacor/MCA", "Modelagem Avançada (2027)", "No Radar", 25.0, 
         "K-Means, Hierárquico, Dendrograma, Bartlett/KMO, Qui-Quadrado, Mapa Perceptual"),
        ("supervisionado_glm_2027", "Módulo 2027: Regressão OLS, Logística, Contagem & Multinível", "Modelagem Avançada (2027)", "No Radar", 35.0, 
         "OLS/Box-Cox, Logística/ROC/Gini, Poisson/Binomial Negativa/ZINB, HLM/GLMM, Séries Temporais ARIMA")
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO disciplinas (codigo, nome, categoria, status, horas_meta, referencias_chave)
        VALUES (?, ?, ?, ?, ?, ?)
    """, disciplinas_iniciais)

    # Atualiza cronograma completo da Fase 1 (06/11 a 09/12) + Marcos Fase 2 e 3
    cursor.execute("DELETE FROM cronograma WHERE concluido = 0")
    cronograma_atualizado = [
        ("Fase 1", "2026-11-06", "Sex", "data_wrangling", 
         "08h35: Retomar DW II do 35:40 / L262 em (1.1) Script Data Wrangling.py", 
         "+energia: Rodar próximo bloco do script", 
         "Arquivo: Data Wrangling/Aula 1/(1.1) Script Data Wrangling.py"),
        ("Fase 1", "2026-11-07", "Sáb", "data_wrangling", 
         "Manhã: Praticar merge/join e limpeza + rodar (2.2) Script WDI World Bank.py", 
         "+energia: Explorar indicadores WDI", 
         "Arquivo: Data Wrangling/Aula 1/(2.2) Script WDI World Bank.py"),
        ("Fase 1", "2026-11-08", "Dom", "metodologias_ageis", 
         "15 min: Revisão semanal no App Mobile e planejamento", 
         "Descanso mental completo", 
         "App: https://natanmanoel.github.io/data-science-journey/"),
        ("Fase 1", "2026-11-09", "Seg", "estatistica", 
         "08h35: Resolver 3 exercícios da lista em Excel (Testes Z/t ou Qui-quadrado)", 
         "+energia: +1 flashcard p-valor / IC", 
         "Pasta: Fundamentos de Estatística/Aula 1"),
        ("Fase 1", "2026-11-10", "Ter", "bi_dataviz", 
         "19h00 (AULA AO VIVO): BI e Data Visualization I + reproduzir 1 gráfico", 
         "+energia: 5 linhas Feynman: Fato vs Dimensão vs KPI", 
         "Curso Power BI Data Science Academy / FT Visual Vocabulary"),
        ("Fase 1", "2026-11-11", "Qua", "bi_dataviz", 
         "PRESENCIAL (Sem código no PC): Fazer a PROVA EaD de BI I no almoço/transporte", 
         "+energia: Revisar resumo Feynman no celular", 
         "Portal do Aluno MBA USP/ESALQ"),
        ("Fase 1", "2026-11-12", "Qui", "data_wrangling", 
         "08h35: DW III — Carga do dataset CVM e filtros iniciais em (3.1) Script CVM.py", 
         "+energia: Groupby + merge cadastral", 
         "Arquivo: Data Wrangling/Aula 1/(3.1) Script CVM.py"),
        ("Fase 1", "2026-11-13", "Sex", "svm", 
         "08h35: SVM Caso 1 — Rodar StandardScaler + SVC.fit() em SVM - Admissão.py", 
         "+energia: Testar kernel linear vs rbf", 
         "Arquivo: SVM - Support Vector Machines/SVM - Admissão.py"),
        ("Fase 1", "2026-11-14", "Sáb", "apis_llms", 
         "Manhã: Semente APIs — Rodar células [1] e [2] (FinOps + Gemini) em script.py", 
         "+energia: Células [3]-[4] leitura de PDF", 
         "Arquivo: Desenvolvimento de APIs e Integração Prática de LLMs/aula-api-llm/script.py"),
        ("Fase 1", "2026-11-15", "Dom", "metodologias_ageis", 
         "15 min: Revisão semanal e descanso", 
         "Descanso mental", 
         "App: https://natanmanoel.github.io/data-science-journey/"),
        ("Fase 1", "2026-11-16", "Seg", "data_wrangling", 
         "08h35: DW IV — Carga e transformação em (4.1) Script Jogos Copa.py", 
         "+energia: Criar 1 métrica agregada por seleção", 
         "Arquivo: Data Wrangling/Aula 1/(4.1) Script Jogos Copa.py"),
        ("Fase 1", "2026-11-17", "Ter", "bi_dataviz", 
         "19h00 (AULA AO VIVO): BI e Data Visualization II + montar 1 filtro/medida DAX", 
         "+energia: Comparar evolução visual em relação à BI I", 
         "Power BI Desktop"),
        ("Fase 1", "2026-11-18", "Qua", "bi_dataviz", 
         "PRESENCIAL (Sem código no PC): Fazer a PROVA EaD de BI II no almoço/transporte", 
         "+energia: Ler resumo Feynman no celular", 
         "Portal do Aluno MBA USP/ESALQ"),
        ("Fase 1", "2026-11-19", "Qui", "data_wrangling", 
         "08h35: DW V (Pt 1) — Carga e limpeza em (5.1) Script Streaming.py", 
         "+energia: Explorar valores ausentes e duplicados", 
         "Arquivo: Data Wrangling/Aula 2/(5.1) Script Streaming.py"),
        ("Fase 1", "2026-11-20", "Sex", "data_wrangling", 
         "08h35: DW V (Fim!) — Finalizar (5.4) Script Streaming.ipynb e fechar Data Wrangling!", 
         "+energia: Conferir Prova EaD de Data Wrangling", 
         "Arquivo: Data Wrangling/Aula 2/(5.4) Script Streaming.ipynb"),
        ("Fase 1", "2026-11-21", "Sáb", "svm", 
         "Manhã: SVM Caso 2 — Rodar pipeline de Churn + Curva ROC/AUC em SVM - Churn.py", 
         "+energia: Testar GridSearchCV para C e gamma", 
         "Arquivo: SVM - Support Vector Machines/SVM - Churn.py"),
        ("Fase 1", "2026-11-22", "Dom", "metodologias_ageis", 
         "15 min: Revisão semanal no App e descanso", 
         "Descanso", 
         "python scripts/study_tracker.py stats"),
        ("Fase 1", "2026-11-23", "Seg", "estatistica", 
         "08h35: Resolver 3 exercícios práticos (Correlação de Pearson e Teste F)", 
         "+energia: 1 frase Feynman sobre p-valor vs alfa", 
         "Arquivo: Fundamentos de Estatística/Aula 1/Apostila Fundamentos de Estatística.pdf"),
        ("Fase 1", "2026-11-24", "Ter", "bi_dataviz", 
         "19h00 (AULA AO VIVO): BI e Data Visualization III (fechamento BI)", 
         "+energia: Salvar template final Power BI", 
         "Power BI Desktop"),
        ("Fase 1", "2026-11-25", "Qua", "bi_dataviz", 
         "PRESENCIAL (Sem código no PC): Fazer a PROVA EaD de BI III no almoço", 
         "+energia: Revisar conceito de margem e hiperplano (SVM)", 
         "Portal do Aluno MBA USP/ESALQ"),
        ("Fase 1", "2026-11-26", "Qui", "svm", 
         "08h35: SVM Caso 3 — Rodar SVM - Segmentação.py e analisar fronteira de decisão", 
         "+energia: Comparar acurácia treino vs teste", 
         "Arquivo: SVM - Support Vector Machines/SVM - Segmentação.py"),
        ("Fase 1", "2026-11-27", "Sex", "svm", 
         "08h35: SVM Caso 4 (Fim SVM!) — Rodar SVM - Vendas.py e fechar módulo SVM!", 
         "+energia: Feynman comparando kernels Linear, Poly e RBF", 
         "Arquivo: SVM - Support Vector Machines/SVM - Vendas.py"),
        ("Fase 1", "2026-11-28", "Sáb", "apis_llms", 
         "Manhã: APIs & LLMs — Rodar células [5] a [7] (Chunking + ChromaDB) em script.py", 
         "+energia: Testar consulta semântica no ChromaDB", 
         "Arquivo: Desenvolvimento de APIs e Integração Prática de LLMs/aula-api-llm/script.py"),
        ("Fase 1", "2026-11-29", "Dom", "metodologias_ageis", 
         "15 min: Planejamento da semana de SNA", 
         "Descanso", 
         "App Mobile"),
        ("Fase 1", "2026-11-30", "Seg", "estatistica_espacial", 
         "08h35: Revisar conceitos de Shapefile, Raster e Índice de Moran (LISA)", 
         "+energia: Mapear 5 termos-chave da Ementa (pág. 2)", 
         "Ementa do Curso.pdf (pág. 2)"),
        ("Fase 1", "2026-12-01", "Ter", "social_network", 
         "19h00 (AULA AO VIVO): Social Network Analysis (SNA) I", 
         "+energia: Rodar grafo exemplo com networkx", 
         "Documentação NetworkX"),
        ("Fase 1", "2026-12-02", "Qua", "social_network", 
         "PRESENCIAL (Sem código no PC): Fazer a PROVA EaD de SNA I no almoço", 
         "+energia: Flashcard Grau, Betweenness e Closeness", 
         "Portal do Aluno MBA USP/ESALQ"),
        ("Fase 1", "2026-12-03", "Qui", "arvores_ensemble", 
         "08h35: Árvores I — Rodar Aula_1_Árvores_de_Decisão.py (Gini, Entropia, Poda)", 
         "+energia: Visualizar importância de variáveis", 
         "Arquivo: Arvores de Decisão/Aula 1/Aula_1_Árvores_de_Decisão.py"),
        ("Fase 1", "2026-12-04", "Sex", "arvores_ensemble", 
         "08h35: Árvores I — Rodar Aula_1_Árvores_de_Regressão.py e avaliar MSE/R²", 
         "+energia: Comparar árvore rasa vs profunda", 
         "Arquivo: Arvores de Decisão/Aula 1/Aula_1_Árvores_de_Regressão.py"),
        ("Fase 1", "2026-12-05", "Sáb", "social_network", 
         "Manhã: Revisar métricas de grafos (SNA I) + 3 exercícios de estatística", 
         "+energia: Auditar todas as Provas EaD realizadas", 
         "Portal do Aluno MBA USP/ESALQ"),
        ("Fase 1", "2026-12-06", "Dom", "metodologias_ageis", 
         "15 min: Preparar fechamento da Fase 1", 
         "Descanso", 
         "App Mobile"),
        ("Fase 1", "2026-12-07", "Seg", "arvores_ensemble", 
         "08h35: Ensemble — Rodar parte 1 de Aula_2_Métodos_de_Ensemble.py (Bagging/RF)", 
         "+energia: Feynman: Bagging vs Boosting", 
         "Arquivo: Arvores de Decisão/Aula 2/Aula_2_Métodos_de_Ensemble.py"),
        ("Fase 1", "2026-12-08", "Ter", "social_network", 
         "19h00 (AULA AO VIVO): Social Network Analysis (SNA) II — Última aula do ano!", 
         "+energia: Síntese final de SNA", 
         "Aula ao Vivo MBA"),
        ("Fase 2", "2026-12-09", "Qua", "social_network", 
         "PRESENCIAL (Sem código no PC): Fazer a PROVA EaD de SNA II e abrir Fase 2!", 
         "+energia: Celebrar conclusão da Fase 1!", 
         "Portal do Aluno MBA USP/ESALQ")
    ]
    cursor.executemany("""
        INSERT INTO cronograma (fase, data_prevista, dia_semana, disciplina_codigo, meta_dia, meta_energia, referencia_sugerida)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, cronograma_atualizado)

    conn.commit()
    conn.close()
    print("Base de dados de estudos inicializada com sucesso!")

def log_session(codigo, minutos, topico, feynman, dificuldade, material, proximo):
    conn = get_connection()
    cursor = conn.cursor()

    # Busca id da disciplina
    cursor.execute("SELECT id, nome FROM disciplinas WHERE codigo = ? OR nome LIKE ?", (codigo, f"%{codigo}%"))
    row = cursor.fetchone()
    if not row:
        print(f"Erro: Disciplina '{codigo}' não encontrada. Use 'list-disciplinas' para ver códigos válidos.")
        conn.close()
        return False

    disc_id, disc_nome = row["id"], row["nome"]
    hoje = date.today().isoformat()

    cursor.execute("""
        INSERT INTO sessoes (disciplina_id, data, duracao_min, topico, feynman_resumo, dificuldade, material_utilizado, proximo_passo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (disc_id, hoje, minutos, topico, feynman, dificuldade, material, proximo))

    # Atualiza status da disciplina para 'Em Andamento' se estiver pendente
    cursor.execute("UPDATE disciplinas SET status = 'Em Andamento' WHERE id = ? AND status = 'Pendente'", (disc_id,))

    # Verifica se há meta do dia no cronograma e marca como concluída
    cursor.execute("""
        UPDATE cronograma 
        SET concluido = 1, data_conclusao = ? 
        WHERE data_prevista = ? AND disciplina_codigo = ? AND concluido = 0
    """, (hoje, hoje, codigo))

    conn.commit()
    conn.close()

    print(f"\n[OK] Sessao registrada com sucesso!")
    print(f"Disciplina : {disc_nome}")
    print(f"Tempo      : {minutos} minutos | Data: {hoje}")
    print(f"Topico     : {topico}")
    if feynman:
        print(f"Feynman    : \"{feynman}\"")
    if proximo:
        print(f"Proximo    : {proximo}")
    return True

def show_today(target_date=None):
    conn = get_connection()
    cursor = conn.cursor()
    target = target_date or date.today().isoformat()

    cursor.execute("SELECT * FROM cronograma WHERE data_prevista = ?", (target,))
    row = cursor.fetchone()

    print("=" * 75)
    print(f"PLANO DE ESTUDOS - PROGRAMAÇÃO PARA {target}")
    print("=" * 75)

    if row:
        cursor.execute("SELECT nome, referencias_chave FROM disciplinas WHERE codigo = ?", (row["disciplina_codigo"],))
        disc = cursor.fetchone()
        disc_nome = disc["nome"] if disc else row["disciplina_codigo"]

        status_str = "[ CONCLUÍDO ]" if row["concluido"] else "[ PENDENTE ]"
        print(f"Status       : {status_str}")
        print(f"Disciplina   : {disc_nome} ({row['dia_semana']})")
        print(f"Meta Piso    : {row['meta_dia']} (20 minutos)")
        print(f"+ Energia    : {row['meta_energia']}")
        print(f"Referência   : {row['referencia_sugerida']}")
        if disc and disc["referencias_chave"]:
            print(f"Base Chave   : {disc['referencias_chave']}")
    else:
        print("Nenhuma atividade específica agendada para esta data no cronograma direto.")
        print("Dica: você pode escolher um tópico do backlog ou realizar 20 min de revisão.")

    # Mostra sessões já realizadas hoje
    cursor.execute("""
        SELECT s.duracao_min, s.topico, d.nome, s.feynman_resumo 
        FROM sessoes s
        JOIN disciplinas d ON s.disciplina_id = d.id
        WHERE s.data = ?
    """, (target,))
    sessoes_hoje = cursor.fetchall()

    if sessoes_hoje:
        print("\nSessões já realizadas hoje:")
        total_hoje = 0
        for s in sessoes_hoje:
            total_hoje += s["duracao_min"]
            print(f" - [{s['duracao_min']} min] {s['nome']}: {s['topico']}")
            if s["feynman_resumo"]:
                print(f"   Feynman: {s['feynman_resumo']}")
        print(f"Total estudado hoje: {total_hoje} minutos.")
    else:
        print("\nNenhuma sessão registrada ainda para o dia de hoje.")
    print("=" * 75)
    conn.close()

def show_stats():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM vw_resumo_disciplinas ORDER BY total_minutos DESC")
    resumos = cursor.fetchall()

    cursor.execute("SELECT COUNT(DISTINCT data), COALESCE(SUM(duracao_min), 0), COUNT(id) FROM sessoes")
    dias_distintos, total_min, total_sessoes = cursor.fetchone()

    cursor.execute("SELECT COUNT(*), SUM(concluido) FROM cronograma")
    total_metas, metas_concluidas = cursor.fetchone()
    metas_concluidas = metas_concluidas or 0

    print("=" * 80)
    print("HISTÓRICO DE APRENDIZADO & MÉTRICAS DE EVOLUÇÃO")
    print("=" * 80)
    print(f"Total de Dias com Estudos : {dias_distintos} dia(s)")
    print(f"Total de Sessões          : {total_sessoes}")
    print(f"Total de Tempo Dedicado   : {round(total_min / 60.0, 2)} horas ({total_min} minutos)")
    print(f"Progresso do Cronograma   : {metas_concluidas}/{total_metas} metas concluídas")
    print("-" * 80)
    print(f"{'DISCIPLINA':<32} | {'STATUS':<12} | {'SESSÕES':<7} | {'HORAS':<6} | {'DIFICULDADE'}")
    print("-" * 80)
    for r in resumos:
        dif = f"{r['media_dificuldade']}/5" if r['media_dificuldade'] else "-"
        print(f"{r['nome'][:30]:<32} | {r['status']:<12} | {r['total_sessoes']:<7} | {r['total_horas']:<6} | {dif}")
    print("=" * 80)
    conn.close()

def show_history(limit=10):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT s.id, s.data, d.nome AS disciplina, s.duracao_min, s.topico, 
               s.feynman_resumo, s.dificuldade, s.material_utilizado, s.proximo_passo
        FROM sessoes s
        JOIN disciplinas d ON s.disciplina_id = d.id
        ORDER BY s.data DESC, s.id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()

    print("=" * 85)
    print(f"ÚLTIMAS {limit} SESSÕES DE ESTUDO REGISTRADAS")
    print("=" * 85)
    if not rows:
        print("Nenhuma sessão registrada até o momento.")
    for r in rows:
        print(f"[{r['data']}] {r['disciplina']} ({r['duracao_min']} min) - Dificuldade: {r['dificuldade'] or '-'}/5")
        print(f"  Tópico: {r['topico']}")
        if r['feynman_resumo']:
            print(f"  Feynman: \"{r['feynman_resumo']}\"")
        if r['material_utilizado']:
            print(f"  Material: {r['material_utilizado']}")
        if r['proximo_passo']:
            print(f"  Próximo passo: {r['proximo_passo']}")
        print("-" * 85)
    conn.close()

def list_disciplinas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT codigo, nome, categoria, status, referencias_chave FROM disciplinas ORDER BY categoria, nome")
    rows = cursor.fetchall()
    print("=" * 80)
    print("DISCIPLINAS CADASTRADAS NO PLANO")
    print("=" * 80)
    for r in rows:
        print(f"• Código: {r['codigo']:<22} | {r['nome']} [{r['categoria']}]")
        if r['referencias_chave']:
            print(f"  Ref: {r['referencias_chave']}")
    print("=" * 80)
    conn.close()

def main():
    parser = argparse.ArgumentParser(description="Study Tracker CLI para MBA Data Science & IA")
    subparsers = parser.add_subparsers(dest="command")

    # init
    subparsers.add_parser("init", help="Inicializa banco de dados e sementes")

    # today
    today_p = subparsers.add_parser("today", help="Mostra metas e referências para hoje ou data específica")
    today_p.add_argument("--date", help="Data no formato AAAA-MM-DD", default=None)

    # log
    log_p = subparsers.add_parser("log", help="Registra uma sessão de estudo")
    log_p.add_argument("--disciplina", required=True, help="Código da disciplina (ex: data_wrangling, svm)")
    log_p.add_argument("--minutos", type=int, default=20, help="Duração em minutos (padrão: 20)")
    log_p.add_argument("--topico", required=True, help="O que foi estudado exatamente")
    log_p.add_argument("--feynman", help="Resumo no método Feynman (em palavras simples)")
    log_p.add_argument("--dificuldade", type=int, choices=[1, 2, 3, 4, 5], default=3, help="Dificuldade percebida (1 a 5)")
    log_p.add_argument("--material", help="Material consultado (ex: Wes McKinney Cap. 8)")
    log_p.add_argument("--proximo", help="Onde parou / próximo passo")

    # stats
    subparsers.add_parser("stats", help="Exibe estatísticas de evolução e progresso")

    # history
    hist_p = subparsers.add_parser("history", help="Exibe histórico de sessões")
    hist_p.add_argument("--limit", type=int, default=10, help="Quantidade de sessões para exibir")

    # list
    subparsers.add_parser("list-disciplinas", help="Lista códigos e nomes das disciplinas")

    args = parser.parse_args()

    if args.command == "init" or not os.path.exists(DB_PATH):
        init_db()
        if args.command == "init":
            return

    if args.command == "today":
        show_today(args.date)
    elif args.command == "log":
        log_session(args.disciplina, args.minutos, args.topico, args.feynman, args.dificuldade, args.material, args.proximo)
    elif args.command == "stats":
        show_stats()
    elif args.command == "history":
        show_history(args.limit)
    elif args.command == "list-disciplinas":
        list_disciplinas()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

