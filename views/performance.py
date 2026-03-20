"""📊 매매 성과 분석 — 12 KPI + RR/기대값 구간 차트 + 마우스오버 프리뷰"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils import fmt_date_short, init_state, df_state, result_badge, market_badge


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


def _mini_badge(text, bg, fg):
    return f'<span style="display:inline-block;padding:1px 6px;border-radius:999px;background:{bg};color:{fg};font-size:10px;font-weight:700;">{text}</span>'


def _html_table(df):
    if df.empty:
        return "<div style='color:#7a8599;padding:10px 0;'>데이터가 없습니다.</div>"

    rows = []
    for _, r in df.iterrows():
        grade = str(r.get("grade", "-") or "-")
        grade_bg = {"A": "rgba(34,197,94,0.14)", "B": "rgba(234,179,8,0.14)", "C": "rgba(239,68,68,0.14)"}.get(grade, "rgba(122,133,153,0.14)")
        grade_fg = {"A": "#22c55e", "B": "#eab308", "C": "#ef4444"}.get(grade, "#7a8599")
        result = str(r.get("result", "-") or "-")
        result_bg = {"승": "rgba(34,197,94,0.14)", "패": "rgba(239,68,68,0.14)", "잉": "rgba(59,130,246,0.14)"}.get(result, "rgba(122,133,153,0.14)")
        result_fg = {"승": "#22c55e", "패": "#ef4444", "잉": "#3b82f6"}.get(result, "#7a8599")

        rows.append(
            "<tr style='border-bottom:1px solid #1e2530;'>"
            f"<td style='padding:6px 4px;text-align:center;'>{market_badge(str(r.get('market','')))}</td>"
            f"<td style='padding:6px 4px;color:#7a8599;text-align:center;font-size:10px;'>{fmt_date_short(r.get('date'))}</td>"
            f"<td style='padding:6px 4px;color:#e2e8f0;text-align:left;font-size:11px;font-weight:500;'>{r.get('name','-')}</td>"
            f"<td style='padding:6px 4px;color:#7a8599;text-align:left;font-size:10px;'>{r.get('code','-')}</td>"
            f"<td style='padding:6px 4px;text-align:center;'><span style='padding:1px 6px;border-radius:999px;background:{grade_bg};color:{grade_fg};font-size:10px;font-weight:700;'>{grade}</span></td>"
            f"<td style='padding:6px 4px;color:#e2e8f0;text-align:right;font-size:10px;'>{_safe_num(r.get('gap_rate')):.1f}%</td>"
            f"<td style='padding:6px 4px;color:#e2e8f0;text-align:right;font-size:10px;'>₩{_safe_int(r.get('entry_price')):,}</td>"
            f"<td style='padding:6px 4px;color:#14b8a6;text-align:right;font-size:10px;font-weight:600;'>{_safe_num(r.get('target_rate')):.1f}%</td>"
            f"<td style='padding:6px 4px;color:#14b8a6;text-align:right;font-size:10px;'>₩{_safe_int(r.get('target_price')):,}</td>"
            f"<td style='padding:6px 4px;color:#ef4444;text-align:right;font-size:10px;'>₩{_safe_int(r.get('stop_price')):,}</td>"
            f"<td style='padding:6px 4px;color:#ef4444;text-align:right;font-size:10px;'>{_safe_num(r.get('stop_rate')):.1f}%</td>"
            f"<td style='padding:6px 4px;color:#22c55e;text-align:center;font-size:10px;font-weight:700;'>{_safe_num(r.get('rr_ratio')):.2f}</td>"
            f"<td style='padding:6px 4px;color:#38bdf8;text-align:right;font-size:10px;font-weight:700;'>{_safe_num(r.get('expected_value')):.1f}</td>"
            f"<td style='padding:6px 4px;color:#22c55e;text-align:right;font-size:10px;font-weight:700;'>{_safe_num(r.get('peak_pct')):+.1f}%</td>"
            f"<td style='padding:6px 4px;color:#ef4444;text-align:right;font-size:10px;'>{_safe_num(r.get('min_low_pct')):+.1f}%</td>"
            f"<td style='padding:6px 4px;text-align:center;'>{_mini_badge(result, result_bg, result_fg)}</td>"
            f"<td style='padding:6px 4px;color:#7a8599;text-align:center;font-size:10px;'>{_safe_int(r.get('days_to_target'))}일</td>"
            f"<td style='padding:6px 4px;color:#7a8599;text-align:left;font-size:9px;'>{r.get('ma_pattern','-')}</td>"
            f"<td style='padding:6px 4px;color:#7a8599;text-align:left;font-size:10px;'>{r.get('sector','-')}</td>"
            "</tr>"
        )

    show_sell_ma = "sell_ma" in df.columns
    sell_ma_header = "<th style='padding:6px 4px;color:#a78bfa;text-align:left;font-size:10px;'>MA(매도)</th>" if show_sell_ma else ""

    html = f"""
    <style>
    .perf-wrap{{background:#0a0e14;border:1px solid #1e2530;border-radius:12px;overflow-x:auto;}}
    .perf-table{{width:100%;border-collapse:collapse;white-space:nowrap;font-variant-numeric:tabular-nums;font-size:11px;}}
    .perf-table thead tr{{border-bottom:2px solid #1e2530;background:#111820;}}
    .perf-table th{{padding:6px 4px;color:#7a8599;font-size:10px;}}
    .hl{{background:rgba(20,184,166,0.06);}}
    </style>
    <div class="perf-wrap">
      <table class="perf-table">
        <thead>
          <tr>
            <th style="text-align:center;">시장</th>
            <th style="text-align:center;">날짜</th>
            <th style="text-align:left;">종목</th>
            <th style="text-align:left;">코드</th>
            <th style="text-align:center;">등급</th>
            <th style="text-align:right;">갭</th>
            <th style="text-align:right;">진입가</th>
            <th class="hl" style="color:#14b8a6;text-align:right;font-weight:600;">목표율</th>
            <th style="text-align:right;">목표가</th>
            <th style="text-align:right;">손절가</th>
            <th style="text-align:right;">손절율</th>
            <th class="hl" style="color:#14b8a6;text-align:center;font-weight:600;">손익비</th>
            <th class="hl" style="color:#14b8a6;text-align:right;font-weight:600;">기대값</th>
            <th style="text-align:right;">최고</th>
            <th style="text-align:right;">최저</th>
            <th style="text-align:center;">결과</th>
            <th style="text-align:center;">소요일</th>
            <th style="text-align:left;">MA</th>
            {sell_ma_header}
            <th style="text-align:left;">섹터</th>
          </tr>
        </thead>
        <tbody>
          {''.join(rows)}
        </tbody>
      </table>
    </div>
    """
    return html


def render():
    init_state()
    st.markdown("### ▸ 매매 성과 분석")

    trades = df_state("trades")
    if trades.empty:
        st.info("데이터가 없습니다.")
        return

    if "date" in trades.columns:
        trades["date"] = pd.to_datetime(trades["date"], errors="coerce")

    c1, c2, c3, c4 = st.columns(4)
    win_cnt = int((trades["result"] == "승").sum()) if "result" in trades.columns else 0
    lose_cnt = int((trades["result"] == "패").sum()) if "result" in trades.columns else 0
    ing_cnt = int((trades["result"] == "잉").sum()) if "result" in trades.columns else 0
    total_cnt = len(trades)
    win_rate = (win_cnt / max(win_cnt + lose_cnt, 1)) * 100 if (win_cnt + lose_cnt) else 0

    c1.metric("총 매매", f"{total_cnt}건")
    c2.metric("승/패", f"{win_cnt}/{lose_cnt}")
    c3.metric("진행중", f"{ing_cnt}건")
    c4.metric("승률", f"{win_rate:.1f}%")

    st.markdown(
        """
        <div style="margin:8px 0 10px 0;color:#7a8599;font-size:12px;">
        수익 인자: RR, 기대값, MA 패턴, 섹터, 보유기간 기준으로 성과를 해석합니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

    fig = go.Figure()

    has_result = "result" in trades.columns
    has_profit = "profit_pct" in trades.columns
    has_equity = "equity" in trades.columns

    if has_profit and has_result:
        win = trades[trades["result"] == "승"]
        lose = trades[trades["result"] == "패"]

        if not win.empty:
            fig.add_trace(go.Bar(
                x=win["date"],
                y=win["profit_pct"],
                name="승리",
                marker_color="#22c55e",
                hovertemplate="날짜: %{x|%m/%d}<br>수익: %{y:.2f}%<extra></extra>",
            ))
        if not lose.empty:
            fig.add_trace(go.Bar(
                x=lose["date"],
                y=lose["profit_pct"],
                name="패배",
                marker_color="#7f1d1d",
                hovertemplate="날짜: %{x|%m/%d}<br>수익: %{y:.2f}%<extra></extra>",
            ))

    if has_equity:
        fig.add_trace(go.Scatter(
            x=trades["date"],
            y=trades["equity"],
            name="누적",
            mode="lines+markers",
            line=dict(color="#38bdf8", width=2),
            hovertemplate="날짜: %{x|%m/%d}<br>누적: %{y:.2f}<extra></extra>",
        ))

    fig.update_layout(
        template="plotly_dark",
        barmode="group",
        hovermode="x unified",
        height=420,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="#0a0e14",
        plot_bgcolor="#0a0e14",
        legend=dict(orientation="h", y=1.05),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### ▸ 거래 상세")
    st.components.v1.html(_html_table(trades), height=min(800, 44 + len(trades) * 34), scrolling=True)
