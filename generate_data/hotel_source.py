"""
HOTEL SOURCE SYSTEM (OLTP) - Refactored v3
==========================================
Perubahan utama dari v2:
  - checkin_date = actual_arrival.date() dari flight segment (bukan departure)
  - booking_date hotel = tanggal jauh sebelum arrival (pre-booking realistis)
  - Kota hotel dijamin cocok dengan destination_airport dari segment yang sama
  - actual_arrival digunakan sebagai anchor tunggal semua tanggal stay

Reads: /home/claude/output/flight/

Output:
  src_hotel_property.csv  - 50 hotels
  src_room_inventory.csv  - ~8,000 rooms
  src_guest_profile.csv   - mirrors customer population (SCD Type-1 loyalty)
  src_reservation.csv     - 15,000 reservations
  src_hotel_stay.csv      - ~13,500 actual stays

FK design:
  src_guest_profile  → customer_key
  src_reservation    → customer_key, hotel_id
  src_hotel_stay     → reservation_id
"""

import os, random
import numpy as np
import pandas as pd
from faker import Faker
from datetime import timedelta

Faker.seed(99); random.seed(99); np.random.seed(99)
fake = Faker("en_US")

FLIGHT_DIR = r"C:\Users\Dewi Oka\Documents\files\flight"
OUTPUT_DIR = r"C:\Users\Dewi Oka\Documents\files\hotel"
os.makedirs(OUTPUT_DIR, exist_ok=True)

AIRPORT_TO_CITY = {
    "CGK":"Jakarta",  "SUB":"Surabaya",   "DPS":"Denpasar",
    "MDC":"Manado",   "UPG":"Makassar",   "BDO":"Bandung",
    "PLM":"Palembang","SIN":"Singapore",  "KUL":"Kuala Lumpur",
    "BKK":"Bangkok",  "HKG":"Hong Kong",  "NRT":"Tokyo",
    "SYD":"Sydney",   "LHR":"London",     "DXB":"Dubai",
}
CITIES = list(AIRPORT_TO_CITY.values())

HOTEL_BRANDS = [
    ("Grand Hyatt","Luxury"),  ("Marriott","Luxury"),   ("Hilton","Premium"),
    ("Novotel","Midscale"),    ("Ibis Styles","Economy"),("Aston","Midscale"),
    ("Swiss-Belhotel","Midscale"),("Amaris","Economy"), ("Favehotel","Economy"),
]
ROOM_TYPES = [
    ("STD","Standard Room",    50.0),
    ("SUP","Superior Room",    75.0),
    ("DLX","Deluxe Room",     110.0),
    ("SUT","Suite Room",      250.0),
    ("EXE","Executive Suite", 400.0),
]

# ── Load upstream ─────────────────────────────────────────────────────────────
print("Loading flight source data...")
cust_df    = pd.read_csv(os.path.join(FLIGHT_DIR, "src_customer.csv"))
booking_df = pd.read_csv(os.path.join(FLIGHT_DIR, "src_booking.csv"))
segment_df = pd.read_csv(os.path.join(FLIGHT_DIR, "src_flight_segment.csv"))

# Gabungkan segment + customer_key, ambil yang Flown saja
# seg_full = segment_df.merge(booking_df[["booking_id","customer_key"]], on="booking_id")
# flown = seg_full[seg_full["status"] == "Flown"].copy()
# flown["actual_arrival"]    = pd.to_datetime(flown["actual_arrival"])
# flown["scheduled_arrival"] = pd.to_datetime(flown["scheduled_arrival"])
# flown["dest_city"]         = flown["destination_airport"].map(AIRPORT_TO_CITY)

# Gabungkan segment + customer_key
seg_full = segment_df.merge(
    booking_df[
        ["booking_id","customer_key"]
    ],
    on="booking_id"
).copy()

seg_full["actual_arrival"] = pd.to_datetime(
    seg_full["actual_arrival"]
)

seg_full["scheduled_arrival"] = pd.to_datetime(
    seg_full["scheduled_arrival"]
)

