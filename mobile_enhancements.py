import sys

with open('app.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Add a hint about swiping right below the coach header
old_html_assignment = '''                    html += "<div style=\'display: flex; flex-direction: column; gap: 10px; max-width: 320px; margin: 0 auto;\'>"'''

new_html_assignment = '''                    html += "<div style='text-align: center; color: var(--text-muted); font-size: 0.85rem; margin-bottom: 10px;'>👈 Swipe left or right to view all seats 👉</div>"
                    html += "<div style='overflow-x: auto; padding-bottom: 15px; -webkit-overflow-scrolling: touch;'>"
                    html += "<div style='display: flex; flex-direction: column; gap: 10px; min-width: 300px; max-width: 320px; margin: 0 auto;'>"'''

code = code.replace(old_html_assignment, new_html_assignment)

# Ensure the container closes the overflow div properly
# Wait, let's see how the container closes. It does: html += "</div>" then st.markdown(html)
# Let's check how it closes.
old_close = '''                        html += "</div>"
                        
                    html += "</div>"
                    st.markdown(html, unsafe_allow_html=True)'''

new_close = '''                        html += "</div>"
                        
                    html += "</div></div>" # Close min-width wrapper AND overflow-x wrapper
                    st.markdown(html, unsafe_allow_html=True)'''

if old_close in code:
    code = code.replace(old_close, new_close)

# Add CSS for larger touch targets and mobile spacing
css_insertion = '''    /* 3. Mobile Specific Adjustments */
    @media (max-width: 768px) {
        html { font-size: 14px; }
        .block-container { padding: 0.5rem !important; }
        
        /* Enforce touch target size */
        div[data-testid="stButton"] button { min-height: 44px !important; }
        div[data-testid="stSelectbox"] div[data-baseweb="select"] { min-height: 44px !important; }
        div[data-testid="stTextInput"] input { min-height: 44px !important; }
        div[data-testid="stDateInput"] input { min-height: 44px !important; }
        
        .hero-title { font-size: 2rem !important; }
        .pred-price { font-size: 3rem !important; }'''

if '    /* 3. Mobile Specific Adjustments */\n    @media (max-width: 768px) {\n        html { font-size: 14px; }\n        .block-container { padding: 0.5rem !important; }' in code:
    code = code.replace(
        '    /* 3. Mobile Specific Adjustments */\n    @media (max-width: 768px) {\n        html { font-size: 14px; }\n        .block-container { padding: 0.5rem !important; }',
        css_insertion
    )

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("Applied mobile enhancements!")

