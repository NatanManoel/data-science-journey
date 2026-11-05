# %% [1] SETUP: IMPORTS, CONSTANTES E FINOPS
# Instalação dos pacotes necessários para o funcionamento da aula
# pip install -r requirements.txt

"""
===============================================================================
CÉLULA 1: SETUP, VARIÁVEIS DE AMBIENTE E CONSTANTES FINOPS
-------------------------------------------------------------------------------
Conceito: Carregamos as bibliotecas essenciais e definimos os custos unitários
e configurações de rate limit para a arquitetura de FinOps.
===============================================================================
"""

import io
import os
import time
from typing import Any, Dict, List
import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types
import numpy as np
from pydantic import BaseModel
from pypdf import PdfReader, PdfWriter
import requests

load_dotenv()

# Modelos e constantes de FinOps
MODELO_LLM = "gemini-3.5-flash"
MODELO_EMBEDDING = "gemini-embedding-2"
PRECO_INPUT_POR_MILHAO = 0.075
PRECO_OUTPUT_POR_MILHAO = 0.30
PAUSA_ENTRE_LOTES_SEGUNDOS = 60.0

print("✅ Bibliotecas carregadas e constantes de FinOps configuradas!")


# %% [2] CONEXÃO COM CLIENTES (GEMINI E CHROMADB)
"""
===============================================================================
CÉLULA 2: INICIALIZAÇÃO DOS CLIENTES DE SERVIÇO
-------------------------------------------------------------------------------
Conceito: Validação de credenciais e conexão com o Google GenAI SDK e com o
banco vetorial persistente ChromaDB configurado com distância por cosseno.
===============================================================================
"""

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("⚠️ GEMINI_API_KEY não encontrada no arquivo .env!")

# Cliente Gemini
gemini_client = genai.Client(api_key=api_key)

# Banco Vetorial local ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
colecao = chroma_client.get_or_create_collection(
    name="base_conhecimento_aula", metadata={"hnsw:space": "cosine"}
)

print("✅ Gemini SDK autenticado com sucesso!")
print(f"✅ ChromaDB conectado! Coleção ativa: '{colecao.name}'")


# %% [3] EXTRAÇÃO DE ARQUIVOS: FUNÇÃO
"""
===============================================================================
CÉLULA 3: LÓGICA DE EXTRAÇÃO DE TEXTO BRUTO (TXT / PDF)
-------------------------------------------------------------------------------
Conceito: O pipeline RAG inicia com bytes recebidos de arquivos de upload.
Definimos a função que inspeciona o buffer e extrai strings puras.
===============================================================================
"""


def extrair_texto_arquivo(nome_arquivo: str, conteudo_bytes: bytes) -> str:
    extensao = nome_arquivo.lower().split(".")[-1]
    if extensao == "txt":
        return conteudo_bytes.decode("utf-8", errors="ignore")
    elif extensao == "pdf":
        leitor = PdfReader(io.BytesIO(conteudo_bytes))
        texto = ""
        for pagina in leitor.pages:
            t = pagina.extract_text()
            if t:
                texto += t + "\n"
        return texto
    return conteudo_bytes.decode("utf-8", errors="ignore")


print("✅ Função `extrair_texto_arquivo` compilada.")


# %% [4] EXTRAÇÃO DE ARQUIVOS: DEMO PRÁTICA
"""
===============================================================================
CÉLULA 4: DEMONSTRAÇÃO DE EXTRAÇÃO EM MEMÓRIA
-------------------------------------------------------------------------------
Conceito: Demonstração ao vivo da conversão de bytes para texto legível
utilizando um exemplo de TXT e sintetizando um PDF em buffer.
===============================================================================
"""

# 1. Simulação de upload de arquivo .TXT
bytes_txt = "Política de Viagens: O limite diário para alimentação é de R$ 90,00.".encode(
    "utf-8"
)
texto_txt = extrair_texto_arquivo("politica_alimentacao.txt", bytes_txt)
print(f'📄 [TXT Extraído]: "{texto_txt}"')

# 2. Simulação de PDF sintetizado em memória
writer = PdfWriter()
writer.add_blank_page(width=300, height=100)
buffer_pdf = io.BytesIO()
writer.write(buffer_pdf)
texto_pdf = extrair_texto_arquivo("anexo_vazio.pdf", buffer_pdf.getvalue())
print(
    f"📄 [PDF Processado]: {len(buffer_pdf.getvalue())} bytes lidos, {len(texto_pdf)} caracteres extraídos."
)


