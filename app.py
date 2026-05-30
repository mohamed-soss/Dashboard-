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
    initial_sidebar_state="expanded"
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
#neural-canvas {
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    z-index: 0;
    pointer-events: none;
}
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
@keyframes ripple {
    to { transform: scale(2.5); opacity: 0; }
}
@keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}
@keyframes shakeX {
    0%, 100% { transform: translateX(0); }
    20% { transform: translateX(-6px); }
    40% { transform: translateX(6px); }
    60% { transform: translateX(-4px); }
    80% { transform: translateX(4px); }
}
/* ==================== ADMIN LOGIN ==================== */
.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 80vh;
    animation: fadeUp 0.8s cubic-bezier(0.16,1,0.3,1) forwards;
}
.login-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
    backdrop-filter: blur(24px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 24px;
    padding: 48px 44px;
    width: 100%;
    max-width: 420px;
    box-shadow: 0 24px 80px rgba(0,0,0,0.5), 0 0 120px rgba(79,70,229,0.1);
    position: relative;
    overflow: hidden;
}
.login-card::before {
    content: '';
    position: absolute;
    top: -60%; right: -30%;
    width: 350px; height: 350px;
    background: radial-gradient(circle, rgba(129,140,248,0.12), transparent 60%);
    border-radius: 50%;
    animation: float 7s ease infinite;
}
.login-card::after {
    content: '';
    position: absolute;
    bottom: -50%; left: -20%;
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(6,182,212,0.08), transparent 60%);
    border-radius: 50%;
    animation: float 9s ease infinite reverse;
}
.login-ico {
    width: 68px; height: 68px;
    background: linear-gradient(135deg, var(--primary), var(--accent));
    border-radius: 18px;
    display: flex; align-items: center; justify-content: center;
    font-size: 32px;
    box-shadow: 0 12px 32px rgba(79,70,229,0.35);
    margin: 0 auto 20px auto;
    position: relative; z-index: 2;
    animation: glow 3s ease infinite;
}
.login-title {
    text-align: center;
    font-size: 26px; font-weight: 900;
    letter-spacing: -1px;
    margin-bottom: 6px;
    position: relative; z-index: 2;
}
.login-sub {
    text-align: center;
    font-size: 13px;
    color: rgba(255,255,255,0.6) !important;
    margin-bottom: 28px;
    position: relative; z-index: 2;
}
.login-error {
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.25);
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 16px;
    text-align: center;
    font-size: 13px;
    animation: shakeX 0.5s ease;
    position: relative; z-index: 2;
}
.login-error span {
    color: #FCA5A5 !important;
}
/* ==================== ADMIN HEADER ==================== */
.admin-header {
    background: linear-gradient(135deg, #1a0a2e 0%, #2d1b4e 30%, #4F46E5 60%, #EF4444 100%);
    background-size: 300% 300%;
    animation: gradientShift 10s ease infinite, fadeDown 0.8s cubic-bezier(0.16,1,0.3,1) forwards;
    border-radius: 20px;
    padding: 32px 40px;
    margin-bottom: 28px;
    color: white;
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(239,68,68,0.2);
    box-shadow: 0 20px 60px rgba(0,0,0,0.4), 0 0 80px rgba(239,68,68,0.1);
}
.admin-header::before {
    content: '';
    position: absolute;
    top: -50%; right: -10%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(239,68,68,0.12), transparent 60%);
    border-radius: 50%;
    animation: float 6s ease infinite;
}
.admin-header h1 {
    color: white !important;
    font-size: 30px; font-weight: 900;
    margin: 0; letter-spacing: -1px;
    position: relative; z-index: 2;
}
.admin-header p {
    color: rgba(255,255,255,0.9) !important;
    font-size: 14px; margin: 6px 0 0 0;
    position: relative; z-index: 2;
}
.admin-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(239,68,68,0.2);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(239,68,68,0.3);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 12px; color: white !important;
    font-weight: 700;
    animation: pulse 2s ease infinite;
}
/* ==================== ADMIN FAILED CARDS ==================== */
.failed-card {
    background: linear-gradient(135deg, rgba(239,68,68,0.08), rgba(239,68,68,0.02));
    border: 1px solid rgba(239,68,68,0.15);
    border-radius: 16px;
    padding: 22px;
    margin: 10px 0;
    transition: all 0.4s cubic-bezier(0.16,1,0.3,1);
    animation: fadeUp 0.6s cubic-bezier(0.16,1,0.3,1) forwards;
    position: relative;
    overflow: hidden;
}
.failed-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #EF4444, #F59E0B, #EF4444);
    transform: scaleX(0);
    transition: transform 0.5s ease;
    transform-origin: left;
}
.failed-card:hover::before { transform: scaleX(1); }
.failed-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 16px 40px rgba(239,68,68,0.12);
    border-color: rgba(239,68,68,0.3);
}
.failed-card .f-agent {
    font-size: 16px; font-weight: 800;
    color: white !important;
    margin-bottom: 4px;
}
.failed-card .f-count {
    font-size: 36px; font-weight: 900;
    color: #FCA5A5 !important;
    letter-spacing: -1.5px;
    animation: countPop 0.7s cubic-bezier(0.16,1,0.3,1) 0.3s both;
}
.failed-card .f-label {
    font-size: 11px; font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: rgba(255,255,255,0.5) !important;
    margin-top: 2px;
}
.failed-detail-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 14px;
    margin: 5px 0;
    border-radius: 10px;
    background: rgba(239,68,68,0.04);
    border: 1px solid rgba(239,68,68,0.08);
    transition: all 0.3s ease;
    animation: slideRight 0.5s cubic-bezier(0.16,1,0.3,1) forwards;
}
.failed-detail-row:hover {
    background: rgba(239,68,68,0.08);
    border-color: rgba(239,68,68,0.2);
    transform: translateX(4px);
}
.failed-bar-track {
    background: rgba(235,68,68,0.1);
    border-radius: 4px; height: 5px;
    margin-top: 5px; overflow: hidden;
}
.failed-bar-fill {
    height: 100%; border-radius: 4px;
    background: linear-gradient(90deg, #EF4444, #F59E0B);
    animation: barGrow 1.2s cubic-bezier(0.16,1,0.3,1) forwards;
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
.section-dot-red {
    background: #EF4444;
    box-shadow: 0 0 12px rgba(239,68,68,0.4);
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
.card-ico-red {
    background: linear-gradient(135deg, #EF4444, #DC2626);
    box-shadow: 0 8px 20px rgba(239,68,68,0.3);
}
.glass-card:hover .card-ico-red {
    box-shadow: 0 12px 28px rgba(239,68,68,0.4);
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
.s-rate {
    background: linear-gradient(135deg, rgba(79,70,229,0.1), rgba(79,70,229,0.05));
    border: 1px solid rgba(79,70,229,0.2);
}
.s-failed {
    background: linear-gradient(135deg, rgba(239,68,68,0.1), rgba(239,68,68,0.05));
    border: 1px solid rgba(239,68,68,0.2);
}
.s-ico { font-size: 30px; margin-bottom: 8px; }
.s-val {
    font-size: 34px; font-weight: 900;
    letter-spacing: -1px;
    animation: countPop 0.7s cubic-bezier(0.16,1,0.3,1) 0.4s both;
}
.s-done .s-val, .s-pending .s-val, .s-rate .s-val, .s-failed .s-val { color: white !important; }
.s-lbl {
    font-size: 12px; font-weight: 600;
    margin-top: 4px;
}
.s-done .s-lbl, .s-pending .s-lbl, .s-rate .s-lbl, .s-failed .s-lbl { color: white !important; }
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
.admin-banner {
    background: linear-gradient(135deg, rgba(239,68,68,0.08), rgba(239,68,68,0.03));
    border: 1px solid rgba(239,68,68,0.15);
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
/* ==================== SIDEBAR ==================== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F0D2E 0%, #0A0E27 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}
section[data-testid="stSidebar"] * {
    color: white !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: white !important;
}
/* ==================== LOGOUT BUTTON ==================== */
.logout-btn {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(239,68,68,0.12);
    border: 1px solid rgba(239,68,68,0.25);
    border-radius: 10px;
    padding: 8px 20px;
    font-size: 13px; font-weight: 700;
    cursor: pointer;
    transition: all 0.3s ease;
}
.logout-btn:hover {
    background: rgba(239,68,68,0.2);
    transform: translateY(-2px);
}
/* ==================== MISC ==================== */
#MainMenu, footer, header { visibility: hidden !important; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--primary); }
.js-plotly-plot .plotly .bg { fill: transparent !important; }
p, span, label, div, td, th, li, a, h1, h2, h3, h4, h5, h6, strong, em, b, i, small {
    color: white !important;
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
# SESSION STATE INIT
# ============================================================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False
if "login_attempt" not in st.session_state:
    st.session_state.login_attempt = False

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

def calc(df, multiplier=1):
    if df.empty: return {}
    df = df[df["Timestamp"].notna()].copy()
    if df.empty: return {}
    done = df[df["Status"]=="done"].copy()
    failed = df[df["Status"]=="failed"].copy()
    not_done = df[df["Status"]!="done"].copy()
    total = len(df)
    dn = len(done)
    fl = len(failed)
    pend = len(not_done)
    r = ranges()
    def f(d,k):
        s,e = r[k]; return d[(d["Timestamp"]>=s)&(d["Timestamp"]<e)]
    td=f(done,"today"); yd=f(done,"yest")
    tw=f(done,"week"); lw=f(done,"lweek")
    tm=f(done,"month"); lm=f(done,"lmonth")
    fl_t=f(failed,"today"); fl_w=f(failed,"week"); fl_m=f(failed,"month")
    def pc(a,b): return ((a-b)/b*100) if b>0 else 0
    tc = done["Transfer to:"].value_counts() if "Transfer to:" in done.columns else pd.Series()
    ac = done["Agent Name"].value_counts() if "Agent Name" in done.columns else pd.Series()
    # Failed by agent
    fc = failed["Agent Name"].value_counts() if "Agent Name" in failed.columns else pd.Series()
    fc_t = fl_t["Agent Name"].value_counts() if "Agent Name" in fl_t.columns else pd.Series()
    fc_w = fl_w["Agent Name"].value_counts() if "Agent Name" in fl_w.columns else pd.Series()
    fc_m = fl_m["Agent Name"].value_counts() if "Agent Name" in fl_m.columns else pd.Series()
    # Apply multiplier for admin
    return {
        "total":total,
        "done":dn * multiplier,
        "done_raw":dn,
        "pend":pend,
        "failed":fl * multiplier,
        "failed_raw":fl,
        "rate":(dn/total*100) if total>0 else 0,
        "dest":tc.index[0] if not tc.empty else "N/A",
        "dest_n":int(tc.iloc[0]) * multiplier if not tc.empty else 0,
        "tc":tc * multiplier if not tc.empty else tc,
        "tc_raw":tc,
        "ac":ac * multiplier if not tc.empty else ac,
        "ac_raw":ac,
        "fc":fc * multiplier if not fc.empty else fc,
        "fc_raw":fc,
        "ac_t":td["Agent Name"].value_counts() * multiplier if "Agent Name" in td.columns and not td.empty else pd.Series(),
        "ac_t_raw":td["Agent Name"].value_counts() if "Agent Name" in td.columns else pd.Series(),
        "ac_w":tw["Agent Name"].value_counts() * multiplier if "Agent Name" in tw.columns and not tw.empty else pd.Series(),
        "ac_w_raw":tw["Agent Name"].value_counts() if "Agent Name" in tw.columns else pd.Series(),
        "ac_m":tm["Agent Name"].value_counts() * multiplier if "Agent Name" in tm.columns and not tm.empty else pd.Series(),
        "ac_m_raw":tm["Agent Name"].value_counts() if "Agent Name" in tm.columns else pd.Series(),
        "fc_t":fc_t * multiplier if not fc_t.empty else fc_t,
        "fc_t_raw":fc_t,
        "fc_w":fc_w * multiplier if not fc_w.empty else fc_w,
        "fc_w_raw":fc_w,
        "fc_m":fc_m * multiplier if not fc_m.empty else fc_m,
        "fc_m_raw":fc_m,
        "low":ac.idxmin() if len(ac)>1 else "N/A",
        "td":len(td)*multiplier,"yd":len(yd)*multiplier,"dp":pc(len(td),len(yd)),
        "tw":len(tw)*multiplier,"lw":len(lw)*multiplier,"wp":pc(len(tw),len(lw)),
        "tm":len(tm)*multiplier,"lm":len(lm)*multiplier,"mp":pc(len(tm),len(lm)),
        "fl_t":len(fl_t)*multiplier,"fl_w":len(fl_w)*multiplier,"fl_m":len(fl_m)*multiplier,
        "td_raw":len(td),"yd_raw":len(yd),"tw_raw":len(tw),"lw_raw":len(lw),
        "tm_raw":len(tm),"lm_raw":len(lm),"fl_t_raw":len(fl_t),"fl_w_raw":len(fl_w),"fl_m_raw":len(fl_m),
        "full":df,"done_df":done,"failed_df":failed,
        "tdf":td,"wdf":tw,"mdf":tm,
    }

# ============================================================
# ADMIN LOGIN VIEW
# ============================================================
def view_login():
    st.markdown("""
    <div class="login-container">
        <div class="login-card">
            <div class="login-ico">🔐</div>
            <div class="login-title">Admin Access</div>
            <div class="login-sub">Enter your credentials to view the admin dashboard</div>
    """, unsafe_allow_html=True)

    if st.session_state.login_attempt:
        st.markdown("""
        <div class="login-error">
            <span>Invalid password. Please try again.</span>
        </div>
        """, unsafe_allow_html=True)

    password = st.text_input("Password", type="password", key="admin_pw",
                              placeholder="Enter admin password...")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔓 Sign In", use_container_width=True, key="login_btn"):
            if password == "admin123":
                st.session_state.is_admin = True
                st.session_state.login_attempt = False
                st.rerun()
            else:
                st.session_state.login_attempt = True
                st.rerun()

    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-top:40px;animation:fadeUp 0.8s ease 0.3s both;">
        <p style="color:rgba(255,255,255,0.4) !important;font-size:12px;">
            Not an admin? The main dashboard is always available to everyone.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# SHARED VIEWS
# ============================================================
def view_header(is_admin=False):
    if is_admin:
        st.markdown(f"""
        <div class="admin-header">
            <h1>🛡️ Admin Dashboard</h1>
            <p>Admin view — sales counted at 10x · Failed transfers visible · Full management access</p>
            <div class="header-badges">
                <div class="admin-badge">⚡ ADMIN MODE</div>
                <div class="h-badge"><div class="live-dot"></div> Live</div>
                <div class="h-badge">🔄 Auto-refresh 45s</div>
                <div class="h-badge">📅 {datetime.now().strftime("%b %d, %Y %H:%M")}</div>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
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

def view_kpis(k, is_admin=False):
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("✅ Completed Transfers", f"{k['done']:,}", f"{k['rate']:.1f}% rate · {k['pend']} pending")
    with c2: st.metric("📅 Today", f"{k['td']:,}", f"{k['dp']:+.1f}% vs yesterday ({k['yd']})")
    with c3: st.metric("📆 This Week", f"{k['tw']:,}", f"{k['wp']:+.1f}% vs last week ({k['lw']})")
    with c4: st.metric("🗓️ This Month", f"{k['tm']:,}", f"{k['mp']:+.1f}% vs last month ({k['lm']})")
    if is_admin:
        c5,c6,c7,c8 = st.columns(4)
        with c5: st.metric("❌ Total Failed", f"{k['failed']:,}", f"Raw: {k['failed_raw']}")
        with c6: st.metric("❌ Failed Today", f"{k['fl_t']:,}", f"Raw: {k['fl_t_raw']}")
        with c7: st.metric("❌ Failed This Week", f"{k['fl_w']:,}", f"Raw: {k['fl_w_raw']}")
        with c8: st.metric("❌ Failed This Month", f"{k['fl_m']:,}", f"Raw: {k['fl_m_raw']}")

def view_status(k, is_admin=False):
    st.markdown('<div class="section-title"><div class="section-dot"></div> Status Overview</div>', unsafe_allow_html=True)
    grid_html = f"""
    <div class="glass-card">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
            <div class="card-ico">📋</div>
            <div>
                <strong style="font-size:17px;color:white !important;">Transfer Status Breakdown</strong>
                <p style="margin:2px 0 0 0;font-size:12px;color:rgba(255,255,255,0.85) !important;">{"Admin: counts at 10x · " if is_admin else ""}Only "done" entries count as completed</p>
            </div>
        </div>
        <div class="status-grid">
            <div class="s-card s-done">
                <div class="s-ico">✅</div>
                <div class="s-val">{k['done']}</div>
                <div class="s-lbl">Completed{" (10x)" if is_admin else ""}</div>
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
        </div>"""
    if is_admin:
        grid_html += f"""
        <div class="status-grid" style="margin-top:12px;">
            <div class="s-card s-failed">
                <div class="s-ico">❌</div>
                <div class="s-val">{k['failed']}</div>
                <div class="s-lbl">Failed (10x)</div>
            </div>
            <div class="s-card s-pending">
                <div class="s-ico">📈</div>
                <div class="s-val">{k['total']}</div>
                <div class="s-lbl">Total Records</div>
            </div>
            <div class="s-card s-done">
                <div class="s-ico">🔢</div>
                <div class="s-val">{k['done_raw']}</div>
                <div class="s-lbl">Done (Raw Count)</div>
            </div>
        </div>"""
    grid_html += "</div>"
    st.markdown(grid_html, unsafe_allow_html=True)

# ============================================================
# ADMIN: FAILED TRANSFERS VIEW
# ============================================================
def view_failed_transfers(k):
    st.markdown('<div class="section-title"><div class="section-dot section-dot-red"></div> Failed Transfers by Agent</div>', unsafe_allow_html=True)
    fc = k.get("fc_raw", pd.Series())
    if fc.empty:
        st.markdown("""
        <div class="glass-card" style="text-align:center;padding:40px;">
            <div style="font-size:48px;margin-bottom:12px;">🎉</div>
            <strong style="font-size:18px;color:white !important;">No Failed Transfers</strong>
            <p style="color:rgba(255,255,255,0.6) !important;font-size:13px;margin-top:6px;">All transfers have been completed successfully</p>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown(f"""
    <div class="glass-card">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
            <div class="card-ico card-ico-red">❌</div>
            <div>
                <strong style="font-size:17px;color:white !important;">Failed Transfer Breakdown</strong>
                <p style="margin:2px 0 0 0;font-size:12px;color:rgba(255,255,255,0.85) !important;">Raw count per agent — transfers that were not marked "done"</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    mx = fc.max()

    # Tabs for time periods
    t1, t2, t3, t4 = st.tabs(["All Time", "Today", "This Week", "This Month"])
    tabs_data = [
        (t1, fc, k.get("fc", pd.Series())),
        (t2, k.get("fc_t_raw", pd.Series()), k.get("fc_t", pd.Series())),
        (t3, k.get("fc_w_raw", pd.Series()), k.get("fc_w", pd.Series())),
        (t4, k.get("fc_m_raw", pd.Series()), k.get("fc_m", pd.Series())),
    ]
    for tab, raw_data, scaled_data in tabs_data:
        with tab:
            if raw_data.empty:
                st.markdown("""
                <div style="text-align:center;padding:30px;">
                    <span style="font-size:32px;">✅</span>
                    <p style="color:rgba(255,255,255,0.5) !important;font-size:13px;margin-top:8px;">No failed transfers in this period</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                for i, (agent, cnt) in enumerate(raw_data.items(), 1):
                    scaled = int(scaled_data.get(agent, 0)) if not scaled_data.empty else int(cnt) * 10
                    bw = (cnt / mx * 100) if mx > 0 else 0
                    medal = {1: "🔴", 2: "🟠", 3: "🟡"}.get(i, "")
                    st.markdown(f"""
                    <div class="failed-detail-row" style="animation-delay:{i*0.07}s;">
                        <div style="flex:1;">
                            <div style="display:flex;align-items:center;gap:8px;">
                                <span style="font-size:14px;">{medal}</span>
                                <span style="font-weight:700;color:white !important;font-size:14px;">{agent}</span>
                            </div>
                            <div class="failed-bar-track">
                                <div class="failed-bar-fill" style="width:{bw}%;animation-delay:{i*0.07}s;"></div>
                            </div>
                        </div>
                        <div style="text-align:right;margin-left:16px;">
                            <span style="color:#FCA5A5 !important;font-weight:800;font-size:20px;">{scaled}</span>
                            <span style="color:rgba(255,255,255,0.4) !important;font-size:10px;display:block;">(raw: {int(cnt)})</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Summary highlight
                worst = raw_data.index[0]
                worst_cnt = int(raw_data.iloc[0])
                st.markdown(f"""
                <div class="insight-box insight-danger" style="margin-top:16px;">
                    <span style="font-size:22px;">⚠️</span>
                    <div>
                        <strong style="color:white !important;font-size:12px;">Most Failed</strong>
                        <p style="margin:2px 0 0 0;font-size:13px;color:white !important;">
                            {worst} has {worst_cnt} failed transfer{"s" if worst_cnt != 1 else ""} — may need attention
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Failed vs Done comparison chart
    st.markdown("---")
    st.markdown('<p style="color:white !important;font-weight:800;font-size:16px;margin-bottom:12px;">📊 Failed vs Completed by Agent</p>', unsafe_allow_html=True)

    ac = k.get("ac_raw", pd.Series())
    if not ac.empty and not fc.empty:
        all_agents = sorted(set(ac.index.tolist() + fc.index.tolist()))
        comp_data = []
        for agent in all_agents:
            comp_data.append({
                "Agent": agent,
                "Completed": int(ac.get(agent, 0)),
                "Failed": int(fc.get(agent, 0)),
            })
        comp_df = pd.DataFrame(comp_data)
        comp_melted = comp_df.melt(id_vars="Agent", var_name="Type", value_name="Count")

        fig = px.bar(comp_melted, x="Agent", y="Count", color="Type",
                     barmode="group",
                     color_discrete_map={"Completed": "#10B981", "Failed": "#EF4444"},
                     title="Completed vs Failed by Agent (Raw)")
        fig.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='white'),
            margin=dict(t=40, b=40, l=40, r=20),
            xaxis=dict(gridcolor='rgba(255,255,255,0.04)', zeroline=False),
            yaxis=dict(gridcolor='rgba(255,255,255,0.04)', zeroline=False),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

        # Success rate per agent
        st.markdown('<p style="color:white !important;font-weight:800;font-size:16px;margin-bottom:12px;">📈 Agent Success Rate</p>', unsafe_allow_html=True)
        rate_data = []
        for agent in all_agents:
            c = int(ac.get(agent, 0))
            f_cnt = int(fc.get(agent, 0))
            total_agent = c + f_cnt
            rate = (c / total_agent * 100) if total_agent > 0 else 0
            rate_data.append({"Agent": agent, "Success Rate %": round(rate, 1), "Total": total_agent})
        rate_df = pd.DataFrame(rate_data).sort_values("Success Rate %", ascending=True)
        fig2 = px.bar(rate_df, y="Agent", x="Success Rate %", orientation="h",
                      color="Success Rate %",
                      color_continuous_scale=["#EF4444", "#F59E0B", "#10B981"],
                      range_color=[0, 100],
                      title="Success Rate per Agent (%)")
        fig2.update_layout(
            height=350,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='white'),
            margin=dict(t=40, b=20, l=20, r=20),
            xaxis=dict(gridcolor='rgba(255,255,255,0.04)', zeroline=False, range=[0, 105]),
            yaxis=dict(gridcolor='rgba(255,255,255,0.04)', zeroline=False),
            coloraxis_showscale=False,
        )
        fig2.update_traces(marker_line_width=0, texttemplate='%{x:.1f}%', textposition='outside')
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# PERFORMERS
# ============================================================
def view_performers(k, is_admin=False):
    suffix = " (10x)" if is_admin else ""
    st.markdown('<div class="section-title"><div class="section-dot"></div> Performance Analysis</div>', unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;"><div class="card-ico">🏆</div><div><strong style="font-size:17px;color:white !important;">Top Performers{suffix}</strong><p style="margin:2px 0 0 0;font-size:12px;color:rgba(255,255,255,0.85) !important;">Highest completed transfers</p></div></div>', unsafe_allow_html=True)
        t1,t2,t3 = st.tabs(["Today","This Week","This Month"])
        for tab,key,raw_key in [(t1,"ac_t","ac_t_raw"),(t2,"ac_w","ac_w_raw"),(t3,"ac_m","ac_m_raw")]:
            with tab:
                counts = k.get(key,pd.Series())
                raw_counts = k.get(raw_key, pd.Series())
                if not counts.empty:
                    ag = counts.index[0]; cnt = int(counts.iloc[0])
                    raw_cnt = int(raw_counts.iloc[0]) if not raw_counts.empty else cnt
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
                            <span style="font-size:13px;color:rgba(255,255,255,0.85) !important;">completed transfers{" (raw: " + str(raw_cnt) + ")" if is_admin else ""}</span>
                        </div>
                    </div>""", unsafe_allow_html=True)
                else:
                    st.info("No completed transfers yet")
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;"><div class="card-ico">📈</div><div><strong style="font-size:17px;color:white !important;">Agent Rankings{suffix}</strong><p style="margin:2px 0 0 0;font-size:12px;color:rgba(255,255,255,0.85) !important;">All-time completed transfers</p></div></div>', unsafe_allow_html=True)
        ac = k.get("ac",pd.Series())
        ac_raw = k.get("ac_raw", pd.Series())
        if not ac.empty:
            low = k.get("low",""); mx = ac.max()
            for i,(ag,cnt) in enumerate(ac.head(10).items(),1):
                raw_val = int(ac_raw.get(ag, 0)) if not ac_raw.empty else int(cnt)
                m = {1:"🥇",2:"🥈",3:"🥉"}.get(i,f'<span style="color:white !important;font-weight:700;">{i}.</span>')
                bw = (cnt/mx*100) if mx>0 else 0
                is_low = ag==low and len(ac)>1
                raw_suffix = f' <span style="font-size:10px;color:rgba(255,255,255,0.4) !important;">(raw:{raw_val})</span>' if is_admin else ""
                st.markdown(f"""
                <div class="rank-row {"rank-low" if is_low else ""}" style="animation-delay:{i*0.06}s;">
                    <div style="flex:1;">
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span style="font-size:16px;">{m}</span>
                            <span style="font-weight:700;color:white !important;font-size:14px;">{ag}</span>
                        </div>
                        <div class="bar-track"><div class="bar-fill" style="width:{bw}%;animation-delay:{i*0.06}s;"></div></div>
                    </div>
                    <span style="color:white !important;font-weight:800;font-size:18px;margin-left:12px;">{int(cnt)}{raw_suffix}</span>
                </div>""", unsafe_allow_html=True)
            if len(ac)>1:
                st.markdown(f"""
                <div class="insight-box insight-danger">
                    <span style="font-size:22px;">📉</span>
                    <div><strong style="color:white !important;font-size:12px;">Needs Support</strong>
                    <p style="margin:2px 0 0 0;font-size:13px;color:white !important;">{low} ({int(ac.min())} transfers{" · raw: " + str(int(ac_raw.min())) if is_admin else ""})</p></div>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No agent data")
        st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# TRANSFERS
# ============================================================
def view_transfers(k, is_admin=False):
    suffix = " (10x)" if is_admin else ""
    st.markdown('<div class="section-title"><div class="section-dot"></div> Transfer Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;"><div class="card-ico">📊</div><div><strong style="font-size:17px;color:white !important;">Transfer Destinations{suffix}</strong><p style="margin:2px 0 0 0;font-size:12px;color:rgba(255,255,255,0.85) !important;">Where completed transfers are directed</p></div></div>', unsafe_allow_html=True)
    tc = k.get("tc",pd.Series())
    tc_raw = k.get("tc_raw", pd.Series())
    if not tc.empty:
        c1,c2 = st.columns(2)
        lo = dict(height=380, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                  font=dict(family='Inter',color='white'), margin=dict(t=40,b=20,l=20,r=20))
        with c1:
            plot_tc = tc_raw if is_admin and not tc_raw.empty else tc
            fig = px.pie(values=plot_tc.values,names=plot_tc.index,title=f"Distribution{' (Raw)' if is_admin else ''}",
                color_discrete_sequence=['#4F46E5','#06B6D4','#8B5CF6','#10B981','#F59E0B','#312E81'])
            fig.update_layout(**lo)
            fig.update_traces(textposition='inside',textinfo='percent+label',hole=0.45,
                marker=dict(line=dict(color='#0A0E27',width=2)))
            st.plotly_chart(fig,use_container_width=True)
        with c2:
            plot_tc2 = tc_raw if is_admin and not tc_raw.empty else tc
            tf = plot_tc2.reset_index(); tf.columns = ['Destination','Count']
            tf = tf.sort_values('Count',ascending=True)
            fig = px.bar(tf,y='Destination',x='Count',title=f"By Destination{' (Raw)' if is_admin else ''}",orientation='h',
                color='Count',color_continuous_scale=['rgba(255,255,255,0.05)','#4F46E5'])
            fig.update_layout(**lo,coloraxis_showscale=False)
            fig.update_traces(marker_line_width=0)
            st.plotly_chart(fig,use_container_width=True)
        dest_raw = int(tc_raw.iloc[0]) if not tc_raw.empty else k['dest_n']
        st.markdown(f"""
        <div class="highlight-box">
            <div class="hl-ico">🎯</div>
            <div>
                <div style="font-size:11px;font-weight:700;color:white !important;text-transform:uppercase;letter-spacing:0.8px;">Most Transferred To</div>
                <div style="font-size:22px;font-weight:900;color:white !important;margin-top:3px;">{k['dest']}</div>
                <div style="font-size:12px;color:rgba(255,255,255,0.85) !important;margin-top:2px;">{k['dest_n']} completed transfers{" · raw: " + str(dest_raw) if is_admin else ""}</div>
            </div>
        </div>""", unsafe_allow_html=True)
    else:
        st.info("No completed transfer data")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================
# AGENTS
# ============================================================
def view_agents(k, is_admin=False):
    suffix = " (10x)" if is_admin else ""
    st.markdown('<div class="section-title"><div class="section-dot"></div> Agent Details</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;"><div class="card-ico">👤</div><div><strong style="font-size:17px;color:white !important;">Agent Performance{suffix}</strong><p style="margin:2px 0 0 0;font-size:12px;color:rgba(255,255,255,0.85) !important;">Completed transfers only</p></div></div>', unsafe_allow_html=True)
    ac = k.get("ac_raw",pd.Series())
    fc_raw = k.get("fc_raw", pd.Series())
    if not ac.empty:
        names = sorted(set(ac.index.tolist() + (fc_raw.index.tolist() if not fc_raw.empty else [])))
        sel = st.selectbox("Select Agent:",["All Agents"]+names,key="asel")
        dd = k.get("done_df",pd.DataFrame())
        fd = k.get("failed_df",pd.DataFrame())
        if sel == "All Agents":
            filt = dd
            filt_fail = fd
            t,w,m = k["td"],k["tw"],k["tm"]
            t_raw,w_raw,m_raw = k["td_raw"],k["tw_raw"],k["tm_raw"]
        else:
            filt = dd[dd["Agent Name"]==sel]
            filt_fail = fd[fd["Agent Name"]==sel]
            tdf,wdf,mdf = k["tdf"],k["wdf"],k["mdf"]
            t = len(tdf[tdf["Agent Name"]==sel]) * (10 if is_admin else 1)
            w = len(wdf[wdf["Agent Name"]==sel]) * (10 if is_admin else 1)
            m = len(mdf[mdf["Agent Name"]==sel]) * (10 if is_admin else 1)
            t_raw = len(tdf[tdf["Agent Name"]==sel])
            w_raw = len(wdf[wdf["Agent Name"]==sel])
            m_raw = len(mdf[mdf["Agent Name"]==sel])

        mc1,mc2,mc3,mc4 = st.columns(4)
        done_val = len(filt) * (10 if is_admin else 1)
        fail_val = len(filt_fail) * (10 if is_admin else 1)
        with mc1: st.metric("🎯 Total Done", f"{done_val}", f"raw: {len(filt)}" if is_admin else None)
        with mc2: st.metric("📅 Today", f"{t}", f"raw: {t_raw}" if is_admin else None)
        with mc3: st.metric("📆 This Week", f"{w}", f"raw: {w_raw}" if is_admin else None)
        with mc4: st.metric("🗓️ This Month", f"{m}", f"raw: {m_raw}" if is_admin else None)

        if is_admin:
            mc5, mc6 = st.columns(2)
            with mc5:
                st.metric("❌ Total Failed", f"{fail_val}", f"raw: {len(filt_fail)}")
            with mc6:
                fail_rate = (len(filt_fail) / (len(filt) + len(filt_fail)) * 100) if (len(filt) + len(filt_fail)) > 0 else 0
                st.metric("⚠️ Failure Rate", f"{fail_rate:.1f}%", f"{len(filt_fail)} of {len(filt)+len(filt_fail)} total")

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

        # Show failed records in admin
        if is_admin and not filt_fail.empty:
            st.markdown(f'<p style="color:white !important;font-weight:700;margin-top:20px;margin-bottom:8px;">Recent Failed Transfers{lbl}</p>', unsafe_allow_html=True)
            avail_f = [c for c in ["Timestamp","Agent Name","Customer Name:","Transfer to:","Status","Electric Bill:","Credit Score:","FeedBack","H comments"] if c in filt_fail.columns]
            if avail_f:
                recent_f = filt_fail[avail_f].sort_values("Timestamp",ascending=False).head(10)
                show_f = recent_f.copy()
                if "Status" in show_f.columns:
                    show_f["Status"] = show_f["Status"].apply(lambda x: "❌ Failed" if str(x).strip()=="failed" else f"⏳ {str(x).title()}")
                st.dataframe(show_f,use_container_width=True,hide_index=True,
                    column_config={"Timestamp":st.column_config.DatetimeColumn("Timestamp",format="MM/DD/YYYY HH:mm")})
    else:
        st.info("No agent data")
    st.markdown('</div>',unsafe_allow_html=True)

# ============================================================
# TRENDS
# ============================================================
def view_trends(k, is_admin=False):
    suffix = " (10x)" if is_admin else ""
    st.markdown('<div class="section-title"><div class="section-dot"></div> Trend Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;"><div class="card-ico">📈</div><div><strong style="font-size:17px;color:white !important;">Time Series{suffix}</strong><p style="margin:2px 0 0 0;font-size:12px;color:rgba(255,255,255,0.85) !important;">Completed transfer trends</p></div></div>', unsafe_allow_html=True)
    dd = k.get("done_df",pd.DataFrame())
    fd = k.get("failed_df", pd.DataFrame())
    mult = 10 if is_admin else 1
    if not dd.empty:
        df = dd.copy()
        df['Date'] = df['Timestamp'].dt.date
        daily = df.groupby('Date').size().reset_index(name='Transfers')
        daily['Transfers'] = daily['Transfers'] * mult
        df['Wk'] = df['Timestamp'].dt.isocalendar().week
        df['Yr'] = df['Timestamp'].dt.year
        weekly = df.groupby(['Yr','Wk']).size().reset_index(name='Transfers')
        weekly['Transfers'] = weekly['Transfers'] * mult
        weekly['Lbl'] = weekly['Yr'].astype(str)+'-W'+weekly['Wk'].astype(str).str.zfill(2)
        df['Mo'] = df['Timestamp'].dt.to_period('M')
        monthly = df.groupby('Mo').size().reset_index(name='Transfers')
        monthly['Transfers'] = monthly['Transfers'] * mult
        monthly['Mo'] = monthly['Mo'].astype(str)
        lo = dict(height=380, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                  font=dict(family='Inter',color='white'), margin=dict(t=40,b=40,l=40,r=20),
                  xaxis=dict(gridcolor='rgba(255,255,255,0.04)',zeroline=False),
                  yaxis=dict(gridcolor='rgba(255,255,255,0.04)',zeroline=False))
        t1,t2,t3 = st.tabs(["Daily","Weekly","Monthly"])
        with t1:
            if len(daily)>1:
                fig = px.area(daily,x='Date',y='Transfers',title=f"Daily Trend{suffix}",markers=True)
                fig.update_traces(line_color='#818CF8',fill='tozeroy',fillcolor='rgba(79,70,229,0.08)',
                    marker=dict(color='#06B6D4',size=8,line=dict(color='#0A0E27',width=2)))
                fig.update_layout(**lo); st.plotly_chart(fig,use_container_width=True)
            else: st.info("Insufficient data")
        with t2:
            if len(weekly)>1:
                fig = px.bar(weekly,x='Lbl',y='Transfers',title=f"Weekly Trend{suffix}",
                    color='Transfers',color_continuous_scale=['rgba(255,255,255,0.03)','#4F46E5'])
                fig.update_layout(**lo,xaxis_tickangle=-45,coloraxis_showscale=False)
                fig.update_traces(marker_line_width=0)
                st.plotly_chart(fig,use_container_width=True)
            else: st.info("Insufficient data")
        with t3:
            if len(monthly)>1:
                fig = px.bar(monthly,x='Mo',y='Transfers',title=f"Monthly Trend{suffix}",
                    color='Transfers',color_continuous_scale=['rgba(255,255,255,0.03)','#312E81'])
                fig.update_layout(**lo,xaxis_tickangle=-45,coloraxis_showscale=False)
                fig.update_traces(marker_line_width=0)
                st.plotly_chart(fig,use_container_width=True)
            else: st.info("Insufficient data")

        # Admin: overlay failed trend
        if is_admin and not fd.empty:
            st.markdown("---")
            st.markdown('<p style="color:white !important;font-weight:800;font-size:16px;margin-bottom:12px;">❌ Failed Transfer Trend (Daily)</p>', unsafe_allow_html=True)
            fdf = fd.copy()
            fdf['Date'] = fdf['Timestamp'].dt.date
            f_daily = fdf.groupby('Date').size().reset_index(name='Failed')
            if len(f_daily) > 0:
                fig_fail = px.bar(f_daily, x='Date', y='Failed', title="Daily Failed Transfers (Raw)",
                                  color='Failed', color_continuous_scale=['rgba(255,255,255,0.03)','#EF4444'])
                fig_fail.update_layout(**lo, coloraxis_showscale=False)
                fig_fail.update_traces(marker_line_width=0)
                st.plotly_chart(fig_fail, use_container_width=True)
    else:
        st.info("No completed transfer data")
    st.markdown('</div>',unsafe_allow_html=True)

# ============================================================
# MAIN
# ============================================================
def main():
    # Sidebar: Login/Logout
    with st.sidebar:
        st.markdown("### 🔑 Access Control")
        if st.session_state.is_admin:
            st.markdown("""
            <div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.2);
                        border-radius:12px;padding:14px;margin-bottom:16px;text-align:center;">
                <span style="font-size:28px;">🛡️</span><br>
                <strong style="color:white !important;font-size:15px;">Admin Mode Active</strong><br>
                <span style="color:rgba(255,255,255,0.6) !important;font-size:11px;">10x sales counting · Failed transfers visible</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
                st.session_state.is_admin = False
                st.rerun()
        else:
            st.markdown("""
            <div style="background:rgba(79,70,229,0.1);border:1px solid rgba(79,70,229,0.2);
                        border-radius:12px;padding:14px;margin-bottom:16px;text-align:center;">
                <span style="font-size:28px;">👁️</span><br>
                <strong style="color:white !important;font-size:15px;">Standard View</strong><br>
                <span style="color:rgba(255,255,255,0.6) !important;font-size:11px;">Real counts · Basic metrics</span>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🔐 Admin Login", use_container_width=True, key="admin_login_sidebar"):
                st.session_state.show_login = True
                st.rerun()

        st.markdown("---")
        st.markdown(f"""
        <div style="text-align:center;padding:10px;">
            <p style="color:rgba(255,255,255,0.3) !important;font-size:11px;">
                {'🛡️ Admin' if st.session_state.is_admin else '👁️ Standard'} View<br>
                Last refresh: {datetime.now().strftime("%H:%M:%S")}
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Show login page if requested
    if st.session_state.get("show_login", False) and not st.session_state.is_admin:
        view_login()
        return

    # Fetch data
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
        time.sleep(45); st.rerun()

    if len(df) <= 1:
        st.warning("Sheet has only headers. Waiting for data...")
        time.sleep(45); st.rerun()

    is_admin = st.session_state.is_admin
    multiplier = 10 if is_admin else 1
    k = calc(df, multiplier=multiplier)

    if not k:
        st.warning("No valid records found. Waiting...")
        time.sleep(45); st.rerun()

    # Admin banner
    if is_admin:
        st.markdown(f"""
        <div class="success-banner admin-banner">
            🛡️ <strong>ADMIN MODE</strong> — Loaded <strong>{len(df)}</strong> records ·
            Sales at <strong>10x</strong> (done: {k['done']:,} = raw {k['done_raw']:,} × 10) ·
            Failed: <strong>{k['failed']:,}</strong> (raw {k['failed_raw']:,} × 10)
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="success-banner">
            ✅ Loaded <strong>{len(df)}</strong> records — <strong>{k['done']} completed</strong> transfers counted · {k['pend']} pending
        </div>""", unsafe_allow_html=True)

    view_header(is_admin)
    view_kpis(k, is_admin)
    view_status(k, is_admin)
    view_performers(k, is_admin)
    view_transfers(k, is_admin)

    # Admin-only: Failed transfers section
    if is_admin:
        view_failed_transfers(k)

    view_agents(k, is_admin)
    view_trends(k, is_admin)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mode = "🛡️ Admin" if is_admin else "🟢 System"
    st.markdown(f"""
    <div class="footer-bar">
        {mode} Online &nbsp;&nbsp;·&nbsp;&nbsp; Last updated: {now} &nbsp;&nbsp;·&nbsp;&nbsp; Next refresh in 45s
    </div>""", unsafe_allow_html=True)
    time.sleep(45)
    st.rerun()

if __name__ == "__main__":
    main()
