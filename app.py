import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Page configuration
st.set_page_config(
    page_title="Sales Transfer Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Color palette
COLORS = {
    "primary": "#0166FF",
    "primary_dark": "#03045E",
    "secondary": "#0077B6",
    "accent": "#00B4D8",
    "black": "#000000",
    "light_gray": "#E6E7E8",
    "white": "#FFFFFF",
    "success": "#00C851",
    "warning": "#FFBB33",
    "danger": "#FF4444",
    "surface": "#F8FAFF",
    "card_border": "#E3E8F0"
}

# Custom CSS with animations and transitions
def inject_custom_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    * {{
        font-family: 'Inter', sans-serif;
    }}

    .stApp {{
        background: linear-gradient(135deg, {COLORS['surface']} 0%, {COLORS['white']} 50%, #F0F4FF 100%);
    }}

    /* Page load animation */
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(30px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    @keyframes fadeInLeft {{
        from {{ opacity: 0; transform: translateX(-30px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}

    @keyframes fadeInRight {{
        from {{ opacity: 0; transform: translateX(30px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}

    @keyframes scaleIn {{
        from {{ opacity: 0; transform: scale(0.9); }}
        to {{ opacity: 1; transform: scale(1); }}
    }}

    @keyframes shimmer {{
        0% {{ background-position: -200% 0; }}
        100% {{ background-position: 200% 0; }}
    }}

    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
    }}

    @keyframes slideDown {{
        from {{ opacity: 0; transform: translateY(-20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    @keyframes countUp {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    @keyframes glowPulse {{
        0%, 100% {{ box-shadow: 0 4px 15px rgba(1, 102, 255, 0.1); }}
        50% {{ box-shadow: 0 4px 25px rgba(1, 102, 255, 0.25); }}
    }}

    @keyframes gradientShift {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* Make all text black by default */
    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
    .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
    .stMetric, .stMetric label, .stMetric div,
    .stDataFrame, .stTabs label, .stSelectbox label,
    .element-container, .stText, .stAlert {{
        color: {COLORS['black']} !important;
    }}

    /* Header area */
    .dashboard-header {{
        animation: slideDown 0.6s ease-out forwards;
        background: linear-gradient(135deg, {COLORS['primary_dark']} 0%, {COLORS['primary']} 60%, {COLORS['accent']} 100%);
        background-size: 200% 200%;
        animation: gradientShift 8s ease infinite, slideDown 0.6s ease-out forwards;
        border-radius: 16px;
        padding: 30px 40px;
        margin-bottom: 30px;
        color: white;
        position: relative;
        overflow: hidden;
    }}

    .dashboard-header::before {{
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        border-radius: 50%;
    }}

    .dashboard-header::after {{
        content: '';
        position: absolute;
        bottom: -30%;
        left: 10%;
        width: 250px;
        height: 250px;
        background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
        border-radius: 50%;
    }}

    .header-title {{
        font-size: 32px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}

    .header-subtitle {{
        font-size: 15px;
        font-weight: 400;
        opacity: 0.85;
        margin-top: 6px;
        letter-spacing: 0.3px;
    }}

    .header-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255,255,255,0.15);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 12px;
        font-weight: 500;
        margin-top: 12px;
    }}

    .live-dot {{
        width: 8px;
        height: 8px;
        background: #00C851;
        border-radius: 50%;
        animation: pulse 2s ease-in-out infinite;
    }}

    /* KPI Cards */
    .kpi-card {{
        background: {COLORS['white']};
        border-radius: 16px;
        padding: 24px;
        border: 1px solid {COLORS['card_border']};
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
        transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        height: 100%;
        position: relative;
        overflow: hidden;
    }}

    .kpi-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['accent']});
        transform: scaleX(0);
        transition: transform 0.4s ease;
        transform-origin: left;
    }}

    .kpi-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 32px rgba(1, 102, 255, 0.12);
        border-color: {COLORS['primary']};
    }}

    .kpi-card:hover::before {{
        transform: scaleX(1);
    }}

    .kpi-card-1 {{ animation: fadeInUp 0.5s ease-out 0.1s both; }}
    .kpi-card-2 {{ animation: fadeInUp 0.5s ease-out 0.2s both; }}
    .kpi-card-3 {{ animation: fadeInUp 0.5s ease-out 0.3s both; }}
    .kpi-card-4 {{ animation: fadeInUp 0.5s ease-out 0.4s both; }}

    .kpi-icon {{
        width: 44px;
        height: 44px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        margin-bottom: 14px;
    }}

    .kpi-icon-blue {{ background: rgba(1, 102, 255, 0.1); }}
    .kpi-icon-green {{ background: rgba(0, 200, 81, 0.1); }}
    .kpi-icon-orange {{ background: rgba(255, 187, 51, 0.1); }}
    .kpi-icon-purple {{ background: rgba(102, 51, 255, 0.1); }}

    .kpi-title {{
        color: #6B7280;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }}

    .kpi-value {{
        color: {COLORS['primary_dark']};
        font-size: 36px;
        font-weight: 800;
        margin: 6px 0;
        letter-spacing: -1px;
        animation: countUp 0.6s ease-out 0.5s both;
    }}

    .kpi-change {{
        font-size: 12px;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 20px;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        margin-top: 4px;
    }}

    .kpi-change.positive {{
        background: rgba(0, 200, 81, 0.1);
        color: #00C851 !important;
    }}

    .kpi-change.negative {{
        background: rgba(255, 68, 68, 0.1);
        color: #FF4444 !important;
    }}

    .kpi-subtitle {{
        color: #9CA3AF;
        font-size: 12px;
        margin-top: 6px;
    }}

    /* Section Headers */
    .section-header {{
        color: {COLORS['primary_dark']};
        font-size: 22px;
        font-weight: 700;
        margin: 36px 0 20px 0;
        padding-bottom: 12px;
        border-bottom: 2px solid transparent;
        border-image: linear-gradient(90deg, {COLORS['primary']}, transparent) 1;
        animation: fadeInLeft 0.5s ease-out both;
        letter-spacing: -0.3px;
    }}

    /* Performance Cards */
    .performance-card {{
        background: {COLORS['white']};
        border-radius: 16px;
        padding: 28px;
        border: 1px solid {COLORS['card_border']};
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
        margin-bottom: 20px;
        transition: all 0.3s ease;
        animation: fadeInUp 0.6s ease-out both;
    }}

    .performance-card:hover {{
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
    }}

    .performance-header {{
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }}

    .performance-icon {{
        background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['accent']});
        color: {COLORS['white']};
        width: 44px;
        height: 44px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 14px;
        font-size: 18px;
        box-shadow: 0 4px 12px rgba(1, 102, 255, 0.3);
    }}

    /* Status Badge */
    .status-done {{
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: rgba(0, 200, 81, 0.1);
        color: #00C851 !important;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
    }}

    .status-pending {{
        display: inline-flex;
        align-items: center;
        gap: 5px;
        background: rgba(255, 187, 51, 0.1);
        color: #E6A800 !important;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
    }}

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        background: {COLORS['surface']};
        border-radius: 12px;
        padding: 4px;
    }}

    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border-radius: 10px;
        padding: 10px 24px;
        border: none;
        color: #6B7280 !important;
        font-weight: 500;
        transition: all 0.3s ease;
    }}

    .stTabs [aria-selected="true"] {{
        background: {COLORS['white']} !important;
        color: {COLORS['primary']} !important;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }}

    .stTabs [data-baseweb="tab"]:hover {{
        color: {COLORS['primary']} !important;
    }}

    /* Agent ranking items */
    .rank-item {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 16px;
        margin: 6px 0;
        border-radius: 10px;
        background: {COLORS['surface']};
        border: 1px solid transparent;
        transition: all 0.3s ease;
        animation: fadeInRight 0.4s ease-out both;
    }}

    .rank-item:hover {{
        background: {COLORS['white']};
        border-color: {COLORS['primary']};
        transform: translateX(4px);
        box-shadow: 0 2px 8px rgba(1, 102, 255, 0.1);
    }}

    .rank-item-lowest {{
        background: rgba(255, 68, 68, 0.05);
        border: 1px solid rgba(255, 68, 68, 0.15);
    }}

    /* Insight Box */
    .insight-box {{
        background: linear-gradient(135deg, rgba(1, 102, 255, 0.05), rgba(0, 180, 216, 0.05));
        border: 1px solid rgba(1, 102, 255, 0.15);
        border-radius: 12px;
        padding: 16px 20px;
        margin-top: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
        transition: all 0.3s ease;
    }}

    .insight-box:hover {{
        border-color: {COLORS['primary']};
        box-shadow: 0 4px 12px rgba(1, 102, 255, 0.08);
    }}

    .insight-icon {{
        font-size: 24px;
    }}

    /* Data Table */
    .stDataFrame {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid {COLORS['card_border']} !important;
    }}

    /* Selectbox */
    .stSelectbox > div > div {{
        border-radius: 10px;
        border-color: {COLORS['card_border']};
        transition: all 0.3s ease;
    }}

    .stSelectbox > div > div:focus-within {{
        border-color: {COLORS['primary']};
        box-shadow: 0 0 0 3px rgba(1, 102, 255, 0.1);
    }}

    /* Success/Warning Messages */
    .stSuccess {{
        background: rgba(0, 200, 81, 0.08);
        border: 1px solid rgba(0, 200, 81, 0.2);
        border-radius: 12px;
        animation: fadeInUp 0.4s ease-out both;
    }}

    .stWarning {{
        background: rgba(255, 187, 51, 0.08);
        border: 1px solid rgba(255, 187, 51, 0.2);
        border-radius: 12px;
    }}

    /* Status bar */
    .status-bar {{
        margin-top: 36px;
        padding: 14px 20px;
        background: {COLORS['white']};
        border-radius: 12px;
        border: 1px solid {COLORS['card_border']};
        text-align: center;
        color: #6B7280;
        font-size: 13px;
        animation: fadeInUp 0.6s ease-out 0.8s both;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 20px;
    }}

    .status-bar-dot {{
        width: 6px;
        height: 6px;
        background: {COLORS['success']};
        border-radius: 50%;
        animation: pulse 2s ease-in-out infinite;
        display: inline-block;
    }}

    /* Chart container */
    .chart-container {{
        animation: scaleIn 0.5s ease-out both;
    }}

    /* Sidebar styling */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORS['primary_dark']} 0%, #0A1628 100%);
    }}

    section[data-testid="stSidebar"] .stMarkdown {{
        color: white !important;
    }}

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: white !important;
    }}

    /* Remove Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* Scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
    }}
    ::-webkit-scrollbar-track {{
        background: {COLORS['surface']};
    }}
    ::-webkit-scrollbar-thumb {{
        background: {COLORS['light_gray']};
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: {COLORS['primary']};
    }}
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# Google Sheets API Connection
@st.cache_resource(ttl=300)
def get_google_sheets_service():
    """Initialize Google Sheets API service using Streamlit secrets"""
    try:
        if 'gcp_service_account' in st.secrets:
            service_account_info = dict(st.secrets["gcp_service_account"])
        else:
            try:
                service_account_info = {
                    "type": st.secrets["type"],
                    "project_id": st.secrets["project_id"],
                    "private_key_id": st.secrets["private_key_id"],
                    "private_key": st.secrets["private_key"].replace('\\n', '\n'),
                    "client_email": st.secrets["client_email"],
                    "client_id": st.secrets["client_id"],
                    "auth_uri": st.secrets["auth_uri"],
                    "token_uri": st.secrets["token_uri"],
                    "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
                    "client_x509_cert_url": st.secrets["client_x509_cert_url"],
                    "universe_domain": st.secrets["universe_domain"]
                }
            except KeyError as e:
                st.error(f"Missing secret: {e}")
                st.info("Please make sure all required secrets are set in Streamlit Cloud.")
                return None

        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        service = build('sheets', 'v4', credentials=credentials)
        return service
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {str(e)}")
        return None

@st.cache_data(ttl=30)
def get_sheet_data():
    """Fetch data from Google Sheet"""
    try:
        service = get_google_sheets_service()
        if not service:
            return pd.DataFrame()

        if 'spreadsheet_id' in st.secrets:
            spreadsheet_id = st.secrets["spreadsheet_id"]
        else:
            spreadsheet_id = "19SvmVDtkIUkuLaQzy6szSgUSixHZVBohbyOxf0itD8I"

        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range="Form Responses 1"
        ).execute()

        values = result.get('values', [])

        if not values:
            st.warning("No data found in the Google Sheet")
            return pd.DataFrame()

        headers = values[0]
        processed_rows = []
        for row in values[1:]:
            while len(row) < len(headers):
                row.append(None)
            if len(row) > len(headers):
                row = row[:len(headers)]
            processed_rows.append(row)

        df = pd.DataFrame(processed_rows, columns=headers)

        # Parse Timestamp
        if "Timestamp" in df.columns:
            for fmt in ["%m/%d/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%m/%d/%Y %H:%M"]:
                try:
                    df["Timestamp"] = pd.to_datetime(df["Timestamp"], format=fmt)
                    break
                except:
                    continue
            else:
                df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors='coerce')

        # Normalize Status column
        if "Status" in df.columns:
            df["Status"] = df["Status"].astype(str).str.strip().str.lower()

        # Create missing columns
        required_columns = ["Timestamp", "Agent Name", "Transfer to:", "Customer Name:",
                            "Electric Bill:", "Credit Score:", "Status", "FeedBack", "H comments"]
        for col in required_columns:
            if col not in df.columns:
                df[col] = None

        return df

    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        import traceback
        st.error(f"Full traceback: {traceback.format_exc()}")
        return pd.DataFrame()


# Date helper functions
def get_today_range():
    now = datetime.now()
    today_start = datetime(now.year, now.month, now.day)
    today_end = today_start + timedelta(days=1)
    return today_start, today_end

def get_yesterday_range():
    now = datetime.now() - timedelta(days=1)
    yesterday_start = datetime(now.year, now.month, now.day)
    yesterday_end = yesterday_start + timedelta(days=1)
    return yesterday_start, yesterday_end

def get_week_range(week_offset=0):
    now = datetime.now() - timedelta(weeks=week_offset)
    weekday = now.isoweekday()
    week_start = now - timedelta(days=weekday-1)
    week_start = datetime(week_start.year, week_start.month, week_start.day)
    week_end = week_start + timedelta(days=7)
    return week_start, week_end

def get_month_range(month_offset=0):
    now = datetime.now()
    month = now.month - month_offset
    year = now.year
    while month <= 0:
        month += 12
        year -= 1
    month_start = datetime(year, month, 1)
    if month == 12:
        month_end = datetime(year+1, 1, 1)
    else:
        month_end = datetime(year, month+1, 1)
    return month_start, month_end


# Data processing — only count "done" status as transfers
def calculate_kpis(df):
    if df.empty or len(df) == 0:
        return {}

    df = df[df["Timestamp"].notna()].copy()
    if len(df) == 0:
        return {}

    # KEY CHANGE: only rows with Status == "done" count as transfers
    done_df = df[df["Status"] == "done"].copy()

    # Stats about non-done rows for transparency
    total_rows = len(df)
    done_count = len(done_df)
    pending_count = total_rows - done_count

    now = datetime.now()

    today_start, today_end = get_today_range()
    today_data = done_df[(done_df["Timestamp"] >= today_start) & (done_df["Timestamp"] < today_end)]

    yesterday_start, yesterday_end = get_yesterday_range()
    yesterday_data = done_df[(done_df["Timestamp"] >= yesterday_start) & (done_df["Timestamp"] < yesterday_end)]

    week_start, week_end = get_week_range(0)
    this_week_data = done_df[(done_df["Timestamp"] >= week_start) & (done_df["Timestamp"] < week_end)]

    last_week_start, last_week_end = get_week_range(1)
    last_week_data = done_df[(done_df["Timestamp"] >= last_week_start) & (done_df["Timestamp"] < last_week_end)]

    month_start, month_end = get_month_range(0)
    this_month_data = done_df[(done_df["Timestamp"] >= month_start) & (done_df["Timestamp"] < month_end)]

    last_month_start, last_month_end = get_month_range(1)
    last_month_data = done_df[(done_df["Timestamp"] >= last_month_start) & (done_df["Timestamp"] < last_month_end)]

    kpis = {
        "total_transfers": len(done_df),
        "total_rows": total_rows,
        "done_count": done_count,
        "pending_count": pending_count,
        "completion_rate": (done_count / total_rows * 100) if total_rows > 0 else 0,
        "most_transferred": done_df["Transfer to:"].mode().iloc[0] if not done_df["Transfer to:"].mode().empty else "N/A",
        "transfer_counts": done_df["Transfer to:"].value_counts() if "Transfer to:" in done_df.columns else pd.Series(),
        "top_achiever_today": today_data["Agent Name"].mode().iloc[0] if not today_data["Agent Name"].mode().empty else "N/A",
        "top_achiever_week": this_week_data["Agent Name"].mode().iloc[0] if not this_week_data["Agent Name"].mode().empty else "N/A",
        "top_achiever_month": this_month_data["Agent Name"].mode().iloc[0] if not this_month_data["Agent Name"].mode().empty else "N/A",
        "agent_today_counts": today_data["Agent Name"].value_counts() if "Agent Name" in today_data.columns else pd.Series(),
        "agent_week_counts": this_week_data["Agent Name"].value_counts() if "Agent Name" in this_week_data.columns else pd.Series(),
        "agent_month_counts": this_month_data["Agent Name"].value_counts() if "Agent Name" in this_month_data.columns else pd.Series(),
        "agent_all_counts": done_df["Agent Name"].value_counts() if "Agent Name" in done_df.columns else pd.Series(),
        "lowest_performer": done_df["Agent Name"].value_counts().idxmin() if len(done_df["Agent Name"].value_counts()) > 0 else "N/A",
        "today_transfers": len(today_data),
        "yesterday_transfers": len(yesterday_data),
        "daily_change_pct": ((len(today_data) - len(yesterday_data)) / len(yesterday_data) * 100) if len(yesterday_data) > 0 else 0,
        "this_week_transfers": len(this_week_data),
        "last_week_transfers": len(last_week_data),
        "weekly_change_pct": ((len(this_week_data) - len(last_week_data)) / len(last_week_data) * 100) if len(last_week_data) > 0 else 0,
        "this_month_transfers": len(this_month_data),
        "last_month_transfers": len(last_month_data),
        "monthly_change_pct": ((len(this_month_data) - len(last_month_data)) / len(last_month_data) * 100) if len(last_month_data) > 0 else 0,
        "full_data": df,
        "done_data": done_df,
        "today_data": today_data,
        "this_week_data": this_week_data,
        "this_month_data": this_month_data
    }

    return kpis


# UI Components
def display_header():
    st.markdown(f"""
    <div class="dashboard-header">
        <div style="display: flex; align-items: center; gap: 16px; position: relative; z-index: 1;">
            <div style="width: 52px; height: 52px; background: rgba(255,255,255,0.2);
                        backdrop-filter: blur(10px); border-radius: 14px;
                        display: flex; align-items: center; justify-content: center;
                        font-size: 24px; border: 1px solid rgba(255,255,255,0.25);">
                📊
            </div>
            <div>
                <div class="header-title">Sales Transfer Dashboard</div>
                <div class="header-subtitle">Real-time performance monitoring — only completed transfers counted</div>
                <div class="header-badge">
                    <div class="live-dot"></div>
                    <span>Live • Auto-refreshes every 45s</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def display_kpi_grid(kpis):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="kpi-card kpi-card-1">
            <div class="kpi-icon kpi-icon-blue">✅</div>
            <div class="kpi-title">Completed Transfers</div>
            <div class="kpi-value">{kpis.get('total_transfers', 0):,}</div>
            <div class="kpi-subtitle">
                {kpis.get('completion_rate', 0):.1f}% completion rate
                ({kpis.get('pending_count', 0)} pending)
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        daily_change = kpis.get('daily_change_pct', 0)
        change_class = "positive" if daily_change >= 0 else "negative"
        change_symbol = "↑" if daily_change >= 0 else "↓"
        st.markdown(f"""
        <div class="kpi-card kpi-card-2">
            <div class="kpi-icon kpi-icon-green">📅</div>
            <div class="kpi-title">Today's Transfers</div>
            <div class="kpi-value">{kpis.get('today_transfers', 0):,}</div>
            <div class="kpi-change {change_class}">
                {change_symbol} {abs(daily_change):.1f}% vs yesterday
            </div>
            <div class="kpi-subtitle">Yesterday: {kpis.get('yesterday_transfers', 0)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        weekly_change = kpis.get('weekly_change_pct', 0)
        change_class = "positive" if weekly_change >= 0 else "negative"
        change_symbol = "↑" if weekly_change >= 0 else "↓"
        st.markdown(f"""
        <div class="kpi-card kpi-card-3">
            <div class="kpi-icon kpi-icon-orange">📆</div>
            <div class="kpi-title">This Week</div>
            <div class="kpi-value">{kpis.get('this_week_transfers', 0):,}</div>
            <div class="kpi-change {change_class}">
                {change_symbol} {abs(weekly_change):.1f}% vs last week
            </div>
            <div class="kpi-subtitle">Last week: {kpis.get('last_week_transfers', 0)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        monthly_change = kpis.get('monthly_change_pct', 0)
        change_class = "positive" if monthly_change >= 0 else "negative"
        change_symbol = "↑" if monthly_change >= 0 else "↓"
        st.markdown(f"""
        <div class="kpi-card kpi-card-4">
            <div class="kpi-icon kpi-icon-purple">🗓️</div>
            <div class="kpi-title">This Month</div>
            <div class="kpi-value">{kpis.get('this_month_transfers', 0):,}</div>
            <div class="kpi-change {change_class}">
                {change_symbol} {abs(monthly_change):.1f}% vs last month
            </div>
            <div class="kpi-subtitle">Last month: {kpis.get('last_month_transfers', 0)}</div>
        </div>
        """, unsafe_allow_html=True)


def display_status_breakdown(kpis):
    """Show status distribution for transparency"""
    st.markdown('<div class="section-header">Status Overview</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="performance-card" style="animation-delay: 0.2s;">
        <div class="performance-header">
            <div class="performance-icon">📋</div>
            <div>
                <h3 style='color: {COLORS["primary_dark"]}; margin: 0;'>Transfer Status Breakdown</h3>
                <p style='color: #6B7280; margin: 0;'>Only "done" status entries count as completed transfers</p>
            </div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 10px;">
            <div style="background: rgba(0, 200, 81, 0.06); border: 1px solid rgba(0, 200, 81, 0.15);
                        border-radius: 12px; padding: 20px; text-align: center;">
                <div style="font-size: 28px; margin-bottom: 6px;">✅</div>
                <div style="font-size: 32px; font-weight: 800; color: #00C851;">{kpis.get('done_count', 0)}</div>
                <div style="font-size: 13px; color: #6B7280; font-weight: 500;">Completed</div>
            </div>
            <div style="background: rgba(255, 187, 51, 0.06); border: 1px solid rgba(255, 187, 51, 0.15);
                        border-radius: 12px; padding: 20px; text-align: center;">
                <div style="font-size: 28px; margin-bottom: 6px;">⏳</div>
                <div style="font-size: 32px; font-weight: 800; color: #E6A800;">{kpis.get('pending_count', 0)}</div>
                <div style="font-size: 13px; color: #6B7280; font-weight: 500;">Pending / Other</div>
            </div>
            <div style="background: rgba(1, 102, 255, 0.06); border: 1px solid rgba(1, 102, 255, 0.15);
                        border-radius: 12px; padding: 20px; text-align: center;">
                <div style="font-size: 28px; margin-bottom: 6px;">📊</div>
                <div style="font-size: 32px; font-weight: 800; color: {COLORS['primary']};">{kpis.get('completion_rate', 0):.1f}%</div>
                <div style="font-size: 13px; color: #6B7280; font-weight: 500;">Completion Rate</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def display_performance_section(kpis):
    st.markdown('<div class="section-header">Performance Analysis</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="performance-card" style="animation-delay: 0.3s;">
            <div class="performance-header">
                <div class="performance-icon">🏆</div>
                <div>
                    <h3 style='color: {COLORS["primary_dark"]}; margin: 0;'>Top Performers</h3>
                    <p style='color: #6B7280; margin: 0;'>Highest completed transfer counts</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["Today", "This Week", "This Month"])

        for tab, key, label in [
            (tab1, 'agent_today_counts', 'today'),
            (tab2, 'agent_week_counts', 'this week'),
            (tab3, 'agent_month_counts', 'this month')
        ]:
            with tab:
                agent_counts = kpis.get(key, pd.Series())
                if not agent_counts.empty:
                    top_agent = agent_counts.index[0]
                    top_count = agent_counts.iloc[0]
                    st.markdown(f"""
                    <div style='margin: 20px 0; animation: fadeInUp 0.4s ease-out both;'>
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                            <div style="width: 48px; height: 48px; background: linear-gradient(135deg, #FFD700, #FFA500);
                                        border-radius: 14px; display: flex; align-items: center; justify-content: center;
                                        font-size: 24px;">🥇</div>
                            <div>
                                <h4 style='color: {COLORS["primary_dark"]}; margin: 0; font-size: 18px;'>{top_agent}</h4>
                                <p style='color: #6B7280; margin: 0; font-size: 13px;'>Top performer {label}</p>
                            </div>
                        </div>
                        <div style="display: flex; align-items: baseline; gap: 6px;">
                            <span style='color: {COLORS["primary"]}; font-size: 40px; font-weight: 800; letter-spacing: -1px;'>{top_count}</span>
                            <span style='color: #9CA3AF; font-size: 14px;'>completed transfers</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f'<p style="color: #6B7280; padding: 30px 0; text-align: center;">No completed transfers {label}</p>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="performance-card" style="animation-delay: 0.4s;">
            <div class="performance-header">
                <div class="performance-icon">📈</div>
                <div>
                    <h3 style='color: {COLORS["primary_dark"]}; margin: 0;'>Agent Rankings</h3>
                    <p style='color: #6B7280; margin: 0;'>All-time completed transfers</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        agent_counts = kpis.get('agent_all_counts', pd.Series())
        if not agent_counts.empty:
            lowest_agent = kpis.get('lowest_performer', 'N/A')
            st.markdown("<div style='margin: 10px 0;'>", unsafe_allow_html=True)

            for i, (agent, count) in enumerate(agent_counts.head(10).items(), 1):
                if i == 1:
                    medal, color = "🥇", "#FFD700"
                elif i == 2:
                    medal, color = "🥈", "#C0C0C0"
                elif i == 3:
                    medal, color = "🥉", "#CD7F32"
                else:
                    medal, color = f"<span style='color: #9CA3AF; font-weight: 600; width: 24px; text-align: center; display: inline-block;'>{i}.</span>", "#6B7280"

                is_lowest = agent == lowest_agent and len(agent_counts) > 1
                delay = 0.1 + i * 0.05

                # Progress bar width
                max_count = agent_counts.max()
                bar_width = (count / max_count * 100) if max_count > 0 else 0

                st.markdown(f"""
                <div class="rank-item {"rank-item-lowest" if is_lowest else ""}" style="animation-delay: {delay}s;">
                    <div style="display: flex; align-items: center; gap: 10px; flex: 1;">
                        <span style="font-size: 18px;">{medal}</span>
                        <div style="flex: 1;">
                            <div style="font-weight: 600; color: {COLORS['black']}; font-size: 14px;">{agent}</div>
                            <div style="background: {COLORS['light_gray']}; border-radius: 4px; height: 4px; margin-top: 6px; overflow: hidden;">
                                <div style="background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['accent']});
                                            height: 100%; width: {bar_width}%; border-radius: 4px;
                                            transition: width 1s ease-out;"></div>
                            </div>
                        </div>
                    </div>
                    <span style='color: {COLORS["primary"]}; font-weight: 700; font-size: 18px;'>{count}</span>
                </div>
                """, unsafe_allow_html=True)

            if len(agent_counts) > 1:
                lowest_count = agent_counts.min()
                st.markdown(f"""
                <div class="insight-box" style="margin-top: 16px; border-color: rgba(255, 68, 68, 0.2);
                            background: linear-gradient(135deg, rgba(255, 68, 68, 0.03), rgba(255, 68, 68, 0.06));">
                    <span style="font-size: 20px;">📉</span>
                    <div>
                        <span style='color: {COLORS["danger"]}; font-weight: 600; font-size: 13px;'>Needs Support:</span>
                        <span style='color: {COLORS["black"]}; font-size: 13px;'> {lowest_agent} ({lowest_count} transfers)</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown(f'<p style="color: #6B7280; padding: 30px 0; text-align: center;">No agent data available</p>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


def display_transfer_analysis(kpis):
    st.markdown('<div class="section-header">Transfer Analysis</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="performance-card" style="animation-delay: 0.3s;">
        <div class="performance-header">
            <div class="performance-icon">📊</div>
            <div>
                <h3 style='color: {COLORS["primary_dark"]}; margin: 0;'>Transfer Destination Analysis</h3>
                <p style='color: #6B7280; margin: 0;'>Where completed transfers are directed</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    transfer_counts = kpis.get('transfer_counts', pd.Series())
    if not transfer_counts.empty:
        col1, col2 = st.columns(2)

        with col1:
            fig = px.pie(
                values=transfer_counts.values,
                names=transfer_counts.index,
                title="Transfer Distribution",
                color_discrete_sequence=[COLORS['primary'], COLORS['secondary'], COLORS['accent'], '#00C851', '#FFBB33', COLORS['primary_dark']]
            )
            fig.update_layout(
                height=420,
                title_font_color=COLORS['primary_dark'],
                title_font_size=16,
                title_font_family='Inter',
                font_color=COLORS['black'],
                font_family='Inter',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=50, b=20, l=20, r=20)
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            transfer_df = transfer_counts.reset_index()
            transfer_df.columns = ['Destination', 'Count']
            transfer_df = transfer_df.sort_values('Count', ascending=True)

            fig = px.bar(
                transfer_df,
                y='Destination',
                x='Count',
                title="Transfers by Destination",
                orientation='h',
                color='Count',
                color_continuous_scale=[[0, '#E3E8F0'], [1, COLORS['primary']]]
            )
            fig.update_layout(
                height=420,
                title_font_color=COLORS['primary_dark'],
                title_font_size=16,
                title_font_family='Inter',
                font_color=COLORS['black'],
                font_family='Inter',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(t=50, b=20, l=20, r=20),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"""
        <div class="insight-box">
            <span class="insight-icon">🎯</span>
            <div>
                <span style='color: {COLORS["primary_dark"]}; font-weight: 600;'>Most Transferred To:</span>
                <span style='color: {COLORS["primary"]}; font-weight: 700; margin-left: 8px;'>
                    {kpis.get('most_transferred', 'N/A')}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f'<p style="color: #6B7280; padding: 30px 0; text-align: center;">No completed transfer data available</p>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def display_agent_filter(kpis):
    st.markdown('<div class="section-header">Agent Details</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="performance-card" style="animation-delay: 0.3s;">
        <div class="performance-header">
            <div class="performance-icon">👤</div>
            <div>
                <h3 style='color: {COLORS["primary_dark"]}; margin: 0;'>Agent Performance Details</h3>
                <p style='color: #6B7280; margin: 0;'>Detailed view by agent (completed transfers only)</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    agent_counts = kpis.get('agent_all_counts', pd.Series())
    if not agent_counts.empty:
        agent_names = sorted(agent_counts.index.tolist())
        selected_agent = st.selectbox("Select Agent:", ["All Agents"] + agent_names, key="agent_select")

        done_data = kpis.get('done_data', pd.DataFrame())
        if selected_agent == "All Agents":
            filtered_data = done_data
        else:
            filtered_data = done_data[done_data["Agent Name"] == selected_agent]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total = len(filtered_data)
            st.markdown(f"""
            <div class="kpi-card" style="padding: 18px;">
                <div class="kpi-title" style="font-size: 11px;">Total Done</div>
                <div class="kpi-value" style="font-size: 28px;">{total:,}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            today_data = kpis.get('today_data', pd.DataFrame())
            if selected_agent != "All Agents":
                today_count = len(today_data[today_data["Agent Name"] == selected_agent])
            else:
                today_count = kpis.get('today_transfers', 0)
            st.markdown(f"""
            <div class="kpi-card" style="padding: 18px;">
                <div class="kpi-title" style="font-size: 11px;">Today</div>
                <div class="kpi-value" style="font-size: 28px;">{today_count:,}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            week_data = kpis.get('this_week_data', pd.DataFrame())
            if selected_agent != "All Agents":
                week_count = len(week_data[week_data["Agent Name"] == selected_agent])
            else:
                week_count = kpis.get('this_week_transfers', 0)
            st.markdown(f"""
            <div class="kpi-card" style="padding: 18px;">
                <div class="kpi-title" style="font-size: 11px;">This Week</div>
                <div class="kpi-value" style="font-size: 28px;">{week_count:,}</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            month_data = kpis.get('this_month_data', pd.DataFrame())
            if selected_agent != "All Agents":
                month_count = len(month_data[month_data["Agent Name"] == selected_agent])
            else:
                month_count = kpis.get('this_month_transfers', 0)
            st.markdown(f"""
            <div class="kpi-card" style="padding: 18px;">
                <div class="kpi-title" style="font-size: 11px;">This Month</div>
                <div class="kpi-value" style="font-size: 28px;">{month_count:,}</div>
            </div>
            """, unsafe_allow_html=True)

        # Recent transfers table
        if not filtered_data.empty:
            st.markdown(f"""
            <div style='margin: 24px 0 12px 0;'>
                <h4 style='color: {COLORS["primary_dark"]}; margin: 0; font-size: 16px;'>
                    Recent Completed Transfers
                    {f" — {selected_agent}" if selected_agent != "All Agents" else ""}
                </h4>
            </div>
            """, unsafe_allow_html=True)

            available_columns = filtered_data.columns.tolist()
            display_columns = ["Timestamp", "Agent Name", "Customer Name:", "Transfer to:", "Status"]
            columns_to_display = [col for col in display_columns if col in available_columns]

            optional_columns = ["Electric Bill:", "Credit Score:"]
            for col in optional_columns:
                if col in available_columns:
                    columns_to_display.append(col)

            if columns_to_display:
                recent_data = filtered_data[columns_to_display].sort_values("Timestamp", ascending=False).head(10)

                # Format the dataframe for display
                display_df = recent_data.copy()
                if "Status" in display_df.columns:
                    display_df["Status"] = display_df["Status"].apply(
                        lambda x: "✅ Done" if str(x).lower().strip() == "done" else f"⏳ {x}"
                    )

                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Timestamp": st.column_config.DatetimeColumn("Timestamp", format="MM/DD/YYYY HH:mm"),
                        "Status": st.column_config.TextColumn("Status", width="small")
                    }
                )
    else:
        st.markdown(f'<p style="color: #6B7280; padding: 30px 0; text-align: center;">No agent data available</p>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def display_time_analysis(kpis):
    st.markdown('<div class="section-header">Trend Analysis</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="performance-card" style="animation-delay: 0.3s;">
        <div class="performance-header">
            <div class="performance-icon">📈</div>
            <div>
                <h3 style='color: {COLORS["primary_dark"]}; margin: 0;'>Time Series Analysis</h3>
                <p style='color: #6B7280; margin: 0;'>Completed transfer trends over time</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    done_data = kpis.get('done_data', pd.DataFrame())
    if not done_data.empty:
        df = done_data.copy()
        df['Date'] = df['Timestamp'].dt.date
        daily_counts = df.groupby('Date').size().reset_index(name='Transfers')

        df['Week'] = df['Timestamp'].dt.isocalendar().week
        df['Year'] = df['Timestamp'].dt.year
        weekly_counts = df.groupby(['Year', 'Week']).size().reset_index(name='Transfers')
        weekly_counts['Week_Label'] = weekly_counts['Year'].astype(str) + '-W' + weekly_counts['Week'].astype(str).str.zfill(2)

        df['Month'] = df['Timestamp'].dt.to_period('M')
        monthly_counts = df.groupby('Month').size().reset_index(name='Transfers')
        monthly_counts['Month'] = monthly_counts['Month'].astype(str)

        tab1, tab2, tab3 = st.tabs(["Daily", "Weekly", "Monthly"])

        chart_layout = dict(
            height=420,
            title_font_color=COLORS['primary_dark'],
            title_font_size=16,
            title_font_family='Inter',
            font_color=COLORS['black'],
            font_family='Inter',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=50, b=40, l=40, r=20),
            xaxis=dict(gridcolor='#F0F0F0', zeroline=False),
            yaxis=dict(gridcolor='#F0F0F0', zeroline=False)
        )

        with tab1:
            if len(daily_counts) > 1:
                fig = px.area(
                    daily_counts, x='Date', y='Transfers',
                    title="Daily Completed Transfers",
                    markers=True
                )
                fig.update_traces(
                    line_color=COLORS['primary'],
                    fill='tozeroy',
                    fillcolor='rgba(1, 102, 255, 0.08)',
                    marker_color=COLORS['accent'],
                    marker_size=7
                )
                fig.update_layout(**chart_layout)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown('<p style="color: #6B7280; padding: 30px 0; text-align: center;">Insufficient data for daily analysis</p>', unsafe_allow_html=True)

        with tab2:
            if len(weekly_counts) > 1:
                fig = px.bar(
                    weekly_counts, x='Week_Label', y='Transfers',
                    title="Weekly Completed Transfers",
                    color='Transfers',
                    color_continuous_scale=[[0, '#E3E8F0'], [1, COLORS['primary']]]
                )
                fig.update_layout(**chart_layout, xaxis_tickangle=-45, coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown('<p style="color: #6B7280; padding: 30px 0; text-align: center;">Insufficient data for weekly analysis</p>', unsafe_allow_html=True)

        with tab3:
            if len(monthly_counts) > 1:
                fig = px.bar(
                    monthly_counts, x='Month', y='Transfers',
                    title="Monthly Completed Transfers",
                    color='Transfers',
                    color_continuous_scale=[[0, '#E3E8F0'], [1, COLORS['primary_dark']]]
                )
                fig.update_layout(**chart_layout, xaxis_tickangle=-45, coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown('<p style="color: #6B7280; padding: 30px 0; text-align: center;">Insufficient data for monthly analysis</p>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# Main application
def main():
    display_header()

    with st.spinner("Loading data from Google Sheets..."):
        df = get_sheet_data()

    if df.empty or len(df) == 0:
        st.markdown(f"""
        <div class="performance-card" style="border-left: 4px solid {COLORS['warning']}; animation: fadeInUp 0.5s ease-out both;">
            <h3 style='color: {COLORS["primary_dark"]}; margin-top: 0;'>⚠️ No data available or connection issue</h3>
            <p style='color: {COLORS["black"]}; line-height: 1.8;'>
                <strong>Please ensure:</strong><br>
                1. Google Sheet is shared with the service account<br>
                2. Sheet contains data in "Form Responses 1"<br>
                3. Internet connection is stable<br>
                4. Service account credentials are properly set in Streamlit Cloud secrets
            </p>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(45)
        st.rerun()

    if len(df) <= 1:
        st.warning("Data loaded but contains only headers or no valid records.")
        time.sleep(45)
        st.rerun()

    kpis = calculate_kpis(df)

    if not kpis:
        st.markdown(f'<p style="color: #6B7280; text-align: center; padding: 40px;">Data loaded but no valid records found. Waiting for new data...</p>', unsafe_allow_html=True)
        time.sleep(45)
        st.rerun()

    # Success banner
    st.markdown(f"""
    <div style="background: rgba(0, 200, 81, 0.06); border: 1px solid rgba(0, 200, 81, 0.15);
                border-radius: 12px; padding: 12px 20px; margin-bottom: 10px;
                display: flex; align-items: center; gap: 10px;
                animation: fadeInUp 0.4s ease-out both;">
        <span style="font-size: 18px;">✅</span>
        <span style="color: #1B5E20; font-weight: 500; font-size: 14px;">
            Loaded {len(df)} total records — <strong>{kpis.get('done_count', 0)} completed transfers</strong> counted
        </span>
    </div>
    """, unsafe_allow_html=True)

    display_kpi_grid(kpis)
    display_status_breakdown(kpis)
    display_performance_section(kpis)
    display_transfer_analysis(kpis)
    display_agent_filter(kpis)
    display_time_analysis(kpis)

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"""
    <div class="status-bar">
        <div style="display: flex; align-items: center; gap: 6px;">
            <div class="status-bar-dot"></div>
            <span>System Online</span>
        </div>
        <span style="color: #D1D5DB;">|</span>
        <span>Last updated: {current_time}</span>
        <span style="color: #D1D5DB;">|</span>
        <span>Auto-refresh in 45s</span>
    </div>
    """, unsafe_allow_html=True)

    time.sleep(45)
    st.rerun()


if __name__ == "__main__":
    main()
