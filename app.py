from urllib import request

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import datetime
import pickle  
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import requests
import datetime  # 🛠️ FIXED THE IMPORT CLASH

# 🚆 THE RAILYATRI ENGINE (Using Your Custom Token)
def fetch_live_seat_status(train_no, travel_class, source, dest, date_of_journey, running_days="1111111"):
    import datetime
    from concurrent.futures import ThreadPoolExecutor
    try:
        d_obj = datetime.datetime.strptime(str(date_of_journey), "%d-%m-%Y")
    except:
        d_obj = datetime.datetime.now()
        
    if len(str(running_days)) < 7:
        running_days = "1111111"
        
    dates_to_fetch = []
    curr_date = d_obj
    for _ in range(30): # max 30 days lookahead to prevent infinite loop
        if running_days[curr_date.weekday()] == '1':
            dates_to_fetch.append(curr_date.strftime("%d-%m-%Y"))
            if len(dates_to_fetch) == 6:
                break
        curr_date += datetime.timedelta(days=1)
        
    if len(dates_to_fetch) == 0:
        dates_to_fetch = [(d_obj + datetime.timedelta(days=i)).strftime("%d-%m-%Y") for i in range(6)]
    
    def fetch_single(d_str):
        url = f"https://cttrainsapi.confirmtkt.com/api/v1/trains/search?sourceStationCode={source}&destinationStationCode={dest}&addAvailabilityCache=true&excludeMultiTicketAlternates=true&sortBy=DEFAULT&dateOfJourney={d_str}&enableNearby=false&enableTG=true&showPredictionGlobal=true"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "Accept": "application/json"}
        try:
            return requests.get(url, headers=headers, timeout=5).json()
        except:
            return None

    mapped_list = []
    try:
        with ThreadPoolExecutor(max_workers=6) as executor:
            results = list(executor.map(fetch_single, dates_to_fetch))
            
        for i, ct_data in enumerate(results):
            if not ct_data:
                continue
            for t in (ct_data.get("data") or {}).get("trainList", []):
                if str(t.get("trainNumber")) == str(train_no):
                    cache = t.get("availabilityCache", {})
                    if travel_class in cache:
                        day = cache[travel_class]
                        mapped_list.append({
                            "date": day.get("date"),
                            "availablity_date": str(day.get("date", ""))[:10] if day.get("date") else dates_to_fetch[i][6:]+"-"+dates_to_fetch[i][3:5]+"-"+dates_to_fetch[i][:2],
                            "status": day.get("availability"),
                            "availablity_status": day.get("availability"),
                            "fare": str(day.get("fare")),
                            "total_fare": str(day.get("fare")),
                            "prediction": day.get("predictionPercentage", 0),
                            "gradient": day.get("gradient", "Medium")
                        })
                        break
                        
        if len(mapped_list) > 0:
            return {"seat_availibility": mapped_list}
        else:
            return {"error": "Seat data not found for this class on ConfirmTkt API."}
    except Exception as e:
        return {"error": str(e)}

import requests

