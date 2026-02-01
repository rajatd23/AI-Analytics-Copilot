import os
import glob
import chromadb
from sentence_transformers import SentenceTransformer

DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")
DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

def chunk_text(text: str, chunk_size: int = 900, overlap: int = 150):
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i + chunk_size])
        i += chunk_size - overlap
    return [c.strip() for c in chunks if c.strip()]

def main():
    model = SentenceTransformer("all-MiniLM-L6-v2")

    client = chromadb.PersistentClient(path=DB_DIR)
    col = client.get_or_create_collection(name="analytics_kb")

    # Rebuild clean
    try:
        col.delete(where={})
    except Exception:
        pass

    idx = 0
    for path in glob.glob(os.path.join(DOCS_DIR, "*.*")):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()

        for chunk in chunk_text(text):
            emb = model.encode(chunk).tolist()
            col.add(
                ids=[str(idx)],
                documents=[chunk],
                metadatas=[{"source": os.path.basename(path)}],
                embeddings=[emb],
            )
            idx += 1

    print(f"✅ Indexed {idx} chunks into: {DB_DIR}")

if __name__ == "__main__":
    main()
