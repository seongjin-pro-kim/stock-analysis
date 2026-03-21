"""GAP R-Zone 6.5 트레이딩 대시보드"""

import os
import sys
import streamlit as st
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from sample_data import (
    get_sample_trades,
    get_sample_equity_curve,
    get_sample_positions,
    get_sample_signals,
    get_sample_signal_archive,
)
from views.overview    import render as render_overview
from views.trade_log   import render as render_trade_log
from views.performance import render as render_performance
from views.risk        import render as render_risk
from views.signals     import render as render_signals
from views.market      import render as render_market

st.set_page_config(
    page_title="GAP R-Zone Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: 'Pretendard', 'Noto Sans KR', sans-serif;
    }
    .stApp {
        background: linear-gradient(180deg, #0a0e14 0%, #0f141b 100%);
        color: #e2e8f0;
    }
    [data-testid="stSidebar"] {
        background: #0a0e14;
        border-right: 1px solid #1e2530;
    }
    [data-testid="stSidebar"] * {
        color: #cbd5e1;
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }
    .stMarkdown, .stDataFrame, .stPlotlyChart, .stMetric, .element-container {
        margin-top: 1.5rem !important;
        margin-bottom: 1.5rem !important;
    }
    p, li, span, div, td, th, label {
        line-height: 1.4;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #d6dde8 !important;
        margin-top: 1.2rem !important;
        margin-bottom: 0.8rem !important;
        line-height: 1.2;
    }
    hr {
        margin: 1rem 0 !important;
        border-color: #1e2530 !important;
    }
    .stMetric {
        background: #0f141b;
        border: 1px solid #1e2530;
        border-radius: 12px;
        padding: 12px 14px;
    }
    .stMetric label {
        color: #7a8599 !important;
        font-size: 12px !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #e2e8f0 !important;
        font-size: 24px !important;
        font-weight: 700 !important;
    }
    .badge-win      { color:#8fbf8f; font-weight:700; }
    .badge-lose     { color:#c98a8a; font-weight:700; }
    .badge-ing      { color:#8aa7d6; font-weight:700; }
    .badge-progress { color:#a8a0c9; font-weight:700; }
    .badge-kospi, .badge-kosdaq, .badge-nasdaq, .badge-btc {
        padding: 2px 8px;
        border-radius: 999px;
        font-size: 10px;
        font-weight: 700;
        display: inline-block;
        filter: saturate(0.55) brightness(0.92);
    }
    .badge-kospi  { background:#1a2330; color:#aab6c9; }
    .badge-kosdaq { background:#241f2f; color:#b7b0c9; }
    .badge-nasdaq { background:#17302b; color:#a8c8c1; }
    .badge-btc    { background:#2f2a1b; color:#c9be92; }
    .table-wrap {
        background:#0a0e14;
        border:1px solid #1e2530;
        border-radius:12px;
        overflow-x:auto;
    }
    .table-dark {
        width:100%;
        border-collapse:collapse;
        white-space:nowrap;
        font-variant-numeric:tabular-nums;
        font-size:11px;
    }
    .table-dark thead tr {
        border-bottom:2px solid #1e2530;
        background:#111820;
    }
    .table-dark th {
        padding:7px 6px;
        color:#7a8599;
        font-size:10px;
        font-weight:600;
    }
    .table-dark td {
        padding:7px 6px;
        border-bottom:1px solid #1e2530;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

CSV_PATH = os.path.join(BASE_DIR, "csv_etc", "trades_enriched_v1.csv")

if "trades" not in st.session_state:
    if os.path.exists(CSV_PATH):
        st.session_state.trades = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
        if "date" in st.session_state.trades.columns:
            st.session_state.trades["date"] = pd.to_datetime(
                st.session_state.trades["date"], errors="coerce"
            )
        if "signal_date" in st.session_state.trades.columns:
            st.session_state.trades["signal_date"] = pd.to_datetime(
                st.session_state.trades["signal_date"], errors="coerce"
            )
    else:
        st.session_state.trades = get_sample_trades()

if "equity_curve"   not in st.session_state:
    st.session_state.equity_curve   = get_sample_equity_curve()
if "positions"      not in st.session_state:
    st.session_state.positions      = get_sample_positions()
if "signals"        not in st.session_state:
    st.session_state.signals        = get_sample_signals()
if "signal_archive" not in st.session_state:
    st.session_state.signal_archive = get_sample_signal_archive()

with st.sidebar:
    st.markdown("### ▸ Navigation")
    page = st.radio(
        "페이지",
        [
            "🏠 Overview",
            "📋 Trade Log",
            "📊 Performance",
            "⚠️ Risk",
            "📈 Signals",
            "🌍 Market",
        ],
        key="nav_page",
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption("GAP R-Zone 6.5")

if   page == "🏠 Overview":    render_overview()
elif page == "📋 Trade Log":   render_trade_log()
elif page == "📊 Performance": render_performance()
elif page == "⚠️ Risk":        render_risk()
elif page == "📈 Signals":     render_signals()
elif page == "🌍 Market":      render_market()
