# UAS-KecerdasanBuatan — PRD Generator & Evaluasi ROUGE

## UAS Kecerdasan Buatan — Text Generation PRD dengan ROUGE Evaluation

### Topik
Generasi Product Requirements Document (PRD) Otomatis Menggunakan Large Language Model (Llama 3.2 1B Instruct) dengan Evaluasi ROUGE.

### Struktur File UAS

```
UAS-KecerdasanBuatan/
├── Laporan_uas.md           # Laporan UAS (10 section)
├── README.md
├── UAS_Model/
│   ├── Signature_model.ipynb    # Model Utama (RAG)
│   └── Comparison_model.ipynb   # Model Pembanding (Tanpa RAG)
└── data/
    ├── dataset/             # PRD referensi (6 dokumen)
    ├── prd_templates/       # 5 template PRD
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

> **Catatan:** Notebook mengimpor modul `App/` dan membutuhkan model `Model/` (keduanya **tidak diikutsertakan** dalam repositori ini karena batas ukuran GitHub). Hasil evaluasi ROUGE sudah dicatat lengkap di `Laporan_uas.md`.

### Referensi
- Lewis et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.
- Lin (2004). ROUGE: A Package for Automatic Evaluation of Summaries.
- Grattafiori et al. (2024). The Llama 3 Herd of Models.
- Kumar et al. (2024). ROUGE-SS: A New ROUGE Variant.
- Liu et al. (2024). How Reliable Are Automatic Evaluation Methods.
- Tanwir et al. (2026). RAG LLM-Based Chatbot for Stunting Prevention.
