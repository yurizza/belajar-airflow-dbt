import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random, os

fake = Faker('en_US')
Faker.seed(99); np.random.seed(99); random.seed(99)

AIRLINE_DIR = r"D:\S2_DW\travel\output"
OUTPUT_DIR  = r"D:\S2_DW\travel\output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Loading shared dimensions from airline dataset...")
dim_date      = pd.read_csv(f"{AIRLINE_DIR}/dim_date.csv")
dim_passenger = pd.read_csv(f"{AIRLINE_DIR}/dim_passenger.csv")
passenger_keys = dim_passenger["passenger_key"].values
date_key_map   = dim_date.set_index("full_date")["date_key"].to_dict()
date_keys_all  = dim_date["date_key"].values

CITIES = [
    ("Jakarta","Indonesia",-6.2088,106.8456,"IDR",0.065),
    ("Surabaya","Indonesia",-7.2575,112.7521,"IDR",0.055),
    ("Bali","Indonesia",-8.4095,115.1889,"IDR",0.070),
    ("Makassar","Indonesia",-5.1477,119.4327,"IDR",0.050),
    ("Bandung","Indonesia",-6.9175,107.6191,"IDR",0.050),
    ("Manado","Indonesia",1.4748,124.8421,"IDR",0.048),
    ("Singapore","Singapore",1.3521,103.8198,"SGD",0.090),
    ("Kuala Lumpur","Malaysia",3.1390,101.6869,"MYR",0.075),
    ("Bangkok","Thailand",13.7563,100.5018,"THB",0.070),
    ("Tokyo","Japan",35.6762,139.6503,"JPY",0.100),
    ("Sydney","Australia",-33.8688,151.2093,"AUD",0.095),
    ("Dubai","UAE",25.2048,55.2708,"AED",0.085),
    ("London","UK",51.5074,-0.1278,"GBP",0.120),
    ("Hong Kong","China",22.3193,114.1694,"HKD",0.105),
]

HOTEL_BRANDS = [
    ("Marriott","Luxury",5,350,800),("Hilton","Luxury",5,300,750),
    ("Hyatt","Luxury",5,320,780),("Sheraton","Upper-Mid",4,150,350),
    ("Novotel","Upper-Mid",4,130,300),("Ibis","Economy",3,50,130),
    ("Fave Hotel","Economy",3,40,110),("Swiss-Belhotel","Upper-Mid",4,120,280),
    ("Grand Mercure","Upper-Mid",4,140,320),("Aloft","Lifestyle",4,160,340),
    ("W Hotels","Luxury",5,400,900),("Aston","Mid-Scale",3,70,160),
    ("Harris","Mid-Scale",3,60,140),("Pop! Hotels","Budget",2,25,65),
]

ROOM_TYPES = [
    ("STD","Standard Room",0.40,1.00),("DLX","Deluxe Room",0.25,1.30),
    ("SUP","Superior Room",0.15,1.15),("SUT","Suite",0.08,2.50),
    ("EXC","Executive Room",0.07,1.80),("FAM","Family Room",0.05,1.60),
]

BOOKING_CHANNELS = [
    ("WEB","Website Direct",0.35),
    ("MOB","Mobile App",0.30),
    ("GDS","Global Distribution System",0.15),
    ("OTA","Online Travel Agency",0.12),
    ("CTR","Call Center",0.05),
    ("AGT","Travel Agent",0.03),
]


# DIM: Hotel Property (SCD2)
def gen_hotel_property_dim():
    rows=[]; key=1
    for city,country,lat,lon,currency,tax_rate in CITIES:
        for _ in range(random.randint(2,5)):
            bname,bcat,stars,plo,phi = random.choice(HOTEL_BRANDS)
            rc = random.randint(80,500)
            base = dict(hotel_property_key=key,hotel_id=f"HTL{key:05d}",
                hotel_name=f"{bname} {city}",brand=bname,category=bcat,star_rating=stars,
                city=city,country=country,currency=currency,local_tax_rate=tax_rate,
                latitude=round(lat+random.uniform(-0.05,0.05),4),
                longitude=round(lon+random.uniform(-0.05,0.05),4),
                total_rooms=rc,has_pool=random.choice([True,False]),
                has_gym=stars>=4,has_spa=stars>=4 and random.random()>0.3,
                price_range_low_usd=plo,price_range_high_usd=phi,
                scd_effective_date="2022-01-01",scd_expiry_date="9999-12-31",
                scd_current_flag=True,scd_version=1)
            rows.append(base); key+=1
            if random.random()<0.30:
                rows[-1]["scd_expiry_date"]="2023-05-31"
                rows[-1]["scd_current_flag"]=False
                v2=rows[-1].copy()
                v2.update(hotel_property_key=key,star_rating=min(5,stars+1),
                    total_rooms=rc+random.randint(20,80),has_spa=True,
                    price_range_low_usd=plo*1.15,price_range_high_usd=phi*1.15,
                    scd_effective_date="2023-06-01",scd_expiry_date="9999-12-31",
                    scd_current_flag=True,scd_version=2)
                rows.append(v2); key+=1
    return pd.DataFrame(rows)

