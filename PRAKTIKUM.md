# BAGIAN 3 — EKSPERIMEN & ANALISIS
## Modul 8: Transactional Storage Layers (Delta Lake / Iceberg)
**Jalur implementasi:** Delta Lake via `deltalake`/delta-rs + PyArrow + MinIO. Iceberg hanya pembanding konsep. Jalankan command dari root folder.

## 3.1 Verifikasi Environment
```bash
docker --version
docker compose version
python --version
python -m pip install -r requirements.txt
python -c "import deltalake, pyarrow, boto3; print(deltalake.__version__, pyarrow.__version__)"
```
Expected: `deltalake` 1.6.6 dan PyArrow 21.0.0. Jika import gagal, pastikan interpreter/venv aktif lalu instal requirements. Evidence E01.

## 3.2 Object Storage dan Transactional Table
```bash
docker compose config
docker compose up -d
docker compose ps
python -m lab.cli init
python -m lab.cli reset
```
Buka `http://127.0.0.1:9001`, login `dpw8admin` / `dpw8secret123`. Bucket `dpw8-lakehouse`; table URI `s3://dpw8-lakehouse/events`. Expected: MinIO berjalan dan CLI menyatakan bucket ready. Jika koneksi gagal, periksa container dan port 9000. Evidence E01.

## 3.3 Parquet vs Transactional Table
```bash
python -m lab.cli compare
```
Bandingkan `parquet_baseline/events.parquet` dengan bucket MinIO `dpw8-lakehouse/events/`. Delta table berisi file data Parquet dan `_delta_log`; Parquet baseline tidak memiliki transaction log Delta. Dataset sama, tiga record. Evidence E02.

## 3.4 Write dan Read-back
```bash
python -m lab.cli write
```
Expected: version, 3 rows, dan schema `event_id`, `customer_id`, `amount`, `event_date`. Jika bucket belum tersedia, ulangi 3.2. Evidence E03.

## 3.5 Schema Enforcement
```bash
python -m lab.cli reset
python -m lab.cli schema-test
```
Command mencoba append kolom `unexpected_column`. Expected: `[SCHEMA] REJECTED`, version dan row count tidak berubah. Diagnosis: input tidak sesuai schema. Fix: selaraskan input dengan schema; jangan mengaktifkan schema evolution tanpa keputusan eksplisit. Ulangi test. Evidence E04.

## 3.6 Time Travel
```bash
python -m lab.cli time-travel
```
Expected: versi awal menampilkan 3 record; versi current 4 record. Membaca versi lama tidak mengubah versi current, sehingga bukan rollback. Jika table state rusak, jalankan reset lalu ulangi. Evidence E05.

## 3.7 Merge / Upsert
```bash
python -m lab.cli reset
python -m lab.cli merge
```
Source mengubah E002 menjadi amount 20000 dan menambah E004 amount 7000. Expected metrics memuat update dan insert; jumlah akhir 4. Jalankan merge sekali lagi untuk menguji idempotensi hasil terhadap source yang sama. Evidence E06.

## 3.8 SCD Type 1 dan Type 2
SCD Type 1:
```bash
python -m lab.cli reset
python -m lab.cli scd1
```
Expected: C001 menjadi Ayu Putri/Sidoarjo dan C003 ditambahkan; atribut lama C001 ditimpa.

SCD Type 2:
```bash
python -m lab.cli reset
python -m lab.cli scd2
```
Expected: C001 memiliki versi lama (`valid_to=2026-10-04`, `is_current=false`) dan versi baru (`valid_from=2026-10-05`, `is_current=true`); C003 menjadi current. Reset sebelum berpindah jenis eksperimen. Evidence E07-E08.

## 3.9 Failure Injection
```bash
python -m lab.cli reset
python -m lab.cli failure
```
Input bertipe string untuk `amount` sengaja tidak cocok dengan schema int64. Expected: write ditolak; version dan row count sebelum/sesudah sama; pesan `[FAILURE] PROVED`. Diagnosis: schema mismatch; fix adalah memperbaiki tipe input, bukan melonggarkan contract tanpa alasan. Ini membuktikan rejection pada skenario ini, bukan konkurensi multi-writer. Evidence E09.

## 3.10 Evidence Chain dan Checkpoint
Isi `evidence/Evidence-Chain-Template.md`. Setiap evidence: log, screenshot terminal/UI, potongan kode/config, output sebelum-sesudah, analisis singkat.

Checkpoint:
1. Apa fungsi `_delta_log` yang tidak dimiliki file Parquet mandiri?
2. Bagaimana membuktikan schema violation tidak membuat commit baru?
3. Apa beda time travel read dan rollback?
4. Bagaimana MERGE menentukan update atau insert?
5. Apa bukti perbedaan SCD1 dan SCD2 pada tabel?
6. Apa yang dibuktikan dan tidak dibuktikan oleh failure injection?

**Definition of Done:** MinIO/bucket siap; Parquet dan Delta dibandingkan; schema/versi/row count dibuktikan; schema violation ditolak; time travel, merge, SCD1/SCD2, dan failure injection berhasil; evidence lengkap.
