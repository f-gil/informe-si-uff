# 🎓 Assistente do Curso de SI — UFF

Um chatbot em português que responde dúvidas sobre o curso de Sistemas de Informação da UFF, alimentado por PDFs e sem nenhum custo de API.

## 🚀 Stack Tecnológico

- **google-generativeai** — Gemini 2.5 Flash (gratuito)
- **sentence-transformers** — Embeddings locais em português
- **chromadb** — Banco de dados vetorial local
- **PyMuPDF** — Leitura de PDFs
- **Streamlit** — Interface web

## 📁 Estrutura do Projeto

```
uff-si-chatbot/
├── data/               ← Coloque seus PDFs aqui
├── chroma_db/          ← Criado automaticamente (embeddings)
├── ingest.py           ← Script para processar PDFs
├── chatbot.py          ← Lógica principal do chatbot
├── app.py              ← Interface Streamlit
├── requirements.txt    ← Dependências
├── .env.example        ← Modelo de variáveis de ambiente
└── README.md           ← Este arquivo
```

## 🔧 Instalação

### 1. Clone ou descarregue o projeto
```bash
cd uff-si-chatbot
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure sua chave de API
- Obtenha uma chave gratuita em: https://aistudio.google.com/apikey
- Copie o arquivo `.env.example` para `.env`
- Adicione sua chave no arquivo `.env`:

```bash
cp .env.example .env
# Edite .env e adicione sua chave
```

Arquivo `.env`:
```
GEMINI_API_KEY=sua_chave_aqui
```

### 5. Adicione seus PDFs
- Coloque seus PDFs na pasta `data/`
- Exemplo: `data/curso_si.pdf`

## 📖 Como Usar

### 1. Processar os PDFs (primeira vez)
```bash
python ingest.py
```

**Saída esperada:**
```
📄 Encontrados 1 PDF(s)
🔄 Carregando modelo de embeddings...
📖 Processando: curso_si.pdf
   ✓ 50 chunks criados
   ✓ Todos os chunks processados
✅ Ingestão concluída! 50 chunks indexados.
```

### 2. Iniciar a interface Streamlit
```bash
streamlit run app.py
```

A interface abrirá em `http://localhost:8501`

### 3. Fazer perguntas
Tipo suas dúvidas sobre o curso e o assistente respondera com base no documento!

## 🤖 Como Funciona

1. **Ingestão**: `ingest.py` lê os PDFs, divide em chunks e gera embeddings localmente
2. **Busca**: Quando você faz uma pergunta, o chatbot busca os 5 chunks mais relevantes
3. **Geração**: O Gemini 2.5 Flash gera a resposta baseada nesses chunks
4. **Histórico**: A conversa é mantida durante a sessão

## 📊 Características

✅ Embeddings locais (nenhum envio de dados)  
✅ Busca semântica eficiente com ChromaDB  
✅ Respostas contextualizadas do PDF  
✅ Interface amigável com Streamlit  
✅ Histórico de conversa  
✅ Sem custo de armazenamento ou busca  

## ⚠️ Notas Importantes

- **Primeira execução**: O modelo de embeddings será baixado automaticamente (~500 MB)
- **Conexão**: Apenas a geração de respostas precisa de internet (Gemini API)
- **Privacidade**: O contexto do PDF é enviado ao Gemini, mas não é armazenado
- **Chave API**: A chave GEMINI_API_KEY é gratuita com limite de requisições/mês

## 🐛 Troubleshooting

### "Collection 'uff_si_docs' não encontrada"
Execute `python ingest.py` primeiro para processar os PDFs.

### "GEMINI_API_KEY não encontrada"
Certifique-se de que:
1. Você criou um arquivo `.env` (cópia de `.env.example`)
2. Adicionou sua chave GEMINI_API_KEY nele
3. Está na pasta correta ao executar

### Modelo de embeddings muito lento
Na primeira execução, o modelo é baixado (~500 MB). Isso pode levar alguns minutos.

## 📝 Licença

Projeto de código aberto. Fique à vontade para adaptar e usar!

## 🙋 Suporte

Se encontrar problemas:
1. Verifique se todos os PDFs estão em `data/`
2. Confirme que executou `python ingest.py`
3. Valide sua chave GEMINI_API_KEY em https://aistudio.google.com/apikey

Bom uso! 🎓✨
