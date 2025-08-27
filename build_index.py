# build_index.py
# Build a FAISS index from the ICPC-2 CSV

import os, json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from icpc_utils import load_icpc_csv, to_entries, build_doc_text, save_meta

# -------- Configuration --------
CSV_PATH = os.environ.get("ICPC_CSV_PATH", "ICPC-2.csv")
EMB_MODEL = os.environ.get("EMB_MODEL", "intfloat/multilingual-e5-base")  # good multilingual baseline
INDEX_OUT = os.environ.get("INDEX_OUT", "icpc2.faiss")
META_OUT = os.environ.get("META_OUT", "icpc2_meta.json")
BATCH = int(os.environ.get("BATCH", "256"))
# --------------------------------

def main():
    print(f"Loading CSV: {CSV_PATH}")
    df = load_icpc_csv(CSV_PATH)
    entries = to_entries(df)
    docs = [build_doc_text(e) for e in entries]

    print(f"Loaded {len(entries)} ICPC-2 entries")

    print(f"Loading embedding model: {EMB_MODEL}")
    model = SentenceTransformer(EMB_MODEL)
    # E5 expects "passage: " prefix for document embeddings
    passages = [f"passage: {t}" for t in docs]

    print("Encoding passages...")
    vecs = model.encode(passages, batch_size=BATCH, show_progress_bar=True, convert_to_numpy=True, normalize_embeddings=True)

    # Build FAISS index (cosine via inner product on normalized vectors)
    d = vecs.shape[1]
    index = faiss.IndexFlatIP(d)
    index.add(vecs.astype(np.float32))

    print(f"Writing index -> {INDEX_OUT}")
    faiss.write_index(index, INDEX_OUT)

    print(f"Writing metadata -> {META_OUT}")
    save_meta(entries, META_OUT)

    print("Done.")

if __name__ == "__main__":
    main()
