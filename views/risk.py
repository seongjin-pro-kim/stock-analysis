"""🛡️ 리스크 관리 — 설명 툴팁, 주간 P&L 4개, 단일색 바, 링크아이콘 설명"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils import init_state, df_state


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


def render():
    init_state()
    trades = df_state("trades")
    positions = df_state("positions")
    equity = df_state("equity_curve")

    st.markdown("### ▸ 리스크")

    st.markdown(
        """
        <style>
        .risk-kpi{
            background:#0f141b;border:1px solid #1e2530;border-radius:12px;padding:14px 14px 12px 14px;
        }
        .risk-sub{
            color:#7a8599;font-size:12px;margin:6px 0 10px 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    risk = st.session_state.get("risk_metrics", {}) or {}
    mdd = _safe_num(risk.get("mdd"))
    var = _safe_num(risk.get("var"))
    win_rate = _safe_num(risk.get("win_rate"))
    rr_avg = _safe_num(risk.get("rr_avg"))

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="risk-kpi"><div style="color:#7a8599;font-size:12px;">MDD</div><div style="color:#e2e8f0;font-size:28px;font-weight:700;">{mdd:.2f}%</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="risk-kpi"><div style="color:#7a8599;font-size:12px;">VaR</div><div style="color:#e2e8f0;font-size:28px;font-weight:700;">{var:.2f}%</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="risk-kpi"><div style="color:#7a8599;font-size:12px;">승률</div><div style="color:#e2e8f0;font-size:28px;font-weight:700;">{win_rate:.1f}%</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="risk-kpi"><div style="color:#7a8599;font-size:12px;">RR 평균</div><div style="color:#e2e8f0;font-size:28px;font-weight:700;">{rr_avg:.2f}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="risk-sub">손실 제한, 변동성, 승률, 손익비를 중심으로 위험도를 확인합니다.</div>', unsafe_allow_html=True)

    total = len(trades)
    win_cnt = int((trades["result"] == "승").sum()) if not trades.empty and "result" in trades.columns else 0
    lose_cnt = int((trades["result"] == "패").sum()) if not trades.empty and "result" in trades.columns else 0
    ing_cnt = int((trades["result"] == "잉").sum()) if not trades.empty and "result" in trades.columns else 0

    a1, a2, a3 = st.columns(3)
    a1.markdown(f'<div class="risk-kpi"><div style="color:#7a8599;font-size:12px;">총 매매</div><div style="color:#e2e8f0;font-size:24px;font-weight:700;">{total}건</div></div>', unsafe_allow_html=True)
    a2.markdown(f'<div class="risk-kpi"><div style="color:#7a8599;font-size:12px;">진행중</div><div style="color:#e2e8f0;font-size:24px;font-weight:700;">{ing_cnt}건</div></div>', unsafe_allow_html=True)
    a3.markdown(f'<div class="risk-kpi"><div style="color:#7a8599;font-size:12px;">승/패</div><div style="color:#e2e8f0;font-size:24px;font-weight:700;">{win_cnt}/{lose_cnt}</div></div>', unsafe_allow_html=True)

    st.markdown("#### ▸ 리스크 추이")
    if not equity.empty and {"date"}.issubset(equity.columns):
        eq = equity.copy()
        eq["date"] = pd.to_datetime(eq["date"], errors="coerce")

        val_col = None
        for c in ["equity", "value", "balance", "nav"]:
            if c in eq.columns:
                val_col = c
                break

        if val_col is not None:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=eq["date"],
                y=eq[val_col],
                mode="lines+markers",
                name="리스크 추이",
                line=dict(color="#38bdf8", width=2),
                hovertemplate="날짜: %{x|%m/%d}<br>값: %{y:.2f}<extra></extra>",
            ))
            fig.update_layout(
                template="plotly_dark",
                height=320,
                margin=dict(l=20, r=20, t=20, b=20),
                paper_bgcolor="#0a0e14",
                plot_bgcolor="#0a0e14",
                legend=dict(orientation="h", y=1.05),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("리스크 추이 데이터가 없습니다.")
    else:
        st.info("리스크 추이 데이터가 없습니다.")

    st.markdown("#### ▸ 위험 요약")
    summary = [
        f"- MDD: {mdd:.2f}%",
        f"- VaR: {var:.2f}%",
        f"- 승률: {win_rate:.1f}%",
        f"- RR 평균: {rr_avg:.2f}",
    ]
    st.markdown("\n".join(summary))

    st.markdown("#### ▸ 포지션")
    if not positions.empty:
        st.dataframe(positions, use_container_width=True, hide_index=True)
    else:
        st.info("포지션 데이터가 없습니다.")
