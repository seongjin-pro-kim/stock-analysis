"""🏠 메인 대시보드 — 지수차트, KPI, Best MA, 계좌별 자산추이, 최근매매+Signal Archive, 옵션만기"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils import result_badge, market_badge, fmt_date_short, archive_result_badge, init_state, df_state


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


def _mini_tag(text, bg, fg):
    return f'<span style="display:inline-block;padding:2px 7px;border-radius:999px;background:{bg};color:{fg};font-size:10px;font-weight:700;">{text}</span>'


def _panel(title, value, delta=None, color="#e2e8f0"):
    delta_html = ""
    if delta is not None:
        delta_html = f'<div style="margin-top:4px;color:{color};font-size:12px;font-weight:600;">{delta}</div>'
    return f"""
    <div style="background:#0f141b;border:1px solid #1e2530;border-radius:12px;padding:14px 14px 12px 14px;">
        <div style="color:#7a8599;font-size:12px;margin-bottom:6px;">{title}</div>
        <div style="color:#e2e8f0;font-size:28px;font-weight:700;line-height:1;">{value}</div>
        {delta_html}
    </div>
    """


def render():
    init_state()

    trades = df_state("trades")
    equity = df_state("equity_curve")
    positions = df_state("positions")
    signals = df_state("signals")
    signal_archive = df_state("signal_archive")
    idx = df_state("major_indices")

    st.markdown("### ▸ 메인 대시보드")

    st.markdown(
        """
        <style>
        .section-title{
            color:#e2e8f0;font-size:18px;font-weight:700;margin:6px 0 10px 0;
        }
        .subtle{
            color:#7a8599;font-size:12px;
        }
        .card-wrap{
            background:#0a0e14;border:1px solid #1e2530;border-radius:12px;padding:12px;
        }
        .table-wrap{
            background:#0a0e14;border:1px solid #1e2530;border-radius:12px;overflow-x:auto;
        }
        .table-dark{
            width:100%;border-collapse:collapse;white-space:nowrap;font-variant-numeric:tabular-nums;font-size:11px;
        }
        .table-dark thead tr{border-bottom:2px solid #1e2530;background:#111820;}
        .table-dark th{padding:7px 6px;color:#7a8599;font-size:10px;font-weight:600;}
        .table-dark td{padding:7px 6px;border-bottom:1px solid #1e2530;}
        .hl{background:rgba(20,184,166,0.06);}
        .positive{color:#22c55e;}
        .negative{color:#ef4444;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### ▸ 주요 시장 지표")
    idx_configs = [
        {"name": "KOSPI", "value": 2685.42, "change": +12.35, "color": "#3b82f6"},
        {"name": "KOSDAQ", "value": 872.15, "change": -3.21, "color": "#a855f7"},
        {"name": "NASDAQ", "value": 18245.80, "change": +85.50, "color": "#14b8a6"},
        {"name": "BTC", "value": 87420.50, "change": +1250.30, "color": "#eab308"},
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
        c.markdown(_panel(cfg["name"], value, delta, cfg["color"]), unsafe_allow_html=True)

    st.markdown("#### ▸ 시장 지수")
    if not idx.empty and "date" in idx.columns:
        idx = idx.copy()
        idx["date"] = pd.to_datetime(idx["date"], errors="coerce")
        fig = go.Figure()
        for name, color in [("KOSPI", "#3b82f6"), ("KOSDAQ", "#a855f7"), ("NASDAQ", "#14b8a6"), ("BTC", "#eab308")]:
            if name in idx.columns:
                fig.add_trace(go.Scatter(
                    x=idx["date"],
                    y=idx[name],
                    name=name,
                    mode="lines",
                    line=dict(width=2, color=color),
                    hovertemplate=f"{name}: %{{y:.2f}}<extra></extra>",
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
    else:
        st.info("시장 지표 데이터가 없습니다.")

    st.markdown("#### ▸ 핵심 KPI")
    total = len(trades)
    win_cnt = int((trades["result"] == "승").sum()) if not trades.empty and "result" in trades.columns else 0
    lose_cnt = int((trades["result"] == "패").sum()) if not trades.empty and "result" in trades.columns else 0
    ing_cnt = int((trades["result"] == "잉").sum()) if not trades.empty and "result" in trades.columns else 0
    win_rate = (win_cnt / max(win_cnt + lose_cnt, 1)) * 100 if (win_cnt + lose_cnt) else 0
    rr_avg = _safe_num(trades["rr_ratio"].mean()) if not trades.empty and "rr_ratio" in trades.columns else 0.0
    ev_avg = _safe_num(trades["expected_value"].mean()) if not trades.empty and "expected_value" in trades.columns else 0.0

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("총 매매", f"{total}건")
    k2.metric("승/패", f"{win_cnt}/{lose_cnt}")
    k3.metric("진행중", f"{ing_cnt}건")
    k4.metric("승률", f"{win_rate:.1f}%")
    k5.metric("RR 평균", f"{rr_avg:.2f}")
    k6.metric("기대값", f"{ev_avg:.1f}")

    st.markdown("#### ▸ 최근 매매")
    if not trades.empty:
        show_cols = [c for c in ["market", "date", "name", "gap_rate", "target_rate", "rr_ratio", "result", "peak_pct", "days_to_target", "ma_pattern", "sector"] if c in trades.columns]
        recent = trades.copy()
        if "date" in recent.columns:
            recent = recent.sort_values("date", ascending=False)
        recent = recent.head(8)

        rows = []
        for _, r in recent.iterrows():
            date_str = fmt_date_short(r.get("date"))
            rows.append(
                "<tr>"
                f"<td style='padding:6px 6px;text-align:center;'>{market_badge(r.get('market',''))}</td>"
                f"<td style='padding:6px 6px;color:#7a8599;text-align:center;font-size:10px;'>{date_str}</td>"
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

        table = f"""
        <div class="table-wrap">
        <table class="table-dark">
        <thead>
        <tr>
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
        </tr>
        </thead>
        <tbody>
        {''.join(rows)}
        </tbody>
        </table>
        </div>
        """
        st.markdown(table, unsafe_allow_html=True)
    else:
        st.info("최근 매매 데이터가 없습니다.")

    st.markdown("#### ▸ Signal Archive")
    if not signal_archive.empty:
        st.dataframe(signal_archive, use_container_width=True, hide_index=True)
    else:
        st.info("Signal Archive 데이터가 없습니다.")

    st.markdown("#### ▸ 계좌별 자산추이")
    if not equity.empty:
        eq = equity.copy()
        if "date" in eq.columns:
            eq["date"] = pd.to_datetime(eq["date"], errors="coerce")
        fig2 = go.Figure()
        for col, color in [("account1", "#3b82f6"), ("account2", "#a855f7"), ("account3", "#14b8a6")]:
            if col in eq.columns:
                fig2.add_trace(go.Scatter(
                    x=eq["date"] if "date" in eq.columns else eq.index,
                    y=eq[col],
                    name=col,
                    mode="lines",
                    line=dict(width=2, color=color),
                    hovertemplate=f"{col}: %{{y:.2f}}<extra></extra>",
                ))
        fig2.update_layout(
            template="plotly_dark",
            hovermode="x unified",
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="#0a0e14",
            plot_bgcolor="#0a0e14",
            legend=dict(orientation="h", y=1.08),
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("계좌 추이 데이터가 없습니다.")

    st.markdown("#### ▸ 최근 시그널")
    if not signals.empty:
        if "date" in signals.columns:
            signals = signals.copy()
            signals["date"] = pd.to_datetime(signals["date"], errors="coerce")
        view_cols = [c for c in ["date", "name", "signal_type", "strength", "ma_pattern", "sector"] if c in signals.columns]
        st.dataframe(signals[view_cols].head(8), use_container_width=True, hide_index=True)
    else:
        st.info("시그널 데이터가 없습니다.")

    st.markdown("#### ▸ 옵션만기")
    st.caption("옵션만기 캘린더/카운트다운은 추후 연동 가능")
