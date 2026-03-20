"""GAP R-Zone 6.5 트레이딩 대시보드 — Streamlit (v2)"""

import os
import streamlit as st
import pandas as pd

from sample_data import (
    get_sample_trades,
    get_sample_equity_curve,
    get_sample_positions,
    get_sample_signals,
    get_sample_signal_archive,
)
from views import overview, performance, trade_log, signals, market, risk, data_mgmt
from utils import init_state, df_state

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
        background-color: #0b0f17 !important;
        color: #e5eefc !important;
    }
    .block-container {
        padding-top: 1.1rem;
        padding-bottom: 1.5rem;
    }
    section[data-testid="stSidebar"] {
        background: #0a0e14;
        border-right: 1px solid #1d2530;
    }
    .stMetric {
        background:#0f141b;
        border:1px solid #1e2530;
        border-radius:12px;
        padding:10px 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def _load_trades():
    csv_path = os.path.join(os.path.dirname(__file__), "csv_etc", "trades_enriched_v1.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path, encoding="utf-8-sig")
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        if "signal_date" in df.columns:
            df["signal_date"] = pd.to_datetime(df["signal_date"], errors="coerce")
        return df
    return get_sample_trades()

def _init_state():
    if "trades" not in st.session_state:
        st.session_state.trades = _load_trades()
    if "equity_curve" not in st.session_state:
        st.session_state.equity_curve = get_sample_equity_curve()
    if "positions" not in st.session_state:
        st.session_state.positions = get_sample_positions()
    if "signals" not in st.session_state:
        st.session_state.signals = get_sample_signals()
    if "signal_archive" not in st.session_state:
        st.session_state.signal_archive = get_sample_signal_archive()
    if "major_indices" not in st.session_state:
        st.session_state.major_indices = []
    if "risk_metrics" not in st.session_state:
        st.session_state.risk_metrics = {}

_init_state()

with st.sidebar:
    st.markdown("### 📈 GAP R-Zone")
    page = st.radio(
        "메뉴",
        ["메인 대시보드", "매매 성과 분석", "매매 기록", "시그널", "시장개요", "리스크", "데이터 관리"],
        index=0,
        label_visibility="collapsed",
    )
    st.caption("다크 테마 · hover 프리뷰 · 데이터 안정화")

if page == "메인 대시보드":
    overview.render()
elif page == "매매 성과 분석":
    performance.render()
elif page == "매매 기록":
    trade_log.render()
elif page == "시그널":
    signals.render()
elif page == "시장개요":
    market.render()
elif page == "리스크":
    risk.render()
elif page == "데이터 관리":
    data_mgmt.render()
