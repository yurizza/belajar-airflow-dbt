"""
FLIGHT SOURCE SYSTEM (OLTP)
Synthetic Data Generator
---------------------------------
Output:
1. src_customer.csv
2. src_airport.csv
3. src_aircraft.csv
4. src_booking.csv
5. src_flight_segment.csv
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os

# =====================================================
# CONFIGURATION
# =====================================================

fake = Faker('en_US')

Faker.seed(42)
random.seed(42)
np.random.seed(42)

OUTPUT_DIR = "C:/Users/Dewi Oka/Documents/Dewi Document/KULIAH/S2-UGM/SEMESTER 1/Data Warehouse dan Ineligensi Bisnis/Tugas_Multidimensional Modelling/dew_ver/sumber_data/output_flight_source"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =====================================================
# MASTER DATA
# =====================================================

AIRPORTS = [
    ("CGK","Soekarno-Hatta Intl","Jakarta","Indonesia","Asia/Jakarta",-6.1256,106.6558),
    ("SUB","Juanda Intl","Surabaya","Indonesia","Asia/Jakarta",-7.3798,112.7866),
    ("DPS","Ngurah Rai Intl","Denpasar","Indonesia","Asia/Makassar",-8.7482,115.1672),
    ("MDC","Sam Ratulangi Intl","Manado","Indonesia","Asia/Makassar",1.5493,124.9257),
    ("UPG","Sultan Hasanuddin Intl","Makassar","Indonesia","Asia/Makassar",-5.0617,119.5540),
    ("BDO","Husein Sastranegara","Bandung","Indonesia","Asia/Jakarta",-6.9006,107.5762),
    ("PLM","Sultan Mahmud Badaruddin II","Palembang","Indonesia","Asia/Jakarta",-2.8982,104.7000),
    ("SIN","Changi Intl","Singapore","Singapore","Asia/Singapore",1.3644,103.9915),
    ("KUL","Kuala Lumpur Intl","Kuala Lumpur","Malaysia","Asia/Kuala_Lumpur",2.7456,101.7099),
    ("BKK","Suvarnabhumi Intl","Bangkok","Thailand","Asia/Bangkok",13.6900,100.7501),
    ("HKG","Hong Kong Intl","Hong Kong","China","Asia/Hong_Kong",22.3080,113.9185),
    ("NRT","Narita Intl","Tokyo","Japan","Asia/Tokyo",35.7720,140.3929),
    ("SYD","Kingsford Smith Intl","Sydney","Australia","Australia/Sydney",-33.9399,151.1753),
    ("LHR","Heathrow","London","UK","Europe/London",51.4775,-0.4614),
    ("DXB","Dubai Intl","Dubai","UAE","Asia/Dubai",25.2528,55.3644),
]

AIRLINES = [
    "Garuda Indonesia",
    "Lion Air",
    "Batik Air",
    "Citilink",
    "AirAsia Indonesia",
    "Sriwijaya Air"
]

AIRCRAFT_TYPES = [
    ("B737","Boeing 737-800","Boeing",162),
    ("B738","Boeing 737 MAX 8","Boeing",172),
    ("A320","Airbus A320","Airbus",180),
    ("A321","Airbus A321","Airbus",220),
    ("B777","Boeing 777-300ER","Boeing",396),
    ("B789","Boeing 787-9","Boeing",296),
    ("A333","Airbus A330-300","Airbus",335),
    ("ATR72","ATR 72-600","ATR",72)
]

FARE_BASIS_CODES = [
    "YOWUS",
    "YOWRS",
    "BSSAVE",
    "WOWBUS",
    "CLXBUS",
    "CLXSAV",
    "FLXFST",
    "GRPECO"
]

BOOKING_CHANNELS = [
    "WEB",
    "MOB",
    "OTA",
    "GDS",
    "CTR",
    "AGT"
]

# =====================================================
# SOURCE TABLE 1
# CUSTOMER
# =====================================================

def gen_src_customer(n=5000):

    rows = []

    for i in range(1, n+1):

        gender = random.choice(["M","F"])

        rows.append({
            # surrogate key
            "customer_key": i,
            
            "customer_id": f"CUS{i:07d}",
            "first_name":
                fake.first_name_male()
                if gender=="M"
                else fake.first_name_female(),
            "last_name": fake.last_name(),
            "gender": gender,
            "date_of_birth":
                fake.date_of_birth(
                    minimum_age=18,
                    maximum_age=75
                ),
            "nationality":
                random.choice([
                    "Indonesian",
                    "Singaporean",
                    "Malaysian",
                    "Australian",
                    "Japanese"
                ]),
            "email": fake.email(),
            "phone": fake.numerify(text="###-###-####")
        })

    return pd.DataFrame(rows)

# =====================================================
# SOURCE TABLE 2
# AIRPORT
# =====================================================

def gen_src_airport():

    rows = []

    for ap in AIRPORTS:

        rows.append({
            "airport_code": ap[0],
            "airport_name": ap[1],
            "city": ap[2],
            "country": ap[3],
            "timezone": ap[4],
            "latitude": ap[5],
            "longitude": ap[6]
        })

    return pd.DataFrame(rows)

# =====================================================
# SOURCE TABLE 3
# AIRCRAFT
# =====================================================

def gen_src_aircraft(n=120):

    rows = []

    for i in range(1, n+1):

        ac = random.choice(AIRCRAFT_TYPES)

        rows.append({
            "registration_number":
                f"PK-{fake.bothify('???##').upper()}",
            "aircraft_type": ac[1],
            "manufacturer": ac[2],
            "seat_capacity": ac[3],
            "operating_airline":
                random.choice(AIRLINES)
        })

    return pd.DataFrame(rows)

# =====================================================
# SOURCE TABLE 4
# BOOKING
# =====================================================

def gen_src_booking(n=15000):

    rows = []

    for i in range(1, n+1):

        rows.append({

            "booking_id": f"BKG{i:08d}",
            "customer_id":
                f"CUS{random.randint(1,5000):07d}",
            "booking_date":
                fake.date_between(
                    start_date="-3y",
                    end_date="today"
                ),
            "booking_channel":
                random.choice(
                    BOOKING_CHANNELS
                ) ,
            "fare_basis_code":
                random.choice(
                    FARE_BASIS_CODES
                )
        })

    return pd.DataFrame(rows)

# =====================================================
# SOURCE TABLE 5
# FLIGHT SEGMENT
# =====================================================

def gen_src_flight_segment(n=15000):

    rows = []

    airport_codes = [x[0] for x in AIRPORTS]

    for i in range(1, n+1):

        origin = random.choice(airport_codes)

        destination = random.choice(
            [x for x in airport_codes if x != origin]
        )

        sched_dep = fake.date_time_between(
            start_date="-3y",
            end_date="now"
        )

        actual_dep = sched_dep + timedelta(
            minutes=random.randint(-10,180)
        )

        rows.append({

            "segment_id": i,

            "booking_id":
                f"BKG{random.randint(1,n):08d}",

            "flight_number":
                f"GA{random.randint(100,999)}",

            "origin_airport": origin,

            "destination_airport": destination,

            "scheduled_departure":
                sched_dep,

            "actual_departure":
                actual_dep,

            "status":
                random.choices(
                    ["Flown","Cancelled","No-Show","Diverted"],
                    weights=[88,6,4,2]
                )[0]
        })

    return pd.DataFrame(rows)

# =====================================================
# GENERATE SOURCE DATA
# =====================================================

print("Generating source tables...")

src_customer = gen_src_customer()
src_airport = gen_src_airport()
src_aircraft = gen_src_aircraft()
src_booking = gen_src_booking()
src_flight_segment = gen_src_flight_segment()

# =====================================================
# SAVE TO CSV
# =====================================================

tables = {
    "src_customer": src_customer,
    "src_airport": src_airport,
    "src_aircraft": src_aircraft,
    "src_booking": src_booking,
    "src_flight_segment": src_flight_segment
}

print("\nSaving CSV files...")

for name, df in tables.items():

    path = f"{OUTPUT_DIR}/{name}.csv"

    df.to_csv(path, index=False)

    print(
        f"{name}: "
        f"{len(df):,} rows x "
        f"{len(df.columns)} cols "
        f"-> {path}"
    )

# =====================================================
# SUMMARY
# =====================================================

print("\n════════════════════════════════════")
print("FLIGHT SOURCE SYSTEM SUMMARY")
print("════════════════════════════════════")

for name, df in tables.items():

    print(
        f"{name:<20}: "
        f"{len(df):,} rows"
    )

print("════════════════════════════════════")