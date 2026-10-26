# 📋 Langkah Praktikum Modul 8 — Versi PowerShell (Windows)

## ⚠️ Langkah 0.0 — Izinkan eksekusi script (sekali saja)

PowerShell secara default memblokir `Activate.ps1`. Buka PowerShell **sebagai user biasa** (bukan admin), lalu:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
Ketik `Y` jika diminta konfirmasi. Ini cukup sekali seumur hidup untuk user kamu.

> Kalau tidak mau mengubah policy, alternatifnya pakai CMD untuk aktivasi, tapi sisanya tetap PowerShell — kurang nyaman. Lebih baik set policy di atas.

---

## 🔧 TAHAP 0 — Persiapan Environment

### Langkah 0.1 — Pastikan di root proyek
Prompt harus `PS D:\Modul 8>`. Cek isi folder:

```powershell
Get-ChildItem
```
Harus terlihat `docker-compose.yml`, `PRAKTIKUM.md`, `README.md`, `requirements.txt`, folder `lab\`.

### Langkah 0.2 — Pastikan Docker Desktop running
- Buka **Docker Desktop** dari Start Menu, tunggu sampai status **"Engine running"** (ikon paus di taskbar tidak abu-abu).
- Cek dari PowerShell:
  ```powershell
  docker --version
  docker compose version
  ```
  Kalau muncul error `cannot connect to the Docker daemon` → Docker Desktop belum siap, tunggu 30 detik lagi.

### Langkah 0.3 — Buat & aktifkan venv
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
Prompt akan berubah menjadi:
```
(.venv) PS D:\Modul 8>
```
✅ Kalau ada `(.venv)` di depan → venv aktif.

> ❌ Kalau muncul error `running scripts is disabled on this system` → kamu belum jalankan Langkah 0.0.

### Langkah 0.4 — Install dependencies
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```
Tunggu sampai selesai. Kalau ada warning kuning soal pip versi, abaikan.

### Langkah 0.5 — Buat folder evidence
```powershell
New-Item -ItemType Directory -Force evidence | Out-Null
New-Item -ItemType Directory -Force evidence\logs | Out-Null
```
Cek:
```powershell
Get-ChildItem evidence
```
Harus ada subfolder `logs`.

---

## ✅ TAHAP 1 — Verifikasi Environment (→ E01)

### Langkah 1.1 + 1.2 — Cek tools & library + simpan log sekaligus
```powershell
docker --version
docker compose version
python --version
python -c "import deltalake, pyarrow, boto3; print(deltalake.__version__, pyarrow.__version__)"
```

**Expected:** `1.6.6 21.0.0`

Simpan log (jalankan ulang sekaligus redirect):
```powershell
@"
=== E01 Environment ===
$(docker --version)
$(docker compose version)
$(python --version)
$(python -c 'import deltalake, pyarrow, boto3; print(deltalake.__version__, pyarrow.__version__)')
"@ | Tee-Object -FilePath evidence\logs\E01-environment.log
```

### Langkah 1.3 — Screenshot
- 📸 **`D:\Modul 8\evidence\E01-environment.png`** — screenshot terminal hasil langkah 1.1–1.2.

> ❌ Import gagal? → venv belum aktif (tidak ada `(.venv)` di prompt) atau install belum selesai. Ulangi Langkah 0.3–0.4.

---

## 🗄️ TAHAP 2 — Object Storage & Bucket (→ E01 lanjutan)

### Langkah 2.1 — Validasi Compose
```powershell
docker compose config
```
Pastikan tidak ada error parsing.

### Langkah 2.2 — Nyalakan MinIO
```powershell
docker compose up -d
```

### Langkah 2.3 — Cek container
```powershell
docker compose ps
```
Container `dpw8-minio` harus **Up (healthy)**. Kalau masih `starting`, tunggu ~10 detik lalu jalankan lagi.

> Kalau status `unhealthy` atau `exited`:
> ```powershell
> docker compose logs minio
> ```

### Langkah 2.4 — Init bucket & reset
```powershell
python -m lab.cli init
python -m lab.cli reset
```
Expected: pesan bucket ready + reset sukses.

