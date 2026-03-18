"""🛡️ 리스크 관리 — 포지션 사이징, 비중 관리, R:R 분포, 손익 한도"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def render():
    trades = st.session_state.trades
    positions = st.session_state.positions
    equity = st.session_state.equity_curve

    st.markdown("### 🛡️ 리스크 관리")

    # ── 포지션 사이징 계산기 ────────────────────────────
    st.markdown("#### 🔢 포지션 사이징 계산기")

    rc1, rc2, rc3, rc4 = st.columns(4)
    with rc1:
        account = st.number_input("계좌 잔고 (원)", value=52340000, step=1000000, format="%d")
    with rc2:
        risk_pct = st.number_input("위험 비율 (%)", value=2.0, step=0.5, min_value=0.5, max_value=10.0)
    with rc3:
        entry_price = st.number_input("진입가 (원)", value=100000, step=1000, format="%d")
    with rc4:
        stop_price = st.number_input("손절가 (원)", value=93500, step=1000, format="%d")

    if entry_price > 0 and stop_price > 0 and entry_price != stop_price:
        risk_amount = account * risk_pct / 100
        per_share_risk = abs(entry_price - stop_price)
        position_size = int(risk_amount / per_share_risk) if per_share_risk > 0 else 0
        total_invest = position_size * entry_price
        invest_pct = (total_invest / account * 100) if account > 0 else 0
        potential_loss = position_size * per_share_risk

        sc1, sc2, sc3, sc4 = st.columns(4)
        results = [
            (sc1, "매수 수량", f"{position_size:,}주", "neutral"),
            (sc2, "투자 금액", f"₩{total_invest/1e4:,.0f}만", "neutral"),
            (sc3, "계좌 대비", f"{invest_pct:.1f}%", "positive" if invest_pct < 30 else "negative"),
            (sc4, "최대 손실", f"₩{potential_loss/1e4:,.0f}만", "negative"),
        ]
        for col, label, val, cls in results:
            with col:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value {cls}">{val}</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 포지션 비중 + R:R 분포 ─────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### ⚖️ 포지션 비중")
        if len(positions) > 0:
            cash_weight = 100 - positions["weight"].sum()
            labels = list(positions["name"]) + ["현금"]
            values = list(positions["weight"]) + [cash_weight]
            colors = ["#14b8a6", "#3b82f6", "#a78bfa", "#eab308", "#ef4444", "#1e2530"]

            fig = go.Figure(go.Pie(
                labels=labels, values=values, hole=0.55,
                marker=dict(colors=colors[:len(labels)]),
                textinfo="label+percent",
                textfont=dict(size=11, color="#e2e8f0"),
            ))
            fig.update_layout(
                plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
                height=300, margin=dict(l=0, r=0, t=10, b=0),
                showlegend=False, font=dict(color="#e2e8f0"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("보유 포지션이 없습니다.")

    with col2:
        st.markdown("#### 📐 R:R 비율 분포")
        # R:R = |peak| / |min_low|  (리워드/리스크 근사)
        rr_data = trades.copy()
        rr_data["rr"] = (rr_data["peak_pct"].abs() / rr_data["min_low_pct"].abs()).round(2)
        rr_data = rr_data.dropna(subset=["rr"])
        rr_data = rr_data[rr_data["rr"] < 50]  # 이상치 제거

        fig2 = go.Figure(go.Histogram(
            x=rr_data["rr"],
            nbinsx=12,
            marker_color="#14b8a6",
            opacity=0.8,
        ))
        fig2.add_vline(x=rr_data["rr"].median(), line_dash="dash",
                       line_color="#eab308", annotation_text=f"중앙값: {rr_data['rr'].median():.1f}",
                       annotation_font_color="#eab308")
        fig2.update_layout(
            plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
            height=300, margin=dict(l=0, r=0, t=10, b=30),
            xaxis=dict(title="R:R 비율", color="#7a8599", showgrid=True, gridcolor="#1e2530"),
            yaxis=dict(title="빈도", color="#7a8599", showgrid=True, gridcolor="#1e2530"),
            font=dict(color="#e2e8f0"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 일별 P&L 한도 ─────────────────────────────────
    st.markdown("#### 📈 일별 손익 변동")
    eq = equity.copy()
    eq["daily_return"] = eq["value"].pct_change() * 100
    eq = eq.dropna()

    fig3 = go.Figure()
    colors = ["#22c55e" if v >= 0 else "#ef4444" for v in eq["daily_return"]]
    fig3.add_trace(go.Bar(
        x=eq["date"], y=eq["daily_return"],
        marker_color=colors,
    ))

    # 한도선
    daily_limit = 3.0
    fig3.add_hline(y=daily_limit, line_dash="dash", line_color="#eab308",
                   annotation_text=f"+{daily_limit}% 한도", annotation_font_color="#eab308")
    fig3.add_hline(y=-daily_limit, line_dash="dash", line_color="#ef4444",
                   annotation_text=f"-{daily_limit}% 한도", annotation_font_color="#ef4444")

    fig3.update_layout(
        plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
        height=300, margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(color="#7a8599"),
        yaxis=dict(showgrid=True, gridcolor="#1e2530", color="#7a8599",
                   zeroline=True, zerolinecolor="#3b3b3b"),
        font=dict(color="#e2e8f0"),
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 리스크 요약 ────────────────────────────────────
    st.markdown("#### 📋 리스크 요약")
    max_dd = equity["value"].max()
    current = equity["value"].iloc[-1]
    dd_pct = ((max_dd - current) / max_dd * 100) if max_dd > 0 else 0
    avg_rr = rr_data["rr"].mean() if len(rr_data) else 0
    max_loss_trade = trades["min_low_pct"].min()
    consecutive_losses = 0
    temp = 0
    for r in trades.sort_values("date")["result"]:
        if r == "패":
            temp += 1
            consecutive_losses = max(consecutive_losses, temp)
        else:
            temp = 0

    risk_items = [
        ("현재 낙폭", f"{dd_pct:.1f}%", dd_pct > 5),
        ("평균 R:R", f"{avg_rr:.1f}", avg_rr < 2),
        ("최대 단일 손실", f"{max_loss_trade:+.1f}%", max_loss_trade < -10),
        ("최대 연패", f"{consecutive_losses}회", consecutive_losses >= 3),
    ]

    for label, value, is_warning in risk_items:
        icon = "🔴" if is_warning else "🟢"
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px; padding:8px 0; border-bottom:1px solid #1e2530;">
            <span>{icon}</span>
            <span style="color:#7a8599; font-size:13px; min-width:120px;">{label}</span>
            <span style="color:#e2e8f0; font-size:14px; font-weight:600;">{value}</span>
        </div>""", unsafe_allow_html=True)
