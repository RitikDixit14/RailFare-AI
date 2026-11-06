# ⚡ RailFare AI: Indian Railways ML Fare Prediction & 3D GIS Telemetry Cockpit

A high-performance railway operations intelligence and dynamic fare forecasting platform designed with a futuristic dark glassmorphic cockpit interface. Integrates real-time train telemetry, 3D GIS satellite routing, interactive halt platform management, delay/crowd risk prediction, and machine-learning-driven flexi-fare surge prediction.

---

## 🌟 Key Features

### 1. 🛰️ 3D GIS Satellite Rail Telemetry
- **Continuous Glowing Track Polyline:** Built with Pydeck `PathLayer` rendering physical track paths.
- **Locomotive Beacon with Pulsing Radar Aura:** High-visibility real-time GPS locomotive marker with speed readout.
- **Live Halts & Stoppage Intelligence:** Color-coded node system distinguishing traversed stations (`● PASSED` in glowing green), active stops (`● AT STATION` in fluorescent red), and remaining halts (`● UPCOMING` in neon cyan).
- **Interactive Route Scrubbing Mode:** Lets users simulate train movement from 0% origin to 100% terminus along physical track curves.

### 2. 🎛️ AI Cockpit & Dynamic Fare Surge Prediction
- **Machine Learning Fare Estimator:** Predicts real-time fare escalations based on route demand, booking window, seat depletion rate, and historical patterns.
- **IRCTC Flexi-Fare Simulator:** Analyzes 10% slab increases across premium trains (Rajdhani, Shatabdi, Duronto, Vande Bharat).
- **Seat Availability Heatmap:** Multi-date availability matrix across travel classes (1A, 2A, 3A, SL, CC, EC).

### 3. 🎫 PNR Status & Operational Intelligence
- **Live Running Status:** Ground-truth schedule tracking accounting for overnight runs and multi-day transitions.
- **Crowd & Delay Risk Badges:** Heuristic classification estimating passenger load and probable route bottlenecks.
- **Alternative Train Recommendations:** Intelligently suggests parallel routes when seats are waitlisted or unavailable.

### 4. 📊 Station Congestion & AR Travel Hub
- **Hourly Station Congestion Forecasts:** Dynamic passenger density analytics across major transit hubs.
- **Passenger Grievance Logging:** Structured feedback submission with auto-generated tracking tokens.

---

## 🏗️ Project Architecture

```
├── app.py                     # Main Streamlit web application & cockpit interface
├── ui_components.py           # Pydeck 3D GIS maps, custom glassmorphic HTML components
├── api_services.py            # Timetable schedule engines, telemetry interpolator, live APIs
├── prediction_engine.py       # ML surge pricing models, delay & crowd heuristics
├── route_planner.py           # Railway graph routing & station congestion analytics
├── database.py                # Local grievance database & analytics storage
├── train_model.py             # Script used to train the surge pricing ML model
├── surge_pricing_model.pkl    # Pre-trained Scikit-learn ML model
├── train_info.csv             # Indian Railways train routes & schedules
├── stations.csv               # Master Indian Railways station GIS catalog
├── historical_train_data.csv  # Historical training dataset
├── requirements.txt           # Python library dependencies
├── assets/
│   ├── style.css              # Cyberpunk holographic styling & animations
│   └── train_animation.json   # Lottie animation asset
└── .streamlit/
    └── config.toml            # Streamlit theme & performance configurations
```

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/railfare-ai.git
cd "indian Railways fare Predction"
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows
python -m venv ir_env
.\ir_env\Scripts\activate

# macOS / Linux
python3 -m venv ir_env
source ir_env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch the Application
```bash
streamlit run app.py
```

The application will launch in your browser at `http://localhost:8501`.

---

## 🛠️ Tech Stack
- **Frontend / Framework:** Streamlit, Pydeck (Deck.gl), Plotly Express, Streamlit-Lottie
- **Backend / Data:** Python 3.10+, Pandas, NumPy
- **Machine Learning:** Scikit-Learn
- **GIS & Visuals:** WebGL, Mapbox Dark Style, 3D ScatterplotLayer & PathLayer

---

## 📜 License
Academic & Educational Project.

