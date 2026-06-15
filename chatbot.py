import os
import logging
import warnings
from pathlib import Path

# Suprimir warnings desnecessários das dependências
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*transformers.*")
warnings.filterwarnings("ignore", message=".*torchvision.*")

from sentence_transformers import SentenceTransformer
import chromadb
import google.generativeai as genai
from dotenv import load_dotenv
from cache import buscar_no_cache, adicionar_ao_cache
from keys_manager import get_keys_manager

# Configurar logging para debug (apenas nossos logs importam)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suprimir logs verbosos das dependências
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("transformers").setLevel(logging.WARNING)
logging.getLogger("sentence_transformers").setLevel(logging.WARNING)

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar gerenciador de chaves
keys_manager = get_keys_manager()

# URLs do site do curso
CURSO_URL = "https://www.uff.br/curso/sistemas-de-informacao/"

# Mapeamento de palavras-chave para links específicos
LINKS_ESPECIFICOS = {
    "disciplina": "https://www.uff.br/curso/sistemas-de-informacao/",
    "semestre": "https://www.uff.br/curso/sistemas-de-informacao/",
    "inscricao": "https://www.uff.br/curso/sistemas-de-informacao/",
    "como entrar": "https://www.uff.br/curso/sistemas-de-informacao/",
    "requisito": "https://www.uff.br/curso/sistemas-de-informacao/",
    "entrada": "https://www.uff.br/curso/sistemas-de-informacao/",
    "enem": "https://www.uff.br/curso/sistemas-de-informacao/",
    "coordinador": "https://www.uff.br/curso/sistemas-de-informacao/",
    "contato": "https://www.uff.br/curso/sistemas-de-informacao/",
    "email": "https://www.uff.br/curso/sistemas-de-informacao/",
    "telefone": "https://www.uff.br/curso/sistemas-de-informacao/",
    "tcc": "https://www.uff.br/curso/sistemas-de-informacao/",
    "trabalho conclusao": "https://www.uff.br/curso/sistemas-de-informacao/",
    "duracao": "https://www.uff.br/curso/sistemas-de-informacao/",
    "horario": "https://www.uff.br/curso/sistemas-de-informacao/",
}

def formatar_contexto_fallback(context, max_linhas=10):
    """
    Formata o contexto do ChromaDB para apresentação legível no fallback.

    Remove ruído, limpa formatação, e organiza de forma amigável.

    Args:
        context: texto bruto dos chunks do ChromaDB
        max_linhas: máximo de linhas para retornar

    Returns:
        texto formatado e legível
    """
    if not context or not context.strip():
        return "Desculpe, não encontrei informação específica sobre isso."

    # Dividir em linhas
    linhas = context.split('\n')

    # Limpar linhas
    linhas_limpas = []
    for linha in linhas:
        linha = linha.strip()

        # Pular linhas muito curtas (ruído)
        if len(linha) < 10:
            continue

        # Pular linhas que parecem URLs incompletas ou truncadas
        if linha.endswith(('...', '–', '—', 'http', '.com')):
            continue

        # Pular linhas que começam com caracteres de erro (como "ntífico)")
        if linha[0] in 'ntçãõó' and not linha[0].isupper():
            continue

        linhas_limpas.append(linha)

    # Remover duplicatas mantendo ordem
    linhas_unicas = []
    vistas = set()
    for linha in linhas_limpas:
        if linha not in vistas:
            linhas_unicas.append(linha)
            vistas.add(linha)

    # Limitar número de linhas
    linhas_unicas = linhas_unicas[:max_linhas]

    # Se ficou vazio, retornar mensagem genérica
    if not linhas_unicas:
        return "Encontrei informação na base, mas com formatação problemática. Tente fazer outra pergunta ou entre em contato."

    # Montar resultado formatado
    resultado = "**Informação encontrada:**\n\n"
    resultado += "\n".join(linhas_unicas)

    return resultado


