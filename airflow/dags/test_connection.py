import pandas as pd
import psycopg2

# 1. Baca CSV
df = pd.read_csv(
    '/opt/airflow/raw_data/employees.csv',
    sep=';'
)

# 2. Bersihkan data
df['reportsTo'] = pd.to_numeric(
    df['reportsTo'],
    errors='coerce'
)

print(df.head())
print(df.dtypes)

# 3. Connect PostgreSQL
conn = psycopg2.connect(
    host='postgres',
    database='data_warehouse',
    user='airflow',
    password='airflow_rahasia_tim_123',
    port='5432'
)

cursor = conn.cursor()

# 4. Create schema
cursor.execute("""
CREATE SCHEMA IF NOT EXISTS classic_models;
""")

# 5. Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS classic_models.employees (
    employeeNumber INT PRIMARY KEY,
    lastName VARCHAR(50),
    firstName VARCHAR(50),
    extension VARCHAR(10),
    email VARCHAR(100),
    officeCode VARCHAR(10),
    reportsTo INT,
    jobTitle VARCHAR(50)
);
""")

# 6. Kosongkan tabel lama
cursor.execute("""
TRUNCATE TABLE classic_models.employees;
""")

# 7. Insert data
for row in df.itertuples(index=False):

    cursor.execute("""
        INSERT INTO classic_models.employees (
            employeeNumber,
            lastName,
            firstName,
            extension,
            email,
            officeCode,
            reportsTo,
            jobTitle
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        int(row.employeeNumber),
        row.lastName,
        row.firstName,
        row.extension,
        row.email,
        str(row.officeCode),
        None if pd.isna(row.reportsTo) else int(row.reportsTo),
        row.jobTitle
    ))

# 8. Simpan perubahan
conn.commit()

print("SUCCESS INSERT DATA")

# 9. Tutup koneksi
cursor.close()
conn.close()