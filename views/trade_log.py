"""📋 매매 기록 — 전체 거래 테이블, 필터 7종, 달력 히트맵"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def render():
    trades = st.session_state.trades.copy()

    st.markdown("### 📋 매매 기록")

    # ── 필터 행 (7열) ──────────────────────────────────
    fc1, fc2, fc3, fc4, fc5, fc6, fc7 = st.columns(7)
    with fc1:
        market_filter = st.selectbox("시장", ["전체", "KOSPI", "KOSDAQ"])
    with fc2:
        result_filter = st.selectbox("결과", ["전체", "승", "패"])
    with fc3:
        sectors = ["전체"] + sorted(trades["sector"].dropna().unique().tolist())
        sector_filter = st.selectbox("섹터", sectors)
    with fc4:
        if "grade" in trades.columns:
            grade_opts = ["전체"] + sorted([g for g in trades["grade"].dropna().unique()])
        else:
            grade_opts = ["전체"]
        grade_filter = st.selectbox("등급", grade_opts)
    with fc5:
        core_filter = st.selectbox("코어 여부", ["전체", "코어만", "코어 제외"])
    with fc6:
        if "rr_ratio" in trades.columns and trades["rr_ratio"].notna().any():
            rr_min = 0.0
            rr_max = float(trades["rr_ratio"].max())
            rr_threshold = st.slider(
                "최소 RR",
                min_value=0.0,
                max_value=round(rr_max, 1),
                value=min(1.5, round(rr_max, 1)),
                step=0.1,
            )
        else:
            rr_threshold = 0.0
            st.caption("RR 데이터 없음")
    with fc7:
        sort_by = st.selectbox("정렬", ["날짜 (최신)", "날짜 (오래된)", "갭비율 ↓", "최고수익 ↓", "소요일 ↑"])

    # ── 필터 적용 ──────────────────────────────────────
    filtered = trades.copy()
    if market_filter != "전체":
        filtered = filtered[filtered["market"] == market_filter]
    if result_filter != "전체":
        filtered = filtered[filtered["result"] == result_filter]
    if sector_filter != "전체":
        filtered = filtered[filtered["sector"] == sector_filter]

    if grade_filter != "전체" and "grade" in filtered.columns:
        filtered = filtered[filtered["grade"] == grade_filter]

    if "is_core" in filtered.columns:
        if core_filter == "코어만":
            filtered = filtered[filtered["is_core"] == True]
        elif core_filter == "코어 제외":
            filtered = filtered[filtered["is_core"] == False]

    if "rr_ratio" in filtered.columns and rr_threshold > 0:
        filtered = filtered[filtered["rr_ratio"] >= rr_threshold]

    # ── 정렬 ──────────────────────────────────────────
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

    # 새 컬럼 존재 여부 확인
    has_signal_date = "signal_date" in filtered.columns
    has_rr_ratio = "rr_ratio" in filtered.columns

    rows_html = ""
    for _, r in filtered.iterrows():
        peak_color = "#22c55e" if r["peak_pct"] >= 20 else ("#eab308" if r["peak_pct"] >= 10 else "#ef4444")
        low_color = "#ef4444" if r["min_low_pct"] < -5 else "#7a8599"

        # 신호일 셀
        if has_signal_date and pd.notna(r.get("signal_date")):
            try:
                sig_date_str = pd.to_datetime(r["signal_date"]).strftime("%Y-%m-%d")
            except Exception:
                sig_date_str = "-"
        else:
            sig_date_str = "-"

        # 시그널 RR 셀
        if has_rr_ratio and pd.notna(r.get("rr_ratio")):
            rr_val = f"{float(r['rr_ratio']):.2f}"
            rr_color = "#22c55e" if float(r["rr_ratio"]) >= 2.0 else ("#eab308" if float(r["rr_ratio"]) >= 1.5 else "#ef4444")
        else:
            rr_val = "-"
            rr_color = "#7a8599"

        rows_html += f"""
        <tr style="border-bottom:1px solid #1e2530;">
            <td style="padding:8px 6px; color:#7a8599; font-size:12px;">{r['date'].strftime('%Y-%m-%d') if hasattr(r['date'], 'strftime') else r['date']}</td>
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
            <td style="padding:8px 6px; color:#7a8599; font-size:11px;">{sig_date_str}</td>
            <td style="padding:8px 6px; color:{rr_color}; text-align:right; font-weight:600;">{rr_val}</td>
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
                <th style="padding:8px 6px; color:#7a8599; text-align:left;">신호일</th>
                <th style="padding:8px 6px; color:#7a8599; text-align:right;">시그널 RR</th>
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
