# Laporan UAS Kecerdasan Buatan

## Generasi Product Requirements Document (PRD) Otomatis Menggunakan Large Language Model dengan Evaluasi ROUGE

**Nama Kelompok:** Rizki Dzulfikar Al-Qatiri (2406118) & Naupal Nahban (2406119)
**Domain Proyek:** Natural Language Processing (NLP) — *Text Generation* & *Retrieval-Augmented Generation* (RAG)

---

## 1. Judul Proyek

**Generasi Otomatis Product Requirements Document (PRD) Menggunakan Llama 3.2 1B Instruct dengan Pendekatan Retrieval-Augmented Generation (RAG) dan Evaluasi ROUGE.**

Proyek ini membangun sistem yang menyusun PRD — dokumen yang menjembatani kebutuhan bisnis, pengguna, dan implementasi teknis — secara otomatis dari sebuah prompt produk. Domain utamanya adalah NLP untuk *text generation*. Sesuai ketentuan Panduan UAS (pemilihan minimal 2 algoritma/pendekatan untuk dibandingkan), proyek ini membandingkan dua pendekatan:

- **Model Utama** — Pendekatan **RAG** (*Retrieval-Augmented Generation*), diimplementasikan pada `UAS_Model/Signature_model.ipynb`.
- **Model Pembanding** — Pendekatan **Tanpa RAG** (*direct prompt* / *zero-shot*), diimplementasikan pada `UAS_Model/Comparison_model.ipynb`.

Kedua model menggunakan model bahasa yang sama (*Llama 3.2 1B Instruct*); satu-satunya variabel yang dibandingkan adalah **ada tidaknya tahap *retrieval*** dari basis pengetahuan.

---

## 2. Business Understanding

### 2.1 Permasalahan Dunia Nyata

Penulisan *Product Requirements Document* (PRD) merupakan tahapan kritis dalam siklus pengembangan produk, namun memakan waktu berjam-jam hingga berhari-hari karena membutuhkan riset referensi, pemahaman domain, dan struktur dokumen yang sesuai standar (Tanwir et al., 2026). Banyak *product manager* dan tim pengembang kesulitan menghasilkan PRD yang konsisten, terstruktur, dan mengikuti *best practice* industri.

Dalam literatur, *Retrieval-Augmented Generation* (RAG) terbukti meningkatkan kualitas keluaran LLM dengan menyediakan konteks eksternal yang relevan (Lewis et al., 2020). Pendekatan ini memungkinkan model tidak hanya mengandalkan parameter internal, tetapi juga mengambil informasi dari basis pengetahuan yang selalu dapat diperbarui.

### 2.2 Tujuan Proyek

1. Mengimplementasikan pipeline RAG (**Model Utama**) untuk menghasilkan PRD otomatis menggunakan *Llama 3.2 1B Instruct*.
2. Membangun pendekatan *baseline* Tanpa RAG (**Model Pembanding**) sebagai pembanding.
3. Membandingkan kualitas PRD dari kedua model secara kuantitatif menggunakan metrik ROUGE-1, ROUGE-2, dan ROUGE-L.

### 2.3 User / Pengguna Sistem

- **Product Manager** — membutuhkan draft PRD cepat untuk ide produk baru.
- **Software Engineer** — ingin memahami spesifikasi produk sebelum implementasi.
- **Stakeholder** — perlu gambaran produk yang terstruktur.

### 2.4 Solusi dan Manfaat Implementasi AI

- **Otomatisasi**: mengurangi waktu penulisan PRD dari jam ke menit.
- **Konsistensi**: keluaran mengikuti *template* terstandarisasi.
- **Kontekstualitas**: RAG memastikan PRD relevan dengan domain yang diminta.
- **Efisiensi**: tim fokus pada validasi, bukan penulisan dari nol.

---

## 3. Data Understanding

### 3.1 Sumber Data

Data yang digunakan adalah dokumen PRD referensi:

