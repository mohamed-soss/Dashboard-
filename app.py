import streamlit as st
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
    initial_sidebar_state="collapsed"
)

# ============================================================
# NEURAL NETWORK CANVAS + FULL CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
:root {
    --primary: #4F46E5;
    --primary-light: #818CF8;
    --primary-dark: #312E81;
    --accent: #06B6D4;
    --accent2: #8B5CF6;
    --bg: #0A0E27;
    --surface: rgba(255,255,255,0.04);
    --surface2: rgba(255,255,255,0.06);
    --border: rgba(255,255,255,0.08);
    --border2: rgba(255,255,255,0.12);
    --text: #FFFFFF;
    --text-muted: rgba(255,255,255,0.85);
    --text-bright: #FFFFFF;
    --success: #10B981;
    --warning: #F59E0B;
    --danger: #EF4444;
    --glow: rgba(79,70,229,0.4);
}
* { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; color: #FFFFFF !important; }
.stApp {
    background: var(--bg) !important;
}
/* Neural canvas behind everything */
#neural-canvas {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    z-index: 0;
    pointer-events: none;
}
/* Make sure Streamlit content is above canvas */
.stApp > div, .stApp > header, .main, .block-container {
    position: relative;
    z-index: 1;
}
/* ==================== ANIMATIONS ==================== */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(30px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeDown {
    from { opacity: 0; transform: translateY(-20px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.9); }
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
@keyframes glow {
    0%, 100% { box-shadow: 0 0 20px rgba(79,70,229,0.15); }
    50% { box-shadow: 0 0 40px rgba(79,70,229,0.35); }
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.85); }
}
@keyframes borderGlow {
    0%, 100% { border-color: rgba(79,70,229,0.2); }
    50% { border-color: rgba(79,70,229,0.5); }
}
@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-8px); }
}
@keyframes countPop {
    0%   { opacity: 0; transform: scale(0.6); filter: blur(6px); }
    60%  { transform: scale(1.08); filter: blur(0); }
    100% { opacity: 1; transform: scale(1); filter: blur(0); }
}
@keyframes barGrow {
    from { width: 0%; }
}
/* ==================== HEADER ==================== */
.main-header {
    background: linear-gradient(135deg, #1E1B4B 0%, #312E81 30%, #4338CA 60%, #0891B2 100%);
    background-size: 300% 300%;
    animation: gradientShift 12s ease infinite, fadeDown 0.8s cubic-bezier(0.16,1,0.3,1) forwards;
    border-radius: 20px;
    padding: 32px 40px;
    margin-bottom: 28px;
    color: white;
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 20px 60px rgba(0,0,0,0.4), 0 0 80px rgba(79,70,229,0.15);
}
.main-header::before {
    content: '';
    position: absolute;
    top: -50%; right: -10%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(129,140,248,0.15), transparent 60%);
    border-radius: 50%;
    animation: float 6s ease infinite;
}
.main-header::after {
    content: '';
    position: absolute;
    bottom: -40%; left: 20%;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(6,182,212,0.1), transparent 60%);
    border-radius: 50%;
    animation: float 8s ease infinite reverse;
}
.main-header h1 {
    color: white !important;
    font-size: 30px; font-weight: 900;
    margin: 0; letter-spacing: -1px;
    position: relative; z-index: 2;
}
.main-header p {
    color: rgba(255,255,255,0.9) !important;
    font-size: 14px; margin: 6px 0 0 0;
    position: relative; z-index: 2;
}
.header-badges {
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
    font-size: 12px; color: white !important;
    transition: all 0.3s ease;
}
.h-badge:hover {
    background: rgba(255,255,255,0.15);
    transform: translateY(-1px);
}
.live-dot {
    width: 8px; height: 8px;
    background: #34D399;
    border-radius: 50%;
    animation: pulse 2s ease infinite;
    box-shadow: 0 0 10px rgba(52,211,153,0.6);
}
/* Mode Switcher Buttons */
.mode-switcher {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
    justify-content: flex-end;
    animation: fadeDown 0.5s ease forwards;
}
/* ==================== METRIC CARDS ==================== */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
    backdrop-filter: blur(20px);
    border: 1px solid var(--border2);
    border-radius: 16px;
    padding: 22px 24px;
    transition: all 0.5s cubic-bezier(0.16,1,0.3,1);
    animation: fadeUp 0.6s cubic-bezier(0.16,1,0.3,1) forwards;
    position: relative;
    overflow: hidden;
}
div[data-testid="stMetric"]:nth-child(1) { animation-delay: 0.1s; }
div[data-testid="stMetric"]:nth-child(2) { animation-delay: 0.2s; }
div[data-testid="stMetric"]:nth-child(3) { animation-delay: 0.3s; }
div[data-testid="stMetric"]:nth-child(4) { animation-delay: 0.4s; }
div[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--primary), var(--accent), var(--accent2));
    transform: scaleX(0);
    transition: transform 0.5s cubic-bezier(0.16,1,0.3,1);
    transform-origin: left;
}
div[data-testid="stMetric"]:hover::before { transform: scaleX(1); }
div[data-testid="stMetric"]:hover {
    transform: translateY(-6px);
    box-shadow: 0 20px 50px rgba(79,70,229,0.2), 0 0 30px rgba(79,70,229,0.1);
    border-color: rgba(129,140,248,0.3);
    background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
}
div[data-testid="stMetric"] label {
    color: white !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: white !important;
    font-size: 36px !important;
    font-weight: 900 !important;
    letter-spacing: -1.5px !important;
    animation: countPop 0.7s cubic-bezier(0.16,1,0.3,1) 0.5s both;
}
div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {
    color: rgba(255,255,255,0.85) !important;
    font-size: 12px !important;
    font-weight: 500 !important;
}
/* ==================== SECTION HEADERS ==================== */
.section-title {
    color: white;
    font-size: 20px; font-weight: 800;
    margin: 36px 0 18px 0;
    padding-bottom: 12px;
    border-bottom: 2px solid;
    border-image: linear-gradient(90deg, var(--primary), var(--accent), transparent) 1;
    animation: slideLeft 0.6s cubic-bezier(0.16,1,0.3,1) forwards;
    letter-spacing: -0.5px;
    display: flex; align-items: center; gap: 10px;
}
.section-dot {
    width: 10px; height: 10px;
    background: var(--primary);
    border-radius: 50%;
    box-shadow: 0 0 12px var(--glow);
    animation: pulse 3s ease infinite;
}
/* ==================== GLASS CARDS ==================== */
.glass-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
    backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 28px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.2);
    animation: fadeUp 0.6s cubic-bezier(0.16,1,0.3,1) forwards;
    transition: all 0.4s cubic-bezier(0.16,1,0.3,1);
    position: relative;
    overflow: hidden;
}
.glass-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: linear-gradient(135deg, rgba(79,70,229,0.03), transparent, rgba(6,182,212,0.02));
    pointer-events: none;
}
.glass-card:hover {
    border-color: rgba(129,140,248,0.2);
    box-shadow: 0 12px 40px rgba(0,0,0,0.3), 0 0 40px rgba(79,70,229,0.08);
    transform: translateY(-2px);
}
.glass-card h3, .glass-card strong {
    color: white !important;
}
.glass-card p, .glass-card span {
    color: rgba(255,255,255,0.85) !important;
}
/* Card icon */
.card-ico {
    width: 44px; height: 44px;
    background: linear-gradient(135deg, var(--primary), var(--accent));
    border-radius: 12px;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 20px;
    box-shadow: 0 8px 20px rgba(79,70,229,0.3);
    margin-bottom: 14px;
    transition: all 0.3s ease;
}
.glass-card:hover .card-ico {
    transform: rotate(-5deg) scale(1.1);
    box-shadow: 0 12px 28px rgba(79,70,229,0.4);
}
/* ==================== STATUS GRID ==================== */
.status-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-top: 16px;
}
.s-card {
    border-radius: 14px;
    padding: 22px;
    text-align: center;
    transition: all 0.4s cubic-bezier(0.16,1,0.3,1);
    position: relative;
    overflow: hidden;
}
.s-card:hover {
    transform: translateY(-4px) scale(1.02);
}
.s-card::after {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 50% 50%, rgba(255,255,255,0.08), transparent 60%);
    opacity: 0;
    transition: opacity 0.4s;
}
.s-card:hover::after { opacity: 1; }
.s-done {
    background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(16,185,129,0.05));
    border: 1px solid rgba(16,185,129,0.2);
}
.s-pending {
    background: linear-gradient(135deg, rgba(245,158,11,0.1), rgba(245,158,11,0.05));
    border: 1px solid rgba(245,158,11,0.2);
}
.s-failed {
    background: linear-gradient(135deg, rgba(239,68,68,0.1), rgba(239,68,68,0.05));
    border: 1px solid rgba(239,68,68,0.2);
}
.s-rate {
    background: linear-gradient(135deg, rgba(79,70,229,0.1), rgba(79,70,229,0.05));
    border: 1px solid rgba(79,70,229,0.2);
}
.s-ico { font-size: 30px; margin-bottom: 8px; }
.s-val {
    font-size: 34px; font-weight: 900;
    letter-spacing: -1px;
    animation: countPop 0.7s cubic-bezier(0.16,1,0.3,1) 0.4s both;
}
.s-done .s-val { color: white !important; }
.s-pending .s-val { color: white !important; }
.s-failed .s-val { color: white !important; }
.s-rate .s-val { color: white !important; }
.s-lbl {
    font-size: 12px; font-weight: 600;
    margin-top: 4px;
}
.s-done .s-lbl { color: white !important; }
.s-pending .s-lbl { color: white !important; }
.s-failed .s-lbl { color: white !important; }
.s-rate .s-lbl { color: white !important; }
/* ==================== TOP PERFORMER ==================== */
.top-hero {
    background: linear-gradient(135deg, rgba(245,158,11,0.08), rgba(245,158,11,0.03));
    border: 1px solid rgba(245,158,11,0.15);
    border-radius: 14px;
    padding: 22px;
    margin: 14px 0;
    animation: scaleIn 0.5s cubic-bezier(0.16,1,0.3,1) forwards;
    transition: all 0.3s ease;
}
.top-hero:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 32px rgba(245,158,11,0.12);
}
/* ==================== RANKING ==================== */
.rank-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 16px;
    margin: 7px 0;
    border-radius: 12px;
    background: rgba(255,255,255,0.02);
    border: 1px solid transparent;
    transition: all 0.4s cubic-bezier(0.16,1,0.3,1);
    animation: slideRight 0.5s cubic-bezier(0.16,1,0.3,1) forwards;
    cursor: default;
}
.rank-row:hover {
    background: rgba(255,255,255,0.06);
    border-color: rgba(129,140,248,0.2);
    transform: translateX(6px);
    box-shadow: 0 8px 24px rgba(79,70,229,0.1);
}
.rank-low {
    background: rgba(239,68,68,0.04) !important;
    border-color: rgba(239,68,68,0.1) !important;
}
.rank-low:hover {
    border-color: rgba(239,68,68,0.25) !important;
    box-shadow: 0 8px 24px rgba(239,68,68,0.08) !important;
}
.bar-track {
    background: rgba(255,255,255,0.06);
    border-radius: 4px; height: 5px;
    margin-top: 6px; overflow: hidden;
}
.bar-fill {
    height: 100%; border-radius: 4px;
    background: linear-gradient(90deg, var(--primary), var(--accent));
    animation: barGrow 1.2s cubic-bezier(0.16,1,0.3,1) forwards;
}
/* ==================== HIGHLIGHT BOX ==================== */
.highlight-box {
    margin-top: 18px;
    padding: 20px 24px;
    background: linear-gradient(135deg, rgba(79,70,229,0.08), rgba(6,182,212,0.06));
    border: 1px solid rgba(79,70,229,0.15);
    border-radius: 14px;
    display: flex; align-items: center; gap: 16px;
    animation: scaleIn 0.5s cubic-bezier(0.16,1,0.3,1) 0.3s both;
    transition: all 0.4s ease;
}
.highlight-box:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 32px rgba(79,70,229,0.12);
    border-color: rgba(129,140,248,0.3);
}
.hl-ico {
    width: 50px; height: 50px;
    background: linear-gradient(135deg, var(--primary), var(--accent));
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    box-shadow: 0 8px 20px rgba(79,70,229,0.3);
    flex-shrink: 0;
}
/* ==================== INSIGHT BOX ==================== */
.insight-box {
    margin-top: 14px;
    padding: 14px 18px;
    border-radius: 12px;
    display: flex; align-items: center; gap: 12px;
    animation: fadeUp 0.5s cubic-bezier(0.16,1,0.3,1) 0.5s both;
    transition: all 0.3s ease;
}
.insight-box:hover { transform: translateY(-2px); }
.insight-danger {
    background: rgba(239,68,68,0.06);
    border: 1px solid rgba(239,68,68,0.12);
}
.insight-success {
    background: rgba(16,185,129,0.06);
    border: 1px solid rgba(16,185,129,0.12);
}
.insight-warning {
    background: rgba(245,158,11,0.06);
    border: 1px solid rgba(245,158,11,0.12);
}
/* ==================== TABS ==================== */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: rgba(255,255,255,0.04);
    border-radius: 12px;
    padding: 4px;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 10px;
    padding: 8px 20px;
    border: none !important;
    color: white !important;
    font-weight: 600;
    font-size: 13px;
    transition: all 0.3s ease;
}
.stTabs [aria-selected="true"] {
    background: rgba(79,70,229,0.2) !important;
    color: white !important;
    font-weight: 700;
    box-shadow: 0 0 20px rgba(79,70,229,0.15);
}
.stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
    color: white !important;
    background: rgba(255,255,255,0.04);
}
/* ==================== DATAFRAME ==================== */
.stDataFrame {
    border-radius: 14px !important;
    overflow: hidden !important;
    border: 1px solid var(--border) !important;
}
.stDataFrame table { color: white !important; }
.stDataFrame th {
    background: rgba(79,70,229,0.1) !important;
    color: white !important;
    font-weight: 700 !important;
}
.stDataFrame td { color: white !important; }
/* ==================== SELECTBOX ==================== */
.stSelectbox label { color: white !important; }
.stSelectbox > div > div {
    border-radius: 10px !important;
    border-color: var(--border2) !important;
    background: rgba(255,255,255,0.04) !important;
    color: white !important;
}
/* ==================== SUCCESS BANNER ==================== */
.success-banner {
    background: linear-gradient(135deg, rgba(16,185,129,0.08), rgba(16,185,129,0.03));
    border: 1px solid rgba(16,185,129,0.15);
    border-radius: 14px;
    padding: 14px 22px;
    margin-bottom: 14px;
    display: flex; align-items: center; gap: 12px;
    animation: fadeDown 0.5s cubic-bezier(0.16,1,0.3,1) forwards;
    color: white !important;
    font-size: 14px; font-weight: 500;
}
/* ==================== WARNING ==================== */
.warn-card {
    background: linear-gradient(135deg, rgba(245,158,11,0.08), rgba(245,158,11,0.03));
    border: 1px solid rgba(245,158,11,0.15);
    border-left: 4px solid var(--warning);
    border-radius: 16px;
    padding: 28px;
    animation: fadeUp 0.5s ease forwards;
    color: white !important;
}
/* ==================== FOOTER ==================== */
.footer-bar {
    margin-top: 36px;
    padding: 16px;
    background: linear-gradient(135deg, rgba(255,255,255,0.04), rgba(255,255,255,0.02));
    backdrop-filter: blur(20px);
    border: 1px solid var(--border);
    border-radius: 14px;
    text-align: center;
    color: white !important;
    font-size: 13px;
    animation: fadeUp 0.5s ease 0.8s both;
}
/* ==================== MISC ==================== */
#MainMenu, footer, header { visibility: hidden !important; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--primary); }
/* Plotly dark fix */
.js-plotly-plot .plotly .bg { fill: transparent !important; }
/* ==================== GLOBAL WHITE TEXT OVERRIDE ==================== */
p, span, label, div, td, th, li, a, h1, h2, h3, h4, h5, h6, strong, em, b, i, small {
    color: white !important;
}
/* Admin Panel Styles */
.admin-header {
    background: linear-gradient(135deg, #1E1B4B 0%, #312E81 30%, #7C3AED 60%, #D946EF 100%);
    background-size: 300% 300%;
    animation: gradientShift 12s ease infinite;
}
.login-container {
    max-width: 400px;
    margin: 100px auto;
    padding: 40px;
    background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.02));
    backdrop-filter: blur(20px);
    border: 1px solid var(--border2);
    border-radius: 24px;
    text-align: center;
}
</style>
<!-- NEURAL NETWORK CANVAS -->
<canvas id="neural-canvas"></canvas>
<script>
(function() {
    const canvas = document.getElementById('neural-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let W, H;
    function resize() {
        W = canvas.width = window.innerWidth;
        H = canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);
    const NUM = 80;
    const MAX_DIST = 150;
    const dots = [];
    for (let i = 0; i < NUM; i++) {
        dots.push({
            x: Math.random() * W,
            y: Math.random() * H,
            vx: (Math.random() - 0.5) * 0.6,
            vy: (Math.random() - 0.5) * 0.6,
            r: Math.random() * 2 + 1
        });
    }
    function draw() {
        ctx.clearRect(0, 0, W, H);
        for (let i = 0; i < NUM; i++) {
            for (let j = i + 1; j < NUM; j++) {
                const dx = dots[i].x - dots[j].x;
                const dy = dots[i].y - dots[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < MAX_DIST) {
                    const alpha = (1 - dist / MAX_DIST) * 0.25;
                    ctx.beginPath();
                    ctx.strokeStyle = `rgba(129,140,248,${alpha})`;
                    ctx.lineWidth = 0.8;
                    ctx.moveTo(dots[i].x, dots[i].y);
                    ctx.lineTo(dots[j].x, dots[j].y);
                    ctx.stroke();
                }
            }
        }
        for (let i = 0; i < NUM; i++) {
            const d = dots[i];
            ctx.beginPath();
            const grd = ctx.createRadialGradient(d.x, d.y, 0, d.x, d.y, d.r * 4);
            grd.addColorStop(0, 'rgba(129,140,248,0.3)');
            grd.addColorStop(1, 'rgba(129,140,248,0)');
            ctx.fillStyle = grd;
            ctx.arc(d.x, d.y, d.r * 4, 0, Math.PI * 2);
            ctx.fill();
            ctx.beginPath();
            ctx.fillStyle = `rgba(165,180,252,${0.6 + Math.random() * 0.4})`;
            ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2);
            ctx.fill();
            d.x += d.vx;
            d.y += d.vy;
            if (d.x < 0 || d.x > W) d.vx *= -1;
            if (d.y < 0 || d.y > H) d.vy *= -1;
        }
        requestAnimationFrame(draw);
    }
    draw();
})();
</script>
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
        if "Status" in df.columns:
            df["IsFailed"] = df["Status"].isin(["failed", "reject", "rejected", "fail", "not done"])
        else:
            df["IsFailed"] = False
            
        for c in ["Timestamp","Agent Name","Transfer to:","Customer Name:","Electric Bill:","Credit Score:","Status","FeedBack","H comments"]:
            if c not in df.columns: df[c] = None
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return pd.DataFrame()

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def get_custom_date_range():
    """Get date range from 10th of current/previous month to 10th of next month"""
    today = datetime.now()
    if today.day >= 10:
        start_date = datetime(today.year, today.month, 10)
        if today.month == 12:
            end_date = datetime(today.year + 1, 1, 10)
        else:
            end_date = datetime(today.year, today.month + 1, 10)
    else:
        if today.month == 1:
            start_date = datetime(today.year - 1, 12, 10)
        else:
            start_date = datetime(today.year, today.month - 1, 10)
        end_date = datetime(today.year, today.month, 10)
    return start_date, end_date

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
    
    custom_start, custom_end = get_custom_date_range()
    
    return {
        "today":(ts, ts+timedelta(days=1)),
        "yest":(ys, ys+timedelta(days=1)),
        "week":(ws, ws+timedelta(days=7)),
        "lweek":(lws, lws+timedelta(days=7)),
        "month":(ms, datetime(n.year+1,1,1) if n.month==12 else datetime(n.year,n.month+1,1)),
        "lmonth":(lms, lme),
        "custom":(custom_start, custom_end)
    }

