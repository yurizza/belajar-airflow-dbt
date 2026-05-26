"""
CAR RENTAL SOURCE SYSTEM (OLTP) - Refactored v3
================================================
Perubahan utama dari v2:
  - scheduled_pickup = actual_arrival + 1-3 jam (waktu customs & baggage claim)
  - pickup_airport   = destination_airport dari segment (bukan fallback acak)
  - Matching: segment dipilih berdasarkan (customer_key, destination_airport)
    yang cocok dengan kota hotel di reservation yang di-anchor

Reads: /home/claude/output/flight/
       /home/claude/output/hotel/

Output:
  src_vehicle.csv      - 80 vehicles
  src_driver.csv       - 60 drivers
  src_rental_order.csv - 15,000 orders
  src_rental_trip.csv  - ~12,450 trips (completed orders)

FK design:
  src_rental_order → customer_key
  src_rental_order → reservation_id  (kota & tanggal anchor)
  src_rental_order → segment_id      (pickup airport & waktu arrival anchor)
  src_rental_trip  → order_id
"""

import os, random
import numpy as np
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta

Faker.seed(7); random.seed(7); np.random.seed(7)
fake = Faker("en_US")

FLIGHT_DIR = r"C:\Users\Dewi Oka\Documents\files\flight"
HOTEL_DIR  = r"C:\Users\Dewi Oka\Documents\files\hotel"
OUTPUT_DIR = r"C:\Users\Dewi Oka\Documents\files\rental"
os.makedirs(OUTPUT_DIR, exist_ok=True)

AIRPORT_TO_CITY = {
    "CGK":"Jakarta",  "SUB":"Surabaya",   "DPS":"Denpasar",
    "MDC":"Manado",   "UPG":"Makassar",   "BDO":"Bandung",
    "PLM":"Palembang","SIN":"Singapore",  "KUL":"Kuala Lumpur",
    "BKK":"Bangkok",  "HKG":"Hong Kong",  "NRT":"Tokyo",
    "SYD":"Sydney",   "LHR":"London",     "DXB":"Dubai",
}
CITY_TO_AIRPORT = {v: k for k, v in AIRPORT_TO_CITY.items()}

VEHICLE_TYPES = [
    ("SDN_ECO","Sedan Economy",    "Sedan",   "Toyota", "Vios",         4, 35),
    ("SDN_MID","Sedan Mid-Size",   "Sedan",   "Honda",  "Civic",        4, 50),
    ("MPV_STD","MPV Standard",     "MPV",     "Toyota", "Avanza",       7, 40),
    ("MPV_PRE","MPV Premium",      "MPV",     "Toyota", "Alphard",      7,120),
    ("SUV_STD","SUV Standard",     "SUV",     "Honda",  "CR-V",         5, 65),
    ("SUV_LUX","SUV Luxury",       "SUV",     "Toyota", "Land Cruiser", 5,150),
    ("VAN_STD","Minivan Standard", "Van",     "Toyota", "HiAce",       12, 80),
    ("ELC_STD","Electric Sedan",   "Electric","Hyundai","Ioniq 6",      4, 70),
]

# ── Load upstream ─────────────────────────────────────────────────────────────
print("Loading upstream data...")
booking_df   = pd.read_csv(os.path.join(FLIGHT_DIR, "src_booking.csv"))
segment_df   = pd.read_csv(os.path.join(FLIGHT_DIR, "src_flight_segment.csv"))
res_df       = pd.read_csv(os.path.join(HOTEL_DIR,  "src_reservation.csv"))
hotel_df     = pd.read_csv(os.path.join(HOTEL_DIR,  "src_hotel_property.csv"))

# seg_full segments + customer_key + dest_city + arrival datetime
# seg_full = segment_df.merge(booking_df[["booking_id","customer_key"]], on="booking_id")
# seg_full = seg_full[seg_full["status"] == "seg_full"].copy()
# seg_full["actual_arrival"] = pd.to_datetime(seg_full["actual_arrival"])
# seg_full["dest_city"]      = seg_full["destination_airport"].map(AIRPORT_TO_CITY)