def chamar_gemini_com_retry(prompt, max_tentativas=None):
    """
    Chama Gemini com suporte a múltiplas chaves e retry automático.

    Estratégia:
    1. Tenta com a chave atual (round-robin)
    2. Se 429 (quota), rotaciona para próxima chave
    3. Repete até sucesso ou fim das chaves

    Args:
        prompt: prompt para enviar ao Gemini
        max_tentativas: máximo de chaves a tentar (default: todas)

    Returns:
        texto da resposta ou raises Exception se todas falharem

    Raises:
        Exception: se todas as chaves derem erro (quota ou outra razão)
    """
    total_chaves = keys_manager.obter_total_chaves()
    max_tentativas = max_tentativas or total_chaves

    erros = []

    for tentativa in range(max_tentativas):
        chave, numero_chave = keys_manager.obter_proxima_chave()

        try:
            logger.debug(f"🔑 Tentativa {tentativa + 1}/{max_tentativas} com chave #{numero_chave}")

            # Configurar chave globalmente e criar modelo
            genai.configure(api_key=chave)
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            return response.text

        except Exception as erro:
            erro_str = str(erro)
            erro_tipo = type(erro).__name__

            logger.warning(f"⚠️ Chave #{numero_chave} falhou: [{erro_tipo}]")

            # Se é erro de quota, tenta próxima chave
            if "429" in erro_str or "quota" in erro_str.lower() or "resource_exhausted" in erro_str.lower():
                logger.warning(f"⏱️ Chave #{numero_chave} sem quota, rotacionando...")
                erros.append((numero_chave, "Quota excedida"))
                continue

            # Se é outro erro, também tenta próxima (mas loga diferente)
            logger.error(f"❌ Chave #{numero_chave} erro: {erro_str}")
            erros.append((numero_chave, erro_tipo))
            continue

    # Se chegou aqui, todas as chaves falharam
    logger.error(f"❌ Todas as {max_tentativas} chaves falharam!")
    for num, razao in erros:
        logger.error(f"   - Chave #{num}: {razao}")

    raise Exception(
        f"Todas as {max_tentativas} chaves Gemini falharam ou estão sem quota. "
        "Tente novamente mais tarde."
    )


def obter_link_relevante(query):
    """
    Obtém o link mais relevante baseado na pergunta.

    Args:
        query: pergunta do usuário

    Returns:
        URL relevante ou None
    """
    query_lower = query.lower()
    for palavra, url in LINKS_ESPECIFICOS.items():
        if palavra in query_lower:
            return url
    return None


