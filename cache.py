import json
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

CACHE_FILE = Path("cache_respostas.json")


def normalizar_pergunta(pergunta):
    """Normaliza a pergunta para melhor matching."""
    return pergunta.lower().strip()


def carregar_cache():
    """Carrega o cache de respostas do arquivo."""
    if not CACHE_FILE.exists():
        logger.info("📦 Cache vazio - primeiro uso")
        return {}

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
            logger.info(f"📦 Cache carregado: {len(cache)} respostas em cache")
            return cache
    except Exception as e:
        logger.error(f"❌ Erro ao carregar cache: {e}")
        return {}


def salvar_cache(cache):
    """Salva o cache no arquivo."""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        logger.debug(f"💾 Cache salvo: {len(cache)} respostas")
    except Exception as e:
        logger.error(f"❌ Erro ao salvar cache: {e}")


def buscar_no_cache(pergunta):
    """
    Busca uma resposta no cache.

    Args:
        pergunta: pergunta do usuário

    Returns:
        resposta em cache ou None se não encontrado
    """
    cache = carregar_cache()
    pergunta_normalizada = normalizar_pergunta(pergunta)

    # Busca exata
    if pergunta_normalizada in cache:
        logger.info("✅ Hit no cache! (resposta exata encontrada)")
        return cache[pergunta_normalizada]

    # Busca por similaridade (se a pergunta começa com algo em cache)
    for pergunta_cache, resposta in cache.items():
        if pergunta_normalizada.startswith(pergunta_cache[:20]):
            logger.info("✅ Hit no cache! (resposta similar encontrada)")
            return resposta

    logger.debug(f"❌ Pergunta não está em cache")
    return None


def adicionar_ao_cache(pergunta, resposta):
    """
    Adiciona uma resposta ao cache.

    Args:
        pergunta: pergunta do usuário
        resposta: resposta gerada
    """
    cache = carregar_cache()
    pergunta_normalizada = normalizar_pergunta(pergunta)

    # Não cachear respostas muito curtas (erros, etc)
    if len(resposta) < 50:
        logger.debug("⏭️ Resposta muito curta, não vai para cache")
        return

    # Não cachear se já está em cache
    if pergunta_normalizada in cache:
        logger.debug("⏭️ Pergunta já está em cache")
        return

    cache[pergunta_normalizada] = resposta
    salvar_cache(cache)
    logger.info(f"➕ Resposta adicionada ao cache (total: {len(cache)})")


def limpar_cache():
    """Limpa o cache completamente."""
    try:
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()
            logger.info("🗑️ Cache limpo completamente")
    except Exception as e:
        logger.error(f"❌ Erro ao limpar cache: {e}")


def estatisticas_cache():
    """Retorna estatísticas do cache."""
    cache = carregar_cache()
    return {
        "total_respostas": len(cache),
        "tamanho_bytes": CACHE_FILE.stat().st_size if CACHE_FILE.exists() else 0
    }
