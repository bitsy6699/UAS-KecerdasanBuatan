# Laporan UAS Kecerdasan Buatan

## Generasi Product Requirements Document (PRD) Otomatis Menggunakan Large Language Model dengan Evaluasi ROUGE

**Nama Kelompok:** Rizki Dzulfikar Al-Qatiri (2406118) & Naupal Nahban (2406119)
**Domain Proyek:** Natural Language Processing (NLP) — *Text Generation* & *Retrieval-Augmented Generation* (RAG)

---

## 1. Judul Proyek

**Generasi Otomatis Product Requirements Document (PRD) Menggunakan LLM (Llama via Groq cloud) dengan Pendekatan Retrieval-Augmented Generation (RAG) dan Evaluasi ROUGE.**

Proyek ini membangun sistem yang menyusun PRD — dokumen yang menjembatani kebutuhan bisnis, pengguna, dan implementasi teknis — secara otomatis dari sebuah prompt produk. Domain utamanya adalah NLP untuk *text generation*. Sesuai ketentuan Panduan UAS (pemilihan minimal 2 algoritma/pendekatan untuk dibandingkan), proyek ini membandingkan dua pendekatan:

- **Model Utama** — Pendekatan **RAG** (*Retrieval-Augmented Generation*), diimplementasikan pada `UAS_Model/Signature_model.ipynb`.
- **Model Pembanding** — Pendekatan **Tanpa RAG** (*direct prompt* / *zero-shot*), diimplementasikan pada `UAS_Model/Comparison_model.ipynb`.

Kedua model menggunakan LLM yang sama (**Groq cloud `llama-3.1-8b-instant`** — 8B, tanpa beban lokal). Satu-satunya variabel yang dibandingkan adalah **ada tidaknya tahap *retrieval*** dari basis pengetahuan.

---

## 2. Business Understanding

### 2.1 Permasalahan Dunia Nyata

Penulisan *Product Requirements Document* (PRD) merupakan tahapan kritis dalam siklus pengembangan produk, namun memakan waktu berjam-jam hingga berhari-hari karena membutuhkan riset referensi, pemahaman domain, dan struktur dokumen yang sesuai standar (Tanwir et al., 2026). Banyak *product manager* dan tim pengembang kesulitan menghasilkan PRD yang konsisten, terstruktur, dan mengikuti *best practice* industri.

Dalam literatur, *Retrieval-Augmented Generation* (RAG) terbukti meningkatkan kualitas keluaran LLM dengan menyediakan konteks eksternal yang relevan (Lewis et al., 2020). Pendekatan ini memungkinkan model tidak hanya mengandalkan parameter internal, tetapi juga mengambil informasi dari basis pengetahuan yang selalu dapat diperbarui.

### 2.2 Tujuan Proyek

1. Mengimplementasikan pipeline RAG (**Model Utama**) untuk menghasilkan PRD otomatis menggunakan LLM cloud (Groq `llama-3.1-8b-instant`).
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

- **`data/dataset/`** — 7 dokumen PDF yang dipindah dari Google Drive: *Sistem Manajemen Cafe*, *Sistem Koperasi*, *Sistem Inventaris Gudang*, *Sistem Absensi Mahasiswa*, *Sistem Manajemen Kelompok*, *Sistem Peminjaman Alat Camping*, dan *Product Requirement Document* (dijadikan basis pengetahuan RAG dan referensi ROUGE).
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

- **Format**: PDF (`.pdf`) dari Google Drive, teks diekstrak langsung saat *ingestion* (tanpa file `.md` perantara).
- **Jumlah dokumen referensi**: 7 dokumen PDF.
- **Total karakter**: ~250.000 karakter hasil konversi PDF (lihat visualisasi EDA, Gambar 1).
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
- Ekstrak teks langsung dari PDF/DOCX/PPTX (tanpa file `.md` perantara; terdapat 7 dokumen PDF dari Google Drive — *Sistem Manajemen Cafe*, *Sistem Koperasi*, *Sistem Inventaris Gudang*, *Sistem Absensi Mahasiswa*, *Sistem Manajemen Kelompok*, *Sistem Peminjaman Alat Camping*, *Product Requirement Document* — yang teksnya diekstrak lalu di-chunk).
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

- **Basis pengetahuan / *reference* (train)**: 7 dokumen PDF `data/dataset/` di-*embed* ke ChromaDB dan dijadikan acuan ROUGE.
- **Test / prompt**: prompt generasi PRD baru per domain (mis. "Buat PRD untuk aplikasi e-commerce"), yang dibandingkan dengan dokumen referensi domain yang sama.

