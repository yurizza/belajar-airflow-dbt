"""
HOTEL SOURCE SYSTEM (OLTP) - Refactored v4
==========================================
Perubahan dari v3:
  - created_at / updated_at ditambahkan di semua tabel dengan logika benar
  - created_at ≥ tanggal transaksi terkait (booking_date, checkin_date, dll)
  - updated_at ≥ created_at
  - Fix: koma yang hilang di dict rows (bug v3)

Reads: OUTPUT_DIR flight (src_customer, src_booking, src_flight_segment)

Output:
  src_hotel_property.csv
  src_room_inventory.csv
  src_guest_profile.csv
  src_reservation.csv
  src_hotel_stay.csv
"""

import os, random
import numpy as np
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta, date

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

TODAY = date.today()

# ── Helpers ───────────────────────────────────────────────────────────────────

def _rand_datetime_between(start: date, end: date) -> datetime:
    delta = (end - start).days
    if delta < 0:
        delta = 0
    d = start + timedelta(days=random.randint(0, delta))
    return datetime.combine(d, fake.time_object())

def _updated_at(created_at: datetime, latest_event: date = None) -> datetime:
    """
    updated_at >= created_at.
    ~30% tidak pernah diupdate → updated_at == created_at.
    latest_event: batas bawah tanggal update (misal checkin_date).
    """
    floor = max(created_at.date(), latest_event) if latest_event else created_at.date()
    if random.random() < 0.30 or floor >= TODAY:
        return created_at
    return _rand_datetime_between(floor, TODAY)


# ── Load upstream ─────────────────────────────────────────────────────────────
print("Loading flight source data...")
cust_df    = pd.read_csv(os.path.join(FLIGHT_DIR, "src_customer.csv"))
booking_df = pd.read_csv(os.path.join(FLIGHT_DIR, "src_booking.csv"))
segment_df = pd.read_csv(os.path.join(FLIGHT_DIR, "src_flight_segment.csv"))

seg_full = segment_df.merge(
    booking_df[["booking_id","customer_key"]],
    on="booking_id"
).copy()

seg_full["actual_arrival"]    = pd.to_datetime(seg_full["actual_arrival"])
seg_full["scheduled_arrival"] = pd.to_datetime(seg_full["scheduled_arrival"])
seg_full["dest_city"]         = seg_full["destination_airport"].map(AIRPORT_TO_CITY)

print(f"  Flight segments  : {len(seg_full):,}"
      f" | Unique customers: {seg_full['customer_key'].nunique():,}")


# ── Table generators ──────────────────────────────────────────────────────────

def gen_hotel_property(n=50):
    rows = []
    for i in range(1, n+1):
        brand, segment = random.choice(HOTEL_BRANDS)
        city           = random.choice(CITIES)
        is_premium     = segment in ("Luxury","Premium")

        # Hotel properti dibuat di DB antara 3-5 tahun lalu
        created_at = _rand_datetime_between(date(2019, 1, 1), date(2022, 12, 31))
        updated_at = _updated_at(created_at)

        rows.append({
            "hotel_id":       f"HTL{i:04d}",
            "hotel_name":     f"{brand} {city}",
            "brand":          brand,
            "market_segment": segment,
            "city":           city,
            "star_rating":    random.randint(4,5) if is_premium else random.randint(2,4),
            "total_rooms":    random.choice([50,80,120,200,350]),
            "created_at":     created_at,
            "updated_at":     updated_at,
        })
    return pd.DataFrame(rows)


def gen_room_inventory(hotel_df):
    rows = []
    for _, h in hotel_df.iterrows():
        # Room dibuat setelah (atau sama dengan) hotel propertinya
        hotel_created = pd.to_datetime(h["created_at"]).date()
        for rn in range(101, 101 + h["total_rooms"]):
            rt       = random.choice(ROOM_TYPES)
            surcharge = round(random.uniform(20, 50), 2) if random.random() < 0.02 else 0.0

            created_at = _rand_datetime_between(hotel_created, min(hotel_created + timedelta(days=30), TODAY))
            updated_at = _updated_at(created_at)

            rows.append({
                "room_id":        f"RM-{h['hotel_id']}-{rn}",
                "hotel_id":       h["hotel_id"],
                "room_number":    str(rn),
                "room_type_code": rt[0],
                "room_type_name": rt[1],
                "base_rate_usd":  round(rt[2] + random.uniform(-5, 15) + surcharge, 2),
                "is_active":      1 if random.random() > 0.03 else 0,
                "created_at":     created_at,
                "updated_at":     updated_at,
            })
    return pd.DataFrame(rows)


def gen_guest_profile(cust_df):
    """SCD Type-1: loyalty tier di-update in-place."""
    current = cust_df[cust_df["is_current"] == 1].copy()
    rows = []
    for _, c in current.iterrows():
        # Guest profile dibuat ≥ eff_start_date customer
        cust_eff_start = pd.to_datetime(c["eff_start_date"]).date()
        created_at     = _rand_datetime_between(
            cust_eff_start,
            min(cust_eff_start + timedelta(days=7), TODAY)
        )
        # updated_at: loyalty tier bisa berubah kapan saja setelah itu
        updated_at = _updated_at(created_at)

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
            "created_at":          created_at,
            "updated_at":          updated_at,
        })
    return pd.DataFrame(rows)


