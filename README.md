# UAS-KecerdasanBuatan — PRD Generator & Evaluasi ROUGE

## UAS Kecerdasan Buatan — Text Generation PRD dengan ROUGE Evaluation

### Topik
Generasi Product Requirements Document (PRD) Otomatis Menggunakan LLM (Llama via Groq cloud / lokal) dengan Evaluasi ROUGE.

### Struktur File UAS

```
UAS-KecerdasanBuatan/
├── Laporan_uas.md           # Laporan UAS (10 section)
├── README.md
├── UAS_Model/
│   ├── Signature_model.ipynb    # Model Utama (RAG)
│   └── Comparison_model.ipynb   # Model Pembanding (Tanpa RAG)
└── data/
    ├── dataset/             # 7 dokumen PDF (Cafe/Koperasi/Gudang/Absensi/Kelompok/Peminjaman/ProductReq) dari Google Drive
    └── Jurnal/              # Referensi jurnal (5 PDF)
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
# Jalankan notebook (Model Utama & Model Pembanding)
jupyter notebook UAS_Model/Signature_model.ipynb     # Model Utama (RAG)
jupyter notebook UAS_Model/Comparison_model.ipynb   # Model Pembanding (Tanpa RAG)
```

> **Catatan:** Notebook mengimpor modul `App/` dan membutuhkan chromaDB `Model/` (keduanya **tidak diikutsertakan** dalam repositori ini karena batas ukuran GitHub). Hasil evaluasi ROUGE sudah dicatat lengkap di `Laporan_uas.md`.
> 
> **LLM Backend:** Secara default generasi PRD menggunakan **Groq API (cloud)** — laptop tidak panas, model 8B. Untuk fallback lokal (tanpa internet), set `LLM_BACKEND=local` (lihat `.env.example`).

### Konfigurasi LLM Backend

Pipeline mendukung dua mode LLM:

| Variabel | Default | Deskripsi |
|----------|---------|-----------|
| `LLM_BACKEND` | `cloud` | `cloud` (Groq) atau `local` (PyTorch) |
| `LLM_API_BASE` | `https://api.groq.com/openai/v1` | Endpoint OpenAI-compatible |
| `LLM_API_KEY` | — | API key (dapatkan di [console.groq.com](https://console.groq.com/keys)) |
| `LLM_API_MODEL` | `llama-3.1-8b-instant` | Model ID (Groq: 8b, 70b) |

**Setup:**
```bash
pip install -r requirements-cloud.txt
cp .env.example .env
# Isi LLM_API_KEY di .env (jangan commit)
```

**Mode lokal** (tanpa internet):
- Set `LLM_BACKEND=local` di `.env`
- Pastikan model ada di `Model/llama/` (Llama 3.2 1B)
- Jalankan notebook seperti biasa (laptop akan panas)

### Referensi
- Lewis et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.
- Lin (2004). ROUGE: A Package for Automatic Evaluation of Summaries.
- Grattafiori et al. (2024). The Llama 3 Herd of Models.
- Kumar et al. (2024). ROUGE-SS: A New ROUGE Variant.
- Liu et al. (2024). How Reliable Are Automatic Evaluation Methods.
- Tanwir et al. (2026). RAG LLM-Based Chatbot for Stunting Prevention.
