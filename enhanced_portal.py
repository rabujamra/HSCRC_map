import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
from pathlib import Path

base_path = Path(__file__).parent
xlsx_path = base_path / "MIEMSS.xlsx"

# Set layout and custom styling
st.set_page_config(
    page_title="Maryland Hospital Capacity Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional custom CSS - FIXED color visibility
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        .main-header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #3182ce 100%);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(30, 60, 114, 0.3);
            text-align: center;
            color: white;
        }
        
        .title {
            font-family: 'Inter', sans-serif;
            font-size: 42px;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .subtitle {
            font-family: 'Inter', sans-serif;
            font-size: 18px;
            font-weight: 300;
            opacity: 0.95;
            margin-bottom: 0;
        }
        
        .control-panel {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.85));
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 25px;
            margin: 25px 0;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            color: #2d3748;
        }
        
        .metric-card {
            background: linear-gradient(135deg, rgba(66, 153, 225, 0.15), rgba(66, 153, 225, 0.05));
            border-radius: 12px;
            padding: 20px;
            margin: 15px 0;
            border-left: 4px solid #4299e1;
            color: #2d3748;
            font-family: 'Inter', sans-serif;
        }
        
        .stats-container {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
            gap: 15px;
        }
        
        .stat-box {
            background: rgba(66, 153, 225, 0.1);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            border: 1px solid rgba(66, 153, 225, 0.3);
            flex: 1;
        }
        
        .stat-number {
            font-size: 24px;
            font-weight: 700;
            color: #4299e1;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 14px;
            color: #4a5568;
            font-weight: 500;
        }
        
        .footer {
            text-align: center;
            font-size: 14px;
            color: #718096;
            margin-top: 50px;
            padding: 20px;
            background: rgba(0, 0, 0, 0.05);
            border-radius: 10px;
            font-family: 'Inter', sans-serif;
        }
        
        .map-container {
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
            margin: 20px 0;
        }
        
        .sidebar .sidebar-content {
            background: linear-gradient(180deg, #f7fafc 0%, #edf2f7 100%);
        }
        
        .stSelectbox > div > div {
            background-color: rgba(255, 255, 255, 0.9);
            border-radius: 8px;
            border: 1px solid #e2e8f0;
        }
        
        .view-mode-header {
            background: linear-gradient(90deg, #4299e1, #3182ce);
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin: 15px 0;
            font-weight: 600;
        }
        
        .data-summary {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: #2d3748;
        }
        
        .data-table {
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Function to load and calculate dynamic stats
@st.cache_data
def load_hospital_data():
    """Load hospital data and calculate statistics"""
    try:
        # Load Acute Hospitals data
        #acute_df = pd.read_excel("MIEMSS.xlsx", sheet_name="Acute Hospitals")
        acute_df = pd.read_excel(xlsx_path, sheet_name="Acute Hospitals")
        acute_df = acute_df.dropna(subset=["Hospital Name", "County"])

        # Load PAC Hospitals data  
        #pac_df = pd.read_excel("MIEMSS.xlsx", sheet_name="PAC Hospitals")
        pac_df = pd.read_excel(xlsx_path, sheet_name="PAC Hospitals")
        pac_df.columns = ["Facility Name", "County", "Region", "Sum Physical Beds"]
        pac_df = pac_df.dropna(subset=["Facility Name", "County"])
        pac_df["Sum Physical Beds"] = pd.to_numeric(pac_df["Sum Physical Beds"], errors="coerce").fillna(0)
        
        # Load full data for bed information (for acute hospitals)
        #full_df = pd.read_excel("MIEMSS.xlsx", sheet_name="MIEMSS - Daily Query Data Expor")
        full_df = pd.read_excel(xlsx_path, sheet_name="Acute Hospitals")
        full_df.columns = full_df.columns.str.strip()

        return acute_df, pac_df, full_df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None

def calculate_stats(hospital_type, view_mode, acute_df, pac_df, full_df):
    """Calculate dynamic statistics based on current selection"""
    
    if hospital_type == "Acute Care Hospitals":
        total_hospitals = len(acute_df)
        counties_covered = len(acute_df["County"].unique()) if view_mode == "By County" else "N/A"
        total_beds = int(acute_df["Num Bed"].sum())
        
    elif hospital_type == "Post-Acute Care (PAC)":
        total_hospitals = len(pac_df)
        counties_covered = len(pac_df["County"].unique()) if view_mode == "By County" else "N/A"
        total_beds = int(pac_df["Sum Physical Beds"].sum())
    
    return total_hospitals, counties_covered, total_beds

def prepare_data_table(hospital_type, view_mode, acute_df, pac_df, full_df):
    """Prepare data for table display"""
    
    if hospital_type == "Acute Care Hospitals":
        if view_mode == "By County":
            display_df = acute_df.copy()
            display_df["Beds"] = pd.to_numeric(acute_df["Num Bed"], errors="coerce").fillna(-1).astype(int)
            display_df = display_df[["Hospital Name", "County", "Region", "Beds"]].copy()
            display_df.columns = ["Hospital Name", "County", "Region", "Beds"]
        
        else:  # By Region
            display_df = acute_df.copy()
            display_df["Beds"] = pd.to_numeric(display_df["Num Bed"], errors="coerce").fillna(-1).astype(int)
            display_df = display_df[["Hospital Name", "Region", "Beds"]].copy()
            # Group cleaned acute_df by Region, summing beds and counting hospitals
            # grouped = acute_df.groupby("Region").agg(
            #     Hospital_Count=("Hospital Name", "count"),
            #     Total_Beds=("Num Bed", "sum")
            # ).reset_index()
            # display_df = grouped[["Region", "Hospital_Count", "Total_Beds"]].copy()
            # display_df.columns = ["Region", "Number of Hospitals", "Total Beds"]

            
    elif hospital_type == "Post-Acute Care (PAC)":
        if view_mode == "By County":
            display_df = pac_df.copy()
            display_df.columns = ["Hospital Name", "County", "Region", "Beds"]
        else:  # By Region
            grouped = pac_df.groupby("Region").agg(
                Hospital_Count=("Facility Name", "count"),
                Total_Beds=("Sum Physical Beds", "sum")
            ).reset_index()
            display_df = grouped[["Region", "Hospital_Count", "Total_Beds"]].copy()
            display_df.columns = ["Region", "Number of Facilities", "Total Beds"]

    return display_df

# Main header
st.markdown("""
    <div class="main-header">
        <div class="title">🏥 Maryland Hospital Capacity Platform</div>
        <div class="subtitle">Interactive Resource Visualization & Strategic Planning</div>
    </div>
""", unsafe_allow_html=True)

# Load data
acute_df, pac_df, full_df = load_hospital_data()

if acute_df is None:
    st.error("Unable to load hospital data. Please check that MIEMSS.xlsx is available.")
    st.stop()

# Sidebar controls
with st.sidebar:
    st.markdown("### 🎛️ Visualization Controls")
    
    # Hospital type selector - REMOVED combined option
    hospital_type = st.selectbox(
        "🏥 Hospital Type:",
        ["Acute Care Hospitals", "Post-Acute Care (PAC)"],
        index=0
    )
    
    st.markdown("---")
    
    # View mode selector
    view_mode = st.selectbox(
        "📊 Geographic View:",
        ["By Region", "By County"],
        index=0
    )
    
    st.markdown("---")
    
    # NEW: Data/Map Toggle
    display_mode = st.radio(
        "👁️ Display Mode:",
        ["Map View", "Data View"],
        index=0
    )
    
    st.markdown("---")
    
    # Current selection display
    st.markdown(f"""
        <div class="view-mode-header">
            📍 Current View:<br>
            <strong>{hospital_type}</strong><br>
            <strong>{view_mode}</strong><br>
            <strong>{display_mode}</strong>
        </div>
    """, unsafe_allow_html=True)
    
    # Show data summary in sidebar
    total_hospitals, counties_covered, total_beds = calculate_stats(
        hospital_type, view_mode, acute_df, pac_df, full_df
    )
    
    st.markdown(f"""
        <div class="data-summary">
            <strong>Quick Stats:</strong><br>
            🏥 Facilities: {total_hospitals}<br>
            📍 Counties: {counties_covered}<br>
            🛏️ Beds: {total_beds}
        </div>
    """, unsafe_allow_html=True)

# Calculate dynamic statistics
total_hospitals, counties_covered, total_beds = calculate_stats(
    hospital_type, view_mode, acute_df, pac_df, full_df
)

# Control panel with current configuration
st.markdown(f"""
    <div class="control-panel">
        <h3>📊 Current Configuration</h3>
        <div class="metric-card">
            <strong>Geographic View:</strong> {view_mode}<br>
            <strong>Data Layer:</strong> {hospital_type}<br>
            <strong>Display Mode:</strong> {display_mode}<br>
            <strong>Total Facilities:</strong> {total_hospitals}<br>
            <strong>Geographic Coverage:</strong> {counties_covered} counties<br>
            <strong>Total Beds:</strong> {total_beds}
        </div>
    </div>
""", unsafe_allow_html=True)

# Dynamic stats display
if view_mode == "By County":
    st.markdown(f"""
        <div class="stats-container">
            <div class="stat-box">
                <div class="stat-number">{total_hospitals}</div>
                <div class="stat-label">Total Facilities</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{counties_covered}</div>
                <div class="stat-label">Counties Covered</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">5</div>
                <div class="stat-label">EMS Regions</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{total_beds}</div>
                <div class="stat-label">Total Beds</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div class="stats-container">
            <div class="stat-box">
                <div class="stat-number">{total_hospitals}</div>
                <div class="stat-label">Total Facilities</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">5</div>
                <div class="stat-label">EMS Regions</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">23</div>
                <div class="stat-label">Total Counties</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{total_beds}</div>
                <div class="stat-label">Total Beds</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# MAIN CONTENT - Show Map or Data based on toggle
if display_mode == "Map View":
    # File mapping logic
    file_mapping = {
        ("Acute Care Hospitals", "By County"): "maryland_acute_hospitals_counties.html",
        ("Post-Acute Care (PAC)", "By County"): "maryland_pac_hospitals_counties.html",
        ("Acute Care Hospitals", "By Region"): "maryland_beds_interactive_map.html",
        ("Post-Acute Care (PAC)", "By Region"): "maryland_pac_beds_interactive_map.html"
    }
    html_file = file_mapping.get((hospital_type, view_mode))

    # Display map
    if not html_file or not os.path.exists(html_file):
        st.error(f"❌ Map file not found: `{html_file}`")
        st.info("🔍 Available map files:")
        for file in os.listdir('.'):
            if file.endswith('.html') and 'maryland' in file.lower():
                st.write(f"- {file}")
    else:
        with open(html_file, "r", encoding="utf-8") as f:
            html = f.read()
        
        st.markdown('<div class="map-container">', unsafe_allow_html=True)
        components.html(html, height=700, scrolling=True)
        st.markdown('</div>', unsafe_allow_html=True)

else:  # Data View
    # Show data table
    st.markdown(f"""
        <div class="control-panel">
            <h3>📋 {hospital_type} - {view_mode} Data</h3>
        </div>
    """, unsafe_allow_html=True)

    display_df = prepare_data_table(hospital_type, view_mode, acute_df, pac_df, full_df)

    # Display the data table with some styling
    st.markdown('<div class="data-table">', unsafe_allow_html=True)

    st.dataframe(
        display_df,
        use_container_width=True,
        height=600
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add download button
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Data as CSV",
        data=csv,
        file_name=f"maryland_{hospital_type.lower().replace(' ', '_')}_{view_mode.lower().replace(' ', '_')}.csv",
        mime="text/csv"
    )

# Additional insights based on current view
if display_mode == "Map View":
    if view_mode == "By County":
        st.markdown("""
            <div class="control-panel">
                <h3>💡 County-Level Insights</h3>
                <div class="metric-card">
                    <strong>Interactive Features:</strong><br>
                    • Hover over any county to see detailed facility information<br>
                    • Counties with hospitals are highlighted for easy identification<br>
                    • Clean regional color-coding for geographic context<br>
                    • Precise facility counts and names displayed on demand
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="control-panel">
                <h3>💡 Regional Analysis</h3>
                <div class="metric-card">
                    <strong>Strategic Overview:</strong><br>
                    • Five distinct EMS regions with comprehensive coverage<br>
                    • Regional capacity distribution and resource allocation<br>
                    • Interactive markers for detailed facility information<br>
                    • Strategic planning support for resource optimization
                </div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div class="control-panel">
            <h3>💡 Data View Features</h3>
            <div class="metric-card">
                <strong>Table Features:</strong><br>
                • Sortable columns by clicking headers<br>
                • Searchable data within the table<br>
                • Full dataset export available<br>
                • {len(display_df)} total records displayed<br>
                • Switch to Map View for geographic visualization
            </div>
        </div>
    """, unsafe_allow_html=True)

# Professional footer
st.markdown("""
    <div class="footer">
        Built by <strong>Tenacity Solutions</strong> • Advanced Healthcare Analytics Platform<br>
        For Maryland HSCRC Leadership Team • Interactive Hospital Capacity Visualization
    </div>
""", unsafe_allow_html=True)