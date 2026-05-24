"""
Payments Data Warehouse - Synthetic Data Generator
════════════════════════════════════════════════════
Skema Star Schema:
  - dim_date          (shared dari airline)
  - dim_time_of_day   (shared dari airline)
  - dim_customer      (shared dari airline dim_passenger)
  - dim_payment_method
  - dim_currency
  - fact_payment_transaction  (~15,000 rows)

Degenerate Dimensions di Fact:
  payment_reference, invoice_number,
  payment_status, payment_gateway, installment_months

FK ke domain lain:
  flight_segment_key → fact_segment_flight_activity.segment_key
  hotel_stay_key     → hotel_fact_hotel_stay.hotel_stay_key
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random, os

fake = Faker('en_US')
Faker.seed(77); np.random.seed(77); random.seed(77)

AIRLINE_DIR = "D:\S2\DWIB\Multidimensional-Modelling\output"
OUTPUT_DIR  = "D:\S2\DWIB\Multidimensional-Modelling\output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# LOAD SHARED DATA
# ─────────────────────────────────────────────

print("Loading shared dimensions & fact tables...")
dim_date      = pd.read_csv(f"{AIRLINE_DIR}/dim_date.csv")
dim_time      = pd.read_csv(f"{AIRLINE_DIR}/dim_time_of_day.csv")
dim_passenger = pd.read_csv(f"{AIRLINE_DIR}/dim_passenger.csv")
fact_airline  = pd.read_csv(f"{AIRLINE_DIR}/fact_segment_flight_activity.csv")
fact_hotel    = pd.read_csv(f"{AIRLINE_DIR}/hotel_fact_hotel_stay.csv")

date_key_map  = dim_date.set_index("full_date")["date_key"].to_dict()
date_keys_all = dim_date["date_key"].values
time_keys_all = dim_time["time_key"].values

# Lookup dari airline fact
airline_amount  = fact_airline.set_index("segment_key")["total_revenue_usd"].to_dict()
airline_pax     = fact_airline.set_index("segment_key")["passenger_key"].to_dict()
airline_datekey = fact_airline.set_index("segment_key")["scheduled_departure_date_key"].to_dict()
airline_conf    = fact_airline.set_index("segment_key")["confirmation_number"].to_dict()

# Lookup dari hotel fact
hotel_amount    = fact_hotel.set_index("hotel_stay_key")["total_bill_usd"].to_dict()
hotel_cust      = fact_hotel.set_index("hotel_stay_key")["customer_key"].to_dict()
hotel_datekey   = fact_hotel.set_index("hotel_stay_key")["reservation_date_key"].to_dict()
hotel_conf      = fact_hotel.set_index("hotel_stay_key")["confirmation_number"].to_dict()

# ─────────────────────────────────────────────
# REFERENCE DATA
# ─────────────────────────────────────────────

PAYMENT_METHODS = [
    # code, name, type, provider, card_brand, is_digital, vol_share, proc_fee_pct
    ("CC_VISA",    "Visa Credit Card",       "Credit Card",   "Visa",       "Visa",        False, 0.22, 1.80),
    ("CC_MC",      "Mastercard Credit Card", "Credit Card",   "Mastercard", "Mastercard",  False, 0.18, 1.85),
    ("CC_AMEX",    "Amex Credit Card",       "Credit Card",   "Amex",       "Amex",        False, 0.06, 2.50),
    ("DC_VISA",    "Visa Debit Card",        "Debit Card",    "Visa",       "Visa",        False, 0.10, 0.80),
    ("DC_MC",      "Mastercard Debit Card",  "Debit Card",    "Mastercard", "Mastercard",  False, 0.08, 0.75),
    ("GOPAY",      "GoPay",                  "E-Wallet",      "Gojek",      None,          True,  0.10, 0.70),
    ("OVO",        "OVO",                    "E-Wallet",      "OVO",        None,          True,  0.08, 0.70),
    ("DANA",       "DANA",                   "E-Wallet",      "DANA",       None,          True,  0.05, 0.65),
    ("SHOPEEPAY",  "ShopeePay",             "E-Wallet",      "Shopee",     None,          True,  0.04, 0.65),
    ("BANK_TRF",   "Bank Transfer",          "Bank Transfer", "Various",    None,          False, 0.05, 0.50),
    ("BNPL",       "Buy Now Pay Later",      "BNPL",          "Kredivo",    None,          True,  0.03, 3.00),
    ("VOUCHER",    "Travel Voucher/Credit",  "Voucher",       "Internal",   None,          False, 0.01, 0.00),
]

CURRENCIES = [
    # code, name, symbol, usd_rate
    ("USD", "US Dollar",         "$",   1.0000),
    ("IDR", "Indonesian Rupiah", "Rp",  15850.0),
    ("SGD", "Singapore Dollar",  "S$",  1.3500),
    ("MYR", "Malaysian Ringgit", "RM",  4.6800),
    ("THB", "Thai Baht",         "฿",   36.50),
    ("JPY", "Japanese Yen",      "¥",   149.50),
    ("AUD", "Australian Dollar", "A$",  1.5300),
    ("AED", "UAE Dirham",        "د.إ", 3.6725),
    ("GBP", "British Pound",     "£",   0.7900),
    ("HKD", "Hong Kong Dollar",  "HK$", 7.8200),
]

PAYMENT_GATEWAYS   = ["Midtrans", "Xendit", "Stripe", "Adyen", "DOKU", "PayPal", "Internal"]
GATEWAY_PROBS      = [0.33,       0.28,     0.12,     0.10,    0.08,   0.06,     0.03]
GATEWAY_FEES       = { "Midtrans": 0.020, "Xendit": 0.018, "Stripe": 0.029,
                       "Adyen": 0.015, "DOKU": 0.022, "PayPal": 0.034, "Internal": 0.000 }

PAYMENT_STATUSES   = ["Completed", "Pending", "Failed", "Refunded",
                       "Partial Refund", "Chargeback", "Expired", "Cancelled"]
STATUS_PROBS       = [0.82,         0.04,      0.05,     0.04,
                       0.02,           0.01,        0.01,     0.01]

# Loyalty points per USD (varies by tier)
LOYALTY_EARN_RATE  = {"None": 1, "Silver": 2, "Gold": 3, "Platinum": 5}
LOYALTY_REDEEM_CPP = 0.01  # 1 point = $0.01


# ─────────────────────────────────────────────
# DIM 1: Payment Method (SCD Type 2)
# ─────────────────────────────────────────────

def gen_payment_method_dim():
    rows = []
    key  = 1
    for code, name, ptype, provider, card_brand, is_digital, vol_share, fee_pct in PAYMENT_METHODS:
        supports_inst = ptype in ("Credit Card", "BNPL")
        base = dict(
            payment_method_key   = key,
            method_code          = code,
            method_name          = name,
            payment_type         = ptype,
            provider             = provider,
            card_brand           = card_brand if card_brand else "N/A",
            is_digital_wallet    = is_digital,
            processing_fee_pct   = fee_pct,
            volume_share_pct     = vol_share,
            supports_installment = supports_inst,
            max_installment_months = 24 if ptype == "BNPL" else 12 if ptype == "Credit Card" else 0,
            supports_refund      = ptype != "Voucher",
            daily_limit_usd      = (5000 if is_digital else 50000 if ptype == "Credit Card"
                                    else 20000 if ptype == "Debit Card" else 100000),
            scd_effective_date   = "2022-01-01",
            scd_expiry_date      = "9999-12-31",
            scd_current_flag     = True,
            scd_version          = 1,
        )
        rows.append(base)
        key += 1

        # ~25% metode mengalami perubahan fee/limit → SCD2 versi 2
        if random.random() < 0.25:
            rows[-1]["scd_expiry_date"]  = "2023-03-31"
            rows[-1]["scd_current_flag"] = False
            v2 = rows[-1].copy()
            v2.update(
                payment_method_key = key,
                processing_fee_pct = round(fee_pct * random.uniform(0.90, 1.20), 2),
                daily_limit_usd    = int(base["daily_limit_usd"] * random.uniform(1.1, 1.5)),
                scd_effective_date = "2023-04-01",
                scd_expiry_date    = "9999-12-31",
                scd_current_flag   = True,
                scd_version        = 2,
            )
            rows.append(v2)
            key += 1

    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# DIM 2: Currency
# ─────────────────────────────────────────────

def gen_currency_dim():
    rows = []
    for key, (code, name, symbol, rate) in enumerate(CURRENCIES, 1):
        rows.append(dict(
            currency_key        = key,
            currency_code       = code,
            currency_name       = name,
            currency_symbol     = symbol,
            usd_exchange_rate   = rate,
            rate_effective_date = "2024-01-01",
            is_base_currency    = (code == "USD"),
            region              = (
                "Southeast Asia" if code in ("IDR","SGD","MYR","THB") else
                "East Asia"      if code in ("JPY","HKD")              else
                "Oceania"        if code == "AUD"                      else
                "Middle East"    if code == "AED"                      else
                "Europe"         if code == "GBP"                      else
                "Americas"
            ),
        ))
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# FACT: Payment Transaction
# ─────────────────────────────────────────────

def gen_payment_fact(method_df, currency_df, n_rows=15000):

    # ── Method lookups
    method_curr   = method_df[method_df["scd_current_flag"] == True].copy()
    method_keys   = method_curr["payment_method_key"].values
    method_vols   = method_curr["volume_share_pct"].values
    method_info   = method_curr.set_index("payment_method_key")

    # ── Currency lookups
    currency_keys  = currency_df["currency_key"].values
    currency_info  = currency_df.set_index("currency_key")
    # IDR dominan karena mayoritas transaksi Indonesia
    curr_probs     = [0.12, 0.55, 0.08, 0.06, 0.05, 0.04, 0.03, 0.03, 0.02, 0.02]

    # ── Loyalty lookups dari dim_passenger
    pax_tier  = dim_passenger.set_index("passenger_key")["loyalty_tier"].to_dict()
    pax_miles = dim_passenger.set_index("passenger_key")["loyalty_miles_balance"].to_dict()

    # ── Source pools
    airline_seg_keys = fact_airline["segment_key"].values
    hotel_stay_keys  = fact_hotel["hotel_stay_key"].values

    # Split n_rows proporsional ke jumlah fact rows masing-masing domain
    n_airline = int(n_rows * len(airline_seg_keys) /
                    (len(airline_seg_keys) + len(hotel_stay_keys)))
    n_hotel   = n_rows - n_airline

    rows = []

    def build_row(pay_key, source, source_id, cust_key, base_date_key, gross_usd, ref_num):

        # ── Dimensi
        mk  = int(np.random.choice(method_keys, p=method_vols / method_vols.sum()))
        ck  = int(np.random.choice(currency_keys, p=curr_probs))
        gw  = np.random.choice(PAYMENT_GATEWAYS, p=GATEWAY_PROBS)
        st  = np.random.choice(PAYMENT_STATUSES, p=STATUS_PROBS)

        # ── Tanggal payment: 0–7 hari sebelum/pada tanggal sumber
        idx       = int(np.searchsorted(date_keys_all, base_date_key))
        idx       = max(0, min(len(date_keys_all)-1, idx + random.randint(-7, 0)))
        pay_dk    = int(date_keys_all[idx])

        # ── Waktu payment (acak dari time dim)
        pay_tk    = int(np.random.choice(time_keys_all))

        # ── Nilai transaksi
        discount  = round(gross_usd * np.random.choice([0, 0.05, 0.10, 0.15, 0.20],
                          p=[0.60, 0.15, 0.12, 0.08, 0.05]), 2)
        ex_rate   = float(currency_info.loc[ck, "usd_exchange_rate"])
        tax_rate  = random.uniform(0.08, 0.13)
        taxable   = gross_usd - discount
        tax_amt   = round(taxable * tax_rate, 2)
        net_amt   = round(taxable + tax_amt, 2)

        gw_fee    = round(net_amt * GATEWAY_FEES[gw], 2)

        # Refund hanya relevan jika status membutuhkan
        refund = 0.0
        if   st == "Refunded":       refund = net_amt
        elif st == "Partial Refund": refund = round(net_amt * random.uniform(0.1, 0.5), 2)
        elif st == "Chargeback":     refund = net_amt

        # ── Loyalty
        tier           = pax_tier.get(int(cust_key), "None")
        earn_rate      = LOYALTY_EARN_RATE.get(tier, 1)
        pts_earned     = int(net_amt * earn_rate) if st == "Completed" else 0

        # Redeem points: 30% transaksi pakai points (jika tier bukan None)
        pts_balance    = int(pax_miles.get(int(cust_key), 0))
        pts_used       = 0
        if tier != "None" and st in ("Completed","Partial Refund") and random.random() < 0.30:
            max_redeem = min(pts_balance, int(net_amt / LOYALTY_REDEEM_CPP * 0.5))
            pts_used   = random.randint(0, max(0, max_redeem))

        # ── Installment
        supports_inst  = bool(method_info.loc[mk, "supports_installment"])
        max_inst       = int(method_info.loc[mk, "max_installment_months"])
        inst_months    = 0
        if supports_inst and net_amt >= 50 and random.random() < 0.20:
            inst_months = random.choice([m for m in [3,6,12,24] if m <= max_inst])

        # ── Outlier injection ~2%
        if random.random() < 0.02:
            otype = random.choice(["zero", "huge", "negative_discount"])
            if   otype == "zero":             gross_usd = 0.0; tax_amt = 0.0; net_amt = 0.0
            elif otype == "huge":             gross_usd = round(gross_usd * random.uniform(8,20), 2)
            elif otype == "negative_discount":discount   = round(-gross_usd * 0.05, 2)  # surcharge

        return dict(
            # ── Surrogate key
            payment_key              = pay_key,

            # ── FK ke dimensi waktu
            payment_date_key         = pay_dk,
            payment_time_key         = pay_tk,

            # ── FK ke dimensi lain
            customer_key             = int(cust_key),
            payment_method_key       = mk,
            currency_key             = ck,

            # ── FK ke domain transaksi (NULL jika tidak relevan)
            flight_segment_key       = int(source_id) if source == "airline" else None,
            hotel_stay_key           = int(source_id) if source == "hotel"   else None,

            # ── Degenerate Dimensions
            payment_reference        = f"PAY{fake.numerify('###########')}",
            invoice_number           = f"INV-{fake.bothify('??###-######').upper()}",
            payment_status           = st,
            payment_gateway          = gw,
            installment_months       = inst_months,

            # ── Measures
            gross_amount_usd         = round(gross_usd, 2),
            discount_amount_usd      = discount,
            tax_amount_usd           = tax_amt,
            net_amount_usd           = round(net_amt, 2),
            refund_amount_usd        = refund,
            gateway_fee_usd          = gw_fee,
            loyalty_points_used      = pts_used,
            loyalty_points_earned    = pts_earned,

            # ── Turunan / informasi tambahan
            transaction_amount_local = round(net_amt * ex_rate, 2),
            source_reference_num     = ref_num,
            transaction_source = random.choice(["AIRLINE", "HOTEL", "PARTNER", "AGENT"]),
        )

    # ── Generate airline payments
    print(f"  Generating {n_airline:,} airline payment rows...")
    sampled_air = np.random.choice(airline_seg_keys, size=n_airline, replace=True)
    for pk, sid in enumerate(sampled_air, start=1):
        rows.append(build_row(
            pay_key      = pk,
            source       = "airline",
            source_id    = int(sid),
            cust_key     = airline_pax.get(int(sid), int(np.random.choice(dim_passenger["passenger_key"].values))),
            base_date_key= airline_datekey.get(int(sid), int(np.random.choice(date_keys_all))),
            gross_usd    = float(airline_amount.get(int(sid), random.uniform(80, 600))),
            ref_num      = str(airline_conf.get(int(sid), fake.bothify("CNF########"))),
        ))

    # ── Generate hotel payments
    print(f"  Generating {n_hotel:,} hotel payment rows...")
    sampled_hotel = np.random.choice(hotel_stay_keys, size=n_hotel, replace=True)
    for i, sid in enumerate(sampled_hotel, start=n_airline+1):
        rows.append(build_row(
            pay_key      = i,
            source       = "hotel",
            source_id    = int(sid),
            cust_key     = hotel_cust.get(int(sid), int(np.random.choice(dim_passenger["passenger_key"].values))),
            base_date_key= hotel_datekey.get(int(sid), int(np.random.choice(date_keys_all))),
            gross_usd    = float(hotel_amount.get(int(sid), random.uniform(80, 1000))),
            ref_num      = str(hotel_conf.get(int(sid), fake.bothify("HCF########"))),
        ))

    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# GENERATE SEMUA TABEL
# ─────────────────────────────────────────────

print("\nGenerating Payment Method Dimension (SCD2)...")
method_df   = gen_payment_method_dim()

print("Generating Currency Dimension...")
currency_df = gen_currency_dim()

print("Generating Payment Fact Table (~15,000 rows)...")
fact_df     = gen_payment_fact(method_df, currency_df, n_rows=15000)


# ─────────────────────────────────────────────
# SAVE TO CSV
# ─────────────────────────────────────────────

tables = {
    "pay_dim_payment_method"     : method_df,
    "pay_dim_currency"           : currency_df,
    "pay_fact_payment_transaction": fact_df,
}

print()
for name, df in tables.items():
    path = f"{OUTPUT_DIR}/{name}.csv"
    df.to_csv(path, index=False)
    print(f"  {name}: {len(df):,} rows x {len(df.columns)} cols → {path}")


# ─────────────────────────────────────────────
# SUMMARY REPORT
# ─────────────────────────────────────────────

completed = fact_df[fact_df["payment_status"] == "Completed"]

print(f"""
════════════════════════════════════════════
  PAYMENTS DATASET SUMMARY
