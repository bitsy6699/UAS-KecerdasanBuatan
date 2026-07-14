# CONTOH PRD: Platform E-Commerce B2B untuk Produk Lokal

## 1. Ringkasan Eksekutif
Marketplace B2B yang menghubungkan produsen lokal dengan reseller. Fokus pada produk kerajinan, makanan olahan, dan fashion.

## 2. Latar Belakang
Produsen lokal kesulitan menjangkau pasar lebih luas. Reseller kesulitan mencari supplier terpercaya.

## 3. Target Pengguna
### Produsen
- UMKM dengan kapasitas produksi terbatas
- Butuh saluran distribusi tambahan
- Tingkat tech: rendah-sedang

### Reseller
- Pemilik toko online/kecil
- Mencari produk unik dengan margin baik
- Tingkat tech: sedang-tinggi

## 4. Fitur
### MVP (Fase 1)
- Katalog produk dengan foto & deskripsi
- Sistem order & payment escrow
- Dashboard penjualan untuk produsen
- Fitur chat buyer-supplier

### Fase 2
- Sistem rating & review
- Manajemen inventory
- Shipping integration
- Analytics untuk produsen

## 5. Arsitektur Teknis
- Frontend: React Native (mobile) + Next.js (web)
- Backend: Go + PostgreSQL
- Cache: Redis
- Cloud: AWS (ECS RDS)
- Payment: Midtrans/Xendit

## 6. Non-Fungsional
- Waktu muat halaman < 2 detik
- Support 1000 pengguna simultan di fase 1
- Uptime 99.5%
- Enkripsi data pengguna

## 7. Timeline
- Fase 1 (MVP): 12 minggu
- Fase 2: 8 minggu setelah rilis MVP
- Fase 3 (skalabilitas): berkelanjutan
