import streamlit as st
import pandas as pd
from utils import init_state, df_state
import plotly.io as pio

def init_state():
    defaults = {
        "trades": [],
        "equity_curve": [],
        "positions": [],
        "signals": [],
        "signal_archive": [],
        "major_indices": [],
        "risk_metrics": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def df_state(key):
    v = st.session_state.get(key, [])
    return pd.DataFrame(v).copy() if not isinstance(v, pd.DataFrame) else v.copy()


DARK_AIRY_PALETTE = [
    "#3B82F6", "#4F86FF", "#5B8CFF", "#6A94FF", "#7A9BFF",
    "#8AA3FF", "#9AAAFE", "#A9B2FE", "#B7BAFF", "#C4C2FF",
]

MA_COLORS = {
    "MA5": "#ff5fa2",
    "MA20": "#0f3b7a",
    "MA40": "#0f5d3f",
    "MA60": "#6b4f2a",
    "MA120": "#d97706",
}

def setup_theme():
    if "gap_dark" not in pio.templates:
        pio.templates["gap_dark"] = pio.templates["plotly_dark"].layout.template
        pio.templates["gap_dark"].layout.colorway = DARK_AIRY_PALETTE
    pio.templates.default = "gap_dark"

    st.markdown("""
    <style>
    :root {
        --bg: #0a0e14;
        --panel: #111820;
        --line: #1e2530;
        --text: #e2e8f0;
        --muted: #7a8599;
    }
    .stApp { background-color: var(--bg); }
    .block-container { padding-top: 2rem !important; padding-bottom: 1.2rem !important; }
    section.main > div,
    div[data-testid="stVerticalBlock"],
    div[data-testid="stHorizontalBlock"] { gap: 0.75rem; }
    [data-testid="column"] { padding-left: 0.35rem; padding-right: 0.35rem; }
    [data-testid="stSidebar"] {
        background-color: #0d1117;
        border-right: 1px solid var(--line);
    }
    div[data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 8px;
        overflow: hidden;
        margin-top: 0.35rem;
        margin-bottom: 0.35rem;
    }
    [data-testid="stPlotlyChart"] {
        border: 1px solid var(--line);
        border-radius: 10px;
        overflow: hidden;
        background: linear-gradient(180deg, #101722 0%, #0b111a 100%);
        box-shadow: 0 6px 18px rgba(0,0,0,0.18);
    }
    .kpi-card {
        background: linear-gradient(180deg, #121b26 0%, #0f1620 100%);
        border: 1px solid var(--line);
        border-radius: 12px;
        padding: 16px 18px;
        text-align: left;
        box-shadow: 0 6px 20px rgba(0,0,0,0.18);
    }
    .kpi-label { color: var(--muted); font-size: 12px; margin-bottom: 4px; }
    .kpi-value { font-size: 22px; font-weight: 700; font-variant-numeric: tabular-nums; }
    .kpi-sub { color: var(--muted); font-size: 11px; }
    .positive { color: #2dd4bf; }
    .negative { color: #fb7185; }
    .neutral { color: #60a5fa; }
    .logo-box {
        display: flex; align-items: center; gap: 10px;
        padding: 8px 0 16px 0; border-bottom: 1px solid var(--line); margin-bottom: 16px;
    }
    .logo-icon { font-size: 28px; }
    .logo-title { color: var(--text); font-size: 16px; font-weight: 700; }
    .logo-sub { color: var(--muted); font-size: 11px; }
    [data-testid="stMetric"] {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 10px;
        padding: 12px 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }
    div[data-testid="stDataFrame"] table,
    div[data-testid="stDataFrame"] th,
    div[data-testid="stDataFrame"] td {
        font-size: 1.7em !important;
    }
    </style>
    """, unsafe_allow_html=True)

def fmt_krw(v):
    return f"₩{v:,.0f}"

def result_badge(result):
    if result == "승":
        return '<span class="badge-win">승</span>'
    if result == "패":
        return '<span class="badge-lose">패</span>'
    return '<span class="badge-progress">중</span>'

def market_badge(market):
    m = str(market).upper()
    if "KOSPI" in m:
        return '<span class="badge-kospi">KOSPI</span>'
    if "KOSDAQ" in m:
        return '<span class="badge-kosdaq">KOSDAQ</span>'
    return f'<span class="badge-progress">{market}</span>'
