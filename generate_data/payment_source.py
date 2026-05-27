"""
PAYMENT SOURCE SYSTEM (OLTP) - Refactored v3
=============================================
Perubahan dari v2:
  - created_at / updated_at ditambahkan di semua tabel
  - src_payment_method  : created_at = tanggal metode aktif di sistem
  - src_currency        : created_at = statis, master data lama
  - src_payment_transaction:
      created_at = transaction_date (saat transaksi masuk DB)
      updated_at ≥ created_at (berubah jika status berubah: Pending→Completed, refund, dll)

FK design:
  src_payment_transaction → customer_key
  src_payment_transaction → payment_method_id
  src_payment_transaction → source_reference (booking_id / reservation_id / order_id)
"""

import os, random
import numpy as np
import pandas as pd
from faker import Faker
from datetime import datetime, timedelta, date

Faker.seed(13); random.seed(13); np.random.seed(13)
fake = Faker("en_US")

FLIGHT_DIR = r"C:\Users\Dewi Oka\Documents\files\flight"
HOTEL_DIR  = r"C:\Users\Dewi Oka\Documents\files\hotel"
RENTAL_DIR = r"C:\Users\Dewi Oka\Documents\files\rental"
OUTPUT_DIR = r"C:\Users\Dewi Oka\Documents\files\payment"
os.makedirs(OUTPUT_DIR, exist_ok=True)

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
    Transaksi payment sering diupdate (status berubah), ~20% tidak berubah.
    latest_event: batas bawah tanggal update.
    """
    floor = max(created_at.date(), latest_event) if latest_event else created_at.date()
    if random.random() < 0.20 or floor >= TODAY:
        return created_at
    return _rand_datetime_between(floor, TODAY)


# ── Load upstream ─────────────────────────────────────────────────────────────
print("Loading upstream data...")

booking_df = pd.read_csv(os.path.join(FLIGHT_DIR, "src_booking.csv"))
segment_df = pd.read_csv(os.path.join(FLIGHT_DIR, "src_flight_segment.csv"))
res_df     = pd.read_csv(os.path.join(HOTEL_DIR,  "src_reservation.csv"))
order_df   = pd.read_csv(os.path.join(RENTAL_DIR, "src_rental_order.csv"))

segment_status = (
    segment_df.groupby("booking_id")["status"]
    .apply(lambda x: "Cancelled" if "Cancelled" in x.values else "Completed")
    .reset_index(name="flight_status")
)
booking_df = booking_df.merge(segment_status, on="booking_id", how="left")


# ── Master data ────────────────────────────────────────────────────────────────
PAYMENT_METHODS = [
    (1, "CC_VISA",  "Visa Credit Card",       "Credit Card", "Visa",      1.80, True),
    (2, "CC_MC",    "Mastercard Credit Card",  "Credit Card", "Mastercard",1.85, True),
    (3, "CC_AMEX",  "Amex Credit Card",        "Credit Card", "Amex",      2.50, True),
    (4, "DC_VISA",  "Visa Debit Card",         "Debit Card",  "Visa",      0.80, False),
    (5, "GOPAY",    "GoPay",                   "E-Wallet",    "Gojek",     0.70, False),
    (6, "OVO",      "OVO",                     "E-Wallet",    "OVO",       0.70, False),
    (7, "DANA",     "DANA",                    "E-Wallet",    "DANA",      0.65, False),
    (8, "BANK_TRF", "Bank Transfer",           "Transfer",    "Bank",      0.50, False),
    (9, "BNPL",     "Buy Now Pay Later",       "BNPL",        "Kredivo",   3.00, True),
]

CURRENCIES = [
    ("USD","US Dollar",         "$",  1.0),
    ("IDR","Indonesian Rupiah", "Rp", 15850.0),
    ("SGD","Singapore Dollar",  "S$", 1.35),
    ("MYR","Malaysian Ringgit", "RM", 4.68),
    ("THB","Thai Baht",         "฿",  36.5),
    ("JPY","Japanese Yen",      "¥",  149.5),
]
CURRENCY_CODES = [c[0] for c in CURRENCIES]
GATEWAYS = ["Midtrans","Xendit","Stripe","Adyen","PayPal"]


def gen_payment_method():
    rows = []
    for m in PAYMENT_METHODS:
        # Metode pembayaran didaftarkan ke sistem antara 5-3 tahun lalu
        created_at = _rand_datetime_between(date(2019, 1, 1), date(2022, 12, 31))
        updated_at = _updated_at(created_at)
        rows.append({
            "payment_method_id":    m[0],
            "method_code":          m[1],
            "method_name":          m[2],
            "payment_type":         m[3],
            "provider":             m[4],
            "processing_fee_pct":   m[5],
            "supports_installment": m[6],
            "created_at":           created_at,
            "updated_at":           updated_at,
        })
    return pd.DataFrame(rows)


def gen_currency():
    rows = []
    for c in CURRENCIES:
        # Master currency, data lama, statis
        created_at = _rand_datetime_between(date(2019, 1, 1), date(2020, 6, 30))
        # Kurs bisa berubah → updated_at bisa lebih baru
        updated_at = _updated_at(created_at)
        rows.append({
            "currency_code":     c[0],
            "currency_name":     c[1],
            "symbol":            c[2],
            "usd_exchange_rate": c[3],
            "created_at":        created_at,
            "updated_at":        updated_at,
        })
    return pd.DataFrame(rows)


def _make_tx(pid, ck, tx_date, source_type, source_ref, gross_range, status_weights, gateway_fee_pct):
    """Build a single payment transaction dict."""
    method_id = random.randint(1, 9)
    currency  = random.choice(CURRENCY_CODES)

    if random.random() < 0.02:
        gross = round(random.uniform(1500, 5000), 2)
    else:
        gross = round(random.uniform(*gross_range), 2)

    discount = round(gross * random.choice([0,0,0,0.05,0.08,0.10]), 2)
    tax      = round((gross - discount) * 0.11, 2)
    net      = round(gross - discount + tax, 2)

    status = random.choices(
        ["Completed","Pending","Failed","Refunded"],
        weights=status_weights
    )[0]
    refund = (net if status=="Refunded" and random.random()<0.9
              else round(random.uniform(0.3*net, net), 2) if status=="Refunded"
              else 0.0)

    installment = 0
    if status == "Completed":
        m_data = PAYMENT_METHODS[method_id - 1]
        if m_data[6]:
            installment = random.choice([0, 0, 3, 6, 12])

    # tx_date bisa berupa string atau date/datetime — normalisasi ke date
    if isinstance(tx_date, str):
        tx_date_obj = pd.to_datetime(tx_date).date()
    elif isinstance(tx_date, datetime):
        tx_date_obj = tx_date.date()
    else:
        tx_date_obj = tx_date  # already date

    # created_at = saat transaksi masuk DB (= hari transaksi, jam acak)
    created_at = datetime.combine(tx_date_obj, fake.time_object())

    # updated_at ≥ created_at
    # Transaksi Pending/Failed sering diupdate → lebih mungkin updated_at berbeda
    if status in ("Pending", "Failed", "Refunded"):
        updated_at = _updated_at(created_at, tx_date_obj)
    else:
        updated_at = _updated_at(created_at)

    return {
        "payment_id":         f"PAY{pid:08d}",
        "payment_reference":  str(fake.uuid4()),
        "invoice_number":     f"INV{pid:08d}",
        "customer_key":       int(ck),
        "transaction_date":   str(tx_date_obj),
        "transaction_time":   fake.time(),
        "payment_method_id":  method_id,
        "currency_code":      currency,
        "payment_gateway":    random.choice(GATEWAYS),
        "payment_status":     status,
        "gross_amount_usd":   gross,
        "discount_usd":       discount,
        "tax_usd":            tax,
        "net_amount_usd":     net,
        "refund_amount_usd":  refund,
        "gateway_fee_usd":    round(net * gateway_fee_pct, 2),
        "installment_months": installment,
        "source_type":        source_type,
        "source_reference":   source_ref,
        "created_at":         created_at,
        "updated_at":         updated_at,
    }


def gen_payment_transactions(method_df, currency_df):
    rows = []
    pid = 1

    # ── 1. Flight payments ──
    for _, r in booking_df.iterrows():
        fs = r["flight_status"]
        sw = [0,0,0,100] if fs=="Cancelled" else [94,3,2,1]
        rows.append(_make_tx(
            pid=pid, ck=r["customer_key"],
            tx_date=r["booking_date"],
            source_type="FLIGHT", source_ref=r["booking_id"],
            gross_range=(100, 900),
            status_weights=sw,
            gateway_fee_pct=0.020,
        ))
        pid += 1

    # ── 2. Hotel payments ──
    for _, r in res_df.iterrows():
        rs = r["status"]
        if rs=="Cancelled":  sw=[0,0,0,100]
        elif rs=="No-Show":  sw=[85,0,10,5]
        else:                sw=[93,3,2,2]
        rows.append(_make_tx(
            pid=pid, ck=r["customer_key"],
            tx_date=r["booking_date"],
            source_type="HOTEL", source_ref=r["reservation_id"],
            gross_range=(80, 1200),
            status_weights=sw,
            gateway_fee_pct=0.018,
        ))
        pid += 1

    # ── 3. Car rental payments ──
    for _, r in order_df.iterrows():
        os_ = r["order_status"]
        if os_=="Completed":   sw=[96,1,1,2]
        elif os_=="Cancelled": sw=[0,0,0,100]
        else:                  sw=[90,0,0,10]   # No-Show
        rows.append(_make_tx(
            pid=pid, ck=r["customer_key"],
            tx_date=r["order_date"],
            source_type="CAR_RENTAL", source_ref=r["order_id"],
            gross_range=(25, 200),
            status_weights=sw,
            gateway_fee_pct=0.022,
        ))
        pid += 1

    # ── Multi-attempt outlier: inject ~2% duplicate Failed+Completed pairs ──
    df = pd.DataFrame(rows)
    completed = df[df["payment_status"] == "Completed"].sample(frac=0.02, random_state=5)
    retries   = completed.copy()
    retries["payment_id"]        = [f"PAY{pid+j:08d}" for j in range(len(retries))]
    retries["payment_reference"] = [str(fake.uuid4()) for _ in range(len(retries))]
    retries["invoice_number"]    = retries["payment_id"].str.replace("PAY","INV")
    retries["payment_status"]    = "Failed"
    retries["net_amount_usd"]    = 0.0
    retries["gateway_fee_usd"]   = 0.0
    # updated_at retry = sama dengan created_at (langsung failed)

    df = pd.concat([df, retries], ignore_index=True)
    return df


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== PAYMENT SOURCE GENERATOR v3 ===")
    method_df   = gen_payment_method()
    currency_df = gen_currency()
    tx_df       = gen_payment_transactions(method_df, currency_df)

    tables = {
        "src_payment_method":      method_df,
        "src_currency":            currency_df,
        "src_payment_transaction": tx_df,
    }
    for name, df in tables.items():
        path = os.path.join(OUTPUT_DIR, f"{name}.csv")
        df.to_csv(path, index=False)
        print(f"  {name:<28}: {len(df):,} rows x {len(df.columns)} cols")

    print(f"\n  Flight txns     : {(tx_df['source_type']=='FLIGHT').sum():,}")
    print(f"  Hotel txns      : {(tx_df['source_type']=='HOTEL').sum():,}")
    print(f"  Car rental txns : {(tx_df['source_type']=='CAR_RENTAL').sum():,}")
    print(f"  Retry (Failed)  : {(tx_df['payment_status']=='Failed').sum():,}")
    print(f"  Refunded        : {(tx_df['payment_status']=='Refunded').sum():,}")

    # Validasi: created_at <= updated_at
    for name, df in tables.items():
        if "created_at" in df.columns and "updated_at" in df.columns:
            bad = (pd.to_datetime(df["created_at"]) > pd.to_datetime(df["updated_at"])).sum()
            print(f"  [{name}] created_at > updated_at: {bad} rows (harus 0)")

    print("Done ✓")