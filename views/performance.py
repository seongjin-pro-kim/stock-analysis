"""📊 매매 성과 분석 — 12 KPI + RR/기대값 구간 차트 + 마우스오버 프리뷰"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils import fmt_date_short


def _safe_num(x, default=0.0):
    try:
        if pd.isna(x):
            return default
        return float(x)
    except Exception:
        return default


def _safe_int(x, default=0):
    try:
        if pd.isna(x):
            return default
        return int(x)
    except Exception:
        return default


def _fmt_pct(x):
    return f"{_safe_num(x):.1f}%"


def _fmt_num(x):
    return f"{_safe_num(x):,.0f}"


def _fmt_rr(x):
    return f"{_safe_num(x):.2f}"


def _preview_table(items, cols, title=""):
    if len(items) == 0:
        return "<div style='color:#7a8599;font-size:10px;'>데이터 없음</div>"

    header = "".join(
        f"<th style='padding:3px 6px;color:#7a8599;font-size:10px;text-align:left;'>{c}</th>"
        for c in cols
    )
    rows = []
    for item in items:
        cells = "".join(
            f"<td style='padding:3px 6px;color:#e2e8f0;font-size:10px;'>{v}</td>"
            for v in item
        )
        rows.append(f"<tr style='border-bottom:1px solid #1e2530;'>{cells}</tr>")
    title_html = f"<div style='color:#14b8a6;font-size:10px;font-weight:700;margin-bottom:4px;'>{title}</div>" if title else ""
    return f"""
    <div>
      {title_html}
      <table style="width:100%;border-collapse:collapse;">
        <thead><tr style="border-bottom:1px solid #2a3545;">{header}</tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </div>
    """


def _tooltip_wrap(value_html, preview_html):
    return f"""
    <div class="tooltip-wrap">
      <div class="kpi-card">{value_html}</div>
      <div class="tooltip-box">{preview_html}</div>
    </div>
    """


def _kpi_card(label, value, value_class="neutral", preview_html=None):
    body = f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value {value_class}">{value}</div>
    </div>
    """
    if preview_html:
        return f"""
        <div class="tooltip-wrap">
          {body}
          <div class="tooltip-box">{preview_html}</div>
        </div>
        """
    return body