seg_full["dest_city"] = (
    seg_full["destination_airport"]
    .map(AIRPORT_TO_CITY)
)

print(
    f"  Flight segments: {len(seg_full):,}"
    f" | Unique customers:"
    f" {seg_full['customer_key'].nunique():,}"
)

# print(f"  Flown segments: {len(flown):,} | Unique customers: {flown['customer_key'].nunique():,}")

# ── Table generators ──────────────────────────────────────────────────────────

def gen_hotel_property(n=50):
    rows = []
    for i in range(1, n+1):
        brand, segment = random.choice(HOTEL_BRANDS)
        city = random.choice(CITIES)
        is_premium = segment in ("Luxury","Premium")
        rows.append({
            "hotel_id":       f"HTL{i:04d}",
            "hotel_name":     f"{brand} {city}",
            "brand":          brand,
            "market_segment": segment,
            "city":           city,
            "star_rating":    random.randint(4,5) if is_premium else random.randint(2,4),
            "total_rooms":    random.choice([50,80,120,200,350]),
        })
    return pd.DataFrame(rows)

def gen_room_inventory(hotel_df):
    rows = []
    for _, h in hotel_df.iterrows():
        for rn in range(101, 101 + h["total_rooms"]):
            rt = random.choice(ROOM_TYPES)
            surcharge = round(random.uniform(20, 50), 2) if random.random() < 0.02 else 0.0
            rows.append({
                "room_id":        f"RM-{h['hotel_id']}-{rn}",
                "hotel_id":       h["hotel_id"],
                "room_number":    str(rn),
                "room_type_code": rt[0],
                "room_type_name": rt[1],
                "base_rate_usd":  round(rt[2] + random.uniform(-5, 15) + surcharge, 2),
                "is_active":      1 if random.random() > 0.03 else 0,
            })
    return pd.DataFrame(rows)

def gen_guest_profile(cust_df):
    """SCD Type-1: loyalty tier di-update in-place, tidak ada history."""
    current = cust_df[cust_df["is_current"] == 1].copy()
    rows = []
    for _, c in current.iterrows():
        rows.append({
            "guest_id":            c["customer_id"],
            "customer_key":        c["customer_key"],
            "loyalty_tier":        random.choices(
                                       ["BLUE","SILVER","GOLD","PLATINUM"],
                                       weights=[68, 20, 9, 3])[0],
            "preferred_room_type": random.choice([r[0] for r in ROOM_TYPES]),
            "special_requests":    random.choice(
                                       [None, None, None, "High floor",
                                        "Non-smoking","King bed","Near elevator"]),
        })
    return pd.DataFrame(rows)

