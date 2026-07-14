# Panduan Lengkap Menulis Product Requirements Document (PRD)

## Apa itu PRD?
Product Requirements Document (PRD) adalah dokumen teknis yang menjelaskan secara detail tentang produk yang akan dibangun. PRD menjembatani antara kebutuhan bisnis, kebutuhan pengguna, dan implementasi teknis.

## Perbedaan PRD vs Dokumen Lain
- **PRD vs BRD**: BRD (Business Requirements Document) fokus pada kebutuhan bisnis. PRD fokus pada solusi produk.
- **PRD vs SRS**: SRS (Software Requirements Specification) lebih teknis dan detail. PRD lebih ke konsep dan fitur.
- **PRD vs FRD**: FRD (Functional Requirements Document) hanya berisi kebutuhan fungsional, tidak mencakup aspek bisnis.

## 5 Aspek Utama PRD
1. Tujuan Produk — kenapa produk ini harus ada?
2. Fitur + User Story + Acceptance Criteria — apa yang dibangun dan kriteria sukses
3. Flow & Catatan Desain UX — bagaimana user berinteraksi
4. Sistem & Environment Requirements — tech stack dan constraints
5. Asumsi, Kendala & Ketergantungan — apa yang kita asumsikan dan dependensi

## Struktur PRD yang Baik
### 1. Ringkasan Eksekutif
Satu paragraf yang menjelaskan produk, target pengguna, dan nilai unik. Bisa dibaca dalam 30 detik.

### 2. Latar Belakang & Problem Statement
Jelaskan masalah yang ingin dipecahkan. Sertakan data jika ada. Gunakan format: "Saat ini [siapa] mengalami [masalah] karena [alasan]. Dampaknya adalah [dampak]."

### 3. Tujuan Produk
Tujuan yang SMART (Specific, Measurable, Achievable, Relevant, Time-bound). Contoh: "Meningkatkan retensi pengguna dari 40% menjadi 60% dalam 3 bulan."

### 4. Target Pengguna & Persona
Buat 1-3 persona. Setiap persona punya: nama, demografi, pain point, behaviour, tech literacy.

### 5. Fitur & Prioritas
Gunakan prioritas P0/P1/P2:
- P0 (Must Have): Fitur kritis untuk launch
- P1 (Should Have): Penting tapi bisa menyusul
- P2 (Nice to Have): Setelah stabil

### 6. User Stories
Format: "Sebagai [peran], saya ingin [aksi] agar [benefit]."
Contoh: "Sebagai pengguna, saya ingin memfilter transaksi berdasarkan tanggal agar mudah mencari pengeluaran bulan lalu."

### 7. Acceptance Criteria
Syarat yang harus dipenuhi agar fitur dianggap selesai. Harus bisa diuji (testable).

## Do's & Don'ts

### DO's
- Gunakan bahasa yang jelas dan tidak ambigu
- Sertakan data dan referensi
- Libatkan stakeholder sejak awal
- Update dokumen secara berkala
- Gunakan format yang konsisten

### DON'Ts
- Jangan gunakan jargon yang tidak perlu
- Jangan buat asumsi tanpa validasi
- Jangan terlalu detail ke implementasi teknis (itu tugas SRS)
- Jangan skip bagian risiko
- Jangan lupa minta approval

## Tools untuk PRD
- Confluence / Notion / Google Docs: untuk kolaborasi
- Figma / Sketch: untuk wireframe dan mockup
- Jira / Linear: untuk tracking fitur ke task
- Miro / Whimsical: untuk user flow dan diagram