# DIM: Customer (linked to Passenger)
def gen_customer_dim():
    rows=[]
    for _,row in dim_passenger.iterrows():
        rows.append(dict(
            customer_key=int(row["passenger_key"]),
            passenger_key_ref=int(row["passenger_key"]),
            customer_id=row["passenger_id"].replace("PAX","CUS"),
            first_name=row["first_name"],last_name=row["last_name"],
            gender=row["gender"],nationality=row["nationality"],
            age_group=row["age_group"],loyalty_tier=row["loyalty_tier"],
            hotel_loyalty_num=f"HL{int(row['passenger_key']):08d}",
            hotel_loyalty_tier=random.choices(["None","Silver","Gold","Platinum"],weights=[45,28,17,10])[0],
            preferred_room_type=random.choice(["STD","DLX","SUT","EXC"]),
            smoking_preference=random.choices(["Non-Smoking","Smoking"],weights=[85,15])[0],
            travel_purpose=random.choices(["Business","Leisure","Family","Honeymoon","MICE"],weights=[35,35,15,8,7])[0],
            email=row["email"],
            last_updated=fake.date_between(start_date='-3y', end_date='today').isoformat(),
        ))
    return pd.DataFrame(rows)

# DIM: BOOKING Channel
def gen_booking_channel_dim():
    rows=[]

    for key,(code,name,share) in enumerate(BOOKING_CHANNELS,1):

        rows.append(dict(
            booking_channel_key=key,
            channel_code=code,
            channel_name=name,

            channel_type="Direct"
                if code in ("WEB","MOB","CTR")
                else "Indirect",

            # karena BOOKING_CHANNELS tidak punya comm
            commission_rate_pct=
                0 if code in ("WEB","MOB") else
                8 if code=="GDS" else
                10 if code=="OTA" else
                5 if code=="CTR" else
                12,

            instant_confirm=code in ("WEB","MOB","OTA"),

            cancellation_policy=random.choice([
                "Flexible",
                "Moderate",
                "Strict"
            ]),

            volume_share_pct=share,

            avg_lead_days={
                "WEB":14,
                "OTA":10,
                "GDS":21,
                "MOB":7,
                "CTR":5,
                "AGT":30
            }[code]
        ))

    return pd.DataFrame(rows)