class ChatbotUFF:
    def __init__(self):
        """Inicializa o chatbot carregando o modelo e ChromaDB."""
        print("🚀 Inicializando chatbot...")

        # Mostrar informações das chaves
        total_chaves = keys_manager.obter_total_chaves()
        print(f"🔑 {total_chaves} chave(s) Gemini configurada(s)")
        logger.info(f"Quota diária: ~{total_chaves * 20} requisições (~{int(total_chaves * 13)} perguntas)")

        # Carregar modelo de embeddings
        self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

        # Conectar ao ChromaDB
        chroma_dir = Path("chroma_db")
        if not chroma_dir.exists():
            raise FileNotFoundError(
                "❌ Pasta chroma_db não encontrada. Execute ingest.py primeiro!"
            )

        self.client = chromadb.PersistentClient(path=str(chroma_dir))

        try:
            self.collection = self.client.get_collection(name="uff_si_docs")
        except ValueError:
            raise ValueError(
                "❌ Collection 'uff_si_docs' não encontrada. Execute ingest.py primeiro!"
            )

        print("✅ Chatbot inicializado com sucesso!")

    def retrieve_context(self, query, top_k=5):
        """
        Busca os chunks mais relevantes para a pergunta.

        Args:
            query: pergunta do usuário
            top_k: número de chunks a retornar

        Returns:
            string com os chunks concatenados
        """
        # Gerar embedding da pergunta
        query_embedding = self.model.encode(query, convert_to_numpy=True)

        # Buscar chunks relevantes
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        # Concatenar chunks
        context = ""
        if results["documents"] and results["documents"][0]:
            context = "\n\n".join(results["documents"][0])

        return context

    def search_on_uff_site(self, query):
        """
        Tenta buscar a informação no site da UFF.

        Args:
            query: pergunta do usuário

        Returns:
            tuple (encontrou, resposta_resumida)
        """
        try:
            # Montar prompt para o Gemini buscar no site
            search_prompt = f"""Você pode ajudar a responder uma pergunta sobre o curso de Sistemas de Informação da UFF?

Pergunta: {query}

INFORMAÇÃO IMPORTANTE:
- O curso está em: {CURSO_URL}
- Responda APENAS se você tiver informações confiáveis sobre este curso específico
- Se não tiver informações, responda: "Não encontrei essa informação disponível"
- Mantenha a resposta breve e útil
- Comece direto com a resposta, sem preâmbulos"""

            # Usar múltiplas chaves com retry automático
            resposta = chamar_gemini_com_retry(search_prompt)
            resposta = resposta.strip()

            # Verificar se o Gemini encontrou informação
            if "não encontrei" not in resposta.lower():
                return True, resposta
            else:
                return False, ""

        except Exception as e:
            error_str = str(e)
            logger.error(f"🐛 Erro ao buscar no site: {error_str}")
            return False, ""

    def answer(self, query, conversation_history=None):
        """
        Responde a uma pergunta com múltiplos fallbacks e memória de contexto.

        Estratégia:
        0. Verifica cache de respostas anteriores
        1. Tenta encontrar no ChromaDB (documento local)
        2. Se não encontrar, tenta buscar no site da UFF
        3. Se ainda não encontrar, sugere contato com a coordenação
        4. Usa histórico de conversa para contextualizar respostas

        Args:
            query: pergunta do usuário
            conversation_history: lista de mensagens anteriores [{"role": "user"|"assistant", "content": "..."}, ...]

        Returns:
            resposta do assistente como string
        """
        try:
            # CACHE 0: Verificar se já respondemos essa pergunta antes
            resposta_cached = buscar_no_cache(query)
            if resposta_cached:
                logger.info(f"🎯 Resposta retornada do CACHE (economizou quota!)")
                return resposta_cached
            # FALLBACK 1: Tentar com ChromaDB (5 chunks)
            context = self.retrieve_context(query, top_k=5)

            # Se não encontrou, tentar com mais chunks
            if not context.strip():
                context = self.retrieve_context(query, top_k=10)

            # Construir histórico de conversa para contexto
            historico_contexto = ""
            if conversation_history:
                # Usar apenas as últimas 4 mensagens (2 turnos de conversa)
                ultimas_mensagens = conversation_history[-4:] if len(conversation_history) > 4 else conversation_history

                for msg in ultimas_mensagens:
                    role = "Você" if msg["role"] == "user" else "Assistente"
                    historico_contexto += f"{role}: {msg['content']}\n"

            # Se encontrou no documento local, usar
            if context.strip():
                if historico_contexto.strip():
                    system_prompt = """Você é um assistente do curso de Sistemas de Informação da UFF.

CARACTERÍSTICAS DO SEU TOM:
- Seja amigável e conversacional, como falando com um colega
- Seja direto e objetivo: vá direto ao ponto sem floreios
- Use linguagem natural e informal, sem ser genérico
- Sempre respeitoso e inclusivo com TODOS os alunos, independente de idade ou origem
- Use termos apropriados: "veteranos" para alunos mais experientes
- Se não souber, seja honesto: "Não tenho essa informação aqui, mas você pode checar com..."

REGRA IMPORTANTE:
Use APENAS as informações do contexto abaixo para responder.
Considere o histórico de conversa anterior para contextualizar sua resposta.

Histórico da conversa anterior:
{historico}

Contexto do documento:
{context}

Nova pergunta: {query}"""
                    prompt = system_prompt.format(historico=historico_contexto, context=context, query=query)
                else:
                    system_prompt = """Você é um assistente do curso de Sistemas de Informação da UFF.

CARACTERÍSTICAS DO SEU TOM:
- Seja amigável e conversacional, como falando com um colega
- Seja direto e objetivo: vá direto ao ponto sem floreios
- Use linguagem natural e informal, sem ser genérico
- Sempre respeitoso e inclusivo com TODOS os alunos, independente de idade ou origem
- Use termos apropriados: "veteranos" para alunos mais experientes
- Se não souber, seja honesto: "Não tenho essa informação aqui, mas você pode checar com..."

REGRA IMPORTANTE:
Use APENAS as informações do contexto abaixo para responder.

Contexto:
{context}

Pergunta: {query}"""
                    prompt = system_prompt.format(context=context, query=query)

                try:
                    # Usar múltiplas chaves com retry automático
                    resposta = chamar_gemini_com_retry(prompt)
                    # Cachear resposta para próximas vezes
                    adicionar_ao_cache(query, resposta)
                    return resposta
                except Exception as gemini_error:
                    # Log do erro real para debug
                    error_str = str(gemini_error)
                    logger.error(f"🐛 Erro Gemini: {error_str}")

                    # Se TODAS as chaves falharam com quota, usar ChromaDB diretamente
                    if "quota" in error_str.lower() or "resource_exhausted" in error_str.lower() or "Todas as" in error_str:
                        logger.warning("⏱️ Todas as chaves sem quota, usando fallback ChromaDB formatado")
                        # FALLBACK COM QUOTA: Usar ChromaDB formatado de forma legível
                        contexto_limpo = formatar_contexto_fallback(context)
                        resposta_formatada = f"""{contexto_limpo}

⏱️ Nota: Estamos com um fluxo intenso de requisições, mas conseguimos buscar essa informação para você!

Precisa de mais detalhes? Entre em contato:
📧 Email: coord.si@ic.uff.br
📞 Telefone: (21) 2629-5647"""
                        return resposta_formatada
                    else:
                        # Se é outro erro crítico, re-lançar
                        logger.error(f"❌ Erro crítico: {error_str}")
                        raise

            # FALLBACK 2: Tentar buscar no site da UFF
            encontrou_no_site, resposta_site = self.search_on_uff_site(query)

            if encontrou_no_site:
                resposta_final = f"""{resposta_site}

📚 Para mais detalhes, acesse: {CURSO_URL}"""
                # Cachear resposta do site também
                adicionar_ao_cache(query, resposta_final)
                return resposta_final

            # FALLBACK 3: Nenhum lugar encontrou - sugerir contato com link relevante
            link_relevante = obter_link_relevante(query)

            if link_relevante:
                resposta_final = f"""Desculpe, não encontrei essa informação no documento do curso.

Recomendo que você acesse a página do curso para mais detalhes:
📚 {link_relevante}

Ou entre em contato com a coordenação:
📧 Email: coord.si@ic.uff.br
📞 Telefone: (21) 2629-5647"""
            else:
                resposta_final = f"""Desculpe, não encontrei essa informação no documento do curso nem no site.

Recomendo que você:
1. Consulte o site completo do curso: {CURSO_URL}
2. Entre em contato com a coordenação:
   📧 Email: coord.si@ic.uff.br
   📞 Telefone: (21) 2629-5647"""

            return resposta_final

        except ValueError as e:
            logger.error(f"❌ ValueError: {str(e)}")
            return f"❌ Erro: {str(e)}"
        except Exception as e:
            error_str = str(e)
            logger.error(f"❌ Erro inesperado [{type(e).__name__}]: {error_str}")
            return f"❌ Erro ao processar a pergunta: {error_str}"


# Exemplo de uso
if __name__ == "__main__":
    chatbot = ChatbotUFF()

    # Teste
    query = "O que é o curso de Sistemas de Informação?"
    print(f"\n👤 Pergunta: {query}")
    print(f"🤖 Resposta: {chatbot.answer(query)}\n")