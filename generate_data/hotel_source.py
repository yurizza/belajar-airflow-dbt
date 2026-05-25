# =====================================================
# HOTEL SOURCE SYSTEM (OLTP)
# =====================================================

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

Faker.seed(99)
random.seed(99)
np.random.seed(99)

FLIGHT_SOURCE_DIR = r"C:\Users\Dewi Oka\Documents\Dewi Document\KULIAH\S2-UGM\SEMESTER 1\Data Warehouse dan Ineligensi Bisnis\Tugas_Multidimensional Modelling\dew_ver\sumber_data\output_flight_source"

OUTPUT_DIR = r"C:\Users\Dewi Oka\Documents\Dewi Document\KULIAH\S2-UGM\SEMESTER 1\Data Warehouse dan Ineligensi Bisnis\Tugas_Multidimensional Modelling\dew_ver\sumber_data\output_hotel_source"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# =====================================================
# LOAD SHARED CUSTOMER
# =====================================================

print("Loading customer source data...")

customer_df = pd.read_csv(
    os.path.join(
        FLIGHT_SOURCE_DIR,
        "src_customer.csv"
    )
)

# =====================================================
# REFERENCE DATA
# =====================================================

CITIES = [
    "Jakarta",
    "Surabaya",
    "Bali",
    "Bandung",
    "Makassar",
    "Manado",
    "Singapore",
    "Kuala Lumpur",
    "Bangkok",
    "Tokyo",
    "Sydney",
    "Dubai",
    "London",
    "Hong Kong"
]

HOTEL_BRANDS = [
    "Marriott",
    "Hilton",
    "Hyatt",
    "Sheraton",
    "Novotel",
    "Ibis",
    "Swiss-Belhotel",
    "Grand Mercure",
    "Aston",
    "Harris",
    "Aloft",
    "Pop Hotel"
]

ROOM_TYPES = [
    ("STD","Standard"),
    ("SUP","Superior"),
    ("DLX","Deluxe"),
    ("EXC","Executive"),
    ("SUT","Suite"),
    ("FAM","Family")
]

# =====================================================
# SOURCE HOTEL PROPERTY
# =====================================================

def gen_src_hotel_property():

    rows = []

    for i in range(1,51):

        brand = random.choice(HOTEL_BRANDS)
        city  = random.choice(CITIES)

        rows.append({

            "hotel_id":
                f"HTL{i:05d}",

            "hotel_name":
                f"{brand} {city}",

            "brand":
                brand,

            "city":
                city,

            "star_rating":
                random.randint(2,5),

            "total_rooms":
                random.randint(80,500),

            "has_pool":
                random.choice([True,False]),

            "has_gym":
                random.choice([True,False]),

            "created_at":
                fake.date_between(
                    start_date="-3y",
                    end_date="today"
                ),

            "updated_at":
                fake.date_between(
                    start_date="-1y",
                    end_date="today"
                )
        })

    return pd.DataFrame(rows)

# =====================================================
# SOURCE ROOM INVENTORY
# =====================================================

def gen_src_room_inventory(hotel_df):

    rows = []

    room_id = 1

    for _, hotel in hotel_df.iterrows():

        for room_code, room_name in ROOM_TYPES:

            rows.append({

                "room_inventory_id":
                    room_id,

                "hotel_id":
                    hotel["hotel_id"],

                "room_type_code":
                    room_code,

                "room_type_name":
                    room_name,

                "room_count":
                    random.randint(10,80),

                "base_rate_usd":
                    round(
                        random.uniform(50,500),
                        2
                    )
            })

            room_id += 1

    return pd.DataFrame(rows)

# =====================================================
# SOURCE GUEST PROFILE
# =====================================================

def gen_src_guest_profile():

    rows = []

    for _, cust in customer_df.iterrows():

        rows.append({

            "guest_id":
                cust["customer_id"],

            "customer_key":
                cust["customer_key"],

            "preferred_room_type":
                random.choice(
                    ["STD","SUP","DLX","EXC","SUT"]
                ),

            "smoking_preference":
                random.choices(
                    ["Non-Smoking","Smoking"],
                    weights=[85,15]
                )[0],

            "special_request":
                random.choice([
                    "None",
                    "Baby Cot",
                    "Late Check-In",
                    "High Floor",
                    "Near Elevator"
                ]),

            "created_at":
                fake.date_between(
                    start_date="-2y",
                    end_date="today"
                )
        })

    return pd.DataFrame(rows)