---

## 6. Modeling

### 6.1 Pemilihan Algoritma / Pendekatan

Sesuai ketentuan (minimal 2 pendekatan untuk dibandingkan), dibandingkan dua pendekatan berbasis LLM (Groq cloud `llama-3.1-8b-instant`):

| Pendekatan | Peran | Deskripsi | Komponen |
|------------|-------|-----------|----------|
| **RAG** | **Model Utama** (`UAS_Model/Signature_model.ipynb`) | LLM generate PRD **dengan** konteks dari *retrieval* | Groq cloud (8B) + ChromaDB + Embedding |
| **Tanpa RAG** | **Model Pembanding** (`UAS_Model/Comparison_model.ipynb`) | LLM generate PRD **tanpa** konteks eksternal (direct prompt) | Groq cloud (8B) tanpa retrieval |

### 6.2 Alasan Pemilihan

**Groq cloud `llama-3.1-8b-instant`** (8B):
- Model 8B dari Meta yang diakses via API Groq — tanpa beban inferensi lokal.
- Cepat (1–16 detik per generasi) dan tidak membutuhkan GPU/CPU berat.
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
prd = cb.generate_prd(prompt)  # RAG: retrieve -> augment -> generate (cloud)
```

*Pipeline*: `Query -> Embedding -> ChromaDB (top-3) -> Augment Prompt -> Groq API (8B) -> PRD`.

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
| Waktu generasi | ~1-16 detik (cloud API) | ~1-9 detik (cloud API) |

### 6.5 Visualisasi Model

```
[Query User] -> [Embedding] -> [ChromaDB: Semantic Search] -> [Top-3 Chunks]
                                                                |
[Template / Konteks] ---------------------------------------------> [Prompt Builder]
                                                                 |
[Model Utama: Groq cloud (8B)] <- [Augmented Prompt w/ Context]
                                     vs
[Model Pembanding: Groq cloud (8B)] <- [Prompt tanpa Context]
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

Setiap metrik dihitung dalam tiga varian: **Precision** (proporsi output yang ada di referensi), **Recall** (proporsi referensi yang muncul di output), dan **F1** (*harmonic mean* keduanya). Generasi bersifat non-deterministik, sehingga angka berikut diambil dari **eksekusi ulang yang segar** (*fresh run*) pada ketujuh dokumen referensi.

### 7.2 Hasil per Referensi

**Referensi: Sistem Manajemen Cafe** (42.306 karakter)

| Metrik | Model Utama (RAG) P / R / F1 | Model Pembanding (No-RAG) P / R / F1 | Delta F1 |
|--------|------------------------------|---------------------------------------|----------|
| ROUGE-1 | 0.8365 / 0.0449 / **0.0853** | 0.7165 / 0.0397 / 0.0752 | +0.0101 |
| ROUGE-2 | 0.3691 / 0.0198 / **0.0375** | 0.0887 / 0.0049 / 0.0093 | +0.0282 |
| ROUGE-L | 0.5723 / 0.0307 / **0.0584** | 0.3659 / 0.0203 / 0.0384 | +0.0199 |

**Referensi: Sistem Koperasi** (37.575 karakter)

| Metrik | Model Utama (RAG) P / R / F1 | Model Pembanding (No-RAG) P / R / F1 | Delta F1 |
|--------|------------------------------|---------------------------------------|----------|
| ROUGE-1 | 0.7199 / 0.0393 / **0.0745** | 0.6109 / 0.0346 / 0.0655 | +0.0089 |
| ROUGE-2 | 0.1957 / 0.0106 / **0.0202** | 0.0959 / 0.0054 / 0.0103 | +0.0099 |
| ROUGE-L | 0.4468 / 0.0244 / **0.0462** | 0.3447 / 0.0195 / 0.0370 | +0.0092 |

**Referensi: Sistem Inventaris Gudang** (33.129 karakter)

| Metrik | Model Utama (RAG) P / R / F1 | Model Pembanding (No-RAG) P / R / F1 | Delta F1 |
|--------|------------------------------|---------------------------------------|----------|
| ROUGE-1 | 0.8608 / 0.0611 / **0.1140** | 0.7589 / 0.0572 / 0.1064 | +0.0076 |
| ROUGE-2 | 0.4032 / 0.0285 / **0.0533** | 0.2239 / 0.0168 / 0.0313 | +0.0219 |
| ROUGE-L | 0.5032 / 0.0357 / **0.0667** | 0.4196 / 0.0316 / 0.0589 | +0.0078 |

