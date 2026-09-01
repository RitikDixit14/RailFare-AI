import requests
import pandas as pd
import datetime
import time
import os
import random

print("🚀 Starting Enterprise Data Miner...")

# 🔑 AAPKI API KEYS (Yahan comma lagakar 2-3 nayi keys daal sakte hain)
API_KEYS = [
    "da0430f4cfmsh08eeb1382c9da57p18ed09jsn52beb99e83bc",
    "9d5cf39da1msh47a05fbae2c0613p10c813jsn826f73e1a33e",
    "dc9828a2b6mshb69c7dd86a32771p1537d8jsn75eabcf6ad0f"
]

# Zyada routes cover karenge master database ke liye
ROUTES = [
    ("NDLS", "CNB"), ("CSMT", "PUNE"), ("HWH", "PNBE"), ("MAS", "SBC"),
    ("NDLS", "BCT"), ("ALJN", "NDLS"), ("AGC", "NDLS"), ("BSB", "LKO")
]
DAYS_TO_CHECK = [1, 2, 5, 10, 20, 30] 

MASTER_FILE = "master_irctc_db.csv"
url = "https://irctc1.p.rapidapi.com/api/v3/trainBetweenStations"

collected_data = []
current_key_index = 0

for origin, dest in ROUTES:
    for days_ahead in DAYS_TO_CHECK:
        target_date = (datetime.date.today() + datetime.timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        
        while current_key_index < len(API_KEYS):
            active_key = API_KEYS[current_key_index]
            headers = {"Content-Type": "application/json", "x-rapidapi-host": "irctc1.p.rapidapi.com", "x-rapidapi-key": active_key}
            
            print(f"Mining: {origin} ⟶ {dest} ({target_date}) | Using Key {current_key_index + 1}...")
            
            try:
                response = requests.get(url, headers=headers, params={"fromStationCode": origin, "toStationCode": dest, "dateOfJourney": target_date}, timeout=10)
                
                # Agar limit khatam hui toh switch key
                if response.status_code == 429:
                    print(f"⚠️ Key {current_key_index + 1} exhausted. Switching to next key...")
                    current_key_index += 1
                    continue # Wapas while loop ke start me jao aur nayi key try karo
                
                response.raise_for_status()
                api_data = response.json()
                train_list = api_data.get('data', []) if isinstance(api_data.get('data'), list) else (api_data.get('data', {}).get('trains', []) if isinstance(api_data.get('data'), dict) else api_data.get('trains', []))
                
                for t in train_list:
                    if not isinstance(t, dict): continue
                    t_no = str(t.get('trainNumber', t.get('trainNo', '0000')))
                    t_name = str(t.get('trainName', 'Unknown'))
                    is_prem = 1 if any(k in t_name.upper() for k in ['VANDE', 'SHATABDI', 'RAJDHANI', 'TEJAS']) else 0
                    dist = float(t.get('distance', 700))
                    base_fare = int((dist * 2.5) + 150) if is_prem == 1 else int((dist * 1.2) + 50)
                    
                    if days_ahead <= 2: seats_sold = random.randint(85, 120)
                    elif days_ahead <= 7: seats_sold = random.randint(60, 95)
                    elif days_ahead <= 15: seats_sold = random.randint(40, 75)
                    else: seats_sold = random.randint(10, 45)

                    collected_data.append({
                        'Origin': origin, 'Dest': dest,
                        'Train_No': t_no, 'Train_Name': t_name, 
                        'Type': 'Premium' if is_prem == 1 else 'Express',
                        'Base_Fare': base_fare, 'Days_to_Journey': days_ahead, 
                        'Seats_Booked_Percentage': seats_sold, 'Is_Premium': is_prem,
                        'Dep': str(t.get('departureTime', '--:--')), 'Arr': str(t.get('arrivalTime', '--:--')), 'Dur': str(t.get('duration', '--h'))
                    })
                time.sleep(1.5) # Server ko zyada hit na karein
                break # Agar success mila toh while loop se bahar niklo aur next date par jao
                
            except Exception as e:
                print(f"Error fetching: {e}")
                break # Koi aur error aaye toh agle route/date par jao
                
        if current_key_index >= len(API_KEYS):
            print("🚨 ALL API KEYS EXHAUSTED! Halting mining process.")
            break
            
    if current_key_index >= len(API_KEYS): break

# Data ko save karna
if collected_data:
    df_new = pd.DataFrame(collected_data)
    if os.path.exists(MASTER_FILE):
        df_existing = pd.read_csv(MASTER_FILE)
        df_final = pd.concat([df_existing, df_new], ignore_index=True).drop_duplicates(subset=['Origin', 'Dest', 'Train_No', 'Days_to_Journey'])
    else:
        df_final = df_new
        
    df_final.to_csv(MASTER_FILE, index=False)
    print(f"✅ Success! Added {len(df_new)} records. Master DB now has {len(df_final)} rows.")
else:
    print("❌ No new data collected.")