# CONTOH PRD: Aplikasi Manajemen Keuangan Pribadi

## 1. Ringkasan Eksekutif
Aplikasi pencatatan keuangan pribadi dengan fitur budgeting otomatis, tracking pengeluaran via OCR, dan laporan keuangan bulanan.

## 2. Problem Statement
Banyak orang kesulitan mengelola keuangan karena tidak mencatat pengeluaran. Metode manual (buku catatan/Excel) tidak praktis.

## 3. Target Pengguna
- Karyawan usia 22-40 tahun
- Freelancer dengan penghasilan tidak tetap
- Ibu rumah tangga yang mengatur keuangan keluarga

## 4. Fitur Unggulan
- Scan struk belanja (OCR) → otomatis kategorisasi
- Budget planner mingguan/bulanan
- Laporan keuangan otomatis
- Multi-akun (tabungan, cash, e-wallet)
- Reminder tagihan

## 5. Arsitektur
- Mobile: React Native
- Backend: Go + PostgreSQL
- OCR: Google Vision API
- Cloud: AWS

## 6. Monetisasi
- Freemium: catatan 50 transaksi/bulan gratis
- Premium: unlimited, laporan PDF, export data

## 7. Timeline
- MVP: 2 bulan
- OCR & AI kategorisasi: 1 bulan
- Rilis Play Store: bulan ke-4