# %% [5] SEGMENTAÇÃO (CHUNKING): FUNÇÃO
"""
===============================================================================
CÉLULA 5: ESTRATÉGIA DE CHUNKING COM SLIDING WINDOW
-------------------------------------------------------------------------------
Conceito: A técnica de fatiamento de texto baseada em janelas móveis
(tamanho fixo + sobreposição de segurança/overlap).
===============================================================================
"""


def fazer_chunking(
    texto: str, chunk_size: int = 1000, overlap: int = 100
) -> List[str]:
    chunks = []
    inicio = 0
    while inicio < len(texto):
        fim = inicio + chunk_size
        chunks.append(texto[inicio:fim])
        inicio += chunk_size - overlap
    return chunks


print("✅ Função `fazer_chunking` compilada.")


# %% [6] SEGMENTAÇÃO (CHUNKING): COMPARAÇÃO PRÁTICA COM/SEM OVERLAP
"""
===============================================================================
CÉLULA 6: DEMO DO CHUNKING - IMPACTO DO OVERLAP NA PRESERVAÇÃO DE SENTIDO
-------------------------------------------------------------------------------
Conceito: Pausa para mostrar aos alunos como a ausência de sobreposição
pode cortar informações no meio de sentenças críticas de negócio.
===============================================================================
"""

texto_sensivel = (
    "A bonificação anual dos diretores será de 20% do salário. "
    "Já a bonificação dos estagiários será de R$ 350,00 fixos no final do ano fiscal."
)

print("✂️ TESTE A: Sem Overlap (overlap=0):")
chunks_sem_ov = fazer_chunking(texto_sensivel, chunk_size=65, overlap=0)
for i, c in enumerate(chunks_sem_ov):
    print(f'   Chunk {i}: "{c}"')

print("\n✂️ TESTE B: Com Overlap (overlap=25):")
chunks_com_ov = fazer_chunking(texto_sensivel, chunk_size=65, overlap=25)
for i, c in enumerate(chunks_com_ov):
    print(f'   Chunk {i}: "{c}"')

print(
    "\n💡 Repare como no Teste B o termo 'bonificação' e os valores não perdem o contexto na borda."
)


# %% [7] VETORIZAÇÃO: FUNÇÃO DE GERAÇÃO DE EMBEDDINGS COM RESILIÊNCIA
"""
===============================================================================
CÉLULA 7: FUNÇÃO DE GERAÇÃO DE EMBEDDINGS EM LOTE E TRATAMENTO DE 429
-------------------------------------------------------------------------------
Conceito: Como empacotar chamadas ao modelo de embedding lidando com lotes,
pausas estratégicas e retries automáticos com backoff para Rate Limits.
===============================================================================
"""


def gerar_embeddings(
    textos: List[str],
    batch_size: int = 60,
    pausa_segundos: float = PAUSA_ENTRE_LOTES_SEGUNDOS,
) -> List[List[float]]:
    """Gera embeddings em lotes com pausa controlada e retry automático para contornar Rate Limits."""
    todos_embeddings = []
    total_lotes = (len(textos) + batch_size - 1) // batch_size

    for indice, i in enumerate(range(0, len(textos), batch_size)):
        lote = textos[i : i + batch_size]
        conteudos = [types.Content(parts=[types.Part(text=t)]) for t in lote]

        max_tentativas = 5
        for tentativa in range(max_tentativas):
            try:
                resposta = gemini_client.models.embed_content(
                    model=MODELO_EMBEDDING, contents=conteudos
                )
                for e in resposta.embeddings:
                    todos_embeddings.append(list(e.values))
                break
            except Exception as erro:
                erro_str = str(erro)
                if "429" in erro_str or "RESOURCE_EXHAUSTED" in erro_str:
                    espera = 10 + (tentativa * 5)
                    print(
                        f"⚠️ Limite atingido (429). Aguardando {espera}s (Lote {indice+1}/{total_lotes})..."
                    )
                    time.sleep(espera)
                else:
                    raise erro
        else:
            raise RuntimeError(
                f"Falha ao gerar embeddings para o lote {indice+1}."
            )

        if i + batch_size < len(textos):
            time.sleep(pausa_segundos)

    return todos_embeddings


