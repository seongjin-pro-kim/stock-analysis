"""성과 분석 — GAP R-Zone 6.5"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils import DARK_AIRY_PALETTE

def render():
    trades = st.session_state.trades
    equity = st.session_state.equity_curve

    st.markdown("### 📊 매매 성과 분석")

    total = len(trades)
    wins = trades[trades["result"] == "승"]
    losses = trades[trades["result"] == "패"]
    win_count = len(wins)
    loss_count = len(losses)
    win_rate = (win_count / total * 100) if total else 0

    avg_peak = trades["peak_pct"].mean() if len(trades) else 0
    avg_loss = trades["min_low_pct"].mean() if len(trades) else 0
    avg_win_peak = wins["peak_pct"].mean() if win_count else 0
    avg_loss_peak = losses["min_low_pct"].mean() if loss_count else 0
    avg_days_win = wins["days_to_target"].mean() if win_count else 0
    avg_days_loss = losses["days_to_target"].mean() if loss_count else 0

    total_eq = equity.groupby("date")["value"].sum().reset_index()
    total_pnl = total_eq["value"].iloc[-1] - total_eq["value"].iloc[0]
    pnl_pct = (total_pnl / total_eq["value"].iloc[0]) * 100 if total_eq["value"].iloc[0] > 0 else 0
    max_val = total_eq["value"].max()
    max_dd_pct = ((max_val - total_eq["value"].min()) / max_val) * 100 if max_val > 0 else 0
    current_capital = total_eq["value"].iloc[-1]

    profit_factor = 0
    if loss_count and abs(avg_loss_peak) > 0:
        profit_factor = (win_count * avg_win_peak) / (loss_count * abs(avg_loss_peak))

    st.markdown("#### 핵심 지표")
    rows = [
        [("총 거래 건수", f"{total}건", "neutral"), ("수익 인자", f"{profit_factor:.2f}", "positive" if profit_factor > 1 else "negative")],
        [("승리", f"{win_count}건", "positive"), ("승률", f"{win_rate:.1f}%", "positive" if win_rate >= 60 else "negative"), ("최고수익", f"{avg_peak:+.1f}%", "positive"), ("평균수익", f"{avg_win_peak:+.1f}%", "positive"), ("승리 소요일", f"{avg_days_win:.1f}일", "neutral")],
        [("패배", f"{loss_count}건", "negative"), ("평균최저", f"{avg_loss:+.1f}%", "negative"), ("평균손실", f"{avg_loss_peak:+.1f}%", "negative"), ("최대낙폭", f"{max_dd_pct:.1f}%", "negative"), ("패배 소요일", f"{avg_days_loss:.1f}일", "neutral")],
    ]
    for row in rows:
        cols = st.columns(len(row))
        for col, (label, value, cls) in zip(cols, row):
            with col:
                st.markdown(
                    f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
                    f'<div class="kpi-value {cls}">{value}</div></div>',
                    unsafe_allow_html=True
                )
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 갭 비율 범위별 성과")
        bins = [0, 5, 10, 15, 100]
        labels = ["0-5%", "5-10%", "10-15%", "15%+"]
        trades_binned = trades.copy()
        trades_binned["gap_bin"] = pd.cut(trades_binned["gap_rate"], bins=bins, labels=labels, right=False)

        gap_stats = []
        for lbl in labels:
            subset = trades_binned[trades_binned["gap_bin"] == lbl]
            if len(subset):
                gap_stats.append({
                    "range": lbl,
                    "count": len(subset),
                    "win_rate": len(subset[subset["result"] == "승"]) / len(subset) * 100,
                    "avg_peak": subset["peak_pct"].mean(),
                })

        if gap_stats:
            gs = pd.DataFrame(gap_stats)
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=gs["range"], y=gs["win_rate"], name="승률 (%)",
                marker_color=DARK_AIRY_PALETTE[0],
                text=[f"{v:.0f}%" for v in gs["win_rate"]],
                textposition="outside",
                textfont=dict(color="#e2e8f0", size=11),
                opacity=0.92,
            ))
            fig.add_trace(go.Scatter(
                x=gs["range"], y=gs["avg_peak"], name="평균 최고수익 (%)",
                mode="lines+markers", yaxis="y2",
                line=dict(color=DARK_AIRY_PALETTE[4], width=2),
                marker=dict(size=7),
            ))
            fig.update_layout(
                plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
                height=300, margin=dict(l=0, r=40, t=10, b=0),
                legend=dict(font=dict(color="#7a8599", size=10), orientation="h", y=-0.15),
                xaxis=dict(color="#7a8599"),
                yaxis=dict(showgrid=True, gridcolor="#1e2530", color="#7a8599", title=""),
                yaxis2=dict(overlaying="y", side="right", showgrid=False, color=DARK_AIRY_PALETTE[4], title=""),
                font=dict(color="#e2e8f0"), bargap=0.3
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 결과 분포")
        if "result_detail" in trades.columns:
            result_counts = trades["result_detail"].value_counts()
            detail_map = {"reached_20": "20봉 도달", "reached_80": "80봉 도달", "stopped": "손절"}
            color_map = {"reached_20": DARK_AIRY_PALETTE[1], "reached_80": DARK_AIRY_PALETTE[4], "stopped": "#ef4444"}

            if len(result_counts):
                fig2 = go.Figure(go.Pie(
                    labels=[detail_map.get(k, k) for k in result_counts.index],
                    values=result_counts.values,
                    hole=0.55,
                    marker=dict(colors=[color_map.get(k, "#7a8599") for k in result_counts.index]),
                    textinfo="label+value",
                    textfont=dict(size=12, color="#e2e8f0"),
                ))
                fig2.update_layout(
                    plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
                    height=300, margin=dict(l=0, r=0, t=10, b=0),
                    showlegend=False, font=dict(color="#e2e8f0")
                )
                st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("#### MA 패턴별 성과")
    if len(trades) > 0 and "ma_pattern" in trades.columns:
        ma_groups = trades.groupby("ma_pattern").agg(
            거래수=("result", "count"),
            승리=("result", lambda x: (x == "승").sum()),
            평균수익=("peak_pct", "mean"),
            평균손실=("min_low_pct", "mean"),
        ).reset_index()
        ma_groups["승률"] = (ma_groups["승리"] / ma_groups["거래수"] * 100).round(1)
        ma_groups["평균수익"] = ma_groups["평균수익"].round(1)
        ma_groups["평균손실"] = ma_groups["평균손실"].round(1)
        ma_groups = ma_groups.rename(columns={"ma_pattern": "MA 패턴"}).sort_values("승률", ascending=False)

        st.dataframe(
            ma_groups[["MA 패턴", "거래수", "승리", "승률", "평균수익", "평균손실"]],
            use_container_width=True,
            hide_index=True
        )

    st.markdown("#### 섹터별 성과")
    if len(trades) > 0 and "sector" in trades.columns:
        sector_groups = trades.groupby("sector").agg(
            거래수=("result", "count"),
            승리=("result", lambda x: (x == "승").sum()),
            평균수익=("peak_pct", "mean")
        ).reset_index()
        sector_groups["승률"] = (sector_groups["승리"] / sector_groups["거래수"] * 100).round(1)
        sector_groups["평균수익"] = sector_groups["평균수익"].round(1)
        sector_groups = sector_groups.rename(columns={"sector": "섹터"}).sort_values("거래수", ascending=False)

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=sector_groups["섹터"], y=sector_groups["거래수"], name="거래수",
            marker_color=DARK_AIRY_PALETTE[2],
            text=sector_groups["거래수"],
            textposition="outside",
            textfont=dict(color="#e2e8f0", size=11),
            opacity=0.92,
        ))
        fig3.add_trace(go.Scatter(
            x=sector_groups["섹터"], y=sector_groups["승률"], name="승률 (%)",
            mode="lines+markers", yaxis="y2",
            line=dict(color=DARK_AIRY_PALETTE[5], width=2),
            marker=dict(size=7),
        ))
        fig3.update_layout(
            plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
            height=300, margin=dict(l=0, r=40, t=10, b=0),
            legend=dict(font=dict(color="#7a8599", size=10), orientation="h", y=-0.2),
            xaxis=dict(color="#7a8599"),
            yaxis=dict(showgrid=True, gridcolor="#1e2530", color="#7a8599"),
            yaxis2=dict(overlaying="y", side="right", showgrid=False, color=DARK_AIRY_PALETTE[5], range=[0, 110]),
            font=dict(color="#e2e8f0"),
            bargap=0.3
        )
        st.plotly_chart(fig3, use_container_width=True)
