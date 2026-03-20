"""GAP R-Zone 6.5 트레이딩 대시보드 — Streamlit"""
import streamlit as st
from sample_data import (
    get_sample_trades,
    get_sample_equity_curve,
    get_sample_positions,
    get_sample_signals,
)
from utils import setup_theme
from views import overview, performance, trade_log, signals, market, risk, data_mgmt

st.set_page_config(
    page_title="GAP R-Zone Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

setup_theme()

if "trades" not in st.session_state:
    st.session_state.trades = get_sample_trades()
if "equity_curve" not in st.session_state:
    st.session_state.equity_curve = get_sample_equity_curve()
if "positions" not in st.session_state:
    st.session_state.positions = get_sample_positions()
if "signals" not in st.session_state:
    st.session_state.signals = get_sample_signals()
if "signal_archive" not in st.session_state:
    st.session_state.signal_archive = []


with st.sidebar:
    st.markdown(
        '<div class="logo-box"><span class="logo-icon">📈</span><div><div class="logo-title">GAP R-Zone</div><div class="logo-sub">v6.5 Strategy</div></div></div>',
        unsafe_allow_html=True,
    )

    page = st.radio(
        "메뉴",
        ["🏠 메인 대시보드", "📊 매매 성과", "📋 매매 기록", "📡 시그널", "🌐 시장 개요", "🛡️ 리스크", "💾 데이터 관리"],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption("Created with Streamlit + Python")

if "메인 대시보드" in page:
    overview.render()
elif "매매 성과" in page:
    performance.render()
elif "매매 기록" in page:
    trade_log.render()
elif "시그널" in page:
    signals.render()
elif "시장 개요" in page:
    market.render()
elif "리스크" in page:
    risk.render()
elif "데이터 관리" in page:
    data_mgmt.render()
