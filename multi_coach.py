import sys

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if 'total_seats = comp_count * (left_seats + right_seats)' in line:
        start_idx = i
    if start_idx != -1 and 'st.markdown(html, unsafe_allow_html=True)' in line:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    new_code = []
    
    new_code_str = '''            total_seats = comp_count * (left_seats + right_seats)
            
            avail_count = 15 # default fallback
            try:
                import re
                if 'AVAILABLE' in main_status.upper() and 'NOT AVAIL' not in main_status.upper():
                    match = re.search(r'\\d+', main_status)
                    if match: avail_count = int(match.group())
                elif 'RAC' in main_status.upper():
                    avail_count = 5
                elif 'WL' in main_status.upper():
                    avail_count = 0
            except:
                pass
                
            import math
            num_coaches = math.ceil(avail_count / total_seats) if avail_count > 0 else 1
            if num_coaches > 5: num_coaches = 5 # Cap at 5 coaches for UI performance
            
            coaches_avail = []
            remaining_avail = avail_count
            for c in range(num_coaches):
                if remaining_avail >= total_seats:
                    coaches_avail.append(total_seats)
                    remaining_avail -= total_seats
                else:
                    coaches_avail.append(remaining_avail)
                    remaining_avail = 0
                    
            coach_names = [f"{prefix}{random.randint(1, 9)}" for _ in range(num_coaches)]
            tabs = st.tabs([f"COACH {c}" for c in coach_names])
            
            for tab_idx, tab in enumerate(tabs):
                with tab:
                    c_avail = coaches_avail[tab_idx]
                    seats = ['booked'] * total_seats
                    available_indices = random.sample(range(total_seats), c_avail)
                    for idx in available_indices:
                        seats[idx] = 'available'
                        
                    html = f"""
                    <div style='background: var(--bg-1); padding: 15px; border-radius: 10px; border: 1px solid var(--white-alpha-20); margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <p style='color: var(--text-muted); font-size: 14px; margin: 0;'>
                                Coach Type: <strong style='color: var(--text-light);'>{s_class}</strong> | Layout: {total_seats} Seats<br>
                                <span style='color: var(--neon-green); font-weight: bold;'>Green</span>: Available | <span style='color: var(--neon-red); font-weight: bold;'>Red</span>: Booked
                            </p>
                        </div>
                        <div style='background: var(--neon-cyan); color: #000; padding: 5px 15px; border-radius: 8px; font-weight: bold; font-size: 18px;'>
                            COACH {coach_names[tab_idx]}
                        </div>
                    </div>
                    """
                    
                    html += "<div style='display: flex; flex-direction: column; gap: 10px; max-width: 320px; margin: 0 auto;'>"
                    
                    for comp in range(comp_count):
                        html += "<div style='background: var(--white-alpha-05); border: 1px solid var(--white-alpha-10); border-radius: 8px; padding: 10px; display: flex; justify-content: space-between;'>"
                        
                        cols_left = 2 if s_class in ['SL', '3A', '2A', '1A', '3E'] else left_seats
                        html += f"<div style='display: grid; grid-template-columns: repeat({cols_left}, 35px); gap: 5px;'>"
                        for i in range(left_seats):
                            seat_idx = comp * (left_seats + right_seats) + i
                            status = seats[seat_idx]
                            color = "var(--neon-green)" if status == 'available' else "var(--neon-red)"
                            bg = "rgba(0, 255, 0, 0.15)" if status == 'available' else "rgba(255, 0, 0, 0.15)"
                            html += f"<div style='width: 35px; height: 35px; border-radius: 6px; background: {bg}; border: 1px solid {color}; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; color: {color};'>{seat_idx+1}</div>"
                        html += "</div>"
                        
                        if right_seats > 0:
                            html += "<div style='width: 20px; border-left: 2px dashed var(--white-alpha-10); border-right: 2px dashed var(--white-alpha-10);'></div>"
                            
                            cols_right = 1 if s_class in ['SL', '3A', '2A', '1A', '3E'] else right_seats
                            html += f"<div style='display: grid; grid-template-columns: repeat({cols_right}, 35px); gap: 5px; align-content: center;'>"
                            for i in range(right_seats):
                                seat_idx = comp * (left_seats + right_seats) + left_seats + i
                                status = seats[seat_idx]
                                color = "var(--neon-green)" if status == 'available' else "var(--neon-red)"
                                bg = "rgba(0, 255, 0, 0.15)" if status == 'available' else "rgba(255, 0, 0, 0.15)"
                                html += f"<div style='width: 35px; height: 35px; border-radius: 6px; background: {bg}; border: 1px solid {color}; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; color: {color};'>{seat_idx+1}</div>"
                            html += "</div>"
                            
                        html += "</div>"
                        
                    html += "</div>"
                    st.markdown(html, unsafe_allow_html=True)\n'''
                    
    # The new_code_str has exact indentation matching the outer `if else` loop.
    lines[start_idx:end_idx+1] = [new_code_str]
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("Multi-coach layout implemented successfully.")
else:
    print("Could not find block.")