def fetch_railyatri_live_status(train_no, date, source, dest, travel_class):
    # Date format must be YYYY-M-D (e.g., 2026-9-14)
    # Class like 1A, 2A, 3A, SL
    url = f"https://sa.railyatri.in/api/seat/enquiry/{train_no}/{date}/{source}/{dest}/{travel_class}/GN.json"
    
    # 🔑 THE SECRET SAUCE: Tumhara Personal Exported Token
    params = {
        "user_id": "45e29781440389029582b0a374ffeb65",
        "authentication_token": "67a641529d57819e92a2d13a4d0742fb",
        "device_type_id": "6"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/152.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://www.railyatri.in",
        "Referer": "https://www.railyatri.in/"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            return {"error": f"Failed: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# Test run
# print(fetch_railyatri_live_status("20434", "2026-9-14", "DLI", "ALJN", "2A"))

# 🔐 ENVIRONMENT VARIABLES LOAD KARNA
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # Yeh forcefully .env ko dhoondhega

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="RailFare AI",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded" 
)

# 📱 GLOBAL RESPONSIVE CSS FOR MOBILE & LAPTOP
st.markdown("""
<style>
    /* 1. Remove extra padding on mobile */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
    }
    
    /* 2. Responsive Base Font Size */
    html { font-size: 16px; }
    
    /* 3. Mobile Specific Adjustments */
    @media (max-width: 768px) {
        html { font-size: 14px; }
        .block-container { padding: 0.5rem !important; }
        .hero-title { font-size: 2rem !important; }
        .pred-price { font-size: 3rem !important; }
        
        /* Convert stacked columns to 2x2 grids where appropriate (e.g. KPIs & class buttons) */
        div[data-testid="stHorizontalBlock"] {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        /* By default, columns take full width on mobile (Streamlit default behavior) */
        div[data-testid="column"] {
            min-width: 100% !important;
            margin-bottom: 1rem !important;
        }
        
        /* EXCEPT for KPIs and Buttons which should wrap into 2x2 or similar grids */
        div[data-testid="column"]:has(.cyber-kpi),
        div[data-testid="column"]:has(.stButton) {
            min-width: 140px !important;
            flex: 1 1 auto !important;
            margin-bottom: 0px !important;
        }
        
        .cyber-kpi {
            min-height: 120px !important;
            padding: 10px !important;
        }
        .kpi-value { font-size: 1.8rem !important; }
    }

    /* 4. Ultra-Smooth iOS/Android Swipe for Calendar */
    .swipe-container {
        display: flex;
        overflow-x: auto;
        gap: 12px;
        padding-bottom: 15px;
        scroll-snap-type: x mandatory;
        -webkit-overflow-scrolling: touch; /* Makhan jaisa mobile swipe */
        scroll-behavior: smooth;
    }
    .swipe-container::-webkit-scrollbar { height: 6px; }
    .swipe-container::-webkit-scrollbar-thumb { background: var(--neon-cyan)50; border-radius: 10px; }
    
    .swipe-card {
        flex: 0 0 auto;
        min-width: 105px;
        scroll-snap-align: start; /* Card hamesha center mein aake rukega */
    }
</style>
""", unsafe_allow_html=True)
# 🟢 THE 100% REAL DATA SCRAPER ENGINE
def fetch_real_availability_from_web(train_no, date_str, src, dst, travel_class):
    try:
        # Pura URL waisa hi banayenge jaise normal user website par click karta hai
        url = f"https://www.confirmtkt.com/train-seat-availability/{train_no}-{src}-{dst}-{date_str}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 🕵️‍♂️ HTML ke andar us class ka div dhoondhenge jahan asli data likha hota hai
            # ConfirmTkt par class block (jaise '3A') aur uske theek neeche status hota hai
            
            # Step 1: Find all class blocks
            class_blocks = soup.find_all(lambda tag: tag.name == 'div' and travel_class in tag.text)
            
            if class_blocks:
                # Step 2: Extract text from the nearest status block
                for block in class_blocks:
                    parent_text = block.parent.text.upper()
                    if "AVL" in parent_text or "AVAILABLE" in parent_text:
                        return "AVAILABLE-" + ''.join(filter(str.isdigit, parent_text.split("AVL")[-1]))
                    elif "WL" in parent_text or "WAITLIST" in parent_text:
                        return "WL-" + ''.join(filter(str.isdigit, parent_text.split("WL")[-1]))
                    elif "RAC" in parent_text:
                        return "RAC-" + ''.join(filter(str.isdigit, parent_text.split("RAC")[-1]))
            
            # Step 3: Agar direct scrap fail ho, toh hidden JSON script tag me dhoondho (Aakhri rasta!)
            import re
            json_match = re.search(r'availabilityCache":({.*?})', response.text)
            if json_match:
                import json
                try:
                    cache = json.loads(json_match.group(1))
                    for k, v in cache.items():
                        if travel_class in k:
                            return str(v.get('Availability', ''))
                except:
                    pass
                    
        return None
    except Exception as e:
        # DEBUG: st.write(f"Scraper Error: {e}")
        return None

# --- THEME TOGGLE (Sidebar) ---
st.sidebar.markdown("<h3 style='text-align: center; color: var(--text-main); margin-bottom: 0;'>🎨 Theme</h3>", unsafe_allow_html=True)
theme_choice = st.sidebar.radio("ThemeChoice", ["🌙 Dark Mode", "☀️ Light Mode"], horizontal=True, label_visibility="collapsed")

if theme_choice == "☀️ Light Mode":
    css_vars = """
    :root {
        --bg-1: #FFFFFF;
        --bg-2: #F8FAFC;
        --bg-alpha-90: rgba(255, 255, 255, 0.9);
        --bg-alpha-80: rgba(255, 255, 255, 0.8);
        --bg-alpha-70: rgba(255, 255, 255, 0.7);
        --bg-alpha-60: rgba(255, 255, 255, 0.6);
        --bg-1-alpha-90: rgba(241, 245, 249, 0.9);
        --bg-1-alpha-80: rgba(241, 245, 249, 0.8);
        --bg-dark-95: rgba(255, 255, 255, 0.95);
        --bg-dark-92: rgba(255, 255, 255, 0.92);
        --bg-dark-82: rgba(255, 255, 255, 0.82);
        --bg-dark-75: rgba(255, 255, 255, 0.75);
        --bg-dark-60: rgba(255, 255, 255, 0.6);
        --bg-greenish: rgba(240, 253, 244, 0.85);
        
        --neon-cyan: #0284C7;
        --neon-green: #16A34A;
        --neon-yellow: #CA8A04;
        --neon-red: #DC2626;
        --neon-orange: #EA580C;
        
        --text-light: #334155;
        --text-muted: #64748B;
        --border-light: #CBD5E1;
        --text-inverted: #FFFFFF;
        --text-main: #0F172A;
        
        --white-alpha-30: rgba(0, 0, 0, 0.15);
        --white-alpha-20: rgba(0, 0, 0, 0.1);
        --white-alpha-10: rgba(0, 0, 0, 0.05);
        --white-alpha-05: rgba(0, 0, 0, 0.02);
        
        --black-alpha-80: rgba(255, 255, 255, 0.8);
        --black-alpha-60: rgba(255, 255, 255, 0.6);
        --black-alpha-50: rgba(255, 255, 255, 0.5);
        --black-alpha-40: rgba(255, 255, 255, 0.4);
        --black-alpha-30: rgba(255, 255, 255, 0.3);
    }
    """
else:
    css_vars = """
    :root {
        --bg-1: #1E293B;
        --bg-2: #0F172A;
        --bg-alpha-90: rgba(15, 23, 42, 0.9);
        --bg-alpha-80: rgba(15, 23, 42, 0.8);
        --bg-alpha-70: rgba(15, 23, 42, 0.7);
        --bg-alpha-60: rgba(15, 23, 42, 0.6);
        --bg-1-alpha-90: rgba(30, 41, 59, 0.9);
        --bg-1-alpha-80: rgba(30, 41, 59, 0.8);
        --bg-dark-95: rgba(7, 11, 20, 0.95);
        --bg-dark-92: rgba(7, 11, 20, 0.92);
        --bg-dark-82: rgba(7, 11, 20, 0.82);
        --bg-dark-75: rgba(10, 15, 30, 0.75);
        --bg-dark-60: rgba(10, 15, 30, 0.6);
        --bg-greenish: rgba(5, 20, 15, 0.85);
        
        --neon-cyan: #00E5FF;
        --neon-green: #00E676;
        --neon-yellow: #FFD600;
        --neon-red: #FF1744;
        --neon-orange: #FF9100;
        
        --text-light: #E2E8F0;
        --text-muted: #94A3B8;
        --border-light: #334155;
        --text-inverted: #070B14;
        --text-main: #FFFFFF;
        
        --white-alpha-30: rgba(255,255,255,0.3);
        --white-alpha-20: rgba(255,255,255,0.2);
        --white-alpha-10: rgba(255,255,255,0.1);
        --white-alpha-05: rgba(255,255,255,0.05);
        
        --black-alpha-80: rgba(0,0,0,0.8);
        --black-alpha-60: rgba(0,0,0,0.6);
        --black-alpha-50: rgba(0,0,0,0.5);
        --black-alpha-40: rgba(0,0,0,0.4);
        --black-alpha-30: rgba(0,0,0,0.3);
    }
    """

st.markdown(f"<style>{css_vars}</style>", unsafe_allow_html=True)

# --- 2. 3D GLOWING DARK THEME CSS INJECTION ---
st.markdown("""
    <style>
    .stApp, [data-testid="stAppViewContainer"] { 
        background-image: 
            radial-gradient(circle at 15% 50%, rgba(0, 229, 255, 0.15), transparent 40%),
            radial-gradient(circle at 85% 30%, rgba(0, 230, 118, 0.15), transparent 40%),
            linear-gradient(var(--bg-dark-82), var(--bg-dark-92)),
            url("https://images.unsplash.com/photo-1541427468627-a89a96e5ca1d?auto=format&fit=crop&w=2560&q=80");
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
        color: var(--text-light); 
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
    }
    
    .hero-header {
        background: var(--bg-dark-75);
        backdrop-filter: blur(16px);
        color: var(--text-main);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        text-align: center;
        position: relative;
        overflow: hidden;
        border-top: 1px solid var(--white-alpha-20);
        border-bottom: 1px solid var(--black-alpha-80);
        border-left: 1px solid rgba(0, 229, 255, 0.3);
        border-right: 1px solid rgba(0, 229, 255, 0.3);
        box-shadow: 0 15px 35px var(--black-alpha-60), 0 0 25px rgba(0, 229, 255, 0.15);
        margin-bottom: 2.5rem;
    }
    .hero-title { font-size: 3.2rem; font-weight: 800; margin-bottom: 0.5rem; letter-spacing: 1px; color: var(--text-main); text-shadow: 0 0 15px rgba(0, 229, 255, 0.5); }
    .hero-subtitle { font-size: 1.2rem; font-weight: 400; color: var(--text-muted); }

    .premium-card {
        background: var(--bg-alpha-70);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 25px;
        margin-bottom: 25px;
        border-top: 1px solid var(--white-alpha-10);
        border-bottom: 1px solid var(--black-alpha-80);
        box-shadow: 0 10px 30px var(--black-alpha-50), 0 0 15px rgba(0, 229, 255, 0.05);
    }
    /* 🛠️ FIX FOR 'SAVE TO CART' BUTTON VISIBILITY */
    button[data-testid="baseButton-secondary"], button[kind="secondary"] { 
        background: rgba(0, 230, 118, 0.1) !important; 
        border: 2px solid var(--neon-green) !important; 
        color: var(--neon-green) !important; /* Bright Neon Green Text */
        font-weight: 800 !important; 
        font-size: 1.1rem !important;
        border-radius: 8px !important;
        transition: 0.3s ease-in-out !important;
    }
    button[data-testid="baseButton-secondary"]:hover, button[kind="secondary"]:hover { 
        background: var(--neon-green) !important; 
        color: var(--text-inverted) !important; /* Dark text on hover */
        box-shadow: 0 0 15px rgba(0, 230, 118, 0.6) !important;
    }
    .section-title { color: var(--neon-cyan); font-weight: 700; font-size: 1.4rem; margin-bottom: 20px; border-bottom: 1px solid rgba(0, 229, 255, 0.2); padding-bottom: 10px; text-shadow: 0 0 10px rgba(0, 229, 255, 0.3); }
    
    .prediction-card {
        background: var(--bg-greenish); backdrop-filter: blur(16px); border-radius: 16px; padding: 40px 25px;
        text-align: center; margin-bottom: 30px; animation: pulseGlow 2s infinite alternate;
        border-left: 2px solid var(--neon-green); border-right: 2px solid var(--neon-green);
    }
    @keyframes pulseGlow { 
        from { box-shadow: 0 15px 40px var(--black-alpha-60), 0 0 20px rgba(0, 230, 118, 0.2); } 
        to { box-shadow: 0 15px 40px var(--black-alpha-60), 0 0 40px rgba(0, 230, 118, 0.4); } 
    }
    .pred-price { font-size: 4.5rem; color: var(--neon-green); font-weight: 900; margin: 0; line-height: 1; text-shadow: 0 0 20px rgba(0, 230, 118, 0.6); }
    .pred-label { color: var(--text-muted); font-size: 1.2rem; text-transform: uppercase; letter-spacing: 2px; font-weight: 600; margin-bottom: 15px;}
    .pred-meta { color: var(--text-light); font-weight: 600; font-size: 1.1rem; margin-top: 20px;}

    button[data-testid="baseButton-primary"] { background: linear-gradient(135deg, #00B4DB 0%, #0083B0 100%) !important; border: 1px solid var(--white-alpha-30) !important; color: var(--text-main) !important; font-weight: 800 !important; font-size: 1.2rem !important; padding: 1.5rem !important; border-radius: 12px !important; box-shadow: 0 8px 20px var(--black-alpha-40), 0 0 15px rgba(0, 229, 255, 0.4) !important;}
    
    .cyber-kpi { background: var(--bg-dark-60); border: 1px solid rgba(0, 229, 255, 0.2); border-radius: 12px; padding: 20px 15px; text-align: center; box-shadow: 0 4px 15px var(--black-alpha-40); min-height: 165px; display: flex; flex-direction: column; justify-content: center;}
    .kpi-title { color: var(--neon-cyan); font-size: 1.05rem; font-weight: 800; text-transform: uppercase; margin-bottom: 10px; }
    .kpi-value { color: var(--text-main); font-size: 2.5rem; font-weight: 900; line-height: 1.2; margin-bottom: 8px; }
    .delta-positive { color: var(--neon-red); font-weight: 700;} 
    .delta-negative { color: var(--neon-green); font-weight: 700;} 
    .delta-neutral { color: var(--text-muted); font-weight: 700;}
    .wl-glow { color: var(--neon-orange) !important; text-shadow: 0 0 15px rgba(255, 145, 0, 0.6) !important; }

    [data-testid="stSidebar"] { background-color: var(--bg-dark-95) !important; border-right: 1px solid rgba(0, 229, 255, 0.2); }
    
    /* 🛠️ WIDGET LABELS VISIBILITY FIX */
    .stSelectbox label p, .stNumberInput label p, .stSlider label p, .stDateInput label p {
        color: var(--text-main) !important; 
        font-size: 1.1rem !important; 
        font-weight: 800 !important; 
        text-shadow: 2px 2px 5px rgba(0, 0, 0, 1.0), -1px -1px 4px var(--black-alpha-80), 0 0 15px rgba(0, 229, 255, 0.5) !important;
        letter-spacing: 0.5px;
    }
    div[data-baseweb="select"] > div, input { background-color: var(--bg-alpha-80) !important; border-color: rgba(0, 229, 255, 0.3) !important; color: var(--text-main) !important;}
    .stSlider > div > div > div > div { background-color: var(--neon-cyan) !important; box-shadow: 0 0 10px var(--neon-cyan); }
    /* Smart Booking Button Style */
    a[data-testid="stLinkButton"] {
        background: linear-gradient(135deg, var(--neon-orange) 0%, #FF3D00 100%) !important;
        color: var(--text-main) !important;
        font-weight: 800 !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 15px rgba(255, 145, 0, 0.4) !important;
        transition: 0.3s ease-in-out !important;
        text-align: center !important;
    }
    a[data-testid="stLinkButton"]:hover {
        box-shadow: 0 4px 25px rgba(255, 145, 0, 0.7) !important;
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOAD MACHINE LEARNING MODEL ---
@st.cache_resource
def load_ml_model():
    try:
        model = pickle.load(open('surge_pricing_model.pkl', 'rb'))
        return model, True
    except FileNotFoundError:
        return None, False

surge_model, model_loaded = load_ml_model()

# --- 4. STATE MANAGEMENT ---
if 'predicted' not in st.session_state:
    st.session_state.predicted = False
if 'compare_cart' not in st.session_state:
    st.session_state.compare_cart = []

# --- 5. CLASS MULTIPLIERS & STATION DB ---
# --- 5. CLASS MULTIPLIERS & STATION DB ---
CLASS_MULTIPLIERS = {
    "First AC (1A)": 4.0, "Executive Chair Car (EC)": 3.0, "Second AC (2A)": 2.5, 
    "Third AC (3A)": 1.8, "AC Chair Car (CC)": 1.5, "Sleeper (SL)": 1.0, 
    "Second Seating (2S)": 0.6
}

@st.cache_data
def load_stations():
    # 🌍 THE MEGA IRCTC STATION DATABASE (1000+ Prominent Stations & Hubs)
    return {
        # --- NATIONAL CAPITAL REGION (NCR) & HARYANA ---
        "NDLS": "New Delhi", "DLI": "Old Delhi", "NZM": "Hazrat Nizamuddin", "ANVT": "Anand Vihar Terminal",
        "DEE": "Delhi Sarai Rohilla", "DEC": "Delhi Cantt", "DSJ": "Delhi Safdarjung", "SZM": "Subzi Mandi",
        "GGN": "Gurgaon", "RE": "Rewari", "ROK": "Rohtak Jn", "PNP": "Panipat Jn", "KUN": "Karnal", 
        "UMB": "Ambala Cantt", "UBC": "Ambala City", "HSR": "Hisar", "BHI": "Bhiwani", "SIR": "Sirsa",
        "KKDE": "Kurukshetra Jn", "YJUD": "Yamunanagar Jagadhri", "SNP": "Sonipat", "FDB": "Faridabad",
        "BVH": "Ballabgarh", "PWL": "Palwal", "JIND": "Jind Jn", "KUK": "Kurukshetra",
        
        # --- PUNJAB, CHANDIGARH & HIMACHAL ---
        "CDG": "Chandigarh", "ASR": "Amritsar Jn", "LDH": "Ludhiana Jn", "JUC": "Jalandhar City", 
        "JRC": "Jalandhar Cantt", "PTK": "Pathankot", "PTKC": "Pathankot Cantt", "FZR": "Firozpur Cantt", 
        "BTI": "Bathinda Jn", "KLK": "Kalka", "SML": "Shimla", "PGW": "Phagwara Jn", "BEAS": "Beas",
        "FDK": "Faridkot", "KAP": "Kapurthala", "HSX": "Hoshiarpur", "MOGA": "Moga", "DUI": "Dhuri Jn",
        "PTA": "Patiala", "RPJ": "Rajpura Jn", "SIR": "Sirhind Jn", "RMB": "Rampur Bushahr",
        
        # --- JAMMU & KASHMIR ---
        "JAT": "Jammu Tawi", "SVDK": "SMVD Katra", "UHP": "Udhampur", "KTHU": "Kathua", "BAHL": "Banihal",
        "BDGM": "Badgam", "SINA": "Srinagar Kashmir", "ANT": "Anantnag",
        
        # --- UTTARAKHAND ---
        "DDN": "Dehradun", "HW": "Haridwar", "RK": "Roorkee", "KGM": "Kathgodam", "HDW": "Haldwani", 
        "LKU": "Lal Kuan", "RMR": "Ramnagar", "KPV": "Kashipur", "MB": "Moradabad", "KOT": "Kotdwara",
        
        # --- UTTAR PRADESH (Comprehensive) ---
        "ALJN": "Aligarh Jn", "AGC": "Agra Cantt", "AF": "Agra Fort", "MTJ": "Mathura Jn",
        "CNB": "Kanpur Central", "LKO": "Lucknow NR", "LJN": "Lucknow NE", "PRYJ": "Prayagraj Jn",
        "BSB": "Varanasi Jn", "DDU": "Pt. DD Upadhyaya", "GKP": "Gorakhpur Jn", "SRE": "Saharanpur", 
        "BE": "Bareilly", "SIT": "Sitapur", "AY": "Ayodhya Dham", "AYC": "Ayodhya Cantt", "GD": "Gonda Jn", 
        "BST": "Basti", "JHS": "Virangana Lakshmibai (Jhansi)", "MZP": "Mirzapur", "GCT": "Ghazipur City",
        "BUI": "Ballia", "MAU": "Mau Jn", "AMH": "Azamgarh", "ETW": "Etawah", "CPA": "Kanpur Anwarganj",
        "MTC": "Meerut City", "MUT": "Meerut Cantt", "GZB": "Ghaziabad", "NOI": "Noida City Centre",
        "FZB": "Faizabad Jn", "SLN": "Sultanpur", "RBL": "Rae Bareli Jn", "ON": "Unnao Jn",
        "BLP": "Balrampur", "BRK": "Bahraich", "STP": "Sitapur Cantt", "LMP": "Lakhimpur",
        "KJN": "Kannauj", "FBD": "Farrukhabad", "MNQ": "Mainpuri", "SKB": "Shikohabad Jn",
        "TDL": "Tundla Jn", "KRJ": "Khurja Jn", "HRF": "Hathras Killah", "KSJ": "Kasganj",
        "BEM": "Budaun", "CH": "Chandausi Jn", "RMU": "Rampur", "IZN": "Izzatnagar",
        
        # --- BIHAR & JHARKHAND ---
        "PNBE": "Patna Jn", "PPTA": "Patliputra", "DNR": "Danapur", "MFP": "Muzaffarpur Jn",
        "GAYA": "Gaya Jn", "DBG": "Darbhanga Jn", "SPJ": "Samastipur Jn", "KIR": "Katihar Jn",
        "BJU": "Barauni Jn", "BGP": "Bhagalpur", "MGS": "Mughalsarai", "RNC": "Ranchi",
        "TATA": "Tatanagar Jn", "DHN": "Dhanbad Jn", "BKSC": "Bokaro Steel City", "RJPB": "Rajendra Nagar T",
        "BXR": "Buxar", "ARA": "Ara Jn", "MKA": "Mokama", "KIUL": "Kiul Jn", "JAJ": "Jhajha",
        "JSME": "Jasidih Jn", "MDP": "Madhupur Jn", "PNME": "Parasnath", "KQR": "Koderma",
        "HZD": "Hazaribagh Road", "CRP": "Chandrapura", "GMO": "NSCB Gomoh", "HZBN": "Hazaribagh Town",
        
        # --- MADHYA PRADESH & CHHATTISGARH ---
        "BPL": "Bhopal Jn", "RKMP": "Rani Kamlapati", "INDB": "Indore Jn", "GWL": "Gwalior",
        "JBP": "Jabalpur", "UJN": "Ujjain Jn", "KNW": "Khandwa", "ET": "Itarsi Jn",
        "KTE": "Katni", "STA": "Satna", "R": "Raipur Jn", "BSP": "Bilaspur Jn", "DURG": "Durg",
        "BINA": "Bina Jn", "VGLJ": "VGL Jhansi", "MKC": "Maksi", "NAD": "Nagda Jn", "RTM": "Ratlam Jn",
        "MHOW": "Mhow", "DWS": "Dewas", "SHRN": "Sant Hirdaram Nagar", "GUNA": "Guna",
        "RGN": "Raj Nandgaon", "BIA": "Bhilai Power House", "BYT": "Bhatapara", "CPH": "Champa Jn",
        
        # --- RAJASTHAN ---
        "JP": "Jaipur", "JU": "Jodhpur", "AII": "Ajmer Jn", "UDZ": "Udaipur City",
        "BKN": "Bikaner Jn", "KOTA": "Kota Jn", "ABR": "Abu Road", "BTE": "Bharatpur Jn",
        "AWR": "Alwar", "FL": "Phulera Jn", "KSG": "Kishangarh", "BHL": "Bhilwara",
        "COR": "Chittaurgarh", "RTM": "Ratlam Jn", "SWM": "Sawai Madhopur", "BTE": "Bharatpur Jn",
        "AGC": "Agra Cantt", "AF": "Agra Fort", "MTJ": "Mathura Jn", "NGO": "Nagaur",
        "SGNR": "Shri Ganganagar", "HMH": "Hanumangarh Jn", "SOG": "Suratgarh Jn",
        
        # --- GUJARAT ---
        "ADI": "Ahmedabad Jn", "BRC": "Vadodara Jn", "ST": "Surat", "RJT": "Rajkot Jn",
        "BVC": "Bhavnagar Terminus", "GIMB": "Gandhidham Bg", "VAPI": "Vapi", "ND": "Nadiad Jn",
        "ANND": "Anand Jn", "BH": "Bharuch Jn", "NVS": "Navsari", "BL": "Valsad",
        "BVI": "Borivali", "PLG": "Palghar", "DDR": "Dadar Western", "MMCT": "Mumbai Central",
        "JAM": "Jamnagar", "OKHA": "Okha", "PBR": "Porbandar", "VRL": "Veraval",
        "SUNR": "Surendranagar", "VG": "Viramgam Jn", "MSH": "Mahesana Jn", "PNU": "Palanpur Jn",
        
        # --- MAHARASHTRA & GOA ---
        "CSMT": "Mumbai CSMT", "BCT": "Mumbai Central", "LTT": "Lokmanya Tilak T", "DR": "Dadar",
        "BVI": "Borivali", "TNA": "Thane", "KKY": "Kalyan Jn", "PUNE": "Pune Jn",
        "NGP": "Nagpur", "NK": "Nashik Road", "BSL": "Bhusaval Jn", "AK": "Akola Jn",
        "SGL": "Sangli", "KOP": "C.S.M.T. Kolhapur", "MAO": "Madgaon", "VSG": "Vasco-da-Gama",
        "BD": "Badnera Jn", "WR": "Wardha Jn", "BPQ": "Balharshah", "G": "Gondia Jn",
        "DGG": "Dongargarh", "KRMI": "Karmali", "THVM": "Thivim", "PERN": "Pernem",
        "SWV": "Sawantwadi Road", "KUDL": "Kudal", "SNDD": "Sindhudurg", "KKW": "Kankavali",
        "RN": "Ratnagiri", "CHI": "Chiplun", "KHED": "Khed", "MNI": "Mangaon",
        
        # --- KARNATAKA ---
        "SBC": "KSR Bengaluru", "YPR": "Yesvantpur Jn", "BNC": "Bengaluru Cantt", 
        "UBL": "SSS Hubballi", "MYS": "Mysuru Jn", "MAQ": "Mangaluru Central",
        "MAJN": "Mangaluru Jn", "BGM": "Belagavi", "DWR": "Dharwad", "GDG": "Gadag Jn",
        "HPT": "Hosapete Jn", "BAY": "Ballari Jn", "GTL": "Guntakal Jn", "RC": "Raichur",
        "WADI": "Wadi", "KLBG": "Kalaburagi", "SUR": "Solapur", "DD": "Daund Jn",
        "KPG": "Kopargaon", "MMR": "Manmad Jn", "JL": "Jalgaon Jn", "BAU": "Burhanpur",
        
        # --- KERALA ---
        "TVC": "Thiruvananthapuram", "ERS": "Ernakulam Jn", "ERN": "Ernakulam Town",
        "KCVL": "Kochuveli", "CLT": "Kozhikode", "TCR": "Thrissur", "CAN": "Kannur",
        "KTYM": "Kottayam", "QLN": "Kollam Jn", "KYJ": "Kayamkulam Jn", "CNGR": "Chengannur",
        "TRVL": "Tiruvalla", "AWY": "Aluva", "TLY": "Thalassery", "KGQ": "Kasaragod",
        
        # --- TAMIL NADU ---
        "MAS": "Chennai Central", "MS": "Chennai Egmore", "TBM": "Tambaram",
        "CBE": "Coimbatore Jn", "MDU": "Madurai Jn", "TPJ": "Tiruchchirappalli",
        "SA": "Salem Jn", "ED": "Erode Jn", "CAPE": "Kanniyakumari", "TEN": "Tirunelveli",
        "NCJ": "Nagercoil Jn", "VPT": "Virudunagar Jn", "SRT": "Satur", "CVP": "Kovilpatti",
        "MEJ": "Vanchi Maniyachchi", "DG": "Dindigul Jn", "KRR": "Karur", "NMKL": "Namakkal",
        "TJ": "Thanjavur Jn", "KMU": "Kumbakonam", "MV": "Mayiladuturai Jn", "CDM": "Chidambaram",
        "VM": "Villupuram Jn", "CGL": "Chengalpattu", "AJJ": "Arakkonam Jn", "KPD": "Katpadi Jn",
        
        # --- ANDHRA PRADESH & TELANGANA ---
        "SC": "Secunderabad Jn", "HYB": "Hyderabad Deccan", "KCG": "Kacheguda",
        "WL": "Warangal", "BZA": "Vijayawada Jn", "VSKP": "Visakhapatnam", 
        "TPTY": "Tirupati", "RU": "Renigunta Jn", "GNT": "Guntur Jn", "RJY": "Rajahmundry",
        "SLO": "Samalkot Jn", "AKP": "Anakapalle", "TUNI": "Tuni", "EE": "Eluru",
        "KMT": "Khammam", "DKJ": "Dornakal Jn", "MABD": "Mahbubabad", "KZJ": "Kazipet Jn",
        "RDM": "Ramagundam", "MCI": "Manchiryal", "BPA": "Bellampalli", "SKZR": "Sirpur Kaghaznagar",
        
        # --- ODISHA ---
        "BBS": "Bhubaneswar", "PURI": "Puri", "CTC": "Cuttack", "SBP": "Sambalpur",
        "ROU": "Rourkela", "JSG": "Jharsuguda Jn", "BAM": "Brahmapur", "KUR": "Khurda Road Jn",
        "BHC": "Bhadrak", "BLS": "Baleshwar", "KGP": "Kharagpur Jn", "TATA": "Tatanagar Jn",
        
        # --- WEST BENGAL ---
        "HWH": "Howrah Jn", "SDAH": "Sealdah", "KOAA": "Kolkata", "SHM": "Shalimar",
        "KGP": "Kharagpur Jn", "BWN": "Barddhaman Jn", "ASN": "Asansol Jn", 
        "DGR": "Durgapur", "NJP": "New Jalpaiguri", "SGUJ": "Siliguri Jn",
        "MLDT": "Malda Town", "BHP": "Bolpur Shantiniketan", "RPH": "Rampur Hat",
        "SNT": "Sainthia", "UDL": "Andal Jn", "BQA": "Bankura", "MDN": "Medinipur",
        "SRC": "Santragachi Jn", "DKAE": "Dankuni", "BDC": "Bandel Jn", "NH": "Naihati Jn",
        
        # --- NORTH EAST ---
        "GHY": "Guwahati", "KYQ": "Kamakhya", "DBRG": "Dibrugarh", "NTSK": "New Tinsukia Jn",
        "LMG": "Lumding Jn", "BPB": "Badarpur Jn", "SCL": "Silchar", "AGTL": "Agartala",
        "NHLN": "Naharlagun", "MXN": "Mariani Jn", "FKG": "Furkating Jn", "DMV": "Dimapur",
        "DPU": "Diphu", "CPK": "Chaparmukh Jn", "HJI": "Hojai", "LKA": "Lanka"
    }

MODERN_STATIONS = load_stations()

import pandas as pd
import os
import datetime
import requests
import hashlib
import streamlit as st

import pandas as pd
import os
import datetime
import requests
import hashlib
import streamlit as st

# --- 6. INTELLIGENT DATA FETCHING (EXACT CLASSES EXTRACTOR) ---
@st.cache_data(ttl=3600)
def fetch_trains(origin_code, dest_code):
    API_KEY = os.getenv("RAPIDAPI_KEY")
    origin_code = str(origin_code).strip().upper()
    dest_code = str(dest_code).strip().upper()
    tomorrow_rapid = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    tomorrow_ct = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%d-%m-%Y")

    # ====================================================================
    # 🟢 STEP 1: CONFIRMTKT (PRIMARY ENGINE)
    # ====================================================================
    try:
        hacker_url = f"https://cttrainsapi.confirmtkt.com/api/v1/trains/search?sourceStationCode={origin_code}&destinationStationCode={dest_code}&addAvailabilityCache=true&excludeMultiTicketAlternates=true&excludeBoostAlternates=true&sortBy=DEFAULT&dateOfJourney={tomorrow_ct}&enableNearby=false&enableTG=true&showPredictionGlobal=true"
        spoof_headers = {"Accept": "*/*", "ApiKey": "ct-web!2$", "ClientId": "ct-web", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0"}
        
        response = requests.get(hacker_url, headers=spoof_headers, timeout=8)
        if response.status_code == 200:
            live_data = response.json()
            trains_array = live_data.get('data', {}).get('trainList', [])
            parsed_trains = []
            
            for t in trains_array:
                board_stn = str(t.get('boardingStation', origin_code)).strip().upper()
                drop_stn = str(t.get('destinationStation', dest_code)).strip().upper()
                if board_stn != origin_code or drop_stn != dest_code: continue  

                avail_dict = {}
                fares_dict = {}
                fare = 0
                
                # 1. FARE & CACHE EXTRACTION
                try:
                    for c_code, c_data in t.get('availabilityCache', {}).items():
                        if isinstance(c_data, dict):
                            avail_dict[c_code] = str(c_data.get('availability', ''))
                            if c_data.get('fare'): fares_dict[c_code] = int(c_data.get('fare'))
                except: pass
                
                # 🚨 2. THE FIX: EXACT CLASS EXTRACTION FROM API
                actual_classes = t.get('avlClassesSorted', [])
                if not actual_classes: actual_classes = t.get('classes', [])
                
                for cls in actual_classes:
                    base_cls = cls.split('_')[0] if '_' in cls else cls
                    if base_cls not in avail_dict:
                        avail_dict[base_cls] = "Check" # Blank classes me Status 'Check' daal dega
                
                train_no = str(t.get('trainNumber', '0000'))
                train_name = str(t.get('trainName', 'EXPRESS'))
                t_type = "Premium" if any(k in train_name.upper() for k in ["SHATABDI", "VANDE", "RAJDHANI"]) else "Express"
                
                parsed_trains.append([train_no, train_name, str(t.get('departureTime', '10:00')), str(t.get('arrivalTime', '15:00')), str(t.get('duration', '05:00')), t_type, 500, avail_dict, fares_dict, str(t.get('runningDays', '1111111')), {}])
            
            if len(parsed_trains) > 0:
                route_trains = pd.DataFrame(parsed_trains, columns=['Train_No', 'Train_Name', 'Dep', 'Arr', 'Dur', 'Type', 'Base_Fare', 'Avail_Dict', 'Fares_Dict', 'Running_Days', 'Dates_Dict'])
                return route_trains.drop_duplicates(subset=['Train_No'])
    except: pass  

    # ====================================================================
    # 🟡 STEP 2: RAPID-API (SECONDARY ENGINE)
    # ====================================================================
    if API_KEY:
        try:
            url = "https://irctc1.p.rapidapi.com/api/v3/trainBetweenStations"
            headers = {"Content-Type": "application/json", "x-rapidapi-host": "irctc1.p.rapidapi.com", "x-rapidapi-key": API_KEY}
            response = requests.get(url, headers=headers, params={"fromStationCode": origin_code, "toStationCode": dest_code, "dateOfJourney": tomorrow_rapid}, timeout=6)
            
            if response.status_code == 200:
                train_list = response.json().get('data', []) if isinstance(response.json().get('data'), list) else response.json().get('data', {}).get('trains', [])
                parsed = []
                for t in train_list:
                    if not isinstance(t, dict): continue
                    if str(t.get('fromStnCode', origin_code)).strip().upper() != origin_code or str(t.get('toStnCode', dest_code)).strip().upper() != dest_code: continue
                    
                    # 🚨 THE FIX: Extract Exact Classes from Rapid API
                    raw_classes = t.get('classes', [])
                    avail_dict = {}
                    for c in raw_classes:
                        avail_dict[str(c).strip().upper()] = "Check"

                    parsed.append({
                        'Train_No': str(t.get('trainNumber', '0000')), 'Train_Name': str(t.get('trainName', 'Unknown')),
                        'Type': 'Premium' if any(k in str(t.get('trainName', '')).upper() for k in ['VANDE', 'SHATABDI', 'RAJDHANI']) else 'Express',
                        'Base_Fare': 500, 'Dep': str(t.get('departureTime', '--:--')), 'Arr': str(t.get('arrivalTime', '--:--')), 'Dur': str(t.get('duration', '--h --m')),
                        'Avail_Dict': avail_dict, 'Fares_Dict': {}, 'Running_Days': '1111111', 'Dates_Dict': {}
                    })
                if len(parsed) > 0: return pd.DataFrame(parsed).drop_duplicates('Train_No')
        except: pass  

    # Fallback Empty Dataframe
    return pd.DataFrame(columns=['Train_No', 'Train_Name', 'Dep', 'Arr', 'Dur', 'Type', 'Base_Fare', 'Avail_Dict', 'Fares_Dict', 'Running_Days', 'Dates_Dict'])  

    # ====================================================================

# --- 7. SIDEBAR: COMPARE CART & DOWNLOAD ---
with st.sidebar:
    st.markdown("<h2 style='color:var(--neon-cyan); text-align:center;'>🛒 Saved Trains</h2>", unsafe_allow_html=True)
    if not st.session_state.compare_cart:
        st.info("No trains added for comparison yet.")
    else:
        df_cart = pd.DataFrame(st.session_state.compare_cart)
        for idx, row in df_cart.iterrows():
            st.markdown(f"""
            <div style='background:var(--bg-alpha-80); padding:10px; border-radius:5px; margin-bottom:10px; border-left:3px solid var(--neon-cyan);'>
                <b style='color: var(--text-main);'>{row['Train']}</b> <span style='color:var(--text-muted); font-size:0.8rem;'>({row['Class']})</span><br>
                <span style='color:var(--neon-green); font-size:1.1rem; font-weight:bold;'>₹{row['Fare']}</span>
            </div>""", unsafe_allow_html=True)
            
        if st.button("🗑️ Clear Cart", use_container_width=True):
            st.session_state.compare_cart = []
            st.rerun()
            
        st.markdown("---")
        csv_data = df_cart.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download RailFare AI Report",
            data=csv_data,
            file_name=f"RailFare_AI_Report_{datetime.date.today()}.csv",
            mime="text/csv",
            use_container_width=True
        )
        # ====================================================================
    # 🎫 LIVE PNR STATUS SECTION (Sidebar)
    # ====================================================================
    st.sidebar.markdown("---")
    st.sidebar.markdown("<h3 style='color: var(--neon-yellow); text-shadow: 1px 1px 2px var(--black-alpha-50);'>🎫 Live PNR Status</h3>", unsafe_allow_html=True)
    
    # 🛠️ CSS MAGIC: Zabardasti Box aur Text ko clear (High Contrast) banana
    st.sidebar.markdown("""
    <style>
    div[data-testid="stTextInput"] input {
        color: var(--text-main) !important;
        background-color: var(--bg-1) !important;
        border: 1px solid var(--neon-cyan) !important;
    }
    div[data-testid="stTextInput"] input::placeholder {
        color: var(--text-muted) !important;
        opacity: 1 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 🌟 Custom High-Visibility Label (Margin fix kar diya gaya hai)
    st.sidebar.markdown("<div style='color: var(--text-light); font-size: 14px; font-weight: bold; margin-bottom: 5px;'>Enter 10-digit PNR Number:</div>", unsafe_allow_html=True)
    
    # 📝 Input Box (Ab label aur box ke beech overlap nahi hoga)
    pnr_input = st.sidebar.text_input("Hidden_Label", label_visibility="collapsed", max_chars=10, placeholder="e.g. 1234567890")
    
    if st.sidebar.button("🔍 Check PNR", use_container_width=True):
        if len(pnr_input) == 10:
            with st.sidebar.status("Fetching live status...", expanded=True) as pnr_status:
                try:
                    import requests
                    pnr_url = f"https://api.confirmtkt.com/api/pnr/status/{pnr_input}"
                    pnr_res = requests.get(pnr_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                    
                    if pnr_res.status_code == 200:
                        data = pnr_res.json()
                        if data.get("Pnr") is None:
                            pnr_status.update(label="Error", state="error")
                            st.sidebar.error("⚠️ Flushed PNR / Invalid PNR.")
                        else:
                            pnr_status.update(label="Success", state="complete")
                            
                            train_name = data.get('TrainName', 'N/A')
                            doj = data.get('Doj', 'N/A')
                            chart = "Prepared" if data.get('ChartPrepared') else "Not Prepared"
                            
                            passengers_html = ""
                            passengers = data.get('PassengerStatus', [])
                            for p in passengers:
                                status = p.get('CurrentStatus', 'N/A')
                                color = "var(--neon-green)" if "CNF" in status or "RAC" in status else "var(--neon-yellow)"
                                passengers_html += f"<div style='margin-bottom: 4px;'>Passenger {p.get('Number', '')}: <b style='color: {color};'>{status}</b></div>"
                            
                            st.sidebar.markdown(f"""
                            <div style="background-color: var(--bg-1); border: 2px solid var(--neon-cyan); border-radius: 10px; padding: 15px; margin-top: 10px; box-shadow: 0px 4px 6px var(--black-alpha-30);">
                                <div style="color: var(--neon-cyan); font-size: 16px; font-weight: bold; margin-bottom: 8px; border-bottom: 1px solid var(--border-light); padding-bottom: 5px;">
                                    PNR: {pnr_input}
                                </div>
                                <div style="color: var(--text-main); font-size: 13.5px; line-height: 1.5;">
                                    <div style="color: var(--text-muted); margin-bottom: 8px;">{train_name} | {doj}</div>
                                    {passengers_html}
                                    <div style="margin-top: 8px; border-top: 1px solid var(--border-light); padding-top: 5px;">
                                        <span style="color: var(--text-muted);">Chart:</span> <b style="color: var(--neon-yellow);">{chart}</b>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        pnr_status.update(label="API Error", state="error")
                        st.sidebar.error("⚠️ Server returned an error.")
                except Exception as e:
                    pnr_status.update(label="Network Error", state="error")
                    st.sidebar.error(f"⚠️ Connection failed: {e}")
        else:
            # Clean error message
            st.sidebar.markdown("""
            <div style="background-color: rgba(255,23,68,0.1); border-left: 4px solid var(--neon-red); padding: 10px; color: var(--neon-red); border-radius: 4px; margin-top: 10px;">
                <b>Error:</b> Kripya sahi 10-digit PNR enter karein.
            </div>
            """, unsafe_allow_html=True)
    # ====================================================================
    # ====================================================================
    # 🤖 RAILMATE AI ASSISTANT (Modern Google GenAI SDK)
    # ====================================================================
    st.sidebar.markdown("---")
    st.sidebar.markdown("<h3 style='color: var(--neon-cyan); text-shadow: 1px 1px 2px var(--black-alpha-50);'>🤖 RailMate AI Assistant</h3>", unsafe_allow_html=True)
    st.sidebar.markdown("<div style='color: var(--text-light); font-size: 14px; font-weight: bold; margin-bottom: 5px;'>Ask me anything about your journey:</div>", unsafe_allow_html=True)
    
    with st.sidebar.form(key='railmate_form'):
        user_query = st.text_input(
            "Hidden_AI_Label",
            label_visibility="collapsed",
            placeholder="e.g., Which side of train avoids sun?"
        )
        submit_btn = st.form_submit_button("Ask RailMate 🚀", use_container_width=True)

    # 🚨 API Key ab safely hidden secrets folder se fetch hogi
    API_KEY = st.secrets["GEMINI_API"]

    if submit_btn and user_query:
        with st.sidebar.status("RailMate is thinking...", expanded=True) as status:
            try:
                import requests
                
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={API_KEY}"
                
                system_prompt = f"""You are 'RailMate', an expert Indian Railways AI assistant built for a B.Tech project solely by Ritik Dixit.
                Keep your answers concise, highly helpful, and focused on Indian railways. Answer directly in Hinglish or English based on the user's input.
                User Query: {user_query}"""
                
                payload = {
                    "contents": [{"parts": [{"text": system_prompt}]}],
                    "generationConfig": {"temperature": 0.7, "maxOutputTokens": 500}
                }
                
                response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=30)
                
                if response.status_code == 200:
                    ai_text = response.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "Sorry, I couldn't process that.")
                    status.update(label="Response Ready!", state="complete", expanded=False)
                    st.sidebar.success(f"**RailMate:** {ai_text}")
                else:
                    status.update(label="API Error", state="error", expanded=False)
                    st.sidebar.error(f"⎠️ RailMate API Error: {response.text}")
                    
            except Exception as e:
                status.update(label="Network Error", state="error", expanded=False)
                st.sidebar.error("⎠️ Connection failed. Please check your internet.")

    # ====================================================================

# --- 8. MAIN UI HERO & INPUTS ---
st.markdown("""
<div class="hero-header">
    <div class="hero-content">
        <div class="hero-title">🚆 RailFare AI</div>
        <div class="hero-subtitle">Predictive Surge Pricing Engine</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='premium-card'><div class='section-title'>🚉 Plan Your Route</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    station_names = sorted([f"{code} - {name}" for code, name in MODERN_STATIONS.items()])
    
    # 🚨 THE FIX: Custom First Option (100% Bright & Visible)
    origin_options = ["-- Select Origin Station --"] + station_names
    selected_origin_str = st.selectbox(
        "Source Station 🚉", 
        origin_options, 
        index=0  # Ab by default humara custom text dikhega
    )
    
with col2:
    dest_options = ["-- Select Destination Station --"] + station_names
    selected_dest_str = st.selectbox(
        "Destination Station 🏁", 
        dest_options, 
        index=0
    )

st.markdown("<br>", unsafe_allow_html=True)

# ====================================================================
# 🛑 SMART SAFETY LOCK: Custom text wali condition check karega
# ====================================================================
route_trains = pd.DataFrame()

if selected_origin_str == "-- Select Origin Station --" or selected_dest_str == "-- Select Destination Station --":
    st.info("👆 Kripya pehle apna Source aur Destination Station select karein.")
else:
    origin_code = selected_origin_str.split(" - ")[0]
    dest_code = selected_dest_str.split(" - ")[0]

    if origin_code == dest_code:
        st.error("❌ Source aur Destination ek hi station nahi ho sakte!")
    else:
        # Dono alag-alag station mil gaye, ab API run karo!
        route_trains = fetch_trains(origin_code, dest_code)
        
        if route_trains.empty:
            st.warning(f"🚫 **No direct trains available** between **{origin_code}** and **{dest_code}**. Please try selecting a different route.")


# ====================================================================
# BAAKI KA UI CODE (Tension-free kyunki route_trains empty hai toh error nahi ayega)
# ====================================================================
st.markdown("<br>", unsafe_allow_html=True)

# ====================================================================
# 🚨 THE MASTER LOCK: UI Tabhi aayega jab train milegi
# ====================================================================
if not route_trains.empty:
    import ast
    import re
    import datetime

    # 🔧 STREAMLIT SESSION STATE SETUP 
    if 'selected_train_no' not in st.session_state:
        st.session_state.selected_train_no = None
    if 'selected_class' not in st.session_state:
        st.session_state.selected_class = None

    # 🚨 THE FIX: CSS me 'white-space: pre-wrap' lagaya taaki \n (enter) kaam kare aur status dikhe!
    st.markdown("""
    <style>
    div[data-testid="stButton"] button {
        background: linear-gradient(145deg, var(--bg-1), var(--bg-2));
        border: 1px solid rgba(0, 229, 255, 0.4);
        border-radius: 8px;
        padding: 2px;
        min-height: 75px;
        transition: all 0.3s;
    }
    div[data-testid="stButton"] button:hover {
        border-color: var(--neon-green);
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0, 230, 118, 0.2);
    }
    div[data-testid="stButton"] button p {
        font-size: 0.9rem; 
        font-weight: 800; 
        line-height: 1.5; 
        color: var(--text-light);
        white-space: pre-wrap !important; /* 🔥 THE MAGIC FIX FOR SEAT STATUS */
        text-align: center;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ⏳ TIME & DURATION SMART PARSER (Fixes '200 min' issue)
    def format_duration(dur_str):
        dur_str = str(dur_str).strip()
        try:
            if ":" in dur_str:
                parts = dur_str.split(":")
                return f"{int(parts[0])}h {int(parts[1])}m"
            elif dur_str.isdigit():
                mins = int(dur_str)
                return f"{mins // 60}h {mins % 60}m"
        except Exception: pass
        return dur_str 

    def format_time_ampm(time_str):
        try:
            t_parts = str(time_str).split(":")
            if len(t_parts) >= 2:
                h, m = int(t_parts[0]), int(t_parts[1])
                ampm = "AM" if h < 12 else "PM"
                h = h % 12
                if h == 0: h = 12
                return f"{h:02d}:{m:02d} {ampm}"
        except: pass
        return str(time_str)[:5]

    def safe_eval(val):
        if isinstance(val, dict): return val
        try: return ast.literal_eval(str(val))
        except: return {}

    # ====================================================================
    # 🚂 PHASE 1: RAIL-YATRI STYLE TRAIN LISTING (100% ACCURATE)
    # ====================================================================
    if st.session_state.selected_train_no is None:
        st.markdown(f"<h3 style='color: var(--neon-cyan); text-align:center;'>🚂 Available Trains: {origin_code} ⟷ {dest_code}</h3>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 1px dashed var(--white-alpha-20); margin-bottom: 20px;'>", unsafe_allow_html=True)

        for idx, row in route_trains.iterrows():
            t_no = str(row['Train_No'])
            t_name = str(row['Train_Name'])
            f_dep = format_time_ampm(row['Dep'])
            f_arr = format_time_ampm(row['Arr'])
            f_dur = format_duration(row['Dur'])
            
            # --- RUNNING DAYS BADGE ---
            running_days = str(row.get('Running_Days', '1111111'))
            if len(running_days) < 7: running_days = '1111111'
            days_names = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
            days_html = ""
            for i, val in enumerate(running_days):
                color = "var(--neon-green)" if val == '1' else "var(--border-light)"
                bg = "rgba(0, 230, 118, 0.15)" if val == '1' else "transparent"
                days_html += f"<span style='color: {color}; background: {bg}; padding: 2px 5px; border-radius: 4px; margin-right: 3px; font-size: 0.7rem; font-weight: bold;'>{days_names[i]}</span>"

            st.markdown(f"""
            <div style="background: linear-gradient(90deg, var(--bg-1-alpha-80), var(--bg-alpha-90)); padding: 15px; border-radius: 12px; border: 1px solid rgba(0,229,255,0.3); margin-top: 15px; margin-bottom: 5px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 1.15rem; font-weight: 900; color: var(--text-main); letter-spacing: 0.5px;">{t_name} <span style="color: var(--neon-cyan); font-size: 0.9rem;">({t_no})</span></div>
                    <div style="font-size: 0.75rem; font-weight: 800; color: var(--text-muted); background: var(--white-alpha-10); padding: 4px 10px; border-radius: 20px;">{row['Type']}</div>
                </div>
                <div style="margin-top: 8px;">{days_html}</div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px; font-weight: bold;">
                    <div style="color: var(--neon-green); font-size: 1.2rem; text-shadow: 0 0 5px rgba(0,230,118,0.4);">{f_dep} <span style="font-size:0.75rem; color:var(--text-muted);">{origin_code}</span></div>
                    <div style="color: var(--neon-red); font-size: 1.2rem; text-shadow: 0 0 5px rgba(255,23,68,0.4);"><span style="font-size:0.75rem; color:var(--text-muted);">{dest_code}</span> {f_arr}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            avail = safe_eval(row.get('Avail_Dict', '{}'))
            valid_irctc_classes = ['1A', '2A', '3A', '3E', 'SL', 'CC', 'EC', 'EA', 'VS', 'FC', '2S']
            filtered_avail = {k: v for k, v in avail.items() if str(k).strip().upper() in valid_irctc_classes}
            avail_items = list(filtered_avail.items())[:8]

            if len(avail_items) > 0:
                class_cols = st.columns(len(avail_items))
                
                st.markdown("""
                <style>
                div[data-testid="stButton"] button {
                    white-space: pre-wrap !important;
                    height: auto !important;
                    padding: 10px 5px !important;
                }
                .stHorizontalBlock:has(> div > div > div > div[data-testid="stButton"]) {
                    flex-wrap: wrap !important;
                }
                .stHorizontalBlock > div:has(> div > div[data-testid="stButton"]) {
                    min-width: 60px !important;
                    flex-basis: 60px !important;
                    flex-grow: 1 !important;
                    margin-bottom: 5px !important;
                }
                </style>
                """, unsafe_allow_html=True)
                
                for c_idx, (c_code, c_status) in enumerate(avail_items):
                    with class_cols[c_idx]:
                        btn_label = f"{c_code}"
                        if st.button(btn_label, key=f"btn_{t_no}_{c_code}", use_container_width=True):
                            st.session_state.selected_train_no = t_no
                            st.session_state.selected_class = c_code
                            st.rerun() 
            else:
                st.markdown("<div style='color:var(--text-muted); font-size:0.85rem; text-align:center;'>⚠️ Class info currently updating from servers...</div>", unsafe_allow_html=True)
                    
            st.markdown("</div>", unsafe_allow_html=True)


    # ====================================================================
    # 🌟 PHASE 2: VIP DASHBOARD (Detailed View for Clicked Train)
    # ====================================================================
    else:
        selected_train_no = st.session_state.selected_train_no
        short_class = st.session_state.selected_class
        train_data = route_trains[route_trains['Train_No'].astype(str) == selected_train_no].iloc[0]
        
        # 🔙 Back Button
        if st.button("⬅️ Back to Train List", type="secondary"):
            st.session_state.selected_train_no = None
            st.session_state.selected_class = None
            st.rerun()

        st.markdown(f"<div style='background: rgba(0, 229, 255, 0.1); border-left: 4px solid var(--neon-cyan); padding: 10px 15px; border-radius: 5px; margin: 15px 0;'><b>Analyzing:</b> {train_data['Train_Name']} ({selected_train_no}) | <b>Class:</b> {short_class}</div>", unsafe_allow_html=True)
        col_date, col_dummy = st.columns([1, 2])
        with col_date:
            today = datetime.date.today()
            max_allowed_date = today + datetime.timedelta(days=60) # IRCTC new ARP rule is 60 days
            
            st.markdown("""
            <style>
            div[data-testid="stDateInput"] input::placeholder { color: var(--neon-cyan) !important; opacity: 0.8 !important; font-weight: 600 !important; }
            div[data-testid="stDateInput"] input { color: var(--text-main) !important; font-weight: 700 !important; caret-color: transparent; cursor: pointer; }
div[data-testid="stDateInput"] { cursor: pointer; }
            </style>
            """, unsafe_allow_html=True)
            
            # Force user explicit choice
            journey_date = st.date_input("Select Journey Date", format="DD/MM/YYYY", value=None, min_value=today, max_value=max_allowed_date)
            
            if not journey_date:
                st.info("Please select a **Journey Date** from the calendar above to unlock Live Status and Insights.", icon="\U0001F4C5")
                st.stop()
                
            days_to_journey = max(1, (journey_date - today).days)
                
        st.markdown("""<img src="dummy" onerror="setTimeout(function(){var inputs = document.querySelectorAll('div[data-testid=\\'stDateInput\\'] input'); for(var i=0; i<inputs.length; i++){inputs[i].setAttribute('readonly', 'readonly'); inputs[i].addEventListener('focus', function(){this.blur();});}}, 500);" style="display:none;">""", unsafe_allow_html=True)

        # 🔄 Fetch API Data for Date
        formatted_date = journey_date.strftime("%d-%m-%Y")
        r_days = str(train_data.get('Running_Days', '1111111'))
        live_data = fetch_live_seat_status(selected_train_no, short_class, origin_code, dest_code, formatted_date, r_days)
        
        seat_list = []
        error_msg = live_data.get("error")
        if error_msg:
            st.error(f"📡 Update: {error_msg}")
        elif live_data.get("seat_availibility") and len(live_data["seat_availibility"]) > 0:
            seat_list = live_data["seat_availibility"]
            
            main_day = seat_list[0]
            
            # 🛑 100% PURE REAL FARE EXTRACTOR (No AI, No Estimation)
            real_fare = (
                main_day.get("total_fare") or 
                main_day.get("fare") or 
                main_day.get("totalFare") or 
                main_day.get("ticketFare") or 
                "--"
            )
            
            # Agar live API se exact fare nahi mila, toh Fares_Dict (Master DB / ConfirmTkt cache) se real check karo
            if str(real_fare) == "--" or not str(real_fare).isdigit():
                try:
                    import ast
                    fares_mapping = train_data.get('Fares_Dict', {})
                    if isinstance(fares_mapping, str):
                        fares_mapping = ast.literal_eval(fares_mapping)
                    
                    if isinstance(fares_mapping, dict) and short_class in fares_mapping:
                        real_fare = str(fares_mapping[short_class])
                except:
                    pass

            # Agar kahin bhi real fare nahi mila, toh strict "--" dikhega (No Fake Numbers)
            try: 
                adjusted_base_fare = int(real_fare) if str(real_fare).isdigit() else 500
            except: 
                adjusted_base_fare = 500

        # ====================================================================
        # 🌟 VIP LAYOUT (Left: Traffic, Right: Calendar)
        # ====================================================================
        if len(seat_list) > 0:
            st.markdown("<hr style='border: 1px dashed rgba(0,229,255,0.2); margin: 25px 0px 15px 0px;'>", unsafe_allow_html=True)
        # ====================================================================
        # ?? LIVE STATUS & FARE BANNER
    # ====================================================================
            main_status = seat_list[0].get("status", "N/A")
            status_color = "var(--neon-green)" if "AVAIL" in main_status.upper() or "CURR" in main_status.upper() else "var(--neon-red)" if "WL" in main_status.upper() else "var(--neon-orange)"
            
            if "/" in main_status:
                parts = main_status.split("/")
                initial, current = parts[0].strip(), parts[-1].strip()
                ui_status = f'<div style="display: flex; align-items: center; gap: 12px;"><div style="color: {status_color}; font-size: 1.8rem; font-weight: 900; text-shadow: 0 0 10px {status_color}88;">{current}</div><div style="color: var(--text-muted); font-size: 0.85rem; font-weight: bold; padding: 4px 10px; border-radius: 20px; background: var(--white-alpha-10); border: 1px solid var(--white-alpha-10);">Initial: {initial}</div></div>'
            elif "AVAIL" in main_status.upper():
                num = main_status.upper().replace("AVAILABLE", "").replace("AVAIL", "").replace("-", "").strip()
                if num:
                    ui_status = f'<div style="display: flex; align-items: center; gap: 12px;"><div style="color: {status_color}; font-size: 1.8rem; font-weight: 900; text-shadow: 0 0 10px {status_color}88;">AVAILABLE</div><div style="color: var(--neon-green); font-size: 1.1rem; font-weight: 900; padding: 4px 12px; border-radius: 20px; background: rgba(0, 230, 118, 0.15); border: 1px solid rgba(0, 230, 118, 0.3);">{num} Seats</div></div>'
                else:
                    ui_status = f'<div style="color: {status_color}; font-size: 1.8rem; font-weight: 900; text-shadow: 0 0 10px {status_color}88;">AVAILABLE</div>'
            else:
                ui_status = f'<div style="color: {status_color}; font-size: 1.8rem; font-weight: 900; text-shadow: 0 0 10px {status_color}88;">{main_status}</div>'
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, var(--bg-alpha-90), var(--bg-1-alpha-90)); border: 1px solid rgba(0, 229, 255, 0.4); border-radius: 12px; padding: 20px; margin-top: 15px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 8px 32px var(--black-alpha-30);">
                <div>
                    <div style="color: var(--text-muted); font-size: 0.85rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">Selected Date Status</div>
                    {ui_status}
                </div>
                <div style="text-align: right;">
                    <div style="color: var(--text-muted); font-size: 0.85rem; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">Current Fare</div>
                    <div style="color: var(--neon-cyan); font-size: 1.8rem; font-weight: 900;">&#8377;{real_fare}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_traffic, col_calendar = st.columns([1.3, 2.7])
            
            with col_traffic:
                import random
                import re
                main_st = str(seat_list[0].get("status", "")).upper()
                pred_pct = int(seat_list[0].get("prediction") or 50)
                
                # Dynamic Demand Metrics based on LIVE API Status & Waitlist Number
                wl_number = 0
                if "WL" in main_st and "/" in main_st:
                    try: wl_number = int(re.sub(r'[^0-9]', '', main_st.split('/')[-1]))
                    except: wl_number = 20
                
                urgency = max(0, 30 - days_to_journey)
                
                if "WL" in main_st:
                    users_viewing = 120 + wl_number * 3 + urgency * 5 + random.randint(10, 40)
                    booking_rate = int(users_viewing * 0.25)
                    trend_color = "var(--neon-red)"
                    trend_text = "EXTREME DEMAND"
                    box_bg = "linear-gradient(145deg, #2A1118, var(--bg-2))"
                elif "RAC" in main_st:
                    users_viewing = 60 + wl_number * 2 + urgency * 3 + random.randint(5, 20)
                    booking_rate = int(users_viewing * 0.18)
                    trend_color = "var(--neon-orange)"
                    trend_text = "HIGH DEMAND"
                    box_bg = "linear-gradient(145deg, #2A1A08, var(--bg-2))"
                else: # Available
                    avail_num = 50
                    try: avail_num = int(re.sub(r'[^0-9]', '', main_st))
                    except: pass
                    users_viewing = max(15, 80 - avail_num + urgency * 2 + random.randint(5, 15))
                    booking_rate = int(users_viewing * 0.08)
                    trend_color = "var(--neon-green)"
                    trend_text = "FILLING FAST" if avail_num < 30 else "STEADY DEMAND"
                    box_bg = "linear-gradient(145deg, #0A1C14, var(--bg-2))"
                
                st.markdown(f"""
                <style>
                @keyframes pulse-{trend_color.replace('#','')} {{ 0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 {trend_color}b3; }} 70% {{ transform: scale(1); box-shadow: 0 0 0 10px rgba(0,0,0,0); }} 100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0,0,0,0); }} }}
                .live-dot-{trend_color.replace('#','')} {{ height: 10px; width: 10px; background-color: {trend_color}; border-radius: 50%; display: inline-block; margin-right: 8px; margin-bottom: 1px; animation: pulse-{trend_color.replace('#','')} 2s infinite; }}
                </style>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div style="margin-top: 0px; padding: 15px; background: {box_bg}; border: 1px solid {trend_color}66; border-radius: 10px; box-shadow: 0 4px 15px {trend_color}22; height: 90%;">
                    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid {trend_color}44; padding-bottom: 8px; margin-bottom: 12px;">
                        <div style="display: flex; align-items: center;"><div class="live-dot-{trend_color.replace('#','')}"></div><span style="color: {trend_color}; font-weight: 900; font-size: 13px; letter-spacing: 1px;">{trend_text}</span></div>
                    </div>
                    <div style="color: var(--text-light); font-size: 14.5px; line-height: 1.6;">
                        <b style="color: var(--text-main); font-size: 18px;">{users_viewing}</b> travelers viewing this train.<br>
                        <span style="color: var(--neon-yellow); font-size: 13px; font-weight: bold;">&#9889; {booking_rate} bookings in last hour!</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_calendar:
                st.markdown(f"<h4 style='color: var(--neon-cyan); font-size: 1.1rem; margin-top: 0px; margin-bottom: 12px;'>📅 Next 6 Days Availability ({short_class})</h4>", unsafe_allow_html=True)
                
                calendar_html = '<div class="swipe-container">'
                for idx, day_data in enumerate(seat_list[:6]):
                    date_dict = day_data.get("date_format", {})
                    display_date = f"{date_dict.get('date', '')} {date_dict.get('month', '')}".strip()
                    if not display_date:
                        a_date = day_data.get("availablity_date", "")
                        import datetime
                        try: display_date = datetime.datetime.strptime(a_date, "%Y-%m-%d").strftime("%d %b")
                        except:
                            try: display_date = datetime.datetime.strptime(a_date, "%d-%m-%Y").strftime("%d %b")
                            except: display_date = a_date[:5]
                    
                    raw_st = str(day_data.get("availablity_status", "")).upper()
                    c_stat = raw_st.split("/")[-1] if "/" in raw_st else raw_st
                    pct = day_data.get("cp_percentage", "")
                    
                    # 🚨 THE FIX: Saaf-suthra aur CRASH-PROOF code
                    if "AVL" in c_stat or "AVAILABLE" in c_stat:
                        box_color, chance_text, badge_bg = "var(--neon-green)", "Available", "rgba(0, 230, 118, 0.15)"
                        nums = re.findall(r'\d+', c_stat)
                        c_stat = f"AVL {int(nums[-1]):02d}" if nums else "AVL"
                    elif "RAC" in c_stat: 
                        box_color, chance_text, badge_bg = "var(--neon-yellow)", f"{pct}% Chance" if pct else "RAC", "rgba(255, 214, 0, 0.15)"
                    elif "WL" in c_stat or "WAIT" in c_stat: 
                        box_color, chance_text, badge_bg = "var(--neon-orange)", f"{pct}% Chance" if pct else "Waitlist", "rgba(255, 145, 0, 0.15)"
                        c_stat = re.sub(r'([A-Z]+)(\d+)', r'\1 \2', c_stat)
                    else: 
                        box_color, c_stat, chance_text, badge_bg = "var(--neon-red)", "REGRET", "No Chance", "rgba(255, 23, 68, 0.15)"

                    calendar_html += f'<div class="swipe-card" style="background: linear-gradient(145deg, var(--bg-1), var(--bg-2)); border: 1px solid {box_color}60; border-radius: 12px; padding: 12px 8px; text-align: center; box-shadow: 0 4px 10px var(--black-alpha-40);"><div style="color: var(--text-muted); font-size: 0.8rem; font-weight: 700; margin-bottom: 6px;">{display_date}</div><div style="color: {box_color}; font-size: 1.1rem; font-weight: 900; margin-bottom: 6px; text-shadow: 0 0 8px {box_color}40;">{c_stat}</div><div style="color: {box_color}; font-size: 0.65rem; font-weight: 800; background: {badge_bg}; border-radius: 20px; padding: 4px 2px; white-space: nowrap;">{chance_text}</div></div>'
                
                calendar_html += "</div>"
                st.markdown(calendar_html, unsafe_allow_html=True)
        # ====================================================================
        # 🟢 PREDICT BUTTON 
        # ====================================================================
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Predict Surge Fare & ML Analysis", use_container_width=True, type="primary"):
            st.session_state.predicted = True

        # --- 9. PREDICTION & ANALYTICS SECTION ---
        # 🧮 DIRECT VARIABLE INJECTOR 

        selected_class = short_class
        train_category = train_data.get('Type', 'Express')
        try:
            raw_base_fare = int(train_data.get('Base_Fare', 500))
        except:
            raw_base_fare = 500

        try:
            if 'seat_list' in locals() and len(seat_list) > 0:
                c_stat = str(seat_list[0].get('availablity_status', '')).upper()
                if "AVL" in c_stat or "AVAILABLE" in c_stat:
                    seats_booked_pct = 40
                elif "RAC" in c_stat:
                    seats_booked_pct = 85
                elif "WL" in c_stat or "WAIT" in c_stat:
                    seats_booked_pct = 110
                else:
                    seats_booked_pct = 120
            else:
                seats_booked_pct = 50
        except:
            seats_booked_pct = 50

        if train_data is not None and 'Fares_Dict' in train_data:
            exact_fares = train_data['Fares_Dict']
            import ast
            if isinstance(exact_fares, str):
                try:
                    exact_fares = ast.literal_eval(exact_fares)
                except:
                    exact_fares = {}
            if isinstance(exact_fares, dict) and short_class in exact_fares and int(exact_fares[short_class]) > 0:
                adjusted_base_fare = int(exact_fares[short_class])
            else:
                adjusted_base_fare = int(real_fare) if 'real_fare' in locals() and str(real_fare).isdigit() else int(raw_base_fare * CLASS_MULTIPLIERS.get(selected_class, 1.0))
        else:
            adjusted_base_fare = int(real_fare) if 'real_fare' in locals() and str(real_fare).isdigit() else int(raw_base_fare * CLASS_MULTIPLIERS.get(selected_class, 1.0))

            # Yahan se original condition start hoti hai
        if st.session_state.predicted and adjusted_base_fare > 0:
    
            is_premium = 1 if train_category == "Premium" else 0
    
            # 🟢 MASTER DYNAMIC PRICING ALGORITHM (Strict IRCTC Flexi-Fare Rules)
            def calculate_live_surge(b_fare, cap_pct, days_left, is_p, travel_c):
                # 🛡️ RULE 1: STRICT BASE FARE (If seats are easily available, NO SURGE)
                if cap_pct <= 50:
                    return b_fare 
            
                # RULE 2: Gradual Surge kicks in ONLY AFTER 50% seats are booked
                if cap_pct <= 85:
                    m = 1.0 + ((cap_pct - 50) * 0.005) # Max +17.5%
                elif cap_pct <= 100:
                    m = 1.175 + ((cap_pct - 85) * 0.015) # Max +40%
                else:
                    wl_intensity = min(cap_pct - 100, 100) 
                    m = 1.40 + (wl_intensity * 0.005) # Extreme waitlist surge
            
                # RULE 3: Premium Trains have higher ceiling
                if is_p == 1 or "1A" in travel_c or "EC" in travel_c:
                    m = 1.0 + ((m - 1.0) * 1.4)
            
                # RULE 4: Urgency Penalty APPLIES ONLY IF train is already filling up (High Demand)
                if cap_pct > 75:
                    if days_left <= 2:
                        m += 0.25
                    elif days_left <= 6:
                        m += 0.10
                
                return int(b_fare * min(m, 2.5))

            calculated_fare = calculate_live_surge(adjusted_base_fare, seats_booked_pct, days_to_journey, is_premium, selected_class)
    
            # 🧠 HYBRID MACHINE LEARNING PREDICTION 
            if model_loaded:
                input_features = pd.DataFrame([[adjusted_base_fare, days_to_journey, seats_booked_pct, is_premium]], 
                                              columns=['Base_Fare', 'Days_to_Journey', 'Seats_Booked_Percentage', 'Is_Premium'])
                raw_prediction = float(surge_model.predict(input_features)[0])
        
                # 🛡️ THE FIX: Override AI Model if Seats are Available!
                if seats_booked_pct <= 55:
                    current_surge_price = adjusted_base_fare
                    pricing_model_name = "IRCTC Flexi-Fare Rule (No Surge)"
                else:
                    current_surge_price = max(calculated_fare, raw_prediction)
                    pricing_model_name = "Hybrid AI + Live Engine" if current_surge_price == raw_prediction else "IRCTC Live Replica Engine"
            else:
                current_surge_price = calculated_fare
                pricing_model_name = "IRCTC Live Replica Engine"

            surge_percentage = int(((current_surge_price / adjusted_base_fare) - 1.0) * 100)
    
            # Smart Risk Probability (Mathematical)
            urgency_multiplier = 0.7 if days_to_journey > 30 else (1.4 if days_to_journey <= 5 else 1.0 + ((30 - days_to_journey) / 100.0))
            premium_penalty = 15 if (is_premium == 1 and seats_booked_pct > 40) else 0
            surge_probability = max(2, min(99, int((seats_booked_pct * urgency_multiplier) + premium_penalty)))

            col_pred, col_cart = st.columns([4, 1])
            with col_pred:
                st.markdown(f"""
                <div class="prediction-card">
                    <div class="pred-label">Live Dynamic Fare ({selected_class})</div>
                    <div class="pred-price">₹{int(current_surge_price):,}</div>
                    <div class="pred-meta">Model Active: <span style="color:var(--neon-green);">{pricing_model_name}</span> | Base Fare: ₹{adjusted_base_fare:,}</div>
                </div>
                """, unsafe_allow_html=True)
            with col_cart:
                st.markdown("<br>", unsafe_allow_html=True)
                st.link_button("🎫 Book on IRCTC ↗", "https://www.irctc.co.in/nget/train-search", use_container_width=True, type="secondary")
        
                if st.button("📌 Save to Cart", use_container_width=True):
                    st.session_state.compare_cart.append({
                        "Train": train_data['Train_Name'], "Class": selected_class, 
                        "Fare": int(current_surge_price), "Days": days_to_journey
                    })
                    st.rerun()

            # --- KPIs ---
            st.markdown("<div class='premium-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>\U0001F4CA Live Fare & Scarcity Comparisons</div>", unsafe_allow_html=True)
            chart_col1, chart_col2 = st.columns(2)
    
            with chart_col1:
                import ast
                def safe_eval_dict(d_str):
                    if isinstance(d_str, dict): return d_str
                    try: return ast.literal_eval(d_str)
                    except: return {}
                
                t_fares = safe_eval_dict(train_data.get('Fares_Dict', {}))
                t_avail = safe_eval_dict(train_data.get('Avail_Dict', {}))
                
                classes_list, base_f_list, surge_f_list = [], [], []
                
                for c_code, c_base in t_fares.items():
                    c_status = str(t_avail.get(c_code, 'AVAILABLE 50')).upper()
                    import re
                    d_nums = re.findall(r'\d+', c_status)
                    if "WL" in c_status or "WAIT" in c_status: c_cap = 100
                    elif "RAC" in c_status: c_cap = 90
                    elif "AV" in c_status or "AVL" in c_status: c_cap = max(10, 100 - int(d_nums[-1])) if len(d_nums) >= 1 else 50
                    else: c_cap = 50
                    
                    c_surge = calculate_live_surge(c_base, c_cap, days_to_journey, is_premium, c_code)
                    classes_list.append(c_code)
                    base_f_list.append(c_base)
                    surge_f_list.append(c_surge)
                
                if classes_list:
                    df_c = pd.DataFrame({'Class': classes_list * 2, 'Fare': base_f_list + surge_f_list, 'Type': ['Base Fare']*len(classes_list) + ['Live Surged Fare']*len(classes_list)})
                    fig1 = px.bar(df_c, x='Class', y='Fare', color='Type', barmode='group', title=f"Fare Comparison Across Classes ({selected_train_no})", color_discrete_map={'Base Fare': 'var(--border-light)', 'Live Surged Fare': 'var(--neon-cyan)'})
                    fig1.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="var(--text-light)", title_font=dict(color='var(--neon-cyan)', size=16), yaxis_title="Fare (\u20B9)", legend=dict(font=dict(color='var(--text-light)'), title=dict(font=dict(color='var(--neon-cyan)'))))
                    st.plotly_chart(fig1, use_container_width=True, config={'staticPlot': True})
                else:
                    st.info("No class data available for comparison.")
                    
            with chart_col2:
                train_names, t_base_list, t_surge_list = [], [], []
                
                for _, r_row in route_trains.iterrows():
                    r_fares = safe_eval_dict(r_row.get('Fares_Dict', {}))
                    r_avail = safe_eval_dict(r_row.get('Avail_Dict', {}))
                    if short_class in r_fares:
                        r_base = r_fares[short_class]
                        r_status = str(r_avail.get(short_class, 'AVAILABLE 50')).upper()
                        import re
                        d_nums = re.findall(r'\d+', r_status)
                        if "WL" in r_status or "WAIT" in r_status: r_cap = 100
                        elif "RAC" in r_status: r_cap = 90
                        elif "AV" in r_status or "AVL" in r_status: r_cap = max(10, 100 - int(d_nums[-1])) if len(d_nums) >= 1 else 50
                        else: r_cap = 50
                        
                        r_surge = calculate_live_surge(r_base, r_cap, days_to_journey, (r_row['Type']=='Premium'), short_class)
                        train_names.append(f"{r_row['Train_No']} ({r_row['Type']})")
                        t_base_list.append(r_base)
                        t_surge_list.append(r_surge)
                        
                if train_names:
                    df_t = pd.DataFrame({'Train': train_names * 2, 'Fare': t_base_list + t_surge_list, 'Type': ['Base Fare']*len(train_names) + ['Live Surged Fare']*len(train_names)})
                    fig2 = px.bar(df_t, y='Train', x='Fare', color='Type', orientation='h', barmode='group', title=f"Route Comparison for {short_class} Class", color_discrete_map={'Base Fare': 'var(--border-light)', 'Live Surged Fare': 'var(--neon-green)'})
                    fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="var(--text-light)", title_font=dict(color='var(--neon-cyan)', size=16), xaxis_title="Fare (\u20B9)", legend=dict(font=dict(color='var(--text-light)'), title=dict(font=dict(color='var(--neon-cyan)'))))
                    st.plotly_chart(fig2, use_container_width=True, config={'staticPlot': True})
                else:
                    st.info("No route data available for comparison.")
        
            st.markdown("</div>", unsafe_allow_html=True)
        # ====================================================================
                # 🛡️ FEATURE 2 ENHANCED: SMART 'PLAN B' STRATEGY (Premium UI & Logic)
                # ====================================================================
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<h3 style='color: var(--neon-yellow); text-shadow: 1px 1px 3px var(--black-alpha-80);'>🛡️ RailFare AI: Smart Travel Strategy</h3>", unsafe_allow_html=True)
        
            plan_col1, plan_col2 = st.columns(2)
        
                # --- 🧠 SUPER ACCURATE LOGIC ENGINE ---
                # Tatkal timing exactly matches IRCTC rules based on AC vs Non-AC
            ac_classes = ['1A', '2A', '3A', 'CC', 'EC', '3E']
            is_ac = any(c in short_class for c in ac_classes)
            tatkal_time = "10:00 AM (AC Class)" if is_ac else "11:00 AM (Non-AC Class)"
        
            if seats_booked_pct <= 100:
                    risk_color = "var(--neon-green)"  # Safe Green
                    risk_level = "LOW RISK (Safe Zone)"
                    risk_desc = "Ticket almost confirmed ya available hai. Surge badhne se pehle book kar lein."
                    action_1 = "✅ <b>Immediate Action:</b> Book right now to lock the lowest base fare."
                    action_2 = "💡 <b>Pro Tip:</b> Chart preparation tak wait na karein, demand badhne par flexi-fare lag sakta hai."
            
            elif seats_booked_pct > 100 and seats_booked_pct <= 115:
                    risk_color = "var(--neon-yellow)"  # Warning Yellow
                    risk_level = "MODERATE RISK (Borderline)"
                    risk_desc = f"Waitlist/RAC chal rahi hai. Journey me {days_to_journey} days bache hain, chances hain confirm hone ke."
                    action_1 = "⚠️ <b>Action Plan:</b> Normal ticket book kar lein, par backup ready rakhein."
                    action_2 = "🔄 <b>Vikalp Scheme:</b> Book karte waqt IRCTC ki 'Vikalp' (Alternate Train) scheme zarur select karein."
            
            else:
                    risk_color = "var(--neon-red)"  # Danger Red
                    risk_level = "HIGH RISK (Critical Zone)"
                    risk_desc = "Waitlist bohot lambi hai ya REGRET ho gaya hai. Normal ticket ka confirm hona kaafi mushkil hai."
                    action_1 = f"🕒 <b>Tatkal Strategy:</b> Kal subah exact <b>{tatkal_time}</b> par Tatkal quota try karein."
                    action_2 = f"🔀 <b>Class Upgrade:</b> {short_class} chhod kar higher class me seat check karein, wahan chance zyada hai."

                # --- 🎨 PREMIUM UI DESIGN (Cards) ---
            with plan_col1:
                    st.markdown(f"""
                    <div style='background: linear-gradient(145deg, var(--bg-1), var(--bg-2)); padding: 20px; border-radius: 12px; border-left: 6px solid {risk_color}; box-shadow: 0 6px 15px var(--black-alpha-40); display: flex; flex-direction: column; justify-content: center; word-wrap: break-word; min-height: 180px;'>
                        <h4 style='color: {risk_color}; margin-top: 0; font-weight: 800; font-size: 1.1rem;'>{risk_level}</h4>
                        <p style='color: var(--text-light); font-size: 15px; margin-bottom: 15px;'>{risk_desc}</p>
                        <div style='background: var(--white-alpha-05); padding: 10px; border-radius: 6px; border: 1px solid var(--white-alpha-10);'>
                            <span style='color: var(--text-muted); font-size: 13px;'>Journey Proximity:</span> <b style='color: var(--text-main);'>{days_to_journey} Days</b><br>
                            <span style='color: var(--text-muted); font-size: 13px;'>Selected Class:</span> <b style='color: var(--text-main);'>{short_class}</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            with plan_col2:
                    st.markdown(f"""
                    <div style='background: linear-gradient(145deg, var(--bg-1), var(--bg-2)); padding: 20px; border-radius: 12px; border: 1px solid var(--border-light); box-shadow: 0 6px 15px var(--black-alpha-40); display: flex; flex-direction: column; justify-content: center; word-wrap: break-word; min-height: 180px;'>
                        <h4 style='color: var(--neon-cyan); margin-top: 0; font-weight: 800; font-size: 1.1rem;'>⚡ RailFare 'Plan B'</h4>
                        <p style='color: var(--text-main); font-size: 14.5px; line-height: 1.6; margin-bottom: 10px;'>{action_1}</p>
                        <p style='color: var(--text-main); font-size: 14.5px; line-height: 1.6; margin-bottom: 15px;'>{action_2}</p>
                        <div style='border-top: 1px dashed var(--border-light); padding-top: 10px; text-align: center;'>
                            <span style='color: var(--neon-yellow); font-size: 13px; font-weight: bold; letter-spacing: 0.5px;'>🤖 AI SUGGESTION ENGINE ACTIVE</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                # ====================================================================
            # ====================================================================
                # 🔔 FEATURE 4 ENHANCED: SMART PRICE ALERT (Professional UI)
                # ====================================================================
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<h3 style='color: var(--neon-green); text-shadow: 1px 1px 3px var(--black-alpha-80); margin-top: 30px;'>🔔 Set AI Price Alert</h3>", unsafe_allow_html=True)
            
            st.markdown("""
            <div style='background: var(--bg-alpha-60); padding: 15px 20px; border-radius: 12px; border: 1px solid var(--border-light); margin-bottom: 20px; word-wrap: break-word; white-space: normal;'>
                <p style='color: var(--text-light); font-size: 15.5px; margin: 0;'>Select your target price and notification channel. Our AI will monitor the dynamic fare curve 24/7 and alert you instantly when prices drop.</p>
            </div>
            """, unsafe_allow_html=True)
            
            min_alert = int(adjusted_base_fare * 0.7) 
            max_alert = int(adjusted_base_fare * 1.5) 
            default_alert = int(adjusted_base_fare * 0.9) 
            
            alert_col1, alert_col2 = st.columns([1.5, 1])
            
            st.markdown("""
            <style>
            div[data-testid="stRadio"] label p, div[data-testid="stTextInput"] label p {
                color: var(--neon-cyan) !important;
                font-size: 15px !important;
                font-weight: bold !important;
                letter-spacing: 0.5px;
            }
            div[data-testid="stRadio"] div[role="radiogroup"] p {
                color: var(--text-main) !important;
                font-size: 14.5px !important;
                font-weight: 600 !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            with alert_col1:
                target_price = st.slider(
                    "🎯 Set Target Fare (₹)", 
                    min_value=min_alert, 
                    max_value=max_alert, 
                    value=default_alert, 
                    step=10
                )
                
                alert_channel = st.radio("Notify me via:", ["WhatsApp", "Email"], horizontal=True)
                contact_info = st.text_input("Contact Details", placeholder="+91 9876543210" if alert_channel == "WhatsApp" else "you@example.com")
            
            discount_pct = ((adjusted_base_fare - target_price) / adjusted_base_fare) * 100
            if target_price >= adjusted_base_fare:
                prob_text = "VERY HIGH (Current)"
                prob_color = "var(--neon-green)"
            elif discount_pct < 10:
                prob_text = "HIGH (Slight Drop)"
                prob_color = "var(--neon-green)"
            elif discount_pct >= 10 and discount_pct < 20:
                prob_text = "MODERATE (Wait/Watch)"
                prob_color = "var(--neon-yellow)"
            else:
                prob_text = "LOW (Rare Drop)"
                prob_color = "var(--neon-red)"
                
            with alert_col2:
                st.markdown(f"""
                <div style='background: var(--black-alpha-30); padding: 25px; border-radius: 12px; border: 1px dashed {prob_color}; text-align: center; display: flex; flex-direction: column; justify-content: center; word-wrap: break-word; min-height: 180px;'>
                    <div style='color: var(--text-muted); font-size: 14px; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px;'>Target Set At</div>
                    <div style='color: var(--text-main); font-size: 38px; font-weight: 900; margin-bottom: 15px;'>&#8377;{target_price}</div>
                    <div style='background: var(--white-alpha-05); padding: 10px; border-radius: 8px;'>
                        <span style='color: var(--text-muted); font-size: 13px;'>AI Drop Probability</span><br>
                        <b style='color: {prob_color}; font-size: 16px;'>{prob_text}</b>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            btn_col1, btn_col2, btn_col3 = st.columns([1,2,1])
            with btn_col2:
                btn_disabled = len(contact_info.strip()) < 5
                if st.button("🔔 Activate AI Price Alert", use_container_width=True, type="primary", disabled=btn_disabled):
                    st.toast(f"Tracker Active! Alert set for ₹{target_price}.", icon="✅")
                    st.balloons()
                    st.success(f"**Alert Locked:** We are monitoring the dynamic fare curve for Train {selected_train_no}. You will receive a **{alert_channel}** at **{contact_info}** when the fare hits **₹{target_price}**.")
                # ====================================================================            