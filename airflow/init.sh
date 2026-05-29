#!/bin/bash

# Menghentikan script jika ada perintah yang error
set -e

echo "🚀 Memulai setup Airflow Environment..."

# =====================================================================
# 1. MENYALAKAN DATABASE & REDIS DULUAN
# =====================================================================
docker compose up -d postgres redis

echo "⏳ Menunggu database Postgres siap..."
sleep 5

# =====================================================================
# INTERMISI: MEMBUAT DATABASE DATA WAREHOUSE
# =====================================================================
echo "🗄️  Membuat database 'data_warehouse' di PostgreSQL..."
set +e
# Menggunakan 'docker compose exec -T' agar aman dijalankan di dalam script/non-tty
docker compose exec -T postgres psql -U airflow -d airflow -c "CREATE DATABASE data_warehouse;" >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Database 'data_warehouse' berhasil dibuat!"
else
    echo "⚠️  Database 'data_warehouse' sudah ada atau dilewati."
fi
set -e


# =====================================================================
# 2. MIGRASI DATABASE METADATA AIRFLOW & USER ADMIN
# =====================================================================
echo "👤 Menjalankan migrasi database Airflow..."
docker compose run --rm airflow-scheduler airflow db migrate

echo "👤 Membuat user Admin Airflow..."
set +e # Mengantisipasi jika user admin sudah pernah dibuat sebelumnya
docker compose run --rm airflow-scheduler airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@gmail.com \
    --password admin
set -e


# =====================================================================
# 3. OTOMATISASI PENDAFTARAN KONEKSI (CONNECTION INJECTOR)
# =====================================================================
echo "🔑 Mendaftarkan koneksi external ke Metadata Airflow..."
set +e

# A. Suntik Koneksi PostgreSQL Data Warehouse
docker compose run --rm airflow-scheduler airflow connections add 'postgres_dwh' \
    --conn-uri 'postgres://airflow:airflow_rahasia_tim_123@postgres:5432/data_warehouse' 2>/dev/null
if [ $? -eq 0 ]; then echo "✅ Koneksi 'postgres_dwh' berhasil ditambahkan!"; fi

# B. Suntik Koneksi Google Cloud Platform (GCP)
docker compose run --rm airflow-scheduler airflow connections add 'google_cloud_default' --conn-uri 'google-cloud-platform://?key_path=/opt/airflow/dags/sql/service_account.json&project=DATA_WAREHOUSE' 2>/dev/null
if [ $? -eq 0 ]; then echo "✅ Koneksi 'google_cloud_default' berhasil ditambahkan!"; fi

set -e


# =====================================================================
# 4. MENYALAKAN SELURUH SERVICE AIRFLOW Utama
# =====================================================================
echo "🐳 Menjalankan seluruh service Airflow (Webserver, Scheduler, Worker)..."
docker compose up -d


# =====================================================================
# RINGKASAN REKAPITULASI SETUP
# =====================================================================
echo ""
echo "================================================================="
echo "✅ Setup selesai! Silakan buka Web UI: http://localhost:8080"
echo "================================================================="
echo "  Standard Credentials:"
echo "  - Username : admin"
echo "  - Password : admin"
echo ""
echo "  Pre-configured Connections (Lihat di Admin -> Connections):"
echo "  - postgres_dwh        -> Terhubung ke DB 'data_warehouse'"
echo "  - google_cloud_default -> Menggunakan kunci service_account.json"
echo "================================================================="