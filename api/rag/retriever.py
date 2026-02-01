import os
import chromadb
from sentence_transformers import SentenceTransformer

DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")

_model = None
_col = None

def _init():
    global _model, _col
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        client = chromadb.PersistentClient(path=DB_DIR)
        _col = client.get_or_create_collection(name="analytics_kb")

def retrieve_context(query: str, k: int = 4) -> str:
    _init()
    q_emb = _model.encode(query).tolist()
    res = _col.query(query_embeddings=[q_emb], n_results=k)

    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]

    blocks = []
    for d, m in zip(docs, metas):
        src = m.get("source", "doc")
        blocks.append(f"[{src}]\n{d}")
    return "\n\n".join(blocks).strip()
