"""
===============================================================================
MÓDULO CORE: MOTOR RAG, BANCO VETORIAL E OBSERVABILIDADE (rag.py)
-------------------------------------------------------------------------------
Conceito: Este arquivo é o coração da aplicação de IA. Ele encapsula:
1. ETL & Parsing: Extração e limpeza de arquivos físicos (.pdf e .txt).
2. Segmentação: Divisão em pedaços (chunking) com janela deslizante (overlap).
3. Vetorização: Geração de embeddings com gestão de Rate Limits e retries.
4. Persistência: Indexação e upsert com metadados no ChromaDB.
5. Retrieval & Grounding: Busca vetorial por cosseno e ancoragem de contexto.
6. Observabilidade & FinOps: Telemetria de latência, tokens e custo em dólares.
===============================================================================
"""

# =============================================================================
# 1. IMPORTAÇÕES E DEPENDÊNCIAS
# =============================================================================
import io
import os
import time
from typing import Any, Dict, List

# ChromaDB: Banco de dados vetorial embarcado para indexação e busca semântica
import chromadb
from dotenv import load_dotenv

# Google GenAI SDK: SDK oficial para modelos Gemini (geração e embeddings)
from google import genai
from google.genai import types

# PyPDF: Biblioteca para parsing e extração de texto de streams binários de PDF
from pypdf import PdfReader

# Carrega as variáveis de ambiente declaradas no arquivo .env local
load_dotenv()


# =============================================================================
# 2. CONSTANTES DE MODELOS E ENGENHARIA DE FINOPS
# =============================================================================
# Identificadores oficiais dos modelos utilizados no pipeline
MODELO_LLM = "gemini-3.5-flash"
MODELO_EMBEDDING = "gemini-embedding-2"

# Precificação (USD) por milhão de tokens para monitoramento contínuo de custos
PRECO_INPUT_POR_MILHAO = 0.075  # Custo do prompt enviado à LLM
PRECO_OUTPUT_POR_MILHAO = 0.30  # Custo da resposta gerada pela LLM

# Intervalo entre lotes de embedding para respeitar as cotas (RPM) da API gratuita
PAUSA_ENTRE_LOTES_SEGUNDOS = 60.0


# =============================================================================
# 3. CLIENTES E BANCO VETORIAL (CHROMADB)
# =============================================================================
# Inicializa o cliente do Gemini autenticado com a chave de API
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Inicializa o cliente persistente do ChromaDB (salva os vetores no disco local)
chroma_client = chromadb.PersistentClient(path="../chroma_db")

# Cria ou recupera a coleção vetorial.
# hnsw:space = "cosine" define a métrica matemática de similaridade (distância por cosseno).
colecao = chroma_client.get_or_create_collection(
    name="base_conhecimento", metadata={"hnsw:space": "cosine"}
)


# =============================================================================
# 4. EXTRAÇÃO DE ARQUIVOS (ETL)
# =============================================================================
def extrair_texto_arquivo(nome_arquivo: str, conteudo_bytes: bytes) -> str:
    """
    Recebe os bytes brutos de um arquivo e o seu nome.
    Identifica a extensão e decodifica para texto puro (string).
    """
    extensao = nome_arquivo.lower().split(".")[-1]

    # Tratamento para arquivos de texto simples (.txt)
    if extensao == "txt":
        return conteudo_bytes.decode("utf-8", errors="ignore")

    # Tratamento para arquivos PDF (.pdf) via stream em memória
    elif extensao == "pdf":
        leitor = PdfReader(io.BytesIO(conteudo_bytes))
        texto = ""
        for pagina in leitor.pages:
            t = pagina.extract_text()
            if t:
                texto += t + "\n"
        return texto

    # Fallback genérico para formatos baseados em texto
    return conteudo_bytes.decode("utf-8", errors="ignore")


# =============================================================================
# 5. SEGMENTAÇÃO DE DOCUMENTOS (CHUNKING)
# =============================================================================
def fazer_chunking(
    texto: str, chunk_size: int = 1000, overlap: int = 100
) -> List[str]:
    """
    Divide um texto longo em blocos menores utilizando janela deslizante.
    - chunk_size: Quantidade máxima de caracteres por bloco.
    - overlap: Quantidade de caracteres repetidos na borda do bloco anterior,
      garantindo que sentenças críticas não percam o sentido semântico.
    """
    chunks = []
    inicio = 0
    while inicio < len(texto):
        fim = inicio + chunk_size
        chunks.append(texto[inicio:fim])
        # Avança a janela subtraindo o overlap de segurança
        inicio += chunk_size - overlap
    return chunks