### Langkah 2.5 — Buka UI MinIO
```powershell
Start-Process "http://127.0.0.1:9001"
```
Login: `dpw8admin` / `dpw8secret123`. Pastikan bucket **`dpw8-lakehouse`** muncul.

### Langkah 2.6 — Screenshot
- 📸 **`evidence\E01-minio-bucket.png`** — UI MinIO + output `docker compose ps` (bisa dua screenshot, atau satu yang menampilkan keduanya).

---

## 📊 TAHAP 3 — Parquet vs Delta Table (→ E02)

### Langkah 3.1 — Jalankan & simpan log
```powershell
python -m lab.cli compare 2>&1 | Tee-Object -FilePath evidence\logs\E02-compare.log
```

### Langkah 3.2 — Amati
- `parquet_baseline\events.parquet` → tanpa `_delta_log`
- `s3://dpw8-lakehouse/events/` → ada `_delta_log/`

### Langkah 3.3 — (Opsional) Cek manual di UI MinIO
Buka `dpw8-lakehouse` → `events/` → ada folder `_delta_log/`.

### Langkah 3.4 — Screenshot
- 📸 **`evidence\E02-parquet-vs-delta.png`**

---

## ✍️ TAHAP 4 — Write & Read-back (→ E03)

```powershell
python -m lab.cli write 2>&1 | Tee-Object -FilePath evidence\logs\E03-write.log
```
Expected: **version**, **3 rows**, schema `event_id, customer_id, amount, event_date`.

📸 **`evidence\E03-write-readback.png`**

---

## 🛡️ TAHAP 5 — Schema Enforcement (→ E04)

```powershell
python -m lab.cli reset
python -m lab.cli schema-test 2>&1 | Tee-Object -FilePath evidence\logs\E04-schema-test.log
```

**Sebelum menjalankan `schema-test`**, catat dulu **version** & **row count** dari output `reset`.
Expected setelah `schema-test`: **`[SCHEMA] REJECTED`** + version & rows **tidak berubah**.

📸 **`evidence\E04-schema-rejected.png`**

✍️ Di template catat: `sebelum: version=0, rows=3` → `sesudah: version=0, rows=3` (angka menyesuaikan output aktual).

---

## ⏮️ TAHAP 6 — Time Travel (→ E05)

```powershell
python -m lab.cli time-travel 2>&1 | Tee-Object -FilePath evidence\logs\E05-time-travel.log
```
Expected: versi lama = **3 record**, current = **4 record**.

📸 **`evidence\E05-time-travel.png`**

> ❌ State rusak? → `python -m lab.cli reset` lalu ulangi.

---

## 🔀 TAHAP 7 — Merge / Upsert (→ E06)

```powershell
python -m lab.cli reset
python -m lab.cli merge 2>&1 | Tee-Object -FilePath evidence\logs\E06-merge-run1.log
python -m lab.cli merge 2>&1 | Tee-Object -FilePath evidence\logs\E06-merge-run2.log
```
Expected:
- Run #1: update (E002→20000) + insert (E004→7000), total **4 rows**
- Run #2: hasil sama (idempotent, tidak duplikat E004)

📸 **`evidence\E06-merge.png`** — tampilkan kedua run.

---

## 🧬 TAHAP 8 — SCD Type 1 & Type 2 (→ E07, E08)

### Langkah 8.1 — SCD1
```powershell
python -m lab.cli reset
python -m lab.cli scd1 2>&1 | Tee-Object -FilePath evidence\logs\E07-scd1.log
```
Expected: C001 → Ayu Putri / Sidoarjo (overwrite), C003 ditambahkan.

📸 **`evidence\E07-scd1.png`**

### Langkah 8.2 — SCD2 (wajib reset dulu)
```powershell
python -m lab.cli reset
python -m lab.cli scd2 2>&1 | Tee-Object -FilePath evidence\logs\E08-scd2.log
```
Expected:
- C001 **2 versi**: lama (`valid_to=2026-10-04`, `is_current=false`) + baru (`valid_from=2026-10-05`, `is_current=true`)
- C003 → `is_current=true`