def render():
    trades = st.session_state.trades.copy()
    equity = st.session_state.equitycurve.copy() if "equitycurve" in st.session_state else pd.DataFrame()

    st.markdown(
        """
        <style>
        .kpi-card{
            background:#111820;border:1px solid #1e2530;border-radius:12px;
            padding:14px 14px 12px 14px;min-height:72px;
        }
        .kpi-label{color:#7a8599;font-size:11px;margin-bottom:6px;}
        .kpi-value{font-size:22px;font-weight:800;line-height:1.1;color:#e2e8f0;}
        .kpi-value.positive{color:#22c55e;}
        .kpi-value.negative{color:#ef4444;}
        .kpi-value.neutral{color:#e2e8f0;}
        .tooltip-wrap{position:relative;}
        .tooltip-box{
            display:none;position:absolute;z-index:20;left:0;top:110%;
            width:340px;max-width:340px;background:#0a0e14;border:1px solid #1e2530;
            border-radius:10px;padding:10px;box-shadow:0 16px 40px rgba(0,0,0,.35);
        }
        .tooltip-wrap:hover .tooltip-box{display:block;}
        .tooltip-box table{font-size:10px;}
        .tooltip-box th,.tooltip-box td{padding:3px 4px;white-space:nowrap;}
        .section-title{font-size:16px;font-weight:800;color:#e2e8f0;margin:4px 0 10px 0;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### ▸ 매매성과")

    if trades.empty:
        st.info("데이터가 없습니다.")
        return

    completed = trades[trades["result"].isin(["승", "패"])].copy()
    wins = completed[completed["result"] == "승"].copy()
    losses = completed[completed["result"] == "패"].copy()

    total = len(completed)
    wincount = len(wins)
    losscount = len(losses)
    winrate = (wincount / total * 100) if total else 0.0

    avg_peak = completed["peakpct"].mean() if "peakpct" in completed.columns and total else 0.0
    avg_low = completed["minlowpct"].mean() if "minlowpct" in completed.columns and total else 0.0
    avg_win_peak = wins["peakpct"].mean() if "peakpct" in wins.columns and wincount else 0.0
    avg_loss_low = losses["minlowpct"].mean() if "minlowpct" in losses.columns and losscount else 0.0
    avg_days_win = wins["daystotarget"].mean() if "daystotarget" in wins.columns and wincount else 0.0
    avg_days_loss = losses["daystotarget"].mean() if "daystotarget" in losses.columns and losscount else 0.0

    total_eq = equity.copy()
    max_dd_pct = 0.0
    if not total_eq.empty and "date" in total_eq.columns and "value" in total_eq.columns:
        total_eq = total_eq.groupby("date")["value"].sum().reset_index()
        max_val = total_eq["value"].max()
        if max_val != 0:
            max_dd_pct = ((max_val - total_eq["value"].min()) / max_val) * 100

    profit_factor = 0.0
    if wincount and losscount and avg_win_peak != 0 and avg_loss_low != 0:
        profit_factor = abs(avg_win_peak / avg_loss_low)

    recent_wins = wins.sort_values("date", ascending=False).head(7) if not wins.empty else pd.DataFrame()
    recent_losses = losses.sort_values("date", ascending=False).head(7) if not losses.empty else pd.DataFrame()
    top_peak = completed.sort_values("peakpct", ascending=False).head(7) if "peakpct" in completed.columns else pd.DataFrame()
    worst_low = completed.sort_values("minlowpct", ascending=True).head(7) if "minlowpct" in completed.columns else pd.DataFrame()
    top_days_win = wins.sort_values("daystotarget", ascending=True).head(7) if "daystotarget" in wins.columns else pd.DataFrame()
    worst_dd = completed.sort_values("minlowpct", ascending=True).head(7) if "minlowpct" in completed.columns else pd.DataFrame()

    avg_rr_wins = wins["rr_ratio"].mean() if "rr_ratio" in wins.columns and wincount else 0.0
    avg_ev_wins = wins["expected_value"].mean() if "expected_value" in wins.columns and wincount else 0.0
    avg_rr_losses = losses["rr_ratio"].mean() if "rr_ratio" in losses.columns and losscount else 0.0
    avg_ev_losses = losses["expected_value"].mean() if "expected_value" in losses.columns and losscount else 0.0

    def _trade_preview(df, mode="winrate"):
        if df.empty:
            return "<div style='color:#7a8599;font-size:10px;'>데이터 없음</div>"
        cols = ["매도일", "종목", "손익율"]
        if "rr_ratio" in df.columns:
            cols += ["RR"]
        if "expected_value" in df.columns:
            cols += ["EV"]
        rows = []
        for _, r in df.iterrows():
            row = [
                fmt_date_short(r.get("date")),
                str(r.get("name", "-")),
                _fmt_pct(r.get("peakpct", r.get("minlowpct", 0))),
            ]
            if "rr_ratio" in df.columns:
                row.append(_fmt_rr(r.get("rr_ratio")))
            if "expected_value" in df.columns:
                row.append(f"{_safe_num(r.get('expected_value')):.1f}")
            rows.append(row)
        return _preview_table(rows, cols)

    def _peak_preview(df):
        if df.empty:
            return "<div style='color:#7a8599;font-size:10px;'>데이터 없음</div>"
        rows = [[fmt_date_short(r.get("date")), r.get("name", "-"), _fmt_pct(r.get("peakpct", 0))] for _, r in df.iterrows()]
        return _preview_table(rows, ["매도일", "종목", "최고수익"], "최고수익 상위 7")

    def _low_preview(df):
        if df.empty:
            return "<div style='color:#7a8599;font-size:10px;'>데이터 없음</div>"
        rows = [[fmt_date_short(r.get("date")), r.get("name", "-"), _fmt_pct(r.get("minlowpct", 0))] for _, r in df.iterrows()]
        return _preview_table(rows, ["매도일", "종목", "최저수익"], "최저수익 하위 7")

    def _days_preview(df, by="ev"):
        if df.empty:
            return "<div style='color:#7a8599;font-size:10px;'>데이터 없음</div>"
        rows = []
        for _, r in df.iterrows():
            rows.append([
                fmt_date_short(r.get("date")),
                r.get("name", "-"),
                f"{_safe_int(r.get('daystotarget'))}일",
                f"{_safe_num(r.get('expected_value')):.1f}",
                _fmt_rr(r.get("rr_ratio")),
            ])
        return _preview_table(rows, ["매도일", "종목", "소요일", "EV", "RR"], "오름차순 7")

    cols1 = st.columns(4)
    with cols1[0]:
        st.markdown(_kpi_card("총거래건수", f"{total}건", "neutral", _trade_preview(completed)), unsafe_allow_html=True)
    with cols1[1]:
        st.markdown(_kpi_card("승리", f"{wincount}건", "positive", _trade_preview(wins)), unsafe_allow_html=True)
    with cols1[2]:
        st.markdown(_kpi_card("패배", f"{losscount}건", "negative", _trade_preview(losses)), unsafe_allow_html=True)
    with cols1[3]:
        st.markdown(_kpi_card("승률", f"{winrate:.1f}%", "neutral"), unsafe_allow_html=True)

    cols2 = st.columns(4)
    with cols2[0]:
        st.markdown(_kpi_card("평균 최고 수익", f"{avg_peak:.1f}%", "positive", _peak_preview(top_peak)), unsafe_allow_html=True)
    with cols2[1]:
        st.markdown(_kpi_card("평균 최저 수익", f"{avg_low:.1f}%", "negative", _low_preview(worst_low)), unsafe_allow_html=True)
    with cols2[2]:
        st.markdown(_kpi_card("승리 평균 소요일", f"{avg_days_win:.1f}일", "neutral", _days_preview(top_days_win)), unsafe_allow_html=True)
    with cols2[3]:
        st.markdown(_kpi_card("패배 평균 소요일", f"{avg_days_loss:.1f}일", "neutral", _days_preview(top_days_win)), unsafe_allow_html=True)

    cols3 = st.columns(4)
    with cols3[0]:
        st.markdown(_kpi_card("승리 평균 최고수익", f"{avg_win_peak:.1f}%", "positive"), unsafe_allow_html=True)
    with cols3[1]:
        st.markdown(_kpi_card("패배 평균 최저수익", f"{avg_loss_low:.1f}%", "negative"), unsafe_allow_html=True)
    with cols3[2]:
        st.markdown(_kpi_card("최대 낙폭", f"{max_dd_pct:.1f}%", "negative", _preview_table(
            [[r.get("name", "-"), _fmt_rr(r.get("rr_ratio")), f"{_safe_int(r.get('daystotarget'))}일"] for _, r in worst_dd.iterrows()],
            ["종목", "RR", "소요일"],
            "최대낙폭 오름차순 7"
        )), unsafe_allow_html=True)
    with cols3[3]:
        st.markdown(_kpi_card("손익비", f"{profit_factor:.2f}", "positive"), unsafe_allow_html=True)

    st.markdown("#### ▸ RR / 기대값 구간별 성과")

    col1, col2 = st.columns(2)

    with col1:
        if "rr_ratio" in completed.columns and completed["rr_ratio"].notna().any():
            bins = [0, 1.5, 2.5, 3.5, 100]
            labels = ["0-1.5", "1.5-2.5", "2.5-3.5", "3.5+"]
            tmp = completed.copy()
            tmp["rr_bin"] = pd.cut(tmp["rr_ratio"], bins=bins, labels=labels, right=False)
            stats = []
            for lbl in labels:
                s = tmp[tmp["rr_bin"] == lbl]
                if len(s):
                    stats.append([lbl, len(s), s["result"].eq("승").mean() * 100, s["peakpct"].mean()])
            if stats:
                gs = pd.DataFrame(stats, columns=["구간", "건수", "승률", "평균최고수익"])
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=gs["구간"],
                    y=gs["승률"],
                    marker_color="rgba(20,184,166,0.60)",
                    text=[f"{v:.0f}" for v in gs["승률"]],
                    textposition="outside",
                ))
                fig.add_trace(go.Scatter(
                    x=gs["구간"],
                    y=gs["평균최고수익"],
                    mode="lines+markers",
                    line=dict(color="#34d399", width=2),
                    marker=dict(size=7),
                    yaxis="y2",
                ))
                fig.update_layout(
                    height=300,
                    plot_bgcolor="#0a0e14",
                    paper_bgcolor="#0a0e14",
                    margin=dict(l=0, r=40, t=10, b=0),
                    bargap=0.3,
                    xaxis=dict(color="#7a8599"),
                    yaxis=dict(color="#7a8599", showgrid=True, gridcolor="#1e2530"),
                    yaxis2=dict(overlaying="y", side="right", showgrid=False, color="#34d399"),
                    font=dict(color="#e2e8f0"),
                )
                st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("RR 데이터 없음")

    with col2:
        if "expected_value" in completed.columns and completed["expected_value"].notna().any():
            bins = [0, 5, 15, 30, 1000]
            labels = ["0-5", "5-15", "15-30", "30+"]
            tmp = completed.copy()
            tmp["ev_bin"] = pd.cut(tmp["expected_value"], bins=bins, labels=labels, right=False)
            stats = []
            for lbl in labels:
                s = tmp[tmp["ev_bin"] == lbl]
                if len(s):
                    stats.append([lbl, len(s), s["result"].eq("승").mean() * 100, s["peakpct"].mean()])
            if stats:
                es = pd.DataFrame(stats, columns=["구간", "건수", "승률", "평균최고수익"])
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=es["구간"],
                    y=es["승률"],
                    marker_color="rgba(20,184,166,0.60)",
                    text=[f"{v:.0f}" for v in es["승률"]],
                    textposition="outside",
                ))
                fig.add_trace(go.Scatter(
                    x=es["구간"],
                    y=es["평균최고수익"],
                    mode="lines+markers",
                    line=dict(color="#34d399", width=2),
                    marker=dict(size=7),
                    yaxis="y2",
                ))
                fig.update_layout(
                    height=300,
                    plot_bgcolor="#0a0e14",
                    paper_bgcolor="#0a0e14",
                    margin=dict(l=0, r=40, t=10, b=0),
                    bargap=0.3,
                    xaxis=dict(color="#7a8599"),
                    yaxis=dict(color="#7a8599", showgrid=True, gridcolor="#1e2530"),
                    yaxis2=dict(overlaying="y", side="right", showgrid=False, color="#34d399"),
                    font=dict(color="#e2e8f0"),
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("기대값 데이터 없음")

    st.markdown("#### ▸ MA / 섹터 성과")

    col3, col4 = st.columns(2)

    with col3:
        if "mapattern" in completed.columns:
            mg = completed.groupby("mapattern").agg(
                count=("result", "count"),
                winrate=("result", lambda x: (x == "승").mean() * 100),
                avg_peak=("peakpct", "mean"),
                avg_low=("minlowpct", "mean"),
            ).reset_index()
            mg = mg.sort_values("count", ascending=False)
            st.dataframe(mg, use_container_width=True, hide_index=True)
        else:
            st.info("MA 데이터 없음")

    with col4:
        if "sector" in completed.columns:
            sg = completed.groupby("sector").agg(
                count=("result", "count"),
                winrate=("result", lambda x: (x == "승").mean() * 100),
                avg_peak=("peakpct", "mean"),
            ).reset_index()
            sg = sg.sort_values("count", ascending=False)

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=sg["sector"],
                y=sg["count"],
                marker_color="rgba(20,184,166,0.60)",
                text=sg["count"],
                textposition="outside",
            ))
            fig.add_trace(go.Scatter(
                x=sg["sector"],
                y=sg["winrate"],
                mode="lines+markers",
                line=dict(color="#a7f3d0", width=2),
                marker=dict(size=7),
                yaxis="y2",
            ))
            fig.update_layout(
                height=300,
                plot_bgcolor="#0a0e14",
                paper_bgcolor="#0a0e14",
                margin=dict(l=0, r=40, t=10, b=0),
                bargap=0.3,
                xaxis=dict(color="#7a8599"),
                yaxis=dict(color="#7a8599", showgrid=True, gridcolor="#1e2530"),
                yaxis2=dict(overlaying="y", side="right", showgrid=False, color="#a7f3d0"),
                font=dict(color="#e2e8f0"),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("섹터 데이터 없음")