# =============================================================================
# 6. GERAÇÃO DE EMBEDDINGS COM RESILIÊNCIA E RATE LIMITING
# =============================================================================
def gerar_embeddings(
    textos: List[str],
    batch_size: int = 60,
    pausa_segundos: float = PAUSA_ENTRE_LOTES_SEGUNDOS,
) -> List[List[float]]:
    """
    Converte listas de textos em listas de vetores de ponto flutuante.
    Inclui:
    - Processamento em lotes (batching) para respeitar o limite de payload.
    - Retry com Exponential Backoff contra erros 429 (Too Many Requests).
    - Pausa deliberada entre requisições para controle de cota (RPM).
    """
    todos_embeddings = []
    total_lotes = (len(textos) + batch_size - 1) // batch_size

    for indice, i in enumerate(range(0, len(textos), batch_size)):
        lote = textos[i : i + batch_size]
        conteudos = [types.Content(parts=[types.Part(text=t)]) for t in lote]

        # Estratégia de retries para resiliência de rede
        max_tentativas = 5
        for tentativa in range(max_tentativas):
            try:
                resposta = gemini_client.models.embed_content(
                    model=MODELO_EMBEDDING, contents=conteudos
                )
                for e in resposta.embeddings:
                    todos_embeddings.append(list(e.values))
                break  # Lote processado com sucesso, sai do loop de tentativas
            except Exception as erro:
                erro_str = str(erro)
                # Trata exaustão de cota da API (HTTP 429 / RESOURCE_EXHAUSTED)
                if "429" in erro_str or "RESOURCE_EXHAUSTED" in erro_str:
                    espera = 10 + (tentativa * 5)
                    print(
                        f"⚠️ Limite atingido (429). Aguardando {espera}s para tentar novamente (Lote {indice+1}/{total_lotes})..."
                    )
                    time.sleep(espera)
                else:
                    raise erro
        else:
            raise RuntimeError(
                f"Falha ao gerar embeddings para o lote {indice+1} após {max_tentativas} tentativas."
            )

        # Pausa programada para não estourar a cota por minuto (apenas se houver mais lotes)
        if i + batch_size < len(textos):
            time.sleep(pausa_segundos)

    return todos_embeddings


# =============================================================================
# 7. INGESTÃO E PERSISTÊNCIA NO BANCO VETORIAL
# =============================================================================
def ingerir_documento(documento_id: str, conteudo: str) -> int:
    """
    Pipeline de Ingestão:
    1. Fatia o documento em pedaços (chunks).
    2. Converte os pedaços em vetores semânticos.
    3. Valida a integridade 1 para 1 (cada pedaço precisa ter exatamente um vetor).
    4. Realiza o upsert (criação ou atualização) no ChromaDB com metadados de rastreabilidade.
    """
    pedacos = fazer_chunking(conteudo)
    if not pedacos:
        return 0

    vetores = gerar_embeddings(pedacos)

    # Validação de integridade transacional
    if len(pedacos) != len(vetores):
        raise ValueError(
            f"Divergência: {len(pedacos)} chunks gerados, mas {len(vetores)} embeddings retornados."
        )

    # Gera IDs exclusivos por chunk para permitir reescrita/atualizações pontuais
    ids = [f"{documento_id}_chunk_{i}" for i in range(len(pedacos))]
    metadados = [
        {"origem": documento_id, "chunk": i} for i in range(len(pedacos))
    ]

    # Gravação no banco vetorial
    colecao.upsert(
        ids=ids, documents=pedacos, embeddings=vetores, metadatas=metadados
    )
    return len(pedacos)


