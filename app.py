"""GAP R-Zone 6.5 트레이딩 대시보드 — Streamlit (final integrated app.py)"""

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
from utils import result_badge, market_badge, fmt_date_short, archive_result_badge

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

    /* 섹션 간격만 넓힘 */
    .stMarkdown, .stDataFrame, .stPlotlyChart, .stMetric, .element-container {
        margin-top: 1.5rem !important;
        margin-bottom: 1.5rem !important;
    }

    /* 행간은 원래대로 */
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

    .badge-win { color:#8fbf8f; font-weight:700; }
    .badge-lose { color:#c98a8a; font-weight:700; }
    .badge-ing { color:#8aa7d6; font-weight:700; }
    .badge-progress { color:#a8a0c9; font-weight:700; }

    .badge-kospi, .badge-kosdaq, .badge-nasdaq, .badge-btc {
        padding: 2px 8px;
        border-radius: 999px;
        font-size: 10px;
        font-weight: 700;
        display: inline-block;
        filter: saturate(0.55) brightness(0.92);
    }
    .badge-kospi { background:#1a2330; color:#aab6c9; }
    .badge-kosdaq { background:#241f2f; color:#b7b0c9; }
    .badge-nasdaq { background:#17302b; color:#a8c8c1; }
    .badge-btc { background:#2f2a1b; color:#c9be92; }

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

CSV_PATH = os.path.join(os.path.dirname(__file__), "csv_etc", "trades_enriched_v1.csv")

if "trades" not in st.session_state:
    if os.path.exists(CSV_PATH):
        st.session_state.trades = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
        if "date" in st.session_state.trades.columns:
            st.session_state.trades["date"] = pd.to_datetime(st.session_state.trades["date"], errors="coerce")
        if "signal_date" in st.session_state.trades.columns:
            st.session_state.trades["signal_date"] = pd.to_datetime(st.session_state.trades["signal_date"], errors="coerce")
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


def _safe_num(x, default=0.0):
    try:
        if pd.isna(x):
            return default
        return float(x)
    except Exception:
        return default


def _safe_int(x, default=0):
    try:
        if pd.isna(x):
            return default
        return int(x)
    except Exception:
        return default


def panel(title, value, delta=None, color="#e2e8f0"):
    extra = ""
    if delta is not None:
        extra = f'<div style="margin-top:4px;color:{color};font-size:12px;font-weight:600;">{delta}</div>'
    return f"""
    <div style="background:#0f141b;border:1px solid #1e2530;border-radius:12px;padding:14px 14px 12px 14px;">
        <div style="color:#7a8599;font-size:12px;margin-bottom:6px;">{title}</div>
        <div style="color:#e2e8f0;font-size:28px;font-weight:700;line-height:1;">{value}</div>
        {extra}
    </div>
    """


with st.sidebar:
    st.markdown("### 📌 Navigation")
    page = st.radio(
        "페이지",
        ["🏠 Overview", "📋 Trade Log", "📊 Performance", "⚠️ Risk", "📈 Signals", "🌍 Market"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption("GAP R-Zone 6.5")

st.markdown(f"## {page}")

trades = st.session_state.trades.copy()
equity = st.session_state.equity_curve.copy()
positions = st.session_state.positions.copy()
signals = st.session_state.signals.copy()
signal_archive = st.session_state.signal_archive.copy()

if "date" in trades.columns:
    trades["date"] = pd.to_datetime(trades["date"], errors="coerce")
if "date" in equity.columns:
    equity["date"] = pd.to_datetime(equity["date"], errors="coerce")
if "signal_date" in signal_archive.columns:
    signal_archive["signal_date"] = pd.to_datetime(signal_archive["signal_date"], errors="coerce")
if "date" in signals.columns:
    signals["date"] = pd.to_datetime(signals["date"], errors="coerce")

if page == "🏠 Overview":
    st.markdown("#### ▸ 주요 시장 지표")
    idx_configs = [
        {"name": "KOSPI", "value": 2685.42, "change": 12.35, "color": "#3b82f6"},
        {"name": "KOSDAQ", "value": 872.15, "change": -3.21, "color": "#a855f7"},
        {"name": "NASDAQ", "value": 18245.80, "change": 85.50, "color": "#14b8a6"},
        {"name": "BTC", "value": 87420.50, "change": 1250.30, "color": "#eab308"},
    ]
    cols = st.columns(4)
    for c, cfg in zip(cols, idx_configs):
        sign = "+" if cfg["change"] >= 0 else ""
        if cfg["name"] == "BTC":
            value = f"${cfg['value']:,.1f}"
            delta = f"{sign}${cfg['change']:,.1f}"
        elif cfg["name"] == "NASDAQ":
            value = f"{cfg['value']:,.2f}"
            delta = f"{sign}{cfg['change']:,.2f}"
        else:
            value = f"{cfg['value']:,.2f}"
            delta = f"{sign}{cfg['change']:.2f}"
        c.markdown(panel(cfg["name"], value, delta, cfg["color"]), unsafe_allow_html=True)

    st.markdown("#### ▸ 핵심 KPI")
    total = len(trades)
    win_cnt = int((trades["result"] == "승").sum()) if "result" in trades.columns else 0
    lose_cnt = int((trades["result"] == "패").sum()) if "result" in trades.columns else 0
    ing_cnt = int((trades["result"] == "잉").sum()) if "result" in trades.columns else 0
    win_rate = (win_cnt / max(win_cnt + lose_cnt, 1)) * 100 if (win_cnt + lose_cnt) else 0
    rr_avg = _safe_num(trades["rr_ratio"].mean()) if "rr_ratio" in trades.columns else 0.0
    ev_avg = _safe_num(trades["expected_value"].mean()) if "expected_value" in trades.columns else 0.0

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("총 매매", f"{total}건")
    k2.metric("승/패", f"{win_cnt}/{lose_cnt}")
    k3.metric("진행중", f"{ing_cnt}건")
    k4.metric("승률", f"{win_rate:.1f}%")
    k5.metric("RR 평균", f"{rr_avg:.2f}")
    k6.metric("기대값", f"{ev_avg:.1f}")

    st.markdown("#### ▸ 최근 매매")
    if not trades.empty:
        recent = trades.copy()
        if "date" in recent.columns:
            recent = recent.sort_values("date", ascending=False).head(8)

        rows = []
        for _, r in recent.iterrows():
            rows.append(
                "<tr>"
                f"<td style='padding:6px 6px;text-align:center;'>{market_badge(r.get('market',''))}</td>"
                f"<td style='padding:6px 6px;color:#7a8599;text-align:center;font-size:10px;'>{fmt_date_short(r.get('date'))}</td>"
                f"<td style='padding:6px 6px;color:#e2e8f0;font-weight:600;'>{r.get('name','-')}</td>"
                f"<td style='padding:6px 6px;color:#7a8599;text-align:right;'>{_safe_num(r.get('gap_rate')):.1f}%</td>"
                f"<td style='padding:6px 6px;color:#14b8a6;text-align:right;font-weight:600;'>{_safe_num(r.get('target_rate')):.1f}%</td>"
                f"<td style='padding:6px 6px;color:#22c55e;text-align:center;font-weight:600;'>{_safe_num(r.get('rr_ratio')):.2f}</td>"
                f"<td style='padding:6px 6px;text-align:center;'>{result_badge(r.get('result','-'))}</td>"
                f"<td style='padding:6px 6px;color:#22c55e;text-align:right;font-weight:600;'>{_safe_num(r.get('peak_pct')):+.1f}%</td>"
                f"<td style='padding:6px 6px;color:#7a8599;text-align:center;'>{_safe_int(r.get('days_to_target'))}일</td>"
                f"<td style='padding:6px 6px;color:#7a8599;text-align:left;'>{r.get('ma_pattern','-')}</td>"
                f"<td style='padding:6px 6px;color:#7a8599;text-align:left;'>{r.get('sector','-')}</td>"
                "</tr>"
            )

        st.markdown(
            f"""
            <div class="table-wrap">
            <table class="table-dark">
            <thead><tr>
                <th style="text-align:center;">시장</th>
                <th style="text-align:center;">날짜</th>
                <th style="text-align:left;">종목</th>
                <th style="text-align:right;">갭</th>
                <th style="text-align:right;">목표율</th>
                <th style="text-align:center;">손익비</th>
                <th style="text-align:center;">결과</th>
                <th style="text-align:right;">최고</th>
                <th style="text-align:center;">소요일</th>
                <th style="text-align:left;">MA</th>
                <th style="text-align:left;">섹터</th>
            </tr></thead>
            <tbody>{''.join(rows)}</tbody>
            </table>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("최근 매매 데이터가 없습니다.")

    st.markdown("#### ▸ Signal Archive")
    if not signal_archive.empty:
        rows = []
        view = signal_archive.copy()
        if "signal_date" in view.columns:
            view = view.sort_values("signal_date", ascending=False).head(8)
        for _, r in view.iterrows():
            rows.append(
                "<tr>"
                f"<td style='padding:6px 6px;text-align:center;'>{market_badge(r.get('market',''))}</td>"
                f"<td style='padding:6px 6px;color:#7a8599;text-align:center;font-size:10px;'>{fmt_date_short(r.get('signal_date'))}</td>"
                f"<td style='padding:6px 6px;color:#e2e8f0;font-weight:600;'>{r.get('name','-')}</td>"
                f"<td style='padding:6px 6px;color:#7a8599;text-align:right;'>{_safe_num(r.get('gap_rate')):.1f}%</td>"
                f"<td style='padding:6px 6px;color:#14b8a6;text-align:right;font-weight:600;'>{_safe_num(r.get('target_rate')):.1f}%</td>"
                f"<td style='padding:6px 6px;color:#22c55e;text-align:right;font-weight:600;'>{_safe_num(r.get('progress_pct')):.0f}%</td>"
                f"<td style='padding:6px 6px;color:#7a8599;text-align:center;'>{_safe_int(r.get('days_elapsed'))}일</td>"
                f"<td style='padding:6px 6px;text-align:center;'>{archive_result_badge(r.get('archive_result','-'))}</td>"
                "</tr>"
            )
        st.markdown(
            f"""
            <div class="table-wrap">
            <table class="table-dark">
            <thead><tr>
                <th style="text-align:center;">시장</th>
                <th style="text-align:center;">날짜</th>
                <th style="text-align:left;">종목</th>
                <th style="text-align:right;">갭%</th>
                <th style="text-align:right;">목표율</th>
                <th style="text-align:right;">진행율</th>
                <th style="text-align:center;">소요일</th>
                <th style="text-align:center;">결과</th>
            </tr></thead>
            <tbody>{''.join(rows)}</tbody>
            </table>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("Signal Archive 데이터가 없습니다.")

    st.markdown("#### ▸ 계좌별 자산추이")
    if not equity.empty:
        fig = go.Figure()
        for col, color in [("account1", "#3b82f6"), ("account2", "#a855f7"), ("account3", "#14b8a6")]:
            if col in equity.columns:
                fig.add_trace(go.Scatter(
                    x=equity["date"] if "date" in equity.columns else equity.index,
                    y=equity[col],
                    name=col,
                    mode="lines",
                    line=dict(width=2, color=color),
                ))
        fig.update_layout(
            template="plotly_dark",
            hovermode="x unified",
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="#0a0e14",
            plot_bgcolor="#0a0e14",
            legend=dict(orientation="h", y=1.08),
        )
        st.plotly_chart(fig, use_container_width=True)

elif page == "📋 Trade Log":
    st.info("trade_log.py 내용을 여기에 연결하세요.")

elif page == "📊 Performance":
    st.info("performance.py 내용을 여기에 연결하세요.")

elif page == "⚠️ Risk":
    st.info("risk.py 내용을 여기에 연결하세요.")

elif page == "📈 Signals":
    st.info("signals.py 내용을 여기에 연결하세요.")

elif page == "🌍 Market":
    st.info("market.py 내용을 여기에 연결하세요.")
