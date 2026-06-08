import os
import glob
from pathlib import Path
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
import chromadb

def chunk_text(text, chunk_size=500, overlap=50):
    """
    Divide o texto em chunks com overlap.

    Args:
        text: texto a ser dividido
        chunk_size: tamanho de cada chunk em caracteres
        overlap: sobreposição entre chunks

    Returns:
        lista de chunks
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


def read_pdf(pdf_path):
    """
    Lê um arquivo PDF usando PyMuPDF.

    Args:
        pdf_path: caminho do PDF

    Returns:
        texto extraído do PDF
    """
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception as e:
        print(f"❌ Erro ao ler {pdf_path}: {e}")
        return ""


def ingest_pdfs():
    """
    Ingere todos os PDFs da pasta data/ e indexa no ChromaDB.
    """
    # Configurar caminhos
    data_dir = Path("data")
    chroma_dir = Path("chroma_db")

    # Criar pasta data se não existir
    data_dir.mkdir(exist_ok=True)
    chroma_dir.mkdir(exist_ok=True)

    # Buscar todos os PDFs
    pdf_files = list(data_dir.glob("*.pdf"))

    if not pdf_files:
        print("⚠️  Nenhum PDF encontrado na pasta 'data/'")
        return

    print(f"📄 Encontrados {len(pdf_files)} PDF(s)")

    # Carregar modelo de embeddings
    print("🔄 Carregando modelo de embeddings...")
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

    # Inicializar ChromaDB
    client = chromadb.PersistentClient(path=str(chroma_dir))

    # Deletar collection anterior se existir (para recomeçar do zero)
    try:
        client.delete_collection(name="uff_si_docs")
    except:
        pass

    # Criar nova collection
    collection = client.get_or_create_collection(
        name="uff_si_docs",
        metadata={"hnsw:space": "cosine"}
    )

    total_chunks = 0

    # Processar cada PDF
    for pdf_file in pdf_files:
        print(f"\n📖 Processando: {pdf_file.name}")

        # Ler PDF
        text = read_pdf(pdf_file)
        if not text.strip():
            print(f"⚠️  Nenhum texto extraído de {pdf_file.name}")
            continue

        # Dividir em chunks
        chunks = chunk_text(text, chunk_size=500, overlap=50)
        print(f"   ✓ {len(chunks)} chunks criados")

        # Gerar embeddings e adicionar ao ChromaDB
        for i, chunk in enumerate(chunks):
            # Gerar embedding
            embedding = model.encode(chunk, convert_to_numpy=True)

            # Adicionar ao ChromaDB
            doc_id = f"{pdf_file.stem}_chunk_{i}"
            collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                metadatas=[{"source": pdf_file.name, "chunk_index": i}],
                documents=[chunk]
            )

            total_chunks += 1

            # Mostrar progresso a cada 10 chunks
            if (i + 1) % 10 == 0:
                print(f"   ⏳ {i + 1}/{len(chunks)} chunks processados", end="\r")

        print(f"   ✓ Todos os chunks processados")

    print(f"\n✅ Ingestão concluída! {total_chunks} chunks indexados.")


if __name__ == "__main__":
    ingest_pdfs()
