# 🎓 Instruções Para Usar no Seu Computador

## ⚠️ Importante

O projeto foi criado e testado **no seu computador**, não no servidor. Siga os passos abaixo:

## 🚀 Passo 1: Instalar Python

- Baixe Python 3.8+ de https://www.python.org
- Marque a opção "Add Python to PATH" durante a instalação

## 🚀 Passo 2: Criar Ambiente Virtual

Abra o terminal/cmd na pasta do projeto e execute:

```bash
python -m venv venv
```

**Ativar (Windows):**
```bash
venv\Scripts\activate
```

**Ativar (Mac/Linux):**
```bash
source venv/bin/activate
```

## 🚀 Passo 3: Instalar Dependências

```bash
pip install -r requirements.txt
```

## 🚀 Passo 4: Configurar Chave da API

1. Acesse: https://aistudio.google.com/apikey
2. Clique em "Create API Key"
3. Copie a chave
4. Abra o arquivo `.env` (renomeie `.env.example` se necessário)
5. Cole a chave:

```
GEMINI_API_KEY=sua_chave_aqui
```

## 🚀 Passo 5: Criar o ChromaDB com Dados

Execute **uma das duas opções abaixo**:

### Opção A: Com seu próprio PDF (recomendado)

Coloque um PDF sobre o curso na pasta `data/` e execute:

```bash
python ingest.py
```

### Opção B: Com dados de exemplo (para testes rápidos)

Execute:

```bash
python ingest_demo.py
```

Isso cria um ChromaDB funcional com informações de exemplo sobre o curso.

**Saída esperada:**
```
🔄 Carregando modelo de embeddings...
📊 Indexando 12 chunks no ChromaDB...
   ✓ Todos os 12 chunks processados
✅ ChromaDB criado com sucesso!
```

## 🚀 Passo 6: Iniciar o Chatbot

```bash
streamlit run app.py
```

A interface abrirá automaticamente em `http://localhost:8501`

## ✅ Testando

Tente fazer perguntas como:
- "O que é o curso de SI?"
- "Qual a duração do curso?"
- "Como faço para entrar?"
- "Quais são as disciplinas obrigatórias?"
- "Qual o email da coordenação?"

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'chromadb'"

Certifique-se que:
1. Você ativou o ambiente virtual (`venv\Scripts\activate`)
2. Executou `pip install -r requirements.txt`

### "GEMINI_API_KEY não encontrada"

Verifique se:
1. Você criou um arquivo `.env` (não `.env.example`)
2. Adicionou sua chave no formato: `GEMINI_API_KEY=sua_chave_aqui`
3. O arquivo está na pasta do projeto

### "Collection 'uff_si_docs' não encontrada"

Execute:
```bash
python ingest_demo.py
```

ou coloque um PDF em `data/` e execute:
```bash
python ingest.py
```

### As respostas não estão encontrando informações

Verifique se:
1. Você executou `python ingest_demo.py` ou `python ingest.py`
2. A pasta `chroma_db/` foi criada com arquivos dentro
3. Se tudo falhar, delete a pasta `chroma_db/` e execute novamente

## 📚 Estrutura do Projeto

```
uff-si-chatbot/
├── data/                    ← Coloque seus PDFs aqui
├── chroma_db/               ← Será criado automaticamente
├── ingest.py               ← Processa seus PDFs
├── ingest_demo.py          ← Cria dados de exemplo
├── chatbot.py              ← Lógica do chatbot
├── app.py                  ← Interface Streamlit
├── requirements.txt        ← Dependências
├── .env                    ← Sua chave de API
└── .env.example            ← Template
```

## 💡 Dicas

- Você pode colocar múltiplos PDFs na pasta `data/` e executar `python ingest.py`
- O modelo de embeddings será baixado na primeira execução (~500MB)
- Depois disso, não precisa de internet para buscar informações (só para gerar respostas)

## 🎉 Pronto!

Se seguiu todos os passos, agora você tem um chatbot funcional sobre o curso de SI da UFF!

Bom uso! 🚀✨
