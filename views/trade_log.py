import streamlit as st
import pandas as pd
import calendar
from utils import init_state, df_state, result_badge, market_badge


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


def render():
    init_state()
    trades = df_state("trades")
    if trades.empty:
        st.info("데이터가 없습니다.")
        return

    if "date" in trades.columns:
        trades["date"] = pd.to_datetime(trades["date"], errors="coerce")

    st.markdown("### ▸ 매매 기록")

    st.markdown("""
    <style>
    .filter-box{
        background:#0f141b;
        border:1px solid #1e2530;
        border-radius:10px;
        padding:12px 12px 6px 12px;
        margin-bottom:10px;
    }
    .badge-win{background:#22c55e22;color:#22c55e;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:600;}
    .badge-lose{background:#ef444422;color:#ef4444;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:600;}
    .badge-ing{background:#3b82f622;color:#3b82f6;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:700;}
    table{width:100%;border-collapse:collapse;font-size:11px;font-variant-numeric:tabular-nums;white-space:nowrap;}
    thead tr{border-bottom:2px solid #1e2530;background:#111820;}
    th{padding:6px 4px;color:#7a8599;font-size:10px;}
    .hl{background:rgba(20,184,166,0.06);}
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="filter-box">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

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

    in_progress = len(trades[trades["result"] == "잉"]) if "result" in trades.columns else 0
    st.markdown(f"총 {len(filtered)}건 / {len(trades)}건 (진행중: :blue[{in_progress}건])")

    show_sell_ma = result_filter in ["승", "패"]
    has_ev = "expected_value" in filtered.columns
    has_target_rate = "target_rate" in filtered.columns
    has_stop_rate = "stop_rate" in filtered.columns

    grade_colors = {"A": "#22c55e", "B": "#eab308", "C": "#ef4444"}
    rows_html = []

    for _, r in filtered.iterrows():
        dt = pd.to_datetime(r.get("date"), errors="coerce")
        date_str = dt.strftime("%m/%d") if pd.notna(dt) else "-"
        grade = r.get("grade", "-") or "-"
        peak_pct = _safe_num(r.get("peak_pct"))
        min_low_pct = _safe_num(r.get("min_low_pct"))
        gap_rate = _safe_num(r.get("gap_rate"))
        rr_val = _safe_num(r.get("rr_ratio"))
        ev_val = _safe_num(r.get("expected_value"))

        name_style = 'padding:5px 4px;color:#e2e8f0;font-weight:500;font-size:12px;text-align:left;'
        if grade == "A":
            name_style += 'background:rgba(239,68,68,0.16);border-radius:4px;'

        target_rate_str = f"{_safe_num(r.get('target_rate')):.1f}%" if has_target_rate and pd.notna(r.get("target_rate")) else "-"
        stop_rate_str = f"{_safe_num(r.get('stop_rate')):.1f}%" if has_stop_rate and pd.notna(r.get("stop_rate")) else "-"

        rows_html.append(
            f'<tr style="border-bottom:1px solid #1e2530;">'
            f'<td style="padding:5px 4px;font-size:10px;text-align:center;">{market_badge(r.get("market", ""))}</td>'
            f'<td style="padding:5px 4px;color:#7a8599;font-size:10px;text-align:center;">{date_str}</td>'
            f'<td style="{name_style}">{r.get("name", "-")}</td>'
            f'<td style="padding:5px 4px;color:#7a8599;font-size:10px;text-align:left;">{r.get("code", "-")}</td>'
            f'<td style="padding:5px 4px;color:{grade_colors.get(grade, "#7a8599")};font-weight:600;font-size:10px;text-align:center;">{grade}</td>'
            f'<td style="padding:5px 4px;color:#e2e8f0;text-align:right;font-size:10px;">{gap_rate:.1f}%</td>'
            f'<td style="padding:5px 4px;color:#e2e8f0;text-align:right;font-size:10px;">₩{_safe_int(r.get("entry_price")):,}</td>'
            f'<td class="hl" style="padding:5px 4px;color:#14b8a6;text-align:right;font-size:10px;font-weight:600;">{target_rate_str}</td>'
            f'<td style="padding:5px 4px;color:#14b8a6;text-align:right;font-size:10px;">₩{_safe_int(r.get("target_price")):,}</td>'
            f'<td style="padding:5px 4px;color:#ef4444;text-align:right;font-size:10px;">₩{_safe_int(r.get("stop_price")):,}</td>'
            f'<td style="padding:5px 4px;color:#ef4444;text-align:right;font-size:10px;">{stop_rate_str}</td>'
            f'<td class="hl" style="padding:5px 4px;color:#22c55e;text-align:center;font-size:10px;font-weight:600;">{rr_val:.2f}</td>'
            f'<td class="hl" style="padding:5px 4px;color:#38bdf8;text-align:right;font-size:10px;font-weight:600;">{ev_val:.1f}</td>'
            f'<td style="padding:5px 4px;color:#22c55e;text-align:right;font-size:10px;font-weight:600;">{peak_pct:+.1f}%</td>'
            f'<td style="padding:5px 4px;color:#ef4444;text-align:right;font-size:10px;">{min_low_pct:+.1f}%</td>'
            f'<td style="padding:5px 4px;text-align:center;font-size:10px;">{result_badge(r.get("result", "-"))}</td>'
            f'<td style="padding:5px 4px;color:#7a8599;text-align:center;font-size:10px;">{_safe_int(r.get("days_to_target"))}일</td>'
            f'<td style="padding:5px 4px;color:#7a8599;font-size:9px;text-align:left;">{r.get("ma_pattern", "-")}</td>'
            f'{"<td style=\"padding:5px 4px;color:#a78bfa;font-size:10px;text-align:left;\">" + str(r.get("sell_ma","") or "") + "</td>" if show_sell_ma else ""}'
            f'<td style="padding:5px 4px;color:#7a8599;font-size:10px;text-align:left;">{r.get("sector", "-")}</td>'
            f'</tr>'
        )

    sell_ma_header = '<th style="padding:5px 4px;color:#a78bfa;text-align:left;font-size:10px;">MA(매도)</th>' if show_sell_ma else ""
    table_height = min(40 + len(filtered) * 34 + 20, 800)

    table_html = (
        '<div style="overflow-x:auto;border:1px solid #1e2530;border-radius:10px;background:#0a0e14;">'
        '<table>'
        '<thead><tr>'
        '<th style="text-align:center;">시장</th>'
        '<th style="text-align:center;">날짜</th>'
        '<th style="text-align:left;">종목</th>'
        '<th style="text-align:left;">코드</th>'
        '<th style="text-align:center;">등급</th>'
        '<th style="text-align:right;">갭</th>'
        '<th style="text-align:right;">진입가</th>'
        '<th style="color:#14b8a6;text-align:right;font-weight:600;">목표율</th>'
        '<th style="text-align:right;">목표가</th>'
        '<th style="text-align:right;">손절가</th>'
        '<th style="text-align:right;">손절율</th>'
        '<th style="color:#14b8a6;text-align:center;font-weight:600;">손익비</th>'
        '<th style="color:#14b8a6;text-align:right;font-weight:600;">기대값</th>'
        '<th style="text-align:right;">최고</th>'
        '<th style="text-align:right;">최저</th>'
        '<th style="text-align:center;">결과</th>'
        '<th style="text-align:center;">소요일</th>'
        '<th style="text-align:left;">MA</th>'
        f'{sell_ma_header}'
        '<th style="text-align:left;">섹터</th>'
        '</tr></thead><tbody>'
        + "\n".join(rows_html) +
        '</tbody></table></div>'
    )

    st.components.v1.html(table_html, height=table_height, scrolling=True)

    st.markdown("#### ▸ 거래 달력")
    cal_data = trades.copy()
    cal_data["month"] = pd.to_datetime(cal_data["date"], errors="coerce").dt.to_period("M")
    months = sorted(cal_data["month"].dropna().unique(), reverse=True)
    display_months = months[:3]
    cal_cols = st.columns(len(display_months)) if display_months else []

    for col_idx, month_period in enumerate(display_months):
        with cal_cols[col_idx]:
            year = month_period.year
            month = month_period.month
            st.markdown(
                f"<div style='color:#e2e8f0;font-size:13px;font-weight:600;margin-bottom:8px;text-align:center;'>{str(year)[2:]}년 {month}월</div>",
                unsafe_allow_html=True,
            )

            dow_header = "".join(
                f"<span style='display:inline-block;width:28px;text-align:center;color:#7a8599;font-size:10px;margin:1px;'>{d}</span>"
                for d in ["월", "화", "수", "목", "금", "토", "일"]
            )
            st.markdown(f"<div style='text-align:center;'>{dow_header}</div>", unsafe_allow_html=True)

            month_trades = cal_data[cal_data["month"] == month_period]
            trade_dates = {}
            for _, t in month_trades.iterrows():
                d = pd.to_datetime(t["date"], errors="coerce")
                if pd.isna(d):
                    continue
                trade_dates.setdefault(d.day, []).append(t["result"])

            cal_obj = calendar.monthcalendar(year, month)
            cal_html = ""
            for week in cal_obj:
                for day in week:
                    if day == 0:
                        cal_html += '<span class="calendar-day cal-empty">·</span>'
                    elif day in trade_dates:
                        results = trade_dates[day]
                        if "잉" in results:
                            cls = "cal-ing"
                        elif "승" in results:
                            cls = "cal-win"
                        elif "패" in results:
                            cls = "cal-lose"
                        else:
                            cls = "cal-empty"
                        cal_html += f'<span class="calendar-day {cls}" title="{len(results)}건">{day}</span>'
                    else:
                        cal_html += f'<span class="calendar-day cal-empty">{day}</span>'
                cal_html += "<br>"

            st.markdown(f"<div style='text-align:center;line-height:1.8;'>{cal_html}</div>", unsafe_allow_html=True)

            w = len(month_trades[month_trades["result"] == "승"])
            l = len(month_trades[month_trades["result"] == "패"])
            p = len(month_trades[month_trades["result"] == "잉"])
            st.markdown(
                f"<div style='text-align:center;margin-top:6px;font-size:11px;'>"
                f"<span style='color:#22c55e;'>승 {w}</span> · "
                f"<span style='color:#ef4444;'>패 {l}</span> · "
                f"<span style='color:#3b82f6;'>잉 {p}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