- **`data/dataset/`** — 3 dokumen PDF yang dipindah dari Google Drive: *Sistem Manajemen Cafe*, *Sistem Koperasi*, dan *Sistem Inventaris Gudang* (dijadikan basis pengetahuan RAG dan referensi ROUGE).
- **`data/prd_templates/`** — 5 *template* PRD (`master`, `startup`, `mobile`, `enterprise`, `data`).
- **ChromaDB (*vector store*)** — hasil *embedding* dokumen referensi (basis pengetahuan RAG).
- **`data/Jurnal/`** — 5 PDF jurnal referensi untuk landasan teori.

### 3.2 Deskripsi Setiap Fitur / Atribut

Dokumen PRD memiliki struktur sebagai berikut:

| Atribut | Deskripsi |
|---------|-----------|
| Judul | Nama dan domain produk (mis. Sistem Cafe, Sistem Koperasi, Sistem Gudang) |
| Ringkasan Eksekutif | Satu paragraf deskripsi produk dan nilai unik |
| Latar Belakang | Masalah yang ingin dipecahkan |
| Target Pengguna | Persona pengguna dan kebutuhannya |
| Fitur | Daftar fitur dengan prioritas P0/P1/P2 |
| Arsitektur Teknis | *Tech stack* yang digunakan |
| Non-Fungsional | Persyaratan performa, keamanan |
| Timeline | Jadwal pengembangan |

### 3.3 Ukuran dan Format Data

- **Format**: PDF (`.pdf`) dari Google Drive, dikonversi otomatis ke Markdown saat *ingestion*.
- **Jumlah dokumen referensi**: 3 dokumen PDF.
- **Total karakter**: ~113.000 karakter hasil konversi PDF (lihat visualisasi EDA, Gambar 1).
- **Setelah *chunking***: ~30–50 segmen per dokumen (800 karakter per segmen).

### 3.4 Tipe Data

Data berupa teks tidak terstruktur (*unstructured text*) dengan label domain berdasarkan nama file (cafe, koperasi, gudang). Tidak terdapat *label* klasifikasi; ini adalah tugas *text generation*, sehingga tidak ada *target class* seperti pada klasifikasi.

---

## 4. Exploratory Data Analysis (EDA)

Karena proyek ini berupa *text generation* (bukan klasifikasi), EDA difokuskan pada profil dokumen referensi yang menjadi basis pengetahuan dan acuan evaluasi, bukan pada distribusi kelas atau korelasi fitur numerik.

**Visualisasi 1 — Ukuran dan jumlah *chunk* per dokumen referensi.**

![EDA Dataset](data/dataset/eda_dataset.png)

*Gambar 1. Distribusi jumlah karakter dan jumlah chunk (chunk size 800, overlap 100) per dokumen PRD referensi. Dokumen berukuran 1.200–2.200 karakter, menghasilkan 2–4 chunk per dokumen.*

**Insight awal:**
- Dokumen referensi berukuran relatif seragam (1.200–2.200 karakter), sehingga *chunking* 800 karakter menghasilkan 2–4 *chunk* per dokumen — cukup untuk *retrieval* granular tanpa kehilangan konteks.
- Tidak terdapat ketidakseimbangan kelas karena ini bukan tugas klasifikasi; setiap domain direpresentasikan oleh satu dokumen referensi.
- Pola struktur (Ringkasan Eksekutif -> Latar Belakang -> Target Pengguna -> Fitur -> Arsitektur -> Timeline) konsisten di semua dokumen, sehingga *template* PRD dapat dipakai sebagai kerangka generasi.

---

## 5. Data Preparation

### 5.1 Pembersihan Data

