"""
FLIGHT SOURCE SYSTEM (OLTP) - Refactored v2
============================================
Output:
  src_customer.csv       - 2,000 customers (SCD Type 2 history included)
  src_airport.csv        - 15 airports
  src_aircraft.csv       - 80 aircraft
  src_booking.csv        - 15,000 bookings  ← main transaction table
  src_flight_segment.csv - 15,000 segments (1:1 with booking)

FK design:
  src_booking       → customer_key (PK of src_customer)
  src_flight_segment → booking_id  (PK of src_booking)

No redundant customer_key in src_flight_segment; join via booking.
"""

import os, random
import numpy as np
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta

# ── Config ──────────────────────────────────────────────────────────────────
Faker.seed(42); random.seed(42); np.random.seed(42)
fake = Faker("en_US")

OUTPUT_DIR = r"C:\Users\Dewi Oka\Documents\files\flight"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Master reference ─────────────────────────────────────────────────────────
AIRPORTS = [
    ("CGK","Soekarno-Hatta Intl",    "Jakarta",       "Indonesia", "Asia/Jakarta",   -6.1256, 106.6558),
    ("SUB","Juanda Intl",             "Surabaya",      "Indonesia", "Asia/Jakarta",   -7.3798, 112.7866),
    ("DPS","Ngurah Rai Intl",         "Denpasar",      "Indonesia", "Asia/Makassar",  -8.7482, 115.1672),
    ("MDC","Sam Ratulangi Intl",      "Manado",        "Indonesia", "Asia/Makassar",   1.5493, 124.9257),
    ("UPG","Sultan Hasanuddin Intl",  "Makassar",      "Indonesia", "Asia/Makassar",  -5.0617, 119.5540),
    ("BDO","Husein Sastranegara",     "Bandung",       "Indonesia", "Asia/Jakarta",   -6.9006, 107.5762),
    ("PLM","SM Badaruddin II",        "Palembang",     "Indonesia", "Asia/Jakarta",   -2.8982, 104.7000),
    ("SIN","Changi Intl",             "Singapore",     "Singapore", "Asia/Singapore",  1.3644, 103.9915),
    ("KUL","Kuala Lumpur Intl",       "Kuala Lumpur",  "Malaysia",  "Asia/KL",         2.7456, 101.7099),
    ("BKK","Suvarnabhumi Intl",       "Bangkok",       "Thailand",  "Asia/Bangkok",   13.6900, 100.7501),
    ("HKG","Hong Kong Intl",          "Hong Kong",     "China",     "Asia/HK",        22.3080, 113.9185),
    ("NRT","Narita Intl",             "Tokyo",         "Japan",     "Asia/Tokyo",     35.7720, 140.3929),
    ("SYD","Kingsford Smith Intl",    "Sydney",        "Australia", "Australia/Sydney",-33.9399,151.1753),
    ("LHR","Heathrow",                "London",        "UK",        "Europe/London",  51.4775,  -0.4614),
    ("DXB","Dubai Intl",              "Dubai",         "UAE",       "Asia/Dubai",     25.2528,  55.3644),
]
AIRPORT_CODES = [a[0] for a in AIRPORTS]

BOOKING_CHANNELS = [
    ("WEB","Website Direct",0.35),
    ("MOB","Mobile App",0.30),
    ("GDS","Global Distribution System",0.15),
    ("OTA","Online Travel Agency",0.12),
    ("CTR","Call Center",0.05),
    ("AGT","Travel Agent",0.03),
]

AIRLINES      = ["Garuda Indonesia","Lion Air","Batik Air","Citilink","AirAsia Indonesia","Sriwijaya Air"]
AIRCRAFT_TYPES= [
    ("Boeing 737-800","Boeing",162),("Boeing 737 MAX 8","Boeing",172),
    ("Airbus A320","Airbus",180),("Airbus A321","Airbus",220),
    ("Boeing 777-300ER","Boeing",396),("Boeing 787-9","Boeing",296),
    ("Airbus A330-300","Airbus",335),("ATR 72-600","ATR",72),
]

# Airport groupings for realistic flight duration estimation
DOMESTIC_ID = {"CGK","SUB","DPS","MDC","UPG","BDO","PLM"}
REGIONAL    = {"SIN","KUL","BKK"}
LONG_HAUL   = {"HKG","NRT","DXB"}
ULTRA       = {"SYD","LHR"}