# =============================================================================
# 8. MOTOR DE BUSCA RAG, GROUNDING E TELEMETRIA (FINOPS)
# =============================================================================
def consultar_rag(pergunta: str, top_k: int = 3) -> Dict[str, Any]:
    """
    Pipeline de Retrieval-Augmented Generation (RAG):
    1. Vetoriza a pergunta feita pelo usuário.
    2. Busca os top_k trechos mais próximos semanticamente no ChromaDB.
    3. Constrói um prompt ancorado (Grounding) instruindo a LLM a não alucinar.
    4. Executa a inferência com o modelo Gemini.
    5. Extrai metadados completos de latência (ms), tokens e custo (USD).
    """
    inicio_total = time.perf_counter()

    # --- ETAPA 1: Embedding da Pergunta ---
    inicio_embed = time.perf_counter()
    vetor_pergunta = gerar_embeddings([pergunta], pausa_segundos=0)[0]
    tempo_embed_ms = round((time.perf_counter() - inicio_embed) * 1000, 2)

    # --- ETAPA 2: Busca Vetorial por Cosseno ---
    inicio_busca = time.perf_counter()
    resultados = colecao.query(
        query_embeddings=[vetor_pergunta], n_results=top_k
    )
    tempo_busca_ms = round((time.perf_counter() - inicio_busca) * 1000, 2)

    trechos = resultados["documents"][0] if resultados["documents"] else []
    distancias = (
        resultados["distances"][0]
        if resultados.get("distances") and resultados["distances"]
        else []
    )

    # Tratamento caso a base de conhecimento esteja totalmente vazia
    if not trechos:
        tempo_total_ms = round((time.perf_counter() - inicio_total) * 1000, 2)
        return {
            "pergunta": pergunta,
            "resposta": "Nenhuma informação encontrada na base de conhecimento.",
            "fontes_consultadas": [],
            "metricas": {
                "latencia_ms": {
                    "embedding": tempo_embed_ms,
                    "busca_vetorial": tempo_busca_ms,
                    "llm": 0.0,
                    "total": tempo_total_ms,
                },
                "tokens": {"prompt": 0, "resposta": 0, "total": 0, "cache": 0},
                "similaridade": {"chunks_retornados": 0},
                "custo_estimado_usd": 0.0,
            },
        }

    # Métricas de proximidade semântica (quanto mais próximo de 0 na distância por cosseno, mais similar)
    similaridade_media = (
        round(sum(distancias) / len(distancias), 4) if distancias else 0.0
    )
    melhor_distancia = round(min(distancias), 4) if distancias else 0.0

    # --- ETAPA 3: Grounding (Prompt Ancorado Anti-Alucinação) ---
    contexto = "\n\n".join(f"- {t}" for t in trechos)
    prompt = f"""Você é um assistente corporativo.
      Responda à pergunta do usuário utilizando ESTRITAMENTE as informações do contexto abaixo.
      Se a resposta não estiver no contexto, diga que a informação não consta nos documentos.
      
      CONTEXTO:
      {contexto}
      
      PERGUNTA:
      {pergunta}
      
      RESPOSTA:"""

    # --- ETAPA 4: Inferência com Gemini ---
    inicio_llm = time.perf_counter()
    resposta_llm = gemini_client.models.generate_content(
        model=MODELO_LLM,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1
        ),  # Baixa temperatura = maior aderência factual
    )
    tempo_llm_ms = round((time.perf_counter() - inicio_llm) * 1000, 2)
    tempo_total_ms = round((time.perf_counter() - inicio_total) * 1000, 2)

    # --- ETAPA 5: Extração de Telemetria de Tokens ---
    usage = getattr(resposta_llm, "usage_metadata", None)
    prompt_tokens = getattr(usage, "prompt_token_count", 0) if usage else 0
    resposta_tokens = (
        getattr(usage, "candidates_token_count", 0) if usage else 0
    )
    total_tokens = getattr(usage, "total_token_count", 0) if usage else 0
    cache_tokens = (
        getattr(usage, "cached_content_token_count", 0) if usage else 0
    )

    # Motivo de encerramento da geração (ex: STOP, SAFETY, MAX_TOKENS)
    finish_reason = "UNKNOWN"
    if resposta_llm.candidates:
        candidato = resposta_llm.candidates[0]
        finish_reason = getattr(
            candidato.finish_reason, "name", str(candidato.finish_reason)
        )

    # --- ETAPA 6: Cálculo de FinOps ---
    custo_input = (prompt_tokens / 1_000_000) * PRECO_INPUT_POR_MILHAO
    custo_output = (resposta_tokens / 1_000_000) * PRECO_OUTPUT_POR_MILHAO
    custo_total_usd = round(custo_input + custo_output, 6)

    # Compilação analítica completa da requisição
    metricas_completas = {
        "latencia_ms": {
            "geracao_embedding": tempo_embed_ms,
            "busca_vetorial": tempo_busca_ms,
            "inferencia_llm": tempo_llm_ms,
            "tempo_total": tempo_total_ms,
        },
        "tokens": {
            "prompt_tokens": prompt_tokens,
            "resposta_tokens": resposta_tokens,
            "total_tokens": total_tokens,
            "cached_tokens": cache_tokens,
        },
        "qualidade_retrieval": {
            "chunks_recuperados": len(trechos),
            "melhor_distancia_cosseno": melhor_distancia,
            "distancia_media_cosseno": similaridade_media,
            "caracteres_contexto": len(contexto),
        },
        "governanca_modelo": {
            "modelo_utilizado": MODELO_LLM,
            "finish_reason": finish_reason,
            "caracteres_resposta": len(resposta_llm.text),
        },
        "custo_estimado_usd": custo_total_usd,
    }

    return {
        "pergunta": pergunta,
        "resposta": resposta_llm.text,
        "fontes_consultadas": trechos,
        "metricas": metricas_completas,
    }
