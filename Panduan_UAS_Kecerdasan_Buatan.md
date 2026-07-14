# Instruksi Pengerjaan

Jawaban disusun dalam format **.md (Markdown)** dan diunggah ke **GitHub pribadi** (repository harus **public** dan link dapat diakses).

Lampirkan **link GitHub** pada kolom LMS.

## Struktur GitHub yang disarankan

```text
UAS-KecerdasanBuatan/
│── README.md
│── Laporan_uas.md (berisi laporan)
│── uas_model.ipynb
└── data/
    ├── dataset/
    └── Jurnal/
```

### Wajib mencantumkan

- Referensi jurnal ilmiah (**minimal 5**)
- Penjelasan langkah pengerjaan di **README.md**

# Struktur dan Isi Laporan UAS Kecerdasan Buatan

**Bobot Nilai: 100**

## 1. Judul Proyek

**Contoh:** _Prediksi Jenis Penyakit Tanaman Menggunakan Algoritma Decision Tree_

### Isi

- Nama Kelompok (maksimal 2 orang)
- Domain Proyek (Latar Belakang)

## 2. Business Understanding

### Isi

- Permasalahan dunia nyata dan literature review
- Tujuan proyek
- Siapa user/pengguna sistem
- Solusi dan manfaat implementasi AI

## 3. Data Understanding

### Isi

- Sumber data (Kaggle, simulasi, manual, sensor)
- Deskripsi setiap fitur (atribut)
- Ukuran dan format data
- Tipe data dan target klasifikasi

## 4. Exploratory Data Analysis (EDA)

### Isi

- Visualisasi distribusi data (histogram, bar chart, pie chart, dll.)
- Analisis korelasi antar fitur (heatmap, pairplot)
- Deteksi data tidak seimbang (_imbalanced classes_)
- Insight awal dari pola data

## 5. Data Preparation

### Isi

- Pembersihan data (null value, duplikasi)
- Encoding data kategorik (label encoding, one-hot encoding)
- Normalisasi/standardisasi data numerik
- Split data (train-test)

## 6. Modeling

### Isi

- Pemilihan algoritma minimal **2 algoritma** (Decision Tree, KNN, SVM, Naive Bayes, dll.)
- Alasan pemilihan 2 algoritma
- Implementasi model (dengan kode)
- Perbandingan model
- Visualisasi model (jika memungkinkan, misalnya pohon keputusan)

## 7. Evaluation

### Isi

- Confusion Matrix
- Metrik evaluasi:
  - Accuracy
  - Precision
  - Recall
  - F1-Score
- Penjelasan kinerja model berdasarkan metrik tersebut (**wajib menjelaskan model terbaik dan alasannya**)

## 8. Kesimpulan dan Rekomendasi

### Isi

- Ringkasan hasil modeling dan evaluasi
- Apakah tujuan proyek tercapai?
- Kelebihan dan keterbatasan model
- Rekomendasi perbaikan (dataset lebih besar, algoritma lain, dll.)

## 9. Referensi

### Isi

- Minimal **5 sumber ilmiah** (jurnal, buku, dokumentasi resmi) menggunakan gaya **APA**.
- Setiap pengertian atau teori yang ada di laporan harus memiliki sumber referensi.

## 10. Lampiran (Opsional)

### Isi

- Dataset mentah atau hasil olahan
- Grafik tambahan
