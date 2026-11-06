import sys

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

old_logic = '''    if origin_code == dest_code:
        st.error("❌ Source aur Destination ek hi station nahi ho sakte!")
    else:
        route_trains = fetch_trains(origin_code, dest_code, journey_date)'''

new_logic = '''    if origin_code == dest_code:
        st.error("❌ Source aur Destination ek hi station nahi ho sakte!")
    else:
        raw_trains = fetch_trains(origin_code, dest_code, journey_date)
        
        route_trains = pd.DataFrame()
        if not raw_trains.empty:
            verified_trains = []
            day_name = journey_date.strftime("%A")
            day_abbr = journey_date.strftime("%a")
            idx = journey_date.weekday() # 0 = Mon, 6 = Sun. (Assuming ConfirmTkt uses Mon=0 for 1111111 strings)
            
            for _, row in raw_trains.iterrows():
                rd = str(row.get('Running_Days', '')).strip().upper()
                runs = False
                verified = True
                
                if not rd or rd == 'UNKNOWN' or rd == 'NONE' or rd == 'NAN' or rd == '1111111':
                    # If it's the exact default 1111111 fallback from Rapid API when missing, treat as verified running daily.
                    if rd == '1111111':
                        runs = True
                    else:
                        verified = False
                elif 'DAILY' in rd:
                    runs = True
                elif ',' in rd or any(c.isalpha() for c in rd):
                    if day_name.upper() in rd or day_abbr.upper() in rd:
                        runs = True
                    else:
                        runs = False
                elif len(rd) >= 7:
                    try:
                        if rd[idx] == '1':
                            runs = True
                        else:
                            runs = False
                    except:
                        verified = False
                else:
                    verified = False
                
                if verified and runs:
                    verified_trains.append(row)
                    
            if not verified_trains:
                st.warning("🚫 **No trains are scheduled to run on your selected date.** Try another date or nearby stations.")
                route_trains = pd.DataFrame()
            else:
                route_trains = pd.DataFrame(verified_trains)
                st.markdown(f"<div style='color: var(--neon-cyan); font-size: 1.1rem; font-weight: bold; margin-bottom: 10px; padding: 10px; background: var(--bg-alpha-50); border-radius: 8px;'>📅 Showing trains running on {day_name}, {journey_date.strftime('%d %B %Y')}</div>", unsafe_allow_html=True)'''

if old_logic in code:
    code = code.replace(old_logic, new_logic)
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("Filter logic added successfully!")
else:
    print("Could not find the old logic block.")

