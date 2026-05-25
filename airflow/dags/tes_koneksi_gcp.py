# airflow/dags/tes_koneksi_gcp.py
import os
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook

def uji_koneksi_gcp():
    print("🚀 [START] Memulai pengujian koneksi ke Google BigQuery...")
    
    # 1. Cek Path Service Account di dalam Docker
    path_json = "/opt/airflow/dags/sql/service_account.json"
    print(f"📁 1. Memeriksa keberadaan file JSON di: {path_json}")
    
    if os.path.exists(path_json):
        print("✅ File JSON ditemukan!")
        print(f"ℹ️ Ukuran file: {os.path.getsize(path_json)} bytes")
    else:
        print("❌ ERROR: File JSON tidak ditemukan di path tersebut!")
        print("💡 Pastikan kamu sudah menaruh file service_account.json di folder airflow/dags/sql/")
        return

    # 2. Mencoba inisialisasi Airflow BigQuery Hook
    print("\n🔗 2. Mencoba memanggil Airflow Google Cloud Connection...")
    try:
        # Menggunakan conn_id default yang mengarah ke path JSON di .env
        bq_hook = BigQueryHook(gcp_conn_id='google_cloud_default')
        client = bq_hook.get_client()
        print("✅ Hook & Client BigQuery berhasil diinisialisasi!")
    except Exception as e:
        print("❌ ERROR saat inisialisasi Hook/Client:")
        print(str(e))
        return

    # 3. Tes Query Ringan ke BigQuery (Tanpa Scan Data Besar)
    print("\n📥 3. Mencoba mengirimkan query tes ke BigQuery...")
    try:
        query_test = "SELECT 1 AS status_koneksi, 'Halo GCP!' AS pesan"
        query_job = client.query(query_test)
        results = list(query_job.result())
        
        print("\n🎉 [SUKSES TOTAL] Koneksi ke Google BigQuery Berhasil!")
        print(f"📊 Hasil Query Tes: Status = {results[0][0]}, Pesan = '{results[0][1]}'")
        
    except Exception as e:
        print("❌ ERROR: Gagal mengeksekusi query ke BigQuery!")
        print("💡 Kemungkinan masalah: Hak akses (Role) Service Account kurang, internet Docker mati, atau Project ID salah.")
        print(str(e))

if __name__ == "__main__":
    uji_koneksi_gcp()