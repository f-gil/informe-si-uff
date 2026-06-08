# 🔗 Como Adicionar Links de Informação

## 📍 Como Funciona Atualmente

O bot agora fornece **links específicos por tópico** quando não encontra informação. Por exemplo:

- Pergunta: "Como me inscrever?"
- Resposta: "Desculpe, não encontrei... Acesse: [link de inscrição]"

## 🎯 Personalizando os Links

### Opção 1: Editar Links Existentes

Abra o arquivo `chatbot.py` e procure por `LINKS_ESPECIFICOS`:

```python
LINKS_ESPECIFICOS = {
    "disciplina": "https://www.uff.br/curso/sistemas-de-informacao/",
    "inscricao": "https://www.uff.br/curso/sistemas-de-informacao/",
    "contato": "https://www.uff.br/curso/sistemas-de-informacao/",
    # ... mais links
}
```

**Para alterar um link:**
```python
# Antes:
"disciplina": "https://www.uff.br/curso/sistemas-de-informacao/",

# Depois (seu próprio link):
"disciplina": "https://seu-site.com/disciplinas",
```

### Opção 2: Adicionar Novos Links

Adicione uma nova linha no dicionário:

```python
LINKS_ESPECIFICOS = {
    # ... links existentes
    "bolsa": "https://www.uff.br/bolsas",
    "estudio": "https://www.uff.br/estudio",
    "certificado": "https://www.uff.br/certificados",
}
```

## 📋 Exemplos de Palavras-Chave

Você pode adicionar palavras-chave para:

```python
LINKS_ESPECIFICOS = {
    # Académico
    "disciplina": "link_disciplinas",
    "semestre": "link_semestres",
    "nota": "link_notas",
    "horario": "link_horarios",
    
    # Inscrição
    "inscricao": "link_inscricao",
    "enem": "link_enem",
    "sisu": "link_sisu",
    
    # Administrativo
    "contato": "link_contato",
    "email": "link_contato",
    "telefone": "link_contato",
    
    # Financeito
    "mensalidade": "link_mensalidade",
    "bolsa": "link_bolsa",
    "financiamento": "link_financiamento",
    
    # Outros
    "tcc": "link_tcc",
    "estágio": "link_estagio",
    "certificado": "link_certificado",
}
```

## 🚀 Como Testar

1. Edite `chatbot.py`
2. Adicione um novo link
3. Recarregue o Streamlit (F5)
4. Faça uma pergunta com a palavra-chave
5. Veja o link aparecer na resposta!

## 💡 Dicas

- **Use palavras-chave genéricas** para cobrir mais perguntas
  - ✅ Bom: "disciplina"
  - ❌ Ruim: "disciplina_obrigatoria_primeiro_semestre"

- **Teste com variações**
  - Se adicionar "inscricao", considere também "inscriçao", "como entrar", "como me inscrever"

- **Mantenha URLs atualizadas**
  - Se o site mudar, atualize o URL correspondente

## 📝 Exemplo Completo

Seu `LINKS_ESPECIFICOS` pode ficar assim:

```python
LINKS_ESPECIFICOS = {
    # Informacoes basicas
    "disciplina": "https://www.uff.br/curso/sistemas-de-informacao/",
    "semestre": "https://www.uff.br/curso/sistemas-de-informacao/",
    
    # Inscricao
    "inscricao": "https://www.uff.br/processoseletivo/",
    "enem": "https://www.uff.br/processoseletivo/",
    "como entrar": "https://www.uff.br/processoseletivo/",
    
    # Contato
    "contato": "https://www.uff.br/curso/sistemas-de-informacao/#contato",
    "email": "https://www.uff.br/curso/sistemas-de-informacao/#contato",
    "telefone": "https://www.uff.br/curso/sistemas-de-informacao/#contato",
    
    # TCC
    "tcc": "https://www.uff.br/ic/tcc/",
}
```

## ✅ Pronto!

Agora o bot fornecerá links específicos e inteligentes! 🎯
