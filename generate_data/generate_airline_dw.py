"""
Airline Flight Activity Data Warehouse - Synthetic Data Generator
Schema: Segment-Level Flight Activity Fact + 8 Dimension Tables
Features: 10,000+ transactions, outliers, SCD scenarios, realistic distributions
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta, date
import random
import os

fake = Faker('en_US')
Faker.seed(42)
np.random.seed(42)
random.seed(42)

OUTPUT_DIR = r"D:\S2_DW\travel\output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# REFERENCE DATA
# ─────────────────────────────────────────────

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



CABIN_CLASSES = [
    ("F","First Class",0.04,5.5),
    ("C","Business Class",0.10,2.8),
    ("W","Premium Economy",0.08,1.5),
    ("Y","Economy Class",0.78,1.0),
]

BOOKING_CHANNELS = [
    ("WEB","Website Direct",0.35),
    ("MOB","Mobile App",0.30),
    ("GDS","Global Distribution System",0.15),
    ("OTA","Online Travel Agency",0.12),
    ("CTR","Call Center",0.05),
    ("AGT","Travel Agent",0.03),
]

FARE_BASIS_CODES = [
    ("YOWUS","Economy Flexible","Y",1.20),
    ("YOWRS","Economy Restricted","Y",0.85),
    ("BSSAVE","Economy Promo","Y",0.55),
    ("WOWBUS","Premium Eco Flex","W",1.30),
    ("CLXBUS","Business Flex","C",2.50),
    ("CLXSAV","Business Saver","C",1.90),
    ("FLXFST","First Flex","F",4.00),
    ("GRPECO","Group Economy","Y",0.70),
]

# ─────────────────────────────────────────────
# DIMENSION 1: Date Dimension
# ─────────────────────────────────────────────

def gen_date_dim(start="2022-01-01", end="2024-12-31"):
    rows = []
    d = datetime.strptime(start, "%Y-%m-%d").date()
    end_d = datetime.strptime(end, "%Y-%m-%d").date()
    key = 1
    while d <= end_d:
        is_holiday = d.month == 12 and d.day in [25,31] or d.month == 1 and d.day == 1
        rows.append({
            "date_key": key,
            "full_date": d.isoformat(),
            "day_of_week": d.strftime("%A"),
            "day_num": d.isoweekday(),
            "week_num": d.isocalendar()[1],
            "month_num": d.month,
            "month_name": d.strftime("%B"),
            "quarter": (d.month - 1) // 3 + 1,
            "year": d.year,
            "is_weekend": d.weekday() >= 5,
            "is_holiday": is_holiday,
            "season": (["Summer","Summer","Fall","Fall","Fall","Winter","Winter","Winter","Spring","Spring","Spring","Summer"][d.month-1]),
        })
        d += timedelta(days=1)
        key += 1
    return pd.DataFrame(rows)

# ─────────────────────────────────────────────
# DIMENSION 2: Time-of-Day Dimension
# ─────────────────────────────────────────────

def gen_time_dim():
    rows = []
    for h in range(24):
        for m in range(0, 60, 15):
            key = h * 100 + m
            if 6 <= h < 12:   period = "Morning"
            elif 12 <= h < 17: period = "Afternoon"
            elif 17 <= h < 21: period = "Evening"
            else:               period = "Night"
            rows.append({
                "time_key": key,
                "hour": h,
                "minute": m,
                "time_str": f"{h:02d}:{m:02d}",
                "period_of_day": period,
                "is_peak_hour": (7 <= h <= 9) or (17 <= h <= 19),
            })
    return pd.DataFrame(rows)

# ─────────────────────────────────────────────
# DIMENSION 3: Airport Dimension (with SCD Type 2)
# ─────────────────────────────────────────────

def gen_airport_dim():
    rows = []
    key = 1
    for ap in AIRPORTS:
        code, name, city, country, tz, lat, lon = ap
        # Current record
        rows.append({
            "airport_key": key,
            "airport_code": code,
            "airport_name": name,
            "city": city,
            "country": country,
            "timezone": tz,
            "latitude": lat,
            "longitude": lon,
            "terminal_count": random.randint(1,5),
            "gate_count": random.randint(10,80),
            "hub_type": random.choice(["Primary Hub","Secondary Hub","Regional","International"]),
            # SCD2 fields
            "scd_effective_date": "2022-01-01",
            "scd_expiry_date": "9999-12-31",
            "scd_current_flag": True,
            "scd_version": 1,
        })
        key += 1
        # Simulate SCD2 change: some airports get terminal expansion
        if random.random() < 0.4:
            rows[-1]["scd_expiry_date"] = "2023-06-30"
            rows[-1]["scd_current_flag"] = False
            updated = rows[-1].copy()
            updated["airport_key"] = key
            updated["terminal_count"] += random.randint(1,2)
            updated["gate_count"] += random.randint(5,15)
            updated["scd_effective_date"] = "2023-07-01"
            updated["scd_expiry_date"] = "9999-12-31"
            updated["scd_current_flag"] = True
            updated["scd_version"] = 2
            rows.append(updated)
            key += 1
    return pd.DataFrame(rows)

# ─────────────────────────────────────────────
# DIMENSION 4: Passenger Dimension (with SCD Type 1)
# ─────────────────────────────────────────────

def gen_passenger_dim(n=3000):
    rows = []
    for i in range(1, n+1):
        gender = random.choice(["M","F"])
        dob = fake.date_of_birth(minimum_age=18, maximum_age=75)
        age = (date(2024,12,31) - dob).days // 365
        rows.append({
            "passenger_key": i,
            "passenger_id": f"PAX{i:07d}",
            "first_name": fake.first_name_male() if gender=="M" else fake.first_name_female(),
            "last_name": fake.last_name(),
            "gender": gender,
            "date_of_birth": dob.isoformat(),
            "age_group": ("18-25" if age<26 else "26-35" if age<36 else "36-50" if age<51 else "51-65" if age<66 else "65+"),
            "nationality": random.choices(
                ["Indonesian","Singaporean","Malaysian","Australian","Japanese","British","American","Other"],
                weights=[55,10,8,5,5,5,5,7])[0],
            "loyalty_tier": random.choices(
                ["None","Silver","Gold","Platinum"],
                weights=[50,25,15,10])[0],
            "loyalty_miles_balance": int(np.random.exponential(5000)),
            "email": fake.email(),
            "phone_country": random.choice(["+62","+65","+60","+61"]),
        })
    return pd.DataFrame(rows)

# ─────────────────────────────────────────────
# DIMENSION 5: Passenger Profile Dimension (SCD Type 2)
# ─────────────────────────────────────────────

def gen_passenger_profile_dim(n=3000):
    rows = []
    for i in range(1, n+1):
        base_tier = random.choices(["None","Silver","Gold","Platinum"], weights=[50,25,15,10])[0]
        rows.append({
            "profile_key": i,
            "passenger_id": f"PAX{i:07d}",
            "frequent_flyer_num": f"FF{i:08d}",
            "preferred_seat": random.choice(["Window","Aisle","No Preference"]),
            "preferred_meal": random.choice(["Standard","Vegetarian","Halal","Vegan","Child","None"]),
            "special_assistance": random.choices(["None","Wheelchair","WCHR","WCHC"], weights=[80,10,6,4])[0],
            "marketing_consent": random.choice([True,False]),
            "lifetime_segments_flown": int(np.random.exponential(12)),
            "lifetime_miles_earned": int(np.random.exponential(30000)),
            "customer_segment": random.choice(["Business Traveler","Leisure","Student","Senior","Family"]),
            "scd_effective_date": "2022-01-01",
            "scd_expiry_date": "9999-12-31",
            "scd_current_flag": True,
            "scd_version": 1,
        })
        # SCD2: ~20% of passengers upgrade tier mid-period
        if random.random() < 0.20:
            rows[-1]["scd_expiry_date"] = "2023-03-31"
            rows[-1]["scd_current_flag"] = False
            upgraded = rows[-1].copy()
            upgraded["profile_key"] = n + i
            tier_map = {"None":"Silver","Silver":"Gold","Gold":"Platinum","Platinum":"Platinum"}
            upgraded["customer_segment"] = random.choice(["Business Traveler","Leisure","Student","Senior","Family"])
            upgraded["lifetime_segments_flown"] += random.randint(5,20)
            upgraded["lifetime_miles_earned"] += random.randint(5000,20000)
            upgraded["scd_effective_date"] = "2023-04-01"
            upgraded["scd_expiry_date"] = "9999-12-31"
            upgraded["scd_current_flag"] = True
            upgraded["scd_version"] = 2
            rows.append(upgraded)
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# DIMENSION 7: Class of Service Dimension
# ─────────────────────────────────────────────

def gen_class_of_service_dim():
    rows = []
    key = 1
    for airline in AIRLINES:
        for code, name, share, mult in CABIN_CLASSES:
            rows.append({
                "class_key": key,
                "service_code": code,
                "service_name": name,
                "airline": airline,
                "cabin_width_cm": {"F":90,"C":60,"W":45,"Y":32}[code],
                "seat_pitch_cm": {"F":203,"C":152,"W":97,"Y":79}[code],
                "baggage_allowance_kg": {"F":40,"C":30,"W":23,"Y":20}[code],
                "lounge_access": code in ("F","C"),
                "priority_boarding": code in ("F","C","W"),
                "meal_included": code in ("F","C","W"),
                "seat_share_pct": share,
                "fare_multiplier": mult,
            })
            key += 1
    return pd.DataFrame(rows)

# ─────────────────────────────────────────────
# DIMENSION 8: Booking Channel Dimension
# ─────────────────────────────────────────────

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

# ─────────────────────────────────────────────
# DIMENSION 9: Fare Basis Dimension
# ─────────────────────────────────────────────

def gen_fare_basis_dim():
    rows = []
    for key, (code, name, cabin, mult) in enumerate(FARE_BASIS_CODES, 1):
        rows.append({
            "fare_key": key,
            "fare_basis_code": code,
            "fare_name": name,
            "cabin_code": cabin,
            "fare_multiplier": mult,
            "is_refundable": mult > 1.0,
            "is_changeable": mult > 0.7,
            "advance_purchase_days": (0 if mult>1.1 else 3 if mult>0.9 else 7 if mult>0.7 else 14),
            "minimum_stay_days": (0 if mult>1.1 else 0 if mult>0.9 else 2 if mult>0.7 else 5),
            "blackout_periods": mult < 0.70,
        })
    return pd.DataFrame(rows)

# ─────────────────────────────────────────────
# FACT TABLE: Segment-Level Flight Activity
# ─────────────────────────────────────────────

def gen_fact_table(date_df, time_df, airport_df, passenger_df,
                   profile_df,  class_df, channel_df, fare_df,
                   n_rows=15000):

    date_keys = date_df["date_key"].values
    time_keys = time_df["time_key"].values
    # Only current airport records
    ap_curr = airport_df[airport_df["scd_current_flag"]==True]
    airport_keys = ap_curr["airport_key"].values
    airport_codes = ap_curr.set_index("airport_key")["airport_code"].to_dict()
    passenger_keys = passenger_df["passenger_key"].values
    profile_curr = profile_df[profile_df["scd_current_flag"]==True]
    profile_keys = profile_curr["profile_key"].values
    class_keys    = class_df["class_key"].values
    class_fare    = class_df.set_index("class_key")["fare_multiplier"].to_dict()
    channel_keys  = channel_df["channel_key"].values
    channel_comm  = channel_df.set_index("channel_key")["commission_rate_pct"].to_dict()
    fare_keys     = fare_df["fare_key"].values
    fare_mult     = fare_df.set_index("fare_key")["fare_multiplier"].to_dict()
    fare_cabin    = fare_df.set_index("fare_key")["cabin_code"].to_dict()

    # Base fare by route distance (USD)
    def base_fare(orig_key, dest_key):
        oc = airport_codes.get(orig_key,"CGK")
        dc = airport_codes.get(dest_key,"SIN")
        domestic = {"CGK","SUB","DPS","MDC","UPG","BDO","PLM"}
        if oc in domestic and dc in domestic:
            return np.random.lognormal(4.5, 0.4)   # ~$90-200
        elif oc in {"SIN","KUL","BKK"}|domestic or dc in {"SIN","KUL","BKK"}|domestic:
            return np.random.lognormal(5.2, 0.45)  # ~$180-400
        else:
            return np.random.lognormal(6.0, 0.5)   # ~$400-1500

    rows = []
    for i in range(1, n_rows+1):
        # Weighted date: more bookings on weekends and holiday months (Jun-Aug, Dec)
        month_weights = [0.07,0.07,0.08,0.08,0.08,0.10,0.10,0.10,0.08,0.08,0.08,0.08]
        sampled_date = date_df.sample(1, weights=date_df["month_num"].map(
            lambda m: month_weights[m-1])).iloc[0]

        dep_date_key = int(sampled_date["date_key"])
        dep_time_key = int(np.random.choice(time_keys, p=None))

        # Actual departure: mostly on time, some delays
        delay_min = int(np.random.choice(
            [0, np.random.randint(1,30), np.random.randint(30,120), np.random.randint(120,360)],
            p=[0.60, 0.25, 0.12, 0.03]))
        act_dep_date_key = dep_date_key
        act_dep_time_key = dep_time_key  # simplified

        orig_key = int(np.random.choice(airport_keys))
        dest_key = int(np.random.choice([k for k in airport_keys if k!=orig_key]))

        pax_key  = int(np.random.choice(passenger_keys))
        prof_key = int(np.random.choice(profile_keys))
        ch_key   = int(np.random.choice(channel_keys,
                        p=channel_df["volume_share_pct"].values/channel_df["volume_share_pct"].sum()))
        fk       = int(np.random.choice(fare_keys))

        # Match class key roughly to fare cabin
        cabin_code = fare_cabin[fk]
        eligible   = class_df[class_df["service_code"]==cabin_code]["class_key"].values
        ck = int(np.random.choice(eligible)) if len(eligible)>0 else int(np.random.choice(class_keys))

        # Revenue calculation
        bf   = base_fare(orig_key, dest_key)
        fare = bf * class_fare[ck] * fare_mult[fk]
        pfc  = round(random.uniform(5, 30), 2)         # Passenger Facility Charge
        apt  = round(fare * random.uniform(0.04, 0.10), 2)
        gov  = round(fare * random.uniform(0.05, 0.15), 2)
        bag  = round(np.random.choice([0,0,25,50,75,100], p=[0.55,0.15,0.12,0.10,0.05,0.03]), 2)
        upg  = round(np.random.choice([0,0,0,50,100,200,500], p=[0.70,0.10,0.05,0.07,0.04,0.03,0.01]), 2)
        txn  = round(channel_comm[ch_key] / 100 * fare, 2)

     
        miles = int(np.random.uniform(200, 8000))
        earned = int(miles * class_fare[ck] * fare_mult[fk] * 0.5)

        # Outlier injection (~2%)
        if random.random() < 0.02:
            fare  *= random.choice([0.01, 5.0, 10.0])   # near-zero or very expensive
            bag   = round(random.uniform(500, 2000), 2)  # excess baggage

        # Cancelled / no-show flag
        status = np.random.choice(
            ["Flown","Cancelled","No-Show","Diverted"],
            p=[0.88, 0.06, 0.04, 0.02])

        rows.append({
            "segment_key": i,
            "scheduled_departure_date_key": dep_date_key,
            "scheduled_departure_time_key": dep_time_key,
            "actual_departure_date_key": act_dep_date_key,
            "actual_departure_time_key": act_dep_time_key,
            "passenger_key": pax_key,
            "passenger_profile_key": prof_key,
            "segment_origin_airport_key": orig_key,
            "segment_destination_airport_key": dest_key,
  
            "class_of_service_key": ck,
            "fare_basis_key": fk,
            "booking_channel_key": ch_key,
            # Degenerate dimensions
            "confirmation_number": f"CNF{fake.bothify('########')}",
            "ticket_number": f"TKT{fake.numerify('##########')}",
            "segment_sequence_number": random.randint(1,4),
            "flight_number": f"GA{random.randint(100,999)}",
            # Facts
            "base_fare_revenue_usd": round(fare, 2),
            "passenger_facility_charges_usd": pfc,
            "airport_tax_usd": apt,
            "government_tax_usd": gov,
            "baggage_charges_usd": bag,
            "upgrade_fees_usd": upg,
            "transaction_fees_usd": txn,
            "total_revenue_usd": round(fare+pfc+apt+gov+bag+upg+txn, 2),
            "segment_miles_flown": miles,
            "segment_miles_earned": earned,
            "delay_minutes": delay_min,
            "seat_capacity": cap,
            "flight_status": status,
            "load_factor_pct": round(np.random.beta(6,2)*100, 1),
        })

    return pd.DataFrame(rows)

# ─────────────────────────────────────────────
# GENERATE ALL TABLES
# ─────────────────────────────────────────────

print("Generating dimension tables...")
date_df    = gen_date_dim()
time_df    = gen_time_dim()
airport_df = gen_airport_dim()
pax_df     = gen_passenger_dim(3000)
profile_df = gen_passenger_profile_dim(3000)

class_df   = gen_class_of_service_dim()
channel_df = gen_booking_channel_dim()
fare_df    = gen_fare_basis_dim()

print("Generating fact table (15,000 rows)...")
fact_df = gen_fact_table(date_df, time_df, airport_df, pax_df,
                          profile_df,  class_df, channel_df, fare_df,
                          n_rows=15000)

# ─────────────────────────────────────────────
# SAVE TO CSV
# ─────────────────────────────────────────────

tables = {
    "dim_date": date_df,
    "dim_time_of_day": time_df,
    "dim_airport": airport_df,
    "dim_passenger": pax_df,
    "dim_passenger_profile": profile_df,

    "dim_class_of_service": class_df,
    "dim_booking_channel": channel_df,
    "dim_fare_basis": fare_df,
    "fact_segment_flight_activity": fact_df,
}

for name, df in tables.items():
    path = f"{OUTPUT_DIR}/{name}.csv"
    df.to_csv(path, index=False)
    print(f"  {name}: {len(df):,} rows x {len(df.columns)} cols → {path}")

print("\nAll tables saved.")
print(f"\nSummary:")
print(f"  Fact rows: {len(fact_df):,}")
print(f"  Total revenue (sample): ${fact_df['total_revenue_usd'].sum():,.0f}")
print(f"  Avg base fare: ${fact_df['base_fare_revenue_usd'].mean():.2f}")
print(f"  Flight status dist:\n{fact_df['flight_status'].value_counts().to_string()}")
print(f"  Delay outliers (>120min): {(fact_df['delay_minutes']>120).sum()}")
print(f"  SCD2 airport versions: {airport_df['scd_version'].value_counts().to_dict()}")
print(f"  SCD2 profile versions: {profile_df['scd_version'].value_counts().to_dict()}")
