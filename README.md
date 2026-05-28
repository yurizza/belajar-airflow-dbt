# Transportation Data Pipeline

Pipeline ETL untuk ingest, transformasi, dan visualisasi data transportasi menggunakan:

* Apache Airflow
* PostgreSQL
* DuckDB
* dbt
* Metabase
* Google Cloud Platform BigQuery

## Setup Project

### 1. Clone Repository

```bash
git clone <repository-url>
cd <project-folder>
cd airflow
```

### 2. Setup Environment

Buat file `.env` dari `.env.example`.

```bash
cp .env.example .env
```

Sesuaikan konfigurasi sesuai kebutuhan.

### 3. Tambahkan GCP Credentials

Simpan service account key Google Cloud pada folder project, contoh:

```bash
./airflow/dags/sql/service_account.json
```

Pastikan path credentials sudah sesuai dengan konfigurasi pada `.env`.

---

## Menjalankan Project

### 1. Inisialisasi Airflow

```bash
chmod +x init.sh
./init.sh
```

### 2. Akses Airflow

Buka:

```text
http://localhost:8080
```

---

## Jalankan DAG

### `ingest_transportation_data`

Proses:

* Create table PostgreSQL
* Ingest data dari BigQuery ke PostgreSQL

### `etl_pipeline`

Proses:

* Load data dari PostgreSQL ke DuckDB
* Transformasi data menggunakan dbt
* Simpan hasil data marts ke PostgreSQL

---

## dbt Documentation

Jalankan:

```bash
./show_docs.sh
```

Akses dokumentasi:

```text
http://localhost:8081
```

---

## Setup Metabase

Buka:

```text
http://localhost:3000
```

Kemudian setup koneksi ke PostgreSQL menggunakan credential pada `.env`.

---

## Available Services

| Service  | URL              |
| -------- | ---------------- |
| Airflow  | `localhost:8080` |
| dbt Docs | `localhost:8081` |
| Metabase | `localhost:3000` |
