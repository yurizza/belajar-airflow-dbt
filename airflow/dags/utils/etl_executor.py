from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
import pandas as pd


def fungsi_insert_all(schema_tabel, query_bq, pg_conn_id, gcp_conn_id):

    print("=" * 60)
    print(f"🚀 [START] Full Load untuk tabel: {schema_tabel}")

    # -----------------------------------------
    # Parsing schema dan nama tabel
    # -----------------------------------------
    nama_schema, nama_tabel = schema_tabel.split('.')

    # -----------------------------------------
    # Inisialisasi koneksi
    # -----------------------------------------
    print("🔌 Menghubungkan ke PostgreSQL dan BigQuery...")

    pg_hook = PostgresHook(postgres_conn_id=pg_conn_id)

    bq_hook = BigQueryHook(
        gcp_conn_id=gcp_conn_id,
        use_legacy_sql=False
    )

    bq_client = bq_hook.get_client()

    # -----------------------------------------
    # Validasi tabel PostgreSQL
    # -----------------------------------------
    print(f"🔍 Mengecek keberadaan tabel {schema_tabel}...")

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
        raise Exception(
            f"❌ Tabel PostgreSQL {schema_tabel} BELUM ADA!"
        )

    print(f"✅ Tabel {schema_tabel} ditemukan.")

    # -----------------------------------------
    # EXTRACT dari BigQuery
    # -----------------------------------------
    print("⏳ Mengambil data dari BigQuery...")

    query_job = bq_client.query(query_bq)

    results = query_job.result()

    df = pd.DataFrame([dict(row) for row in results])

    # -----------------------------------------
    # Validasi data kosong
    # -----------------------------------------
    if df.empty:
        print("ℹ️ Data BigQuery kosong. Tidak ada insert dilakukan.")
        return

    print(f"📊 Total data berhasil diambil: {len(df)} baris")

    # -----------------------------------------
    # Cleaning NaN -> NULL
    # -----------------------------------------
    print("🧼 Membersihkan nilai NaN menjadi NULL...")

    rows = [
        tuple(
            None if pd.isna(value) else value
            for value in row
        )
        for row in df.itertuples(index=False, name=None)
    ]

    kolom = list(df.columns)

    # -----------------------------------------
    # TRUNCATE tabel lama
    # -----------------------------------------
    print(f"🧹 Menghapus data lama pada {schema_tabel}...")

    truncate_query = f"TRUNCATE TABLE {schema_tabel} CASCADE;"

    pg_hook.run(truncate_query)

    # -----------------------------------------
    # INSERT batch ke PostgreSQL
    # -----------------------------------------
    print(f"📥 Memasukkan data baru ke {schema_tabel}...")

    # pg_hook.insert_rows(
    #     table=schema_tabel,
    #     rows=rows,
    #     target_fields=kolom,
    #     commit_every=1000
    # )

    print(f"✅ [SUCCESS] Insert selesai untuk {schema_tabel}")
    print("=" * 60)