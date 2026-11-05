"""
===============================================================================
MÓDULO PRINCIPAL: SERVIDOR WEB FASTAPI PARA RAG CORPORATIVO
-------------------------------------------------------------------------------
Conceito: Este arquivo expõe a inteligência vetorial (ChromaDB) e o modelo de
linguagem (Gemini) através de uma API RESTful padronizada.

Ele atua como a camada de entrada para sistemas externos, portais corporativos,
frontends (React, Vue, Streamlit) ou integrações entre microsserviços.
===============================================================================
"""

# =============================================================================
# 1. IMPORTAÇÕES E DEPENDÊNCIAS
# =============================================================================
# FastAPI: framework web assíncrono e de alta performance.
# HTTPException: classe padrão para disparar erros com códigos de status HTTP (4xx, 5xx).
# UploadFile e File: utilitários para recebimento de payloads do tipo multipart/form-data.
from fastapi import FastAPI, HTTPException, UploadFile, File

# CORSMiddleware: mecanismo de segurança que controla quais domínios web externos
# podem fazer requisições para esta API a partir de um navegador.
from fastapi.middleware.cors import CORSMiddleware

# Schemas (Data Transfer Objects - DTOs): contratos de entrada e saída validados pelo Pydantic.
from api.schemas import (
    IngestaoRequest,
    RespostaIngestao,
    PerguntaRequest,
    RespostaRAG,
)

# Core RAG: funções de negócio desenvolvidas para manipulação de arquivos,
# segmentação (chunking), persistência vetorial e inferência ancorada.
from api.rag import ingerir_documento, consultar_rag, extrair_texto_arquivo

# Uvicorn: servidor ASGI responsável por executar e manter a aplicação FastAPI no ar.
import uvicorn

# =============================================================================
# 2. INICIALIZAÇÃO DA APLICAÇÃO E MIDDLEWARES
# =============================================================================
app = FastAPI(
    title="API de RAG Corporativo",
    description="Microsserviço simples de Ingestão e Consulta Semântica com Gemini e ChromaDB",
    version="1.0",
)

# Configuração de CORS (Cross-Origin Resource Sharing):
# Essencial para apresentações e desenvolvimento integrado. Permite que um frontend
# hospedado em outra porta/domínio (ex: http://localhost:3000 ou 8501) faça requisições.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Em produção, substitua pelo domínio exato do frontend
    allow_credentials=True,  # Permite envio de cookies e tokens de autenticação
    allow_methods=[
        "*"
    ],  # Libera todos os verbos HTTP (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Aceita quaisquer cabeçalhos HTTP customizados
)


# =============================================================================
# 3. ENDPOINT: HEALTH CHECK (MONITORAMENTO)
# =============================================================================
@app.get(
    "/health",
    tags=["Monitoramento"],
    summary="Verifica a integridade do serviço",
)
def health_check():
    """
    Objetivo: Liveness probe para Load Balancers, orquestradores (Kubernetes/Docker)
    ou testes de conectividade simples do cliente.
    """
    return {"status": "online"}


# =============================================================================
# 4. ENDPOINT: INGESTÃO VIA TEXTO PURO (JSON)
# =============================================================================
@app.post(
    "/ingest",
    response_model=RespostaIngestao,  # Valida a resposta no contrato oficial de ingestão
    status_code=201,  # 201 Created: padrão REST para recursos persistidos
    tags=["Ingestão"],
    summary="Indexa conteúdo textual direto no banco vetorial",
)
def rota_ingestao(dados: IngestaoRequest):
    """
    Recebe um payload JSON contendo 'documento_id' e 'conteudo'.
    Realiza o pipeline completo: chunking -> geração de embeddings -> upsert no ChromaDB.
    """
    try:
        # Executa o pipeline de ingestão isolado na camada de negócio (rag.py)
        total_chunks = ingerir_documento(dados.documento_id, dados.conteudo)

        # Se o texto for apenas espaços ou vazio, rejeita antes de salvar
        if total_chunks == 0:
            raise HTTPException(
                status_code=400,  # 400 Bad Request: erro imputável à entrada do cliente
                detail="Texto vazio ou inválido para processamento.",
            )

        return {
            "mensagem": "Documento processado com sucesso!",
            "documento_id": dados.documento_id,
            "chunks_salvos": total_chunks,
        }

    except HTTPException:
        # Repassa exceções HTTP intencionais sem mascará-las como erro 500
        raise
    except Exception as erro:
        # Captura falhas inesperadas de banco ou rede externa e retorna 500 Internal Server Error
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno durante a ingestão: {str(erro)}",
        )