print("✅ Função `gerar_embeddings` pronta com suporte a retries.")


# %% [8] ÁLGEBRA LINEAR: SIMILARIDADE DE COSSENO NA PRÁTICA
"""
===============================================================================
CÉLULA 8: ESPAÇO VETORIAL E DISTÂNCIA SEMÂNTICA
-------------------------------------------------------------------------------
Conceito: Pausa didática para demonstrar a geometria dos embeddings.
Mostramos que textos com sentidos correlatos possuem cosseno próximo de 1.
===============================================================================
"""

frases_teste = [
    "Preciso de uma folga remunerada na sexta-feira.",
    "Como solicitar abono salarial por ausência?",
    "Receita caseira de torta de limão com merengue.",
]

print("⏳ Gerando embeddings das frases conceituais...")
vetores = gerar_embeddings(frases_teste, pausa_segundos=0)


def sim_cosseno(v1, v2):
    a, b = np.array(v1), np.array(v2)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


sim_alta = sim_cosseno(vetores[0], vetores[1])
sim_baixa = sim_cosseno(vetores[0], vetores[2])

print(f"📐 Dimensões do vetor: {len(vetores[0])} dimensões por texto.")
print(
    f"🔹 Similaridade ('Folga' vs 'Abono ausência'): {sim_alta:.4f} (Semântica correlata)"
)
print(
    f"🔹 Similaridade ('Folga' vs 'Torta de limão'): {sim_baixa:.4f} (Ortogonais / sem relação)"
)


# %% [9] INGESTÃO NO BANCO VETORIAL: FUNÇÃO
"""
===============================================================================
CÉLULA 9: PIPELINE DE INGESTÃO E MAPEAMENTO DE METADADOS
-------------------------------------------------------------------------------
Conceito: Construção da função `ingerir_documento`.
Une fatiamento, vetorização, validação 1-para-1 e persistência indexada.
===============================================================================
"""


def ingerir_documento(documento_id: str, conteudo: str) -> int:
    pedacos = fazer_chunking(conteudo, chunk_size=300, overlap=50)
    if not pedacos:
        return 0

    vetores = gerar_embeddings(pedacos, pausa_segundos=0)

    # Validação de integridade: correspondência 1 para 1
    if len(pedacos) != len(vetores):
        raise ValueError(
            f"Divergência: {len(pedacos)} chunks gerados, mas {len(vetores)} embeddings retornados."
        )

    ids = [f"{documento_id}_chunk_{i}" for i in range(len(pedacos))]
    metadados = [
        {"origem": documento_id, "chunk": i} for i in range(len(pedacos))
    ]

    colecao.upsert(
        ids=ids, documents=pedacos, embeddings=vetores, metadatas=metadados
    )
    return len(pedacos)


print("✅ Função `ingerir_documento` compilada.")


# %% [10] INGESTÃO NO BANCO VETORIAL: EXECUÇÃO E PERSISTÊNCIA
"""
===============================================================================
CÉLULA 10: ALIMENTANDO A BASE DE CONHECIMENTO
-------------------------------------------------------------------------------
Conceito: Ingestão de duas políticas corporativas reais (TI e RH) no ChromaDB.
Como os textos têm ~550 caracteres e definimos chunk_size=300 na Célula 9,
cada documento gerará 2 chunks no banco vetorial.
===============================================================================
"""

doc_ti = (
    "Política de Segurança de TI 2026: Todo colaborador deve trocar a senha de rede a cada 90 dias. "
    "A nova credencial precisa ter no mínimo 12 caracteres com letras, números e símbolos especiais. "
    "É expressamente proibido conectar pendrives não homologados em máquinas corporativas. "
    "Para qualquer acesso externo aos servidores internos, o uso de VPN corporativa com MFA é mandatório. "
    "Sessões inativas por mais de 30 minutos serão desconectadas automaticamente pelo firewall."
)

doc_rh = (
    "Política de Benefícios e Saúde Corporativa: A empresa subsidia 80% do plano de saúde executivo "
    "e 100% do plano odontológico básico para colaboradores e estagiários. "
    "Consultas com psicólogo pelo app parceiro são gratuitas até o limite de 4 sessões mensais. "
    "Caso o colaborador necessite de acompanhamento estendido, sessões extras têm coparticipação de R$ 45,00. "
    "O reembolso de despesas médicas complementares deve ser solicitado via portal interno até o dia 20."
)

