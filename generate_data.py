import pandas as pd
import numpy as np

# 5000 realistic train journeys generate kar rahe hain
np.random.seed(42)
n_samples = 5000

base_fares = np.random.randint(400, 3000, n_samples)
days_to_journey = np.random.randint(1, 120, n_samples)
seats_booked_pct = np.random.randint(10, 100, n_samples)
is_premium = np.random.choice([0, 1], n_samples) # 1 for Premium, 0 for Express

target_fares = []
for i in range(n_samples):
    fare = base_fares[i]
    seats = seats_booked_pct[i]
    days = days_to_journey[i]
    premium = is_premium[i]

    # Realistic surge logic jo model seekhega
    if premium == 1:
        multiplier = min(1.5, 1.0 + (max(0, seats - 10) // 10) * 0.1)
        target_fares.append(fare * multiplier)
    else:
        if days <= 2 and seats > 80:
            target_fares.append(fare * 1.3)
        elif days <= 2:
            target_fares.append(fare + 300)
        else:
            target_fares.append(fare)

# DataFrame banakar CSV mein save karna
df = pd.DataFrame({
    'Base_Fare': base_fares,
    'Days_to_Journey': days_to_journey,
    'Seats_Booked_Percentage': seats_booked_pct,
    'Is_Premium': is_premium,
    'Target_Fare': target_fares
})

df.to_csv('historical_train_data.csv', index=False)
print("✅ historical_train_data.csv successfully generated with 5000 records!")