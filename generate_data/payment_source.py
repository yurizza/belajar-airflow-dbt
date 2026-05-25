import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os

# =====================================================
# CONFIGURATION
# =====================================================

fake = Faker("en_US")

Faker.seed(77)
random.seed(77)
np.random.seed(77)

FLIGHT_SOURCE_DIR = r"C:\Users\Dewi Oka\Documents\Dewi Document\KULIAH\S2-UGM\SEMESTER 1\Data Warehouse dan Ineligensi Bisnis\Tugas_Multidimensional Modelling\dew_ver\sumber_data\output_flight_source"

HOTEL_SOURCE_DIR = r"C:\Users\Dewi Oka\Documents\Dewi Document\KULIAH\S2-UGM\SEMESTER 1\Data Warehouse dan Ineligensi Bisnis\Tugas_Multidimensional Modelling\dew_ver\sumber_data\output_hotel_source"

OUTPUT_DIR = r"C:\Users\Dewi Oka\Documents\Dewi Document\KULIAH\S2-UGM\SEMESTER 1\Data Warehouse dan Ineligensi Bisnis\Tugas_Multidimensional Modelling\dew_ver\sumber_data\output_payment_source"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =====================================================
# LOAD SOURCE DATA
# =====================================================

customer_df = pd.read_csv(
    os.path.join(
        FLIGHT_SOURCE_DIR,
        "src_customer.csv"
    )
)

reservation_df = pd.read_csv(
    os.path.join(
        HOTEL_SOURCE_DIR,
        "src_reservation.csv"
    )
)

# =====================================================
# MASTER DATA
# =====================================================

PAYMENT_METHODS = [
    ("CC_VISA","Visa Credit Card","Credit Card","Visa",1.80,True),
    ("CC_MC","Mastercard Credit Card","Credit Card","Mastercard",1.85,True),
    ("CC_AMEX","Amex Credit Card","Credit Card","Amex",2.50,True),
    ("DC_VISA","Visa Debit Card","Debit Card","Visa",0.80,False),
    ("GOPAY","GoPay","E-Wallet","Gojek",0.70,False),
    ("OVO","OVO","E-Wallet","OVO",0.70,False),
    ("DANA","DANA","E-Wallet","DANA",0.65,False),
    ("BANK_TRF","Bank Transfer","Transfer","Bank",0.50,False),
    ("BNPL","Buy Now Pay Later","BNPL","Kredivo",3.00,True)
]

CURRENCIES = [
    ("USD","US Dollar","$",1),
    ("IDR","Indonesian Rupiah","Rp",15850),
    ("SGD","Singapore Dollar","S$",1.35),
    ("MYR","Malaysian Ringgit","RM",4.68),
    ("THB","Thai Baht","฿",36.5),
    ("JPY","Japanese Yen","¥",149.5)
]

PAYMENT_GATEWAYS = [
    "Midtrans",
    "Xendit",
    "Stripe",
    "Adyen",
    "PayPal"
]

PAYMENT_STATUS = [
    "Completed",
    "Pending",
    "Failed",
    "Refunded"
]

# =====================================================
# PAYMENT METHOD
# =====================================================

def gen_payment_method():

    rows = []

    for idx,data in enumerate(PAYMENT_METHODS,1):

        code,name,ptype,provider,fee,inst = data

        rows.append({
            "payment_method_id": idx,
            "method_code": code,
            "method_name": name,
            "payment_type": ptype,
            "provider": provider,
            "processing_fee_pct": fee,
            "supports_installment": inst
        })

    return pd.DataFrame(rows)

# =====================================================
# CURRENCY
# =====================================================

def gen_currency():

    rows = []

    for code,name,symbol,rate in CURRENCIES:

        rows.append({
            "currency_code": code,
            "currency_name": name,
            "currency_symbol": symbol,
            "usd_exchange_rate": rate
        })

    return pd.DataFrame(rows)

# =====================================================
# PAYMENT TRANSACTION
# =====================================================

def gen_payment_transaction(
        method_df,
        currency_df,
        n_rows=15000):

    rows = []

    method_ids = method_df["payment_method_id"].tolist()
    currencies = currency_df["currency_code"].tolist()

    customer_keys = customer_df["customer_key"].tolist()

    for i in range(1,n_rows+1):

        gross = round(
            random.uniform(50,1500),
            2
        )

        discount = round(
            gross * random.choice(
                [0,0.05,0.10]
            ),
            2
        )

        tax = round(
            (gross-discount)*0.11,
            2
        )

        net = round(
            gross-discount+tax,
            2
        )

        rows.append({

            "payment_id":
                f"PAY{i:08d}",

            "payment_reference":
                fake.uuid4(),

            "invoice_number":
                f"INV{i:08d}",

            "customer_key":
                random.choice(customer_keys),

            "transaction_date":
                fake.date_between(
                    start_date="-2y",
                    end_date="today"
                ),

            "transaction_time":
                fake.time(),

            "payment_method_id":
                random.choice(method_ids),

            "currency_code":
                random.choice(currencies),

            "payment_gateway":
                random.choice(
                    PAYMENT_GATEWAYS
                ),

            "payment_status":
                random.choices(
                    PAYMENT_STATUS,
                    weights=[85,8,4,3]
                )[0],

            "gross_amount_usd":
                gross,

            "discount_amount_usd":
                discount,

            "tax_amount_usd":
                tax,

            "net_amount_usd":
                net,

            "refund_amount_usd":
                round(
                    random.uniform(0,net)
                    if random.random()<0.05
                    else 0,
                    2
                ),

            "gateway_fee_usd":
                round(net*0.02,2),

            "installment_months":
                random.choice(
                    [0,0,0,3,6,12]
                ),

            "source_type":
                random.choice(
                    ["FLIGHT","HOTEL"]
                ),

            "source_reference":
                fake.bothify(
                    text="REF########"
                )
        })

    return pd.DataFrame(rows)

# =====================================================
# GENERATE DATA
# =====================================================

print("Generating payment methods...")
method_df = gen_payment_method()

print("Generating currencies...")
currency_df = gen_currency()

print("Generating transactions...")
transaction_df = gen_payment_transaction(
    method_df,
    currency_df,
    15000
)

# =====================================================
# SAVE CSV
# =====================================================

tables = {
    "src_payment_method": method_df,
    "src_currency": currency_df,
    "src_payment_transaction": transaction_df
}

for name,df in tables.items():

    path = os.path.join(
        OUTPUT_DIR,
        f"{name}.csv"
    )

    df.to_csv(
        path,
        index=False
    )

    print(
        f"{name}: {len(df):,} rows saved"
    )

print("\nPayment Source System completed.")