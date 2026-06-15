"""
Configurações centralizadas para o sistema de RAG (Retrieval-Augmented Generation)
Mantém todas as configurações de busca semântica em um único lugar para fácil manutenção.
"""

# ============================================================================
# CONFIGURAÇÕES DE TOP_K (número de chunks buscados no ChromaDB)
# ============================================================================

# Queries simples (ex: "Como funciona o BusUFF?", "O que é TCC?")
RAG_TOP_K_SIMPLE = 5

# Queries sobre tópicos com múltiplos itens (atividades, disciplinas, bolsas, etc)
RAG_TOP_K_MULTI = 15

# Fallback quando a busca anterior não retorna resultados
RAG_TOP_K_FALLBACK = 20

# ============================================================================
# KEYWORDS PARA DETECÇÃO AUTOMÁTICA DE TÓPICOS MULTI-ITEM
# ============================================================================
# Quando a query contém alguma dessas palavras, usa RAG_TOP_K_MULTI automaticamente
# Útil para tópicos fragmentados em vários chunks (ex: 23 atividades complementares)

RAG_KEYWORDS_MULTI_ITEM = [
    # Curso (PDF 01)
    "curso", "objetivo", "bacharelado",
    # Atividades Complementares
    "atividade",
    # Disciplinas
    "disciplina", "pré-requisito", "matéria", "cadeia",
    # Bolsas e Auxílios
    "bolsa", "auxílio", "benefício",
    # Estágio
    "estágio",
    # TCC (PDF 07)
    "tcc", "defesa", "projeto", "monografia",
    # Geral para múltiplos programas
    "programa", "atendimento", "modalidade", "requisito",
    # Alimentação e Transporte
    "restaurante", "moradia", "transporte", "horário", "rota",
    # Acessibilidade e Saúde
    "acesso", "acomodação", "inclusão", "saúde", "psicológico",
    # Complementares
    "seminário", "evento", "pesquisa", "extensão", "mentor",
]

# ============================================================================
# DETECÇÃO DE RESPOSTAS INCOMPLETAS
# ============================================================================

# Se a resposta tem menos de X palavras, pode ser incompleta
# Ativa fallback automático para top_k maior
RAG_MIN_RESPONSE_LENGTH = 80  # palavras

# ============================================================================
# CONFIGURAÇÕES DE CACHE
# ============================================================================

# Tempo de expiração do cache em horas
CACHE_EXPIRATION_HOURS = 24

# ============================================================================
# CONFIGURAÇÕES DO GEMINI
# ============================================================================

# Número máximo de tokens na resposta
GEMINI_MAX_TOKENS = 1024

# Temperatura (criatividade da resposta)
# 0.0 = determinístico, 1.0 = criativo
GEMINI_TEMPERATURE = 0.7
