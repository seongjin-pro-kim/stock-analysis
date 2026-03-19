"""▦ 매매 성과 분석 — 톤다운 아이콘, 개선된 프리뷰, 3배 행간격, 차트색상 변경"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils import fmt_date_short


def _preview_table(items, cols, title=""):
    """프리뷰용 미니 테이블 HTML (툴팁 내부)"""
    if len(items) == 0:
        return "<div style='color:#7a8599;'>데이터 없음</div>"
    header = "".join(f"<th style='padding:3px 6px; color:#7a8599; font-size:10px; text-align:left;'>{c}</th>" for c in cols)
    rows = ""
    for item in items:
        cells = "".join(f"<td style='padding:3px 6px; color:#e2e8f0; font-size:10px;'>{v}</td>" for v in item)
        rows += f"<tr style='border-bottom:1px solid #1e2530;'>{cells}</tr>"
    return f"""<table style='width:100%; border-collapse:collapse;'>
        <thead><tr style='border-bottom:1px solid #2a3545;'>{header}</tr></thead>
        <tbody>{rows}</tbody></table>"""


def render():
    trades = st.session_state.trades
    equity = st.session_state.equity_curve

    st.markdown("### ▸ 매매 성과 분석")

    completed = trades[trades["result"].isin(["승", "패"])]
    total = len(completed)
    wins = completed[completed["result"] == "승"]
    losses = completed[completed["result"] == "패"]
    win_count = len(wins)
    loss_count = len(losses)
    win_rate = (win_count / total * 100) if total else 0

    avg_peak = completed["peak_pct"].mean() if total else 0
    avg_loss = completed["min_low_pct"].mean() if total else 0
    avg_win_peak = wins["peak_pct"].mean() if win_count else 0
    avg_loss_peak = losses["min_low_pct"].mean() if loss_count else 0
    avg_days_win = wins["days_to_target"].mean() if win_count else 0
    avg_days_loss = losses["days_to_target"].mean() if loss_count else 0

    total_eq = equity.groupby("date")["value"].sum().reset_index()
    max_val = total_eq["value"].max()
    max_dd_pct = ((max_val - total_eq["value"].min()) / max_val) * 100 if max_val > 0 else 0

    profit_factor = (win_count * avg_win_peak / (loss_count * abs(avg_loss_peak))) if (loss_count and avg_loss_peak) else 0

    # 프리뷰 데이터 준비 — 매도일자 기준 (date = 매수일이지만 completed = 매도 완료)
    recent_wins = wins.sort_values("date", ascending=False).head(7)
    recent_losses = losses.sort_values("date", ascending=False).head(7)
    top_peak = completed.sort_values("peak_pct", ascending=False).head(7)
    worst_low = completed.sort_values("min_low_pct", ascending=True).head(7)

    # 승리 평균 소요일 프리뷰: 종목, 기대값, 소요일 (오름차순 7개)
    top_days_win = wins.sort_values("days_to_target", ascending=True).head(7)
    # 패배 평균 소요일 프리뷰: 종목, 기대값, 소요일 (오름차순 7개)
    top_days_loss = losses.sort_values("days_to_target", ascending=True).head(7)
    # 최대 낙폭 프리뷰: 종목, 손익비, 소요일 (오름차순 7개)
    worst_dd = completed.sort_values("min_low_pct", ascending=True).head(7)

    # 평균 RR/기대값
    avg_rr_wins = wins["rr_ratio"].mean() if "rr_ratio" in wins.columns and win_count else 0
    avg_ev_wins = wins["expected_value"].mean() if "expected_value" in wins.columns and win_count else 0
    avg_rr_losses = losses["rr_ratio"].mean() if "rr_ratio" in losses.columns and loss_count else 0
    avg_ev_losses = losses["expected_value"].mean() if "expected_value" in losses.columns and loss_count else 0

    # ── 12개 핵심 지표 (마우스오버 프리뷰 포함) ─────────
    st.markdown("#### 핵심 지표")

    def _kpi_with_preview(col, label, value, cls, preview_html=""):
        with col:
            if preview_html:
                st.markdown(f"""
                <div class="tooltip-wrapper" style="width:100%;">
                    <div class="kpi-card" style="width:100%;">
                        <div class="kpi-label">{label}</div>
                        <div class="kpi-value {cls}">{value}</div>
                    </div>
                    <div class="tooltip-box" style="bottom:auto; top:110%; left:0; transform:none;">
                        {preview_html}
                    </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value {cls}">{value}</div>
                </div>""", unsafe_allow_html=True)

    # Row 1  (3배 행간격은 CSS h3/h4 margin으로 처리됨; 행 사이 추가 간격)
    cols = st.columns(4)
    _kpi_with_preview(cols[0], "총 거래 수", f"{total}건", "")

    # 승리 — 프리뷰: 매도일 기준 종목, 수익(손실)율 7개 + 평균 손익비, 평균 기대값
    win_preview = _preview_table(
        [[fmt_date_short(r["date"]), r["name"], f"{r['peak_pct']:+.1f}%"] for _, r in recent_wins.iterrows()],
        ["날짜", "종목", "수익%"]
    ) + f"<div style='margin-top:6px; font-size:10px; color:#7a8599;'>평균 RR: {avg_rr_wins:.2f} · 평균 기대값: {avg_ev_wins:.1f}</div>"
    _kpi_with_preview(cols[1], "승리", f"{win_count}건", "positive", win_preview)

    # 패배 — 프리뷰: 매도일 기준 종목, 손실율 7개 + 평균 손익비, 평균 기대값
    loss_preview = _preview_table(
        [[fmt_date_short(r["date"]), r["name"], f"{r['min_low_pct']:+.1f}%"] for _, r in recent_losses.iterrows()],
        ["날짜", "종목", "손실%"]
    ) + f"<div style='margin-top:6px; font-size:10px; color:#7a8599;'>평균 RR: {avg_rr_losses:.2f} · 평균 기대값: {avg_ev_losses:.1f}</div>"
    _kpi_with_preview(cols[2], "패배", f"{loss_count}건", "negative", loss_preview)
    _kpi_with_preview(cols[3], "승률", f"{win_rate:.1f}%", "positive" if win_rate >= 60 else "negative")

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # Row 2
    cols = st.columns(4)
    peak_preview = _preview_table(
        [[r["name"], f"{r['peak_pct']:+.1f}%"] for _, r in top_peak.iterrows()],
        ["종목", "최고수익%"]
    )
    _kpi_with_preview(cols[0], "평균 최고수익", f"{avg_peak:+.1f}%", "positive", peak_preview)
    low_preview = _preview_table(
        [[r["name"], f"{r['min_low_pct']:+.1f}%"] for _, r in worst_low.iterrows()],
        ["종목", "최저%"]
    )
    _kpi_with_preview(cols[1], "평균 최저", f"{avg_loss:+.1f}%", "negative", low_preview)
    _kpi_with_preview(cols[2], "승리 평균 수익", f"{avg_win_peak:+.1f}%", "positive")
    _kpi_with_preview(cols[3], "패배 평균 손실", f"{avg_loss_peak:+.1f}%", "negative")

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

    # Row 3
    cols = st.columns(4)
    # 승리 평균 소요일 — 프리뷰: 종목, 기대값, 소요일 오름차순 7개
    days_win_preview = _preview_table(
        [[r["name"], f"{r.get('expected_value', 0):.1f}", f"{int(r['days_to_target'])}일"] for _, r in top_days_win.iterrows()],
        ["종목", "기대값", "소요일"]
    )
    _kpi_with_preview(cols[0], "승리 평균 소요일", f"{avg_days_win:.1f}일", "", days_win_preview)

    # 패배 평균 소요일 — 프리뷰: 종목, 기대값, 소요일 오름차순 7개
    days_loss_preview = _preview_table(
        [[r["name"], f"{r.get('expected_value', 0):.1f}", f"{int(r['days_to_target'])}일"] for _, r in top_days_loss.iterrows()],
        ["종목", "기대값", "소요일"]
    )
    _kpi_with_preview(cols[1], "패배 평균 소요일", f"{avg_days_loss:.1f}일", "", days_loss_preview)

    # 최대 낙폭 — 프리뷰: 종목, 손익비, 소요일 오름차순 7개
    dd_preview = _preview_table(
        [[r["name"], f"{r.get('rr_ratio', 0):.2f}", f"{int(r['days_to_target'])}일"] for _, r in worst_dd.iterrows()],
        ["종목", "손익비", "소요일"]
    )
    _kpi_with_preview(cols[2], "최대 낙폭", f"{max_dd_pct:.1f}%", "negative", dd_preview)
    _kpi_with_preview(cols[3], "수익 인자", f"{profit_factor:.2f}",
                     "positive" if profit_factor > 1 else "negative")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 차트 4열: 갭비율, 결과분포, RR구간, 기대값구간 ──
    col1, col2 = st.columns(2)

    # 갭 비율 범위별 성과 — 막대 색상 진하게 + 투명도 60%
    with col1:
        st.markdown("#### 갭 비율 범위별 성과")
        bins = [0, 5, 10, 15, 100]
        labels = ["0-5%", "5-10%", "10-15%", "15%+"]
        trades_binned = completed.copy()
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
                name="승률 (%)", marker_color="rgba(20,120,100,0.60)",
                text=[f"{v:.0f}%" for v in gs["win_rate"]],
                textposition="outside", textfont=dict(color="#e2e8f0", size=11),
            ))
            fig.add_trace(go.Scatter(
                x=gs["range"], y=gs["avg_peak"],
                name="평균 최고수익 (%)", mode="lines+markers",
                yaxis="y2", line=dict(color="#eab308", width=2), marker=dict(size=7),
            ))
            fig.update_layout(
                plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
                height=300, margin=dict(l=0, r=40, t=10, b=0),
                legend=dict(font=dict(color="#7a8599", size=10), orientation="h", y=-0.15),
                xaxis=dict(color="#7a8599"),
                yaxis=dict(showgrid=True, gridcolor="#1e2530", color="#7a8599"),
                yaxis2=dict(overlaying="y", side="right", showgrid=False, color="#eab308"),
                font=dict(color="#e2e8f0"), bargap=0.3,
            )
            st.plotly_chart(fig, use_container_width=True)

    # 결과 분포
    with col2:
        st.markdown("#### 결과 분포")
        result_counts = completed["result_detail"].value_counts()
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
            height=300, margin=dict(l=0, r=0, t=10, b=0),
            showlegend=False, font=dict(color="#e2e8f0"),
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── RR 구간별 / 기대값 구간별 성과 — 진한 색 + 투명도 60% ──
    col3, col4 = st.columns(2)

    with col3:
        st.markdown("#### 손익비(RR) 구간별 성과")
        if "rr_ratio" in completed.columns and completed["rr_ratio"].notna().any():
            rr_bins = [0, 1.5, 2.5, 3.5, 100]
            rr_labels = ["~1.5", "1.5~2.5", "2.5~3.5", "3.5+"]
            rr_df = completed.copy()
            rr_df["rr_bin"] = pd.cut(rr_df["rr_ratio"], bins=rr_bins, labels=rr_labels, right=False)

            rr_stats = []
            for lbl in rr_labels:
                subset = rr_df[rr_df["rr_bin"] == lbl]
                if len(subset):
                    rr_stats.append({
                        "range": lbl,
                        "count": len(subset),
                        "win_rate": len(subset[subset["result"] == "승"]) / len(subset) * 100,
                    })

            if rr_stats:
                rrs = pd.DataFrame(rr_stats)
                fig3 = go.Figure(go.Bar(
                    x=rrs["range"], y=rrs["win_rate"],
                    marker_color=["rgba(20,120,100,0.60)" if wr >= 70 else "rgba(26,107,99,0.60)" for wr in rrs["win_rate"]],
                    text=[f"{v:.0f}% ({c}건)" for v, c in zip(rrs["win_rate"], rrs["count"])],
                    textposition="outside", textfont=dict(color="#e2e8f0", size=11),
                ))
                fig3.update_layout(
                    plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
                    height=280, margin=dict(l=0, r=0, t=10, b=0),
                    xaxis=dict(color="#7a8599", title="RR 구간"),
                    yaxis=dict(showgrid=True, gridcolor="#1e2530", color="#7a8599", title="승률 (%)"),
                    font=dict(color="#e2e8f0"), bargap=0.3,
                )
                st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("RR 데이터가 없습니다.")

    with col4:
        st.markdown("#### 기대값 구간별 성과")
        if "expected_value" in completed.columns and completed["expected_value"].notna().any():
            ev_bins = [0, 5, 15, 30, 1000]
            ev_labels = ["~5", "5~15", "15~30", "30+"]
            ev_df = completed.copy()
            ev_df["ev_bin"] = pd.cut(ev_df["expected_value"], bins=ev_bins, labels=ev_labels, right=False)

            ev_stats = []
            for lbl in ev_labels:
                subset = ev_df[ev_df["ev_bin"] == lbl]
                if len(subset):
                    ev_stats.append({
                        "range": lbl,
                        "count": len(subset),
                        "win_rate": len(subset[subset["result"] == "승"]) / len(subset) * 100,
                    })

            if ev_stats:
                evs = pd.DataFrame(ev_stats)
                fig4 = go.Figure(go.Bar(
                    x=evs["range"], y=evs["win_rate"],
                    marker_color=["rgba(20,120,100,0.60)" if wr >= 70 else "rgba(26,107,99,0.60)" for wr in evs["win_rate"]],
                    text=[f"{v:.0f}% ({c}건)" for v, c in zip(evs["win_rate"], evs["count"])],
                    textposition="outside", textfont=dict(color="#e2e8f0", size=11),
                ))
                fig4.update_layout(
                    plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
                    height=280, margin=dict(l=0, r=0, t=10, b=0),
                    xaxis=dict(color="#7a8599", title="기대값 구간"),
                    yaxis=dict(showgrid=True, gridcolor="#1e2530", color="#7a8599", title="승률 (%)"),
                    font=dict(color="#e2e8f0"), bargap=0.3,
                )
                st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("기대값 데이터가 없습니다.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── MA 패턴별 성과 ────────────────────────────────────
    st.markdown("#### MA 패턴별 성과")
    ma_groups = completed.groupby("ma_pattern").agg(
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
        use_container_width=True, hide_index=True,
    )

    # ── 섹터별 성과 — 꺾은선 그래프 밝은 민트 (#5EEAD4) ───
    st.markdown("#### 섹터별 성과")
    sector_groups = completed.groupby("sector").agg(
        거래수=("result", "count"),
        승리=("result", lambda x: (x == "승").sum()),
        평균수익=("peak_pct", "mean"),
    ).reset_index()
    sector_groups["승률"] = (sector_groups["승리"] / sector_groups["거래수"] * 100).round(1)
    sector_groups["평균수익"] = sector_groups["평균수익"].round(1)
    sector_groups = sector_groups.rename(columns={"sector": "섹터"})
    sector_groups = sector_groups.sort_values("거래수", ascending=False)

    fig5 = go.Figure()
    fig5.add_trace(go.Bar(
        x=sector_groups["섹터"], y=sector_groups["거래수"],
        name="거래수", marker_color="rgba(20,120,100,0.60)",
        text=sector_groups["거래수"], textposition="outside",
        textfont=dict(color="#e2e8f0", size=11),
    ))
    fig5.add_trace(go.Scatter(
        x=sector_groups["섹터"], y=sector_groups["승률"],
        name="승률 (%)", mode="lines+markers",
        yaxis="y2", line=dict(color="#5eead4", width=2), marker=dict(size=7, color="#5eead4"),
    ))
    fig5.update_layout(
        plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
        height=300, margin=dict(l=0, r=40, t=10, b=0),
        legend=dict(font=dict(color="#7a8599", size=10), orientation="h", y=-0.2),
        xaxis=dict(color="#7a8599"),
        yaxis=dict(showgrid=True, gridcolor="#1e2530", color="#7a8599"),
        yaxis2=dict(overlaying="y", side="right", showgrid=False, color="#5eead4", range=[0, 110]),
        font=dict(color="#e2e8f0"), bargap=0.3,
    )
    st.plotly_chart(fig5, use_container_width=True)