def gen_reservation(guest_df, hotel_df, n=15000):
    """
    Setiap reservasi di-anchor ke satu flown segment.
    checkin_date = actual_arrival.date() dari segment tersebut.
    Hotel dijamin berada di kota yang sama dengan destination_airport.
    """
    hotel_by_city = {city: sub.reset_index(drop=True)
                     for city, sub in hotel_df.groupby("city")}

    # Buat guest lookup: customer_key → guest_id
    guest_lookup = dict(zip(guest_df["customer_key"], guest_df["guest_id"]))

    # Sample all segments sebagai anchor
    sampled = seg_full.sample(
        n=n,
        replace=True,
        random_state=77
    ).reset_index(drop=True)
    # Sample all segments sebagai anchor

    rows = []
    for i, seg_row in sampled.iterrows():
        ck          = int(seg_row["customer_key"])
        dest_city   = seg_row["dest_city"]
        arrival_dt = ( seg_row["actual_arrival"]
                      if pd.notnull(seg_row["actual_arrival"])
                      else seg_row["scheduled_arrival"]
                      )

        # Kota hotel harus cocok dengan kota tujuan penerbangan
        avail = hotel_by_city.get(dest_city)
        if avail is not None and not avail.empty:
            hotel_id = avail.sample(1).iloc[0]["hotel_id"]
        else:
            # Fallback: ambil hotel manapun (kasus langka jika kota belum ada hotelnya)
            hotel_id = hotel_df.sample(1).iloc[0]["hotel_id"]

        # checkin = hari arrival (atau H+1 jika tiba sangat malam, >22:00)
        if arrival_dt.hour >= 22:
            checkin = arrival_dt.date() + timedelta(days=1)
        else:
            checkin = arrival_dt.date()

        # Durasi menginap: mayoritas 1-7 malam, outlier panjang ~2%
        if random.random() < 0.02:
            nights = random.randint(14, 30)   # outlier: konferensi / expat
        else:
            nights = random.randint(1, 7)

        checkout = checkin + timedelta(days=nights)

        # booking_date hotel biasanya jauh sebelum travel (1 hari s/d 90 hari sebelum checkin)
        # Outlier ~3%: last-minute booking di hari H
        days_before = 0 if random.random() < 0.03 else random.randint(1, 90)
        booking_date = checkin - timedelta(days=days_before)

        flight_status = seg_row["status"]

        if flight_status == "Cancelled":     
            status = "Cancelled"

        elif flight_status == "No-Show":        
            status = "No-Show"

        else:        
            status = random.choices(
                ["Confirmed","Checked-Out"],
                weights=[10,90]
            )[0]                
        
        guest_id = guest_lookup.get(ck)
        if guest_id is None:
            continue

        rows.append({
            "reservation_id": f"RSV{i+1:08d}",
            "customer_key":   ck,
            "guest_id":       guest_id,
            "hotel_id":       hotel_id,
            "segment_id": seg_row["segment_id"],
            "booking_date":   booking_date,
            "destination_city": dest_city,
            "checkin_date":   checkin,
            "checkout_date":  checkout,
            "status":         status
        })

    return pd.DataFrame(rows)

def gen_hotel_stay(res_df):
    """Hanya reservasi Checked-Out dan Confirmed yang punya actual stay record."""
    valid = res_df[res_df["status"].isin(["Checked-Out","Confirmed"])].copy()
    rows = []
    for _, r in valid.iterrows():
        ci = pd.to_datetime(r["checkin_date"])
        co = pd.to_datetime(r["checkout_date"])
        planned_nights = max(1, (co - ci).days)

        # Outlier: early checkout (~4%) atau tambah 1 malam (~3%)
        shift = random.choices([0,0,0,0,0,-1,1], weights=[50,15,15,10,5,4,1])[0]
        actual_nights = max(1, planned_nights + shift)

        rows.append({
            "stay_id":             f"STY-{r['reservation_id']}",
            "reservation_id":      r["reservation_id"],
            "actual_checkin_date": r["checkin_date"],
            "actual_nights":       actual_nights,
            "incidental_usd":      round(random.uniform(0, 200), 2) if random.random() > 0.35 else 0.0,
        })
    return pd.DataFrame(rows)


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== HOTEL SOURCE GENERATOR v3 ===")
    hotel_df  = gen_hotel_property()
    room_df   = gen_room_inventory(hotel_df)
    guest_df  = gen_guest_profile(cust_df)
    res_df    = gen_reservation(guest_df, hotel_df, n=15000)
    stay_df   = gen_hotel_stay(res_df)

    tables = {
        "src_hotel_property": hotel_df,
        "src_room_inventory": room_df,
        "src_guest_profile":  guest_df,
        "src_reservation":    res_df,
        "src_hotel_stay":     stay_df,
    }
    for name, df in tables.items():
        path = os.path.join(OUTPUT_DIR, f"{name}.csv")
        df.to_csv(path, index=False)
        print(f"  {name:<22}: {len(df):,} rows x {len(df.columns)} cols")

    # Validasi: cek bahwa checkin_date sesuai dengan arrival date
    res_check = res_df.merge(
    hotel_df[["hotel_id","city"]],
    on="hotel_id",
    how="left"
    )

    city_match_rate = (
    res_check["destination_city"]
    ==
    res_check["city"]
    ).mean()

    print(f"\nReservations generated : {len(res_df):,}")
    print(f"Stays generated        : {len(stay_df):,}")
    print(f"City match rate        : {city_match_rate:.2%}")

    print("Done ✓")