def calc(df, use_custom_range=False):
    if df.empty: return {}
    df = df[df["Timestamp"].notna()].copy()
    if df.empty: return {}
    done = df[df["Status"]=="done"].copy()
    failed = df[df["IsFailed"] == True].copy()
    total = len(df)
    dn = len(done)
    pend = total - dn - len(failed)
    failed_count = len(failed)
    
    r = ranges()
    
    def f(d,k):
        if k == "custom" and use_custom_range:
            s,e = r["custom"]
        else:
            s,e = r[k]
        return d[(d["Timestamp"]>=s)&(d["Timestamp"]<e)]
    
    td=f(done,"today")
    yd=f(done,"yest")
    tw=f(done,"week")
    lw=f(done,"lweek")
    tm=f(done,"month")
    lm=f(done,"lmonth")
    tc_custom = f(done, "custom") if use_custom_range else pd.DataFrame()
    
    failed_by_agent = failed["Agent Name"].value_counts() if "Agent Name" in failed.columns else pd.Series()
    failed_today = f(failed, "today")
    failed_week = f(failed, "week")
    failed_month = f(failed, "month")
    failed_custom = f(failed, "custom") if use_custom_range else pd.DataFrame()
    
    def pc(a,b): return ((a-b)/b*100) if b>0 else 0
    
    tc = done["Transfer to:"].value_counts() if "Transfer to:" in done.columns else pd.Series()
    ac = done["Agent Name"].value_counts() if "Agent Name" in done.columns else pd.Series()
    
    agent_success_rates = {}
    if "Agent Name" in df.columns:
        for agent in df["Agent Name"].dropna().unique():
            agent_total = len(df[df["Agent Name"] == agent])
            agent_done = len(done[done["Agent Name"] == agent])
            agent_failed = len(failed[failed["Agent Name"] == agent])
            agent_success_rates[agent] = {
                "total": agent_total,
                "done": agent_done,
                "failed": agent_failed,
                "pending": agent_total - agent_done - agent_failed,
                "success_rate": (agent_done / agent_total * 100) if agent_total > 0 else 0,
                "fail_rate": (agent_failed / agent_total * 100) if agent_total > 0 else 0
            }
    
    return {
        "total":total,"done":dn,"pend":pend,"failed":failed_count,
        "rate":(dn/total*100) if total>0 else 0,
        "dest":tc.index[0] if not tc.empty else "N/A",
        "dest_n":int(tc.iloc[0]) if not tc.empty else 0,
        "tc":tc,"ac":ac,
        "ac_t":td["Agent Name"].value_counts() if "Agent Name" in td.columns else pd.Series(),
        "ac_w":tw["Agent Name"].value_counts() if "Agent Name" in tw.columns else pd.Series(),
        "ac_m":tm["Agent Name"].value_counts() if "Agent Name" in tm.columns else pd.Series(),
        "ac_custom":tc_custom["Agent Name"].value_counts() if "Agent Name" in tc_custom.columns else pd.Series(),
        "low":ac.idxmin() if len(ac)>1 else "N/A",
        "td":len(td),"yd":len(yd),"dp":pc(len(td),len(yd)),
        "tw":len(tw),"lw":len(lw),"wp":pc(len(tw),len(lw)),
        "tm":len(tm),"lm":len(lm),"mp":pc(len(tm),len(lm)),
        "tc_custom":len(tc_custom),
        "full":df,"done_df":done,"failed_df":failed,
        "tdf":td,"wdf":tw,"mdf":tm,"custom_df":tc_custom,
        "failed_by_agent":failed_by_agent,
        "failed_today":len(failed_today),
        "failed_week":len(failed_week),
        "failed_month":len(failed_month),
        "failed_custom":len(failed_custom),
        "agent_success_rates":agent_success_rates
    }

