# Laporan UAS Kecerdasan Buatan

## Generasi Product Requirements Document (PRD) Otomatis Menggunakan Large Language Model dengan Evaluasi ROUGE

**Nama Kelompok:** Rizki Dzulfikar Al-Qatiri (2406118) & Naupal Nahban (2406119)
**Domain Proyek:** Natural Language Processing (NLP) — *Text Generation* & *Retrieval-Augmented Generation* (RAG)

---

## 1. Judul Proyek

**Generasi Otomatis Product Requirements Document (PRD) Menggunakan Llama 3.2 1B Instruct dengan Pendekatan Retrieval-Augmented Generation (RAG) dan Evaluasi ROUGE.**

Proyek ini membangun sistem yang menyusun PRD — dokumen yang menjembatani kebutuhan bisnis, pengguna, dan implementasi teknis — secara otomatis dari sebuah prompt produk. Domain utamanya adalah NLP untuk *text generation*. Sesuai ketentuan Panduan UAS (pemilihan minimal 2 algoritma/pendekatan untuk dibandingkan), proyek ini membandingkan dua pendekatan:

- **Model Utama** — Pendekatan **RAG** (*Retrieval-Augmented Generation*), diimplementasikan pada `Signature_model.ipynb`.
- **Model Pembanding** — Pendekatan **Tanpa RAG** (*direct prompt* / *zero-shot*), diimplementasikan pada `Comparison_model.ipynb`.

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

- **`data/dataset/`** — 6 dokumen PRD contoh yang telah dikurasi (e-commerce, fintech, healthtech, edtech, aplikasi keuangan, panduan PRD lengkap).
- **`data/prd_templates/`** — 5 *template* PRD (`master`, `startup`, `mobile`, `enterprise`, `data`).
- **ChromaDB (*vector store*)** — hasil *embedding* dokumen referensi (basis pengetahuan RAG).
- **`data/Jurnal/`** — 5 PDF jurnal referensi untuk landasan teori.

### 3.2 Deskripsi Setiap Fitur / Atribut

Dokumen PRD memiliki struktur sebagai berikut:

| Atribut | Deskripsi |
|---------|-----------|
| Judul | Nama dan domain produk (mis. E-Commerce B2B, Dompet Digital) |
| Ringkasan Eksekutif | Satu paragraf deskripsi produk dan nilai unik |
| Latar Belakang | Masalah yang ingin dipecahkan |
| Target Pengguna | Persona pengguna dan kebutuhannya |
| Fitur | Daftar fitur dengan prioritas P0/P1/P2 |
| Arsitektur Teknis | *Tech stack* yang digunakan |
| Non-Fungsional | Persyaratan performa, keamanan |
| Timeline | Jadwal pengembangan |

### 3.3 Ukuran dan Format Data

- **Format**: Markdown (`.md`).
- **Jumlah dokumen referensi lokal**: 6 dokumen.
- **Total karakter**: ~15.000 karakter (lihat visualisasi EDA, Gambar 1).
- **Setelah *chunking***: ~30–50 segmen per dokumen (800 karakter per segmen).

### 3.4 Tipe Data

Data berupa teks tidak terstruktur (*unstructured text*) dengan label domain berdasarkan nama file (e-commerce, fintech, healthtech, edtech, aplikasi keuangan, panduan). Tidak terdapat *label* klasifikasi; ini adalah tugas *text generation*, sehingga tidak ada *target class* seperti pada klasifikasi.

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
- Konversi PDF/DOCX/PPTX ke teks Markdown (pada *pipeline* lengkap yang mengambil dari Google Drive; untuk evaluasi digunakan 6 file `.md` lokal yang sudah bersih).
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

- **Basis pengetahuan / *reference* (train)**: 6 dokumen `data/dataset/` di-*embed* ke ChromaDB dan dijadikan acuan ROUGE.
- **Test / prompt**: prompt generasi PRD baru per domain (mis. "Buat PRD untuk aplikasi e-commerce"), yang dibandingkan dengan dokumen referensi domain yang sama.

---

## 6. Modeling

### 6.1 Pemilihan Algoritma / Pendekatan

Sesuai ketentuan (minimal 2 pendekatan untuk dibandingkan), dibandingkan dua pendekatan berbasis LLM yang sama (*Llama 3.2 1B Instruct*):

| Pendekatan | Peran | Deskripsi | Komponen |
|------------|-------|-----------|----------|
| **RAG** | **Model Utama** (`Signature_model.ipynb`) | LLM generate PRD **dengan** konteks dari *retrieval* | Llama 3.2 1B + ChromaDB + Embedding + Template `master` |
| **Tanpa RAG** | **Model Pembanding** (`Comparison_model.ipynb`) | LLM generate PRD **tanpa** konteks eksternal (direct prompt) | Llama 3.2 1B + Template `startup` (tanpa retrieval) |

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

**Model Utama — RAG (`Signature_model.ipynb`):**

```python
from chatbot import PRDChatbot
cb = PRDChatbot()
prompt = "Buat PRD untuk aplikasi e-commerce"
prd = cb.generate_prd(prompt, template_key="master")  # RAG: retrieve -> augment -> generate
```