# All segments + customer_key + city
seg_full = segment_df.merge(
    booking_df[["booking_id","customer_key"]],
    on="booking_id").copy()

seg_full["actual_arrival"] = pd.to_datetime(
    seg_full["actual_arrival"])

seg_full["scheduled_arrival"] = pd.to_datetime(
    seg_full["scheduled_arrival"])

seg_full["dest_city"] = (
    seg_full["destination_airport"]
    .map(AIRPORT_TO_CITY))

# Reservasi hotel dengan nama kota
res_with_city = res_df.merge(hotel_df[["hotel_id","city"]], on="hotel_id")
valid_res = res_with_city[res_with_city["status"] == "Checked-Out"].copy()
valid_res["checkin_dt"] = pd.to_datetime(valid_res["checkin_date"])

print(f"  seg_full segments : {len(seg_full):,}")
print(f"  Valid hotel res: {len(valid_res):,}")

# Index cepat: (customer_key, dest_city) → list segment rows
segment_lookup = {
    int(r["segment_id"]): r
    for _, r in seg_full.iterrows()
}

# ── Table generators ──────────────────────────────────────────────────────────

def gen_vehicle(n=80):
    rows = []
    for i in range(1, n+1):
        vt = random.choice(VEHICLE_TYPES)
        rate = round(vt[6] * random.uniform(0.9, 1.3), 2)
        rows.append({
            "vehicle_id":    f"VHC{i:05d}",
            "plate":         fake.bothify("B #### ???", letters="ABCDEFGHJKLMNPRSTUVWXYZ").upper(),
            "type_code":     vt[0],
            "type_name":     vt[1],
            "category":      vt[2],
            "brand":         vt[3],
            "model":         vt[4],
            "seat_capacity": vt[5],
            "rate_usd_day":  rate,
            "prod_year":     random.randint(2018, 2024),
            "status":        random.choices(["Active","Maintenance","Inactive"], weights=[88,8,4])[0],
        })
    return pd.DataFrame(rows)

def gen_driver(n=60):
    rows = []
    for i in range(1, n+1):
        g = random.choice(["M","F"])
        rows.append({
            "driver_id":   f"DRV{i:05d}",
            "driver_name": fake.name_male() if g=="M" else fake.name_female(),
            "gender":      g,
            "license_no":  fake.bothify("SIM-##########"),
            "license_type":random.choice(["A","B1","B2"]),
            "languages":   "; ".join(random.choice([
                               ["Indonesian"],
                               ["Indonesian","English"],
                               ["Indonesian","English","Mandarin"],
                               ["Indonesian","English","Japanese"]])),
            "rating":      round(random.uniform(3.2, 5.0), 1),
            "total_trips": random.randint(10, 3000),
            "is_active":   random.choices([1,0], weights=[90,10])[0],
            "joined_date": fake.date_between(start_date="-5y", end_date="-3m"),
        })
    return pd.DataFrame(rows)

