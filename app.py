import streamlit as st
from chatbot import ChatbotUFF
import time

# Configuracao da pagina
st.set_page_config(
    page_title="Assistente UFF SI",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded"
)

# CSS customizado - Design clean e moderno
st.markdown("""
    <style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background-color: #fafafa;
    }

    .chat-message {
        margin-bottom: 1.25rem;
        display: flex;
        flex-direction: column;
        animation: fadeIn 0.3s ease-in;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    .chat-message.user {
        align-items: flex-end;
    }

    .chat-message.user .message-content {
        background-color: #0B6951;
        color: #f0f0f0;
        padding: 0.875rem 1.25rem;
        border-radius: 18px 18px 4px 18px;
        border-left: 4px solid #0B6951;
        max-width: 85%;
        word-wrap: break-word;
        font-size: 15px;
        line-height: 1.5;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    }

    .chat-message.assistant {
        align-items: flex-start;
    }

    .chat-message.assistant .message-content {
        background-color: #4a4a4a;
        color: #e0e0e0;
        padding: 0.875rem 1.25rem;
        border-radius: 18px 18px 18px 4px;
        border-left: 4px solid #0B6951;
        max-width: 85%;
        word-wrap: break-word;
        font-size: 15px;
        line-height: 1.6;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
    }

    h1 {
        font-size: 2rem;
        font-weight: 700;
        color: #0B6951;
        margin-bottom: 0.25rem !important;
    }

    .subtitle {
        font-size: 0.95rem;
        color: #64748b;
        font-weight: 400;
        margin-bottom: 2rem !important;
    }

    .stChatInputContainer {
        padding: 1rem 0 !important;
    }

    .stChatInputContainer input {
        border: 2px solid #0B6951 !important;
    }

    [data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
    }

    @media (prefers-color-scheme: dark) {
        [data-testid="stSidebar"] {
            background-color: #1a1a1a !important;
        }

        body {
            background-color: #0f0f0f;
        }

        h1 {
            color: #0B6951 !important;
        }

        .subtitle {
            color: #94a3b8 !important;
        }

        .chat-message.user .message-content {
            background-color: #0B6951;
            color: #f0f0f0;
            border-left-color: #0B6951;
        }

        .chat-message.assistant .message-content {
            background-color: #4a4a4a;
            color: #e0e0e0;
            border-left-color: #0B6951;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Titulo e subtitulo
st.markdown("<h1>🎓 Informe_SI</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Tire suas duvidas sobre o curso de Sistemas de Informacao da UFF</p>", unsafe_allow_html=True)

# Inicializar session state
if "chatbot" not in st.session_state:
    try:
        st.session_state.chatbot = ChatbotUFF()
        st.session_state.initialized = True
    except Exception as e:
        st.session_state.initialized = False
        st.session_state.error_msg = str(e)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Barra lateral
with st.sidebar:
    st.header("⚙️ Configuracoes")

    if st.button("🗑️ Limpar conversa", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown(
        """
        ### 📚 Como usar:
        1. Digite sua pergunta sobre o curso
        2. O assistente vai buscar a resposta no documento
        3. Se nao encontrar, ele sugerira consultar a coordenacao

        Por favor, faça a avaliação da aplicação no link à seguir: https://pudim.com.br

        """
    )

# Verificar inicializacao
if not st.session_state.initialized:
    st.error(f"❌ Erro ao inicializar o chatbot: {st.session_state.error_msg}")
    st.info("Verifique se:")
    st.info("1. Executou `python ingest.py` para processar os PDFs")
    st.info("2. Sua chave GEMINI_API_KEY esta configurada no arquivo `.env`")
    st.stop()

# Exibir historico de mensagens
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(
            f'<div class="chat-message user"><div class="message-content">{message["content"]}</div></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="chat-message assistant"><div class="message-content">{message["content"]}</div></div>',
            unsafe_allow_html=True
        )

# Input do usuario
user_input = st.chat_input("Digite sua pergunta sobre o curso...")

if user_input:
    # Adicionar pergunta ao historico
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Exibir a pergunta imediatamente
    st.markdown(
        f'<div class="chat-message user"><div class="message-content">{user_input}</div></div>',
        unsafe_allow_html=True
    )

    # Processar e obter resposta com historico de conversa
    with st.spinner("🔄 Buscando resposta..."):
        try:
            # Passar historico de conversa anterior para contextualizar a resposta
            response = st.session_state.chatbot.answer(
                user_input,
                conversation_history=st.session_state.messages[:-1]
            )
        except Exception as e:
            response = f"❌ Erro ao processar a pergunta: {str(e)}\n\nTente novamente ou consulte a coordenacao."

    # Adicionar resposta ao historico
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Exibir resposta com efeito de digitação (letra por letra)
    response_container = st.empty()
    displayed_text = ""

    # Velocidade de digitação: 0.01 segundos por letra para efeito rápido
    delay = 0.01

    for char in response:
        displayed_text += char
        response_container.markdown(
            f'<div class="chat-message assistant"><div class="message-content">{displayed_text}</div></div>',
            unsafe_allow_html=True
        )
        time.sleep(delay)

    # Rerun para atualizar a interface
    st.rerun()