# ============================================================
# ADMIN VIEWS
# ============================================================
def view_admin_header():
    st.markdown(f"""
    <div class="main-header admin-header">
        <h1>👑 Admin Dashboard</h1>
        <p>Full access — custom date range (10th to 10th) & failed transfer tracking</p>
        <div class="header-badges">
            <div class="h-badge"><div class="live-dot"></div> Admin Mode</div>
            <div class="h-badge">📅 Custom Period: 10th → 10th</div>
            <div class="h-badge">🔄 Auto-refresh 45s</div>
        </div>
    </div>""", unsafe_allow_html=True)

def view_admin_kpis(k):
    try:
        c1,c2,c3,c4,c5 = st.columns(5)
        with c1: st.metric("✅ Completed Transfers", f"{k.get('done', 0):,}", f"{k.get('rate', 0):.1f}% rate")
        with c2: st.metric("❌ Failed Transfers", f"{k.get('failed', 0):,}", help="Transfers marked as failed/rejected")
        with c3: st.metric("⏳ Pending", f"{k.get('pend', 0):,}")
        with c4: st.metric("📅 Custom Period (10th→10th)", f"{k.get('tc_custom', 0):,}", help="Transfers from 10th of month to 10th of next month")
        with c5: st.metric("📊 Success Rate", f"{k.get('rate', 0):.1f}%", f"Failed: {k.get('failed', 0)}")
    except Exception as e:
        st.error(f"Error displaying KPIs")

