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
    h1, h2, h3, h4, h5, h6, p, span, label, div {
        color: #e2e8f0;
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
    .badge-win { color:#22c55e; font-weight:700; }
    .badge-lose { color:#ef4444; font-weight:700; }
    .badge-ing { color:#3b82f6; font-weight:700; }
    .badge-progress { color:#a78bfa; font-weight:700; }
    .badge-kospi, .badge-kosdaq, .badge-nasdaq, .badge-btc {
        padding: 2px 8px;
        border-radius: 999px;
        font-size: 10px;
        font-weight: 700;
        display: inline-block;
    }
    .badge-kospi { background:#172554; color:#93c5fd; }
    .badge-kosdaq { background:#2e1065; color:#c4b5fd; }
    .badge-nasdaq { background:#064e3b; color:#99f6e4; }
    .badge-btc { background:#78350f; color:#fde68a; }
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
    st.markdown("#### ▸ 매매 기록")
    if trades.empty:
        st.info("데이터가 없습니다.")
    else:
        fc1, fc2, fc3, fc4, fc5, fc6, fc7 = st.columns(7)
        with fc1:
            market_filter = st.selectbox("시장", ["전체", "KOSPI", "KOSDAQ"])
        with fc2:
            result_filter = st.selectbox("결과", ["전체", "승", "패", "잉"])
        with fc3:
            sectors = ["전체"] + sorted(trades["sector"].dropna().unique().tolist()) if "sector" in trades.columns else ["전체"]
            sector_filter = st.selectbox("섹터", sectors)
        with fc4:
            grade_opts = ["전체"] + sorted(trades["grade"].dropna().unique().tolist()) if "grade" in trades.columns else ["전체"]
            grade_filter = st.selectbox("등급", grade_opts)
        with fc5:
            core_filter = st.selectbox("코어 여부", ["전체", "코어만", "코어 제외"])
        with fc6:
            if "rr_ratio" in trades.columns and trades["rr_ratio"].notna().any():
                rr_max = float(trades["rr_ratio"].max())
                rr_threshold = st.slider("최소 RR", 0.0, round(rr_max, 1), 0.0, 0.1)
            else:
                rr_threshold = 0.0
                st.caption("RR 데이터 없음")
        with fc7:
            sort_by = st.selectbox("정렬", ["날짜 (최신)", "날짜 (오래된)", "갭비율 ↓", "최고수익 ↓", "손익비 ↓", "기대값 ↓", "소요일 ↑"])

        filtered = trades.copy()
        if market_filter != "전체" and "market" in filtered.columns:
            filtered = filtered[filtered["market"] == market_filter]
        if result_filter != "전체" and "result" in filtered.columns:
            filtered = filtered[filtered["result"] == result_filter]
        if sector_filter != "전체" and "sector" in filtered.columns:
            filtered = filtered[filtered["sector"] == sector_filter]
        if grade_filter != "전체" and "grade" in filtered.columns:
            filtered = filtered[filtered["grade"] == grade_filter]
        if "is_core" in filtered.columns:
            if core_filter == "코어만":
                filtered = filtered[filtered["is_core"] == True]
            elif core_filter == "코어 제외":
                filtered = filtered[filtered["is_core"] == False]
        if "rr_ratio" in filtered.columns and rr_threshold > 0:
            filtered = filtered[filtered["rr_ratio"] >= rr_threshold]

        sort_map = {
            "날짜 (최신)": ("date", False),
            "날짜 (오래된)": ("date", True),
            "갭비율 ↓": ("gap_rate", False),
            "최고수익 ↓": ("peak_pct", False),
            "손익비 ↓": ("rr_ratio", False),
            "기대값 ↓": ("expected_value", False),
            "소요일 ↑": ("days_to_target", True),
        }
        sort_col, sort_asc = sort_map.get(sort_by, ("date", False))
        if sort_col in filtered.columns:
            filtered = filtered.sort_values(sort_col, ascending=sort_asc)

        in_progress = len(trades[trades["result"] == "잉"]) if "result" in trades.columns else 0
        st.markdown(f"총 {len(filtered)}건 / {len(trades)}건 (진행중: :blue[{in_progress}건])")

        show_sell_ma = result_filter in ["승", "패"]
        rows = []
        for _, r in filtered.iterrows():
            grade = r.get("grade", "-") or "-"
            grade_colors = {"A": "#22c55e", "B": "#eab308", "C": "#ef4444"}
            g_color = grade_colors.get(grade, "#7a8599")
            rr_val = _safe_num(r.get("rr_ratio"))
            rr_color = "#22c55e" if rr_val >= 2.0 else ("#eab308" if rr_val >= 1.5 else "#ef4444")
            ev_val = _safe_num(r.get("expected_value"))
            ev_color = "#22c55e" if ev_val >= 15 else ("#eab308" if ev_val >= 5 else "#7a8599")
            sell_ma_td = f"<td style='padding:5px 4px;color:#a78bfa;font-size:10px;text-align:left;'>{r.get('sell_ma','') or ''}</td>" if show_sell_ma else ""

            rows.append(
                "<tr style='border-bottom:1px solid #1e2530;'>"
                f"<td style='padding:5px 4px;font-size:10px;text-align:center;'>{market_badge(r.get('market',''))}</td>"
                f"<td style='padding:5px 4px;color:#7a8599;font-size:10px;text-align:center;'>{fmt_date_short(r.get('date'))}</td>"
                f"<td style='padding:5px 4px;color:#e2e8f0;font-size:12px;text-align:left;font-weight:600;'>{r.get('name','-')}</td>"
                f"<td style='padding:5px 4px;color:#7a8599;font-size:10px;text-align:left;'>{r.get('code','-')}</td>"
                f"<td style='padding:5px 4px;color:{g_color};font-weight:700;font-size:10px;text-align:center;'>{grade}</td>"
                f"<td style='padding:5px 4px;color:#e2e8f0;text-align:right;font-size:10px;'>{_safe_num(r.get('gap_rate')):.1f}%</td>"
                f"<td style='padding:5px 4px;color:#e2e8f0;text-align:right;font-size:10px;'>₩{_safe_int(r.get('entry_price')):,}</td>"
                f"<td style='padding:5px 4px;color:#14b8a6;text-align:right;font-size:10px;font-weight:600;'>{_safe_num(r.get('target_rate')):.1f}%</td>"
                f"<td style='padding:5px 4px;color:#14b8a6;text-align:right;font-size:10px;'>₩{_safe_int(r.get('target_price')):,}</td>"
                f"<td style='padding:5px 4px;color:#ef4444;text-align:right;font-size:10px;'>₩{_safe_int(r.get('stop_price')):,}</td>"
                f"<td style='padding:5px 4px;color:#ef4444;text-align:right;font-size:10px;'>{_safe_num(r.get('stop_rate')):.1f}%</td>"
                f"<td style='padding:5px 4px;color:{rr_color};text-align:center;font-size:10px;font-weight:700;'>{rr_val:.2f}</td>"
                f"<td style='padding:5px 4px;color:{ev_color};text-align:right;font-size:10px;font-weight:700;'>{ev_val:.1f}</td>"
                f"<td style='padding:5px 4px;color:#22c55e;text-align:right;font-size:10px;font-weight:700;'>{_safe_num(r.get('peak_pct')):+.1f}%</td>"
                f"<td style='padding:5px 4px;color:#ef4444;text-align:right;font-size:10px;'>{_safe_num(r.get('min_low_pct')):+.1f}%</td>"
                f"<td style='padding:5px 4px;text-align:center;font-size:10px;'>{result_badge(r.get('result','-'))}</td>"
                f"<td style='padding:5px 4px;color:#7a8599;text-align:center;font-size:10px;'>{_safe_int(r.get('days_to_target'))}일</td>"
                f"<td style='padding:5px 4px;color:#7a8599;font-size:9px;text-align:left;'>{r.get('ma_pattern','-')}</td>"
                f"{sell_ma_td}"
                f"<td style='padding:5px 4px;color:#7a8599;font-size:10px;text-align:left;'>{r.get('sector','-')}</td>"
                "</tr>"
            )

        sell_ma_header = '<th style="padding:5px 4px;color:#a78bfa;text-align:left;font-size:10px;">MA(매도)</th>' if show_sell_ma else ""
        st.markdown(
            f"""
            <div class="table-wrap">
            <table class="table-dark">
            <thead><tr>
                <th style="text-align:center;">시장</th>
                <th style="text-align:center;">날짜</th>
                <th style="text-align:left;">종목</th>
                <th style="text-align:left;">코드</th>
                <th style="text-align:center;">등급</th>
                <th style="text-align:right;">갭</th>
                <th style="text-align:right;">진입가</th>
                <th style="text-align:right;color:#14b8a6;font-weight:600;">목표율</th>
                <th style="text-align:right;">목표가</th>
                <th style="text-align:right;">손절가</th>
                <th style="text-align:right;">손절율</th>
                <th style="text-align:center;color:#14b8a6;font-weight:600;">손익비</th>
                <th style="text-align:right;color:#14b8a6;font-weight:600;">기대값</th>
                <th style="text-align:right;">최고</th>
                <th style="text-align:right;">최저</th>
                <th style="text-align:center;">결과</th>
                <th style="text-align:center;">소요일</th>
                <th style="text-align:left;">MA</th>
                {sell_ma_header}
                <th style="text-align:left;">섹터</th>
            </tr></thead>
            <tbody>{''.join(rows)}</tbody>
            </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### ▸ 거래 달력")
        if "date" in filtered.columns:
            import calendar
            cal_data = filtered.copy()
            cal_data["month"] = pd.to_datetime(cal_data["date"], errors="coerce").dt.to_period("M")
            months = sorted(cal_data["month"].dropna().unique(), reverse=True)[:3]
            cal_cols = st.columns(len(months)) if months else []
            for i, mp in enumerate(months):
                with cal_cols[i]:
                    st.markdown(
                        f"<div style='color:#e2e8f0;font-size:13px;font-weight:600;margin-bottom:8px;text-align:center;'>{str(mp.year)[2:]}년 {mp.month}월</div>",
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        "<div style='text-align:center;'>" +
                        "".join(
                            f"<span style='display:inline-block;width:28px;text-align:center;color:#7a8599;font-size:10px;margin:1px;'>{d}</span>"
                            for d in ["월","화","수","목","금","토","일"]
                        ) +
                        "</div>",
                        unsafe_allow_html=True,
                    )
                    month_trades = cal_data[cal_data["month"] == mp]
                    trade_dates = {}
                    for _, t in month_trades.iterrows():
                        d = pd.to_datetime(t["date"], errors="coerce")
                        if pd.notna(d):
                            trade_dates.setdefault(d.day, []).append(t.get("result", "-"))
                    cal_html = ""
                    for week in calendar.monthcalendar(mp.year, mp.month):
                        for day in week:
                            if day == 0:
                                cal_html += '<span style="display:inline-block;width:28px;color:#1e2530;">·</span>'
                            else:
                                rs = trade_dates.get(day, [])
                                cls = "#7a8599"
                                if "잉" in rs:
                                    cls = "#3b82f6"
                                elif "승" in rs:
                                    cls = "#22c55e"
                                elif "패" in rs:
                                    cls = "#ef4444"
                                cal_html += f'<span style="display:inline-block;width:28px;text-align:center;color:{cls};font-weight:700;">{day}</span>'
                        cal_html += "<br>"
                    st.markdown(f"<div style='text-align:center;line-height:1.8;'>{cal_html}</div>", unsafe_allow_html=True)

elif page == "📊 Performance":
    st.info("performance.py 내용을 여기에 연결하세요.")

elif page == "⚠️ Risk":
    st.info("risk.py 내용을 여기에 연결하세요.")

elif page == "📈 Signals":
    st.info("signals.py 내용을 여기에 연결하세요.")

elif page == "🌍 Market":
    st.info("market.py 내용을 여기에 연결하세요.")
