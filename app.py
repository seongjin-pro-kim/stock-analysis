"""GAP R-Zone 6.5 트레이딩 대시보드 — Streamlit (v2)"""

import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from sample_data import (
    get_sample_trades,
    get_sample_equity_curve,
    get_sample_positions,
    get_sample_signals,
    get_sample_signal_archive,
)
from views import overview, performance, trade_log, signals, market, risk

st.set_page_config(
    page_title="GAP R-Zone Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #0b0f17 !important;
    color: #e5eefc !important;
}
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 1.5rem;
}
section[data-testid="stSidebar"] {
    background: #0a0e14;
    border-right: 1px solid #1d2530;
}
.badge-win{background:#22c55e22;color:#22c55e;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:600;}
.badge-lose{background:#ef444422;color:#ef4444;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:600;}
.badge-ing{background:#3b82f622;color:#3b82f6;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:700;}
.badge-progress{background:#14b8a622;color:#14b8a6;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:700;}
.badge-kospi{background:#3b82f622;color:#3b82f6;padding:1px 4px;border-radius:3px;font-size:9px;font-weight:600;}
.badge-kosdaq{background:#8b5cf622;color:#a78bfa;padding:1px 4px;border-radius:3px;font-size:9px;font-weight:600;}
.badge-nasdaq{background:#14b8a622;color:#14b8a6;padding:1px 4px;border-radius:3px;font-size:9px;font-weight:600;}
.badge-btc{background:#eab30822;color:#eab308;padding:1px 4px;border-radius:3px;font-size:9px;font-weight:600;}
</style>
""", unsafe_allow_html=True)

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

def init_state():
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

def df_state(key):
    v = st.session_state.get(key, [])
    return pd.DataFrame(v).copy() if not isinstance(v, pd.DataFrame) else v.copy()

init_state()

with st.sidebar:
    st.markdown("### 📈 GAP R-Zone")
    page = st.radio(
        "메뉴",
        ["메인 대시보드", "매매 성과 분석", "매매 기록", "시그널", "시장개요", "리스크", "데이터 관리"],
        index=0,
        label_visibility="collapsed",
    )
    st.caption("다크 테마 · hover 프리뷰 · 데이터 안정화")

def render_dashboard():
    st.markdown("### ▸ 메인 대시보드")

    trades = df_state("trades")
    signals_df = df_state("signals")
    archive = df_state("signal_archive")
    idx = df_state("major_indices")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총 매매", f"{len(trades)}건")
    c2.metric("진행중", f"{int((trades['result'] == '잉').sum()) if not trades.empty and 'result' in trades.columns else 0}건")
    c3.metric("시그널", f"{len(signals_df)}건")
    c4.metric("아카이브", f"{len(archive)}건")

    if not idx.empty and "date" in idx.columns:
        idx = idx.copy()
        idx["date"] = pd.to_datetime(idx["date"], errors="coerce")
        fig = go.Figure()
        colors = {"KOSPI": "#3b82f6", "KOSDAQ": "#a855f7", "NASDAQ": "#14b8a6", "S&P500": "#f59e0b"}
        for name, color in colors.items():
            if name in idx.columns:
                fig.add_trace(go.Scatter(
                    x=idx["date"], y=idx[name], name=name, mode="lines",
                    line=dict(width=2, color=color),
                    hovertemplate=f"{name}: %{{y:.2f}}<extra></extra>"
                ))
        fig.update_layout(
            template="plotly_dark",
            hovermode="x unified",
            height=320,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="#0a0e14",
            plot_bgcolor="#0a0e14",
            legend=dict(orientation="h", y=1.08),
        )
        st.plotly_chart(fig, use_container_width=True)

    if not archive.empty:
        st.markdown("#### ▸ Signal Archive")
        st.dataframe(archive, use_container_width=True, hide_index=True)

if page == "메인 대시보드":
    render_dashboard()
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
    st.markdown("### ▸ 데이터 관리")
    st.info("데이터 관리 페이지는 현재 별도 구현이 없습니다.")
