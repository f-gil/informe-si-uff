"""
Demo version of ingest.py for testing without installing all dependencies
Creates a functional ChromaDB with mock course data
"""
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb

def create_chroma_db_with_mock_data():
    """
    Cria um ChromaDB funcional com dados mock do curso
    """
    chroma_dir = Path("chroma_db")
    chroma_dir.mkdir(exist_ok=True)

    print("🔄 Carregando modelo de embeddings...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    # Inicializar ChromaDB
    client = chromadb.PersistentClient(path=str(chroma_dir))

    # Deletar collection anterior se existir
    try:
        client.delete_collection(name="uff_si_docs")
    except:
        pass

    # Criar nova collection
    collection = client.get_or_create_collection(
        name="uff_si_docs",
        metadata={"hnsw:space": "cosine"}
    )

    # Dados mock com informações do curso
    mock_chunks = [
        "O curso de Sistemas de Informação da UFF tem como objetivo formar profissionais capazes de compreender, projetar e implementar soluções tecnológicas que integrem pessoas, processos e tecnologia para resolver problemas de negócio. O egresso deve estar apto a atuar na análise, desenvolvimento e implantação de sistemas de informação em diferentes contextos organizacionais.",

        "Informações do Curso: Duração 4 anos e meio com 8 semestres. Modalidade Presencial. Turno Integral. Carga Horária Total 3.000 horas. Número de Vagas 80 alunos por semestre. Coordenador Prof. Dr. João Silva.",

        "Disciplinas Obrigatórias do Primeiro Semestre: Algoritmos e Programação com 60 horas. Matemática Discreta com 60 horas. Introdução à Computação com 60 horas.",

        "Disciplinas Obrigatórias do Segundo Semestre: Estrutura de Dados com 60 horas. Banco de Dados I com 60 horas. Análise e Projeto de Sistemas com 60 horas.",

        "Disciplinas Obrigatórias do Terceiro Semestre: Engenharia de Software com 60 horas. Segurança da Informação com 60 horas.",

        "Disciplinas Obrigatórias do Quarto Semestre: Gestão de Projetos com 60 horas. Empreendedorismo em TI com 60 horas.",

        "Trabalho de Conclusão de Curso TCC: O TCC é dividido em duas disciplinas. TCC I ocorre no sétimo semestre com 60 horas. TCC II ocorre no oitavo semestre com 60 horas.",

        "Disciplinas Eletivas disponíveis: Inteligência Artificial com fundamentos de IA, machine learning e processamento de linguagem natural. Desenvolvimento Web com arquitetura de aplicações web e frameworks modernos. Computação em Nuvem com infraestrutura em nuvem e containers.",

        "Mais Disciplinas Eletivas: Análise de Dados com data science, visualização de dados e business intelligence. Desenvolvimento Mobile para aplicações em dispositivos móveis. Todas as eletivas têm 60 horas.",

        "Requisitos de Entrada: Ensino Médio Completo ou equivalente. Processo de Seleção através do ENEM ou processo seletivo da UFF. Inscrição realizada através do sistema SIGA da universidade.",

        "Contato e Informações da Coordenação: Email coord.si@ic.uff.br para dúvidas sobre o curso. Site do Instituto de Computação em ic.uff.br. Campus localizado em Santo Antônio, Niterói, RJ. Telefone da coordenação 21 2629-5647.",

        "Perfil do Egresso: O egresso do curso está preparado para atuar como analista de sistemas, desenvolvedor de software, gerente de projetos de TI, consultor de sistemas e empreendedor na área de tecnologia da informação.",
    ]

    print(f"📊 Indexando {len(mock_chunks)} chunks no ChromaDB...")

    # Adicionar chunks ao ChromaDB
    for i, chunk in enumerate(mock_chunks):
        # Gerar embedding
        embedding = model.encode(chunk, convert_to_numpy=True)

        # Adicionar ao ChromaDB
        doc_id = f"demo_chunk_{i}"
        collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[{"source": "curso_si_uff_demo.pdf", "chunk_index": i}],
            documents=[chunk]
        )

        if (i + 1) % 3 == 0:
            print(f"   ⏳ {i + 1}/{len(mock_chunks)} chunks processados", end="\r")

    print(f"   ✓ Todos os {len(mock_chunks)} chunks processados")
    print(f"\n✅ ChromaDB criado com sucesso!")
    print(f"📁 Localização: {chroma_dir}/")
    print(f"✨ Agora você pode usar o chatbot normalmente!")

if __name__ == "__main__":
    print("🔄 Criando ChromaDB funcional com dados mock...")
    create_chroma_db_with_mock_data()
    print("\n✅ Tudo pronto! Execute: streamlit run app.py")
