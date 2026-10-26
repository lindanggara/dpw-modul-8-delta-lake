# DPW Modul 8 Starter Pack
Mulai dari `PRAKTIKUM.md`. Stack dipin: `deltalake==1.6.6`, `pyarrow==21.0.0`, `boto3==1.40.55`, `pytest==8.4.2`.

```bash
python -m pip install -r requirements.txt
docker compose up -d
python -m lab.cli init
python -m lab.cli reset
```
Ikuti urutan aktivitas 3.1–3.10. Credentials adalah kredensial lab lokal, bukan produksi.

Jalankan test lokal:
```bash
python -m pytest -q
```
Test lokal menguji schema mismatch dan state table tanpa MinIO. Uji integrasi MinIO tetap perlu dijalankan pada komputer dengan Docker.