def gen_reservation(guest_df, hotel_df, n=15000):
    hotel_by_city = {city: sub.reset_index(drop=True)
                     for city, sub in hotel_df.groupby("city")}
    guest_lookup  = dict(zip(guest_df["customer_key"], guest_df["guest_id"]))

    sampled = seg_full.sample(n=n, replace=True, random_state=77).reset_index(drop=True)

    rows = []
    for i, seg_row in sampled.iterrows():
        ck        = int(seg_row["customer_key"])
        dest_city = seg_row["dest_city"]
        arrival_dt = (seg_row["actual_arrival"]
                      if pd.notnull(seg_row["actual_arrival"])
                      else seg_row["scheduled_arrival"])

        avail = hotel_by_city.get(dest_city)
        hotel_id = (avail.sample(1).iloc[0]["hotel_id"]
                    if avail is not None and not avail.empty
                    else hotel_df.sample(1).iloc[0]["hotel_id"])

        if arrival_dt.hour >= 22:
            checkin = arrival_dt.date() + timedelta(days=1)
        else:
            checkin = arrival_dt.date()

        nights   = random.randint(14, 30) if random.random() < 0.02 else random.randint(1, 7)
        checkout = checkin + timedelta(days=nights)

        days_before  = 0 if random.random() < 0.03 else random.randint(1, 90)
        booking_date = checkin - timedelta(days=days_before)

        # created_at ≥ booking_date (reservasi masuk DB saat booking dikonfirmasi)
        created_at = datetime.combine(booking_date, fake.time_object())
        # updated_at bisa berubah saat status reservasi berubah (check-in, check-out, dll)
        # pastikan updated_at ≥ created_at dan ≥ checkin jika sudah lewat
        updated_at = _updated_at(created_at, checkin if checkin <= TODAY else None)

        flight_status = seg_row["status"]
        if flight_status == "Cancelled":
            status = "Cancelled"
        elif flight_status == "No-Show":
            status = "No-Show"
        else:
            status = random.choices(
                ["Confirmed","Checked-Out"],
                weights=[10, 90]
            )[0]

        guest_id = guest_lookup.get(ck)
        if guest_id is None:
            continue

        rows.append({
            "reservation_id":   f"RSV{i+1:08d}",
            "customer_key":     ck,
            "guest_id":         guest_id,
            "hotel_id":         hotel_id,
            "segment_id":       seg_row["segment_id"],
            "booking_date":     booking_date,
            "destination_city": dest_city,
            "checkin_date":     checkin,
            "checkout_date":    checkout,
            "status":           status,
            "created_at":       created_at,
            "updated_at":       updated_at,
        })

    return pd.DataFrame(rows)


def gen_hotel_stay(res_df):
    valid = res_df[res_df["status"].isin(["Checked-Out","Confirmed"])].copy()
    rows = []
    for _, r in valid.iterrows():
        ci = pd.to_datetime(r["checkin_date"]).date()
        co = pd.to_datetime(r["checkout_date"]).date()
        planned_nights = max(1, (co - ci).days)

        shift          = random.choices([0,0,0,0,0,-1,1], weights=[50,15,15,10,5,4,1])[0]
        actual_nights  = max(1, planned_nights + shift)

        # created_at ≥ checkin_date (stay record dibuat saat tamu check-in)
        created_at = datetime.combine(ci, fake.time_object()) if ci <= TODAY else datetime.combine(TODAY, fake.time_object())
        # updated_at bisa berubah saat checkout atau ada perubahan incidental
        checkout_date = ci + timedelta(days=actual_nights)
        updated_at    = _updated_at(created_at, checkout_date if checkout_date <= TODAY else None)

        rows.append({
            "stay_id":             f"STY-{r['reservation_id']}",
            "reservation_id":      r["reservation_id"],
            "actual_checkin_date": r["checkin_date"],
            "actual_nights":       actual_nights,
            "incidental_usd":      round(random.uniform(0, 200), 2) if random.random() > 0.35 else 0.0,
            "created_at":          created_at,
            "updated_at":          updated_at,
        })
    return pd.DataFrame(rows)


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== HOTEL SOURCE GENERATOR v4 ===")
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

    # Validasi city match
    res_check = res_df.merge(hotel_df[["hotel_id","city"]], on="hotel_id", how="left")
    city_match_rate = (res_check["destination_city"] == res_check["city"]).mean()

    print(f"\nReservations generated : {len(res_df):,}")
    print(f"Stays generated        : {len(stay_df):,}")
    print(f"City match rate        : {city_match_rate:.2%}")

    # Validasi: created_at <= updated_at
    for name, df in tables.items():
        if "created_at" in df.columns and "updated_at" in df.columns:
            bad = (pd.to_datetime(df["created_at"]) > pd.to_datetime(df["updated_at"])).sum()
            print(f"  [{name}] created_at > updated_at: {bad} rows (harus 0)")

    print("Done ✓")