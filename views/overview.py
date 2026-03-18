"""🏠 메인 대시보드 — KPI, 자산 추이, 포지션, 최근 매매"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def render():
    trades = st.session_state.trades
    equity = st.session_state.equity_curve
    positions = st.session_state.positions

    # ── KPI 계산 ───────────────────────────────────────
    total_trades = len(trades)
    wins = len(trades[trades["result"] == "승"])
    losses = len(trades[trades["result"] == "패"])
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    avg_days = trades[trades["result"] == "승"]["days_to_target"].mean()
    total_pnl = equity["value"].iloc[-1] - equity["value"].iloc[0]
    pnl_pct = (total_pnl / equity["value"].iloc[0]) * 100
    current_capital = equity["value"].iloc[-1]

    # ── KPI 카드 행 ────────────────────────────────────
    st.markdown("### 📊 핵심 지표")
    c1, c2, c3, c4, c5 = st.columns(5)

    def _kpi(col, label, value, sub="", color_class="neutral"):
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value {color_class}">{value}</div>
                <div class="kpi-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    _kpi(c1, "총 거래", f"{total_trades}건",
         f"승 {wins} · 패 {losses}", "neutral")
    _kpi(c2, "승률", f"{win_rate:.1f}%",
         f"20봉 기준", "positive" if win_rate >= 60 else "negative")
    _kpi(c3, "평균 도달일",
         f"{avg_days:.1f}일" if pd.notna(avg_days) else "—",
         "목표 도달까지", "neutral")
    _kpi(c4, "총 손익",
         f"₩{total_pnl/1e4:,.0f}만",
         f"{pnl_pct:+.1f}%", "positive" if total_pnl >= 0 else "negative")
    _kpi(c5, "현재 자산",
         f"₩{current_capital/1e4:,.0f}만",
         "평가 기준", "neutral")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 자산 추이 + 포지션 ─────────────────────────────
    col_chart, col_pos = st.columns([3, 1])

    with col_chart:
        st.markdown("### 💰 자산 추이")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=equity["date"], y=equity["value"],
            mode="lines",
            fill="tozeroy",
            fillcolor="rgba(20,184,166,0.08)",
            line=dict(color="#14b8a6", width=2),
            hovertemplate="날짜: %{x|%m/%d}<br>자산: ₩%{y:,.0f}<extra></extra>",
        ))
        fig.update_layout(
            plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
            margin=dict(l=0, r=0, t=10, b=0),
            height=300,
            xaxis=dict(showgrid=False, color="#7a8599"),
            yaxis=dict(showgrid=True, gridcolor="#1e2530", color="#7a8599",
                       tickformat=",.0f"),
            font=dict(color="#e2e8f0"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_pos:
        st.markdown("### 📌 보유 포지션")
        if len(positions) > 0:
            fig2 = go.Figure(go.Pie(
                labels=positions["name"],
                values=positions["weight"],
                hole=0.55,
                marker=dict(colors=["#14b8a6", "#3b82f6", "#a78bfa",
                                     "#eab308", "#ef4444"]),
                textinfo="label+percent",
                textfont=dict(size=11, color="#e2e8f0"),
            ))
            fig2.update_layout(
                plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
                margin=dict(l=0, r=0, t=10, b=0),
                height=260,
                showlegend=False,
                font=dict(color="#e2e8f0"),
            )
            st.plotly_chart(fig2, use_container_width=True)

            for _, p in positions.iterrows():
                color = "#22c55e" if p["pnl"] >= 0 else "#ef4444"
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:4px 0; font-size:13px;">
                    <span style="color:#e2e8f0">{p['name']}</span>
                    <span style="color:{color}; font-weight:600">{p['pnl']:+.1f}%</span>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("보유 포지션이 없습니다.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 최근 매매 ──────────────────────────────────────
    st.markdown("### 🕐 최근 매매")
    recent = trades.sort_values("date", ascending=False).head(8).copy()
    recent["date_str"] = recent["date"].dt.strftime("%m/%d")

    from utils import result_badge, market_badge

    rows_html = ""
    for _, r in recent.iterrows():
        pnl_color = "#22c55e" if r["peak_pct"] >= 20 else "#ef4444"
        rows_html += f"""
        <tr style="border-bottom:1px solid #1e2530;">
            <td style="padding:8px; color:#7a8599;">{r['date_str']}</td>
            <td style="padding:8px; color:#e2e8f0; font-weight:500;">{r['name']}</td>
            <td style="padding:8px;">{market_badge(r['market'])}</td>
            <td style="padding:8px; color:#e2e8f0; text-align:right;">{r['gap_rate']:.1f}%</td>
            <td style="padding:8px; text-align:center;">{result_badge(r['result'])}</td>
            <td style="padding:8px; color:{pnl_color}; text-align:right; font-weight:600;">{r['peak_pct']:+.1f}%</td>
            <td style="padding:8px; color:#7a8599; text-align:right;">{r['days_to_target']}일</td>
        </tr>"""

    st.markdown(f"""
    <div style="overflow-x:auto;">
    <table style="width:100%; border-collapse:collapse; font-size:13px; font-variant-numeric:tabular-nums;">
        <thead>
            <tr style="border-bottom:2px solid #1e2530;">
                <th style="padding:8px; color:#7a8599; text-align:left;">날짜</th>
                <th style="padding:8px; color:#7a8599; text-align:left;">종목</th>
                <th style="padding:8px; color:#7a8599; text-align:left;">시장</th>
                <th style="padding:8px; color:#7a8599; text-align:right;">갭비율</th>
                <th style="padding:8px; color:#7a8599; text-align:center;">결과</th>
                <th style="padding:8px; color:#7a8599; text-align:right;">최고수익</th>
                <th style="padding:8px; color:#7a8599; text-align:right;">소요일</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
    </div>""", unsafe_allow_html=True)
