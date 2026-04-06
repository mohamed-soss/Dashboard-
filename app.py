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

# Premium color palette
COLORS = {
    "primary": "#4361EE",
    "primary_dark": "#1E3A8A",
    "secondary": "#3B82F6",
    "accent": "#06B6D4",
    "accent2": "#8B5CF6",
    "black": "#0F172A",
    "muted": "#64748B",
    "light_gray": "#F1F5F9",
    "border": "#E2E8F0",
    "white": "#FFFFFF",
    "success": "#10B981",
    "success_light": "#D1FAE5",
    "warning": "#F59E0B",
    "warning_light": "#FEF3C7",
    "danger": "#EF4444",
    "danger_light": "#FEE2E2",
    "surface": "#F8FAFC",
    "gradient1": "#667EEA",
    "gradient2": "#764BA2",
}

# Inject premium CSS
def inject_custom_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    :root {{
        --primary: {COLORS['primary']};
        --primary-dark: {COLORS['primary_dark']};
        --accent: {COLORS['accent']};
        --accent2: {COLORS['accent2']};
        --success: {COLORS['success']};
        --warning: {COLORS['warning']};
        --danger: {COLORS['danger']};
    }}

    * {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    .stApp {{
        background: {COLORS['surface']};
        background-image:
            radial-gradient(ellipse at 10% 0%, rgba(102, 126, 234, 0.06) 0%, transparent 50%),
            radial-gradient(ellipse at 90% 100%, rgba(6, 182, 212, 0.04) 0%, transparent 50%);
    }}

    /* ==================== ANIMATIONS ==================== */

    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(40px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    @keyframes fadeInDown {{
        from {{ opacity: 0; transform: translateY(-30px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    @keyframes fadeInLeft {{
        from {{ opacity: 0; transform: translateX(-40px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}

    @keyframes fadeInRight {{
        from {{ opacity: 0; transform: translateX(40px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}

    @keyframes scaleIn {{
        from {{ opacity: 0; transform: scale(0.85); }}
        to {{ opacity: 1; transform: scale(1); }}
    }}

    @keyframes slideInBounce {{
        0% {{ opacity: 0; transform: translateY(50px) scale(0.95); }}
        60% {{ opacity: 1; transform: translateY(-8px) scale(1.01); }}
        80% {{ transform: translateY(3px) scale(0.99); }}
        100% {{ opacity: 1; transform: translateY(0) scale(1); }}
    }}

    @keyframes shimmer {{
        0% {{ background-position: -200% 0; }}
        100% {{ background-position: 200% 0; }}
    }}

    @keyframes pulse {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50% {{ opacity: 0.6; transform: scale(0.95); }}
    }}

    @keyframes pulseRing {{
        0% {{ transform: scale(0.8); opacity: 1; }}
        100% {{ transform: scale(2.2); opacity: 0; }}
    }}

    @keyframes gradientMove {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    @keyframes floatUp {{
        0%, 100% {{ transform: translateY(0); }}
        50% {{ transform: translateY(-6px); }}
    }}

    @keyframes countUp {{
        from {{ opacity: 0; transform: translateY(20px); filter: blur(4px); }}
        to {{ opacity: 1; transform: translateY(0); filter: blur(0); }}
    }}

    @keyframes expandWidth {{
        from {{ width: 0%; }}
        to {{ width: var(--bar-width); }}
    }}

    @keyframes glowPulse {{
        0%, 100% {{ box-shadow: 0 0 15px rgba(67, 97, 238, 0.15); }}
        50% {{ box-shadow: 0 0 30px rgba(67, 97, 238, 0.3); }}
    }}

    @keyframes borderGlow {{
        0%, 100% {{ border-color: rgba(67, 97, 238, 0.2); }}
        50% {{ border-color: rgba(67, 97, 238, 0.5); }}
    }}

    @keyframes rotateIn {{
        from {{ opacity: 0; transform: rotate(-10deg) scale(0.8); }}
        to {{ opacity: 1; transform: rotate(0) scale(1); }}
    }}

    @keyframes typewriter {{
        from {{ width: 0; }}
        to {{ width: 100%; }}
    }}

    @keyframes ripple {{
        0% {{ transform: scale(0); opacity: 0.5; }}
        100% {{ transform: scale(4); opacity: 0; }}
    }}

    /* ==================== HEADER ==================== */

    .dashboard-header {{
        background: linear-gradient(135deg, {COLORS['primary_dark']} 0%, {COLORS['primary']} 40%, {COLORS['accent']} 100%);
        background-size: 300% 300%;
        animation: gradientMove 10s ease infinite, fadeInDown 0.7s cubic-bezier(0.22, 1, 0.36, 1) forwards;
        border-radius: 20px;
        padding: 36px 44px;
        margin-bottom: 32px;
        color: white;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(30, 58, 138, 0.25);
    }}

    .dashboard-header::before {{
        content: '';
        position: absolute;
        top: -80px; right: -60px;
        width: 500px; height: 500px;
        background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 60%);
        border-radius: 50%;
        animation: floatUp 6s ease-in-out infinite;
    }}

    .dashboard-header::after {{
        content: '';
        position: absolute;
        bottom: -100px; left: 15%;
        width: 350px; height: 350px;
        background: radial-gradient(circle, rgba(255,255,255,0.04) 0%, transparent 60%);
        border-radius: 50%;
        animation: floatUp 8s ease-in-out infinite reverse;
    }}

    .header-content {{
        position: relative; z-index: 2;
        display: flex; align-items: center; gap: 20px;
    }}

    .header-icon {{
        width: 60px; height: 60px;
        background: rgba(255,255,255,0.12);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 16px;
        display: flex; align-items: center; justify-content: center;
        font-size: 28px;
        animation: floatUp 4s ease-in-out infinite;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }}

    .header-title {{
        font-size: 30px; font-weight: 800; margin: 0;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 10px rgba(0,0,0,0.15);
    }}

    .header-subtitle {{
        font-size: 14px; font-weight: 400;
        opacity: 0.8; margin-top: 4px;
    }}

    .header-badges {{
        display: flex; gap: 10px; margin-top: 12px; flex-wrap: wrap;
    }}

    .header-badge {{
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 24px;
        padding: 5px 14px;
        font-size: 12px; font-weight: 500;
        transition: all 0.3s ease;
    }}

    .header-badge:hover {{
        background: rgba(255,255,255,0.2);
        transform: translateY(-1px);
    }}

    .live-dot-wrapper {{
        position: relative; width: 10px; height: 10px;
    }}

    .live-dot {{
        width: 8px; height: 8px;
        background: #34D399;
        border-radius: 50%;
        animation: pulse 2s ease-in-out infinite;
        position: absolute; top: 1px; left: 1px;
    }}

    .live-dot-ring {{
        width: 10px; height: 10px;
        border: 1.5px solid #34D399;
        border-radius: 50%;
        position: absolute; top: 0; left: 0;
        animation: pulseRing 2s ease-out infinite;
    }}

    /* ==================== KPI CARDS ==================== */

    .kpi-card {{
        background: {COLORS['white']};
        border-radius: 18px;
        padding: 26px;
        border: 1px solid {COLORS['border']};
        box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.02);
        transition: all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        height: 100%;
        position: relative;
        overflow: hidden;
    }}

    .kpi-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary), var(--accent));
        transform: scaleX(0);
        transition: transform 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        transform-origin: left;
        border-radius: 0 0 4px 4px;
    }}

    .kpi-card::after {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(135deg, rgba(67,97,238,0.02) 0%, rgba(6,182,212,0.02) 100%);
        opacity: 0;
        transition: opacity 0.5s ease;
        border-radius: 18px;
        pointer-events: none;
    }}

    .kpi-card:hover {{
        transform: translateY(-6px);
        box-shadow: 0 20px 40px rgba(67, 97, 238, 0.12), 0 8px 16px rgba(0,0,0,0.06);
        border-color: rgba(67, 97, 238, 0.3);
    }}

    .kpi-card:hover::before {{ transform: scaleX(1); }}
    .kpi-card:hover::after {{ opacity: 1; }}

    .kpi-1 {{ animation: slideInBounce 0.7s cubic-bezier(0.22, 1, 0.36, 1) 0.1s both; }}
    .kpi-2 {{ animation: slideInBounce 0.7s cubic-bezier(0.22, 1, 0.36, 1) 0.2s both; }}
    .kpi-3 {{ animation: slideInBounce 0.7s cubic-bezier(0.22, 1, 0.36, 1) 0.3s both; }}
    .kpi-4 {{ animation: slideInBounce 0.7s cubic-bezier(0.22, 1, 0.36, 1) 0.4s both; }}

    .kpi-icon-wrap {{
        width: 50px; height: 50px;
        border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        font-size: 22px;
        margin-bottom: 16px;
        position: relative;
        transition: transform 0.3s ease;
    }}

    .kpi-card:hover .kpi-icon-wrap {{
        transform: scale(1.1) rotate(-3deg);
    }}

    .kpi-icon-blue {{ background: linear-gradient(135deg, #DBEAFE, #BFDBFE); }}
    .kpi-icon-green {{ background: linear-gradient(135deg, #D1FAE5, #A7F3D0); }}
    .kpi-icon-orange {{ background: linear-gradient(135deg, #FEF3C7, #FDE68A); }}
    .kpi-icon-purple {{ background: linear-gradient(135deg, #EDE9FE, #DDD6FE); }}

    .kpi-label {{
        color: {COLORS['muted']};
        font-size: 12px; font-weight: 600;
        text-transform: uppercase; letter-spacing: 1px;
        margin-bottom: 8px;
    }}

    .kpi-number {{
        color: {COLORS['primary_dark']};
        font-size: 38px; font-weight: 800;
        margin: 4px 0 8px 0;
        letter-spacing: -1.5px;
        line-height: 1;
        animation: countUp 0.8s cubic-bezier(0.22, 1, 0.36, 1) 0.6s both;
    }}

    .kpi-change {{
        font-size: 12px; font-weight: 600;
        padding: 4px 10px;
        border-radius: 20px;
        display: inline-flex; align-items: center; gap: 4px;
    }}

    .kpi-change.positive {{
        background: {COLORS['success_light']};
        color: {COLORS['success']};
    }}

    .kpi-change.negative {{
        background: {COLORS['danger_light']};
        color: {COLORS['danger']};
    }}

    .kpi-meta {{
        color: #94A3B8;
        font-size: 12px;
        margin-top: 6px;
    }}

    /* ==================== SECTION HEADERS ==================== */

    .section-header {{
        color: {COLORS['primary_dark']};
        font-size: 22px; font-weight: 800;
        margin: 40px 0 20px 0;
        padding-bottom: 14px;
        border-bottom: 3px solid transparent;
        border-image: linear-gradient(90deg, {COLORS['primary']}, {COLORS['accent']}, transparent) 1;
        animation: fadeInLeft 0.6s cubic-bezier(0.22, 1, 0.36, 1) both;
        letter-spacing: -0.5px;
        display: flex; align-items: center; gap: 10px;
    }}

    .section-header-icon {{
        width: 36px; height: 36px;
        background: linear-gradient(135deg, var(--primary), var(--accent));
        border-radius: 10px;
        display: inline-flex; align-items: center; justify-content: center;
        font-size: 16px;
        box-shadow: 0 4px 12px rgba(67, 97, 238, 0.25);
    }}

    /* ==================== CARDS ==================== */

    .glass-card {{
        background: {COLORS['white']};
        border-radius: 18px;
        padding: 28px;
        border: 1px solid {COLORS['border']};
        box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.02);
        margin-bottom: 20px;
        transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        animation: fadeInUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) both;
        position: relative;
    }}

    .glass-card:hover {{
        box-shadow: 0 12px 32px rgba(0,0,0,0.08);
        border-color: rgba(67, 97, 238, 0.15);
    }}

    .card-header {{
        display: flex; align-items: center; gap: 14px;
        margin-bottom: 22px;
    }}

    .card-icon {{
        background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['accent']});
        color: white;
        width: 48px; height: 48px;
        border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px;
        box-shadow: 0 8px 20px rgba(67, 97, 238, 0.3);
        transition: all 0.3s ease;
    }}

    .glass-card:hover .card-icon {{
        transform: rotate(-5deg) scale(1.05);
        box-shadow: 0 12px 28px rgba(67, 97, 238, 0.4);
    }}

    .card-title {{
        color: {COLORS['primary_dark']};
        font-size: 18px; font-weight: 700;
        margin: 0;
    }}

    .card-subtitle {{
        color: {COLORS['muted']};
        font-size: 13px; margin: 2px 0 0 0;
    }}

    /* ==================== STATUS CARDS ==================== */

    .status-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin-top: 8px;
    }}

    .status-card {{
        border-radius: 14px;
        padding: 24px;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        position: relative;
        overflow: hidden;
    }}

    .status-card::before {{
        content: '';
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 60%);
        opacity: 0;
        transition: opacity 0.4s ease;
    }}

    .status-card:hover::before {{ opacity: 1; }}

    .status-card:hover {{
        transform: translateY(-4px) scale(1.02);
    }}

    .status-done-card {{
        background: linear-gradient(135deg, #ECFDF5, #D1FAE5);
        border: 1px solid #A7F3D0;
    }}

    .status-pending-card {{
        background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
        border: 1px solid #FDE68A;
    }}

    .status-rate-card {{
        background: linear-gradient(135deg, #EFF6FF, #DBEAFE);
        border: 1px solid #BFDBFE;
    }}

    .status-icon {{ font-size: 32px; margin-bottom: 8px; }}

    .status-value {{
        font-size: 36px; font-weight: 800;
        letter-spacing: -1px;
        animation: countUp 0.8s cubic-bezier(0.22, 1, 0.36, 1) 0.5s both;
    }}

    .status-done-card .status-value {{ color: #059669; }}
    .status-pending-card .status-value {{ color: #D97706; }}
    .status-rate-card .status-value {{ color: {COLORS['primary']}; }}

    .status-label {{
        font-size: 13px; font-weight: 600;
        margin-top: 4px;
    }}

    .status-done-card .status-label {{ color: #047857; }}
    .status-pending-card .status-label {{ color: #B45309; }}
    .status-rate-card .status-label {{ color: {COLORS['primary_dark']}; }}

    /* ==================== RANKING ==================== */

    .rank-item {{
        display: flex; justify-content: space-between; align-items: center;
        padding: 14px 18px;
        margin: 8px 0;
        border-radius: 14px;
        background: {COLORS['surface']};
        border: 1px solid transparent;
        transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        animation: fadeInRight 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
        cursor: default;
    }}

    .rank-item:hover {{
        background: {COLORS['white']};
        border-color: rgba(67, 97, 238, 0.25);
        transform: translateX(6px);
        box-shadow: 0 8px 24px rgba(67, 97, 238, 0.1);
    }}

    .rank-item-lowest {{
        background: linear-gradient(135deg, rgba(239,68,68,0.04), rgba(239,68,68,0.08));
        border: 1px solid rgba(239,68,68,0.15);
    }}

    .rank-item-lowest:hover {{
        border-color: rgba(239,68,68,0.3);
        box-shadow: 0 8px 24px rgba(239,68,68,0.08);
    }}

    .rank-bar-track {{
        background: {COLORS['light_gray']};
        border-radius: 6px;
        height: 6px;
        margin-top: 8px;
        overflow: hidden;
    }}

    .rank-bar-fill {{
        height: 100%;
        border-radius: 6px;
        background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['accent']});
        transition: width 1.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }}

    /* ==================== INSIGHT BOX ==================== */

    .insight-box {{
        background: linear-gradient(135deg, rgba(67, 97, 238, 0.04), rgba(6, 182, 212, 0.04));
        border: 1px solid rgba(67, 97, 238, 0.12);
        border-radius: 14px;
        padding: 18px 22px;
        margin-top: 18px;
        display: flex; align-items: center; gap: 14px;
        transition: all 0.4s ease;
        animation: fadeInUp 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
    }}

    .insight-box:hover {{
        border-color: rgba(67, 97, 238, 0.3);
        box-shadow: 0 8px 24px rgba(67, 97, 238, 0.08);
        transform: translateY(-2px);
    }}

    .insight-box-danger {{
        background: linear-gradient(135deg, rgba(239,68,68,0.03), rgba(239,68,68,0.06));
        border-color: rgba(239,68,68,0.12);
    }}

    .insight-box-danger:hover {{
        border-color: rgba(239,68,68,0.3);
        box-shadow: 0 8px 24px rgba(239,68,68,0.06);
    }}

    .insight-box-success {{
        background: linear-gradient(135deg, rgba(16,185,129,0.03), rgba(16,185,129,0.06));
        border-color: rgba(16,185,129,0.12);
    }}

    .insight-box-success:hover {{
        border-color: rgba(16,185,129,0.3);
        box-shadow: 0 8px 24px rgba(16,185,129,0.06);
    }}

    .insight-emoji {{ font-size: 26px; }}

    .insight-title {{
        font-weight: 700; font-size: 13px;
        color: {COLORS['primary_dark']};
    }}

    .insight-value {{
        font-weight: 800; font-size: 15px;
        color: {COLORS['primary']};
    }}

    .insight-text {{
        color: {COLORS['black']};
        font-size: 14px; font-weight: 500;
    }}

    /* ==================== TABS ==================== */

    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        background: {COLORS['light_gray']};
        border-radius: 14px;
        padding: 5px;
    }}

    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        border-radius: 11px;
        padding: 10px 24px;
        border: none;
        color: {COLORS['muted']} !important;
        font-weight: 600;
        font-size: 13px;
        transition: all 0.3s ease;
    }}

    .stTabs [aria-selected="true"] {{
        background: {COLORS['white']} !important;
        color: {COLORS['primary']} !important;
        font-weight: 700;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    }}

    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {{
        color: {COLORS['primary_dark']} !important;
        background: rgba(255,255,255,0.5);
    }}

    /* ==================== TOP PERFORMER HERO ==================== */

    .top-performer-hero {{
        background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
        border: 1px solid #FDE68A;
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        animation: fadeInUp 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
        transition: all 0.3s ease;
    }}

    .top-performer-hero:hover {{
        transform: translateY(-2px);
        box-shadow: 0 12px 32px rgba(245, 158, 11, 0.15);
    }}

    /* ==================== DATA TABLE ==================== */

    .stDataFrame {{
        border-radius: 14px !important;
        overflow: hidden !important;
        border: 1px solid {COLORS['border']} !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
    }}

    .stDataFrame table {{
        border-radius: 14px !important;
    }}

    /* ==================== SELECTBOX ==================== */

    .stSelectbox > div > div {{
        border-radius: 12px !important;
        border-color: {COLORS['border']} !important;
        transition: all 0.3s ease !important;
    }}

    .stSelectbox > div > div:focus-within {{
        border-color: {COLORS['primary']} !important;
        box-shadow: 0 0 0 4px rgba(67, 97, 238, 0.1) !important;
    }}

    /* ==================== SUCCESS BANNER ==================== */

    .success-banner {{
        background: linear-gradient(135deg, #ECFDF5, #D1FAE5);
        border: 1px solid #A7F3D0;
        border-radius: 14px;
        padding: 14px 22px;
        margin-bottom: 12px;
        display: flex; align-items: center; gap: 12px;
        animation: fadeInDown 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
        transition: all 0.3s ease;
    }}

    .success-banner:hover {{
        box-shadow: 0 8px 20px rgba(16, 185, 129, 0.12);
    }}

    /* ==================== STATUS BAR ==================== */

    .status-bar {{
        margin-top: 40px;
        padding: 16px 24px;
        background: {COLORS['white']};
        border-radius: 14px;
        border: 1px solid {COLORS['border']};
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 24px;
        animation: fadeInUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) 0.8s both;
        font-size: 13px;
        color: {COLORS['muted']};
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }}

    .status-bar-dot {{
        width: 8px; height: 8px;
        background: {COLORS['success']};
        border-radius: 50%;
        animation: pulse 2s ease-in-out infinite;
        display: inline-block;
        box-shadow: 0 0 8px rgba(16, 185, 129, 0.4);
    }}

    .status-divider {{
        width: 1px; height: 16px;
        background: {COLORS['border']};
    }}

    /* ==================== SIDEBAR ==================== */

    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORS['primary_dark']} 0%, #0F1D3A 100%);
        border-right: 1px solid rgba(255,255,255,0.05);
    }}

    section[data-testid="stSidebar"] * {{
        color: rgba(255,255,255,0.85) !important;
    }}

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: white !important;
    }}

    /* ==================== MISC ==================== */

    #MainMenu {{ visibility: hidden; }}
    footer {{ visibility: hidden; }}
    header {{ visibility: hidden; }}

    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{
        background: #CBD5E1;
        border-radius: 3px;
    }}
    ::-webkit-scrollbar-thumb:hover {{ background: {COLORS['primary']}; }}

    /* Remove default streamlit padding */
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}

    /* Chart animation wrapper */
    .chart-wrapper {{
        animation: scaleIn 0.6s cubic-bezier(0.22, 1, 0.36, 1) both;
    }}

    /* Most transferred highlight */
    .highlight-card {{
        background: linear-gradient(135deg, rgba(67, 97, 238, 0.06), rgba(6, 182, 212, 0.06));
        border: 1px solid rgba(67, 97, 238, 0.15);
        border-radius: 14px;
        padding: 20px 24px;
        margin-top: 18px;
        display: flex; align-items: center; gap: 16px;
        transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
        animation: slideInBounce 0.6s cubic-bezier(0.22, 1, 0.36, 1) 0.3s both;
    }}

    .highlight-card:hover {{
        transform: translateY(-3px) scale(1.01);
        box-shadow: 0 12px 32px rgba(67, 97, 238, 0.12);
        border-color: rgba(67, 97, 238, 0.3);
    }}

    .highlight-icon {{
        width: 52px; height: 52px;
        background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['accent']});
        border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        font-size: 24px;
        box-shadow: 0 8px 20px rgba(67, 97, 238, 0.3);
        flex-shrink: 0;
    }}

    .highlight-content {{ flex: 1; }}

    .highlight-label {{
        font-size: 12px; font-weight: 600;
        color: {COLORS['muted']};
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }}

    .highlight-name {{
        font-size: 22px; font-weight: 800;
        color: {COLORS['primary_dark']};
        margin: 4px 0 0 0;
        letter-spacing: -0.3px;
    }}

    .highlight-count {{
        font-size: 13px; font-weight: 500;
        color: {COLORS['muted']};
        margin-top: 2px;
    }}

    /* Error / warning */
    .error-card {{
        background: linear-gradient(135deg, #FFFBEB, #FEF3C7);
        border: 1px solid #FDE68A;
        border-left: 4px solid {COLORS['warning']};
        border-radius: 16px;
        padding: 28px;
        animation: fadeInUp 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
    }}

    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ==================== GOOGLE SHEETS ====================

@st.cache_resource(ttl=300)
def get_google_sheets_service():
    try:
        if 'gcp_service_account' in st.secrets:
            service_account_info = dict(st.secrets["gcp_service_account"])
        else:
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
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        return build('sheets', 'v4', credentials=credentials)
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {str(e)}")
        return None

@st.cache_data(ttl=30)
def get_sheet_data():
    try:
        service = get_google_sheets_service()
        if not service:
            return pd.DataFrame()

        spreadsheet_id = st.secrets.get("spreadsheet_id", "19SvmVDtkIUkuLaQzy6szSgUSixHZVBohbyOxf0itD8I")

        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range="Form Responses 1"
        ).execute()

        values = result.get('values', [])
        if not values:
            return pd.DataFrame()

        headers = values[0]
        processed_rows = []
        for row in values[1:]:
            while len(row) < len(headers):
                row.append(None)
            processed_rows.append(row[:len(headers)])

        df = pd.DataFrame(processed_rows, columns=headers)

        if "Timestamp" in df.columns:
            for fmt in ["%m/%d/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%m/%d/%Y %H:%M"]:
                try:
                    df["Timestamp"] = pd.to_datetime(df["Timestamp"], format=fmt)
                    break
                except:
                    continue
            else:
                df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors='coerce')

        if "Status" in df.columns:
            df["Status"] = df["Status"].astype(str).str.strip().str.lower()

        required = ["Timestamp", "Agent Name", "Transfer to:", "Customer Name:",
                     "Electric Bill:", "Credit Score:", "Status", "FeedBack", "H comments"]
        for col in required:
            if col not in df.columns:
                df[col] = None

        return df
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return pd.DataFrame()


# ==================== DATE HELPERS ====================

def get_today_range():
    now = datetime.now()
    start = datetime(now.year, now.month, now.day)
    return start, start + timedelta(days=1)

def get_yesterday_range():
    now = datetime.now() - timedelta(days=1)
    start = datetime(now.year, now.month, now.day)
    return start, start + timedelta(days=1)

def get_week_range(offset=0):
    now = datetime.now() - timedelta(weeks=offset)
    start = now - timedelta(days=now.isoweekday()-1)
    start = datetime(start.year, start.month, start.day)
    return start, start + timedelta(days=7)

def get_month_range(offset=0):
    now = datetime.now()
    month, year = now.month - offset, now.year
    while month <= 0:
        month += 12
        year -= 1
    start = datetime(year, month, 1)
    end = datetime(year+1, 1, 1) if month == 12 else datetime(year, month+1, 1)
    return start, end


# ==================== KPI CALCULATION ====================

def calculate_kpis(df):
    if df.empty:
        return {}

    df = df[df["Timestamp"].notna()].copy()
    if df.empty:
        return {}

    # Better status normalization
    if "Status" in df.columns:
        # Convert to string and strip whitespace
        df["Status"] = df["Status"].astype(str).str.strip().str.lower()
        # Handle case variations like "Done", "DONE", "done"
        done_df = df[df["Status"] == "done"].copy()
        done_count = len(done_df)
        total_rows = len(df)
        pending_count = total_rows - done_count
        completion_rate = (done_count / total_rows * 100) if total_rows > 0 else 0
    else:
        done_count = 0
        total_rows = 0
        pending_count = 0
        completion_rate = 0
        done_df = pd.DataFrame()

    today_s, today_e = get_today_range()
    yesterday_s, yesterday_e = get_yesterday_range()
    week_s, week_e = get_week_range(0)
    last_week_s, last_week_e = get_week_range(1)
    month_s, month_e = get_month_range(0)
    last_month_s, last_month_e = get_month_range(1)

    today_data = done_df[(done_df["Timestamp"] >= today_s) & (done_df["Timestamp"] < today_e)]
    yesterday_data = done_df[(done_df["Timestamp"] >= yesterday_s) & (done_df["Timestamp"] < yesterday_e)]
    this_week = done_df[(done_df["Timestamp"] >= week_s) & (done_df["Timestamp"] < week_e)]
    last_week = done_df[(done_df["Timestamp"] >= last_week_s) & (done_df["Timestamp"] < last_week_e)]
    this_month = done_df[(done_df["Timestamp"] >= month_s) & (done_df["Timestamp"] < month_e)]
    last_month = done_df[(done_df["Timestamp"] >= last_month_s) & (done_df["Timestamp"] < last_month_e)]

    def pct_change(current, previous):
        return ((current - previous) / previous * 100) if previous > 0 else 0

    transfer_counts = done_df["Transfer to:"].value_counts() if "Transfer to:" in done_df.columns else pd.Series()
    agent_counts = done_df["Agent Name"].value_counts() if "Agent Name" in done_df.columns else pd.Series()

    return {
        "total_rows": total_rows,
        "done_count": done_count,
        "pending_count": pending_count,
        "completion_rate": completion_rate,
        "total_transfers": done_count,
        "most_transferred": transfer_counts.index[0] if not transfer_counts.empty else "N/A",
        "most_transferred_count": int(transfer_counts.iloc[0]) if not transfer_counts.empty else 0,
        "transfer_counts": transfer_counts,
        "agent_today_counts": today_data["Agent Name"].value_counts() if "Agent Name" in today_data.columns else pd.Series(),
        "agent_week_counts": this_week["Agent Name"].value_counts() if "Agent Name" in this_week.columns else pd.Series(),
        "agent_month_counts": this_month["Agent Name"].value_counts() if "Agent Name" in this_month.columns else pd.Series(),
        "agent_all_counts": agent_counts,
        "lowest_performer": agent_counts.idxmin() if len(agent_counts) > 1 else "N/A",
        "today_transfers": len(today_data),
        "yesterday_transfers": len(yesterday_data),
        "daily_change_pct": pct_change(len(today_data), len(yesterday_data)),
        "this_week_transfers": len(this_week),
        "last_week_transfers": len(last_week),
        "weekly_change_pct": pct_change(len(this_week), len(last_week)),
        "this_month_transfers": len(this_month),
        "last_month_transfers": len(last_month),
        "monthly_change_pct": pct_change(len(this_month), len(last_month)),
        "full_data": df,
        "done_data": done_df,
        "today_data": today_data,
        "this_week_data": this_week,
        "this_month_data": this_month
    }


# ==================== UI COMPONENTS ====================

def display_header():
    st.markdown(f"""
    <div class="dashboard-header">
        <div class="header-content">
            <div class="header-icon">📊</div>
            <div>
                <div class="header-title">Sales Transfer Dashboard</div>
                <div class="header-subtitle">Real-time monitoring — only completed (done) transfers counted</div>
                <div class="header-badges">
                    <div class="header-badge">
                        <div class="live-dot-wrapper">
                            <div class="live-dot"></div>
                            <div class="live-dot-ring"></div>
                        </div>
                        <span>Live</span>
                    </div>
                    <div class="header-badge">🔄 Auto-refresh 45s</div>
                    <div class="header-badge">📅 {datetime.now().strftime("%b %d, %Y")}</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def display_kpi_grid(kpis):
    cols = st.columns(4)
    cards = [
        {
            "cls": "kpi-1", "icon_cls": "kpi-icon-blue", "icon": "✅",
            "label": "Completed Transfers", 
            "value": f"{kpis.get('total_transfers', 0):,}",
            "meta": f"{kpis.get('completion_rate', 0):.1f}% rate · {kpis.get('pending_count', 0)} pending"
        },
        {
            "cls": "kpi-2", "icon_cls": "kpi-icon-green", "icon": "📅",
            "label": "Today", 
            "value": f"{kpis.get('today_transfers', 0):,}",
            "change": kpis.get('daily_change_pct', 0),
            "meta": f"Yesterday: {kpis.get('yesterday_transfers', 0)}"
        },
        {
            "cls": "kpi-3", "icon_cls": "kpi-icon-orange", "icon": "📆",
            "label": "This Week", 
            "value": f"{kpis.get('this_week_transfers', 0):,}",
            "change": kpis.get('weekly_change_pct', 0),
            "meta": f"Last week: {kpis.get('last_week_transfers', 0)}"
        },
        {
            "cls": "kpi-4", "icon_cls": "kpi-icon-purple", "icon": "🗓️",
            "label": "This Month", 
            "value": f"{kpis.get('this_month_transfers', 0):,}",
            "change": kpis.get('monthly_change_pct', 0),
            "meta": f"Last month: {kpis.get('last_month_transfers', 0)}"
        }
    ]

    for col, card in zip(cols, cards):
        with col:
            change_html = ""
            if "change" in card:
                c = card["change"]
                cls = "positive" if c >= 0 else "negative"
                arrow = "↑" if c >= 0 else "↓"
                change_html = f'<div class="kpi-change {cls}">{arrow} {abs(c):.1f}% vs previous</div>'

            st.markdown(f"""
            <div class="kpi-card {card['cls']}">
                <div class="kpi-icon-wrap {card['icon_cls']}">{card['icon']}</div>
                <div class="kpi-label">{card['label']}</div>
                <div class="kpi-number">{card['value']}</div>
                {change_html}
                <div class="kpi-meta">{card['meta']}</div>
            </div>
            """, unsafe_allow_html=True)


def display_status_breakdown(kpis):
    st.markdown(f"""
    <div class="section-header">
        <div class="section-header-icon">📋</div>
        Status Overview
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="glass-card" style="animation-delay: 0.15s;">
        <div class="card-header">
            <div class="card-icon">📋</div>
            <div>
                <div class="card-title">Transfer Status Breakdown</div>
                <div class="card-subtitle">Only "done" status entries are counted as completed transfers</div>
            </div>
        </div>
        <div class="status-grid">
            <div class="status-card status-done-card">
                <div class="status-icon">✅</div>
                <div class="status-value">{kpis.get('done_count', 0)}</div>
                <div class="status-label">Completed</div>
            </div>
            <div class="status-card status-pending-card">
                <div class="status-icon">⏳</div>
                <div class="status-value">{kpis.get('pending_count', 0)}</div>
                <div class="status-label">Pending / Other</div>
            </div>
            <div class="status-card status-rate-card">
                <div class="status-icon">📊</div>
                <div class="status-value">{kpis.get('completion_rate', 0):.1f}%</div>
                <div class="status-label">Completion Rate</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def display_performance_section(kpis):
    st.markdown(f"""
    <div class="section-header">
        <div class="section-header-icon">🏆</div>
        Performance Analysis
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="glass-card" style="animation-delay: 0.2s;">
            <div class="card-header">
                <div class="card-icon">🏆</div>
                <div>
                    <div class="card-title">Top Performers</div>
                    <div class="card-subtitle">Highest completed transfer counts</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["Today", "This Week", "This Month"])
        for tab, key in [(tab1, 'agent_today_counts'), (tab2, 'agent_week_counts'), (tab3, 'agent_month_counts')]:
            with tab:
                counts = kpis.get(key, pd.Series())
                if not counts.empty:
                    agent = counts.index[0]
                    count = int(counts.iloc[0])
                    st.markdown(f"""
                    <div class="top-performer-hero">
                        <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 14px;">
                            <div style="width: 52px; height: 52px; background: linear-gradient(135deg, #F59E0B, #D97706);
                                        border-radius: 14px; display: flex; align-items: center; justify-content: center;
                                        font-size: 26px; box-shadow: 0 6px 16px rgba(245,158,11,0.3);">🥇</div>
                            <div>
                                <div style="font-size: 20px; font-weight: 800; color: {COLORS['primary_dark']};">{agent}</div>
                                <div style="font-size: 12px; color: {COLORS['muted']}; font-weight: 500;">Top performer</div>
                            </div>
                        </div>
                        <div style="display: flex; align-items: baseline; gap: 6px;">
                            <span style="font-size: 44px; font-weight: 800; color: #D97706; letter-spacing: -2px; line-height: 1;">{count}</span>
                            <span style="font-size: 14px; color: {COLORS['muted']}; font-weight: 500;">completed transfers</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f'<div style="text-align: center; padding: 40px 0; color: {COLORS["muted"]};">No completed transfers yet</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="glass-card" style="animation-delay: 0.3s;">
            <div class="card-header">
                <div class="card-icon">📈</div>
                <div>
                    <div class="card-title">Agent Rankings</div>
                    <div class="card-subtitle">All-time completed transfers</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        agent_counts = kpis.get('agent_all_counts', pd.Series())
        if not agent_counts.empty:
            lowest = kpis.get('lowest_performer', 'N/A')
            max_count = agent_counts.max()

            for i, (agent, count) in enumerate(agent_counts.head(10).items(), 1):
                medals = {1: "🥇", 2: "🥈", 3: "🥉"}
                medal = medals.get(i, f'<span style="color: #94A3B8; font-weight: 700; width: 24px; text-align: center; display: inline-block;">{i}</span>')
                bar_w = (count / max_count * 100) if max_count > 0 else 0
                is_lowest = agent == lowest and len(agent_counts) > 1
                delay = 0.05 * i

                st.markdown(f"""
                <div class="rank-item {"rank-item-lowest" if is_lowest else ""}" style="animation-delay: {delay}s;">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="font-size: 18px;">{medal}</span>
                            <span style="font-weight: 700; color: {COLORS['black']}; font-size: 14px;">{agent}</span>
                        </div>
                        <div class="rank-bar-track">
                            <div class="rank-bar-fill" style="width: {bar_w}%;"></div>
                        </div>
                    </div>
                    <span style="color: {COLORS['primary']}; font-weight: 800; font-size: 20px; margin-left: 16px; min-width: 36px; text-align: right;">{int(count)}</span>
                </div>
                """, unsafe_allow_html=True)

            if len(agent_counts) > 1:
                lowest_count = int(agent_counts.min())
                st.markdown(f"""
                <div class="insight-box insight-box-danger" style="margin-top: 16px;">
                    <span class="insight-emoji">📉</span>
                    <div>
                        <div class="insight-title" style="color: {COLORS['danger']};">Needs Support</div>
                        <div class="insight-text">{lowest} ({lowest_count} transfers)</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="text-align: center; padding: 40px 0; color: {COLORS["muted"]};">No agent data</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


def display_transfer_analysis(kpis):
    st.markdown(f"""
    <div class="section-header">
        <div class="section-header-icon">📊</div>
        Transfer Analysis
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="glass-card" style="animation-delay: 0.2s;">
        <div class="card-header">
            <div class="card-icon">📊</div>
            <div>
                <div class="card-title">Transfer Destination Analysis</div>
                <div class="card-subtitle">Where completed transfers are being directed</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    transfer_counts = kpis.get('transfer_counts', pd.Series())
    if not transfer_counts.empty:
        col1, col2 = st.columns(2)

        chart_layout = dict(
            height=400,
            title_font_color=COLORS['primary_dark'],
            title_font_size=15,
            title_font_family='Plus Jakarta Sans',
            font_color=COLORS['black'],
            font_family='Plus Jakarta Sans',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=50, b=20, l=20, r=20)
        )

        with col1:
            st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
            fig = px.pie(
                values=transfer_counts.values,
                names=transfer_counts.index,
                title="Distribution",
                color_discrete_sequence=[COLORS['primary'], COLORS['accent'], COLORS['accent2'],
                                         COLORS['success'], COLORS['warning'], COLORS['primary_dark']]
            )
            fig.update_layout(**chart_layout)
            fig.update_traces(textposition='inside', textinfo='percent+label', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-wrapper" style="animation-delay: 0.1s;">', unsafe_allow_html=True)
            tf = transfer_counts.reset_index()
            tf.columns = ['Destination', 'Count']
            tf = tf.sort_values('Count', ascending=True)

            fig = px.bar(
                tf, y='Destination', x='Count',
                title="By Destination", orientation='h',
                color='Count',
                color_continuous_scale=[[0, '#E2E8F0'], [1, COLORS['primary']]]
            )
            fig.update_layout(**chart_layout, coloraxis_showscale=False)
            fig.update_traces(
                marker_line_width=0,
                hovertemplate='<b>%{y}</b><br>%{x} transfers<extra></extra>'
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Most Transferred display
        most_name = kpis.get('most_transferred', 'N/A')
        most_count = kpis.get('most_transferred_count', 0)

        st.markdown(f"""
        <div class="highlight-card">
            <div class="highlight-icon">🎯</div>
            <div class="highlight-content">
                <div class="highlight-label">Most Transferred To</div>
                <div class="highlight-name">{most_name}</div>
                <div class="highlight-count">{most_count} completed transfers directed here</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="text-align: center; padding: 40px 0; color: {COLORS["muted"]};">No completed transfer data</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def display_agent_filter(kpis):
    st.markdown(f"""
    <div class="section-header">
        <div class="section-header-icon">👤</div>
        Agent Details
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="glass-card" style="animation-delay: 0.2s;">
        <div class="card-header">
            <div class="card-icon">👤</div>
            <div>
                <div class="card-title">Agent Performance</div>
                <div class="card-subtitle">Detailed view by agent (completed transfers only)</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    agent_counts = kpis.get('agent_all_counts', pd.Series())
    if not agent_counts.empty:
        agent_names = sorted(agent_counts.index.tolist())
        selected = st.selectbox("Select Agent:", ["All Agents"] + agent_names, key="agent_sel")

        done_data = kpis.get('done_data', pd.DataFrame())
        filtered = done_data if selected == "All Agents" else done_data[done_data["Agent Name"] == selected]

        today_d = kpis.get('today_data', pd.DataFrame())
        week_d = kpis.get('this_week_data', pd.DataFrame())
        month_d = kpis.get('this_month_data', pd.DataFrame())

        if selected != "All Agents":
            t_count = len(today_d[today_d["Agent Name"] == selected])
            w_count = len(week_d[week_d["Agent Name"] == selected])
            m_count = len(month_d[month_d["Agent Name"] == selected])
        else:
            t_count = kpis.get('today_transfers', 0)
            w_count = kpis.get('this_week_transfers', 0)
            m_count = kpis.get('this_month_transfers', 0)

        mini_cards = [
            ("🎯", "Total Done", len(filtered), "kpi-icon-blue"),
            ("📅", "Today", t_count, "kpi-icon-green"),
            ("📆", "This Week", w_count, "kpi-icon-orange"),
            ("🗓️", "This Month", m_count, "kpi-icon-purple"),
        ]

        mcols = st.columns(4)
        for mcol, (icon, label, val, icls) in zip(mcols, mini_cards):
            with mcol:
                st.markdown(f"""
                <div class="kpi-card" style="padding: 18px; animation: slideInBounce 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;">
                    <div class="kpi-icon-wrap {icls}" style="width: 38px; height: 38px; font-size: 16px; margin-bottom: 10px; border-radius: 10px;">{icon}</div>
                    <div class="kpi-label" style="font-size: 10px;">{label}</div>
                    <div class="kpi-number" style="font-size: 28px;">{val:,}</div>
                </div>
                """, unsafe_allow_html=True)

        if not filtered.empty:
            st.markdown(f"""
            <div style="margin: 28px 0 12px 0;">
                <h4 style="color: {COLORS['primary_dark']}; margin: 0; font-size: 16px; font-weight: 700;">
                    Recent Completed Transfers
                    {f' — <span style="color: {COLORS["primary"]};">{selected}</span>' if selected != 'All Agents' else ''}
                </h4>
            </div>
            """, unsafe_allow_html=True)

            display_cols = [c for c in ["Timestamp", "Agent Name", "Customer Name:", "Transfer to:", "Status",
                                         "Electric Bill:", "Credit Score:"] if c in filtered.columns]

            if display_cols:
                recent = filtered[display_cols].sort_values("Timestamp", ascending=False).head(10)
                display_df = recent.copy()
                if "Status" in display_df.columns:
                    display_df["Status"] = display_df["Status"].apply(
                        lambda x: "✅ Done" if str(x).strip() == "done" else f"⏳ {x.title()}"
                    )

                st.dataframe(
                    display_df, use_container_width=True, hide_index=True,
                    column_config={
                        "Timestamp": st.column_config.DatetimeColumn("Timestamp", format="MM/DD/YYYY HH:mm"),
                        "Status": st.column_config.TextColumn("Status", width="small")
                    }
                )
    else:
        st.markdown(f'<div style="text-align: center; padding: 40px 0; color: {COLORS["muted"]};">No agent data</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def display_time_analysis(kpis):
    st.markdown(f"""
    <div class="section-header">
        <div class="section-header-icon">📈</div>
        Trend Analysis
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="glass-card" style="animation-delay: 0.2s;">
        <div class="card-header">
            <div class="card-icon">📈</div>
            <div>
                <div class="card-title">Time Series</div>
                <div class="card-subtitle">Completed transfer trends over time</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    done_data = kpis.get('done_data', pd.DataFrame())
    if not done_data.empty:
        df = done_data.copy()
        df['Date'] = df['Timestamp'].dt.date
        daily = df.groupby('Date').size().reset_index(name='Transfers')

        df['Week'] = df['Timestamp'].dt.isocalendar().week
        df['Year'] = df['Timestamp'].dt.year
        weekly = df.groupby(['Year', 'Week']).size().reset_index(name='Transfers')
        weekly['Label'] = weekly['Year'].astype(str) + '-W' + weekly['Week'].astype(str).str.zfill(2)

        df['Month'] = df['Timestamp'].dt.to_period('M')
        monthly = df.groupby('Month').size().reset_index(name='Transfers')
        monthly['Month'] = monthly['Month'].astype(str)

        layout = dict(
            height=400,
            title_font_color=COLORS['primary_dark'],
            title_font_size=15,
            title_font_family='Plus Jakarta Sans',
            font_color=COLORS['black'],
            font_family='Plus Jakarta Sans',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=50, b=40, l=40, r=20),
            xaxis=dict(gridcolor='#F1F5F9', zeroline=False),
            yaxis=dict(gridcolor='#F1F5F9', zeroline=False)
        )

        tab1, tab2, tab3 = st.tabs(["Daily", "Weekly", "Monthly"])

        with tab1:
            if len(daily) > 1:
                fig = px.area(daily, x='Date', y='Transfers', title="Daily Trend", markers=True)
                fig.update_traces(
                    line_color=COLORS['primary'], fill='tozeroy',
                    fillcolor='rgba(67,97,238,0.08)',
                    marker=dict(color=COLORS['accent'], size=7, line=dict(color='white', width=2))
                )
                fig.update_layout(**layout)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown(f'<div style="text-align: center; padding: 40px 0; color: {COLORS["muted"]};">Insufficient data</div>', unsafe_allow_html=True)

        with tab2:
            if len(weekly) > 1:
                fig = px.bar(weekly, x='Label', y='Transfers', title="Weekly Trend",
                             color='Transfers', color_continuous_scale=[[0, '#E2E8F0'], [1, COLORS['primary']]])
                fig.update_layout(**layout, xaxis_tickangle=-45, coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown(f'<div style="text-align: center; padding: 40px 0; color: {COLORS["muted"]};">Insufficient data</div>', unsafe_allow_html=True)

        with tab3:
            if len(monthly) > 1:
                fig = px.bar(monthly, x='Month', y='Transfers', title="Monthly Trend",
                             color='Transfers', color_continuous_scale=[[0, '#E2E8F0'], [1, COLORS['primary_dark']]])
                fig.update_layout(**layout, xaxis_tickangle=-45, coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown(f'<div style="text-align: center; padding: 40px 0; color: {COLORS["muted"]};">Insufficient data</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ==================== MAIN ====================

def main():
    display_header()

    with st.spinner("Loading data from Google Sheets..."):
        df = get_sheet_data()

    if df.empty:
        st.markdown(f"""
        <div class="error-card">
            <h3 style="color: {COLORS['primary_dark']}; margin-top: 0; font-size: 20px;">⚠️ No data available</h3>
            <p style="color: {COLORS['black']}; line-height: 1.8; margin: 0;">
                <strong>Please check:</strong><br>
                1. Google Sheet is shared with the service account<br>
                2. Sheet contains data in "Form Responses 1"<br>
                3. Service account credentials in Streamlit Cloud secrets<br>
                4. Internet connection is stable
            </p>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(45)
        st.rerun()

    if len(df) <= 1:
        st.warning("Data loaded but contains only headers.")
        time.sleep(45)
        st.rerun()

    kpis = calculate_kpis(df)
    if not kpis:
        st.markdown(f'<div style="text-align: center; padding: 40px; color: {COLORS["muted"]};">No valid records found...</div>', unsafe_allow_html=True)
        time.sleep(45)
        st.rerun()

    # Success banner
    st.markdown(f"""
    <div class="success-banner">
        <span style="font-size: 20px;">✅</span>
        <span style="color: #065F46; font-weight: 600; font-size: 14px;">
            Loaded <strong>{len(df)}</strong> records — <strong>{kpis.get('done_count', 0)} completed transfers</strong> counted
            · {kpis.get('pending_count', 0)} pending
        </span>
    </div>
    """, unsafe_allow_html=True)

    display_kpi_grid(kpis)
    display_status_breakdown(kpis)
    display_performance_section(kpis)
    display_transfer_analysis(kpis)
    display_agent_filter(kpis)
    display_time_analysis(kpis)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"""
    <div class="status-bar">
        <div style="display: flex; align-items: center; gap: 8px;">
            <div class="status-bar-dot"></div>
            <span style="font-weight: 600;">System Online</span>
        </div>
        <div class="status-divider"></div>
        <span>Last updated: {now}</span>
        <div class="status-divider"></div>
        <span>Next refresh in 45s</span>
    </div>
    """, unsafe_allow_html=True)

    time.sleep(45)
    st.rerun()


if __name__ == "__main__":
    main()
