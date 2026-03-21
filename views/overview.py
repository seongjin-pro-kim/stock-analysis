"""메인 대시보드 — views/overview.py"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils import result_badge, market_badge, fmt_date_short, archive_result_badge


def _safe_num(x, default=0.0):
    try:
        return default if pd.isna(x) else float(x)
    except Exception:
        return default


def _safe_int(x, default=0):
    try:
        return default if pd.isna(x) else int(x)
    except Exception:
        return default


def _card(title, value, delta=None, delta_color="#9aa5b4"):
    delta_html = (
        f'<div style="margin-top:4px;color:{delta_color};font-size:11px;font-weight:600;">{delta}</div>'
        if delta is not None else ""
    )
    return f"""
    <div style="background:#0f141b;border:1px solid #1e2530;border-radius:10px;padding:14px 16px 12px 16px;">
        <div style="color:#566270;font-size:11px;margin-bottom:5px;letter-spacing:.4px;">{title}</div>
        <div style="color:#dde3ed;font-size:26px;font-weight:700;line-height:1;">{value}</div>
        {delta_html}
    </div>
    """


def render():
    trades        = st.session_state.trades.copy()
    equity        = st.session_state.equity_curve.copy()
    signal_archive = st.session_state.signal_archive.copy()

    if "date" in trades.columns:
        trades["date"] = pd.to_datetime(trades["date"], errors="coerce")
    if "date" in equity.columns:
        equity["date"] = pd.to_datetime(equity["date"], errors="coerce")
    if "signal_date" in signal_archive.columns:
        signal_archive["signal_date"] = pd.to_datetime(signal_archive["signal_date"], errors="coerce")

    st.markdown("### ▸ 메인 대시보드")

    # ── 시장 지표 카드 ────────────────────────────────────
    st.markdown("#### ▸ 주요 시장 지표")
    idx_configs = [
        {"name": "KOSPI",  "value": 2685.42,  "change": 12.35,   "color": "#7a9fc0"},
        {"name": "KOSDAQ", "value": 872.15,   "change": -3.21,   "color": "#9b8fc4"},
        {"name": "NASDAQ", "value": 18245.80, "change": 85.50,   "color": "#6aada5"},
        {"name": "BTC",    "value": 87420.50, "change": 1250.30, "color": "#b8a96a"},
    ]
    cols = st.columns(4)
    for c, cfg in zip(cols, idx_configs):
        sign = "+" if cfg["change"] >= 0 else ""
        d_color = "#6aad8a" if cfg["change"] >= 0 else "#c98a8a"
        if cfg["name"] == "BTC":
            value = f"${cfg['value']:,.1f}"
            delta = f"{sign}${cfg['change']:,.1f}"
        elif cfg["name"] == "NASDAQ":
            value = f"{cfg['value']:,.2f}"
            delta = f"{sign}{cfg['change']:,.2f}"
        else:
            value = f"{cfg['value']:,.2f}"
            delta = f"{sign}{cfg['change']:.2f}"
        c.markdown(_card(cfg["name"], value, delta, d_color), unsafe_allow_html=True)

    # ── 핵심 KPI ─────────────────────────────────────────
    st.markdown("#### ▸ 핵심 KPI")
    total    = len(trades)
    win_cnt  = int((trades["result"] == "승").sum()) if "result" in trades.columns else 0
    lose_cnt = int((trades["result"] == "패").sum()) if "result" in trades.columns else 0
    ing_cnt  = int((trades["result"] == "잉").sum()) if "result" in trades.columns else 0
    win_rate = (win_cnt / max(win_cnt + lose_cnt, 1)) * 100
    rr_avg   = _safe_num(trades["rr_ratio"].mean()) if "rr_ratio" in trades.columns else 0.0
    ev_avg   = _safe_num(trades["expected_value"].mean()) if "expected_value" in trades.columns else 0.0

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("총 매매",  f"{total}건")
    k2.metric("승/패",    f"{win_cnt}/{lose_cnt}")
    k3.metric("진행중",   f"{ing_cnt}건")
    k4.metric("승률",     f"{win_rate:.1f}%")
    k5.metric("RR 평균",  f"{rr_avg:.2f}")
    k6.metric("기대값",   f"{ev_avg:.1f}")

    # ── 최근 매매 ─────────────────────────────────────────
    st.markdown("#### ▸ 최근 매매")
    if not trades.empty:
        recent = trades.sort_values("date", ascending=False).head(8) if "date" in trades.columns else trades.head(8)
        rows = []
        for _, r in recent.iterrows():
            rows.append(
                "<tr>"
                f"<td style='padding:6px 5px;text-align:center;'>{market_badge(r.get('market',''))}</td>"
                f"<td style='padding:6px 5px;color:#566270;font-size:10px;text-align:center;'>{fmt_date_short(r.get('date'))}</td>"
                f"<td style='padding:6px 5px;color:#dde3ed;font-weight:600;text-align:left;'>{r.get('name','-')}</td>"
                f"<td style='padding:6px 5px;color:#7a8599;text-align:right;'>{_safe_num(r.get('gap_rate')):.1f}%</td>"
                f"<td style='padding:6px 5px;color:#6aada5;font-weight:600;text-align:right;'>{_safe_num(r.get('target_rate')):.1f}%</td>"
                f"<td style='padding:6px 5px;color:#8fbf8f;font-weight:700;text-align:center;'>{_safe_num(r.get('rr_ratio')):.2f}</td>"
                f"<td style='padding:6px 5px;text-align:center;'>{result_badge(r.get('result','-'))}</td>"
                f"<td style='padding:6px 5px;color:#8fbf8f;font-weight:600;text-align:right;'>{_safe_num(r.get('peak_pct')):+.1f}%</td>"
                f"<td style='padding:6px 5px;color:#566270;text-align:center;'>{_safe_int(r.get('days_to_target'))}일</td>"
                f"<td style='padding:6px 5px;color:#566270;text-align:left;font-size:10px;'>{r.get('ma_pattern','-')}</td>"
                f"<td style='padding:6px 5px;color:#566270;text-align:left;font-size:10px;'>{r.get('sector','-')}</td>"
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
                <th style="text-align:right;color:#6aada5;">목표율</th>
                <th style="text-align:center;color:#8fbf8f;">손익비</th>
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
        st.info("매매 데이터가 없습니다.")

    # ── Signal Archive ────────────────────────────────────
    st.markdown("#### ▸ Signal Archive")
    if not signal_archive.empty:
        view = signal_archive.sort_values("signal_date", ascending=False).head(8) if "signal_date" in signal_archive.columns else signal_archive.head(8)
        rows = []
        for _, r in view.iterrows():
            rows.append(
                "<tr>"
                f"<td style='padding:6px 5px;text-align:center;'>{market_badge(r.get('market',''))}</td>"
                f"<td style='padding:6px 5px;color:#566270;font-size:10px;text-align:center;'>{fmt_date_short(r.get('signal_date'))}</td>"
                f"<td style='padding:6px 5px;color:#dde3ed;font-weight:600;text-align:left;'>{r.get('name','-')}</td>"
                f"<td style='padding:6px 5px;color:#7a8599;text-align:right;'>{_safe_num(r.get('gap_rate')):.1f}%</td>"
                f"<td style='padding:6px 5px;color:#6aada5;font-weight:600;text-align:right;'>{_safe_num(r.get('target_rate')):.1f}%</td>"
                f"<td style='padding:6px 5px;color:#8fbf8f;font-weight:600;text-align:right;'>{_safe_num(r.get('progress_pct')):.0f}%</td>"
                f"<td style='padding:6px 5px;color:#566270;text-align:center;'>{_safe_int(r.get('days_elapsed'))}일</td>"
                f"<td style='padding:6px 5px;text-align:center;'>{archive_result_badge(r.get('archive_result','-'))}</td>"
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
                <th style="text-align:right;color:#6aada5;">목표율</th>
                <th style="text-align:right;color:#8fbf8f;">진행율</th>
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

    # ── 계좌별 자산추이 ───────────────────────────────────
    st.markdown("#### ▸ 계좌별 자산추이")
    if not equity.empty:
        fig = go.Figure()
        for col, color in [("account1", "#7a9fc0"), ("account2", "#9b8fc4"), ("account3", "#6aada5")]:
            if col in equity.columns:
                fig.add_trace(go.Scatter(
                    x=equity["date"] if "date" in equity.columns else equity.index,
                    y=equity[col],
                    name=col,
                    mode="lines",
                    line=dict(width=2, color=color),
                    hovertemplate=f"{col}: %{{y:,.0f}}<extra></extra>",
                ))
        fig.update_layout(
            template="plotly_dark",
            hovermode="x unified",
            height=280,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="#0a0e14",
            plot_bgcolor="#0a0e14",
            legend=dict(orientation="h", y=1.08, font=dict(size=11, color="#7a8599")),
            xaxis=dict(gridcolor="#1e2530", color="#566270"),
            yaxis=dict(gridcolor="#1e2530", color="#566270"),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("계좌 추이 데이터가 없습니다.")
