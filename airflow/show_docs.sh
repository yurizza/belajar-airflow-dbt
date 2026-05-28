#!/bin/bash
echo "📊 Mengambil metadata terupdate dari database..."
docker compose exec airflow-worker bash -c "cd /opt/airflow/dbt_project && dbt docs generate"

echo "🌐 Menjalankan server dokumentasi dbt di port 8081..."
echo "🔗 Silakan buka: http://localhost:8081"
# Perintah ini akan jalan terus di terminal untuk men-serve dokumentasi
docker compose exec airflow-worker bash -c "cd /opt/airflow/dbt_project && dbt docs serve --port 8081"