*Pipeline*: `Query -> Embedding -> ChromaDB (top-3) -> Augment Prompt + Template -> Llama 3.2 1B -> PRD`.

**Model Pembanding — Tanpa RAG (`Comparison_model.ipynb`):**

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
| Waktu generasi | ~42-253 detik (termasuk *retrieval*) | ~42-47 detik |

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

**Referensi: Contoh PRD E-Commerce** (1.288 karakter)

| Metrik | Model Utama (RAG) P / R / F1 | Model Pembanding (No-RAG) P / R / F1 | Delta F1 |
|--------|------------------------------|---------------------------------------|----------|
| ROUGE-1 | 0.1734 / 0.3529 / **0.2326** | 0.0846 / 0.1941 / 0.1179 | +0.1147 |
| ROUGE-2 | 0.0754 / 0.1538 / **0.1012** | 0.0129 / 0.0296 / 0.0179 | +0.0833 |
| ROUGE-L | 0.1329 / 0.2706 / **0.1783** | 0.0641 / 0.1471 / 0.0893 | +0.0890 |

**Referensi: Contoh PRD Fintech** (2.161 karakter)

| Metrik | Model Utama (RAG) P / R / F1 | Model Pembanding (No-RAG) P / R / F1 | Delta F1 |
|--------|------------------------------|---------------------------------------|----------|
| ROUGE-1 | 0.1783 / 0.1879 / **0.1830** | 0.1294 / 0.1611 / 0.1435 | +0.0395 |
| ROUGE-2 | 0.0288 / 0.0303 / **0.0295** | 0.0216 / 0.0269 / 0.0240 | +0.0055 |
| ROUGE-L | 0.1051 / 0.1107 / **0.1078** | 0.0782 / 0.0973 / 0.0867 | +0.0211 |

**Referensi: Contoh PRD Healthtech** (1.228 karakter)

| Metrik | Model Utama (RAG) P / R / F1 | Model Pembanding (No-RAG) P / R / F1 | Delta F1 |
|--------|------------------------------|---------------------------------------|----------|
| ROUGE-1 | 0.2200 / 0.4639 / **0.2984** | 0.1621 / 0.3193 / 0.2150 | +0.0834 |
| ROUGE-2 | 0.0401 / 0.0848 / **0.0545** | 0.0215 / 0.0424 / 0.0285 | +0.0260 |
| ROUGE-L | 0.1029 / 0.2169 / **0.1395** | 0.0765 / 0.1506 / 0.1014 | +0.0381 |

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

**Model terbaik: Model Utama (RAG).**

Alasan:
1. **Semua metrik ROUGE lebih tinggi** dari Model Pembanding pada ketiga referensi - RAG konsisten meningkatkan Precision, Recall, dan F1.
2. **Recall meningkat tajam** (mis. ROUGE-1 Recall E-Commerce 0.3529 vs 0.1941) karena model mendapat contoh PRD nyata sehingga menangkap lebih banyak informasi domain target.
3. **ROUGE-L meningkat** - struktur kalimat lebih mirip referensi (pola PRD terjamah).
4. Peningkatan terbesar ada pada **ROUGE-1** (rata-rata Delta F1 ~ +0.079), menunjukkan RAG menambah kosakata relevan; **ROUGE-2** skor absolut terendah karena overlap *bigram* lebih sulit dicapai pada teks bebas.

---

## 8. Kesimpulan dan Rekomendasi

### 8.1 Ringkasan Hasil

Proyek berhasil mengimplementasikan pipeline **Retrieval-Augmented Generation** menggunakan **Llama 3.2 1B Instruct** untuk menghasilkan PRD otomatis (**Model Utama**), dan membandingkannya dengan pendekatan *baseline* **Tanpa RAG** (**Model Pembanding**). Evaluasi ROUGE dari eksekusi segar menunjukkan **Model Utama (RAG) secara konsisten unggul** di semua metrik dan semua referensi.

### 8.2 Apakah Tujuan Proyek Tercapai?

- ✅ Pipeline RAG berfungsi dan menghasilkan PRD terstruktur.
- ✅ Perbandingan dua pendekatan menunjukkan RAG unggul secara kuantitatif.
- ✅ Evaluasi ROUGE memberikan gambaran objektif kualitas output.
- ✅ Sistem dapat digunakan untuk berbagai domain produk.

### 8.3 Kelebihan dan Keterbatasan Model

| Kelebihan | Keterbatasan |
|-----------|--------------|
| PRD lebih kontekstual & relevan (RAG) | Dataset referensi terbatas (6 dokumen) |
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

- **Notebook Model Utama (RAG)**: `Signature_model.ipynb`
- **Notebook Model Pembanding (Tanpa RAG)**: `Comparison_model.ipynb`
- **Dataset referensi**: `data/dataset/` (6 dokumen PRD)
- **Template PRD**: `data/prd_templates/` (5 template)
- **Jurnal referensi**: `data/Jurnal/` (5 PDF)
- **ChromaDB**: *vector store* lokal (basis pengetahuan RAG)
- **Visualisasi ROUGE**: `data/dataset/rouge_comparison.png`
- **Visualisasi EDA**: `data/dataset/eda_dataset.png`
- **Contoh Output**: `output/prd_frozen_food_b2b.md`
