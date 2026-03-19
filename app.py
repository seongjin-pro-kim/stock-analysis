"""GAP R-Zone 6.5 트레이딩 대시보드 — Streamlit (v2)"""
import streamlit as st
import pandas as pd
from sample_data import (
    get_sample_trades, get_sample_equity_curve,
    get_sample_positions, get_sample_signals,
    get_sample_signal_archive,
)

# ── 페이지 설정 ──────────────────────────────────────────
st.set_page_config(
    page_title="GAP R-Zone Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 다크 테마 CSS ────────────────────────────────────────
st.markdown("""
<style>
/* 전역 다크 스타일 */
[data-testid="stSidebar"] {
    background-color: #0d1117;
    border-right: 1px solid #1e2530;
}
.stApp { background-color: #0a0e14; }

/* KPI 카드 */
.kpi-card {
    background: #111820;
    border: 1px solid #1e2530;
    border-radius: 10px;
    padding: 16px 20px;
    text-align: left;
    position: relative;
}
.kpi-label { color: #7a8599; font-size: 12px; margin-bottom: 4px; }
.kpi-value { font-size: 22px; font-weight: 700; font-variant-numeric: tabular-nums; }
.kpi-sub { color: #7a8599; font-size: 11px; }
.positive { color: #22c55e; }
.negative { color: #ef4444; }
.neutral { color: #14b8a6; }

/* 결과 뱃지 */
.badge-win { background:#22c55e22; color:#22c55e; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:600; }
.badge-lose { background:#ef444422; color:#ef4444; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:600; }
.badge-progress { background:#eab30822; color:#eab308; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:600; }
.badge-ing { background:#3b82f622; color:#3b82f6; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:700; }
.badge-kospi { background:#3b82f622; color:#3b82f6; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:600; }
.badge-kosdaq { background:#8b5cf622; color:#a78bfa; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:600; }
.badge-nasdaq { background:#14b8a622; color:#14b8a6; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:600; }
.badge-btc { background:#eab30822; color:#eab308; padding:2px 8px; border-radius:4px; font-size:12px; font-weight:600; }

/* 하이라이트 열 (목표율/손익비/기대값) */
.highlight-cell { background: rgba(20,184,166,0.06); }

/* 섹션 헤더 */
.section-header { color: #e2e8f0; font-size: 15px; font-weight: 600; margin-bottom: 12px; }

/* 테이블 스타일 */
.dataframe { font-variant-numeric: tabular-nums !important; }
div[data-testid="stDataFrame"] { border: 1px solid #1e2530; border-radius: 8px; }

/* 사이드바 로고 */
.logo-box {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 0 16px 0; border-bottom: 1px solid #1e2530; margin-bottom: 16px;
}
.logo-icon { font-size: 28px; }
.logo-title { color: #e2e8f0; font-size: 16px; font-weight: 700; }
.logo-sub { color: #7a8599; font-size: 11px; }

/* metric 숨기기 (기본 스타일 덮어쓰기) */
[data-testid="stMetric"] { background: #111820; border: 1px solid #1e2530; border-radius: 10px; padding: 12px 16px; }

/* 툴팁 (마우스오버 프리뷰) */
.tooltip-wrapper { position: relative; display: inline-block; cursor: pointer; }
.tooltip-box {
    visibility: hidden; opacity: 0;
    position: absolute; z-index: 999;
    bottom: 110%; left: 50%; transform: translateX(-50%);
    background: #1a2233; border: 1px solid #2a3545;
    border-radius: 8px; padding: 12px 14px;
    min-width: 280px; max-width: 380px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
    font-size: 11px; color: #e2e8f0;
    transition: opacity 0.2s ease, visibility 0.2s ease;
    white-space: normal; line-height: 1.6;
}
.tooltip-wrapper:hover .tooltip-box { visibility: visible; opacity: 1; }

/* 정보 툴팁 아이콘 */
.info-tip {
    display: inline-flex; align-items: center; justify-content: center;
    width: 16px; height: 16px; border-radius: 50%;
    background: #1e2530; color: #7a8599; font-size: 10px;
    cursor: help; margin-left: 6px; font-weight: 700;
    border: 1px solid #2a3545;
}
.info-tip:hover + .info-content { visibility: visible; opacity: 1; }
.info-content {
    visibility: hidden; opacity: 0;
    position: absolute; z-index: 999;
    top: 28px; left: 0;
    background: #1a2233; border: 1px solid #2a3545;
    border-radius: 8px; padding: 12px 14px;
    min-width: 260px; max-width: 360px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
    font-size: 11px; color: #c0c8d8; line-height: 1.6;
    transition: opacity 0.2s ease, visibility 0.2s ease;
}

/* 달력 개선 */
.calendar-day { display:inline-flex; align-items:center; justify-content:center; width:28px; height:28px; border-radius:6px; font-size:11px; margin:1px; }
.cal-win { background:#22c55e33; color:#22c55e; font-weight:600; }
.cal-lose { background:#ef444433; color:#ef4444; font-weight:600; }
.cal-ing { background:#3b82f633; color:#3b82f6; font-weight:600; }
.cal-empty { background: transparent; color: #3a4555; }
</style>
""", unsafe_allow_html=True)


# ── Session State 초기화 ─────────────────────────────────
import os

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
if "equity_curve" not in st.session_state:
    st.session_state.equity_curve = get_sample_equity_curve()
if "positions" not in st.session_state:
    st.session_state.positions = get_sample_positions()
if "signals" not in st.session_state:
    st.session_state.signals = get_sample_signals()
if "signal_archive" not in st.session_state:
    st.session_state.signal_archive = get_sample_signal_archive()


# ── 사이드바 네비게이션 ──────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="logo-box">
        <span class="logo-icon">📈</span>
        <div>
            <div class="logo-title">GAP R-Zone</div>
            <div class="logo-sub">v6.5 Strategy</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "메뉴",
        ["🏠 메인 대시보드", "📊 매매 성과", "📋 매매 기록",
         "📡 시그널", "🌐 시장 개요", "🛡️ 리스크", "💾 데이터 관리"],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption("Created with Streamlit + Python")


# ── 공통 헬퍼 ────────────────────────────────────────────
from utils import fmt_krw, result_badge, market_badge


# ── 페이지 라우팅 ────────────────────────────────────────
from views import overview, performance, trade_log, signals, market, risk, data_mgmt

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