════════════════════════════════════════════
  Total rows             : {len(fact_df):,}
    └─ Airline payments  : {(fact_df['transaction_source']=='AIRLINE').sum():,}
    └─ Hotel payments    : {(fact_df['transaction_source']=='HOTEL').sum():,}

  Gross revenue (USD)    : ${fact_df['gross_amount_usd'].sum():,.0f}
  Total discounts        : ${fact_df['discount_amount_usd'].sum():,.0f}
  Total tax collected    : ${fact_df['tax_amount_usd'].sum():,.0f}
  Total net revenue      : ${fact_df['net_amount_usd'].sum():,.0f}
  Total refunds issued   : ${fact_df['refund_amount_usd'].sum():,.0f}
  Total gateway fees     : ${fact_df['gateway_fee_usd'].sum():,.0f}

  Avg net amount (USD)   : ${fact_df['net_amount_usd'].mean():.2f}
  Loyalty points earned  : {fact_df['loyalty_points_earned'].sum():,}
  Loyalty points used    : {fact_df['loyalty_points_used'].sum():,}
  Installment txn        : {(fact_df['installment_months'] > 0).sum():,}

  Payment status:
{fact_df['payment_status'].value_counts().to_string()}

  Payment gateway:
{fact_df['payment_gateway'].value_counts().to_string()}

  Top payment methods:
{fact_df['payment_method_key'].map(method_df[method_df['scd_current_flag']==True].set_index('payment_method_key')['method_name']).value_counts().head(6).to_string()}

  Outliers (net=0)       : {(fact_df['net_amount_usd']==0).sum()}
  Outliers (net>5000)    : {(fact_df['net_amount_usd']>5000).sum()}
  SCD2 method versions   : {method_df['scd_version'].value_counts().to_dict()}

  LINK KE DATASET LAIN:
  flight_segment_key  <-> fact_segment_flight_activity.segment_key
  hotel_stay_key      <-> hotel_fact_hotel_stay.hotel_stay_key
  customer_key        <-> dim_passenger.passenger_key
  payment_date_key    <-> dim_date.date_key
  payment_time_key    <-> dim_time_of_day.time_key
════════════════════════════════════════════
""")