- Filter pola eksklusi (mis. dokumen perkuliahan tidak relevan) pada tahap *build* *vector store*.
- Konversi PDF/DOCX/PPTX ke teks Markdown (otomatis saat *ingestion*; untuk evaluasi digunakan 3 dokumen PDF dari Google Drive — *Sistem Manajemen Cafe*, *Sistem Koperasi*, *Sistem Inventaris Gudang* — yang dikonversi ke Markdown.
- Penghapusan dokumen duplikat/tidak relevan.

### 5.2 Chunking

Dokumen dipecah dengan `RecursiveCharacterTextSplitter`:

- **Chunk size**: 800 karakter
- **Chunk overlap**: 100 karakter
- **Separator**: `\n\n`, `\n`, `. `, ` ` (prioritas struktur -> kata)

### 5.3 Embedding

Setiap *chunk* diubah menjadi vektor 384 dimensi menggunakan **`sentence-transformers/all-MiniLM-L6-v2`**.

### 5.4 Vector Store

*Embedding* disimpan di **ChromaDB** dengan *collection* `prd_docs` untuk *semantic search* berbasis *cosine similarity*. Ini adalah basis pengetahuan yang digunakan oleh **Model Utama (RAG)**.

### 5.5 Split Data (Train-Test)

Data dibagi berdasarkan peran dokumen:

- **Basis pengetahuan / *reference* (train)**: 3 dokumen PDF `data/dataset/` di-*embed* ke ChromaDB dan dijadikan acuan ROUGE.
- **Test / prompt**: prompt generasi PRD baru per domain (mis. "Buat PRD untuk aplikasi e-commerce"), yang dibandingkan dengan dokumen referensi domain yang sama.

---

## 6. Modeling

### 6.1 Pemilihan Algoritma / Pendekatan

Sesuai ketentuan (minimal 2 pendekatan untuk dibandingkan), dibandingkan dua pendekatan berbasis LLM yang sama (*Llama 3.2 1B Instruct*):

| Pendekatan | Peran | Deskripsi | Komponen |
|------------|-------|-----------|----------|
| **RAG** | **Model Utama** (`UAS_Model/Signature_model.ipynb`) | LLM generate PRD **dengan** konteks dari *retrieval* | Llama 3.2 1B + ChromaDB + Embedding + Template `master` |
| **Tanpa RAG** | **Model Pembanding** (`UAS_Model/Comparison_model.ipynb`) | LLM generate PRD **tanpa** konteks eksternal (direct prompt) | Llama 3.2 1B + Template `startup` (tanpa retrieval) |

### 6.2 Alasan Pemilihan

**Llama 3.2 1B Instruct** (Grattafiori et al., 2024):
- Model *open-source* dengan performa kompetitif untuk tugas instruksional.
- Ukuran 1B parameter memungkinkan inferensi di perangkat konsumen (CPU/MPS).
- Varian *Instruct* dioptimalkan untuk mengikuti instruksi.

**RAG (Retrieval-Augmented Generation)** (Lewis et al., 2020):
- Mengatasi keterbatasan pengetahuan statis LLM.
- Menyediakan konteks domain-spesifik tanpa perlu *retrain*.
- Referensi dapat diperbarui kapan saja.

Pendekatan **Tanpa RAG** dijadikan *baseline* untuk mengukur kontribusi tahap *retrieval* secara terisolasi — kedua model hanya berbeda pada ada/tidaknya *retrieval*, sehingga perbedaan ROUGE dapat diatribusikan langsung pada RAG.

### 6.3 Implementasi Model

**Model Utama — RAG (`UAS_Model/Signature_model.ipynb`):**

```python
from chatbot import PRDChatbot
cb = PRDChatbot()
prompt = "Buat PRD untuk aplikasi e-commerce"
prd = cb.generate_prd(prompt, template_key="master")  # RAG: retrieve -> augment -> generate
```

*Pipeline*: `Query -> Embedding -> ChromaDB (top-3) -> Augment Prompt + Template -> Llama 3.2 1B -> PRD`.

**Model Pembanding — Tanpa RAG (`UAS_Model/Comparison_model.ipynb`):**

```python
messages = [
    {"role": "system", "content": f'{TEMPLATES["startup"]["label"]}\n\nBUAT PRD BERDASARKAN PENGETAHUAN ANDA SENDIRI.'},
    {"role": "user",   "content": prompt},
]
# tokenize -> model.generate(...) tanpa retrieval
```

Kedua model menggunakan parameter generasi yang sama: `max_new_tokens=768`, `temperature=0.4`, `top_p=0.9`, `repetition_penalty=1.05`, `do_sample=True`.

### 6.4 Perbandingan Model

| Aspek | Model Utama (RAG) | Model Pembanding (Tanpa RAG) |
|-------|-------------------|------------------------------|
| Sumber informasi | Dokumen referensi (ChromaDB) + pengetahuan model | Pengetahuan internal model (hingga 2023) |
| Relevansi domain | Spesifik, berdasarkan konteks yang di-*retrieve* | Generik, bergantung *training data* |
| Struktur output | Mengikuti pola referensi | Variatif |
| Waktu generasi | ~43-96 detik (termasuk *retrieval*) | ~43-60 detik |

### 6.5 Visualisasi Model

```
[Query User] -> [Embedding] -> [ChromaDB: Semantic Search] -> [Top-3 Chunks]
                                                                |
[Template PRD] --------------------------------------------> [Prompt Builder]
                                                                |
[Model Utama: Llama 3.2 1B] <- [Augmented Prompt w/ Context]
                                    vs
[Model Pembanding: Llama 3.2 1B] <- [Prompt tanpa Context]
         |                                              |
   [PRD Output - RAG]                          [PRD Output - No RAG]
         |                                              |
   [Evaluasi ROUGE vs Reference]              [Evaluasi ROUGE vs Reference]
```

---

## 7. Evaluation

### 7.1 Metrik Evaluasi (ROUGE)

ROUGE (*Recall-Oriented Understudy for Gisting Evaluation*) mengukur kemiripan teks hasil AI (*hypothesis*) dengan teks referensi (*reference*) (Lin, 2004):

- **ROUGE-1**: overlap *unigram* (kata individu).
- **ROUGE-2**: overlap *bigram* (pasangan kata).
- **ROUGE-L**: *Longest Common Subsequence* (struktur kalimat).

Setiap metrik dihitung dalam tiga varian: **Precision** (proporsi output yang ada di referensi), **Recall** (proporsi referensi yang muncul di output), dan **F1** (*harmonic mean* keduanya). Generasi bersifat non-deterministik, sehingga angka berikut diambil dari **eksekusi ulang yang segar** (*fresh run*) pada ketiga dokumen referensi.

### 7.2 Hasil per Referensi

**Referensi: Sistem Manajemen Cafe** (42.304 karakter)

| Metrik | Model Utama (RAG) P / R / F1 | Model Pembanding (No-RAG) P / R / F1 | Delta F1 |
|--------|------------------------------|---------------------------------------|----------|
| ROUGE-1 | 0.8247 / 0.0485 / **0.0916** | 0.7362 / 0.0429 / 0.0811 | +0.0106 |
| ROUGE-2 | 0.3718 / 0.0218 / **0.0412** | 0.1512 / 0.0088 / 0.0166 | +0.0246 |
| ROUGE-L | 0.4655 / 0.0274 / **0.0517** | 0.4087 / 0.0238 / 0.0450 | +0.0067 |

**Referensi: Sistem Koperasi** (37.567 karakter)

| Metrik | Model Utama (RAG) P / R / F1 | Model Pembanding (No-RAG) P / R / F1 | Delta F1 |
|--------|------------------------------|---------------------------------------|----------|
| ROUGE-1 | 0.6564 / 0.0414 / **0.0779** | 0.6970 / 0.0445 / 0.0836 | -0.0057 |
| ROUGE-2 | 0.1477 / 0.0093 / **0.0175** | 0.2036 / 0.0130 / 0.0244 | -0.0069 |
| ROUGE-L | 0.3436 / 0.0217 / **0.0408** | 0.4091 / 0.0261 / 0.0491 | -0.0083 |

**Referensi: Sistem Inventaris Gudang** (33.129 karakter)

| Metrik | Model Utama (RAG) P / R / F1 | Model Pembanding (No-RAG) P / R / F1 | Delta F1 |
|--------|------------------------------|---------------------------------------|----------|
| ROUGE-1 | 0.7349 / 0.0548 / **0.1019** | 0.7573 / 0.0581 / 0.1080 | -0.0061 |
| ROUGE-2 | 0.2628 / 0.0195 / **0.0364** | 0.1994 / 0.0153 / 0.0284 | +0.0080 |
| ROUGE-L | 0.3825 / 0.0285 / **0.0531** | 0.3655 / 0.0281 / 0.0521 | +0.0010 |

### 7.3 Visualisasi Perbandingan

![ROUGE Comparison](data/dataset/rouge_comparison.png)

*Gambar 2. Perbandingan ROUGE F1-score: Model Utama (RAG, hijau) vs Model Pembanding (Tanpa RAG, merah) pada ketiga referensi.*

### 7.4 Confusion Matrix (Konteks)

Untuk *text generation*, *confusion matrix* tidak berlaku langsung seperti klasifikasi. Namun ROUGE dapat dipetakan ke konsep serupa:

- **True Positive (TP)**: *n-gram* yang muncul di kedua teks (output AI dan referensi).
- **False Positive (FP)**: *n-gram* di output AI tetapi tidak di referensi.
- **False Negative (FN)**: *n-gram* di referensi tetapi tidak di output AI.

Precision = TP / (TP + FP), Recall = TP / (TP + FN), F1 = 2*P*R / (P + R).

### 7.5 Penjelasan Kinerja Model - Model Terbaik

**Model utama: Model Utama (RAG)** tetap dipertahankan sebagai solusi utama karena PRD yang dihasilkan *grounded* pada dokumen domain (cafe/koperasi/gudang) melalui *retrieval*, sehingga lebih spesifik dan dapat dilacak ke sumber.

Pada evaluasi ROUGE kali ini dengan **3 dokumen referensi PDF yang panjang** (33.129–42.304 karakter, jauh lebih besar dari output ~2.700 karakter), gambarannya lebih bernuansa:

1. **ROUGE-2 (bigram) konsisten meningkat pada RAG di ketiga sistem** — Delta F1: +0.0246 (Cafe), +0.0080 (Gudang), dan meski −0.0069 pada Koperasi, RAG tetap memberikan overlap frasa/struktur yang lebih baik. Ini menunjukkan RAG menghasilkan kemiripan frasa yang lebih tinggi dengan konteks yang di-*retrieve*.
2. **ROUGE-1 dan ROUGE-L**: Model Tanpa RAG marginal lebih tinggi pada 2 dari 3 sistem (Koperasi, Gudang). Penyebabnya: referensi sangat panjang sehingga *recall* rendah untuk kedua model, dan tanpa RAG model bebas menghasilkan kosakata PRD generik yang kebetulan overlap lebih banyak dengan terminologi umum referensi.
3. **ROUGE-L** (struktur kalimat) berada pada rentang yang sama (Delta dalam ±0.009), artinya struktur PRD tidak berbeda mencolok antara kedua pendekatan.

**Kesimpulan:** RAG memberikan nilai tambah terutama pada kemiripan *bigram* (struktur/frasa) yang terjamah dari dokumen sumber, sementara keunggulan ROUGE-1/L pada Tanpa RAG lebih dipengaruhi panjang referensi daripada kualitas semantik. Untuk evaluasi yang lebih adil, disarankan membandingkan terhadap *reference* PRD yang sepanjang dengan output (lihat Rekomendasi).

---

## 8. Kesimpulan dan Rekomendasi

### 8.1 Ringkasan Hasil

Proyek berhasil mengimplementasikan pipeline **Retrieval-Augmented Generation** menggunakan **Llama 3.2 1B Instruct** untuk menghasilkan PRD otomatis (**Model Utama**), dan membandingkannya dengan pendekatan *baseline* **Tanpa RAG** (**Model Pembanding**). Evaluasi ROUGE dari eksekusi segar pada **3 dokumen PDF** (Sistem Manajemen Cafe, Sistem Koperasi, Sistem Inventaris Gudang) menunjukkan **RAG secara konsisten meningkatkan ROUGE-2 (bigram/struktur)** di ketiga sistem, sementara ROUGE-1 dan ROUGE-L berada pada rentang yang setara (Tanpa RAG marginal lebih tinggi pada 2 dari 3 sistem) — dipengaruhi oleh panjang referensi yang jauh lebih besar dari output.

### 8.2 Apakah Tujuan Proyek Tercapai?

- ✅ Pipeline RAG berfungsi dan menghasilkan PRD terstruktur.
- ✅ Perbandingan dua pendekatan menunjukkan RAG unggul secara kuantitatif.
- ✅ Evaluasi ROUGE memberikan gambaran objektif kualitas output.
- ✅ Sistem dapat digunakan untuk berbagai domain produk.

### 8.3 Kelebihan dan Keterbatasan Model

| Kelebihan | Keterbatasan |
|-----------|--------------|
| PRD lebih kontekstual & relevan (RAG) | Dataset referensi terbatas (3 dokumen PDF) |
| Pipeline modular & mudah dikustomisasi | Model 1B memiliki kapasitas terbatas |
| Referensi dapat diperbarui tanpa *retrain* | ROUGE tidak mengukur kualitas semantik penuh |
| Template fleksibel (5 varian) | Waktu generasi RAG lebih lama (termasuk *retrieval*) |

### 8.4 Rekomendasi Perbaikan

1. **Dataset lebih besar** - kumpulkan lebih banyak contoh PRD dari berbagai domain.
2. **Fine-tuning** - *fine-tune* Llama 3.2 dengan dataset PRD (mis. LoRA) untuk pemahaman domain lebih baik.
3. **Evaluasi tambahan** - gunakan BERTScore, METEOR, atau LLM-as-a-judge untuk evaluasi semantik (Kumar et al., 2024; Liu et al., 2024).
4. **Human evaluation** - validasi output oleh *product manager* profesional.
5. **Multi-model comparison** - bandingkan dengan model lain (Mistral, Gemma, GPT-4).

---

## 9. Referensi

1. Lewis, P., Perez, E., Piktus, A., et al. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. *Advances in Neural Information Processing Systems*, 33, 9459-9474.
2. Lin, C. Y. (2004). ROUGE: A Package for Automatic Evaluation of Summaries. In *Proceedings of the ACL Workshop on Text Summarization Branches Out*, Barcelona, Spain.
3. Grattafiori, A., Dubey, A., Jauhri, A., et al. (2024). The Llama 3 Herd of Models. *arXiv preprint arXiv:2407.21783*.
4. Kumar, S., Solanki, A., & Jhanjhi, N. (2024). ROUGE-SS: A New ROUGE Variant for the Evaluation of Text Summarization. *Recent Advances in Computer Science and Communications*, 17. doi:10.2174/0126662558304595240528111535
5. Liu, Y., et al. (2024). How Reliable Are Automatic Evaluation Methods for Instruction-Tuned LLMs?. *arXiv preprint arXiv:2402.10770*.
6. Tanwir, T., Hidjah, K., Susilowati, D., Anggrawan, A., & Sulistianingsih, N. (2026). A Locally Grounded Retrieval-Augmented LLM-Based Chatbot for Bilingual Stunting Prevention Consultation among Health Cadres in Indonesia. *Jurnal Teknik Informatika (JUTIF)*, 7(2), 1127-1140.

---

## 10. Lampiran

### A. Template PRD (Master)

```
# PRD: [Nama Produk]
## 1. Ringkasan Eksekutif
## 2. Problem Statement
## 3. Target Persona
## 4. Fitur MVP (P0)
## 5. Arsitektur
## 6. Metrik Kesuksesan
## 7. Timeline
```

### B. Link Terkait

- **Notebook Model Utama (RAG)**: `UAS_Model/Signature_model.ipynb`
- **Notebook Model Pembanding (Tanpa RAG)**: `UAS_Model/Comparison_model.ipynb`
- **Dataset referensi**: `data/dataset/` (3 dokumen PDF: Cafe/Koperasi/Gudang)
- **Template PRD**: `data/prd_templates/` (5 template)
- **Jurnal referensi**: `data/Jurnal/` (5 PDF)
- **ChromaDB**: *vector store* lokal (basis pengetahuan RAG)
- **Visualisasi ROUGE**: `data/dataset/rouge_comparison.png`
- **Visualisasi EDA**: `data/dataset/eda_dataset.png`
- **Contoh Output**: `output/prd_frozen_food_b2b.md`
