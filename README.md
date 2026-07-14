<p align="center">
  <img src="data/dataset/eda_dataset.png" alt="EDA Dataset" width="600"/>
</p>

<h1 align="center">
  📄 UAS Kecerdasan Buatan
</h1>

<p align="center">
  <b>Generasi Product Requirements Document (PRD) Otomatis</b>
  —
  LLM + Retrieval-Augmented Generation + Evaluasi ROUGE
</p>

<p align="center">
  <img src="https://img.shields.io/badge/LLM-Llama_3.1_8B_(Groq_Cloud)-4ade80?style=flat-square" alt="LLM"/>
  <img src="https://img.shields.io/badge/Embedding-MiniLM_L6_v2-60a5fa?style=flat-square" alt="Embedding"/>
  <img src="https://img.shields.io/badge/RAG-ChromaDB-fbbf24?style=flat-square" alt="RAG"/>
  <img src="https://img.shields.io/badge/Evaluasi-ROUGE_1_2_L-f472b6?style=flat-square" alt="ROUGE"/>
  <img src="https://img.shields.io/badge/Backend-FastAPI-22c55e?style=flat-square" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Frontend-React-3b82f6?style=flat-square" alt="React"/>
</p>

<p align="center">
  <b>👤 Kelompok:</b>
  Rizki Dzulfikar Al-Qatiri (2406118) &amp; Naupal Nahban (2406119)
</p>

---

## 🎯 Ringkasan Proyek

Pipeline **RAG-based PRD Generator** yang memanfaatkan **Groq cloud (`llama-3.1-8b-instant`)** untuk menghasilkan Product Requirements Document secara otomatis berdasarkan 7 dokumen referensi PDF. Kualitas output dievaluasi menggunakan metrik **ROUGE-1/2/L**.

> **Dua pendekatan yang dibandingkan:**
> - 🅰️ **Tanpa RAG** — direct prompt, ngandalin pengetahuan internal LLM
> - 🅱️ **Dengan RAG** — retrieval dari ChromDB + konteks dokumen — **Model Utama**

---

## 🧱 Arsitektur

```
UAS-KecerdasanBuatan/
├── 📄 Laporan_uas.md               # Laporan UAS lengkap (10 section)
├── ⚙️ App/                          # Python source
│   ├── chatbot.py                  # LLM pipeline (Groq cloud)
│   ├── config.py                   # Konfigurasi path & model
│   ├── rag_builder.py              # Build ChromaDB vectorstore
│   ├── evaluate_dataset.py         # Evaluasi ROUGE (7 PDF)
│   ├── patch_notebooks.py          # Patch notebook: fix + inject
│   ├── backend/                    # FastAPI backend 🚀
│   └── frontend/                   # React frontend ⚛️
├── 📓 UAS_Model/
│   ├── Signature_model.ipynb       # Model Utama (Dengan RAG)
│   └── Comparison_model.ipynb      # Model Pembanding (Tanpa RAG)
├── 📚 data/
│   ├── dataset/                    # 7 PDF referensi + hasil evaluasi
│   └── Jurnal/                     # 5 referensi jurnal
├── 📂 output/                      # PRD hasil generate (ter-track)
└── 📦 requirements-cloud.txt
```

---

## 🚀 Pipeline

```
┌────────────────────┐     ┌────────────────────┐     ┌──────────────────────┐
│   Data Preparation │ ──▶ │     Modeling       │ ──▶ │  ROUGE Evaluation    │
│   Chunking (800)   │     │  Tanpa RAG / RAG   │     │  ROUGE-1, ROUGE-2,   │
│   Embedding (MiniLM)│     │  2 pendekatan      │     │  ROUGE-L             │
│   ChromDB          │     │                    │     │  + Visualisasi       │
└────────────────────┘     └────────────────────┘     └──────────────────────┘
```

---

## ⚡ Quick Start

```bash
# 1. Install dependensi
pip install -r requirements-cloud.txt

# 2. Setup API key Groq
cp .env.example .env
# → Isi LLM_API_KEY di .env (dapet dari https://console.groq.com/keys)

# 3. Bangun vectorstore dari 7 PDF referensi
python3 -m App.rag_builder

# 4. Jalanin notebook
jupyter notebook UAS_Model/Signature_model.ipynb      # Model Utama (RAG)
jupyter notebook UAS_Model/Comparison_model.ipynb     # Model Pembanding

# 5. Evaluasi ROUGE otomatis
python3 App/evaluate_dataset.py

# 6. Patch notebook (update markdown + inject hasil)
python3 App/patch_notebooks.py
```

---

## 🔧 Konfigurasi LLM

| Variabel | Default | Deskripsi |
|----------|---------|-----------|
| `LLM_BACKEND` | `cloud` | Groq cloud (satu-satunya mode 🎯) |
| `LLM_API_BASE` | `https://api.groq.com/openai/v1` | Endpoint OpenAI-compatible |
| `LLM_API_KEY` | — | API key ([console.groq.com](https://console.groq.com/keys)) |
| `LLM_API_MODEL` | `llama-3.1-8b-instant` | Model ID Groq |

**Contoh `.env`:**
```env
LLM_BACKEND=cloud
LLM_API_KEY=gsk_...
```

---

## 📊 Hasil Evaluasi

<p align="center">
  <img src="data/dataset/rouge_comparison.png" alt="ROUGE Comparison" width="700"/>
</p>

---

## 📖 Referensi

| # | Paper |
|---|-------|
| 1 | Lewis et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks* |
| 2 | Lin (2004). *ROUGE: A Package for Automatic Evaluation of Summaries* |
| 3 | Grattafiori et al. (2024). *The Llama 3 Herd of Models* |
| 4 | Kumar et al. (2024). *ROUGE-SS: A New ROUGE Variant* |
| 5 | Liu et al. (2024). *How Reliable Are Automatic Evaluation Methods* |
| 6 | Tanwir et al. (2026). *RAG LLM-Based Chatbot for Stunting Prevention* |
