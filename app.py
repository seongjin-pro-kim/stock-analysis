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

st.set_page_config(
    page_title="GAP R-Zone Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background-color: #0a0e14; }
    </style>
    """,
    unsafe_allow_html=True,
)

_CSV_PATH = os.path.join(os.path.dirname(__file__), "csv_etc", "trades_enriched_v1.csv")

if "trades" not in st.session_state:
    if os.path.exists(_CSV_PATH):
        st.session_state.trades = pd.read_csv(_CSV_PATH, encoding="utf-8-sig")
        if "date" in st.session_state.trades.columns:
            st.session_state.trades["date"] = pd.to_datetime(st.session_state.trades["date"])
        if "signal_date" in st.session_state.trades.columns:
            st.session_state.trades["signal_date"] = pd.to_datetime(
                st.session_state.trades["signal_date"], errors="coerce"
            )
    else:
        st.session_state.trades = get_sample_trades()

if "equitycurve" not in st.session_state:
    st.session_state.equitycurve = get_sample_equity_curve()

if "positions" not in st.session_state:
    st.session_state.positions = get_sample_positions()

if "signals" not in st.session_state:
    st.session_state.signals = get_sample_signals()

if "signal_archive" not in st.session_state:
    st.session_state.signal_archive = get_sample_signal_archive()

with st.sidebar:
    st.markdown("### GAP R-Zone")
    page = st.radio(
        "페이지",
        ["대시보드", "매매성과", "매매기록", "시그널", "시장개요", "리스크", "데이터관리"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption("Created with Streamlit")

if page == "대시보드":
    overview.render()
elif page == "매매성과":
    performance.render()
elif page == "매매기록":
    trade_log.render()
elif page == "시그널":
    signals.render()
elif page == "시장개요":
    market.render()
elif page == "리스크":
    risk.render()
elif page == "데이터관리":
    data_mgmt.render()
