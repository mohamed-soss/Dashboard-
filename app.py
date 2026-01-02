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

# Color palette based on provided codes
COLORS = {
    "primary": "#0166FF",  # RGB 1,102,255
    "primary_dark": "#03045E",  # RGB 3,4,94
    "secondary": "#0077B6",  # RGB 0,119,182
    "black": "#000000",  # RGB 0,0,0
    "light_gray": "#E6E7E8",  # RGB 230,231,232
    "white": "#FFFFFF",  # RGB 255,255,255
    "success": "#00C851",
    "warning": "#FFBB33",
    "danger": "#FF4444"
}

# Custom CSS for modern dashboard
def inject_custom_css():
    st.markdown(f"""
    <style>
    .stApp {{
        background-color: {COLORS['white']};
    }}
    
    /* Make all text black by default */
    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6,
    .stMetric, .stMetric label, .stMetric div,
    .stDataFrame, .stTabs label, .stSelectbox label,
    .element-container, .stText, .stAlert {{
        color: {COLORS['black']} !important;
    }}
    
    /* KPI Cards */
    .kpi-card {{
        background: {COLORS['white']};
        border-radius: 12px;
        padding: 20px;
        border: 1px solid {COLORS['light_gray']};
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        height: 100%;
    }}
    
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
    }}
    
    .kpi-title {{
        color: {COLORS['primary_dark']};
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .kpi-value {{
        color: {COLORS['primary']};
        font-size: 32px;
        font-weight: 700;
        margin: 8px 0;
    }}
    
    .kpi-change {{
        font-size: 12px;
        font-weight: 500;
        padding: 4px 8px;
        border-radius: 12px;
        display: inline-block;
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
    
    /* Section Headers */
    .section-header {{
        color: {COLORS['primary_dark']};
        font-size: 24px;
        font-weight: 700;
        margin: 20px 0 15px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid {COLORS['light_gray']};
    }}
    
    /* Performance Cards */
    .performance-card {{
        background: {COLORS['white']};
        border-radius: 12px;
        padding: 20px;
        border: 1px solid {COLORS['light_gray']};
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        margin-bottom: 20px;
    }}
    
    .performance-header {{
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }}
    
    .performance-icon {{
        background: {COLORS['primary']};
        color: {COLORS['white']};
        width: 40px;
        height: 40px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 12px;
        font-size: 18px;
    }}
    
    /* Agent Selection */
    .agent-select {{
        background: {COLORS['white']};
        border: 1px solid {COLORS['light_gray']};
        border-radius: 8px;
        padding: 8px 12px;
    }}
    
    /* Data Table Styling */
    .data-table {{
        border: 1px solid {COLORS['light_gray']};
        border-radius: 8px;
        overflow: hidden;
    }}
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: transparent;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: {COLORS['white']};
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        border: 1px solid {COLORS['light_gray']};
        border-bottom: none;
        color: {COLORS['black']} !important;
    }}
    
    .stTabs [aria-selected="true"] {{
        background: {COLORS['primary']} !important;
        color: {COLORS['white']} !important;
    }}
    
    /* Remove Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# Google Sheets API Connection - UPDATED FOR STREAMLIT CLOUD
@st.cache_resource(ttl=300)
def get_google_sheets_service():
    """Initialize Google Sheets API service using Streamlit secrets"""
    try:
        # Access secrets from Streamlit Cloud
        # The secrets should be in .streamlit/secrets.toml as:
        # [gcp_service_account]
        # type = "service_account"
        # project_id = "..."
        # private_key_id = "..."
        # private_key = "-----BEGIN PRIVATE KEY-----\n..."
        # client_email = "..."
        # client_id = "..."
        # auth_uri = "https://accounts.google.com/o/oauth2/auth"
        # token_uri = "https://oauth2.googleapis.com/token"
        # auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
        # client_x509_cert_url = "..."
        # universe_domain = "googleapis.com"
        
        if 'gcp_service_account' in st.secrets:
            # For structured secrets in Streamlit Cloud
            service_account_info = dict(st.secrets["gcp_service_account"])
        else:
            # Fallback: try to get all secrets individually
            # This handles the case where secrets are stored as separate variables
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
        
        # You can make the spreadsheet ID configurable via secrets too
        if 'spreadsheet_id' in st.secrets:
            spreadsheet_id = st.secrets["spreadsheet_id"]
        else:
            # Default spreadsheet ID - you can change this
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
        
        df = pd.DataFrame(values[1:], columns=values[0])
        
        # Clean and parse data
        if "Timestamp" in df.columns:
            for fmt in ["%m/%d/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%m/%d/%Y %H:%M"]:
                try:
                    df["Timestamp"] = pd.to_datetime(df["Timestamp"], format=fmt)
                    break
                except:
                    continue
            else:
                df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors='coerce')
        
        # Ensure required columns exist
        required_columns = ["Timestamp", "Agent Name", "Transfer to:", "Customer Name:", "Electric Bill:", "Credit Score:"]
        for col in required_columns:
            if col not in df.columns:
                df[col] = None
        
        return df
    
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
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

# Data processing functions
def calculate_kpis(df):
    if df.empty or len(df) == 0:
        return {}
    
    df = df[df["Timestamp"].notna()].copy()
    
    if len(df) == 0:
        return {}
    
    now = datetime.now()
    
    today_start, today_end = get_today_range()
    today_data = df[(df["Timestamp"] >= today_start) & (df["Timestamp"] < today_end)]
    
    yesterday_start, yesterday_end = get_yesterday_range()
    yesterday_data = df[(df["Timestamp"] >= yesterday_start) & (df["Timestamp"] < yesterday_end)]
    
    week_start, week_end = get_week_range(0)
    this_week_data = df[(df["Timestamp"] >= week_start) & (df["Timestamp"] < week_end)]
    
    last_week_start, last_week_end = get_week_range(1)
    last_week_data = df[(df["Timestamp"] >= last_week_start) & (df["Timestamp"] < last_week_end)]
    
    month_start, month_end = get_month_range(0)
    this_month_data = df[(df["Timestamp"] >= month_start) & (df["Timestamp"] < month_end)]
    
    last_month_start, last_month_end = get_month_range(1)
    last_month_data = df[(df["Timestamp"] >= last_month_start) & (df["Timestamp"] < last_month_end)]
    
    kpis = {
        "total_transfers": len(df),
        "most_transferred": df["Transfer to:"].mode().iloc[0] if not df["Transfer to:"].mode().empty else "N/A",
        "transfer_counts": df["Transfer to:"].value_counts() if "Transfer to:" in df.columns else pd.Series(),
        "top_achiever_today": today_data["Agent Name"].mode().iloc[0] if not today_data["Agent Name"].mode().empty else "N/A",
        "top_achiever_week": this_week_data["Agent Name"].mode().iloc[0] if not this_week_data["Agent Name"].mode().empty else "N/A",
        "top_achiever_month": this_month_data["Agent Name"].mode().iloc[0] if not this_month_data["Agent Name"].mode().empty else "N/A",
        "agent_today_counts": today_data["Agent Name"].value_counts() if "Agent Name" in today_data.columns else pd.Series(),
        "agent_week_counts": this_week_data["Agent Name"].value_counts() if "Agent Name" in this_week_data.columns else pd.Series(),
        "agent_month_counts": this_month_data["Agent Name"].value_counts() if "Agent Name" in this_month_data.columns else pd.Series(),
        "agent_all_counts": df["Agent Name"].value_counts() if "Agent Name" in df.columns else pd.Series(),
        "lowest_performer": df["Agent Name"].value_counts().idxmin() if len(df["Agent Name"].value_counts()) > 0 else "N/A",
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
        "today_data": today_data,
        "this_week_data": this_week_data,
        "this_month_data": this_month_data
    }
    
    return kpis

# UI Components with new styling
def display_header():
    col1, col2 = st.columns([1, 6])
    with col1:
        try:
            st.image("logo.png", width=80)
        except:
            st.markdown(f"""
            <div style="width: 80px; height: 80px; background: {COLORS['primary']}; 
                        border-radius: 12px; display: flex; align-items: center; 
                        justify-content: center; color: white; font-weight: bold;">
                ST
            </div>
            """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"<h1 style='color: {COLORS['primary_dark']}; margin-bottom: 0;'>Sales Transfer Dashboard</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color: {COLORS['black']}; opacity: 0.7; margin-top: 0;'>Real-time performance monitoring</p>", unsafe_allow_html=True)

def display_kpi_grid(kpis):
    """Display KPI cards in a grid"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Total Transfers</div>
            <div class="kpi-value">{kpis.get('total_transfers', 0):,}</div>
            <div style="color: {COLORS['black']}; opacity: 0.7; font-size: 12px;">All-time transfers</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        daily_change = kpis.get('daily_change_pct', 0)
        change_class = "positive" if daily_change >= 0 else "negative"
        change_symbol = "+" if daily_change >= 0 else ""
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">Today's Transfers</div>
            <div class="kpi-value">{kpis.get('today_transfers', 0):,}</div>
            <div class="kpi-change {change_class}">
                {change_symbol}{daily_change:.1f}% vs yesterday
            </div>
            <div style="color: {COLORS['black']}; opacity: 0.7; font-size: 12px; margin-top: 4px;">
                Yesterday: {kpis.get('yesterday_transfers', 0)}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        weekly_change = kpis.get('weekly_change_pct', 0)
        change_class = "positive" if weekly_change >= 0 else "negative"
        change_symbol = "+" if weekly_change >= 0 else ""
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">This Week</div>
            <div class="kpi-value">{kpis.get('this_week_transfers', 0):,}</div>
            <div class="kpi-change {change_class}">
                {change_symbol}{weekly_change:.1f}% vs last week
            </div>
            <div style="color: {COLORS['black']}; opacity: 0.7; font-size: 12px; margin-top: 4px;">
                Last week: {kpis.get('last_week_transfers', 0)}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        monthly_change = kpis.get('monthly_change_pct', 0)
        change_class = "positive" if monthly_change >= 0 else "negative"
        change_symbol = "+" if monthly_change >= 0 else ""
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">This Month</div>
            <div class="kpi-value">{kpis.get('this_month_transfers', 0):,}</div>
            <div class="kpi-change {change_class}">
                {change_symbol}{monthly_change:.1f}% vs last month
            </div>
            <div style="color: {COLORS['black']}; opacity: 0.7; font-size: 12px; margin-top: 4px;">
                Last month: {kpis.get('last_month_transfers', 0)}
            </div>
        </div>
        """, unsafe_allow_html=True)

def display_performance_section(kpis):
    """Display top and lowest performers"""
    st.markdown('<div class="section-header">Performance Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="performance-card">
            <div class="performance-header">
                <div class="performance-icon">🏆</div>
                <div>
                    <h3 style='color: {COLORS['primary_dark']}; margin: 0;'>Top Performers</h3>
                    <p style='color: {COLORS['black']}; opacity: 0.7; margin: 0;'>Highest transfer counts</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs(["Today", "This Week", "This Month"])
        
        with tab1:
            agent_counts = kpis.get('agent_today_counts', pd.Series())
            if not agent_counts.empty:
                top_today = agent_counts.index[0]
                count_today = agent_counts.iloc[0]
                st.markdown(f"""
                <div style='margin: 20px 0;'>
                    <h4 style='color: {COLORS['primary_dark']}; margin-bottom: 5px;'>{top_today}</h4>
                    <p style='color: {COLORS['primary']}; font-size: 28px; font-weight: bold; margin: 0;'>{count_today}</p>
                    <p style='color: {COLORS['black']}; opacity: 0.7; margin: 0;'>transfers</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f'<p style="color: {COLORS["black"]}; opacity: 0.7;">No transfers today</p>', unsafe_allow_html=True)
        
        with tab2:
            agent_counts = kpis.get('agent_week_counts', pd.Series())
            if not agent_counts.empty:
                top_week = agent_counts.index[0]
                count_week = agent_counts.iloc[0]
                st.markdown(f"""
                <div style='margin: 20px 0;'>
                    <h4 style='color: {COLORS['primary_dark']}; margin-bottom: 5px;'>{top_week}</h4>
                    <p style='color: {COLORS['primary']}; font-size: 28px; font-weight: bold; margin: 0;'>{count_week}</p>
                    <p style='color: {COLORS['black']}; opacity: 0.7; margin: 0;'>transfers</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f'<p style="color: {COLORS["black"]}; opacity: 0.7;">No transfers this week</p>', unsafe_allow_html=True)
        
        with tab3:
            agent_counts = kpis.get('agent_month_counts', pd.Series())
            if not agent_counts.empty:
                top_month = agent_counts.index[0]
                count_month = agent_counts.iloc[0]
                st.markdown(f"""
                <div style='margin: 20px 0;'>
                    <h4 style='color: {COLORS['primary_dark']}; margin-bottom: 5px;'>{top_month}</h4>
                    <p style='color: {COLORS['primary']}; font-size: 28px; font-weight: bold; margin: 0;'>{count_month}</p>
                    <p style='color: {COLORS['black']}; opacity: 0.7; margin: 0;'>transfers</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f'<p style="color: {COLORS["black"]}; opacity: 0.7;">No transfers this month</p>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="performance-card">
            <div class="performance-header">
                <div class="performance-icon">📈</div>
                <div>
                    <h3 style='color: {COLORS['primary_dark']}; margin: 0;'>Agent Rankings</h3>
                    <p style='color: {COLORS['black']}; opacity: 0.7; margin: 0;'>All-time performance</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        agent_counts = kpis.get('agent_all_counts', pd.Series())
        if not agent_counts.empty:
            # Get lowest performer
            lowest_agent = kpis.get('lowest_performer', 'N/A')
            lowest_count = agent_counts.min() if len(agent_counts) > 0 else 0
            
            # Display all agents in ranking
            st.markdown("<div style='margin: 20px 0;'>", unsafe_allow_html=True)
            for i, (agent, count) in enumerate(agent_counts.head(10).items(), 1):
                if i == 1:
                    medal = "🥇"
                    color = COLORS['success']
                elif i == 2:
                    medal = "🥈"
                    color = "#6C757D"
                elif i == 3:
                    medal = "🥉"
                    color = "#CD7F32"
                else:
                    medal = f"{i}."
                    color = COLORS['black']
                
                is_lowest = agent == lowest_agent
                bg_color = f"rgba(255, 68, 68, 0.1)" if is_lowest else COLORS['white']
                
                st.markdown(f"""
                <div style='display: flex; justify-content: space-between; align-items: center; 
                            padding: 8px 12px; margin: 4px 0; border-radius: 6px;
                            background: {bg_color};'>
                    <div>
                        <span style='color: {color}; font-weight: bold;'>{medal}</span>
                        <span style='margin-left: 8px; color: {COLORS["black"]};'>{agent}</span>
                    </div>
                    <span style='color: {COLORS["primary"]}; font-weight: bold;'>{count}</span>
                </div>
                """, unsafe_allow_html=True)
            
            if is_lowest:
                st.markdown(f"""
                <div style='margin-top: 10px; padding: 8px; background: rgba(255, 68, 68, 0.1); 
                            border-radius: 6px; border-left: 3px solid {COLORS["danger"]};'>
                    <span style='color: {COLORS["danger"]}; font-weight: bold;'>Needs Improvement:</span>
                    <span style='color: {COLORS["black"]};'> {lowest_agent} ({lowest_count} transfers)</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown(f'<p style="color: {COLORS["black"]}; opacity: 0.7;">No agent data available</p>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def display_transfer_analysis(kpis):
    """Display transfer destination analysis"""
    st.markdown('<div class="section-header">Transfer Analysis</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="performance-card">
        <div class="performance-header">
            <div class="performance-icon">📊</div>
            <div>
                <h3 style='color: {COLORS['primary_dark']}; margin: 0;'>Transfer Destination Analysis</h3>
                <p style='color: {COLORS['black']}; opacity: 0.7; margin: 0;'>Where transfers are being directed</p>
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
                color_discrete_sequence=[COLORS['primary'], COLORS['secondary'], COLORS['primary_dark'], '#00C851', '#FFBB33']
            )
            fig.update_layout(
                height=400,
                title_font_color=COLORS['primary_dark'],
                title_font_size=18,
                font_color=COLORS['black']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            transfer_df = transfer_counts.reset_index()
            transfer_df.columns = ['Destination', 'Count']
            
            fig = px.bar(
                transfer_df,
                x='Destination',
                y='Count',
                title="Transfers by Destination",
                color='Count',
                color_continuous_scale=[[0, COLORS['light_gray']], [1, COLORS['primary']]]
            )
            fig.update_layout(
                height=400,
                xaxis_tickangle=-45,
                title_font_color=COLORS['primary_dark'],
                title_font_size=18,
                font_color=COLORS['black']
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(f"""
        <div style='margin-top: 20px; padding: 12px; background: rgba(1, 102, 255, 0.1); 
                    border-radius: 8px; border-left: 4px solid {COLORS['primary']};'>
            <span style='color: {COLORS['primary_dark']}; font-weight: bold;'>Most Transferred To:</span>
            <span style='color: {COLORS['primary']}; font-weight: bold; margin-left: 8px;'>
                {kpis.get('most_transferred', 'N/A')}
            </span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f'<p style="color: {COLORS["black"]}; opacity: 0.7;">No transfer data available</p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_agent_filter(kpis):
    """Display agent filter and detailed view"""
    st.markdown('<div class="section-header">Agent Details</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="performance-card">
        <div class="performance-header">
            <div class="performance-icon">👤</div>
            <div>
                <h3 style='color: {COLORS['primary_dark']}; margin: 0;'>Agent Performance Details</h3>
                <p style='color: {COLORS['black']}; opacity: 0.7; margin: 0;'>Detailed view by agent</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    agent_counts = kpis.get('agent_all_counts', pd.Series())
    if not agent_counts.empty:
        agent_names = sorted(agent_counts.index.tolist())
        selected_agent = st.selectbox("Select Agent:", ["All Agents"] + agent_names, key="agent_select")
        
        full_data = kpis.get('full_data', pd.DataFrame())
        if selected_agent == "All Agents":
            filtered_data = full_data
        else:
            filtered_data = full_data[full_data["Agent Name"] == selected_agent]
        
        # Display agent stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_transfers = len(filtered_data)
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Total Transfers</div>
                <div class="kpi-value">{total_transfers:,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            today_data = kpis.get('today_data', pd.DataFrame())
            if selected_agent != "All Agents":
                today_count = len(today_data[today_data["Agent Name"] == selected_agent])
            else:
                today_count = kpis.get('today_transfers', 0)
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Today</div>
                <div class="kpi-value">{today_count:,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            week_data = kpis.get('this_week_data', pd.DataFrame())
            if selected_agent != "All Agents":
                week_count = len(week_data[week_data["Agent Name"] == selected_agent])
            else:
                week_count = kpis.get('this_week_transfers', 0)
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">This Week</div>
                <div class="kpi-value">{week_count:,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            month_data = kpis.get('this_month_data', pd.DataFrame())
            if selected_agent != "All Agents":
                month_count = len(month_data[month_data["Agent Name"] == selected_agent])
            else:
                month_count = kpis.get('this_month_transfers', 0)
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">This Month</div>
                <div class="kpi-value">{month_count:,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Show recent transfers for selected agent
        if selected_agent != "All Agents" and not filtered_data.empty and len(filtered_data) > 0:
            st.markdown(f"""
            <div style='margin: 20px 0;'>
                <h4 style='color: {COLORS['primary_dark']};'>Recent Transfers by {selected_agent}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Check if columns exist before selecting them
            available_columns = filtered_data.columns.tolist()
            display_columns = ["Timestamp", "Customer Name:", "Transfer to:"]
            
            # Only include columns that actually exist in the data
            columns_to_display = [col for col in display_columns if col in available_columns]
            
            # Also check for optional columns
            optional_columns = ["Electric Bill:", "Credit Score:"]
            for col in optional_columns:
                if col in available_columns:
                    columns_to_display.append(col)
            
            if columns_to_display:
                recent_data = filtered_data[columns_to_display].sort_values("Timestamp", ascending=False).head(10)
                st.dataframe(
                    recent_data,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Timestamp": st.column_config.DatetimeColumn(
                            "Timestamp",
                            format="MM/DD/YYYY HH:mm"
                        )
                    }
                )
            else:
                st.markdown(f'<p style="color: {COLORS["black"]}; opacity: 0.7;">No display columns found in the data.</p>', unsafe_allow_html=True)
        elif selected_agent == "All Agents" and not full_data.empty:
            st.markdown(f"""
            <div style='margin: 20px 0;'>
                <h4 style='color: {COLORS['primary_dark']};'>Recent Transfers (All Agents)</h4>
            </div>
            """, unsafe_allow_html=True)
            
            available_columns = full_data.columns.tolist()
            display_columns = ["Timestamp", "Agent Name", "Customer Name:", "Transfer to:"]
            columns_to_display = [col for col in display_columns if col in available_columns]
            
            optional_columns = ["Electric Bill:", "Credit Score:"]
            for col in optional_columns:
                if col in available_columns:
                    columns_to_display.append(col)
            
            if columns_to_display:
                recent_data = full_data[columns_to_display].sort_values("Timestamp", ascending=False).head(10)
                st.dataframe(
                    recent_data,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Timestamp": st.column_config.DatetimeColumn(
                            "Timestamp",
                            format="MM/DD/YYYY HH:mm"
                        )
                    }
                )
    else:
        st.markdown(f'<p style="color: {COLORS["black"]}; opacity: 0.7;">No agent data available</p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_time_analysis(kpis):
    """Display time-based analysis"""
    st.markdown('<div class="section-header">Trend Analysis</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="performance-card">
        <div class="performance-header">
            <div class="performance-icon">📈</div>
            <div>
                <h3 style='color: {COLORS['primary_dark']}; margin: 0;'>Time Series Analysis</h3>
                <p style='color: {COLORS['black']}; opacity: 0.7; margin: 0;'>Transfer trends over time</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    full_data = kpis.get('full_data', pd.DataFrame())
    if not full_data.empty:
        df = full_data.copy()
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
        
        with tab1:
            if len(daily_counts) > 1:
                fig = px.line(
                    daily_counts,
                    x='Date',
                    y='Transfers',
                    title="Daily Transfers Trend",
                    markers=True,
                    line_shape='spline'
                )
                fig.update_traces(line_color=COLORS['primary'], marker_color=COLORS['secondary'])
                fig.update_layout(
                    height=400,
                    title_font_color=COLORS['primary_dark'],
                    title_font_size=18,
                    font_color=COLORS['black'],
                    plot_bgcolor=COLORS['white'],
                    paper_bgcolor=COLORS['white']
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown(f'<p style="color: {COLORS["black"]}; opacity: 0.7;">Insufficient data for daily analysis</p>', unsafe_allow_html=True)
        
        with tab2:
            if len(weekly_counts) > 1:
                fig = px.bar(
                    weekly_counts,
                    x='Week_Label',
                    y='Transfers',
                    title="Weekly Transfers",
                    color='Transfers',
                    color_continuous_scale=[[0, COLORS['light_gray']], [1, COLORS['primary']]]
                )
                fig.update_layout(
                    height=400,
                    xaxis_tickangle=-45,
                    title_font_color=COLORS['primary_dark'],
                    title_font_size=18,
                    font_color=COLORS['black'],
                    plot_bgcolor=COLORS['white'],
                    paper_bgcolor=COLORS['white']
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown(f'<p style="color: {COLORS["black"]}; opacity: 0.7;">Insufficient data for weekly analysis</p>', unsafe_allow_html=True)
        
        with tab3:
            if len(monthly_counts) > 1:
                fig = px.bar(
                    monthly_counts,
                    x='Month',
                    y='Transfers',
                    title="Monthly Transfers",
                    color='Transfers',
                    color_continuous_scale=[[0, COLORS['light_gray']], [1, COLORS['primary_dark']]]
                )
                fig.update_layout(
                    height=400,
                    xaxis_tickangle=-45,
                    title_font_color=COLORS['primary_dark'],
                    title_font_size=18,
                    font_color=COLORS['black'],
                    plot_bgcolor=COLORS['white'],
                    paper_bgcolor=COLORS['white']
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown(f'<p style="color: {COLORS["black"]}; opacity: 0.7;">Insufficient data for monthly analysis</p>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main application
def main():
    # Header
    display_header()
    
    # Get data
    df = get_sheet_data()
    
    if df.empty or len(df) == 0:
        st.markdown(f"""
        <div style='background: rgba(255, 193, 7, 0.1); border: 1px solid rgba(255, 193, 7, 0.3); 
                    border-radius: 8px; padding: 20px; margin: 20px 0;'>
            <h3 style='color: {COLORS['primary_dark']}; margin-top: 0;'>No data available or connection issue</h3>
            <p style='color: {COLORS['black']};'>
                <strong>Please ensure:</strong><br>
                1. Google Sheet is shared with the service account<br>
                2. Sheet contains data in "Form Responses 1"<br>
                3. Internet connection is stable<br><br>
                <strong>Check that service account credentials are properly set in Streamlit Cloud secrets.</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Wait before retrying
        time.sleep(45)
        st.rerun()
    
    # Calculate KPIs
    kpis = calculate_kpis(df)
    
    if not kpis:
        st.markdown(f'<p style="color: {COLORS["black"]}; opacity: 0.7;">Data loaded but no valid records found. Waiting for new data...</p>', unsafe_allow_html=True)
        time.sleep(45)
        st.rerun()
    
    # Display KPIs
    display_kpi_grid(kpis)
    
    # Performance section
    display_performance_section(kpis)
    
    # Transfer analysis
    display_transfer_analysis(kpis)
    
    # Agent filter
    display_agent_filter(kpis)
    
    # Time analysis
    display_time_analysis(kpis)
    
    # Status bar
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"""
    <div style='margin-top: 30px; padding: 10px; background: {COLORS['light_gray']}; 
                border-radius: 6px; text-align: center; color: {COLORS['primary_dark']}; 
                font-size: 12px;'>
        Last updated: {current_time} • Auto-refreshes every 45 seconds
    </div>
    """, unsafe_allow_html=True)
    
    # Auto-refresh
    time.sleep(45)
    st.rerun()

if __name__ == "__main__":
    main()