# =====================================================
# SOURCE RESERVATION
# =====================================================

def gen_src_reservation(
        guest_df,
        hotel_df,
        n_rows=15000):

    rows = []

    for i in range(1,n_rows+1):

        guest = guest_df.sample(1).iloc[0]
        hotel = hotel_df.sample(1).iloc[0]

        booking_date = fake.date_between(
            start_date="-2y",
            end_date="today"
        )

        arrival_date = (
            booking_date +
            timedelta(
                days=random.randint(1,60)
            )
        )

        nights = random.randint(1,7)

        departure_date = (
            arrival_date +
            timedelta(days=nights)
        )

        rows.append({

            "reservation_id":
                f"RSV{i:08d}",

            "guest_id":
                guest["guest_id"],

            "hotel_id":
                hotel["hotel_id"],

            "booking_date":
                booking_date,

            "arrival_date":
                arrival_date,

            "departure_date":
                departure_date,

            "reservation_status":
                random.choices(
                    [
                        "Confirmed",
                        "Cancelled",
                        "No Show"
                    ],
                    weights=[85,10,5]
                )[0],

            "booking_source":
                random.choice([
                    "Website",
                    "Mobile App",
                    "OTA",
                    "Travel Agent"
                ])
        })

    return pd.DataFrame(rows)

# =====================================================
# SOURCE HOTEL STAY
# =====================================================

def gen_src_hotel_stay(reservation_df):

    rows = []

    stay_id = 1

    confirmed = reservation_df[
        reservation_df["reservation_status"]
        == "Confirmed"
    ]

    for _, res in confirmed.iterrows():

        nights = (
            pd.to_datetime(
                res["departure_date"]
            )
            -
            pd.to_datetime(
                res["arrival_date"]
            )
        ).days

        room_charge = round(
            random.uniform(80,1500),
            2
        )

        extra_charge = round(
            random.uniform(0,250),
            2
        )

        rows.append({

            "stay_id":
                stay_id,

            "reservation_id":
                res["reservation_id"],

            "checkin_date":
                res["arrival_date"],

            "checkout_date":
                res["departure_date"],

            "number_of_nights":
                nights,

            "room_charge_usd":
                room_charge,

            "extra_charge_usd":
                extra_charge,

            "total_bill_usd":
                round(
                    room_charge +
                    extra_charge,
                    2
                )
        })

        stay_id += 1

    return pd.DataFrame(rows)

# =====================================================
# GENERATE SOURCE TABLES
# =====================================================

print("Generating hotel property...")
hotel_df = gen_src_hotel_property()

print("Generating room inventory...")
room_df = gen_src_room_inventory(
    hotel_df
)

print("Generating guest profile...")
guest_df = gen_src_guest_profile()

print("Generating reservation...")
reservation_df = gen_src_reservation(
    guest_df,
    hotel_df,
    n_rows=15000
)

print("Generating hotel stay...")
stay_df = gen_src_hotel_stay(
    reservation_df
)

# =====================================================
# SAVE CSV
# =====================================================

tables = {

    "src_hotel_property":
        hotel_df,

    "src_room_inventory":
        room_df,

    "src_guest_profile":
        guest_df,

    "src_reservation":
        reservation_df,

    "src_hotel_stay":
        stay_df
}

print("\nSaving CSV files...\n")

for name, df in tables.items():

    path = os.path.join(
        OUTPUT_DIR,
        f"{name}.csv"
    )

    df.to_csv(
        path,
        index=False
    )

    print(
        f"{name}: "
        f"{len(df):,} rows x "
        f"{len(df.columns)} cols "
        f"-> {path}"
    )

# =====================================================
# SUMMARY
# =====================================================

print("\n====================================")
print("HOTEL SOURCE SYSTEM SUMMARY")
print("====================================")

for name, df in tables.items():
    print(
        f"{name:<25} {len(df):>8,} rows"
    )

print("====================================")
print("All source files saved successfully.")
print("====================================")