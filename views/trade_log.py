"""📋 매매 기록 — 전체 거래 테이블, 필터, 달력 히트맵"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def render():
    trades = st.session_state.trades.copy()

    st.markdown("### 📋 매매 기록")

    # ── 필터 행 ────────────────────────────────────────
    fc1, fc2, fc3, fc4 = st.columns(4)
    with fc1:
        market_filter = st.selectbox("시장", ["전체", "KOSPI", "KOSDAQ"])
    with fc2:
        result_filter = st.selectbox("결과", ["전체", "승", "패"])
    with fc3:
        sectors = ["전체"] + sorted(trades["sector"].unique().tolist())
        sector_filter = st.selectbox("섹터", sectors)
    with fc4:
        sort_by = st.selectbox("정렬", ["날짜 (최신)", "날짜 (오래된)", "갭비율 ↓", "최고수익 ↓", "소요일 ↑"])

    # 필터 적용
    filtered = trades.copy()
    if market_filter != "전체":
        filtered = filtered[filtered["market"] == market_filter]
    if result_filter != "전체":
        filtered = filtered[filtered["result"] == result_filter]
    if sector_filter != "전체":
        filtered = filtered[filtered["sector"] == sector_filter]

    # 정렬
    sort_map = {
        "날짜 (최신)": ("date", False),
        "날짜 (오래된)": ("date", True),
        "갭비율 ↓": ("gap_rate", False),
        "최고수익 ↓": ("peak_pct", False),
        "소요일 ↑": ("days_to_target", True),
    }
    sort_col, sort_asc = sort_map[sort_by]
    filtered = filtered.sort_values(sort_col, ascending=sort_asc)

    # 건수 표시
    st.markdown(f"<div style='color:#7a8599; font-size:13px; margin-bottom:8px;'>총 {len(filtered)}건 / {len(trades)}건</div>",
                unsafe_allow_html=True)

    # ── 거래 테이블 (HTML) ─────────────────────────────
    from utils import result_badge, market_badge

    rows_html = ""
    for _, r in filtered.iterrows():
        peak_color = "#22c55e" if r["peak_pct"] >= 20 else ("#eab308" if r["peak_pct"] >= 10 else "#ef4444")
        low_color = "#ef4444" if r["min_low_pct"] < -5 else "#7a8599"
        rows_html += f"""
        <tr style="border-bottom:1px solid #1e2530;">
            <td style="padding:8px 6px; color:#7a8599; font-size:12px;">{r['date'].strftime('%Y-%m-%d')}</td>
            <td style="padding:8px 6px; color:#e2e8f0; font-weight:500;">{r['name']}</td>
            <td style="padding:8px 6px; color:#7a8599; font-size:11px;">{r['code']}</td>
            <td style="padding:8px 6px;">{market_badge(r['market'])}</td>
            <td style="padding:8px 6px; color:#e2e8f0; text-align:right;">{r['gap_rate']:.1f}%</td>
            <td style="padding:8px 6px; color:#e2e8f0; text-align:right;">₩{r['entry_price']:,}</td>
            <td style="padding:8px 6px; color:#14b8a6; text-align:right;">₩{r['target_price']:,}</td>
            <td style="padding:8px 6px; color:#ef4444; text-align:right;">₩{r['stop_price']:,}</td>
            <td style="padding:8px 6px; text-align:center;">{result_badge(r['result'])}</td>
            <td style="padding:8px 6px; color:{peak_color}; text-align:right; font-weight:600;">{r['peak_pct']:+.1f}%</td>
            <td style="padding:8px 6px; color:{low_color}; text-align:right;">{r['min_low_pct']:+.1f}%</td>
            <td style="padding:8px 6px; color:#7a8599; text-align:right;">{r['days_to_target']}일</td>
            <td style="padding:8px 6px; color:#7a8599; font-size:10px;">{r['ma_pattern']}</td>
            <td style="padding:8px 6px; color:#7a8599;">{r['sector']}</td>
        </tr>"""

    st.markdown(f"""
    <div style="overflow-x:auto; border:1px solid #1e2530; border-radius:8px;">
    <table style="width:100%; border-collapse:collapse; font-size:12px; font-variant-numeric:tabular-nums; white-space:nowrap;">
        <thead>
            <tr style="border-bottom:2px solid #1e2530; background:#111820;">
                <th style="padding:8px 6px; color:#7a8599; text-align:left;">날짜</th>
                <th style="padding:8px 6px; color:#7a8599; text-align:left;">종목</th>
                <th style="padding:8px 6px; color:#7a8599; text-align:left;">코드</th>
                <th style="padding:8px 6px; color:#7a8599; text-align:left;">시장</th>
                <th style="padding:8px 6px; color:#7a8599; text-align:right;">갭비율</th>
                <th style="padding:8px 6px; color:#7a8599; text-align:right;">진입가</th>
                <th style="padding:8px 6px; color:#7a8599; text-align:right;">목표가</th>
                <th style="padding:8px 6px; color:#7a8599; text-align:right;">손절가</th>
                <th style="padding:8px 6px; color:#7a8599; text-align:center;">결과</th>
                <th style="padding:8px 6px; color:#7a8599; text-align:right;">최고</th>
                <th style="padding:8px 6px; color:#7a8599; text-align:right;">최저</th>
                <th style="padding:8px 6px; color:#7a8599; text-align:right;">소요일</th>
                <th style="padding:8px 6px; color:#7a8599; text-align:left;">MA</th>
                <th style="padding:8px 6px; color:#7a8599; text-align:left;">섹터</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 거래 달력 히트맵 ───────────────────────────────
    st.markdown("#### 📅 거래 달력")
    cal_data = trades.copy()
    cal_data["week"] = cal_data["date"].dt.isocalendar().week.astype(int)
    cal_data["dow"] = cal_data["date"].dt.dayofweek  # 0=Mon

    # 주별 x 요일별 거래 수
    heatmap = cal_data.groupby(["week", "dow"]).size().reset_index(name="count")
    dow_labels = ["월", "화", "수", "목", "금", "토", "일"]

    # pivot
    weeks = sorted(heatmap["week"].unique())
    matrix = np.zeros((7, len(weeks)))
    for _, row in heatmap.iterrows():
        wi = weeks.index(row["week"])
        matrix[int(row["dow"]), wi] = row["count"]

    fig = go.Figure(go.Heatmap(
        z=matrix,
        x=[f"W{w}" for w in weeks],
        y=dow_labels,
        colorscale=[[0, "#111820"], [0.5, "#14b8a6"], [1, "#22c55e"]],
        showscale=False,
        hovertemplate="주: %{x}<br>요일: %{y}<br>거래 수: %{z}<extra></extra>",
    ))
    fig.update_layout(
        plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
        height=200,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(color="#7a8599", side="top"),
        yaxis=dict(color="#7a8599", autorange="reversed"),
        font=dict(color="#e2e8f0"),
    )
    st.plotly_chart(fig, use_container_width=True)
