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

    # Seed disciplinas se tabela vazia
    cursor.execute("SELECT COUNT(*) FROM disciplinas")
    if cursor.fetchone()[0] == 0:
        disciplinas_iniciais = [
            ("data_wrangling", "Data Wrangling", "Engenharia & Dados", "Em Andamento", 20.0, 
             "Livro: Wes McKinney - Python for Data Analysis (Cap. 7 e 8) | Docs: pandas.pydata.org"),
            ("estatistica", "Fundamentos de Estatística", "Fundamentos", "Em Andamento", 25.0, 
             "Livros: Fávero & Belfiore (Manual de Análise de Dados p.78-487) | Bruce & Bruce (Estatística Prática) | Canal: StatQuest"),
            ("svm", "Support Vector Machines (SVM)", "Machine Learning", "Em Andamento", 15.0, 
             "Livro: Aurélien Géron (Hands-On ML Cap. 5) | StatQuest: Support Vector Machines"),
            ("arvores_ensemble", "Árvores de Decisão & Ensemble Models", "Machine Learning", "Pendente", 20.0, 
             "Livro: Aurélien Géron (Cap. 6 e 7) | StatQuest: Random Forests, AdaBoost, XGBoost"),
            ("bi_dataviz", "BI e Data Visualization", "Analytics & Negócios", "Em Andamento", 15.0, 
             "Livro: Cole Knaflic (Storytelling com Dados) | Guia: Financial Times Visual Vocabulary"),
            ("social_network", "Social Network Analysis (SNA)", "Analytics & Negócios", "Pendente", 10.0, 
             "Livro: Albert-László Barabási (Network Science) | Docs: NetworkX Tutorial"),
            ("crawlers", "Coleta de Dados: Crawlers & Scraping", "Engenharia & Dados", "Pendente", 12.0, 
             "Docs: Beautiful Soup 4 & Scrapy Official Documentation"),
            ("text_mining_nlp", "Text Mining, Sentiment Analysis & NLP", "IA & NLP", "Pendente", 15.0, 
             "Curso: Hugging Face NLP Course | NLTK Book"),
            ("apis_llms", "Desenvolvimento de APIs & Integração de LLMs", "Engenharia & IA", "Em Andamento", 20.0, 
             "Docs: FastAPI (fastapi.tiangolo.com) | Cursos: DeepLearning.AI (LangChain, Vector DBs, Building Systems with LLMs)"),
            ("pesquisa_operacional", "Pesquisa Operacional & Otimização", "Fundamentos", "Pendente", 15.0, 
             "Docs: PuLP Documentation (coin-or.github.io/pulp) | MIT OCW Linear Programming"),
            ("deep_learning", "Deep Learning e IA", "Machine Learning", "Pendente", 25.0, 
             "Série: 3Blue1Brown Neural Networks | Livro: Aurélien Géron Cap. 10 | Fast.ai"),
            ("estatistica_espacial", "Análise Estatística Espacial", "Fundamentos", "Pendente", 10.0, 
             "Livro: Geographic Data Science with Python (Rey, Arribas-Bel, Wolf) | GeoPandas & PySAL"),
            ("engenharia_dados", "Engenharia de Dados", "Engenharia & Dados", "Pendente", 30.0, 
             "Livro: Martin Kleppmann (Designing Data-Intensive Applications) | Bootcamp: Data Engineering Zoomcamp | LeetCode 50 SQL"),
            ("metodologias_ageis", "Metodologias Ágeis", "Gestão & Negócios", "Pendente", 8.0, 
             "Scrum Guide & Práticas Ágeis de Gestão de Projetos")
        ]
        cursor.executemany("""
            INSERT INTO disciplinas (codigo, nome, categoria, status, horas_meta, referencias_chave)
            VALUES (?, ?, ?, ?, ?, ?)
        """, disciplinas_iniciais)

    # Seed cronograma inicial (Fase 1 - 2 semanas imediatas)
    cursor.execute("SELECT COUNT(*) FROM cronograma")
    if cursor.fetchone()[0] == 0:
        cronograma_inicial = [
            ("Fase 1", "2026-11-04", "Qua", "data_wrangling", 
             "Retomar Data Wrangling II do 35:40 / L262 (~15-20 min)", 
             "+energia: Avançar até o próximo bloco de código", 
             "Wes McKinney - Python for Data Analysis Cap. 8 (Joins & Concat)"),
            ("Fase 1", "2026-11-05", "Qui", "data_wrangling", 
             "Continuar DW II: rodar e testar trecho de joins/limpeza", 
             "+energia: Resolver exercício de limpeza da aula", 
             "Wes McKinney Cap. 7 (Data Cleaning & Preparation)"),
            ("Fase 1", "2026-11-06", "Sex", "estatistica", 
             "Lista estatística Excel: 3 a 5 exercícios", 
             "+energia: +5 exercícios OU 1 flashcard (média vs mediana / variância)", 
             "Manual de Análise de Dados (Fávero & Belfiore) p.78-150 | StatQuest P-Value"),
            ("Fase 1", "2026-11-07", "Sáb", "svm", 
             "OPCIONAL: 20 min SVM Admissão (scaling + fit)", 
             "+energia: Completar pipeline Admissão", 
             "Aurélien Géron Hands-On ML Cap. 5 | StatQuest SVM"),
            ("Fase 1", "2026-11-08", "Dom", "gestao_estudos", 
             "15 min: Revisão de checks e planejamento da semana", 
             "Descanso e consolidação mental", 
             "Revisão rápida de metas"),
            ("Fase 1", "2026-11-09", "Seg", "data_wrangling", 
             "Fechar o que falta de DW II (Meta: aula II ok)", 
             "+energia: DW III abrir imports + load de dados", 
             "Documentação do pandas (`pd.DataFrame.merge`)"),
            ("Fase 1", "2026-11-10", "Ter", "bi_dataviz", 
             "Aula ao vivo BI I + recriar 1 gráfico no mesmo dia", 
             "+energia: 5 linhas de notas conceituais (dimensão / fato / KPI)", 
             "Storytelling com Dados (Cole Knaflic Cap. 1-2) | FT Visual Vocabulary"),
            ("Fase 1", "2026-11-11", "Qua", "bi_dataviz", 
             "Refazer 1 visual da aula BI I sem gabarito", 
             "+energia: DW III - 1 seção do script", 
             "FT Visual Vocabulary (escolha do gráfico ideal)"),
            ("Fase 1", "2026-11-12", "Qui", "data_wrangling", 
             "DW III (CVM): Load de dados + limpeza inicial", 
             "+energia: Merge e análise descritiva", 
             "Wes McKinney Cap. 10 (Data Aggregation & Group Operations)"),
            ("Fase 1", "2026-11-13", "Sex", "svm", 
             "SVM Churn: StandardScaler + SVC fit (script cego curto)", 
             "+energia: GridSearch ou Confusion Matrix / ROC-AUC", 
             "Aurélien Géron Cap. 5 | StatQuest ROC & AUC"),
            ("Fase 1", "2026-11-14", "Sáb", "apis_llms", 
             "OPCIONAL semente APIs (20 min): script.py células [1] e [2] (FinOps + Gemini/Chroma)", 
             "+energia: Células [3]-[4] extração de PDF", 
             "FastAPI Docs tutorial | DeepLearning.AI Building Systems with LLMs"),
            ("Fase 1", "2026-11-15", "Dom", "gestao_estudos", 
             "15 min planejamento e descanso", 
             "Descanso mental", 
             "Revisão de metas"),
            ("Fase 1", "2026-11-16", "Seg", "data_wrangling", 
             "Fechar DW III OU resumo Feynman de 10 linhas da aula de BI I", 
             "+energia: DW IV (Copa) apenas load e inspeção", 
             "Método Feynman de síntese"),
            ("Fase 1", "2026-11-17", "Ter", "bi_dataviz", 
             "Aula ao vivo BI II + 1 prática no mesmo dia", 
             "+energia: Comparar evolução visual em relação a BI I", 
             "Storytelling com Dados (Cole Knaflic Cap. 3-4: Eliminar Ruído)")
        ]
        cursor.executemany("""
            INSERT INTO cronograma (fase, data_prevista, dia_semana, disciplina_codigo, meta_dia, meta_energia, referencia_sugerida)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, cronograma_inicial)

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
