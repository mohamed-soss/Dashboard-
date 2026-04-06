import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build

st.set_page_config(
    page_title="Sales Transfer Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# NEURAL NETWORK BACKGROUND - using components.html() so JS runs
# ============================================================
neural_html = """
<div style="position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:0;overflow:hidden;background:#0A0E27;">
<canvas id="c"></canvas>
</div>
<style>
body{margin:0;overflow:hidden;background:#0A0E27;}
</style>
<script>
(function(){
    var c=document.getElementById('c');
    var ctx=c.getContext('2d');
    var W,H;
    function resize(){
        W=c.width=window.innerWidth;
        H=c.height=window.innerHeight;
    }
    resize();
    window.addEventListener('resize',resize);
    var N=90;
    var MAX=160;
    var pts=[];
    for(var i=0;i<N;i++){
        pts.push({
            x:Math.random()*W,
            y:Math.random()*H,
            vx:(Math.random()-0.5)*0.5,
            vy:(Math.random()-0.5)*0.5,
            r:Math.random()*1.8+0.8
        });
    }
    function frame(){
        ctx.clearRect(0,0,W,H);
        var i,j,dx,dy,dist,a;
        for(i=0;i<N;i++){
            for(j=i+1;j<N;j++){
                dx=pts[i].x-pts[j].x;
                dy=pts[i].y-pts[j].y;
                dist=Math.sqrt(dx*dx+dy*dy);
                if(dist<MAX){
                    a=(1-dist/MAX)*0.3;
                    ctx.beginPath();
                    ctx.strokeStyle='rgba(129,140,248,'+a+')';
                    ctx.lineWidth=0.7;
                    ctx.moveTo(pts[i].x,pts[i].y);
                    ctx.lineTo(pts[j].x,pts[j].y);
                    ctx.stroke();
                }
            }
        }
        for(i=0;i<N;i++){
            var p=pts[i];
            ctx.beginPath();
            var g=ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,p.r*5);
            g.addColorStop(0,'rgba(129,140,248,0.25)');
            g.addColorStop(1,'rgba(129,140,248,0)');
            ctx.fillStyle=g;
            ctx.arc(p.x,p.y,p.r*5,0,6.28);
            ctx.fill();
            ctx.beginPath();
            ctx.fillStyle='rgba(165,180,252,0.8)';
            ctx.arc(p.x,p.y,p.r,0,6.28);
            ctx.fill();
            p.x+=p.vx;
            p.y+=p.vy;
            if(p.x<0||p.x>W)p.vx*=-1;
            if(p.y<0||p.y>H)p.vy*=-1;
        }
        requestAnimationFrame(frame);
    }
    frame();
})();
</script>
"""
components.html(neural_html, height=0, scrolling=False)

# ============================================================
# FULL CSS - dark glassmorphism over neural background
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

* { font-family: 'Inter', sans-serif; }

/* Make the Streamlit app background transparent so neural net shows through */
.stApp {
    background: transparent !important;
}
.stApp > div:first-child {
    background: transparent !important;
}
.main .block-container {
    background: transparent !important;
    position: relative;
    z-index: 10;
}

/* ==================== ANIMATIONS ==================== */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(30px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeDown {
    from { opacity: 0; transform: translateY(-25px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.88); }
    to   { opacity: 1; transform: scale(1); }
}
@keyframes slideLeft {
    from { opacity: 0; transform: translateX(-40px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes slideRight {
    from { opacity: 0; transform: translateX(40px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes countPop {
    0%   { opacity: 0; transform: scale(0.5); filter: blur(8px); }
    60%  { transform: scale(1.08); filter: blur(0); }
    100% { opacity: 1; transform: scale(1); filter: blur(0); }
}
@keyframes barGrow {
    from { width: 0%; }
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.8); }
}
@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}
@keyframes glow {
    0%, 100% { box-shadow: 0 0 20px rgba(79,70,229,0.15); }
    50% { box-shadow: 0 0 40px rgba(79,70,229,0.3); }
}
@keyframes borderShimmer {
    0%   { border-color: rgba(79,70,229,0.15); }
    50%  { border-color: rgba(79,70,229,0.4); }
    100% { border-color: rgba(79,70,229,0.15); }
}
@keyframes ripple {
    to { transform: scale(3); opacity: 0; }
}

/* ==================== HEADER ==================== */
.main-header {
    background: linear-gradient(135deg, #1E1B4B 0%, #312E81 25%, #4338CA 50%, #6366F1 75%, #0891B2 100%);
    background-size: 300% 300%;
    animation: gradientShift 10s ease infinite, fadeDown 0.7s cubic-bezier(0.16,1,0.3,1) forwards;
    border-radius: 20px;
    padding: 32px 40px;
    margin-bottom: 28px;
    color: white;
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 100px rgba(79,70,229,0.15);
}
.main-header::before {
    content: '';
    position: absolute;
    top: -60%; right: -8%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(129,140,248,0.12), transparent 60%);
    border-radius: 50%;
    animation: float 6s ease infinite;
}
.main-header::after {
    content: '';
    position: absolute;
    bottom: -50%; left: 15%;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(6,182,212,0.08), transparent 60%);
    border-radius: 50%;
    animation: float 8s ease infinite reverse;
}
.main-header h1 {
    color: white !important;
    font-size: 30px !important;
    font-weight: 900 !important;
    margin: 0 !important;
    letter-spacing: -1px;
    position: relative; z-index: 2;
}
.main-header p {
    color: rgba(255,255,255,0.7) !important;
    font-size: 14px !important;
    margin: 6px 0 0 0 !important;
    position: relative; z-index: 2;
}
.h-badges {
    display: flex; gap: 10px; margin-top: 14px;
    position: relative; z-index: 2; flex-wrap: wrap;
}
.h-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 12px; color: rgba(255,255,255,0.85);
    transition: all 0.3s ease;
}
.h-badge:hover {
    background: rgba(255,255,255,0.15);
    transform: translateY(-2px);
}
.live-dot {
    width: 8px; height: 8px;
    background: #34D399;
    border-radius: 50%;
    animation: pulse 2s ease infinite;
    box-shadow: 0 0 10px rgba(52,211,153,0.6);
}

/* ==================== KPI METRICS ==================== */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02)) !important;
    backdrop-filter: blur(24px) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 16px !important;
    padding: 22px 24px !important;
    transition: all 0.5s cubic-bezier(0.16,1,0.3,1) !important;
    animation: fadeUp 0.6s cubic-bezier(0.16,1,0.3,1) both !important;
    position: relative !important;
    overflow: hidden !important;
}
div[data-testid="stMetric"]:nth-child(1) { animation-delay: 0.1s !important; }
div[data-testid="stMetric"]:nth-child(2) { animation-delay: 0.2s !important; }
div[data-testid="stMetric"]:nth-child(3) { animation-delay: 0.3s !important; }
div[data-testid="stMetric"]:nth-child(4) { animation-delay: 0.4s !important; }