**Referensi: Sistem Absensi Mahasiswa** (38.485 karakter)

| Metrik | Model Utama (RAG) P / R / F1 | Model Pembanding (No-RAG) P / R / F1 | Delta F1 |
|--------|------------------------------|---------------------------------------|----------|
| ROUGE-1 | 0.7705 / 0.0467 / **0.0880** | 0.7079 / 0.0500 / 0.0935 | −0.0055 |
| ROUGE-2 | 0.3125 / 0.0189 / **0.0356** | 0.2620 / 0.0185 / 0.0345 | +0.0011 |
| ROUGE-L | 0.4918 / 0.0298 / **0.0562** | 0.4101 / 0.0290 / 0.0542 | +0.0020 |

**Referensi: Sistem Manajemen Kelompok** (37.575 karakter)

| Metrik | Model Utama (RAG) P / R / F1 | Model Pembanding (No-RAG) P / R / F1 | Delta F1 |
|--------|------------------------------|---------------------------------------|----------|
| ROUGE-1 | 0.9283 / 0.0576 / **0.1085** | 0.7346 / 0.0509 / 0.0952 | +0.0134 |
| ROUGE-2 | 0.5250 / 0.0325 / **0.0612** | 0.2157 / 0.0149 / 0.0279 | +0.0333 |
| ROUGE-L | 0.6417 / 0.0398 / **0.0750** | 0.4078 / 0.0282 / 0.0528 | +0.0222 |

**Referensi: Sistem Peminjaman Alat Camping** (43.132 karakter)

| Metrik | Model Utama (RAG) P / R / F1 | Model Pembanding (No-RAG) P / R / F1 | Delta F1 |
|--------|------------------------------|---------------------------------------|----------|
| ROUGE-1 | 0.8394 / 0.0384 / **0.0735** | 0.7901 / 0.0428 / 0.0812 | −0.0077 |
| ROUGE-2 | 0.4176 / 0.0191 / **0.0364** | 0.2012 / 0.0109 / 0.0206 | +0.0158 |
| ROUGE-L | 0.4818 / 0.0221 / **0.0422** | 0.4352 / 0.0236 / 0.0447 | −0.0025 |

**Referensi: Product Requirement Document** (18.500 karakter)

| Metrik | Model Utama (RAG) P / R / F1 | Model Pembanding (No-RAG) P / R / F1 | Delta F1 |
|--------|------------------------------|---------------------------------------|----------|
| ROUGE-1 | 0.7626 / 0.0837 / **0.1508** | 0.5132 / 0.0612 / 0.1093 | +0.0415 |
| ROUGE-2 | 0.1588 / 0.0174 / **0.0313** | 0.0565 / 0.0067 / 0.0120 | +0.0193 |
| ROUGE-L | 0.3813 / 0.0418 / **0.0754** | 0.2583 / 0.0308 / 0.0550 | +0.0204 |

### 7.3 Visualisasi Perbandingan

![ROUGE Comparison](data/dataset/rouge_comparison.png)

*Gambar 2. Perbandingan ROUGE F1-score: Model Utama (RAG, hijau) vs Model Pembanding (Tanpa RAG, merah) pada ketujuh referensi.*

### 7.4 Confusion Matrix (Konteks)

Untuk *text generation*, *confusion matrix* tidak berlaku langsung seperti klasifikasi. Namun ROUGE dapat dipetakan ke konsep serupa:

- **True Positive (TP)**: *n-gram* yang muncul di kedua teks (output AI dan referensi).
- **False Positive (FP)**: *n-gram* di output AI tetapi tidak di referensi.
- **False Negative (FN)**: *n-gram* di referensi tetapi tidak di output AI.

Precision = TP / (TP + FP), Recall = TP / (TP + FN), F1 = 2*P*R / (P + R).

### 7.5 Penjelasan Kinerja Model - Model Terbaik

**Model utama: Model Utama (RAG)** tetap dipertahankan sebagai solusi utama karena PRD yang dihasilkan *grounded* pada dokumen domain (7 sistem: Cafe, Koperasi, Gudang, Absensi, Kelompok, Peminjaman, Product Requirement) melalui *retrieval*, sehingga lebih spesifik dan dapat dilacak ke sumber.

Pada evaluasi ROUGE kali ini dengan **7 dokumen referensi PDF** (18.500–43.132 karakter, jauh lebih besar dari output ~2.500–2.900 karakter), gambarannya lebih bernuansa:

1. **ROUGE-2 (bigram) konsisten meningkat pada RAG di seluruh 7 sistem** — Delta F1 positif pada semua sistem (+0.0011 hingga +0.0333). Ini adalah bukti terkuat bahwa RAG meningkatkan kemiripan frasa/struktur dengan konteks yang di-*retrieve*. Sistem Manajemen Kelompok mencatat delta tertinggi (+0.0333), disusul Cafe (+0.0282) dan Gudang (+0.0219).
2. **ROUGE-1**: RAG unggul pada 5 dari 7 sistem (Cafe, Koperasi, Gudang, Kelompok, Product Requirement). Peningkatan terbesar pada Product Requirement Document (+0.0415) — dokumen dengan referensi terpendek (18.500 karakter), paling dekat dengan panjang output. Sedikit penurunan pada Absensi (−0.0055) dan Peminjaman (−0.0077).
3. **ROUGE-L** (struktur kalimat): RAG unggul pada 5 dari 7 sistem dengan delta +0.0020 hingga +0.0222. Satu sistem (Peminjaman) menunjukkan delta−0.0025 yang dapat diabaikan.

**Kesimpulan:** RAG memberikan nilai tambah yang konsisten pada kemiripan *bigram* (struktur/frasa) di semua sistem, dan secara umum meningkatkan ROUGE-1/L pada mayoritas sistem. Manfaat RAG paling terlihat ketika panjang referensi mendekati panjang output (Product Requirement Document). Untuk evaluasi yang lebih adil, tetap disarankan membandingkan terhadap *reference* PRD yang sepanjang dengan output (lihat Rekomendasi).

---

## 8. Kesimpulan dan Rekomendasi

### 8.1 Ringkasan Hasil

Proyek berhasil mengimplementasikan pipeline **Retrieval-Augmented Generation** menggunakan **Groq cloud llama-3.1-8b-instant** untuk menghasilkan PRD otomatis (**Model Utama**), dan membandingkannya dengan pendekatan *baseline* **Tanpa RAG** (**Model Pembanding**). Evaluasi ROUGE dari eksekusi segar pada **7 dokumen PDF** (Cafe, Koperasi, Gudang, Absensi, Kelompok, Peminjaman, Product Requirement) menunjukkan **RAG secara konsisten meningkatkan ROUGE-2 (bigram/struktur)** di seluruh 7 sistem (Delta +0.0011 hingga +0.0333). ROUGE-1 dan ROUGE-L juga meningkat pada mayoritas sistem (5 dari 7) — pengaruh RAG paling kuat pada dokumen dengan referensi lebih pendek (Product Requirement Document, +0.0415).

### 8.2 Apakah Tujuan Proyek Tercapai?

- ✅ Pipeline RAG berfungsi dan menghasilkan PRD terstruktur.
- ✅ Perbandingan dua pendekatan menunjukkan RAG unggul secara kuantitatif.
- ✅ Evaluasi ROUGE memberikan gambaran objektif kualitas output.
- ✅ Sistem dapat digunakan untuk berbagai domain produk.

### 8.3 Kelebihan dan Keterbatasan Model

| Kelebihan | Keterbatasan |
|-----------|--------------|
| PRD lebih kontekstual & relevan (RAG) | Dataset referensi terbatas (7 dokumen PDF) |
| Pipeline modular & mudah dikustomisasi | Cloud API memerlukan koneksi internet |
| Referensi dapat diperbarui tanpa *retrain* | ROUGE tidak mengukur kualitas semantik penuh |
| Template fleksibel (5 varian) | Waktu generasi RAG lebih lama (termasuk *retrieval*) |

### 8.4 Rekomendasi Perbaikan

1. **Dataset lebih besar** - kumpulkan lebih banyak contoh PRD dari berbagai domain.
2. **Fine-tuning** - *fine-tune* Llama dengan dataset PRD (mis. LoRA) untuk pemahaman domain lebih baik.
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
- **Dataset referensi**: `data/dataset/` (7 dokumen PDF)
- **Jurnal referensi**: `data/Jurnal/` (5 PDF)
- **ChromaDB**: *vector store* (basis pengetahuan RAG)
- **Visualisasi ROUGE**: `data/dataset/rouge_comparison.png` (dihasilkan `App/evaluate_dataset.py`)
- **Visualisasi EDA**: `data/dataset/eda_dataset.png` (dihasilkan `App/evaluate_dataset.py`)
- **Contoh Output**: `output/prd_rag_buat_prd_lengkap_untuk_sistem_absensi_mahasiswa.md`