def gen_rental_order(vehicle_df, driver_df, n=15000):
    active_veh = vehicle_df[vehicle_df["status"]=="Active"]["vehicle_id"].tolist()
    active_drv = driver_df[driver_df["is_active"]==1]["driver_id"].tolist()

    # Anchor: sample dari valid hotel reservations
    sampled_res = valid_res.sample(n=n, replace=True, random_state=55).reset_index(drop=True)

    rows = []

    for i, res in sampled_res.iterrows():
        ck          = int(res["customer_key"])
        hotel_city  = res["city"]
        res_id      = res["reservation_id"]
        checkin_dt  = res["checkin_dt"]   # datetime anchor dari hotel

        # ── Cari segment yang cocok: customer_key DAN kota destinasi = kota hotel ──
        seg_row = segment_lookup.get(int(res["segment_id"]))

        if seg_row is None:
            continue

        segment_id     = int(seg_row["segment_id"])
        pickup_airport = seg_row["destination_airport"]   # selalu bandara kedatangan
        arrival_dt = (seg_row["actual_arrival"]
                      if pd.notnull(seg_row["actual_arrival"])
                      else seg_row["scheduled_arrival"])
        flight_status = seg_row["status"]

        # ── scheduled_pickup = actual_arrival + 1-3 jam (customs + baggage) ──
        # Outlier ~3%: langsung naik (e.g. no baggage, fast track)
        if random.random() < 0.03:
            buffer_minutes = random.randint(15, 30)
        else:
            buffer_minutes = random.randint(60, 180)

        scheduled_pickup = arrival_dt + timedelta(minutes=buffer_minutes)

        # order_date bisa sama hari atau beberapa hari sebelum keberangkatan
        order_date = checkin_dt.date() - timedelta(days=random.randint(0, 14))

        if flight_status == "Cancelled":
            order_status = "Cancelled"
        elif flight_status == "No-Show":
            order_status = "No-Show"
        else:
            order_status = random.choices(
                ["Completed","Cancelled"], weights=[92,8]
                )[0]                        
        rows.append({
            "order_id":         f"RNT{i+1:08d}",
            "customer_key":     ck,
            "reservation_id":   res_id,
            "segment_id":       segment_id,
            "vehicle_id":       random.choice(active_veh),
            "driver_id":        random.choice(active_drv),
            "pickup_airport":   pickup_airport,
            "order_date":       order_date,
            "scheduled_pickup": scheduled_pickup,
            "order_status":     order_status,
            "booking_source":   random.choice(["Website","Mobile App","OTA","Call Center"]),
            "special_request":  random.choice([None, None, "Child Seat","Extra Luggage","Meet & Greet Sign"]),
            "estimated_rate_usd": round(random.uniform(25, 200), 2),
        })
    return pd.DataFrame(rows)

def gen_rental_trip(order_df):
    done = order_df[order_df["order_status"] == "Completed"].copy()
    rows = []
    for _, o in done.iterrows():
        sched = pd.to_datetime(o["scheduled_pickup"])

        # Delay: distribusi realistis — kebanyakan on-time, ekor panjang ke kanan
        delay = int(np.random.choice(
            [-5, 0, 5, 15, 30, 60, 120],
            p=[0.05, 0.45, 0.20, 0.15, 0.08, 0.05, 0.02]
        ))
        actual_pickup  = sched + timedelta(minutes=delay)
        duration_min   = random.randint(15, 120)
        actual_dropoff = actual_pickup + timedelta(minutes=duration_min)
        distance_km    = round(random.uniform(5, 80), 1)

        base      = float(o["estimated_rate_usd"])
        surcharge = round(base * random.choice([0,0,0,0,0.05,0.10,0.20]), 2)
        total     = round(base + surcharge, 2)

        trip_status = random.choices(
            ["Completed","Delayed","Incident"],
            weights=[91, 7, 2]
        )[0]

        rows.append({
            "trip_id":          len(rows) + 1,
            "order_id":         o["order_id"],
            "actual_pickup":    actual_pickup,
            "actual_dropoff":   actual_dropoff,
            "delay_minutes":    delay,
            "duration_minutes": duration_min,
            "distance_km":      distance_km,
            "base_charge_usd":  base,
            "surcharge_usd":    surcharge,
            "total_charge_usd": total,
            "trip_status":      trip_status,
            "driver_rating":    round(random.uniform(3.0, 5.0), 1) if trip_status == "Completed" else None,
        })
    return pd.DataFrame(rows)


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== CAR RENTAL SOURCE GENERATOR v3 ===")
    veh_df   = gen_vehicle()
    drv_df   = gen_driver()
    order_df = gen_rental_order(veh_df, drv_df, n=15000)
    trip_df  = gen_rental_trip(order_df)

    tables = {
        "src_vehicle":      veh_df,
        "src_driver":       drv_df,
        "src_rental_order": order_df,
        "src_rental_trip":  trip_df,
    }
    for name, df in tables.items():
        path = os.path.join(OUTPUT_DIR, f"{name}.csv")
        df.to_csv(path, index=False)
        print(f"  {name:<22}: {len(df):,} rows x {len(df.columns)} cols")
    print("Done ✓")
