# ====================================================================
# 🤖 FLOATING RAILMATE AI (WhatsApp Meta AI Style)
# ====================================================================
st.markdown("""
<style>
/* Floating Button Container */
div[data-testid="stPopover"] {
    position: fixed !important;
    bottom: 30px !important;
    right: 30px !important;
    z-index: 99999 !important;
}
/* WhatsApp/Meta AI Style Button */
div[data-testid="stPopover"] > button {
    border-radius: 50px !important;
    padding: 12px 24px !important;
    background: linear-gradient(135deg, #25D366, #128C7E) !important; /* WhatsApp Green */
    color: white !important;
    box-shadow: 0 4px 15px rgba(37, 211, 102, 0.4) !important;
    border: none !important;
    transition: all 0.3s ease !important;
}
div[data-testid="stPopover"] > button:hover {
    transform: scale(1.05) !important;
    box-shadow: 0 6px 20px rgba(37, 211, 102, 0.6) !important;
}
/* Text inside button */
div[data-testid="stPopover"] > button p {
    font-size: 16px !important;
    font-weight: 800 !important;
    margin: 0 !important;
    color: white !important;
}
/* Style the Popover Body */
div[data-testid="stPopoverBody"] {
    border: 2px solid #25D366 !important;
    background: var(--bg-1) !important;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3) !important;
    border-radius: 16px !important;
    width: 350px !important;
    padding: 20px !important;
}
</style>
""", unsafe_allow_html=True)

with st.popover("💬 RailMate AI"):
    st.markdown("<h3 style='color: #25D366; margin-top: 0;'>🤖 RailMate AI</h3>", unsafe_allow_html=True)
    st.markdown("<div style='color: var(--text-muted); font-size: 14px; font-weight: bold; margin-bottom: 15px;'>Ask me anything about your journey:</div>", unsafe_allow_html=True)
    
    with st.form(key='railmate_floating_form'):
        user_query = st.text_input(
            "Hidden_AI_Label",
            label_visibility="collapsed",
            placeholder="e.g., Which side of train avoids sun?"
        )
        submit_btn = st.form_submit_button("Ask RailMate 🚀", use_container_width=True)

    if submit_btn and user_query:
        API_KEY = st.secrets["GEMINI_API"]
        
        with st.status("RailMate is thinking...", expanded=True) as status:
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
                    st.success(f"**RailMate:** {ai_text}")
                else:
                    status.update(label="API Error", state="error", expanded=False)
                    st.error(f"⚠️ RailMate API Error: {response.text}")
                    
            except Exception as e:
                status.update(label="Network Error", state="error", expanded=False)
                st.error("⚠️ Connection failed. Please check your internet.")

