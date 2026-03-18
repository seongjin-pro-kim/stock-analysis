"""🛡️ 리스크 관리 — 설명 툴팁, 주간 P&L 4개, 단일색 바, 링크아이콘 설명"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go


def render():
    trades = st.session_state.trades
    positions = st.session_state.positions
    equity = st.session_state.equity_curve

    st.markdown("### 🛡️ 리스크 관리")

    # ── 포지션 사이징 계산기 (설명 포함) ─────────────────
    st.markdown("""
    <div style="display:flex; align-items:center; gap:6px; margin-bottom:8px;">
        <span style="color:#e2e8f0; font-size:15px; font-weight:600;">포지션 사이징 계산기</span>
        <div style="position:relative; display:inline-block;">
            <span class="info-tip">?</span>
            <div class="info-content">
                <strong style="color:#e2e8f0;">포지션 사이징이란?</strong><br>
                한 거래에서 잃어도 되는 최대 금액(위험 금액)을 정하고,<br>
                진입가와 손절가 사이의 차이로 나누어 <strong>적정 매수 수량</strong>을 계산합니다.<br><br>
                <strong>공식:</strong> 매수수량 = (계좌잔고 × 위험비율%) ÷ |진입가 - 손절가|<br><br>
                예) 5000만원 계좌, 2% 위험 = 100만원 리스크<br>
                진입가 10만원, 손절가 9.35만원 → 주당 리스크 6,500원<br>
                → 100만 ÷ 6,500 = 약 153주
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

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
        st.markdown("#### 포지션 비중")
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
        st.markdown("""
        <div style="display:flex; align-items:center; gap:6px; margin-bottom:4px;">
            <span style="color:#e2e8f0; font-size:15px; font-weight:600;">R:R 비율 분포</span>
            <div style="position:relative; display:inline-block;">
                <span class="info-tip">?</span>
                <div class="info-content">
                    <strong style="color:#e2e8f0;">R:R (Risk:Reward) 비율이란?</strong><br>
                    실제 거래에서 달성한 <strong>최고 수익률 ÷ 최대 하락률</strong>의 비율입니다.<br><br>
                    <strong>읽는 법:</strong><br>
                    • R:R > 2.0 → 리스크 대비 2배 이상 수익 (우수)<br>
                    • R:R 1.0~2.0 → 리스크와 수익이 비슷 (보통)<br>
                    • R:R < 1.0 → 리스크가 수익보다 큼 (주의)<br><br>
                    <strong>히스토그램:</strong> X축은 R:R 비율, Y축은 해당 구간의 거래 건수.<br>
                    노란 점선은 전체 거래의 중앙값입니다.
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        completed = trades[trades["result"].isin(["승", "패"])]
        rr_data = completed.copy()
        rr_data["rr"] = (rr_data["peak_pct"].abs() / rr_data["min_low_pct"].abs()).round(2)
        rr_data = rr_data.dropna(subset=["rr"])
        rr_data = rr_data[rr_data["rr"] < 50]

        # 톤다운 색상 (#14b8a6 → 어두운 톤)
        fig2 = go.Figure(go.Histogram(
            x=rr_data["rr"], nbinsx=12,
            marker_color="#0d5c54",
            opacity=0.9,
        ))
        if len(rr_data) > 0:
            fig2.add_vline(x=rr_data["rr"].median(), line_dash="dash",
                           line_color="#eab308",
                           annotation_text=f"중앙값: {rr_data['rr'].median():.1f}",
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

    # ── 주간 P&L (4주간, 단일색 진한/옅은 톤) ────────────
    st.markdown("#### 주간 손익 변동")

    total_eq = equity.groupby("date")["value"].sum().reset_index().sort_values("date")
    total_eq["daily_return"] = total_eq["value"].pct_change() * 100
    total_eq = total_eq.dropna()

    if len(total_eq) >= 5:
        # 주차 구분
        total_eq["week_num"] = ((total_eq.index - total_eq.index[0]) // 5)
        weeks = sorted(total_eq["week_num"].unique())[-4:]  # 최근 4주

        week_cols = st.columns(4)
        for idx, week in enumerate(weeks):
            with week_cols[idx]:
                week_data = total_eq[total_eq["week_num"] == week]
                week_label = f"Week {int(week) + 1}"

                # 단일색 두가지 톤
                colors = ["#14b8a6" if v >= 0 else "#0d5c54" for v in week_data["daily_return"]]

                fig_w = go.Figure(go.Bar(
                    x=week_data["date"].dt.strftime("%m/%d"),
                    y=week_data["daily_return"],
                    marker_color=colors,
                ))
                fig_w.update_layout(
                    plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
                    height=180, margin=dict(l=0, r=0, t=24, b=0),
                    title=dict(text=week_label, font=dict(color="#7a8599", size=11), x=0.5),
                    xaxis=dict(color="#7a8599", tickfont=dict(size=9)),
                    yaxis=dict(showgrid=True, gridcolor="#1e2530", color="#7a8599",
                               zeroline=True, zerolinecolor="#3b3b3b", tickfont=dict(size=9)),
                    font=dict(color="#e2e8f0"),
                )
                st.plotly_chart(fig_w, use_container_width=True)

                # 주간 합계
                week_total = week_data["daily_return"].sum()
                color = "#22c55e" if week_total >= 0 else "#ef4444"
                st.markdown(f"<div style='text-align:center; font-size:12px; color:{color}; font-weight:600;'>{week_total:+.2f}%</div>",
                            unsafe_allow_html=True)
    else:
        st.info("주간 손익을 표시하기에 데이터가 부족합니다.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 리스크 요약 ────────────────────────────────────
    st.markdown("#### 리스크 요약")
    total_eq_vals = equity.groupby("date")["value"].sum().reset_index()
    max_dd = total_eq_vals["value"].max()
    current = total_eq_vals["value"].iloc[-1]
    dd_pct = ((max_dd - current) / max_dd * 100) if max_dd > 0 else 0
    avg_rr = rr_data["rr"].mean() if len(rr_data) else 0

    completed_sorted = completed.sort_values("date")
    max_loss_trade = completed["min_low_pct"].min() if len(completed) else 0
    consecutive_losses = 0
    temp = 0
    for r in completed_sorted["result"]:
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
        icon_color = "#ef4444" if is_warning else "#22c55e"
        icon = "●"
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px; padding:8px 0; border-bottom:1px solid #1e2530;">
            <span style="color:{icon_color}; font-size:8px;">{icon}</span>
            <span style="color:#7a8599; font-size:13px; min-width:120px;">{label}</span>
            <span style="color:#e2e8f0; font-size:14px; font-weight:600;">{value}</span>
        </div>""", unsafe_allow_html=True)