print("⏳ Ingerindo documentos corporativos...")
chunks_ti = ingerir_documento("politica_ti", doc_ti)
chunks_rh = ingerir_documento("politica_rh", doc_rh)

print(f"📥 Documento de TI indexado: {chunks_ti} chunks.")
print(f"📥 Documento de RH indexado: {chunks_rh} chunks.")
print(f"📚 Total de itens agora persistidos no ChromaDB: {colecao.count()}")

# %% [11] MOTOR RAG E OBSERVABILIDADE: FUNÇÃO COMPLETA
"""
===============================================================================
CÉLULA 11: ARQUITETURA DE RETRIEVAL, GROUNDING E FINOPS
-------------------------------------------------------------------------------
Conceito: Definição da função central `consultar_rag`.
Executa busca vetorial, ancora o prompt (Anti-Hallucination) e calcula métricas
detalhadas de latência por estágio, consumo de tokens e custo em dólares.
===============================================================================
"""


def consultar_rag(pergunta: str, top_k: int = 3) -> Dict[str, Any]:
    inicio_total = time.perf_counter()

    # 1. Medição do tempo de embedding da pergunta
    inicio_embed = time.perf_counter()
    vetor_pergunta = gerar_embeddings([pergunta], pausa_segundos=0)[0]
    tempo_embed_ms = round((time.perf_counter() - inicio_embed) * 1000, 2)

    # 2. Medição da busca vetorial no ChromaDB
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

    similaridade_media = (
        round(sum(distancias) / len(distancias), 4) if distancias else 0.0
    )
    melhor_distancia = round(min(distancias), 4) if distancias else 0.0

    # 3. Prompt Ancorado (Grounding rígido)
    contexto = "\n\n".join(f"- {t}" for t in trechos)
    prompt = f"""Você é um assistente corporativo.
Responda à pergunta do usuário utilizando ESTRITAMENTE as informações do contexto abaixo.
Se a resposta não estiver no contexto, diga que a informação não consta nos documentos.

CONTEXTO:
{contexto}

PERGUNTA:
{pergunta}

RESPOSTA:"""

    # 4. Invocação da LLM
    inicio_llm = time.perf_counter()
    resposta_llm = gemini_client.models.generate_content(
        model=MODELO_LLM,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.1),
    )
    tempo_llm_ms = round((time.perf_counter() - inicio_llm) * 1000, 2)
    tempo_total_ms = round((time.perf_counter() - inicio_total) * 1000, 2)

    # 5. Extração de telemetria da LLM
    usage = getattr(resposta_llm, "usage_metadata", None)
    prompt_tokens = getattr(usage, "prompt_token_count", 0) if usage else 0
    resposta_tokens = (
        getattr(usage, "candidates_token_count", 0) if usage else 0
    )
    total_tokens = getattr(usage, "total_token_count", 0) if usage else 0
    cache_tokens = (
        getattr(usage, "cached_content_token_count", 0) if usage else 0
    )

    finish_reason = "UNKNOWN"
    if resposta_llm.candidates:
        candidato = resposta_llm.candidates[0]
        finish_reason = getattr(
            candidato.finish_reason, "name", str(candidato.finish_reason)
        )

    # 6. Cálculo de Custos (FinOps)
    custo_input = (prompt_tokens / 1_000_000) * PRECO_INPUT_POR_MILHAO
    custo_output = (resposta_tokens / 1_000_000) * PRECO_OUTPUT_POR_MILHAO
    custo_total_usd = round(custo_input + custo_output, 6)

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


print("✅ Motor `consultar_rag` pronto com observabilidade completa.")


# %% [12] CONSULTA RAG: CENÁRIO 1 (RESPOSTA EM BASE + TELEMETRIA)
"""
===============================================================================
CÉLULA 12: EXECUÇÃO DE PERGUNTA VÁLIDA E ANÁLISE DE FINOPS
-------------------------------------------------------------------------------
Conceito: Pausa para inspecionar a resposta extraída dos documentos ingeridos
e analisar os custos e tempos de inferência retornados.
===============================================================================
"""

print("🔍 EXECUTANDO CENÁRIO 1: PERGUNTA COM RESPOSTA NA BASE...")
resultado_valido = consultar_rag(
    "Quantas sessões de psicólogo a empresa cobre?"
)