def flight_duration_minutes(origin, dest):
    both = {origin, dest}
    if both.issubset(DOMESTIC_ID):                          return random.randint(60, 150)
    if (both & DOMESTIC_ID) and (both & REGIONAL):          return random.randint(90, 210)
    if both.issubset(REGIONAL):                             return random.randint(60, 150)
    if (both & LONG_HAUL) and not (both & ULTRA):           return random.randint(180, 420)
    if both & ULTRA:                                        return random.randint(480, 900)
    return random.randint(150, 360)

CHANNELS      = ["WEB","MOB","OTA","GDS","CTR","AGT"]
NATIONALITIES = ["Indonesian","Singaporean","Malaysian","Australian","Japanese","Thai","British","Emirati"]
EMAIL_DOMAINS = ["gmail.com","yahoo.com","outlook.com","hotmail.com"]

# ── SCD Type-2 customer history helper ───────────────────────────────────────
# We generate a base population of 2,000 unique travellers.
# ~8% get a name/contact update (new row, new surrogate key, overlapping dates).
N_NATURAL_CUSTOMERS = 15000

def gen_src_customer():
    rows = []
    surrogate = 1
    for nat_id in range(1, N_NATURAL_CUSTOMERS + 1):
        cid   = f"CUS{nat_id:07d}"
        gender = random.choice(["M","F"])
        fn    = fake.first_name_male() if gender == "M" else fake.first_name_female()
        ln    = fake.last_name()
        dob   = fake.date_of_birth(minimum_age=18, maximum_age=75)
        nat   = random.choice(NATIONALITIES)
        email = f"{fn.lower().replace(' ','')}.{ln.lower().replace(' ','')}@{random.choice(EMAIL_DOMAINS)}"
        phone = fake.numerify("###-###-####")

        eff_start = fake.date_between(start_date="-5y", end_date="-3y")

        # SCD Type-2: ~8% of customers have an updated record
        if random.random() < 0.08:
            eff_end = eff_start + timedelta(days=random.randint(180, 730))
            rows.append({
                "customer_key": surrogate,
                "customer_id":  cid,
                "first_name":   fn, "last_name": ln, "gender": gender,
                "date_of_birth": dob, "nationality": nat,
                "email": email, "phone": phone,
                "eff_start_date": eff_start,
                "eff_end_date":   eff_end,
                "is_current":     0
            })
            surrogate += 1
            # New version: maybe changed email or phone
            email2 = f"{fn.lower()}{random.randint(10,99)}@{random.choice(EMAIL_DOMAINS)}"
            phone2 = fake.numerify("###-###-####")
            rows.append({
                "customer_key": surrogate,
                "customer_id":  cid,
                "first_name":   fn, "last_name": ln, "gender": gender,
                "date_of_birth": dob, "nationality": nat,
                "email": email2, "phone": phone2,
                "eff_start_date": eff_end + timedelta(days=1),
                "eff_end_date":   None,
                "is_current":     1
            })
        else:
            rows.append({
                "customer_key": surrogate,
                "customer_id":  cid,
                "first_name":   fn, "last_name": ln, "gender": gender,
                "date_of_birth": dob, "nationality": nat,
                "email": email, "phone": phone,
                "eff_start_date": eff_start,
                "eff_end_date":   None,
                "is_current":     1
            })
        surrogate += 1

    return pd.DataFrame(rows)

def gen_src_airport():
    return pd.DataFrame([
        {"airport_code":a[0],"airport_name":a[1],"city":a[2],"country":a[3],
         "timezone":a[4],"latitude":a[5],"longitude":a[6]} for a in AIRPORTS
    ])

def gen_src_aircraft(n=80):
    rows = []
    for i in range(1, n+1):
        at = random.choice(AIRCRAFT_TYPES)
        rows.append({
            "aircraft_id":    f"AC{i:04d}",
            "registration":   f"PK-{fake.bothify('???##').upper()}",
            "aircraft_type":  at[0],
            "manufacturer":   at[1],
            "seat_capacity":  at[2],
            "airline":        random.choice(AIRLINES),
        })
    return pd.DataFrame(rows)

