import streamlit as st
import streamlit.components.v1 as components
import os

# Set layout and custom styling
st.set_page_config(layout="wide")
st.markdown("""
    <style>
        .title {
            font-size: 36px;
            font-weight: bold;
            color: #003366;
        }
        .subtitle {
            font-size: 18px;
            color: #555;
            margin-top: -10px;
        }
        .footer {
            text-align: center;
            font-size: 14px;
            color: #999;
            margin-top: 50px;
        }
    </style>
""", unsafe_allow_html=True)

# Display Title
st.markdown('<div class="title">Maryland’s Hospital Bed Maps</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Interactive Capacity Visualizations by Region & County</div>', unsafe_allow_html=True)

# Dropdown selector
map_files = {
    "🛏️ All Beds Map": "maryland_beds_interactive_map.html",
    "🏥 PAC Beds Map": "maryland_pac_beds_interactive_map.html"
}
selected = st.selectbox("Select a Map to View:", list(map_files.keys()))

# Show selected map
html_file = map_files[selected]
if not os.path.exists(html_file):
    st.error(f"❌ File not found: `{html_file}`")
else:
    with open(html_file, "r", encoding="utf-8") as f:
        html = f.read()
    components.html(html, height=650, scrolling=True)

# Footer
st.markdown('<div class="footer">Built by Tenacity Solutions • For Maryland HSCRC Leadership • Powered by Streamlit</div>', unsafe_allow_html=True)
