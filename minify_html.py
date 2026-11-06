import sys
import re

with open('station_ui.py', 'r', encoding='utf-8') as f:
    code = f.read()

# We need to replace `st.markdown(textwrap.dedent(html), unsafe_allow_html=True)` 
# or `st.markdown(html, unsafe_allow_html=True)`
# with `st.markdown(re.sub(r'\\n\\s+', ' ', html), unsafe_allow_html=True)`

if "st.markdown(textwrap.dedent(html)" in code:
    code = code.replace("st.markdown(textwrap.dedent(html), unsafe_allow_html=True)", 
                        "import re\n    minified_html = re.sub(r'\\n\\s*', ' ', html)\n    st.markdown(minified_html, unsafe_allow_html=True)")
elif "st.markdown(html, unsafe_allow_html=True)" in code:
    code = code.replace("st.markdown(html, unsafe_allow_html=True)", 
                        "import re\n    minified_html = re.sub(r'\\n\\s*', ' ', html)\n    st.markdown(minified_html, unsafe_allow_html=True)")

with open('station_ui.py', 'w', encoding='utf-8') as f:
    f.write(code)
print("Applied aggressive HTML minification to prevent markdown code block rendering.")