def view_failed_transfers(k):
    st.markdown('<div class="section-title"><div class="section-dot"></div> ❌ Failed Transfer Analysis</div>', unsafe_allow_html=True)
    
    c1,c2 = st.columns(2)
    
    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;"><div class="card-ico">⚠️</div><div><strong style="font-size:17px;color:white !important;">Failed Transfers by Agent</strong></div></div>', unsafe_allow_html=True)
        
        failed_by_agent = k.get("failed_by_agent", pd.Series())
        if not failed_by_agent.empty and len(failed_by_agent) > 0:
            try:
                failed_df = failed_by_agent.reset_index()
                failed_df.columns = ['Agent', 'Failed Count']
                failed_df = failed_df.sort_values('Failed Count', ascending=True)
                
                fig = px.bar(failed_df, y='Agent', x='Failed Count', title="Failed Transfers per Agent",
                            orientation='h', color='Failed Count',
                            color_continuous_scale=['rgba(255,255,255,0.05)', '#EF4444'])
                fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                font=dict(family='Inter',color='white'), margin=dict(t=40,b=20,l=20,r=20))
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.info("No failed transfers data to display")
        else:
            st.info("No failed transfers recorded")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with c2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;"><div class="card-ico">📈</div><div><strong style="font-size:17px;color:white !important;">Failed Transfer Trends</strong></div></div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="status-grid" style="grid-template-columns: repeat(2, 1fr);">
            <div class="s-card s-failed">
                <div class="s-ico">📅</div>
                <div class="s-val">{k.get('failed_today', 0)}</div>
                <div class="s-lbl">Failed Today</div>
            </div>
            <div class="s-card s-failed">
                <div class="s-ico">📆</div>
                <div class="s-val">{k.get('failed_week', 0)}</div>
                <div class="s-lbl">Failed This Week</div>
            </div>
            <div class="s-card s-failed">
                <div class="s-ico">🗓️</div>
                <div class="s-val">{k.get('failed_month', 0)}</div>
                <div class="s-lbl">Failed This Month</div>
            </div>
            <div class="s-card s-failed">
                <div class="s-ico">📊</div>
                <div class="s-val">{k.get('failed_custom', 0)}</div>
                <div class="s-lbl">Failed (Custom Period)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def view_agent_success_rates(k):
    st.markdown('<div class="section-title"><div class="section-dot"></div> 📊 Agent Success & Failure Rates</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    agent_rates = k.get("agent_success_rates", {})
    if agent_rates and len(agent_rates) > 0:
        agent_data = []
        for agent, stats in agent_rates.items():
            agent_data.append({
                "Agent": agent,
                "Completed": stats.get("done", 0),
                "Failed": stats.get("failed", 0),
                "Pending": stats.get("pending", 0),
                "Total": stats.get("total", 0),
                "Success Rate %": round(stats.get("success_rate", 0), 1),
                "Fail Rate %": round(stats.get("fail_rate", 0), 1)
            })
        
        agent_df = pd.DataFrame(agent_data)
        if not agent_df.empty:
            agent_df = agent_df.sort_values("Success Rate %", ascending=False)
            
            try:
                fig = px.bar(agent_df, x='Agent', y=['Success Rate %', 'Fail Rate %'], 
                            title="Agent Performance Metrics",
                            barmode='group',
                            color_discrete_map={'Success Rate %': '#10B981', 'Fail Rate %': '#EF4444'})
                fig.update_layout(height=450, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                                 font=dict(family='Inter',color='white'), margin=dict(t=40,b=40,l=40,r=40),
                                 xaxis_tickangle=-45)
                fig.update_yaxes(title="Percentage (%)", range=[0, 100])
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.info("Could not create performance chart")
            
            st.markdown('<p style="margin-top:20px;font-weight:700;">Agent Performance Details</p>', unsafe_allow_html=True)
            st.dataframe(agent_df, use_container_width=True, hide_index=True)
            
            low_performers = agent_df[agent_df["Success Rate %"] < 50]
            if not low_performers.empty:
                low_agents = ', '.join(low_performers['Agent'].tolist())
                st.markdown(f"""
                <div class="insight-box insight-danger">
                    <span style="font-size:22px;">⚠️</span>
                    <div>
                        <strong>Low Performance Alert</strong><br>
                        The following agents have success rates below 50%: {low_agents}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No agent performance data available")
    else:
        st.info("No agent performance data available")
    
    st.markdown('</div>', unsafe_allow_html=True)

def view_custom_period_performance(k):
    st.markdown('<div class="section-title"><div class="section-dot"></div> 📅 Custom Period Performance (10th → 10th)</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    try:
        start_date, end_date = get_custom_date_range()
        st.markdown(f"""
        <div class="highlight-box">
            <div class="hl-ico">📅</div>
            <div>
                <div style="font-size:11px;font-weight:700;text-transform:uppercase;">Current Reporting Period</div>
                <div style="font-size:18px;font-weight:800;margin-top:3px;">{start_date.strftime('%B %d, %Y')} → {end_date.strftime('%B %d, %Y')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.warning("Could not calculate custom date range")
    
    ac_custom = k.get("ac_custom", pd.Series())
    if not ac_custom.empty and len(ac_custom) > 0:
        st.markdown('<p style="font-weight:700;margin-top:20px;">🏆 Top Performers (Custom Period)</p>', unsafe_allow_html=True)
        
        for i, (agent, count) in enumerate(ac_custom.head(5).items(), 1):
            medal = {1:"🥇",2:"🥈",3:"🥉"}.get(i, f"{i}.")
            st.markdown(f"""
            <div class="rank-row" style="animation-delay:{i*0.05}s;">
                <div style="display:flex;align-items:center;gap:12px;">
                    <span style="font-size:20px;">{medal}</span>
                    <span style="font-weight:700;font-size:16px;">{agent}</span>
                </div>
                <span style="font-weight:800;font-size:20px;">{int(count)}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No data available for custom period")
    
    st.markdown('</div>', unsafe_allow_html=True)

def view_admin_transfers(k):
    st.markdown('<div class="section-title"><div class="section-dot"></div> 📋 Failed Transfer Details</div>', unsafe_allow_html=True)
    
    failed_df = k.get("failed_df", pd.DataFrame())
    if not failed_df.empty and len(failed_df) > 0:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        
        try:
            col1, col2 = st.columns(2)
            with col1:
                agents = ["All"] + sorted(failed_df["Agent Name"].dropna().unique().tolist())
                selected_agent = st.selectbox("Filter by Agent:", agents, key="admin_agent_filter")
            with col2:
                min_date = failed_df["Timestamp"].min().date() if not failed_df.empty else datetime.now().date()
                max_date = failed_df["Timestamp"].max().date() if not failed_df.empty else datetime.now().date()
                date_range = st.date_input("Date Range:", 
                                           value=(min_date, max_date),
                                           key="admin_date_filter")
            
            filtered_failed = failed_df.copy()
            if selected_agent != "All":
                filtered_failed = filtered_failed[filtered_failed["Agent Name"] == selected_agent]
            if len(date_range) == 2:
                filtered_failed = filtered_failed[(filtered_failed["Timestamp"].dt.date >= date_range[0]) &
                                                  (filtered_failed["Timestamp"].dt.date <= date_range[1])]
            
            display_cols = ["Timestamp", "Agent Name", "Customer Name:", "Transfer to:", "Status", "FeedBack", "H comments"]
            available_cols = [c for c in display_cols if c in filtered_failed.columns]
            
            if not filtered_failed.empty:
                st.markdown(f'<p style="font-weight:700;">Failed Transfers: {len(filtered_failed)} records</p>', unsafe_allow_html=True)
                st.dataframe(filtered_failed[available_cols].sort_values("Timestamp", ascending=False), 
                            use_container_width=True, hide_index=True)
            else:
                st.info("No failed transfers match the filters")
        except Exception as e:
            st.warning(f"Error displaying failed transfers")
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="glass-card"><p>✅ No failed transfers recorded. All transfers completed successfully!</p></div>', unsafe_allow_html=True)

# ============================================================
# REGULAR VIEWS (Original)
# ============================================================
def view_header():
    st.markdown(f"""
    <div class="main-header">
        <h1>⚡ Sales Transfer Dashboard</h1>
        <p>Real-time monitoring — only completed (done) transfers are counted</p>
        <div class="header-badges">
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
    st.markdown('<div class="section-title"><div class="section-dot"></div> Status Overview</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="glass-card">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
            <div class="card-ico">📋</div>
            <div>
                <strong style="font-size:17px;color:white !important;">Transfer Status Breakdown</strong>
                <p style="margin:2px 0 0 0;font-size:12px;color:rgba(255,255,255,0.85) !important;">Only "done" entries count as completed transfers</p>
            </div>
        </div>
        <div class="status-grid">
            <div class="s-card s-done">
                <div class="s-ico">✅</div>
                <div class="s-val">{k['done']}</div>
                <div class="s-lbl">Completed</div>
            </div>
            <div class="s-card s-pending">
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
    st.markdown('<div class="section-title"><div class="section-dot"></div> Performance Analysis</div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;"><div class="card-ico">🏆</div><div><strong style="font-size:17px;color:white !important;">Top Performers</strong><p style="margin:2px 0 0 0;font-size:12px;color:rgba(255,255,255,0.85) !important;">Highest completed transfers</p></div></div>', unsafe_allow_html=True)
        t1,t2,t3 = st.tabs(["Today","This Week","This Month"])
        for tab,key in [(t1,"ac_t"),(t2,"ac_w"),(t3,"ac_m")]:
            with tab:
                counts = k.get(key,pd.Series())
                if not counts.empty:
                    ag = counts.index[0]; cnt = int(counts.iloc[0])
                    st.markdown(f"""
                    <div class="top-hero">
                        <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
                            <div style="width:48px;height:48px;background:linear-gradient(135deg,#F59E0B,#D97706);
                            border-radius:13px;display:flex;align-items:center;justify-content:center;
                            font-size:24px;box-shadow:0 6px 16px rgba(245,158,11,0.3);">🥇</div>
                            <div>
                                <strong style="font-size:18px;color:white !important;">{ag}</strong>
                                <p style="margin:0;font-size:11px;color:rgba(255,255,255,0.85) !important;">Top performer</p>
                            </div>
                        </div>
                        <div style="display:flex;align-items:baseline;gap:6px;">
                            <span style="font-size:42px;font-weight:900;color:white !important;letter-spacing:-2px;line-height:1;animation:countPop 0.6s ease 0.2s both;">{cnt}</span>
                            <span style="font-size:13px;color:rgba(255,255,255,0.85) !important;">completed transfers</span>
                        </div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.info("No completed transfers yet")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;"><div class="card-ico">📈</div><div><strong style="font-size:17px;color:white !important;">Agent Rankings</strong><p style="margin:2px 0 0 0;font-size:12px;color:rgba(255,255,255,0.85) !important;">All-time completed transfers</p></div></div>', unsafe_allow_html=True)
        ac = k.get("ac",pd.Series())
        if not ac.empty:
            low = k.get("low",""); mx = ac.max()
            for i,(ag,cnt) in enumerate(ac.head(10).items(),1):
                m = {1:"🥇",2:"🥈",3:"🥉"}.get(i,f'<span style="color:white !important;font-weight:700;">{i}.</span>')
                bw = (cnt/mx*100) if mx>0 else 0
                is_low = ag==low and len(ac)>1
                st.markdown(f"""
                <div class="rank-row {"rank-low" if is_low else ""}" style="animation-delay:{i*0.06}s;">
                    <div style="flex:1;">
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span style="font-size:16px;">{m}</span>
                            <span style="font-weight:700;color:white !important;font-size:14px;">{ag}</span>
                        </div>
                        <div class="bar-track"><div class="bar-fill" style="width:{bw}%;animation-delay:{i*0.06}s;"></div></div>
                    </div>
                    <span style="color:white !important;font-weight:800;font-size:18px;margin-left:12px;">{int(cnt)}</span>
                </div>""", unsafe_allow_html=True)
            if len(ac)>1:
                st.markdown(f"""
                <div class="insight-box insight-danger">
                    <span style="font-size:22px;">📉</span>
                    <div><strong style="color:white !important;font-size:12px;">Needs Support</strong>
                    <p style="margin:2px 0 0 0;font-size:13px;color:white !important;">{low} ({int(ac.min())} transfers)</p></div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No agent data")
        st.markdown('</div>', unsafe_allow_html=True)

def view_transfers(k):
    st.markdown('<div class="section-title"><div class="section-dot"></div> Transfer Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;"><div class="card-ico">📊</div><div><strong style="font-size:17px;color:white !important;">Transfer Destinations</strong><p style="margin:2px 0 0 0;font-size:12px;color:rgba(255,255,255,0.85) !important;">Where completed transfers are directed</p></div></div>', unsafe_allow_html=True)
    tc = k.get("tc",pd.Series())
    if not tc.empty:
        c1,c2 = st.columns(2)
        lo = dict(height=380, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                  font=dict(family='Inter',color='white'), margin=dict(t=40,b=20,l=20,r=20))
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
        <div class="highlight-box">
            <div class="hl-ico">🎯</div>
            <div>
                <div style="font-size:11px;font-weight:700;color:white !important;text-transform:uppercase;letter-spacing:0.8px;">Most Transferred To</div>
                <div style="font-size:22px;font-weight:900;color:white !important;margin-top:3px;">{k['dest']}</div>
                <div style="font-size:12px;color:rgba(255,255,255,0.85) !important;margin-top:2px;">{k['dest_n']} completed transfers directed here</div>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.info("No completed transfer data")
    st.markdown('</div>', unsafe_allow_html=True)

def view_agents(k):
    st.markdown('<div class="section-title"><div class="section-dot"></div> Agent Details</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;"><div class="card-ico">👤</div><div><strong style="font-size:17px;color:white !important;">Agent Performance</strong><p style="margin:2px 0 0 0;font-size:12px;color:rgba(255,255,255,0.85) !important;">Completed transfers only</p></div></div>', unsafe_allow_html=True)
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
            st.markdown(f'<p style="color:white !important;font-weight:700;margin-top:20px;margin-bottom:8px;">Recent Completed Transfers{lbl}</p>',unsafe_allow_html=True)
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
    st.markdown('<div class="section-title"><div class="section-dot"></div> Trend Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;"><div class="card-ico">📈</div><div><strong style="font-size:17px;color:white !important;">Time Series</strong><p style="margin:2px 0 0 0;font-size:12px;color:rgba(255,255,255,0.85) !important;">Completed transfer trends</p></div></div>', unsafe_allow_html=True)
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
                  font=dict(family='Inter',color='white'), margin=dict(t=40,b=40,l=40,r=20),
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
# MODE SELECTION UI
# ============================================================
def mode_selector():
    st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; min-height: 80vh;">
        <div style="text-align: center;">
            <h1 style="font-size: 48px; margin-bottom: 20px;">⚡ Sales Transfer Dashboard</h1>
            <p style="margin-bottom: 40px; font-size: 18px;">Select your access mode</p>
            <div style="display: flex; gap: 20px; justify-content: center;">
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👤 User Mode", use_container_width=True, key="user_main_btn"):
            st.session_state.view_mode = "user"
            st.session_state.authenticated = True
            st.rerun()
    with col2:
        if st.button("👑 Admin Mode", use_container_width=True, key="admin_main_btn"):
            st.session_state.pending_admin_auth = True
            st.rerun()
    
    st.markdown("""
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def admin_login_modal():
    st.markdown("""
    <div class="login-container">
        <h2>👑 Admin Access</h2>
        <p style="margin: 20px 0;">Enter password to access admin features</p>
    </div>
    """, unsafe_allow_html=True)
    
    password = st.text_input("Password:", type="password", key="admin_password_modal", placeholder="Enter admin password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Cancel", use_container_width=True):
            st.session_state.pending_admin_auth = False
            st.rerun()
    with col2:
        if st.button("Login", use_container_width=True):
            if password == "admin123":
                st.session_state.authenticated = True
                st.session_state.view_mode = "admin"
                st.session_state.pending_admin_auth = False
                st.rerun()
            else:
                st.error("Incorrect password")

# ============================================================
# MAIN
# ============================================================
def main():
    # Initialize session state
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "view_mode" not in st.session_state:
        st.session_state.view_mode = "user"
    if "pending_admin_auth" not in st.session_state:
        st.session_state.pending_admin_auth = False
    
    # Show mode selector if not authenticated
    if not st.session_state.authenticated and not st.session_state.pending_admin_auth:
        mode_selector()
        return
    
    # Show admin login modal if pending
    if st.session_state.pending_admin_auth:
        admin_login_modal()
        return
    
    # Load data
    with st.spinner("Connecting to Google Sheets..."):
        df = fetch_data()
    
    if df.empty:
        st.markdown("""
        <div class="warn-card">
            <h3 style="color:white !important;margin-top:0;">⚠️ No data available</h3>
            <p style="color:white !important;line-height:1.8;">
                <strong>Check:</strong><br>
                1. Google Sheet shared with service account<br>
                2. Data exists in "Form Responses 1"<br>
                3. Secrets configured in Streamlit Cloud
            </p>
        </div>""", unsafe_allow_html=True)
        time.sleep(45)
        st.rerun()
    
    if len(df) <= 1:
        st.warning("Sheet has only headers. Waiting for data...")
        time.sleep(45)
        st.rerun()
    
    # Calculate based on view mode
    if st.session_state.view_mode == "admin":
        k = calc(df, use_custom_range=True)
        view_admin_header()
    else:
        k = calc(df, use_custom_range=False)
        view_header()
    
    # Add mode switcher buttons at the top right
    st.markdown("""
    <style>
    .mode-buttons {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        display: flex;
        gap: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Mode switching buttons
    col1, col2, col3 = st.columns([6, 1, 1])
    with col2:
        if st.button("👤 User", key="switch_user", use_container_width=True):
            st.session_state.view_mode = "user"
            st.rerun()
    with col3:
        if st.button("👑 Admin", key="switch_admin", use_container_width=True):
            password = st.text_input("Admin Password:", type="password", key="switch_password", label_visibility="collapsed", placeholder="Enter password")
            if password == "admin123":
                st.session_state.view_mode = "admin"
                st.rerun()
            elif password:
                st.error("Wrong password")
    
    if not k:
        st.warning("No valid records found. Waiting...")
        time.sleep(45)
        st.rerun()
    
    # Summary banner
    st.markdown(f"""
    <div class="success-banner">
        ✅ Loaded <strong>{len(df)}</strong> records — <strong>{k.get('done', 0)} completed</strong> · 
        {k.get('failed', 0)} failed · {k.get('pend', 0)} pending
    </div>""", unsafe_allow_html=True)
    
    if st.session_state.view_mode == "admin":
        view_admin_kpis(k)
        view_failed_transfers(k)
        view_agent_success_rates(k)
        view_custom_period_performance(k)
        view_admin_transfers(k)
        view_performers(k)
        view_transfers(k)
        view_trends(k)
    else:
        view_kpis(k)
        view_status(k)
        view_performers(k)
        view_transfers(k)
        view_agents(k)
        view_trends(k)
    
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mode_text = "Admin Mode" if st.session_state.view_mode == "admin" else "User Mode"
    st.markdown(f"""
    <div class="footer-bar">
        🟢 {mode_text} &nbsp;&nbsp;·&nbsp;&nbsp; Last updated: {now} &nbsp;&nbsp;·&nbsp;&nbsp; Next refresh in 45s
    </div>""", unsafe_allow_html=True)
    
    time.sleep(45)
    st.rerun()

if __name__ == "__main__":
    main()
