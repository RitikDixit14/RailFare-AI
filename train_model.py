import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import pickle
import os

print("🧠 Starting Model Training Process...")

# 1. Check if the real data exists
DATA_FILE = "real_irctc_data.csv"
if not os.path.exists(DATA_FILE):
    print(f"❌ Error: {DATA_FILE} not found! Please run data_logger.py first.")
    exit()

print("Loading Real Data...")
df = pd.read_csv(DATA_FILE)

print(f"Found {len(df)} records for training.")

# 2. Define Features (Inputs) and Target (Output)
X = df[['Base_Fare', 'Days_to_Journey', 'Seats_Booked_Percentage', 'Is_Premium']]

print("Calculating Target Fares for Training...")
target_fares = []
for index, row in df.iterrows():
    base = row['Base_Fare']
    days = row['Days_to_Journey']
    seats = row['Seats_Booked_Percentage']
    prem = row['Is_Premium']
    
    # Mathematical logic that the model will learn
    if prem == 1:
        multiplier = min(1.5, 1.0 + (max(0, seats - 10) // 10) * 0.1)
        target = base * multiplier
    else:
        if days <= 2 and seats > 80:
            target = base * 1.3
        elif days <= 2:
            target = base + 300
        else:
            target = base
    target_fares.append(target)

y = pd.Series(target_fares)

# 3. Train the Model
print("Training the Machine Learning Model (Random Forest)...")
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# 4. Save the Model (This will overwrite the old simulated .pkl file)
MODEL_FILE = 'surge_pricing_model.pkl'
with open(MODEL_FILE, 'wb') as file:
    pickle.dump(model, file)

print(f"✅ Success! Real-Data Model trained and saved as {MODEL_FILE}!")