print(f"\n🤖 Resposta da LLM:\n   {resultado_valido['resposta']}\n")
print("⏱️ Latências:")
print(
    f"   • Embedding: {resultado_valido['metricas']['latencia_ms']['geracao_embedding']} ms"
)
print(
    f"   • ChromaDB:  {resultado_valido['metricas']['latencia_ms']['busca_vetorial']} ms"
)
print(
    f"   • Gemini:    {resultado_valido['metricas']['latencia_ms']['inferencia_llm']} ms"
)
print(
    f"   • TOTAL:     {resultado_valido['metricas']['latencia_ms']['tempo_total']} ms\n"
)
print("💰 FinOps:")
print(
    f"   • Tokens Prompt:   {resultado_valido['metricas']['tokens']['prompt_tokens']}"
)
print(
    f"   • Tokens Resposta: {resultado_valido['metricas']['tokens']['resposta_tokens']}"
)
print(
    f"   • Custo Estimado:  ${resultado_valido['metricas']['custo_estimado_usd']} USD"
)


# %% [13] CONSULTA RAG: CENÁRIO 2 (TESTE DE ANTI-ALUCINAÇÃO)
"""
===============================================================================
CÉLULA 13: TESTE DE RESISTÊNCIA A ALUCINAÇÃO
-------------------------------------------------------------------------------
Conceito: Pausa para demonstrar que o prompt ancorado impede a LLM de inventar
respostas que não existam explicitamente na base indexada.
===============================================================================
"""

print("🔍 EXECUTANDO CENÁRIO 2: PERGUNTA FORA DA BASE...")
resultado_ausente = consultar_rag(
    "A empresa financia bolsas de pós-graduação?"
)

print(f"\n🤖 Resposta da LLM:\n   {resultado_ausente['resposta']}")
print(
    f"\n💡 Repare que o modelo admitiu a ausência de dados em vez de alucinar benefícios inexistentes."
)


# %% [14] SCHEMAS E VALIDAÇÃO DE DADOS (PYDANTIC)
"""
===============================================================================
CÉLULA 14: CONTRATOS DE DADOS PARA A API COM PYDANTIC
-------------------------------------------------------------------------------
Conceito: Definição dos Schemas de entrada e saída (DTOs) com tipagem básica.
Inclui RespostaIngestao para padronizar as respostas das rotas de ingestão.
===============================================================================
"""


class IngestaoRequest(BaseModel):
    documento_id: str
    conteudo: str


class RespostaIngestao(BaseModel):
    mensagem: str
    documento_id: str
    chunks_salvos: int


class PerguntaRequest(BaseModel):
    pergunta: str
    top_k: int = 3


class RespostaRAG(BaseModel):
    pergunta: str
    resposta: str
    fontes_consultadas: List[str]
    metricas: Dict[str, Any]


print("✅ Schemas Pydantic compilados e sincronizados com a API.")


# %% [15] VALIDAÇÃO DOS SCHEMAS NA PRÁTICA
"""
===============================================================================
CÉLULA 15: DEMO DE SERIALIZAÇÃO E VALIDAÇÃO DOS SCHEMAS
-------------------------------------------------------------------------------
Conceito: Demonstra como o Pydantic valida os dados no backend antes de
enviar a resposta para o cliente.
===============================================================================
"""

# 1. Validando o payload localmente
dados_entrada = PerguntaRequest(
    pergunta="Qual é a regra para troca de senha?", top_k=2
)
print(
    f"✅ Entrada validada via Pydantic: '{dados_entrada.pergunta}' (top_k={dados_entrada.top_k})"
)

# 2. Validando a saída com o schema RespostaRAG
saida_bruta = consultar_rag(dados_entrada.pergunta, dados_entrada.top_k)
objeto_resposta = RespostaRAG(**saida_bruta)

print(f"✅ Saída aprovada pelo schema RespostaRAG:")
print(f"   Resposta: {objeto_resposta.resposta}")
print(f"   Fontes validadas: {len(objeto_resposta.fontes_consultadas)}")


# %% [16] CLIENTE HTTP: HEALTH CHECK DA API FASTAPI
"""
===============================================================================
CÉLULA 16: TESTE DE CONECTIVIDADE COM O SERVIDOR FASTAPI
-------------------------------------------------------------------------------
Conceito: Testamos a disponibilidade do microsserviço no endpoint `/health`.
(Certifique-se de que `python main.py` esteja rodando em outro terminal).
===============================================================================
"""

