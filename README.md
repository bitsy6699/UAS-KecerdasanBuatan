# UAS-KecerdasanBuatan — PRD Generator & Evaluasi ROUGE

## UAS Kecerdasan Buatan — Text Generation PRD dengan ROUGE Evaluation

### Topik
Generasi Product Requirements Document (PRD) Otomatis Menggunakan LLM (Llama via Groq cloud) dengan Evaluasi ROUGE.

### Struktur File UAS

 ```
UAS-KecerdasanBuatan/
├── Laporan_uas.md                 # Laporan UAS (10 section)
├── README.md
├── App/                           # All Python source & utilities
│   ├── chatbot.py                 #   LLM pipeline (cloud Groq)
│   ├── config.py                  #   Konfigurasi path & model
│   ├── rag_builder.py             #   Bangun ChromaDB vectorstore
│   ├── evaluate_dataset.py        #   Evaluasi ROUGE 7 PDF (hasilkan JSON + PNG)
│   ├── patch_notebooks.py         #   Patch notebook: fix markdown + inject output
│   ├── backend/                   #   FastAPI backend
│   └── frontend/                  #   React frontend
├── UAS_Model/
│   ├── Signature_model.ipynb      # Model Utama (RAG)
│   └── Comparison_model.ipynb     # Model Pembanding (Tanpa RAG)
├── data/
│   ├── dataset/                   # 7 dokumen PDF referensi
│   └── Jurnal/                    # 5 referensi jurnal
├── output/                        # PRD hasil generate (ter-track)
└── requirements-cloud.txt
```

### Pipeline
1. **Data Understanding** — PRD reference documents
2. **Data Preparation** — Chunking (800 chars), Embedding (MiniLM), ChromaDB
3. **ROUGE Evaluation** — ROUGE-1/2/L metric theory & implementation
4. **Modeling (2 Pendekatan)**:
   - Tanpa RAG (Direct Prompt)
   - Dengan RAG (Retrieval-Augmented Generation)
5. **Evaluation** — Perbandingan ROUGE scores
6. **Kesimpulan & Rekomendasi**

### Cara Menjalankan

```bash
# 1. Setup environment
pip install -r requirements-cloud.txt
cp .env.example .env
# Isi LLM_API_KEY di .env (jangan commit)

# 2. Build vectorstore (ChromaDB) dari data/dataset/
python3 -m App.rag_builder

# 3. Jalankan notebook (Model Utama & Model Pembanding)
jupyter notebook UAS_Model/Signature_model.ipynb
jupyter notebook UAS_Model/Comparison_model.ipynb

# 4. Evaluasi ROUGE otomatis
python3 App/evaluate_dataset.py

# 5. Patch notebook (update markdown + inject hasil evaluasi)
python3 App/patch_notebooks.py
```

> **Catatan:** Notebook mengimpor modul `App/`. ChromaDB (`App/backend/vectorstore/`) tidak diikutsertakan di git — bangun dengan `python3 -m App.rag_builder`. Hasil evaluasi ROUGE tercatat di `Laporan_uas.md`.

### Konfigurasi LLM

| Variabel | Default | Deskripsi |
|----------|---------|-----------|
| `LLM_BACKEND` | `cloud` | Groq cloud (satu-satunya mode) |
| `LLM_API_BASE` | `https://api.groq.com/openai/v1` | Endpoint OpenAI-compatible |
| `LLM_API_KEY` | — | API key ([console.groq.com](https://console.groq.com/keys)) |
| `LLM_API_MODEL` | `llama-3.1-8b-instant` | Model ID Groq |

**Contoh `.env`:**
```
LLM_BACKEND=cloud
LLM_API_KEY=gsk_...
```

### Referensi
- Lewis et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.
- Lin (2004). ROUGE: A Package for Automatic Evaluation of Summaries.
- Grattafiori et al. (2024). The Llama 3 Herd of Models.
- Kumar et al. (2024). ROUGE-SS: A New ROUGE Variant.
- Liu et al. (2024). How Reliable Are Automatic Evaluation Methods.
- Tanwir et al. (2026). RAG LLM-Based Chatbot for Stunting Prevention.