def gen_src_booking(customer_df, n=15000):
    # Only use current customer records as booking actors
    current_customers = customer_df[customer_df["is_current"] == 1]
    cust_keys = current_customers["customer_key"].tolist()
    cust_key_to_id = dict(zip(current_customers["customer_key"], current_customers["customer_id"]))

    rows = []
    for i in range(1, n+1):
        ck  = random.choice(cust_keys)
        bdate = fake.date_between(start_date="-3y", end_date="today")

        # Outlier: ~2% bookings have very high (group/corporate)

        rows.append({
            "booking_id":      f"BKG{i:08d}",
            "customer_key":    ck,
            "customer_id":     cust_key_to_id[ck],
            "booking_date":    bdate,
            "booking_channel": random.choice(CHANNELS),
        })
    return pd.DataFrame(rows)

def gen_booking_channel_dim():
    rows = []
    for key, (code, name, share) in enumerate(BOOKING_CHANNELS, 1):
        rows.append({
            "channel_key": key,
            "channel_code": code,
            "channel_name": name,
            "channel_type": ("Direct" if code in ("WEB","MOB","CTR") else "Indirect"),
            "commission_rate_pct": (0 if code in ("WEB","MOB") else
                                    8 if code=="GDS" else
                                    10 if code=="OTA" else
                                    5 if code=="CTR" else 12),
            "booking_fee_usd": random.uniform(0,15),
            "typical_lead_days": {"WEB":21,"MOB":14,"GDS":30,"OTA":18,"CTR":7,"AGT":45}[code],
            "volume_share_pct": share,
        })
    return pd.DataFrame(rows)

def gen_src_flight_segment(booking_df):
    rows = []
    for _, bk in booking_df.iterrows():
        bdate = pd.to_datetime(bk["booking_date"])
        origin = random.choice(AIRPORT_CODES)
        dest   = random.choice([c for c in AIRPORT_CODES if c != origin])

        # Outlier: ~3% booked same-day (last-minute)
        days_ahead = 0 if random.random() < 0.03 else random.randint(1, 60)
        # Outlier: ~1% very far-future (advance booking > 180 days)
        if random.random() < 0.01:
            days_ahead = random.randint(181, 365)

        sched_dep = bdate + timedelta(
            days=days_ahead,
            hours=random.randint(0, 23),
            minutes=random.choice([0, 15, 30, 45])
        )
        # Delay distribution: mostly on-time, some late, rare extreme delay
        delay_min = int(np.random.choice(
            [-10, 0, 15, 30, 60, 120, 240],
            p=[0.05, 0.55, 0.15, 0.10, 0.08, 0.05, 0.02]
        ))
        actual_dep = sched_dep + timedelta(minutes=delay_min)

        status = random.choices(
            ["Flown","Cancelled","No-Show","Diverted"],
            weights=[87, 7, 4, 2]
        )[0]

        duration_min      = flight_duration_minutes(origin, dest)
        sched_arr         = sched_dep + timedelta(minutes=duration_min)
        actual_arr        = actual_dep + timedelta(minutes=duration_min)

        rows.append({
            "segment_id":               len(rows) + 1,
            "booking_id":               bk["booking_id"],
            "flight_number":            f"GA{random.randint(100,999)}",
            "origin_airport":           origin,
            "destination_airport":      dest,
            "scheduled_departure":      sched_dep,
            "actual_departure":         actual_dep,
            "scheduled_arrival":        sched_arr,
            "actual_arrival":           actual_arr,
            "flight_duration_minutes":  duration_min,
            "delay_minutes":            delay_min,
            "status":                   status,
        })
    return pd.DataFrame(rows)

# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== FLIGHT SOURCE GENERATOR v2 ===")

    cust_df    = gen_src_customer()
    airport_df = gen_src_airport()
    aircraft_df= gen_src_aircraft()
    booking_df = gen_src_booking(cust_df, n=15000)
    segment_df = gen_src_flight_segment(booking_df)
    channel_df = gen_booking_channel_dim()

    tables = {
        "src_customer":       cust_df,
        "src_airport":        airport_df,
        "src_aircraft":       aircraft_df,
        "src_booking":        booking_df,
        "src_flight_segment": segment_df,
        "src_book_channel"  : channel_df
    }
    for name, df in tables.items():
        path = os.path.join(OUTPUT_DIR, f"{name}.csv")
        df.to_csv(path, index=False)
        print(f"  {name:<22}: {len(df):,} rows x {len(df.columns)} cols")

    print(f"\nFlown segments : {(segment_df['status']=='Flown').sum():,}")
    print(f"SCD v2 records : {(cust_df['is_current']==0).sum()}")
    print("Done ✓")