# FACT
def gen_hotel_fact(hotel_df,customer_df,channel_df,n_rows=15000):
    hotel_curr = hotel_df[hotel_df["scd_current_flag"]==True]
    hotel_keys = hotel_curr["hotel_property_key"].values
    hotel_info = hotel_curr.set_index("hotel_property_key")
    cust_keys  = customer_df["customer_key"].values
    ch_keys    = channel_df["booking_channel_key"].values
    ch_shares  = channel_df["volume_share_pct"].values
    ch_comm    = channel_df.set_index("booking_channel_key")["commission_rate_pct"].to_dict()
    month_w    = [0.07,0.07,0.08,0.08,0.08,0.10,0.10,0.10,0.08,0.08,0.08,0.08]

    rows=[]
    for i in range(1,n_rows+1):
        hk = int(np.random.choice(hotel_keys))
        h  = hotel_info.loc[hk]
        plo,phi = float(h["price_range_low_usd"]),float(h["price_range_high_usd"])
        stars   = int(h["star_rating"])
        rc,rn,_,rmult = random.choices(ROOM_TYPES,weights=[r[2] for r in ROOM_TYPES])[0]
        nightly = round(np.random.uniform(plo,phi)*rmult,2)

        arr_row = dim_date.sample(1,weights=dim_date["month_num"].map(lambda m:month_w[m-1])).iloc[0]
        arr_key = int(arr_row["date_key"])
        arr_dt  = datetime.strptime(arr_row["full_date"],"%Y-%m-%d")

        lead   = int(np.random.exponential(14))+1
        res_dt = arr_dt - timedelta(days=lead)
        res_str= res_dt.strftime("%Y-%m-%d")
        res_key= int(date_key_map.get(res_str, arr_key))

        nights = int(np.random.choice([1,2,3,4,5,6,7],
            p=([0.20,0.25,0.20,0.15,0.10,0.06,0.04] if stars>=5 else
               [0.30,0.30,0.20,0.10,0.06,0.03,0.01] if stars==4 else
               [0.45,0.30,0.15,0.07,0.03,0,0])))
        dep_dt  = arr_dt + timedelta(days=nights)
        dep_key = int(date_key_map.get(dep_dt.strftime("%Y-%m-%d"),arr_key))

        ck  = int(np.random.choice(cust_keys))
        chk = int(np.random.choice(ch_keys,p=ch_shares/ch_shares.sum()))

        ext   = round(nightly*nights,2)
        tax   = float(h["local_tax_rate"])
        taxc  = round(ext*tax,2)
        comm  = round(ext*ch_comm[chk]/100,2)
        net   = round(ext-comm,2)
        extra = round(np.random.choice([0,0,np.random.uniform(10,50),np.random.uniform(50,200)],p=[0.50,0.25,0.15,0.10]),2)

        if random.random()<0.02:
            ot=random.choice(["zero","long","expensive"])
            if ot=="zero":   ext=0.0;taxc=0.0
            elif ot=="long": nights=random.randint(30,90);ext=round(nightly*nights,2);taxc=round(ext*tax,2)
            else:            ext=round(ext*random.uniform(5,10),2);taxc=round(ext*tax,2)

        status=np.random.choice(["Checked-Out","Cancelled","No-Show","In-House"],p=[0.82,0.10,0.05,0.03])

        rows.append(dict(
            hotel_stay_key=i,
            reservation_date_key=res_key,arrival_date_key=arr_key,departure_date_key=dep_key,
            customer_key=ck,hotel_property_key=hk,booking_channel_key=chk,
            confirmation_number=f"HCF{fake.bothify('########')}",
            ticket_number=f"HTK{fake.numerify('##########')}",
            number_of_nights=nights,room_type_code=rc,room_type_name=rn,
            nightly_rate_usd=round(nightly,2),extended_room_charge_usd=ext,
            tax_charge_usd=taxc,extra_charges_usd=extra,
            commission_paid_usd=comm,net_revenue_usd=net,
            total_bill_usd=round(ext+taxc+extra,2),
            reservation_status=status,lead_time_days=lead,
            linked_flight_segment=random.random()<0.45,
        ))
    return pd.DataFrame(rows)

print("Generating Hotel Property Dimension (SCD2)...")
hotel_df    = gen_hotel_property_dim()
print("Generating Customer Dimension (linked to Passenger)...")
customer_df = gen_customer_dim()
print("Generating Booking Channel Dimension...")
booking_df  = gen_booking_channel_dim()
print("Generating Hotel Stay Fact Table (15,000 rows)...")
fact_df     = gen_hotel_fact(hotel_df,customer_df,booking_df,n_rows=15000)

tables = {
    "hotel_dim_hotel_property": hotel_df,
    "hotel_dim_customer":       customer_df,
    "hotel_dim_booking_channel":  booking_df,
    "hotel_fact_hotel_stay":    fact_df,
}
print()
for name,df in tables.items():
    path=f"{OUTPUT_DIR}/{name}.csv"
    df.to_csv(path,index=False)
    print(f"  {name}: {len(df):,} rows x {len(df.columns)} cols → {path}")

print(f"""
════════════════════════════════════════════
  HOTEL DATASET SUMMARY
════════════════════════════════════════════
  Fact rows            : {len(fact_df):,}
  Total room revenue   : ${fact_df['extended_room_charge_usd'].sum():,.0f}
  Total tax collected  : ${fact_df['tax_charge_usd'].sum():,.0f}
  Avg nightly rate     : ${fact_df['nightly_rate_usd'].mean():.2f}
  Avg length of stay   : {fact_df['number_of_nights'].mean():.1f} nights

  Reservation status:
{fact_df['reservation_status'].value_counts().to_string()}

  Room type distribution:
{fact_df['room_type_code'].value_counts().to_string()}

  Outliers (nights>14) : {(fact_df['number_of_nights']>14).sum()}
  Outliers (rate=0)    : {(fact_df['extended_room_charge_usd']==0).sum()}
  SCD2 hotel versions  : {hotel_df['scd_version'].value_counts().to_dict()}
  Linked to flight     : {fact_df['linked_flight_segment'].sum():,} transaksi (paket travel)

  LINK KE AIRLINE DATASET:
  customer_key  <-> passenger_key  (3,000 pelanggan sama)
  date_key      <-> date_key       (kalender 2022-2024 sama)
════════════════════════════════════════════
""")