# DPW Modul 8: Transactional Storage Layers (Delta Lake & MinIO)

Repository ini berisi hasil pengerjaan Praktikum Modul 8 **Data Processing & Warehousing (DPW)** dengan topik *Transactional Storage Layers*, menggunakan **Delta Lake** melalui `delta-rs` dan **MinIO** sebagai object storage.

Proyek ini mendemonstrasikan perbedaan antara penyimpanan data menggunakan file Parquet biasa dan tabel Delta Lake, serta implementasi berbagai fitur transaksional, meliputi *Schema Enforcement*, *Time Travel*, *Upsert (Merge)*, *Slowly Changing Dimensions (SCD)*, dan *Failure Injection*.

## Tech Stack & Environment

| Teknologi | Versi / Keterangan |
|---|---|
| Python | 3.x |
| Deltalake (`delta-rs`) | 1.6.6 |
| PyArrow | 21.0.0 |
| Boto3 | 1.40.55 |
| Docker & Docker Compose | Menjalankan layanan MinIO |
| MinIO | Community Edition, image `cgr.dev/chainguard/minio:latest` |
| Pytest | Pengujian lokal |

## Getting Started

### Prerequisites

Pastikan perangkat telah memiliki:
- Python 3.x
- Docker Desktop
- Git

Pastikan Docker Desktop sudah berjalan sebelum memulai eksperimen.

### 1. Clone Repository

Jika repository belum tersedia secara lokal, jalankan:

```bash
git clone <repository-url>
cd <repository-folder>
```

Ganti `<repository-url>` dan `<repository-folder>` sesuai dengan repository yang digunakan.

### 2. Create Virtual Environment

Buat virtual environment menggunakan perintah berikut:

```bash
python -m venv .venv
```

Aktifkan virtual environment sesuai sistem operasi.

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

Instal seluruh dependensi yang tercantum dalam `requirements.txt`:

```bash
python -m pip install -r requirements.txt
```

### 4. Start MinIO

Jalankan layanan MinIO menggunakan Docker Compose:

```bash
docker compose up -d
```

Periksa status container untuk memastikan layanan telah berjalan:

```bash
docker compose ps
```

### 5. Initialize Storage

Inisialisasi bucket dan tabel Delta menggunakan CLI proyek:

```bash
python -m lab.cli init
python -m lab.cli reset
```

**Catatan:** Periksa implementasi `init` dan `reset` sebelum menjalankannya secara berurutan. Pastikan perintah `reset` tidak menghapus hasil eksperimen yang masih diperlukan.

### 6. Access MinIO Console

MinIO Console dapat diakses melalui alamat berikut:

- **URL:** `http://127.0.0.1:9001`
- **Username:** `dpw8admin`
- **Password:** `dpw8secret123`

Kredensial tersebut merupakan konfigurasi untuk lingkungan praktikum lokal. Jangan menggunakan kredensial contoh ini untuk lingkungan produksi atau mengeksposnya pada layanan publik.

## Experiments

Eksperimen dijalankan melalui CLI yang tersedia pada modul `lab.cli`.

| Perintah | Eksperimen | Tujuan |
|---|---|---|
| `python -m lab.cli compare` | Parquet vs. Delta Lake | Membandingkan penyimpanan Parquet biasa dengan tabel Delta Lake dan memeriksa keberadaan `_delta_log`. |
| `python -m lab.cli write` | Data Writing | Menguji proses penulisan data dan pembacaan skema tabel. |
| `python -m lab.cli schema-test` | Schema Enforcement | Menguji penolakan data yang tidak sesuai dengan skema tabel. |
| `python -m lab.cli time-travel` | Time Travel | Menguji pembacaan data berdasarkan versi atau snapshot tabel sebelumnya. |
| `python -m lab.cli merge` | Upsert (Merge) | Menguji operasi pembaruan data (*update*) dan penambahan data baru (*insert*). |
| `python -m lab.cli scd1` | SCD Type 1 | Menguji pengelolaan perubahan dimensi tanpa menyimpan riwayat nilai sebelumnya. |
| `python -m lab.cli scd2` | SCD Type 2 | Menguji pengelolaan perubahan dimensi dengan mempertahankan riwayat perubahan. |
| `python -m lab.cli failure` | Failure Injection | Menguji penanganan kegagalan ketika data yang ditulis tidak sesuai dengan tipe data yang diharapkan. |

## Evidence & Documentation

Bukti pengerjaan praktikum disimpan dalam folder [`evidence/`](evidence/).

Folder tersebut digunakan untuk mengorganisasi dokumentasi eksperimen, seperti:
- Screenshot terminal.
- Bukti konfigurasi dan tampilan MinIO.
- Log hasil eksperimen.
- Analisis hasil pengujian.

Dokumentasi analisis utama dapat dilihat pada [`evidence/Evidence-Chain-Template.md`](evidence/Evidence-Chain-Template.md).

Dokumentasi ini membantu menelusuri proses eksperimen, hasil yang diperoleh, dan bukti pendukung dari setiap tahapan praktikum.

## Local Testing

Pengujian lokal dapat dijalankan menggunakan `pytest`:

```bash
python -m pytest -q
```

Pengujian ini ditujukan untuk memverifikasi logika yang berkaitan dengan *schema mismatch* dan *table state* tanpa harus menjalankan seluruh layanan MinIO dan Docker, sesuai dengan cakupan pengujian yang diimplementasikan dalam proyek.

## Learning Outcomes

Melalui praktikum ini, beberapa konsep yang dipelajari meliputi:

- Perbedaan penyimpanan data berbasis Parquet dan Delta Lake.
- Pengelolaan perubahan data menggunakan transaksi Delta Lake.
- Penerapan *schema enforcement* untuk menjaga konsistensi struktur data.
- Pembacaan versi data sebelumnya menggunakan *time travel*.
- Pengelolaan data melalui operasi *upsert* dan *slowly changing dimensions*.
- Pengujian perilaku sistem ketika terjadi kegagalan penulisan data.
- Pemanfaatan object storage untuk mendukung pengelolaan data.

---

*Dikerjakan sebagai bagian dari Praktikum Data Processing & Warehousing (DPW), Modul 8: Transactional Storage Layers.*