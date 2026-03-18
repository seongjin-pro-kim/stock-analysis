"""🌐 시장 개요 — KOSPI/KOSDAQ 지수, 섹터 성과, 기관 수급"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def render():
    st.markdown("### 🌐 시장 개요")

    # ── 지수 정보 (시뮬레이션 데이터) ──────────────────
    col1, col2 = st.columns(2)

    indices = [
        {"name": "KOSPI", "value": 2685.42, "change": +12.35, "pct": +0.46,
         "col": col1, "color": "#3b82f6"},
        {"name": "KOSDAQ", "value": 872.15, "change": -3.21, "pct": -0.37,
         "col": col2, "color": "#a78bfa"},
    ]

    for idx in indices:
        with idx["col"]:
            sign = "+" if idx["change"] >= 0 else ""
            c_class = "positive" if idx["change"] >= 0 else "negative"

            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{idx['name']}</div>
                <div class="kpi-value" style="color:{idx['color']}">{idx['value']:,.2f}</div>
                <div class="kpi-sub {c_class}">{sign}{idx['change']:.2f} ({sign}{idx['pct']:.2f}%)</div>
            </div>""", unsafe_allow_html=True)

            # 미니 차트
            np.random.seed(hash(idx["name"]) % 2**32)
            days = 30
            base = idx["value"] * 0.97
            vals = [base]
            for i in range(days - 1):
                vals.append(vals[-1] * (1 + np.random.normal(0.001, 0.008)))

            fig = go.Figure(go.Scatter(
                y=vals, mode="lines",
                fill="tozeroy",
                fillcolor=f"rgba({','.join(str(int(idx['color'].lstrip('#')[i:i+2], 16)) for i in (0,2,4))},0.08)",
                line=dict(color=idx["color"], width=1.5),
            ))
            fig.update_layout(
                plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
                height=150, margin=dict(l=0, r=0, t=5, b=0),
                xaxis=dict(showticklabels=False, showgrid=False),
                yaxis=dict(showticklabels=False, showgrid=False),
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 섹터 성과 ──────────────────────────────────────
    st.markdown("#### 📊 섹터별 등락률")
    sectors = [
        {"name": "반도체", "change": 2.1}, {"name": "2차전지", "change": -1.3},
        {"name": "바이오", "change": 1.5}, {"name": "인터넷", "change": 0.8},
        {"name": "게임", "change": 3.2}, {"name": "엔터", "change": -0.5},
        {"name": "핀테크", "change": 1.8}, {"name": "자동차", "change": 0.3},
        {"name": "화장품", "change": -0.2}, {"name": "소재", "change": -1.8},
        {"name": "전자부품", "change": 0.9}, {"name": "가전", "change": -0.1},
        {"name": "지주", "change": 0.4}, {"name": "금융", "change": 1.1},
    ]
    sec_df = pd.DataFrame(sectors).sort_values("change", ascending=True)

    fig2 = go.Figure(go.Bar(
        y=sec_df["name"],
        x=sec_df["change"],
        orientation="h",
        marker_color=[("#22c55e" if v >= 0 else "#ef4444") for v in sec_df["change"]],
        text=[f"{v:+.1f}%" for v in sec_df["change"]],
        textposition="outside",
        textfont=dict(color="#e2e8f0", size=11),
    ))
    fig2.update_layout(
        plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
        height=400, margin=dict(l=80, r=40, t=10, b=0),
        xaxis=dict(showgrid=True, gridcolor="#1e2530", color="#7a8599",
                   zeroline=True, zerolinecolor="#3b3b3b"),
        yaxis=dict(color="#e2e8f0"),
        font=dict(color="#e2e8f0"),
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 기관/외국인 수급 ───────────────────────────────
    st.markdown("#### 🏦 기관/외국인 수급 (최근 5일)")
    flow_data = {
        "날짜": ["03/14", "03/13", "03/12", "03/11", "03/10"],
        "기관 순매수(억)": [+1250, -820, +340, +560, -1100],
        "외국인 순매수(억)": [-680, +1500, +220, -390, +880],
        "개인 순매수(억)": [-570, -680, -560, -170, +220],
    }
    flow_df = pd.DataFrame(flow_data)

    fig3 = go.Figure()
    colors = {"기관 순매수(억)": "#3b82f6", "외국인 순매수(억)": "#a78bfa", "개인 순매수(억)": "#eab308"}
    for col_name in ["기관 순매수(억)", "외국인 순매수(억)", "개인 순매수(억)"]:
        fig3.add_trace(go.Bar(
            x=flow_df["날짜"], y=flow_df[col_name],
            name=col_name.replace(" 순매수(억)", ""),
            marker_color=colors[col_name],
        ))

    fig3.update_layout(
        plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
        height=300, margin=dict(l=0, r=0, t=10, b=0),
        barmode="group",
        legend=dict(font=dict(color="#7a8599", size=11), orientation="h", y=-0.15),
        xaxis=dict(color="#7a8599"),
        yaxis=dict(showgrid=True, gridcolor="#1e2530", color="#7a8599",
                   zeroline=True, zerolinecolor="#3b3b3b"),
        font=dict(color="#e2e8f0"),
        bargap=0.25,
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 시장 뉴스/이벤트 ───────────────────────────────
    st.markdown("#### 📰 주요 이벤트")
    events = [
        {"date": "03/18", "title": "FOMC 의사록 공개", "impact": "중", "desc": "금리 동결 전망 유지"},
        {"date": "03/19", "title": "한국은행 기준금리 결정", "impact": "강", "desc": "25bp 인하 예상"},
        {"date": "03/20", "title": "미국 옵션 만기일", "impact": "약", "desc": "변동성 확대 가능"},
        {"date": "03/21", "title": "삼성전자 실적 프리뷰", "impact": "강", "desc": "HBM 매출 확대 전망"},
    ]
    impact_colors = {"강": "#ef4444", "중": "#eab308", "약": "#7a8599"}

    for e in events:
        ic = impact_colors.get(e["impact"], "#7a8599")
        st.markdown(f"""
        <div style="display:flex; align-items:center; gap:14px; padding:10px 0; border-bottom:1px solid #1e2530;">
            <span style="color:#7a8599; font-size:12px; min-width:50px;">{e['date']}</span>
            <span style="color:{ic}; font-size:10px; font-weight:700; border:1px solid {ic}; padding:1px 6px; border-radius:10px; min-width:24px; text-align:center;">{e['impact']}</span>
            <div>
                <div style="color:#e2e8f0; font-size:13px; font-weight:500;">{e['title']}</div>
                <div style="color:#7a8599; font-size:11px;">{e['desc']}</div>
            </div>
        </div>""", unsafe_allow_html=True)
