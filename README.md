# PT Popeye Trans Logistik - Static Website Mirror (HTML / CSS / JS)

Salinan lengkap (*static mirror*) dari website **[popeye-logistik.com](https://popeye-logistik.com)** ke dalam format murni **HTML, CSS, dan JavaScript**, dilengkapi seluruh aset gambar, logo, ikon, dan web fonts tanpa ketergantungan pada server WordPress online.

---

## 📁 Struktur Halaman & File

Website ini dapat dibuka baik langsung dari file `.html` (misal via browser) maupun melalui web server statis:

### Halaman Utama
- [index.html](file:///Users/adit/Projects/pt_ptl_company_profiles/index.html) - Beranda (Home)
- [tentang-kami.html](file:///Users/adit/Projects/pt_ptl_company_profiles/tentang-kami.html) (atau folder `tentang-kami/`) - Profil & Informasi Tentang Perusahaan
- [armada.html](file:///Users/adit/Projects/pt_ptl_company_profiles/armada.html) (atau folder `armada/`) - Daftar & Spesifikasi Armada Truk Logistik
- [klien.html](file:///Users/adit/Projects/pt_ptl_company_profiles/klien.html) (atau folder `klien/`) - Daftar Klien & Mitra Kerja
- [kontak.html](file:///Users/adit/Projects/pt_ptl_company_profiles/kontak.html) (atau folder `kontak/`) - Kontak & Alamat Kantor
- [proyek.html](file:///Users/adit/Projects/pt_ptl_company_profiles/proyek.html) (atau folder `proyek/`) - Proyek yang Dikerjakan
- [portfolio.html](file:///Users/adit/Projects/pt_ptl_company_profiles/portfolio.html) (atau folder `portfolio/`) - Portofolio Pekerjaan
- [product-2.html](file:///Users/adit/Projects/pt_ptl_company_profiles/product-2.html) (atau folder `product-2/`) - Layanan / Produk Logistik
- [sample-page.html](file:///Users/adit/Projects/pt_ptl_company_profiles/sample-page.html) (atau folder `sample-page/`) - Halaman Contoh

### Aset Lokal
- `wp-content/uploads/` — Seluruh gambar armada, logo PT Popeye Trans Logistik, favicon, sertifikasi, galeri foto, dan font Google Fonts (Roboto & Roboto Slab).
- `wp-content/plugins/` — File CSS dan JS pendukung (Elementor frontend, animations, icon libraries).
- `wp-content/themes/` — CSS tema Astra & stylesheet tata letak.
- `wp-includes/` — Core jQuery, imagesLoaded, dan helper scripts.
- `scripts/` — Skrip pembantu pemeliharaan dan mirroring.

---

## 🚀 Cara Menjalankan Website Secara Lokal

### Opsi 1: Menggunakan Python Web Server (Rekomendasi)
Buka terminal di folder proyek ini (`/Users/adit/Projects/pt_ptl_company_profiles`), lalu jalankan:

```bash
python3 -m http.server 8000
```
Buka browser dan akses:
👉 **[http://localhost:8000](http://localhost:8000)**

### Opsi 2: Menggunakan Node.js / NPX (jika terpasang)
```bash
npx serve .
```

### Opsi 3: Buka Langsung di Browser
Klik ganda file [index.html](file:///Users/adit/Projects/pt_ptl_company_profiles/index.html) di file manager / Finder untuk membukanya secara langsung. Seluruh aset gambar, stylesheet, dan navigasi telah disesuaikan agar bekerja secara offline.