📸 **`evidence\E08-scd2.png`**

---

## 💥 TAHAP 9 — Failure Injection (→ E09)

```powershell
python -m lab.cli reset
```
**Catat** version & row count output reset.

```powershell
python -m lab.cli failure 2>&1 | Tee-Object -FilePath evidence\logs\E09-failure.log
```
Expected:
- Write **ditolak** (amount string vs int64)
- Version & row count **sebelum = sesudah**
- Muncul **`[FAILURE] PROVED`**

📸 **`evidence\E09-failure.png`**

✍️ Catat di template: **dibuktikan** = rejection schema mismatch; **tidak dibuktikan** = konkurensi multi-writer.

---

## 🧪 TAHAP 10 — Test Lokal (opsional)

```powershell
python -m pytest -q 2>&1 | Tee-Object -FilePath evidence\logs\pytest.log
```
Test jalan **tanpa MinIO** (menguji schema mismatch & state table lokal). Semua hijau → konfirmasi logika lab.

---

## 📝 TAHAP 11 — Isi Evidence Chain & Checkpoint (→ E10)

### Langkah 11.1 — Buka template
```powershell
notepad evidence\Evidence-Chain-Template.md
```
(atau pakai VS Code: `code evidence\Evidence-Chain-Template.md`)

### Langkah 11.2 — Isi E01–E09
Untuk setiap evidence isi 5 kolom: perintah, screenshot, kode/config, output sebelum–sesudah, analisis. Contoh format path gambar di Markdown (pakai `/`, bukan `\`):

```markdown
## E04 — Schema Enforcement
**Perintah:** `python -m lab.cli reset` ; `python -m lab.cli schema-test`
**Screenshot:** ![E04](evidence/E04-schema-rejected.png)
**Log:** [E04-schema-test.log](evidence/logs/E04-schema-test.log)
**Sebelum:** version=0, rows=3 — **Sesudah:** version=0, rows=3, `[SCHEMA] REJECTED`
**Analisis:** Append kolom tidak sesuai schema ditolak; tidak ada commit baru di `_delta_log`.
```

### Langkah 11.3 — Jawab 6 pertanyaan Checkpoint
(Sama seperti sebelumnya — lihat tabel di bawah.)

| # | Pertanyaan | Kunci Jawaban Singkat |
|---|---|---|
| 1 | Fungsi `_delta_log` | Log transaksi atomic: ACID, snapshot, schema, time travel. Parquet mandiri tidak punya. |
| 2 | Bukti schema violation tidak buat commit | Version & row count **sebelum = sesudah** `schema-test`. |
| 3 | Time travel vs rollback | Time travel **hanya baca** snapshot lama; rollback **menulis** state baru untuk mengembalikan. |
| 4 | MERGE tentukan update/insert | Berdasar **merge key** (`event_id`): match → update, tidak match → insert. |
| 5 | Bukti SCD1 vs SCD2 | SCD1: 1 baris/key, atribut lama hilang. SCD2: 2 baris C001 dengan `valid_from/valid_to/is_current` berbeda. |
| 6 | Yang dibuktikan & tidak oleh failure injection | **Dibuktikan:** rejection schema mismatch. **Tidak:** isolasi multi-writer/concurrency. |

### Langkah 11.4 — (Opsional) Screenshot template terisi
📸 **`evidence\E10-evidence-chain.png`**

### Langkah 11.5 — (Opsional) Commit ke Git
```powershell
git add evidence\
git commit -m "Add practicum evidence E01-E10"
```

---

## 🏁 TAHAP 12 — Checklist Definition of Done

- [ ] MinIO & bucket `dpw8-lakehouse` siap (E01)
- [ ] `compare` menunjukkan beda Parquet vs Delta (`_delta_log`) (E02)
- [ ] `write` → version, 3 rows, schema benar (E03)
- [ ] `schema-test` → REJECTED, version & rows tidak berubah (E04)
- [ ] `time-travel` → lama 3 rows, current 4 rows (E05)
- [ ] `merge` → update+insert total 4; run kedua idempotent (E06)
- [ ] `scd1` → overwrite C001 + C003 baru (E07)
- [ ] `scd2` → C001 2 versi, C003 current (E08)
- [ ] `failure` → `[FAILURE] PROVED`, state tidak berubah (E09)
- [ ] `Evidence-Chain-Template.md` terisi E01–E09 + analisis (E10)
- [ ] 6 pertanyaan Checkpoint terjawab

---

## 🧹 TAHAP 13 — Cleanup

```powershell
# Matikan container, volume tetap (aman, bisa dilanjut):
docker compose down

# Hapus total termasuk volume MinIO (⚠️ data di MinIO hilang):
docker compose down -v
```

Deactivate venv:
```powershell
deactivate
```

---

## ⚡ Cheat Sheet PowerShell (satu layar)

```powershell
# --- 0. Persiapan (sekali) ---
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned   # sekali seumur hidup
cd "D:\Modul 8"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
New-Item -ItemType Directory -Force evidence\logs | Out-Null

# --- 1–2. Cek env + MinIO (E01) ---
docker --version; docker compose version; python --version
python -c "import deltalake, pyarrow, boto3; print(deltalake.__version__, pyarrow.__version__)"
docker compose config
docker compose up -d
docker compose ps
python -m lab.cli init
python -m lab.cli reset
Start-Process "http://127.0.0.1:9001"

# --- 3–9. Eksperimen (E02–E09) ---
python -m lab.cli compare   2>&1 | Tee-Object evidence\logs\E02-compare.log
python -m lab.cli write     2>&1 | Tee-Object evidence\logs\E03-write.log
python -m lab.cli reset
python -m lab.cli schema-test 2>&1 | Tee-Object evidence\logs\E04-schema-test.log
python -m lab.cli time-travel 2>&1 | Tee-Object evidence\logs\E05-time-travel.log
python -m lab.cli reset
python -m lab.cli merge     2>&1 | Tee-Object evidence\logs\E06-merge-run1.log
python -m lab.cli merge     2>&1 | Tee-Object evidence\logs\E06-merge-run2.log
python -m lab.cli reset
python -m lab.cli scd1      2>&1 | Tee-Object evidence\logs\E07-scd1.log
python -m lab.cli reset
python -m lab.cli scd2      2>&1 | Tee-Object evidence\logs\E08-scd2.log
python -m lab.cli reset
python -m lab.cli failure   2>&1 | Tee-Object evidence\logs\E09-failure.log

# --- 10. Test lokal (opsional) ---
python -m pytest -q 2>&1 | Tee-Object evidence\logs\pytest.log

# --- 11. Isi template ---
code evidence\Evidence-Chain-Template.md

# --- 13. Cleanup ---
docker compose down
deactivate
```

---

## 💡 Catatan khusus PowerShell

1. **Redireksi `2>&1 | Tee-Object`** — beda dengan bash `| tee`. Di PowerShell harus `2>&1` dulu agar stderr ikut tertangkap, baru di-pipe ke `Tee-Object`.
2. **Aktivasi venv** selalu `.\.venv\Scripts\Activate.ps1` (pakai `.\` di depan; tanpa `.\` PowerShell anggap command).
3. **Path di Markdown template**: tetap pakai `/` (`evidence/E04-schema-rejected.png`), meskipun di filesystem Windows pakai `\`. Markdown/Git lebih ramah forward slash.
4. **Screenshot di PowerShell**: gunakan **Snipping Tool** (`Win + Shift + S`) → paste ke Paint → Save As `evidence\E0X-....png`. Atau PowerShell native (Win + Shift + S → auto tersimpan di clipboard, lalu `Win + V` untuk paste).
5. **Port 9000 bentrok** (kadang dipakai service lain di Windows): cek dengan `netstat -ano | findstr :9000`, matikan service tersebut, atau ubah mapping di `docker-compose.yml`.

Kalau kamu mau, saya bisa langsung **generate file `Evidence-Chain-Template.md` versi skeleton** siap tempel (header E01–E10 + kolom kosong), sesuai struktur folder `evidence\` di atas.