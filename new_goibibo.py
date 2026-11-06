import requests
import json
from datetime import datetime

def map_goibibo_live_status(data, train_no):
    if not data or not data.get("success"):
        return {"status": "UNAVAILABLE", "error": "Live data temporarily unavailable"}
    
    train_name = data.get("trainType", data.get("fromCity", "Train"))
    running_status_obj = data.get("trainRunningStatus")
    stations = data.get("stations", [])
    
    # Defaults
    status_msg = "No live update available"
    last_station_name = None
    next_station_name = None
    sch_arr = None
    act_arr = None
    delay_mins = None
    
    # 1. Determine running state
    if running_status_obj:
        msg = running_status_obj.get("running_status_message", "").lower()
        if "not started" in msg or "will start" in msg or "departed from source" in msg and delay_mins == 0: 
            # Wait, checking actual message. MMT puts "has departed from..." or "is yet to start".
            status_msg = "Live running"
            if "yet to start" in msg or "not started" in msg:
                status_msg = "Not started yet"
            elif "reached destination" in msg or "completed" in msg:
                status_msg = "Journey completed"
        else:
            status_msg = "Live running"
            
        last_station_name = running_status_obj.get("last_reported_station_name")
        delay_mins = running_status_obj.get("delay_in_mins")
        
        # Try to map actual/scheduled arrival from the matched station
        for i, st in enumerate(stations):
            if st.get("station_name") == last_station_name or st.get("station_code") == running_status_obj.get("last_reported_station_code"):
                sch_arr = st.get("arrival_time") or st.get("departure_time")
                act_arr = st.get("actual_arrival_time") or st.get("actual_departure_time")
                if i + 1 < len(stations):
                    next_station_name = stations[i+1].get("station_name")
                break
    else:
        # If trainRunningStatus is missing, check if any station has actual arrival/departure
        has_started = False
        last_visited_idx = -1
        
        for i, st in enumerate(stations):
            if st.get("actual_arrival_time") or st.get("actual_departure_time"):
                has_started = True
                last_visited_idx = i
                
        if has_started:
            status_msg = "Live running"
            st = stations[last_visited_idx]
            last_station_name = st.get("station_name")
            sch_arr = st.get("arrival_time") or st.get("departure_time")
            act_arr = st.get("actual_arrival_time") or st.get("actual_departure_time")
            
            # Calculate delay roughly if possible, but strict rule says don't invent if not provided.
            # We won't invent delay if not provided explicitly by trainRunningStatus unless we must.
            # The prompt says "Delay, only when returned".
            delay_mins = None 
            
            if last_visited_idx + 1 < len(stations):
                next_station_name = stations[last_visited_idx+1].get("station_name")
            else:
                status_msg = "Journey completed"
        else:
            # Check operating days logic or just say not started vs no update
            # No actual times, no running status obj -> either not started or not running or no data.
            # We cannot invent "Source station" as current station according to the rule!
            # "Replace all current fallback values such as: Source station as current station..."
            status_msg = "No live update available"
            
            # Special check if the API message itself says something
            if data.get("error"):
                status_msg = "Train does not run on this date"
                
    return {
        "status": "SUCCESS",
        "train_no": str(train_no),
        "train_name": train_name,
        "running_status": status_msg,
        "last_reported_station": last_station_name,
        "next_station": next_station_name,
        "actual_arrival": act_arr,
        "scheduled_arrival": sch_arr,
        "delay_minutes": delay_mins,
        "source": "GoIbibo",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def fetch_goibibo_live_status(train_no, journey_date):
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'origin': 'https://www.goibibo.com',
        'referer': 'https://www.goibibo.com/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36',
    }

    try:
        # Convert date to YYYYMMDD if possible
        if "-" in journey_date:
            parts = journey_date.split("-")
            if len(parts[0]) == 4: # YYYY-MM-DD
                dt_obj = datetime.strptime(journey_date, "%Y-%m-%d")
                journey_date = dt_obj.strftime("%Y%m%d")
                
        params = {
            'train_code': str(train_no),
            'flavour': 'mweb',
            'journey_date': journey_date
        }

        response = requests.get('https://rails-ris.makemytrip.com/api/ris/platform/locator/v1', params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return map_goibibo_live_status(response.json(), train_no)
            
        return {"status": "UNAVAILABLE", "error": "Live data temporarily unavailable"}
    except Exception as e:
        print(f"[Developer Log] Live Status API failed: {str(e)}")
        return {"status": "UNAVAILABLE", "error": "Live data temporarily unavailable"}