# =============================================================================
# 5. ENDPOINT: INGESTÃO VIA UPLOAD DE ARQUIVOS (PDF / TXT)
# =============================================================================
@app.post(
    "/ingest/arquivo",
    response_model=RespostaIngestao,  # Padroniza a resposta no mesmo contrato do /ingest
    status_code=201,
    tags=["Ingestão"],
    summary="Extrai e indexa documentos físicos (.pdf ou .txt)",
)
def rota_ingestao_arquivo(arquivo: UploadFile = File(...)):
    """
    Recebe arquivos binários via multipart/form-data.
    """
    # 1. Sanitização e validação de segurança básica do nome do arquivo
    nome_arquivo = arquivo.filename or "documento_sem_nome"
    extensao = nome_arquivo.lower().split(".")[-1]

    # 2. Validação da extensão permitida (evita arquivos binários não suportados)
    if extensao not in ["pdf", "txt"]:
        raise HTTPException(
            status_code=400,
            detail=f"Formato '.{extensao}' não suportado. Envie apenas arquivos com extensão .PDF ou .TXT.",
        )

    try:
        # 3. Leitura dos bytes do stream do arquivo em memória
        conteudo_bytes = arquivo.file.read()

        # 4. Decodificação de bytes para texto puro
        texto = extrair_texto_arquivo(nome_arquivo, conteudo_bytes)

        # 5. Validação de conteúdo legível
        if not texto.strip():
            raise HTTPException(
                status_code=400,
                detail="Não foi possível extrair texto legível do arquivo ou o arquivo está vazio.",
            )

        # 6. Indexação vetorial: utiliza o nome do arquivo como documento_id
        total_chunks = ingerir_documento(nome_arquivo, texto)

        return {
            "mensagem": "Arquivo processado e indexado com sucesso!",
            "documento_id": nome_arquivo,  # Padronizado com o schema RespostaIngestao
            "chunks_salvos": total_chunks,
        }

    except HTTPException:
        # Repassa exceções HTTP de validação
        raise
    except Exception as erro:
        # Captura erros de parsing do PDF ou falhas de conexão vetorial
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar e indexar o arquivo: {str(erro)}",
        )
    finally:
        # Boa prática: garante o fechamento do descritor de arquivo no sistema operacional
        arquivo.file.close()


# =============================================================================
# 6. ENDPOINT: CONSULTA RAG E ANÁLISE DE FINOPS
# =============================================================================
@app.post(
    "/query",
    response_model=RespostaRAG,  # Garante que o retorno seja validado e tipado pelo Schema Pydantic
    tags=["Consulta"],
    summary="Realiza pergunta com contexto ancorado e telemetria completa",
)
def rota_consulta(dados: PerguntaRequest):
    """
    Recebe a pergunta do usuário e o parâmetro top_k.
    Executa o fluxo completo do RAG:
    1. Vetorização da pergunta.
    2. Busca semântica por proximidade de cosseno no ChromaDB.
    3. Construção de prompt ancorado (Grounding anti-alucinação).
    4. Inferência com Gemini.
    5. Coleta de métricas (latência, tokens e custos em dólares).
    """
    try:
        resultado = consultar_rag(dados.pergunta, dados.top_k)
        return resultado
    except Exception as erro:
        # Retorna erro 500 caso a quota da LLM seja excedida ou o banco esteja inacessível
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno durante a consulta RAG: {str(erro)}",
        )


# =============================================================================
# 7. BLOCO DE INICIALIZAÇÃO LOCAL (ENTRYPOINT)
# =============================================================================
# Permite iniciar o servidor diretamente pelo comando: python main.py
if __name__ == "__main__":
    # Host 127.0.0.1: escuta na máquina local
    # Port 8000: porta padrão para rodar o servidor uvicorn
    # Reload=True: recarrega a aplicação automaticamente a cada alteração salva no código
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
