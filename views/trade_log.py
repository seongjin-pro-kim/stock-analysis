"""매매 기록 — views/trade_log.py"""

import calendar
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import result_badge, market_badge, fmt_date_short


def _safe_num(x, default=0.0):
    try:
        return default if pd.isna(x) else float(x)
    except Exception:
        return default


def _safe_int(x, default=0):
    try:
        return default if pd.isna(x) else int(x)
    except Exception:
        return default


def _shade_style(field, text_color="#d6dde8"):
    if field == "target_rate":
        return f"color:{text_color};background:rgba(16,185,129,0.06);"
    if field == "rr_ratio":
        return f"color:{text_color};background:rgba(59,130,246,0.06);"
    if field == "expected_value":
        return f"color:{text_color};background:rgba(168,85,247,0.06);"
    return f"color:{text_color};"


def _ma_color(ma):
    mapping = {
        "5": "#ef4444",
        "20": "#f59e0b",
        "40": "#22c55e",
        "60": "#3b82f6",
        "120": "#a855f7",
    }
    if ma is None:
        return "#7a8599"
    txt = str(ma)
    for k, v in mapping.items():
        if k in txt:
            return v
    return "#7a8599"


def _ma_tokens(ma_text):
    if not ma_text or pd.isna(ma_text):
        return "-"
    parts = [p.strip() for p in str(ma_text).replace(">", " ").replace(",", " ").split() if p.strip()]
    tokens = []
    for p in parts:
        c = _ma_color(p)
        tokens.append(f"<span style='color:{c};font-weight:700;'>{p}</span>")
    return "<span style='font-size:10px;'>" + "&nbsp;&nbsp;".join(tokens) + "</span>"


