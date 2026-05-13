import pandas as pd
import numpy as np

# Load a small sample
df = pd.read_csv('zomato_dataset.csv', nrows=100)
df.columns = df.columns.str.strip()

# 1. Prep Time
print("Original Time_Orderd:", df['Time_Orderd'].head().tolist())
print("Original Time_Order_picked:", df['Time_Order_picked'].head().tolist())

# They might be like '21:55', '22:10'. We need to parse them safely.
# Some might be 'NaN' or float 'NaN'.
def parse_time(col):
    # Convert to string and handle decimals like '0.9999' which might exist in some datasets, or just normal time 'HH:MM'
    # Actually, let's just use pd.to_datetime
    return pd.to_datetime(df[col].astype(str), format='%H:%M', errors='coerce')

t_ord = parse_time('Time_Orderd')
t_pick = parse_time('Time_Order_picked')
prep = (t_pick - t_ord).dt.total_seconds() / 60
prep = np.where(prep < 0, prep + 24*60, prep) # handle midnight crossing

print("Prep time min:", prep[:5])

# 2. dist_bucket
df['Distance_km'] = np.random.uniform(1, 20, 100) # mock
df['dist_bucket'] = pd.cut(df['Distance_km'], bins=[0, 3, 6, 10, 100], labels=['0-3km', '3-6km', '6-10km', '>10km']).astype(str)
print("dist_bucket:", df['dist_bucket'].head().tolist())

# 3. is_peak_hour
df['is_peak_hour'] = df['Road_traffic_density'].astype(str).str.strip().apply(lambda x: 1 if x in ['Jam', 'High'] else 0)
print("is_peak_hour:", df['is_peak_hour'].head().tolist())

# 4. is_bad_weather
bad_weather = ['Storm', 'Sandstorms', 'Windy', 'Fog']
df['is_bad_weather'] = df['Weather_conditions'].astype(str).str.strip().apply(lambda x: 1 if any(w in x for w in bad_weather) else 0)
print("is_bad_weather:", df['is_bad_weather'].head().tolist())
