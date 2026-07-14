# CONTOH PRD: Aplikasi Dompet Digital untuk Pekerja Informal

## 1. Ringkasan Eksekutif
Dompet digital khusus untuk pekerja informal (driver, freelancer, pedagang kecil) dengan fitur pencatatan penghasilan harian, tabungan otomatis, dan akses pinjaman mikro.

## 2. Problem Statement
Pekerja informal (60% dari angkatan kerja Indonesia) tidak memiliki akses ke produk keuangan formal karena penghasilan tidak tetap dan tidak ada slip gaji.

## 3. Tujuan
- 50.000 pengguna terdaftar di tahun pertama
- 30% pengguna aktif menabung setiap minggu
- Tingkat gagal bayar pinjaman < 5%

## 4. Target Persona
### Budi (28 tahun, driver ojek online)
- Penghasilan: Rp100-200rb/hari (tidak tetap)
- Pain: Sulit nabung, tidak punya riwayat kredit
- Tech: Smartphone Android, melek aplikasi

### Sari (35 tahun, pedagang pasar)
- Penghasilan: Rp3-5jt/bulan
- Pain: Butuh modal usaha, tidak punya agunan
- Tech: WhatsApp, kadang pakai Shopee

## 5. Fitur
### P0 (MVP)
- Top-up via berbagai metode (indomaret, transfer, QR)
- Catat penghasilan & pengeluaran harian
- Goal-based saving (target HP, lebaran, dll)
- Auto-save (sisihkan % dari setiap pemasukan)

### P1 (Fase 2)
- Pinjaman mikro (Rp500k-Rp5jt)
- Score kredit alternatif (berdasarkan histori transaksi)
- Asuransi mikro

### P2 (Fase 3)
- Investasi reksadana
- Fitur nabung bareng (group saving)
- Laporan pajak

## 6. Regulasi & Kepatuhan
- Terdaftar di OJK sebagai penyelenggara fintech
- KYC level 1 (NIK & selfie) untuk basic
- KYC level 2 (NPWP & KK) untuk pinjaman
- Enkripsi data pengguna (AES-256)
- Audit trail untuk semua transaksi

## 7. Arsitektur
- Android (Kotlin) + iOS (Swift)
- Backend: Go + PostgreSQL
- Redis untuk caching & session
- AWS dengan multi-AZ deployment
- 3rd party: OVO/GoPay/QRIS untuk top-up

## 8. Metrik
- CAC (Customer Acquisition Cost) < Rp10.000
- LTV (Life Time Value) > Rp150.000
- Monthly active users / registered users > 40%
- Pinjaman disbursed per bulan > Rp1M

## 9. Timeline
- Bulan 1-3: Pengembangan MVP
- Bulan 4: Beta testing (1000 user)
- Bulan 5: Public launch (Play Store)
- Bulan 6: Evaluasi & iterasi
- Bulan 7-9: Fitur pinjaman
- Bulan 10-12: Skalabilitas
