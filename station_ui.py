import textwrap
import streamlit as st
import datetime

def render_station_congestion(data):
    if not data:
        st.info("No congestion data available for this station.")
        return
        
    if "error" in data:
        st.error(data["error"])
        return
        
    # Extract
    forecast = data.get("hourly_forecast", {})
    last_updated = data.get("last_updated", datetime.datetime.now().strftime("%I:%M %p"))
    
    # Configuration
    level_map = {
        "Low": {"color": "#4caf50", "icon": "🟢", "bars": "███░░░░░░░", "width": "30%"},
        "Moderate": {"color": "#ff9800", "icon": "🟡", "bars": "██████░░░░", "width": "60%"},
        "High": {"color": "#ff5722", "icon": "🟠", "bars": "████████░░", "width": "80%"},
        "Very High": {"color": "#d32f2f", "icon": "🔴", "bars": "██████████", "width": "100%"},
    }

    # Header / Meta
    html = f"""
    <div style="background: var(--bg-alpha-50); border: 1px solid var(--white-alpha-10); border-radius: 12px; padding: 20px; margin-top: 15px;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--white-alpha-10); padding-bottom: 12px; margin-bottom: 15px;">
            <div>
                <h3 style="margin: 0; font-size: 1.2rem; display: flex; align-items: center; gap: 8px;">
                    📊 Station Congestion Forecast
                    <span style="font-size: 0.7rem; background: var(--white-alpha-10); padding: 2px 8px; border-radius: 12px; font-weight: normal;">PREDICTED</span>
                </h3>
                <div style="color: var(--text-muted); font-size: 0.85rem; margin-top: 5px;">
                    Estimated from train schedules and historical patterns • Updated {last_updated}
                </div>
            </div>
        </div>
        
        <!-- Legend -->
        <div style="display: flex; gap: 15px; font-size: 0.85rem; color: var(--text-muted); margin-bottom: 20px; flex-wrap: wrap;">
            <div><span style="color: #4caf50;">■</span> Low</div>
            <div><span style="color: #ff9800;">■</span> Moderate</div>
            <div><span style="color: #ff5722;">■</span> High</div>
            <div><span style="color: #d32f2f;">■</span> Very High</div>
        </div>
        
        <!-- Chart -->
        <div style="display: flex; flex-direction: column; gap: 10px; max-height: 400px; overflow-y: auto; padding-right: 5px;">
    """
    
    # Current time to highlight next slot
    now = datetime.datetime.now()
    current_hour = now.hour
    
    for time_str, level in forecast.items():
        # Parse hour from "08:00"
        try:
            slot_hour = int(time_str.split(":")[0])
        except:
            slot_hour = -1
            
        config = level_map.get(level, level_map["Low"])
        
        # Highlight logic (just bold/accent the current/next hour if possible, or mark 'Peak')
        is_peak = level in ["High", "Very High"]
        peak_badge = f'<span style="background: {config["color"]}22; color: {config["color"]}; font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; margin-left: 8px; font-weight: bold;">PEAK</span>' if is_peak else ''
        
        # Draw Bar
        html += f"""
        <div style="display: flex; align-items: center; gap: 15px; width: 100%;">
            <div style="width: 55px; font-weight: bold; font-family: monospace; font-size: 0.95rem; color: var(--text-main);">{time_str}</div>
            <div style="flex-grow: 1; background: var(--white-alpha-05); height: 16px; border-radius: 8px; overflow: hidden; display: flex; align-items: center;">
                <div style="width: {config['width']}; background: {config['color']}; height: 100%; border-radius: 8px; transition: width 0.5s ease;"></div>
            </div>
            <div style="width: 100px; font-size: 0.85rem; color: var(--text-muted); display: flex; align-items: center;">
                {config['icon']} {level} {peak_badge}
            </div>
        </div>
        """
        
    # Footer / Summary
    html += f"""
        </div>
        <div style="margin-top: 20px; padding: 12px; background: rgba(255, 152, 0, 0.1); border-left: 4px solid #ff9800; border-radius: 6px; font-size: 0.9rem;">
            <strong>Expected Peak:</strong> {", ".join(data.get("peak_periods", []))}. 
            {data.get("suggested_buffer", "Plan your arrival accordingly.")}
        </div>
    </div>
    """
    
    import re
    minified_html = re.sub(r'\n\s*', ' ', html)
    st.markdown(minified_html, unsafe_allow_html=True)

