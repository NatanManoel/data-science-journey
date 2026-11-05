"""
===============================================================================
MÓDULO DE CONTRATOS DE DADOS: SCHEMAS E DTOs (schemas.py)
-------------------------------------------------------------------------------
Conceito: Define os contratos de entrada e saída (Data Transfer Objects)
utilizando apenas tipagem básica do Python com Pydantic.
Garante a validação automática dos tipos antes de processar qualquer dado.
===============================================================================
"""

from typing import Any, Dict, List
from pydantic import BaseModel


# =============================================================================
# 1. ENTRADA: INGESTÃO DE DOCUMENTO (/ingest)
# =============================================================================
class IngestaoRequest(BaseModel):
    """Payload JSON enviado para indexar um novo documento."""

    documento_id: str  # Nome ou identificador do documento (ex: 'politica_rh')
    conteudo: str  # Texto completo que será fatiado e salvo


# =============================================================================
# 2. SAÍDA: CONFIRMAÇÃO DE INGESTÃO (/ingest e /ingest/arquivo)
# =============================================================================
class RespostaIngestao(BaseModel):
    """Estrutura da resposta retornada após a indexação no ChromaDB."""

    mensagem: (
        str  # Mensagem de status (ex: 'Documento processado com sucesso!')
    )
    documento_id: str  # ID ou nome do arquivo que foi persistido
    chunks_salvos: int  # Quantidade de pedaços fatiados e gravados no banco


# =============================================================================
# 3. ENTRADA: CONSULTA RAG (/query)
# =============================================================================
class PerguntaRequest(BaseModel):
    """Payload JSON com a pergunta do usuário e configuração de busca."""

    pergunta: str  # Pergunta em linguagem natural
    top_k: int = 3  # Quantidade de chunks relevantes a recuperar (padrão: 3)


# =============================================================================
# 4. SAÍDA: RESPOSTA RAG COM TELEMETRIA (/query)
# =============================================================================
class RespostaRAG(BaseModel):
    """Estrutura da resposta retornada pela API com grounding e métricas."""

    pergunta: str  # Pergunta que foi realizada
    resposta: str  # Resposta textual gerada pelo Gemini
    fontes_consultadas: List[str]  # Lista de trechos usados como contexto
    metricas: Dict[str, Any]  # Métricas de latência, tokens e FinOps
