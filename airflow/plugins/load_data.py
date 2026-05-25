# airflow/plugins/load.py
import pandas as pd
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from airflow.providers.postgres.hooks.postgres import PostgresHook

def fungsi_ingest_incremental(schema_tabel, query_bq, incremental_column):
    print(f"🔍 [START] Memulai proses audit untuk tabel: {schema_tabel}")
    
    # 1. Hubungkan ke PostgreSQL Target
    pg_hook = PostgresHook(postgres_conn_id='postgres_dwh')
    
    # Pecah schema dan nama tabel (Contoh: 'airline.dim_airport' -> 'airline' dan 'dim_airport')
    nama_schema = schema_tabel.split('.')[0]
    nama_tabel = schema_tabel.split('.')[1]
    
    # Cek dulu apakah tabelnya sudah terbuat atau belum di Postgres
    check_table_query = f"""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = '{nama_schema}' 
            AND table_name = '{nama_tabel}'
        );
    """
    table_exists = pg_hook.get_first(check_table_query)[0]
    
    if not table_exists:
        print(f"❌ [ERROR] Tabel {schema_tabel} BELUM TERBUAT di Postgres!")
        print("💡 Harap jalankan DAG inisialisasi DDL (travel_dw_schema.sql) terlebih dahulu.")
        return

    # Ambil jumlah baris saat ini di Postgres
    row_count_pg = pg_hook.get_first(f"SELECT COUNT(*) FROM {schema_tabel};")[0]
    
    # 2. Hubungkan ke Google BigQuery Source
    bq_hook = BigQueryHook(gcp_conn_id='google_cloud_default')
    bq_client = bq_hook.get_client()
    
    # Hitung jumlah baris di BigQuery menggunakan query COUNT subquery
    query_count_bq = f"SELECT COUNT(*) FROM ({query_bq}) AS count_query"
    row_count_bq = list(bq_client.query(query_count_bq).result())[0][0]
    
    print(f"📊 Hasil Audit -> BigQuery (Source): {row_count_bq} baris | Postgres (Target): {row_count_pg} baris")
    
    # 3. Tentukan Strategi Ingestion Berdasarkan Kuantitas Data
    if row_count_bq == row_count_pg:
        print(f"✅ [SKIP] Jumlah data SAMA. Tidak ada data baru. Ingestion dilewati!")
        print("="*60)
        return
        
    elif row_count_pg == 0:
        print(f"🔄 [FULL LOAD] Postgres masih kosong. Menarik seluruh data dari BigQuery...")
        query_to_run = query_bq
        
    else:
        print(f"🚀 [INCREMENTAL LOAD] Perbedaan terdeteksi! Mengambil data terbaru saja...")
        # Cari tahu nilai ID atau tanggal maksimum yang ada di Postgres saat ini
        max_val_pg = pg_hook.get_first(f"SELECT MAX({incremental_column}) FROM {schema_tabel};")[0]
        
        # Modifikasi query BigQuery agar hanya mengambil data yang lebih baru dari data terakhir di Postgres
        if isinstance(max_val_pg, (int, float)):
            query_to_run = f"SELECT * FROM ({query_bq}) WHERE {incremental_column} > {max_val_pg}"
        else:
            # Jika tipe datanya adalah Date/Timestamp/String (butuh bungkus tanda kutip tunggal di SQL)
            query_to_run = f"SELECT * FROM ({query_bq}) WHERE {incremental_column} > '{max_val_pg}'"
            
        print(f"📥 Memodifikasi Query BQ: Mengambil data di mana {incremental_column} > {max_val_pg}")

    # 4. Eksekusi Penarikan Data dari BigQuery
    query_job = bq_client.query(query_to_run)
    results = query_job.result()
    
    # Konversi hasil query ke Pandas DataFrame
    rows = [dict(row) for row in results]
    df = pd.DataFrame(rows)
    
    if df.empty:
        print("ℹ️ Tidak ada baris baru yang memenuhi syarat untuk dimasukkan.")
        print("="*60)
        return

    # 5. Proses Insert (Append) Data ke PostgreSQL
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    
    # Jika ini proses Full Load, kita kosongkan tabel dulu (Trunacte) demi kebersihan data
    if row_count_pg == 0:
        cursor.execute(f"TRUNCATE TABLE {schema_tabel} CASCADE;")

    # Otomatisasi mapping kolom menggunakan Pandas DataFrame
    kolom = list(df.columns)
    string_kolom = ", ".join(kolom)
    string_placeholders = ", ".join(["%s"] * len(kolom))
    query_insert = f"INSERT INTO {schema_tabel} ({string_kolom}) VALUES ({string_placeholders})"
    
    print(f"📥 Memasukkan {len(df)} baris data baru ke {schema_tabel}...")
    for row in df.itertuples(index=False):
        # Bersihkan nilai NaN/NaT dari Pandas agar terbaca sebagai NULL di Postgres
        row_clean = tuple(None if pd.isna(value) else value for value in row)
        cursor.execute(query_insert, row_clean)
        
    # Commit semua transaksi ke database
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"✅ [SUCCESS] Sinkronisasi tabel {schema_tabel} selesai!\n" + "="*60)