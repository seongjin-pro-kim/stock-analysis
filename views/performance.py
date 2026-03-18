"""📊 매매 성과 분석 — 12개 핵심 지표, 갭 범위 차트, 결과 분포, MA 패턴 테이블"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

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

    avg_peak = trades["peak_pct"].mean()
    avg_loss = trades["min_low_pct"].mean()
    avg_win_peak = wins["peak_pct"].mean() if win_count else 0
    avg_loss_peak = losses["min_low_pct"].mean() if loss_count else 0
    avg_days_win = wins["days_to_target"].mean() if win_count else 0
    avg_days_loss = losses["days_to_target"].mean() if loss_count else 0

    total_pnl = equity["value"].iloc[-1] - equity["value"].iloc[0]
    max_val = equity["value"].max()
    max_dd_pct = ((max_val - equity["value"].min()) / max_val) * 100 if max_val > 0 else 0

    # 수익 인자 (win_rate * avg_win / avg_loss 근사)
    profit_factor = (win_count * avg_win_peak / (loss_count * abs(avg_loss_peak))) if (loss_count and avg_loss_peak) else 0

    # ── 12개 핵심 지표 ─────────────────────────────────
    st.markdown("#### 핵심 지표")
    rows = [
        [("총 거래 수", f"{total}건", ""), ("승리", f"{win_count}건", "positive"),
         ("패배", f"{loss_count}건", "negative"), ("승률", f"{win_rate:.1f}%", "positive" if win_rate >= 60 else "negative")],
        [("평균 최고수익", f"{avg_peak:+.1f}%", "positive"), ("평균 최저", f"{avg_loss:+.1f}%", "negative"),
         ("승리 평균 수익", f"{avg_win_peak:+.1f}%", "positive"), ("패배 평균 손실", f"{avg_loss_peak:+.1f}%", "negative")],
        [("승리 평균 소요일", f"{avg_days_win:.1f}일", ""), ("패배 평균 소요일", f"{avg_days_loss:.1f}일", ""),
         ("최대 낙폭", f"{max_dd_pct:.1f}%", "negative"), ("수익 인자", f"{profit_factor:.2f}", "positive" if profit_factor > 1 else "negative")],
    ]
    for row in rows:
        cols = st.columns(4)
        for col, (label, value, cls) in zip(cols, row):
            with col:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value {cls}">{value}</div>
                </div>""", unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 차트 2열 ───────────────────────────────────────
    col1, col2 = st.columns(2)

    # 갭 비율 범위별 성과
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
                    "avg_peak": subset["peak_pct"].mean()
                })

        if gap_stats:
            gs = pd.DataFrame(gap_stats)
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=gs["range"], y=gs["win_rate"],
                name="승률 (%)",
                marker_color="#14b8a6",
                text=[f"{v:.0f}%" for v in gs["win_rate"]],
                textposition="outside",
                textfont=dict(color="#e2e8f0", size=11),
            ))
            fig.add_trace(go.Scatter(
                x=gs["range"], y=gs["avg_peak"],
                name="평균 최고수익 (%)",
                mode="lines+markers",
                yaxis="y2",
                line=dict(color="#eab308", width=2),
                marker=dict(size=7),
            ))
            fig.update_layout(
                plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
                height=300,
                margin=dict(l=0, r=40, t=10, b=0),
                legend=dict(font=dict(color="#7a8599", size=10), orientation="h", y=-0.15),
                xaxis=dict(color="#7a8599"),
                yaxis=dict(showgrid=True, gridcolor="#1e2530", color="#7a8599", title=""),
                yaxis2=dict(overlaying="y", side="right", showgrid=False, color="#eab308", title=""),
                font=dict(color="#e2e8f0"),
                bargap=0.3,
            )
            st.plotly_chart(fig, use_container_width=True)

    # 결과 분포 (파이)
    with col2:
        st.markdown("#### 결과 분포")
        result_counts = trades["result_detail"].value_counts()
        detail_map = {"reached_20": "20봉 도달", "reached_80": "80봉 도달", "stopped": "손절"}
        color_map = {"reached_20": "#22c55e", "reached_80": "#14b8a6", "stopped": "#ef4444"}

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
            height=300,
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
            font=dict(color="#e2e8f0"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── MA 패턴 테이블 ────────────────────────────────
    st.markdown("#### MA 패턴별 성과")
    ma_groups = trades.groupby("ma_pattern").agg(
        거래수=("result", "count"),
        승리=("result", lambda x: (x == "승").sum()),
        평균수익=("peak_pct", "mean"),
        평균손실=("min_low_pct", "mean"),
    ).reset_index()
    ma_groups["승률"] = (ma_groups["승리"] / ma_groups["거래수"] * 100).round(1)
    ma_groups["평균수익"] = ma_groups["평균수익"].round(1)
    ma_groups["평균손실"] = ma_groups["평균손실"].round(1)
    ma_groups = ma_groups.rename(columns={"ma_pattern": "MA 패턴"})
    ma_groups = ma_groups.sort_values("승률", ascending=False)

    st.dataframe(
        ma_groups[["MA 패턴", "거래수", "승리", "승률", "평균수익", "평균손실"]],
        use_container_width=True,
        hide_index=True,
    )

    # ── 섹터별 성과 ────────────────────────────────────
    st.markdown("#### 섹터별 성과")
    sector_groups = trades.groupby("sector").agg(
        거래수=("result", "count"),
        승리=("result", lambda x: (x == "승").sum()),
        평균수익=("peak_pct", "mean"),
    ).reset_index()
    sector_groups["승률"] = (sector_groups["승리"] / sector_groups["거래수"] * 100).round(1)
    sector_groups["평균수익"] = sector_groups["평균수익"].round(1)
    sector_groups = sector_groups.rename(columns={"sector": "섹터"})
    sector_groups = sector_groups.sort_values("거래수", ascending=False)

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=sector_groups["섹터"], y=sector_groups["거래수"],
        name="거래수",
        marker_color="#3b82f6",
        text=sector_groups["거래수"],
        textposition="outside",
        textfont=dict(color="#e2e8f0", size=11),
    ))
    fig3.add_trace(go.Scatter(
        x=sector_groups["섹터"], y=sector_groups["승률"],
        name="승률 (%)",
        mode="lines+markers",
        yaxis="y2",
        line=dict(color="#22c55e", width=2),
        marker=dict(size=7),
    ))
    fig3.update_layout(
        plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
        height=300,
        margin=dict(l=0, r=40, t=10, b=0),
        legend=dict(font=dict(color="#7a8599", size=10), orientation="h", y=-0.2),
        xaxis=dict(color="#7a8599"),
        yaxis=dict(showgrid=True, gridcolor="#1e2530", color="#7a8599"),
        yaxis2=dict(overlaying="y", side="right", showgrid=False, color="#22c55e",
                    range=[0, 110]),
        font=dict(color="#e2e8f0"),
        bargap=0.3,
    )
    st.plotly_chart(fig3, use_container_width=True)