def render():
    trades = st.session_state.trades.copy()
    st.markdown("### ▸ 매매 기록")

    if trades.empty:
        st.info("데이터가 없습니다.")
        return

    for col in ["date", "sell_date", "expiry_date"]:
        if col in trades.columns:
            trades[col] = pd.to_datetime(trades[col], errors="coerce")

    st.markdown(
        """
        <style>
        .table-wrap{background:#0a0e14;border:1px solid #1e2530;border-radius:12px;overflow-x:auto;}
        .table-dark{width:100%;border-collapse:collapse;white-space:nowrap;font-variant-numeric:tabular-nums;font-size:11px;}
        .table-dark thead tr{border-bottom:2px solid #1e2530;background:#111820;}
        .table-dark th{padding:7px 6px;color:#7a8599;font-size:10px;font-weight:600;}
        .table-dark td{padding:7px 6px;border-bottom:1px solid #1e2530;}
        .grade-a-name{background:rgba(239,68,68,0.30);border-radius:6px;padding:2px 4px;display:inline-block;}
        .strong-win{color:#86efac;font-weight:800;}
        .strong-lose{color:#fca5a5;font-weight:800;}
        .strong-ing{color:#93c5fd;font-weight:800;}
        .cal-win{color:#22c55e;font-weight:800;}
        .cal-lose{color:#ef4444;font-weight:800;}
        .cal-ing{color:#3b82f6;font-weight:800;}
        .badge-tight span{transform:scale(1.00);display:inline-block;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    fc1, fc2, fc3, fc4, fc5, fc6, fc7 = st.columns(7)
    with fc1:
        market_filter = st.selectbox("시장", ["전체", "KOSPI", "KOSDAQ"])
    with fc2:
        result_filter = st.selectbox("결과", ["전체", "승", "패", "잉"])
    with fc3:
        sectors = ["전체"] + sorted(trades["sector"].dropna().unique().tolist()) if "sector" in trades.columns else ["전체"]
        sector_filter = st.selectbox("섹터", sectors)
    with fc4:
        grade_opts = ["전체"] + sorted(trades["grade"].dropna().unique().tolist()) if "grade" in trades.columns else ["전체"]
        grade_filter = st.selectbox("등급", grade_opts)
    with fc5:
        core_filter = st.selectbox("코어 여부", ["전체", "코어만", "코어 제외"])
    with fc6:
        if "rr_ratio" in trades.columns and trades["rr_ratio"].notna().any():
            rr_max = float(trades["rr_ratio"].max())
            rr_threshold = st.slider("최소 RR", 0.0, round(rr_max, 1), 0.0, 0.1)
        else:
            rr_threshold = 0.0
            st.caption("RR 데이터 없음")
    with fc7:
        sort_by = st.selectbox("정렬", ["날짜 (최신)", "날짜 (오래된)", "갭비율 ↓", "최고수익 ↓", "손익비 ↓", "기대값 ↓", "소요일 ↑"])

    filtered = trades.copy()
    if market_filter != "전체" and "market" in filtered.columns:
        filtered = filtered[filtered["market"] == market_filter]
    if result_filter != "전체" and "result" in filtered.columns:
        filtered = filtered[filtered["result"] == result_filter]
    if sector_filter != "전체" and "sector" in filtered.columns:
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

    sort_map = {
        "날짜 (최신)": ("date", False),
        "날짜 (오래된)": ("date", True),
        "갭비율 ↓": ("gap_rate", False),
        "최고수익 ↓": ("peak_pct", False),
        "손익비 ↓": ("rr_ratio", False),
        "기대값 ↓": ("expected_value", False),
        "소요일 ↑": ("days_to_target", True),
    }
    sort_col, sort_asc = sort_map.get(sort_by, ("date", False))
    if sort_col in filtered.columns:
        filtered = filtered.sort_values(sort_col, ascending=sort_asc)
    elif "date" in filtered.columns:
        filtered = filtered.sort_values("date", ascending=False)

    in_progress = len(trades[trades["result"] == "잉"]) if "result" in trades.columns else 0
    st.markdown(f"총 {len(filtered)}건 / {len(trades)}건 (진행중: :blue[{in_progress}건])")

    show_sell_ma = result_filter in ["승", "패"]
    rows = []
    for _, r in filtered.iterrows():
        grade = r.get("grade", "-") or "-"
        grade_colors = {"A": "#22c55e", "B": "#eab308", "C": "#ef4444"}
        g_color = grade_colors.get(grade, "#7a8599")
        rr_val = _safe_num(r.get("rr_ratio"))
        rr_color = "#22c55e" if rr_val >= 2.0 else ("#eab308" if rr_val >= 1.5 else "#ef4444")
        ev_val = _safe_num(r.get("expected_value"))
        ev_color = "#22c55e" if ev_val >= 15 else ("#eab308" if ev_val >= 5 else "#7a8599")
        sell_ma_td = f"<td style='padding:5px 4px;font-size:10px;text-align:left;'>{_ma_tokens(r.get('sell_ma',''))}</td>" if show_sell_ma else ""
        name = r.get("name", "-")
        if grade == "A":
            name_html = f"<span class='grade-a-name'>{name}</span>"
        else:
            name_html = name

        rows.append(
            "<tr style='border-bottom:1px solid #1e2530;'>"
            f"<td style='padding:5px 4px;font-size:10px;text-align:center;'>{market_badge(r.get('market',''))}</td>"
            f"<td style='padding:5px 4px;color:#7a8599;font-size:10px;text-align:center;'>{fmt_date_short(r.get('date'))}</td>"
            f"<td style='padding:5px 4px;color:#e2e8f0;font-size:12px;text-align:left;font-weight:600;'>{name_html}</td>"
            f"<td style='padding:5px 4px;color:#7a8599;font-size:10px;text-align:left;'>{r.get('code','-')}</td>"
            f"<td style='padding:5px 4px;color:{g_color};font-weight:800;font-size:10px;text-align:center;'>{grade}</td>"
            f"<td style='padding:5px 4px;{_shade_style('gap_rate')} text-align:right;font-size:10px;'>{_safe_num(r.get('gap_rate')):.1f}%</td>"
            f"<td style='padding:5px 4px;{_shade_style('entry_price')} text-align:right;font-size:10px;'>₩{_safe_num(r.get('entry_price')):,.0f}</td>"
            f"<td style='padding:5px 4px;{_shade_style('target_rate')} text-align:right;font-size:10px;font-weight:700;'>{_safe_num(r.get('target_rate')):.1f}%</td>"
            f"<td style='padding:5px 4px;{_shade_style('target_price')} text-align:right;font-size:10px;'>₩{_safe_num(r.get('target_price')):,.0f}</td>"
            f"<td style='padding:5px 4px;{_shade_style('stop_price')} text-align:right;font-size:10px;'>₩{_safe_num(r.get('stop_price')):,.0f}</td>"
            f"<td style='padding:5px 4px;{_shade_style('stop_rate')} text-align:right;font-size:10px;'>{_safe_num(r.get('stop_rate')):.1f}%</td>"
            f"<td style='padding:5px 4px;{_shade_style('rr_ratio')} text-align:center;font-size:10px;font-weight:800;'>{rr_val:.2f}</td>"
            f"<td style='padding:5px 4px;{_shade_style('expected_value')} text-align:right;font-size:10px;font-weight:800;'>{ev_val:.1f}</td>"
            f"<td style='padding:5px 4px;color:#22c55e;text-align:right;font-size:10px;font-weight:700;'>{_safe_num(r.get('peak_pct')):+.1f}%</td>"
            f"<td style='padding:5px 4px;color:#ef4444;text-align:right;font-size:10px;'>{_safe_num(r.get('min_low_pct')):+.1f}%</td>"
            f"<td style='padding:5px 4px;text-align:center;font-size:10px;'>{result_badge(r.get('result','-'))}</td>"
            f"<td style='padding:5px 4px;color:#7a8599;text-align:center;font-size:10px;'>{_safe_int(r.get('days_to_target'))}일</td>"
            f"<td style='padding:5px 4px;color:#7a8599;font-size:9px;text-align:left;'>{r.get('ma_pattern','-')}</td>"
            f"{sell_ma_td}"
            f"<td style='padding:5px 4px;color:#7a8599;font-size:10px;text-align:left;'>{r.get('sector','-')}</td>"
            "</tr>"
        )

    sell_ma_header = '<th style="padding:5px 4px;color:#a78bfa;text-align:left;font-size:10px;">MA(매도)</th>' if show_sell_ma else ""
    st.markdown(
        f"""
        <div class="table-wrap">
        <table class="table-dark">
        <thead><tr>
            <th style="text-align:center;">시장</th>
            <th style="text-align:center;">날짜</th>
            <th style="text-align:left;">종목</th>
            <th style="text-align:left;">코드</th>
            <th style="text-align:center;">등급</th>
            <th style="text-align:right;">갭</th>
            <th style="text-align:right;">진입가</th>
            <th style="text-align:right;color:#14b8a6;font-weight:700;">목표율</th>
            <th style="text-align:right;">목표가</th>
            <th style="text-align:right;">손절가</th>
            <th style="text-align:right;">손절율</th>
            <th style="text-align:center;color:#14b8a6;font-weight:700;">손익비</th>
            <th style="text-align:right;color:#14b8a6;font-weight:700;">기대값</th>
            <th style="text-align:right;">최고</th>
            <th style="text-align:right;">최저</th>
            <th style="text-align:center;">결과</th>
            <th style="text-align:center;">소요일</th>
            <th style="text-align:left;">MA</th>
            {sell_ma_header}
            <th style="text-align:left;">섹터</th>
        </tr></thead>
        <tbody>{''.join(rows)}</tbody>
        </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### ▸ 거래 달력")
    if "date" in filtered.columns:
        cal_data = filtered.copy()
        cal_data["month"] = pd.to_datetime(cal_data["date"], errors="coerce").dt.to_period("M")
        months = sorted(cal_data["month"].dropna().unique(), reverse=True)[:3]
        cal_cols = st.columns(len(months)) if months else []
        for i, mp in enumerate(months):
            with cal_cols[i]:
                st.markdown(
                    f"<div style='color:#e2e8f0;font-size:13px;font-weight:600;margin-bottom:8px;text-align:center;'>{str(mp.year)[2:]}년 {mp.month}월</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    "<div style='text-align:center;'>" +
                    "".join(
                        f"<span style='display:inline-block;width:28px;text-align:center;color:#7a8599;font-size:10px;margin:1px;'>{d}</span>"
                        for d in ["월","화","수","목","금","토","일"]
                    ) +
                    "</div>",
                    unsafe_allow_html=True,
                )
                month_trades = cal_data[cal_data["month"] == mp]
                trade_dates = {}
                for _, t in month_trades.iterrows():
                    d = pd.to_datetime(t["date"], errors="coerce")
                    if pd.notna(d):
                        trade_dates.setdefault(d.day, []).append(t.get("result", "-"))
                cal_html = ""
                for week in calendar.monthcalendar(mp.year, mp.month):
                    for day in week:
                        if day == 0:
                            cal_html += '<span style="display:inline-block;width:28px;color:#1e2530;">·</span>'
                        else:
                            rs = trade_dates.get(day, [])
                            cls = "#7a8599"
                            if "잉" in rs:
                                cls = "#3b82f6"
                            elif "승" in rs:
                                cls = "#22c55e"
                            elif "패" in rs:
                                cls = "#ef4444"
                            cal_html += f'<span style="display:inline-block;width:28px;text-align:center;color:{cls};font-weight:700;">{day}</span>'
                    cal_html += "<br>"
                st.markdown(f"<div style='text-align:center;line-height:1.8;'>{cal_html}</div>", unsafe_allow_html=True)
