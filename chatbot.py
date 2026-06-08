import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
import google.generativeai as genai
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurar chave da API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY não encontrada. Configure no arquivo .env")

genai.configure(api_key=GEMINI_API_KEY)

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

            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(search_prompt)

            resposta = response.text.strip()

            # Verificar se o Gemini encontrou informação
            if "não encontrei" not in resposta.lower():
                return True, resposta
            else:
                return False, ""

        except Exception as e:
            print(f"Erro ao buscar no site: {e}")
            return False, ""

    def answer(self, query, conversation_history=None):
        """
        Responde a uma pergunta com múltiplos fallbacks e memória de contexto.

        Estratégia:
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
                    system_prompt = """Você é um assistente amigável e prestativo do curso de Sistemas de Informação da UFF! 🎓

CARACTERÍSTICAS DO SEU TOM:
- Seja entusiasta sobre o curso e amigável com os alunos
- Use tom conversacional e acessível
- Simpatize com as dúvidas dos alunos
- Estruture respostas com clareza e organização
- Use emojis ocasionalmente para deixar mais amigável
- Se não souber, seja honesto e sugira alternativas

EXEMPLOS DO TOM ESPERADO:
- ❌ Ruim: "Não encontrei informação"
- ✅ Bom: "Deixa eu procurar isso para você! 😊"

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
                    system_prompt = """Você é um assistente amigável e prestativo do curso de Sistemas de Informação da UFF! 🎓

CARACTERÍSTICAS DO SEU TOM:
- Seja entusiasta sobre o curso e amigável com os alunos
- Use tom conversacional e acessível
- Simpatize com as dúvidas dos alunos
- Estruture respostas com clareza e organização
- Use emojis ocasionalmente para deixar mais amigável
- Se não souber, seja honesto e sugira alternativas

EXEMPLOS DO TOM ESPERADO:
- ❌ Ruim: "Não encontrei informação"
- ✅ Bom: "Deixa eu procurar isso para você! 😊"

REGRA IMPORTANTE:
Use APENAS as informações do contexto abaixo para responder.

Contexto:
{context}

Pergunta: {query}"""
                    prompt = system_prompt.format(context=context, query=query)

                try:
                    model = genai.GenerativeModel("gemini-2.5-flash")
                    response = model.generate_content(
                        prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.7,  # Tom amigável e natural
                            top_p=0.9,
                            top_k=40
                        )
                    )
                    return response.text
                except Exception as gemini_error:
                    # Se deu erro 429 (quota excedida), usar ChromaDB diretamente
                    if "429" in str(gemini_error) or "quota" in str(gemini_error).lower():
                        # FALLBACK COM QUOTA: Usar apenas ChromaDB
                        resposta_formatada = f"""📚 Informação encontrada na base de conhecimento:

{context}

⏱️ Estamos com um fluxo intenso de requisições no momento, mas conseguimos buscar essa informação para você!

Se tiver dúvidas adicionais, fique à vontade para perguntar! 😊"""
                        return resposta_formatada
                    else:
                        raise

            # FALLBACK 2: Tentar buscar no site da UFF
            encontrou_no_site, resposta_site = self.search_on_uff_site(query)

            if encontrou_no_site:
                resposta_final = f"""{resposta_site}

📚 Para mais detalhes, acesse: {CURSO_URL}"""
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
            return f"❌ Erro: {str(e)}"
        except Exception as e:
            return f"❌ Erro ao processar a pergunta: {str(e)}"


# Exemplo de uso
if __name__ == "__main__":
    chatbot = ChatbotUFF()

    # Teste
    query = "O que é o curso de Sistemas de Informação?"
    print(f"\n👤 Pergunta: {query}")
    print(f"🤖 Resposta: {chatbot.answer(query)}\n")
