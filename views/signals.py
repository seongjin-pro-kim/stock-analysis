"""📡 시그널 — 활성 시그널, 워치리스트, 갭 감지, 볼륨 알림"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def render():
    signals = st.session_state.signals
    trades = st.session_state.trades

    st.markdown("### 📡 시그널 & 워치리스트")

    # ── 요약 KPI ────────────────────────────────────────
    total_sig = len(signals)
    strong = len(signals[signals["strength"] == "강"])
    medium = len(signals[signals["strength"] == "중"])
    weak = len(signals[signals["strength"] == "약"])

    c1, c2, c3, c4 = st.columns(4)
    kpis = [
        (c1, "활성 시그널", f"{total_sig}개", "neutral"),
        (c2, "강 시그널", f"{strong}개", "positive"),
        (c3, "중 시그널", f"{medium}개", "neutral"),
        (c4, "약 시그널", f"{weak}개", "negative"),
    ]
    for col, label, val, cls in kpis:
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value {cls}">{val}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 활성 시그널 카드 ────────────────────────────────
    st.markdown("#### 🎯 활성 시그널")
    for _, s in signals.iterrows():
        strength_colors = {"강": "#22c55e", "중": "#eab308", "약": "#ef4444"}
        s_color = strength_colors.get(s["strength"], "#7a8599")

        # 목표까지 거리
        dist_target = ((s["target_price"] - s["current_price"]) / s["current_price"] * 100)
        dist_stop = ((s["current_price"] - s["stop_price"]) / s["current_price"] * 100)

        # 진행바 (현재 위치 비율)
        total_range = s["target_price"] - s["stop_price"]
        progress = (s["current_price"] - s["stop_price"]) / total_range * 100 if total_range > 0 else 50

        from utils import market_badge
        vol_icon = "🔊" if s["volume_spike"] else "🔇"

        st.markdown(f"""
        <div style="background:#111820; border:1px solid #1e2530; border-radius:10px; padding:16px; margin-bottom:10px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="color:#e2e8f0; font-weight:600; font-size:15px;">{s['name']}</span>
                    <span style="color:#7a8599; font-size:12px;">{s['code']}</span>
                    {market_badge(s['market'])}
                </div>
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="color:{s_color}; font-weight:700; font-size:14px; border:1px solid {s_color}; padding:2px 10px; border-radius:20px;">{s['strength']}</span>
                </div>
            </div>
            <div style="display:flex; gap:24px; font-size:12px; margin-bottom:10px;">
                <div><span style="color:#7a8599;">갭비율</span> <span style="color:#e2e8f0; font-weight:600;">{s['gap_rate']:.1f}%</span></div>
                <div><span style="color:#7a8599;">현재가</span> <span style="color:#e2e8f0; font-weight:600;">₩{s['current_price']:,}</span></div>
                <div><span style="color:#7a8599;">목표가</span> <span style="color:#14b8a6; font-weight:600;">₩{s['target_price']:,}</span></div>
                <div><span style="color:#7a8599;">손절가</span> <span style="color:#ef4444; font-weight:600;">₩{s['stop_price']:,}</span></div>
                <div><span style="color:#7a8599;">볼륨</span> <span>{vol_icon}</span></div>
            </div>
            <div style="display:flex; gap:16px; font-size:11px; margin-bottom:8px;">
                <span style="color:#14b8a6;">목표까지 {dist_target:+.1f}%</span>
                <span style="color:#ef4444;">손절까지 -{dist_stop:.1f}%</span>
            </div>
            <div style="background:#1e2530; border-radius:4px; height:6px; overflow:hidden;">
                <div style="background:linear-gradient(90deg, #ef4444, #eab308, #22c55e); width:{min(max(progress,0),100):.0f}%; height:100%; border-radius:4px;"></div>
            </div>
            <div style="display:flex; justify-content:space-between; font-size:10px; color:#7a8599; margin-top:4px;">
                <span>손절</span><span>현재</span><span>목표</span>
            </div>
            <div style="color:#7a8599; font-size:10px; margin-top:6px;">MA: {s['ma_pattern']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 갭 비율 분포 차트 ──────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📊 시그널 갭 비율")
        fig = go.Figure(go.Bar(
            x=signals["name"],
            y=signals["gap_rate"],
            marker_color=[strength_colors.get(s, "#7a8599") for s in signals["strength"]],
            text=[f"{v:.1f}%" for v in signals["gap_rate"]],
            textposition="outside",
            textfont=dict(color="#e2e8f0", size=11),
        ))
        fig.update_layout(
            plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
            height=280, margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(color="#7a8599"),
            yaxis=dict(showgrid=True, gridcolor="#1e2530", color="#7a8599"),
            font=dict(color="#e2e8f0"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 🔔 볼륨 스파이크 현황")
        vol_yes = len(signals[signals["volume_spike"] == True])
        vol_no = len(signals) - vol_yes

        fig2 = go.Figure(go.Pie(
            labels=["볼륨 스파이크", "일반 볼륨"],
            values=[vol_yes, vol_no],
            hole=0.55,
            marker=dict(colors=["#eab308", "#1e2530"]),
            textinfo="label+value",
            textfont=dict(size=12, color="#e2e8f0"),
        ))
        fig2.update_layout(
            plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
            height=280, margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False,
            font=dict(color="#e2e8f0"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── 최근 승률 높은 패턴 ────────────────────────────
    st.markdown("#### 🏆 고승률 MA 패턴 (이력 기반)")
    ma_stats = trades.groupby("ma_pattern").agg(
        count=("result", "count"),
        wins=("result", lambda x: (x == "승").sum()),
    ).reset_index()
    ma_stats["win_rate"] = (ma_stats["wins"] / ma_stats["count"] * 100).round(1)
    ma_stats = ma_stats.sort_values("win_rate", ascending=False).head(5)

    for _, m in ma_stats.iterrows():
        bar_w = min(m["win_rate"], 100)
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:6px;">
            <span style="color:#7a8599; font-size:11px; min-width:220px;">{m['ma_pattern']}</span>
            <div style="flex:1; background:#1e2530; border-radius:4px; height:8px; overflow:hidden;">
                <div style="background:#14b8a6; width:{bar_w}%; height:100%; border-radius:4px;"></div>
            </div>
            <span style="color:#e2e8f0; font-size:12px; font-weight:600; min-width:50px; text-align:right;">{m['win_rate']:.0f}%</span>
            <span style="color:#7a8599; font-size:11px;">({m['count']}건)</span>
        </div>""", unsafe_allow_html=True)