URL_API = "http://127.0.0.1:8000"

try:
    health = requests.get(f"{URL_API}/health", timeout=3).json()
    print(f"🟢 Servidor FastAPI online! Retorno /health: {health}")
except requests.exceptions.ConnectionError:
    print(
        "⚠️ O servidor FastAPI não está respondendo em http://127.0.0.1:8000"
    )
    print(
        "👉 Abra outro terminal e execute 'python main.py' para testar as próximas células."
    )


# %% [17] CLIENTE HTTP: INGESTÃO E CONSULTA DIRETA (SEM USAR PYDANTIC)
"""
===============================================================================
CÉLULA 17: CHAMADAS HTTP REAIS USANDO APENAS DICIONÁRIOS (JSON BRUTO)
-------------------------------------------------------------------------------
Conceito: Aqui simulamos um cliente real (Postman, frontend JavaScript ou mobile)
enviando payloads normais em formato dict/JSON, SEM usar classes Pydantic.
===============================================================================
"""

try:
    # 1. Ingestão de texto puro via dicionário comum (sem modelos Pydantic)
    payload_ingestao = {
        "documento_id": "politica_homeoffice",
        "conteudo": "Os colaboradores de tecnologia podem fazer home office às segundas e sextas-feiras.",
    }

    res_ingest = requests.post(
        f"{URL_API}/ingest", json=payload_ingestao, timeout=10
    )
    print(f"📥 Retorno /ingest (JSON Puro):\n   {res_ingest.json()}\n")

    # 2. Consulta via dicionário comum (sem modelos Pydantic)
    payload_consulta = {
        "pergunta": "Quais dias posso fazer home office?",
        "top_k": 2,
    }

    res_query = requests.post(
        f"{URL_API}/query", json=payload_consulta, timeout=15
    )
    dados = res_query.json()

    print("💬 Resposta vinda do Endpoint HTTP (/query):")
    print(f" • Pergunta: {dados['pergunta']}")
    print(f" • Resposta: {dados['resposta']}")
    print(
        f" • Latência Total: {dados['metricas']['latencia_ms']['tempo_total']} ms"
    )
    print(f" • Custo Estimado: ${dados['metricas']['custo_estimado_usd']} USD")

except requests.exceptions.ConnectionError:
    print("💡 Requisição não enviada pois o servidor FastAPI está desligado.")


# %% [18] CLIENTE HTTP: INGESTÃO VIA UPLOAD DE ARQUIVO (/INGEST/ARQUIVO)
"""
===============================================================================
CÉLULA 18: TESTE DE UPLOAD MULTIPART/FORM-DATA (SEM USAR PYDANTIC)
-------------------------------------------------------------------------------
Conceito: Testa o endpoint `/ingest/arquivo` criado no main.py, enviando um arquivo
sintetizado em memória diretamente através do parâmetro `files` da biblioteca requests.
===============================================================================
"""

try:
    # Simula o upload de um arquivo real .txt em buffer de memória
    conteudo_arquivo_teste = (
        "Política de Horas Extras 2026: Horas extras devem ser pré-aprovadas pelo gestor. "
        "O limite máximo permitido por lei é de 2 horas suplementares por jornada diária."
    )

    arquivos = {
        "arquivo": (
            "politica_horas_extras.txt",
            io.BytesIO(conteudo_arquivo_teste.encode("utf-8")),
            "text/plain",
        )
    }

    res_arquivo = requests.post(
        f"{URL_API}/ingest/arquivo", files=arquivos, timeout=15
    )

    print(
        f"📥 Retorno /ingest/arquivo (Upload Multipart):\n   {res_arquivo.json()}\n"
    )

    # Realiza pergunta sobre o arquivo recém-enviado
    payload_teste_arquivo = {
        "pergunta": "Qual o limite de horas extras por dia?",
        "top_k": 2,
    }

    res_pergunta = requests.post(
        f"{URL_API}/query", json=payload_teste_arquivo, timeout=15
    )
    dados_arquivo = res_pergunta.json()

    print("💬 Validação da busca no arquivo enviado:")
    print(f" • Pergunta: {dados_arquivo['pergunta']}")
    print(f" • Resposta: {dados_arquivo['resposta']}")

except requests.exceptions.ConnectionError:
    print("💡 Requisição não enviada pois o servidor FastAPI está desligado.")