div[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #4F46E5, #06B6D4, #8B5CF6);
    transform: scaleX(0);
    transition: transform 0.5s cubic-bezier(0.16,1,0.3,1);
    transform-origin: left;
}
div[data-testid="stMetric"]:hover::before { transform: scaleX(1) !important; }

div[data-testid="stMetric"]:hover {
    transform: translateY(-6px) !important;
    box-shadow: 0 20px 50px rgba(79,70,229,0.2), 0 0 40px rgba(79,70,229,0.08) !important;
    border-color: rgba(129,140,248,0.35) !important;
    background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.04)) !important;
}

div[data-testid="stMetric"] label {
    color: #94A3B8 !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #F8FAFC !important;
    font-size: 36px !important;
    font-weight: 900 !important;
    letter-spacing: -1.5px !important;
    animation: countPop 0.7s cubic-bezier(0.16,1,0.3,1) 0.5s both !important;
}
div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {
    color: #94A3B8 !important;
    font-size: 12px !important;
}

/* ==================== SECTION HEADERS ==================== */
.sec-title {
    color: #F8FAFC;
    font-size: 20px; font-weight: 800;
    margin: 36px 0 18px 0;
    padding-bottom: 12px;
    border-bottom: 2px solid;
    border-image: linear-gradient(90deg, #4F46E5, #06B6D4, transparent) 1;
    animation: slideLeft 0.6s cubic-bezier(0.16,1,0.3,1) both;
    letter-spacing: -0.5px;
    display: flex; align-items: center; gap: 10px;
}
.sec-dot {
    width: 10px; height: 10px;
    background: #4F46E5;
    border-radius: 50%;
    box-shadow: 0 0 14px rgba(79,70,229,0.5);
    animation: pulse 3s ease infinite;
}

/* ==================== GLASS CARDS ==================== */
.g-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02)) !important;
    backdrop-filter: blur(24px) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 18px !important;
    padding: 28px !important;
    box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important;
    animation: fadeUp 0.6s cubic-bezier(0.16,1,0.3,1) both !important;
    transition: all 0.4s cubic-bezier(0.16,1,0.3,1) !important;
    position: relative !important;
    overflow: hidden !important;
}
.g-card::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(79,70,229,0.03), transparent, rgba(6,182,212,0.02));
    pointer-events: none;
    border-radius: 18px;
}
.g-card:hover {
    border-color: rgba(129,140,248,0.2) !important;
    box-shadow: 0 12px 40px rgba(0,0,0,0.4), 0 0 50px rgba(79,70,229,0.08) !important;
    transform: translateY(-2px) !important;
}
.card-ico {
    width: 44px; height: 44px;
    background: linear-gradient(135deg, #4F46E5, #06B6D4);
    border-radius: 12px;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 20px;
    box-shadow: 0 8px 20px rgba(79,70,229,0.3);
    transition: all 0.3s ease;
}
.g-card:hover .card-ico {
    transform: rotate(-5deg) scale(1.1);
    box-shadow: 0 12px 28px rgba(79,70,229,0.4);
}

/* ==================== STATUS CARDS ==================== */
.s-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px; margin-top: 16px;
}
.s-card {
    border-radius: 14px;
    padding: 24px;
    text-align: center;
    transition: all 0.4s cubic-bezier(0.16,1,0.3,1);
    position: relative; overflow: hidden;
}
.s-card:hover { transform: translateY(-4px) scale(1.02); }
.s-done {
    background: linear-gradient(135deg, rgba(16,185,129,0.12), rgba(16,185,129,0.04));
    border: 1px solid rgba(16,185,129,0.2);
}
.s-pend {
    background: linear-gradient(135deg, rgba(245,158,11,0.12), rgba(245,158,11,0.04));
    border: 1px solid rgba(245,158,11,0.2);
}
.s-rate {
    background: linear-gradient(135deg, rgba(79,70,229,0.12), rgba(79,70,229,0.04));
    border: 1px solid rgba(79,70,229,0.2);
}
.s-ico { font-size: 30px; margin-bottom: 8px; }
.s-val {
    font-size: 36px; font-weight: 900;
    letter-spacing: -1px;
    animation: countPop 0.7s cubic-bezier(0.16,1,0.3,1) 0.4s both;
}
.s-done .s-val { color: #34D399; }
.s-pend .s-val { color: #FBBF24; }
.s-rate .s-val { color: #818CF8; }
.s-lbl { font-size: 12px; font-weight: 600; margin-top: 4px; }
.s-done .s-lbl { color: #6EE7B7; }
.s-pend .s-lbl { color: #FCD34D; }
.s-rate .s-lbl { color: #C7D2FE; }

/* ==================== TOP PERFORMER ==================== */
.top-hero {
    background: linear-gradient(135deg, rgba(245,158,11,0.1), rgba(245,158,11,0.03));
    border: 1px solid rgba(245,158,11,0.15);
    border-radius: 14px;
    padding: 22px;
    margin: 14px 0;
    animation: scaleIn 0.5s cubic-bezier(0.16,1,0.3,1) both;
    transition: all 0.3s ease;
}
.top-hero:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 32px rgba(245,158,11,0.12);
}

/* ==================== RANKING ==================== */
.rank-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 16px; margin: 7px 0;
    border-radius: 12px;
    background: rgba(255,255,255,0.02);
    border: 1px solid transparent;
    transition: all 0.4s cubic-bezier(0.16,1,0.3,1);
    animation: slideRight 0.5s cubic-bezier(0.16,1,0.3,1) both;
}
.rank-row:hover {
    background: rgba(255,255,255,0.06) !important;
    border-color: rgba(129,140,248,0.2) !important;
    transform: translateX(6px) !important;
    box-shadow: 0 8px 24px rgba(79,70,229,0.1) !important;
}
.rank-low {
    background: rgba(239,68,68,0.04) !important;
    border-color: rgba(239,68,68,0.1) !important;
}
.rank-low:hover {
    border-color: rgba(239,68,68,0.25) !important;
    box-shadow: 0 8px 24px rgba(239,68,68,0.08) !important;
}
.bar-trk {
    background: rgba(255,255,255,0.06);
    border-radius: 4px; height: 5px;
    margin-top: 6px; overflow: hidden;
}
.bar-fl {
    height: 100%; border-radius: 4px;
    background: linear-gradient(90deg, #4F46E5, #06B6D4);
    animation: barGrow 1.2s cubic-bezier(0.16,1,0.3,1) both;
}

/* ==================== HIGHLIGHT ==================== */
.hl-box {
    margin-top: 18px; padding: 20px 24px;
    background: linear-gradient(135deg, rgba(79,70,229,0.1), rgba(6,182,212,0.06));
    border: 1px solid rgba(79,70,229,0.18);
    border-radius: 14px;
    display: flex; align-items: center; gap: 16px;
    animation: scaleIn 0.5s cubic-bezier(0.16,1,0.3,1) 0.3s both;
    transition: all 0.4s ease;
}
.hl-box:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 32px rgba(79,70,229,0.12);
    border-color: rgba(129,140,248,0.35);
}
.hl-ico {
    width: 50px; height: 50px;
    background: linear-gradient(135deg, #4F46E5, #06B6D4);
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    box-shadow: 0 8px 20px rgba(79,70,229,0.3);
    flex-shrink: 0;
}

/* ==================== INSIGHT ==================== */
.ins-box {
    margin-top: 14px; padding: 14px 18px;
    border-radius: 12px;
    display: flex; align-items: center; gap: 12px;
    animation: fadeUp 0.5s cubic-bezier(0.16,1,0.3,1) 0.5s both;
    transition: all 0.3s ease;
}
.ins-box:hover { transform: translateY(-2px); }
.ins-danger {
    background: rgba(239,68,68,0.06);
    border: 1px solid rgba(239,68,68,0.12);
}

/* ==================== TABS ==================== */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px !important;
    background: rgba(255,255,255,0.04) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 10px !important;
    padding: 8px 20px !important;
    border: none !important;
    color: #94A3B8 !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    transition: all 0.3s ease !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(79,70,229,0.2) !important;
    color: #A5B4FC !important;
    font-weight: 700 !important;
    box-shadow: 0 0 20px rgba(79,70,229,0.15) !important;
}
.stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
    color: #E2E8F0 !important;
    background: rgba(255,255,255,0.04) !important;
}

/* ==================== DATAFRAME ==================== */
.stDataFrame {
    border-radius: 14px !important;
    overflow: hidden !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
}
.stDataFrame table { color: #E2E8F0 !important; }
.stDataFrame th {
    background: rgba(79,70,229,0.12) !important;
    color: #A5B4FC !important;
    font-weight: 700 !important;
}
.stDataFrame td { color: #E2E8F0 !important; }

/* ==================== SELECTBOX ==================== */
.stSelectbox label { color: #94A3B8 !important; }
.stSelectbox > div > div {
    border-radius: 10px !important;
    border-color: rgba(255,255,255,0.1) !important;
    background: rgba(255,255,255,0.04) !important;
    color: #E2E8F0 !important;
}

/* ==================== BANNERS ==================== */
.ok-banner {
    background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(16,185,129,0.03));
    border: 1px solid rgba(16,185,129,0.15);
    border-radius: 14px;
    padding: 14px 22px;
    margin-bottom: 14px;
    display: flex; align-items: center; gap: 12px;
    animation: fadeDown 0.5s cubic-bezier(0.16,1,0.3,1) both;
    color: #6EE7B7;
    font-size: 14px; font-weight: 500;
}
.warn-card {
    background: linear-gradient(135deg, rgba(245,158,11,0.1), rgba(245,158,11,0.03));
    border: 1px solid rgba(245,158,11,0.15);
    border-left: 4px solid #F59E0B;
    border-radius: 16px;
    padding: 28px;
    animation: fadeUp 0.5s ease both;
    color: #E2E8F0;
}

/* ==================== FOOTER ==================== */
.foot-bar {
    margin-top: 36px; padding: 16px;
    background: linear-gradient(135deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    text-align: center;
    color: #94A3B8;
    font-size: 13px;
    animation: fadeUp 0.5s ease 0.8s both;
}

/* ==================== SIDEBAR ==================== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F0D2E 0%, #0A0E27 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}
section[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.75) !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: white !important;
}

/* ==================== MISC ==================== */
#MainMenu, footer, header { visibility: hidden !important; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #4F46E5; }

/* Plotly transparent */
.js-plotly-plot .plotly .bg { fill: transparent !important; }

/* Streamlit text colors on dark */
.stMarkdown, .stMarkdown p, .stMarkdown span {
    color: #E2E8F0 !important;
}
.stMarkdown strong {
    color: #F8FAFC !important;
}
.stAlert {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #E2E8F0 !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# GOOGLE SHEETS
# ============================================================
@st.cache_resource(ttl=300)
def get_service():
    try:
        if 'gcp_service_account' in st.secrets:
            info = dict(st.secrets["gcp_service_account"])
        else:
            info = {k: st.secrets[k] for k in [
                "type","project_id","private_key_id","private_key",
                "client_email","client_id","auth_uri","token_uri",
                "auth_provider_x509_cert_url","client_x509_cert_url","universe_domain"
            ]}
            info["private_key"] = info["private_key"].replace('\\n','\n')
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=['https://www.googleapis.com/auth/spreadsheets.readonly'])
        return build('sheets','v4',credentials=creds)
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

@st.cache_data(ttl=30)
def fetch_data():
    try:
        svc = get_service()
        if not svc: return pd.DataFrame()
        sid = st.secrets.get("spreadsheet_id","19SvmVDtkIUkuLaQzy6szSgUSixHZVBohbyOxf0itD8I")
        vals = svc.spreadsheets().values().get(spreadsheetId=sid, range="Form Responses 1").execute().get('values',[])
        if not vals: return pd.DataFrame()
        hdr = vals[0]
        rows = [r[:len(hdr)] + [None]*(len(hdr)-len(r)) for r in vals[1:]]
        df = pd.DataFrame(rows, columns=hdr)
        if "Timestamp" in df.columns:
            for fmt in ["%m/%d/%Y %H:%M:%S","%Y-%m-%d %H:%M:%S","%d/%m/%Y %H:%M:%S","%m/%d/%Y %H:%M"]:
                try: df["Timestamp"] = pd.to_datetime(df["Timestamp"],format=fmt); break
                except: pass
            else: df["Timestamp"] = pd.to_datetime(df["Timestamp"],errors='coerce')
        if "Status" in df.columns:
            df["Status"] = df["Status"].astype(str).str.strip().str.lower()
        for c in ["Timestamp","Agent Name","Transfer to:","Customer Name:","Electric Bill:","Credit Score:","Status","FeedBack","H comments"]:
            if c not in df.columns: df[c] = None
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

# ============================================================
# HELPERS
# ============================================================
def ranges():
    n = datetime.now()
    ts = datetime(n.year,n.month,n.day)
    y = n - timedelta(days=1)
    ys = datetime(y.year,y.month,y.day)
    ws = n - timedelta(days=n.isoweekday()-1)
    ws = datetime(ws.year,ws.month,ws.day)
    lws = ws - timedelta(weeks=1)
    ms = datetime(n.year,n.month,1)
    lms = datetime(n.year-1,12,1) if n.month==1 else datetime(n.year,n.month-1,1)
    lme = ms
    return {
        "today":(ts, ts+timedelta(days=1)),
        "yest":(ys, ys+timedelta(days=1)),
        "week":(ws, ws+timedelta(days=7)),
        "lweek":(lws, lws+timedelta(days=7)),
        "month":(ms, datetime(n.year+1,1,1) if n.month==12 else datetime(n.year,n.month+1,1)),
        "lmonth":(lms, lme),
    }

def calc(df):
    if df.empty: return {}
    df = df[df["Timestamp"].notna()].copy()
    if df.empty: return {}
    done = df[df["Status"]=="done"].copy()
    total = len(df); dn = len(done); pend = total - dn
    r = ranges()
    def f(d,k):
        s,e = r[k]; return d[(d["Timestamp"]>=s)&(d["Timestamp"]<e)]
    td=f(done,"today"); yd=f(done,"yest")
    tw=f(done,"week"); lw=f(done,"lweek")
    tm=f(done,"month"); lm=f(done,"lmonth")
    def pc(a,b): return ((a-b)/b*100) if b>0 else 0
    tc = done["Transfer to:"].value_counts() if "Transfer to:" in done.columns else pd.Series()
    ac = done["Agent Name"].value_counts() if "Agent Name" in done.columns else pd.Series()
    return {
        "total":total,"done":dn,"pend":pend,
        "rate":(dn/total*100) if total>0 else 0,
        "dest":tc.index[0] if not tc.empty else "N/A",
        "dest_n":int(tc.iloc[0]) if not tc.empty else 0,
        "tc":tc,"ac":ac,
        "ac_t":td["Agent Name"].value_counts() if "Agent Name" in td.columns else pd.Series(),
        "ac_w":tw["Agent Name"].value_counts() if "Agent Name" in tw.columns else pd.Series(),
        "ac_m":tm["Agent Name"].value_counts() if "Agent Name" in tm.columns else pd.Series(),
        "low":ac.idxmin() if len(ac)>1 else "N/A",
        "td":len(td),"yd":len(yd),"dp":pc(len(td),len(yd)),
        "tw":len(tw),"lw":len(lw),"wp":pc(len(tw),len(lw)),
        "tm":len(tm),"lm":len(lm),"mp":pc(len(tm),len(lm)),
        "full":df,"done_df":done,
        "tdf":td,"wdf":tw,"mdf":tm
    }

# ============================================================
# VIEWS
# ============================================================
def view_header():
    st.markdown(f"""
    <div class="main-header">
        <h1>⚡ Sales Transfer Dashboard</h1>
        <p>Real-time monitoring — only completed (done) transfers are counted</p>
        <div class="h-badges">
            <div class="h-badge"><div class="live-dot"></div> Live</div>
            <div class="h-badge">🔄 Auto-refresh 45s</div>
            <div class="h-badge">📅 {datetime.now().strftime("%b %d, %Y %H:%M")}</div>
        </div>
    </div>""", unsafe_allow_html=True)

def view_kpis(k):
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("✅ Completed Transfers", f"{k['done']:,}", f"{k['rate']:.1f}% rate · {k['pend']} pending")
    with c2: st.metric("📅 Today", f"{k['td']:,}", f"{k['dp']:+.1f}% vs yesterday ({k['yd']})")
    with c3: st.metric("📆 This Week", f"{k['tw']:,}", f"{k['wp']:+.1f}% vs last week ({k['lw']})")
    with c4: st.metric("🗓️ This Month", f"{k['tm']:,}", f"{k['mp']:+.1f}% vs last month ({k['lm']})")

def view_status(k):
    st.markdown('<div class="sec-title"><div class="sec-dot"></div> Status Overview</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="g-card">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;position:relative;z-index:2;">
            <div class="card-ico">📋</div>
            <div>
                <strong style="font-size:17px;color:#F8FAFC;">Transfer Status Breakdown</strong>
                <p style="margin:2px 0 0 0;font-size:12px;color:#94A3B8;">Only "done" entries count as completed transfers</p>
            </div>
        </div>
        <div class="s-grid" style="position:relative;z-index:2;">
            <div class="s-card s-done">
                <div class="s-ico">✅</div>
                <div class="s-val">{k['done']}</div>
                <div class="s-lbl">Completed</div>
            </div>
            <div class="s-card s-pend">
                <div class="s-ico">⏳</div>
                <div class="s-val">{k['pend']}</div>
                <div class="s-lbl">Pending / Other</div>
            </div>
            <div class="s-card s-rate">
                <div class="s-ico">📊</div>
                <div class="s-val">{k['rate']:.1f}%</div>
                <div class="s-lbl">Completion Rate</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

def view_performers(k):
    st.markdown('<div class="sec-title"><div class="sec-dot"></div> Performance Analysis</div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="g-card">', unsafe_allow_html=True)
        st.markdown('<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;position:relative;z-index:2;"><div class="card-ico">🏆</div><div><strong style="font-size:17px;color:#F8FAFC;">Top Performers</strong><p style="margin:2px 0 0 0;font-size:12px;color:#94A3B8;">Highest completed transfers</p></div></div>', unsafe_allow_html=True)
        t1,t2,t3 = st.tabs(["Today","This Week","This Month"])
        for tab,key in [(t1,"ac_t"),(t2,"ac_w"),(t3,"ac_m")]:
            with tab:
                counts = k.get(key,pd.Series())
                if not counts.empty:
                    ag = counts.index[0]; cnt = int(counts.iloc[0])
                    st.markdown(f"""
                    <div class="top-hero" style="position:relative;z-index:2;">
                        <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
                            <div style="width:48px;height:48px;background:linear-gradient(135deg,#F59E0B,#D97706);
                            border-radius:13px;display:flex;align-items:center;justify-content:center;
                            font-size:24px;box-shadow:0 6px 16px rgba(245,158,11,0.3);">🥇</div>
                            <div>
                                <strong style="font-size:18px;color:#F8FAFC;">{ag}</strong>
                                <p style="margin:0;font-size:11px;color:#94A3B8;">Top performer</p>
                            </div>
                        </div>
                        <div style="display:flex;align-items:baseline;gap:6px;">
                            <span style="font-size:42px;font-weight:900;color:#FBBF24;letter-spacing:-2px;line-height:1;animation:countPop 0.6s ease 0.2s both;">{cnt}</span>
                            <span style="font-size:13px;color:#94A3B8;">completed transfers</span>
                        </div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.info("No completed transfers yet")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="g-card">', unsafe_allow_html=True)
        st.markdown('<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;position:relative;z-index:2;"><div class="card-ico">📈</div><div><strong style="font-size:17px;color:#F8FAFC;">Agent Rankings</strong><p style="margin:2px 0 0 0;font-size:12px;color:#94A3B8;">All-time completed transfers</p></div></div>', unsafe_allow_html=True)
        ac = k.get("ac",pd.Series())
        if not ac.empty:
            low = k.get("low",""); mx = ac.max()
            for i,(ag,cnt) in enumerate(ac.head(10).items(),1):
                m = {1:"🥇",2:"🥈",3:"🥉"}.get(i,f'<span style="color:#64748B;font-weight:700;">{i}.</span>')
                bw = (cnt/mx*100) if mx>0 else 0
                is_low = ag==low and len(ac)>1
                st.markdown(f"""
                <div class="rank-row {"rank-low" if is_low else ""}" style="animation-delay:{i*0.06}s;position:relative;z-index:2;">
                    <div style="flex:1;">
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span style="font-size:16px;">{m}</span>
                            <span style="font-weight:700;color:#E2E8F0;font-size:14px;">{ag}</span>
                        </div>
                        <div class="bar-trk"><div class="bar-fl" style="width:{bw}%;animation-delay:{i*0.06}s;"></div></div>
                    </div>
                    <span style="color:#818CF8;font-weight:800;font-size:18px;margin-left:12px;">{int(cnt)}</span>
                </div>""", unsafe_allow_html=True)
            if len(ac)>1:
                st.markdown(f"""
                <div class="ins-box ins-danger" style="position:relative;z-index:2;">
                    <span style="font-size:22px;">📉</span>
                    <div><strong style="color:#EF4444;font-size:12px;">Needs Support</strong>
                    <p style="margin:2px 0 0 0;font-size:13px;color:#E2E8F0;">{low} ({int(ac.min())} transfers)</p></div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No agent data")
        st.markdown('</div>', unsafe_allow_html=True)

def view_transfers(k):
    st.markdown('<div class="sec-title"><div class="sec-dot"></div> Transfer Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="g-card">', unsafe_allow_html=True)
    st.markdown('<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;position:relative;z-index:2;"><div class="card-ico">📊</div><div><strong style="font-size:17px;color:#F8FAFC;">Transfer Destinations</strong><p style="margin:2px 0 0 0;font-size:12px;color:#94A3B8;">Where completed transfers are directed</p></div></div>', unsafe_allow_html=True)

    tc = k.get("tc",pd.Series())
    if not tc.empty:
        c1,c2 = st.columns(2)
        lo = dict(height=380, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                  font=dict(family='Inter',color='#94A3B8'), margin=dict(t=40,b=20,l=20,r=20))
        with c1:
            fig = px.pie(values=tc.values,names=tc.index,title="Distribution",
                color_discrete_sequence=['#4F46E5','#06B6D4','#8B5CF6','#10B981','#F59E0B','#312E81'])
            fig.update_layout(**lo)
            fig.update_traces(textposition='inside',textinfo='percent+label',hole=0.45,
                marker=dict(line=dict(color='#0A0E27',width=2)))
            st.plotly_chart(fig,use_container_width=True)
        with c2:
            tf = tc.reset_index(); tf.columns = ['Destination','Count']
            tf = tf.sort_values('Count',ascending=True)
            fig = px.bar(tf,y='Destination',x='Count',title="By Destination",orientation='h',
                color='Count',color_continuous_scale=['rgba(255,255,255,0.05)','#4F46E5'])
            fig.update_layout(**lo,coloraxis_showscale=False)
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig,use_container_width=True)

        st.markdown(f"""
        <div class="hl-box" style="position:relative;z-index:2;">
            <div class="hl-ico">🎯</div>
            <div>
                <div style="font-size:11px;font-weight:700;color:#94A3B8;text-transform:uppercase;letter-spacing:0.8px;">Most Transferred To</div>
                <div style="font-size:22px;font-weight:900;color:#F8FAFC;margin-top:3px;">{k['dest']}</div>
                <div style="font-size:12px;color:#64748B;margin-top:2px;">{k['dest_n']} completed transfers directed here</div>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.info("No completed transfer data")
    st.markdown('</div>', unsafe_allow_html=True)

def view_agents(k):
    st.markdown('<div class="sec-title"><div class="sec-dot"></div> Agent Details</div>', unsafe_allow_html=True)
    st.markdown('<div class="g-card">', unsafe_allow_html=True)
    st.markdown('<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;position:relative;z-index:2;"><div class="card-ico">👤</div><div><strong style="font-size:17px;color:#F8FAFC;">Agent Performance</strong><p style="margin:2px 0 0 0;font-size:12px;color:#94A3B8;">Completed transfers only</p></div></div>', unsafe_allow_html=True)

    ac = k.get("ac",pd.Series())
    if not ac.empty:
        names = sorted(ac.index.tolist())
        sel = st.selectbox("Select Agent:",["All Agents"]+names,key="asel")
        dd = k.get("done_df",pd.DataFrame())
        filt = dd if sel=="All Agents" else dd[dd["Agent Name"]==sel]
        tdf,wdf,mdf = k["tdf"],k["wdf"],k["mdf"]
        if sel!="All Agents":
            t=len(tdf[tdf["Agent Name"]==sel]); w=len(wdf[wdf["Agent Name"]==sel]); m=len(mdf[mdf["Agent Name"]==sel])
        else: t,w,m = k["td"],k["tw"],k["tm"]

        mc1,mc2,mc3,mc4 = st.columns(4)
        with mc1: st.metric("🎯 Total Done",len(filt))
        with mc2: st.metric("📅 Today",t)
        with mc3: st.metric("📆 This Week",w)
        with mc4: st.metric("🗓️ This Month",m)

        if not filt.empty:
            lbl = f" — {sel}" if sel!="All Agents" else ""
            st.markdown(f'<p style="color:#E2E8F0;font-weight:700;margin-top:20px;margin-bottom:8px;">Recent Completed Transfers{lbl}</p>',unsafe_allow_html=True)
            avail = [c for c in ["Timestamp","Agent Name","Customer Name:","Transfer to:","Status","Electric Bill:","Credit Score:"] if c in filt.columns]
            if avail:
                recent = filt[avail].sort_values("Timestamp",ascending=False).head(10)
                show = recent.copy()
                if "Status" in show.columns:
                    show["Status"] = show["Status"].apply(lambda x: "✅ Done" if str(x).strip()=="done" else f"⏳ {str(x).title()}")
                st.dataframe(show,use_container_width=True,hide_index=True,
                    column_config={"Timestamp":st.column_config.DatetimeColumn("Timestamp",format="MM/DD/YYYY HH:mm")})
    else:
        st.info("No agent data")
    st.markdown('</div>',unsafe_allow_html=True)

def view_trends(k):
    st.markdown('<div class="sec-title"><div class="sec-dot"></div> Trend Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="g-card">', unsafe_allow_html=True)
    st.markdown('<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;position:relative;z-index:2;"><div class="card-ico">📈</div><div><strong style="font-size:17px;color:#F8FAFC;">Time Series</strong><p style="margin:2px 0 0 0;font-size:12px;color:#94A3B8;">Completed transfer trends</p></div></div>', unsafe_allow_html=True)

    dd = k.get("done_df",pd.DataFrame())
    if not dd.empty:
        df = dd.copy()
        df['Date'] = df['Timestamp'].dt.date
        daily = df.groupby('Date').size().reset_index(name='Transfers')
        df['Wk'] = df['Timestamp'].dt.isocalendar().week
        df['Yr'] = df['Timestamp'].dt.year
        weekly = df.groupby(['Yr','Wk']).size().reset_index(name='Transfers')
        weekly['Lbl'] = weekly['Yr'].astype(str)+'-W'+weekly['Wk'].astype(str).str.zfill(2)
        df['Mo'] = df['Timestamp'].dt.to_period('M')
        monthly = df.groupby('Mo').size().reset_index(name='Transfers')
        monthly['Mo'] = monthly['Mo'].astype(str)

        lo = dict(height=380, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                  font=dict(family='Inter',color='#94A3B8'), margin=dict(t=40,b=40,l=40,r=20),
                  xaxis=dict(gridcolor='rgba(255,255,255,0.04)',zeroline=False),
                  yaxis=dict(gridcolor='rgba(255,255,255,0.04)',zeroline=False))

        t1,t2,t3 = st.tabs(["Daily","Weekly","Monthly"])
        with t1:
            if len(daily)>1:
                fig = px.area(daily,x='Date',y='Transfers',title="Daily Trend",markers=True)
                fig.update_traces(line_color='#818CF8',fill='tozeroy',fillcolor='rgba(79,70,229,0.08)',
                    marker=dict(color='#06B6D4',size=8,line=dict(color='#0A0E27',width=2)))
                fig.update_layout(**lo); st.plotly_chart(fig,use_container_width=True)
            else: st.info("Insufficient data")
        with t2:
            if len(weekly)>1:
                fig = px.bar(weekly,x='Lbl',y='Transfers',title="Weekly Trend",
                    color='Transfers',color_continuous_scale=['rgba(255,255,255,0.03)','#4F46E5'])
                fig.update_layout(**lo,xaxis_tickangle=-45,coloraxis_showscale=False)
                fig.update_traces(marker_line_width=0)
                st.plotly_chart(fig,use_container_width=True)
            else: st.info("Insufficient data")
        with t3:
            if len(monthly)>1:
                fig = px.bar(monthly,x='Mo',y='Transfers',title="Monthly Trend",
                    color='Transfers',color_continuous_scale=['rgba(255,255,255,0.03)','#312E81'])
                fig.update_layout(**lo,xaxis_tickangle=-45,coloraxis_showscale=False)
                fig.update_traces(marker_line_width=0)
                st.plotly_chart(fig,use_container_width=True)
            else: st.info("Insufficient data")
    else:
        st.info("No completed transfer data")
    st.markdown('</div>',unsafe_allow_html=True)

# ============================================================
# MAIN
# ============================================================
def main():
    view_header()

    with st.spinner("Connecting to Google Sheets..."):
        df = fetch_data()

    if df.empty:
        st.markdown("""
        <div class="warn-card">
            <h3 style="color:#FBBF24;margin-top:0;">⚠️ No data available</h3>
            <p style="color:#E2E8F0;line-height:1.8;">
                <strong>Check:</strong><br>
                1. Google Sheet shared with service account<br>
                2. Data exists in "Form Responses 1"<br>
                3. Secrets configured in Streamlit Cloud
            </p>
        </div>""", unsafe_allow_html=True)
        time.sleep(45); st.rerun()

    if len(df) <= 1:
        st.warning("Sheet has only headers. Waiting for data...")
        time.sleep(45); st.rerun()

    k = calc(df)
    if not k:
        st.warning("No valid records found. Waiting...")
        time.sleep(45); st.rerun()

    st.markdown(f"""
    <div class="ok-banner">
        ✅ Loaded <strong>{len(df)}</strong> records — <strong>{k['done']} completed</strong> transfers counted · {k['pend']} pending
    </div>""", unsafe_allow_html=True)

    view_kpis(k)
    view_status(k)
    view_performers(k)
    view_transfers(k)
    view_agents(k)
    view_trends(k)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"""
    <div class="foot-bar">
        🟢 System Online &nbsp;&nbsp;·&nbsp;&nbsp; Last updated: {now} &nbsp;&nbsp;·&nbsp;&nbsp; Next refresh in 45s
    </div>""", unsafe_allow_html=True)

    time.sleep(45)
    st.rerun()

if __name__ == "__main__":
    main()
