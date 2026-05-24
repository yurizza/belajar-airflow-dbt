# 1. Menggunakan Image Resmi Apache Airflow v2 terbaru & stabil
FROM apache/airflow:2.7.1-python3.10

# 2. Pindah ke mode root untuk install komponen Linux pendukung dbt
USER root
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    g++ \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 3. Pindah kembali ke user aman (airflow)
USER airflow

# 4. Hanya meng-copy file daftar library (sangat aman, tidak bocor data)
COPY requirements.txt /requirements.txt

# 5. Install pandas, sqlalchemy, dan dbt terbaru
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r /requirements.txt