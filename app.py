import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build

st.set_page_config(
    page_title="Sales Transfer Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS - Clean, targeted, no complex nested HTML
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp {
    background: #F8FAFC;
}

/* Animate everything on load */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(24px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeDown {
    from { opacity: 0; transform: translateY(-20px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes scaleIn {
    from { opacity: 0; transform: scale(0.92); }
    to   { opacity: 1; transform: scale(1); }
}
@keyframes slideRight {
    from { opacity: 0; transform: translateX(-30px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes barGrow {
    from { width: 0%; }
}
@keyframes countPop {
    0%   { opacity: 0; transform: scale(0.7) translateY(10px); }
    70%  { transform: scale(1.05) translateY(-2px); }
    100% { opacity: 1; transform: scale(1) translateY(0); }
}

/* Header */
.main-header {
    background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 50%, #06B6D4 100%);
    background-size: 200% 200%;
    animation: gradientShift 8s ease infinite, fadeDown 0.6s ease forwards;
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 24px;
    color: white;
    box-shadow: 0 12px 40px rgba(30, 58, 138, 0.3);
    position: relative;
    overflow: hidden;
}
.main-header::after {
    content: '';
    position: absolute;
    top: -60px; right: -40px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(255,255,255,0.08), transparent 60%);
    border-radius: 50%;
}
.main-header h1 {
    color: white !important;
    font-size: 28px; font-weight: 800;
    margin: 0; letter-spacing: -0.5px;
}
.main-header p {
    color: rgba(255,255,255,0.8) !important;
    font-size: 14px; margin: 4px 0 0 0;
}
.live-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 20px; padding: 4px 12px;
    font-size: 12px; color: rgba(255,255,255,0.9);
    margin-top: 10px;
}
.live-dot {
    width: 7px; height: 7px;
    background: #34D399; border-radius: 50%;
    animation: pulse 2s ease infinite;
    box-shadow: 0 0 6px rgba(52,211,153,0.6);
}

/* KPI metric cards */
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 20px 22px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: all 0.4s cubic-bezier(0.25,0.46,0.45,0.94);
    animation: fadeUp 0.5s ease forwards;
    position: relative;
    overflow: hidden;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(59,130,246,0.12);
    border-color: #93C5FD;
}
div[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #3B82F6, #06B6D4);
    transform: scaleX(0);
    transition: transform 0.4s ease;
    transform-origin: left;
}
div[data-testid="stMetric"]:hover::before {
    transform: scaleX(1);
}
div[data-testid="stMetric"] label {
    color: #64748B !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
}
div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    color: #1E3A8A !important;
    font-size: 34px !important;
    font-weight: 800 !important;
    animation: countPop 0.6s ease 0.3s both;
}
div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {
    font-size: 13px !important;
    font-weight: 600 !important;
}

/* Section headers */
.section-title {
    color: #1E3A8A;
    font-size: 20px; font-weight: 800;
    margin: 32px 0 16px 0;
    padding-bottom: 10px;
    border-bottom: 3px solid;
    border-image: linear-gradient(90deg, #3B82F6, #06B6D4, transparent) 1;
    animation: slideRight 0.5s ease forwards;
    letter-spacing: -0.3px;
}

/* Cards */
.glass-card {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    animation: fadeUp 0.5s ease forwards;
    transition: all 0.3s ease;
}
.glass-card:hover {
    box-shadow: 0 8px 24px rgba(0,0,0,0.06);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: #F1F5F9;
    border-radius: 12px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 10px;
    padding: 8px 20px;
    border: none !important;
    color: #64748B !important;
    font-weight: 600;
    font-size: 13px;
    transition: all 0.3s ease;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #3B82F6 !important;
    font-weight: 700;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

/* Dataframe */
.stDataFrame {
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid #E2E8F0 !important;
}

/* Selectbox */
.stSelectbox > div > div {
    border-radius: 10px !important;
    border-color: #E2E8F0 !important;
}

/* Status bar */
.footer-bar {
    margin-top: 32px;
    padding: 14px;
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    text-align: center;
    color: #64748B;
    font-size: 13px;
    animation: fadeUp 0.5s ease 0.8s both;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1E3A8A, #0F1D3A);
}
section[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.85) !important;
}

/* Remove branding */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# GOOGLE SHEETS
# ============================================================
@st.cache_resource(ttl=300)
def get_google_sheets_service():
    try:
        if 'gcp_service_account' in st.secrets:
            info = dict(st.secrets["gcp_service_account"])
        else:
            info = {
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
        creds = service_account.Credentials.from_service_account_info(
            info, scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        return build('sheets', 'v4', credentials=creds)
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

@st.cache_data(ttl=30)
def get_sheet_data():
    try:
        svc = get_google_sheets_service()
        if not svc:
            return pd.DataFrame()
        sid = st.secrets.get("spreadsheet_id", "19SvmVDtkIUkuLaQzy6szSgUSixHZVBohbyOxf0itD8I")
        result = svc.spreadsheets().values().get(
            spreadsheetId=sid, range="Form Responses 1"
        ).execute()
        values = result.get('values', [])
        if not values:
            return pd.DataFrame()
        headers = values[0]
        rows = [r[:len(headers)] + [None]*(len(headers)-len(r)) for r in values[1:]]
        df = pd.DataFrame(rows, columns=headers)
        if "Timestamp" in df.columns:
            for fmt in ["%m/%d/%Y %H:%M:%S","%Y-%m-%d %H:%M:%S","%d/%m/%Y %H:%M:%S","%m/%d/%Y %H:%M"]:
                try:
                    df["Timestamp"] = pd.to_datetime(df["Timestamp"], format=fmt)
                    break
                except: continue
            else:
                df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors='coerce')
        if "Status" in df.columns:
            df["Status"] = df["Status"].astype(str).str.strip().str.lower()
        for c in ["Timestamp","Agent Name","Transfer to:","Customer Name:","Electric Bill:","Credit Score:","Status","FeedBack","H comments"]:
            if c not in df.columns: df[c] = None
        return df
    except Exception as e:
        st.error(f"Fetch error: {e}")
        return pd.DataFrame()

# ============================================================
# DATE HELPERS
# ============================================================
def date_ranges():
    now = datetime.now()
    today_s = datetime(now.year, now.month, now.day)
    yest = now - timedelta(days=1)
    yest_s = datetime(yest.year, yest.month, yest.day)
    ws = now - timedelta(days=now.isoweekday()-1)
    ws = datetime(ws.year, ws.month, ws.day)
    lws = ws - timedelta(weeks=1)
    ms = datetime(now.year, now.month, 1)
    if now.month == 1:
        lms = datetime(now.year-1, 12, 1)
        lme = datetime(now.year, 1, 1)
    else:
        lms = datetime(now.year, now.month-1, 1)
        lme = ms
    return {
        "today": (today_s, today_s + timedelta(days=1)),
        "yesterday": (yest_s, yest_s + timedelta(days=1)),
        "week": (ws, ws + timedelta(days=7)),
        "last_week": (lws, lws + timedelta(days=7)),
        "month": (ms, datetime(now.year+1,1,1) if now.month==12 else datetime(now.year,now.month+1,1)),
        "last_month": (lms, lme),
    }

# ============================================================
# KPI CALCULATION - only "done" counts
# ============================================================
def calc_kpis(df):
    if df.empty: return {}
    df = df[df["Timestamp"].notna()].copy()
    if df.empty: return {}

    done = df[df["Status"] == "done"].copy()
    total = len(df)
    dn = len(done)
    pending = total - dn
    dr = date_ranges()

    def filt(data, key):
        s, e = dr[key]
        return data[(data["Timestamp"]>=s) & (data["Timestamp"]<e)]

    td = filt(done, "today")
    yd = filt(done, "yesterday")
    tw = filt(done, "week")
    lw = filt(done, "last_week")
    tm = filt(done, "month")
    lm = filt(done, "last_month")

    def pct(c, p): return ((c-p)/p*100) if p>0 else 0

    tc = done["Transfer to:"].value_counts() if "Transfer to:" in done.columns else pd.Series()
    ac = done["Agent Name"].value_counts() if "Agent Name" in done.columns else pd.Series()

    return {
        "total": total, "done": dn, "pending": pending,
        "rate": (dn/total*100) if total>0 else 0,
        "top_dest": tc.index[0] if not tc.empty else "N/A",
        "top_dest_n": int(tc.iloc[0]) if not tc.empty else 0,
        "tc": tc, "ac": ac,
        "ac_today": td["Agent Name"].value_counts() if "Agent Name" in td.columns else pd.Series(),
        "ac_week": tw["Agent Name"].value_counts() if "Agent Name" in tw.columns else pd.Series(),
        "ac_month": tm["Agent Name"].value_counts() if "Agent Name" in tm.columns else pd.Series(),
        "lowest": ac.idxmin() if len(ac)>1 else "N/A",
        "td": len(td), "yd": len(yd), "d_pct": pct(len(td),len(yd)),
        "tw": len(tw), "lw": len(lw), "w_pct": pct(len(tw),len(lw)),
        "tm": len(tm), "lm": len(lm), "m_pct": pct(len(tm),len(lm)),
        "full": df, "done_df": done,
        "today_df": td, "week_df": tw, "month_df": tm
    }

# ============================================================
# DISPLAY FUNCTIONS - using Streamlit native components
# ============================================================

def show_header():
    st.markdown(f"""
    <div class="main-header">
        <h1>📊 Sales Transfer Dashboard</h1>
        <p>Real-time monitoring — only completed (done) transfers counted</p>
        <div class="live-badge">
            <div class="live-dot"></div>
            Live · Auto-refresh 45s · {datetime.now().strftime("%b %d, %Y")}
        </div>
    </div>
    """, unsafe_allow_html=True)


def show_kpis(k):
    cols = st.columns(4)
    items = [
        ("✅ Completed Transfers", k["done"], f"{k['rate']:.1f}% rate · {k['pending']} pending"),
        ("📅 Today", k["td"], f"{k['d_pct']:+.1f}% vs yesterday ({k['yd']})"),
        ("📆 This Week", k["tw"], f"{k['w_pct']:+.1f}% vs last week ({k['lw']})"),
        ("🗓️ This Month", k["tm"], f"{k['m_pct']:+.1f}% vs last month ({k['lm']})"),
    ]
    for col, (label, val, delta) in zip(cols, items):
        with col:
            st.metric(label=label, value=f"{val:,}", delta=delta)


def show_status(k):
    st.markdown('<div class="section-title">📋 Status Overview</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("✅ Completed", k["done"])
    with c2:
        st.metric("⏳ Pending / Other", k["pending"])
    with c3:
        st.metric("📊 Completion Rate", f"{k['rate']:.1f}%")


def show_top_performers(k):
    st.markdown('<div class="section-title">🏆 Performance Analysis</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("**🏆 Top Performers** — Highest completed transfers")
        tab1, tab2, tab3 = st.tabs(["Today", "This Week", "This Month"])
        for tab, key in [(tab1,"ac_today"),(tab2,"ac_week"),(tab3,"ac_month")]:
            with tab:
                counts = k.get(key, pd.Series())
                if not counts.empty:
                    agent = counts.index[0]
                    cnt = int(counts.iloc[0])
                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg,#FFFBEB,#FEF3C7);border:1px solid #FDE68A;
                    border-radius:12px;padding:20px;margin:12px 0;animation:scaleIn 0.4s ease forwards;">
                        <div style="font-size:28px;margin-bottom:4px;">🥇</div>
                        <div style="font-size:20px;font-weight:800;color:#1E3A8A;">{agent}</div>
                        <div style="font-size:36px;font-weight:800;color:#D97706;margin:6px 0;animation:countPop 0.5s ease 0.2s both;">{cnt}</div>
                        <div style="font-size:13px;color:#64748B;">completed transfers</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("No completed transfers yet")
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("**📈 Agent Rankings** — All-time completed transfers")
        ac = k.get("ac", pd.Series())
        if not ac.empty:
            lowest = k.get("lowest", "")
            mx = ac.max()
            for i, (agent, cnt) in enumerate(ac.head(10).items(), 1):
                medals = {1:"🥇",2:"🥈",3:"🥉"}
                m = medals.get(i, f"<span style='color:#94A3B8;font-weight:700;'>{i}.</span>")
                bw = (cnt/mx*100) if mx>0 else 0
                is_low = agent == lowest and len(ac)>1
                bg = "rgba(239,68,68,0.06)" if is_low else "transparent"
                border_c = "rgba(239,68,68,0.2)" if is_low else "transparent"
                st.markdown(f"""
                <div style="display:flex;align-items:center;justify-content:space-between;
                padding:10px 14px;margin:6px 0;border-radius:10px;background:{bg};
                border:1px solid {border_c};animation:slideRight 0.4s ease {i*0.05}s both;
                transition:all 0.3s ease;"
                onmouseover="this.style.transform='translateX(4px)';this.style.boxShadow='0 4px 12px rgba(59,130,246,0.1)'"
                onmouseout="this.style.transform='none';this.style.boxShadow='none'">
                    <div style="flex:1;">
                        <div style="display:flex;align-items:center;gap:8px;">
                            <span style="font-size:16px;">{m}</span>
                            <span style="font-weight:700;color:#0F172A;font-size:14px;">{agent}</span>
                        </div>
                        <div style="background:#F1F5F9;border-radius:4px;height:5px;margin-top:6px;overflow:hidden;">
                            <div style="height:100%;width:{bw}%;border-radius:4px;
                            background:linear-gradient(90deg,#3B82F6,#06B6D4);
                            animation:barGrow 1s ease {i*0.05}s both;"></div>
                        </div>
                    </div>
                    <span style="color:#3B82F6;font-weight:800;font-size:18px;margin-left:12px;">{int(cnt)}</span>
                </div>
                """, unsafe_allow_html=True)
            if len(ac)>1:
                st.markdown(f"""
                <div style="margin-top:14px;padding:12px 16px;background:rgba(239,68,68,0.05);
                border:1px solid rgba(239,68,68,0.15);border-radius:10px;
                animation:fadeUp 0.4s ease 0.6s both;">
                    📉 <strong style="color:#EF4444;">Needs Support:</strong> {lowest} ({int(ac.min())} transfers)
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No agent data")
        st.markdown('</div>', unsafe_allow_html=True)


def show_transfer_analysis(k):
    st.markdown('<div class="section-title">📊 Transfer Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("**📊 Transfer Destination Analysis** — Where completed transfers are directed")

    tc = k.get("tc", pd.Series())
    if not tc.empty:
        c1, c2 = st.columns(2)
        lo = dict(height=380, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                  font=dict(family='Inter'), margin=dict(t=40,b=20,l=20,r=20))

        with c1:
            fig = px.pie(values=tc.values, names=tc.index, title="Distribution",
                         color_discrete_sequence=['#3B82F6','#06B6D4','#8B5CF6','#10B981','#F59E0B','#1E3A8A'])
            fig.update_layout(**lo)
            fig.update_traces(textposition='inside', textinfo='percent+label', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            tf = tc.reset_index()
            tf.columns = ['Destination','Count']
            tf = tf.sort_values('Count', ascending=True)
            fig = px.bar(tf, y='Destination', x='Count', title="By Destination",
                         orientation='h', color='Count',
                         color_continuous_scale=['#E2E8F0','#3B82F6'])
            fig.update_layout(**lo, coloraxis_showscale=False)
            st.plotly_chart(fig, use_container_width=True)

        # Most Transferred - clean and proper
        st.markdown(f"""
        <div style="margin-top:16px;padding:18px 22px;
        background:linear-gradient(135deg,rgba(59,130,246,0.06),rgba(6,182,212,0.06));
        border:1px solid rgba(59,130,246,0.15);border-radius:12px;
        display:flex;align-items:center;gap:14px;
        animation:scaleIn 0.5s ease 0.3s both;transition:all 0.3s ease;"
        onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 8px 20px rgba(59,130,246,0.1)'"
        onmouseout="this.style.transform='none';this.style.boxShadow='none'">
            <div style="width:48px;height:48px;background:linear-gradient(135deg,#3B82F6,#06B6D4);
            border-radius:12px;display:flex;align-items:center;justify-content:center;
            font-size:22px;box-shadow:0 6px 16px rgba(59,130,246,0.3);flex-shrink:0;">🎯</div>
            <div>
                <div style="font-size:11px;font-weight:700;color:#64748B;text-transform:uppercase;letter-spacing:0.8px;">Most Transferred To</div>
                <div style="font-size:20px;font-weight:800;color:#1E3A8A;margin-top:2px;">{k['top_dest']}</div>
                <div style="font-size:12px;color:#94A3B8;margin-top:1px;">{k['top_dest_n']} completed transfers</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No completed transfer data")
    st.markdown('</div>', unsafe_allow_html=True)


def show_agent_details(k):
    st.markdown('<div class="section-title">👤 Agent Details</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("**👤 Agent Performance** — Completed transfers only")

    ac = k.get("ac", pd.Series())
    if not ac.empty:
        names = sorted(ac.index.tolist())
        sel = st.selectbox("Select Agent:", ["All Agents"] + names, key="agent_sel")

        done_df = k.get("done_df", pd.DataFrame())
        filt = done_df if sel == "All Agents" else done_df[done_df["Agent Name"]==sel]

        td_df = k.get("today_df", pd.DataFrame())
        tw_df = k.get("week_df", pd.DataFrame())
        tm_df = k.get("month_df", pd.DataFrame())

        if sel != "All Agents":
            t = len(td_df[td_df["Agent Name"]==sel])
            w = len(tw_df[tw_df["Agent Name"]==sel])
            m = len(tm_df[tm_df["Agent Name"]==sel])
        else:
            t, w, m = k["td"], k["tw"], k["tm"]

        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1: st.metric("🎯 Total Done", len(filt))
        with mc2: st.metric("📅 Today", t)
        with mc3: st.metric("📆 This Week", w)
        with mc4: st.metric("🗓️ This Month", m)

        if not filt.empty:
            label = f" — {sel}" if sel != "All Agents" else ""
            st.markdown(f"**Recent Completed Transfers{label}**")
            avail = [c for c in ["Timestamp","Agent Name","Customer Name:","Transfer to:","Status","Electric Bill:","Credit Score:"] if c in filt.columns]
            if avail:
                recent = filt[avail].sort_values("Timestamp",ascending=False).head(10)
                show = recent.copy()
                if "Status" in show.columns:
                    show["Status"] = show["Status"].apply(lambda x: "✅ Done" if str(x).strip()=="done" else f"⏳ {str(x).title()}")
                st.dataframe(show, use_container_width=True, hide_index=True,
                    column_config={"Timestamp": st.column_config.DatetimeColumn("Timestamp", format="MM/DD/YYYY HH:mm")})
    else:
        st.info("No agent data")
    st.markdown('</div>', unsafe_allow_html=True)


def show_trends(k):
    st.markdown('<div class="section-title">📈 Trend Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("**📈 Time Series** — Completed transfer trends")

    done_df = k.get("done_df", pd.DataFrame())
    if not done_df.empty:
        df = done_df.copy()
        df['Date'] = df['Timestamp'].dt.date
        daily = df.groupby('Date').size().reset_index(name='Transfers')

        df['Week'] = df['Timestamp'].dt.isocalendar().week
        df['Year'] = df['Timestamp'].dt.year
        weekly = df.groupby(['Year','Week']).size().reset_index(name='Transfers')
        weekly['Label'] = weekly['Year'].astype(str)+'-W'+weekly['Week'].astype(str).str.zfill(2)

        df['Month'] = df['Timestamp'].dt.to_period('M')
        monthly = df.groupby('Month').size().reset_index(name='Transfers')
        monthly['Month'] = monthly['Month'].astype(str)

        lo = dict(height=380, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                  font=dict(family='Inter'), margin=dict(t=40,b=40,l=40,r=20),
                  xaxis=dict(gridcolor='#F1F5F9',zeroline=False), yaxis=dict(gridcolor='#F1F5F9',zeroline=False))

        t1, t2, t3 = st.tabs(["Daily","Weekly","Monthly"])
        with t1:
            if len(daily)>1:
                fig = px.area(daily,x='Date',y='Transfers',title="Daily Trend",markers=True)
                fig.update_traces(line_color='#3B82F6',fill='tozeroy',fillcolor='rgba(59,130,246,0.08)',
                    marker=dict(color='#06B6D4',size=7,line=dict(color='white',width=2)))
                fig.update_layout(**lo)
                st.plotly_chart(fig, use_container_width=True)
            else: st.info("Insufficient data")
        with t2:
            if len(weekly)>1:
                fig = px.bar(weekly,x='Label',y='Transfers',title="Weekly Trend",
                    color='Transfers',color_continuous_scale=['#E2E8F0','#3B82F6'])
                fig.update_layout(**lo,xaxis_tickangle=-45,coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)
            else: st.info("Insufficient data")
        with t3:
            if len(monthly)>1:
                fig = px.bar(monthly,x='Month',y='Transfers',title="Monthly Trend",
                    color='Transfers',color_continuous_scale=['#E2E8F0','#1E3A8A'])
                fig.update_layout(**lo,xaxis_tickangle=-45,coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)
            else: st.info("Insufficient data")
    else:
        st.info("No completed transfer data")
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# MAIN
# ============================================================
def main():
    show_header()

    with st.spinner("Loading data..."):
        df = get_sheet_data()

    if df.empty:
        st.warning("No data found. Check Google Sheet connection and secrets.")
        time.sleep(45); st.rerun()

    if len(df) <= 1:
        st.warning("Sheet has only headers. Waiting for data...")
        time.sleep(45); st.rerun()

    k = calc_kpis(df)
    if not k:
        st.warning("No valid records. Waiting...")
        time.sleep(45); st.rerun()

    st.success(f"✅ Loaded {len(df)} records — **{k['done']} completed** transfers counted · {k['pending']} pending")

    show_kpis(k)
    show_status(k)
    show_top_performers(k)
    show_transfer_analysis(k)
    show_agent_details(k)
    show_trends(k)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"""
    <div class="footer-bar">
        🟢 System Online &nbsp;|&nbsp; Last updated: {now} &nbsp;|&nbsp; Auto-refresh in 45s
    </div>
    """, unsafe_allow_html=True)

    time.sleep(45)
    st.rerun()

if __name__ == "__main__":
    main()
