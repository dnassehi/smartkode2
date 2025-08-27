# ICPC-2 RAG Starter

## Quickstart
1) Place your CSV at: `/mnt/data/ICPC-2.csv` (or set `ICPC_CSV_PATH`).
2) Build the index:
```bash
pip install -r requirements.txt
python build_index.py
```
(Env vars: `ICPC_CSV_PATH`, `EMB_MODEL`, `INDEX_OUT`, `META_OUT`)

3) Run inference with a note:
```bash
# Set one of these:
export MISTRAL_API_KEY=...              # native Mistral
# or an OpenAI-compatible endpoint (e.g., OpenRouter):
export OPENAI_API_KEY=...
export OPENAI_BASE=https://openrouter.ai/api/v1
export OPENAI_MODEL=mistralai/mistral-large-latest

python rag_infer.py
```

## Files
- `icpc_utils.py` – CSV loader, component guessing, metadata helpers
- `build_index.py` – builds FAISS index from ICPC-2 CSV using multilingual E5 embeddings
- `rag_infer.py` – retrieves top-N ICPC-2 candidates and queries the LLM with a constrained prompt
- `prompt_template.txt` – documentation of the chat messages
- `requirements.txt` – Python deps

## Notes
- Component mapping for processkoder (30–69) kan variere nasjonalt. Denne pakken gjør en fornuftig gjetning (2,4,3,5 per tiår) og instruerer LLM-en til å bruke tittelteksten for presis komponent.
- Sørg for at all behandling skjer innenfor EØS og at notater er avidentifiserte for utvikling/testing.
