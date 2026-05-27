from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd
import traceback

def fungsi_insert_all(schema_tabel, query_bq, pg_conn_id, gcp_conn_id):

    print("=" * 60)
    print(f"🚀 [START] Ingest Pipeline untuk tabel: {schema_tabel}")

    # -----------------------------------------
    # Parsing schema dan nama tabel
    # -----------------------------------------
    nama_schema, nama_tabel = schema_tabel.split('.')

    # Inisialisasi hook ke Postgres dan BigQuery
    pg_hook = PostgresHook(postgres_conn_id=pg_conn_id)
    bq_hook = BigQueryHook(gcp_conn_id=gcp_conn_id, use_legacy_sql=False)
    bq_client = bq_hook.get_client()

    # Variabel penampung metrik rekonsiliasi log run
    total_extracted = 0
    total_inserted = 0
    status_run = "SUCCESS"
    pesan_error = None

    # -----------------------------------------
    # Validasi tabel PostgreSQL sebelum eksekusi
    # -----------------------------------------
    check_table_query = f"""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = '{nama_schema}'
            AND table_name = '{nama_tabel}'
        );
    """
    table_exists = pg_hook.get_first(check_table_query)[0]

    if not table_exists:
        raise Exception(f"❌ Tabel PostgreSQL {schema_tabel} BELUM ADA! Harap jalankan DDL terlebih dahulu.")

    try:
        # -----------------------------------------
        # 1. Cek Apakah Tabel Kosong & Ambil High-Water Mark
        # -----------------------------------------
        cek_isi_tabel_query = f"SELECT COUNT(*) FROM {schema_tabel};"
        jumlah_baris_postgres = pg_hook.get_first(cek_isi_tabel_query)[0]
        
        max_date_query = f"SELECT COALESCE(MAX(updated_at), '1970-01-01 00:00:00'::timestamp) FROM {schema_tabel};"
        last_updated_at = pg_hook.get_first(max_date_query)[0]
        print(f"📅 Data terakhir di Postgres berada pada waktu: {last_updated_at}")

        # -----------------------------------------
        # 2. EXTRACT Data Delta dari BigQuery
        # -----------------------------------------
        incremental_query = f"""
            SELECT * FROM ({query_bq})
            WHERE updated_at > '{last_updated_at}'
        """
        query_job = bq_client.query(incremental_query)
        results = query_job.result()
        df = pd.DataFrame([dict(row) for row in results])

        # -----------------------------------------
        # 3. Validasi & Cleaning Jika Data Kosong / Ada
        # -----------------------------------------
        if df.empty:
            print("ℹ️ Tidak ada data baru atau data terupdate di BigQuery. Selesai.")
            # Catat log sukses dengan extracted=0 dan inserted=0
            _catat_log_ke_db(pg_hook, schema_tabel, 0, 0, "SUCCESS", None)
            print("=" * 60)
            return

        total_extracted = len(df) # <--- Jumlah data dari BigQuery
        print(f"📊 Total data delta ditemukan dari BigQuery: {total_extracted} baris")

        # Bersihkan nilai NaN bawaan Pandas menjadi NULL/None untuk Postgres
        rows = [
            tuple(None if pd.isna(value) else value for value in row)
            for row in df.itertuples(index=False, name=None)
        ]
        kolom = list(df.columns)

        # -----------------------------------------
        # 4. ADAPTIF INSERT / UPSERT LOGIC
        # -----------------------------------------
        string_kolom = ", ".join(kolom)
        string_placeholder = ", ".join(["%s"] * len(kolom))

        # KONDISI A: JIKA TABEL MASIH KOSONG MELOMPONG (FIRST LOAD RUN)
        if jumlah_baris_postgres == 0:
            print(f"🆕 Tabel {schema_tabel} terdeteksi KOSONG. Menjalankan perintah INSERT murni untuk pertama kali...")
            
            upsert_sql = f"""
                INSERT INTO {schema_tabel} ({string_kolom})
                VALUES ({string_placeholder});
            """
            
        # KONDISI B: JIKA TABEL SUDAH ADA ISINYA (INCREMENTAL RUN)
        else:
            print(f"🔄 Tabel {schema_tabel} sudah berisi data. Menjalankan perintah UPSERT adaptif aman...")
            
            if "src_payment_transaction" in nama_tabel:
                target_conflict = "payment_reference"  # Mengunci keunikan via UUID Transaksi hulu
            elif "src_booking" in nama_tabel:
                target_conflict = "booking_id"
            else:
                target_conflict = kolom[0]  # Fallback ke kolom pertama untuk tabel master biasa
            
            list_conflict_keys = [k.strip() for k in target_conflict.split(",")]
            list_update = [f"{col} = EXCLUDED.{col}" for col in kolom if col not in list_conflict_keys]
            string_update = ", ".join(list_update)

            upsert_sql = f"""
                INSERT INTO {schema_tabel} ({string_kolom})
                VALUES ({string_placeholder})
                ON CONFLICT ({target_conflict})
                DO UPDATE SET {string_update};
            """

        # -----------------------------------------
        # 5. LOAD - Eksekusi Data Batch ke PostgreSQL
        # -----------------------------------------
        print(f"📥 Memproses penulisan ke database Postgres...")
        conn = pg_hook.get_conn()
        cursor = conn.cursor()
        
        cursor.executemany(upsert_sql, rows)
        conn.commit()
        
        # Jika commit berhasil tanpa error, maka jumlah data yang ter-insert sama dengan data yang di-extract
        total_inserted = total_extracted 
        
        cursor.close()
        conn.close()
        
        print(f"✅ [SUCCESS] Eksekusi data berhasil dimuat ke {schema_tabel}")
        
        # Catat status SUKSES ke database logging
        _catat_log_ke_db(pg_hook, schema_tabel, total_extracted, total_inserted, status_run, pesan_error)

    except Exception as e:
        status_run = "FAILED"
        pesan_error = str(e)
        total_inserted = 0 # Karena error dan di-rollback, maka 0 baris masuk ke Postgres
        print(f"❌ [ERROR] Terjadi kegagalan proses: {pesan_error}")
        print(traceback.format_exc())
        
        # Catat status GAGAL ke database logging
        _catat_log_ke_db(pg_hook, schema_tabel, total_extracted, total_inserted, status_run, pesan_error)
        
        # Lemparkan kembali error agar task Airflow berstatus Failed di UI
        raise e
        
    print("=" * 60)


def _catat_log_ke_db(pg_hook, nama_tabel, rows_extracted, rows_affected, status, error_msg):
    """Fungsi helper internal untuk mencatatkan riwayat eksekusi pipeline ke skema logging"""
    log_sql = """
        INSERT INTO logging.etl_run_log (target_table, rows_extracted, rows_inserted, status, error_message)
        VALUES (%s, %s, %s, %s, %s);
    """
    try:
        pg_hook.run(log_sql, parameters=(nama_tabel, rows_extracted, rows_affected, status, error_msg))
        print("📝 Log run operasional (Reconciliation) berhasil disimpan ke logging.etl_run_log")
    except Exception as log_err:
        print(f"⚠️ Gagal menyimpan log ke DB (Proses data utama tetap aman): {str(log_err)}")