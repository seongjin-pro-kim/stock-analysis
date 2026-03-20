"""▤ 매매 기록 — 톤다운 아이콘, 정렬 통일, 등급A 종목 음영, 뱃지 축소"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from utils import result_badge, market_badge

import calendar


def render():
    trades = st.session_state.trades.copy()

    st.markdown("### ▸ 매매 기록")

    # ── 필터 행 (7열) ──────────────────────────────────
    fc1, fc2, fc3, fc4, fc5, fc6, fc7 = st.columns(7)
    with fc1:
        market_filter = st.selectbox("시장", ["전체", "KOSPI", "KOSDAQ"])
    with fc2:
        result_filter = st.selectbox("결과", ["전체", "승", "패", "잉"])
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
            rr_max = float(trades["rr_ratio"].max())
            rr_threshold = st.slider("최소 RR", min_value=0.0,
                                     max_value=round(rr_max, 1),
                                     value=0.0, step=0.1)
        else:
            rr_threshold = 0.0
            st.caption("RR 데이터 없음")
    with fc7:
        sort_by = st.selectbox("정렬", ["날짜 (최신)", "날짜 (오래된)", "갭비율 ↓", "최고수익 ↓", "손익비 ↓", "기대값 ↓", "소요일 ↑"])

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
        "손익비 ↓": ("rr_ratio", False),
        "기대값 ↓": ("expected_value", False),
        "소요일 ↑": ("days_to_target", True),
    }
    sort_col, sort_asc = sort_map.get(sort_by, ("date", False))
    if sort_col in filtered.columns:
        filtered = filtered.sort_values(sort_col, ascending=sort_asc)
    else:
        filtered = filtered.sort_values("date", ascending=False)

    # 건수 표시
    in_progress = len(trades[trades["result"] == "잉"])
    st.markdown(f"총 {len(filtered)}건 / {len(trades)}건 (진행중: :blue[{in_progress}건])")

    # ── 거래 테이블 (정렬 통일 + 등급A 음영) ──────────────
    # 정렬 규칙: 시장/날짜/손익비/소요일=가운데, 종목=좌측, 갭/목표/진행/수익=우측, MA=좌측
    show_sell_ma = result_filter in ["승", "패"]
    has_ev = "expected_value" in filtered.columns
    has_target_rate = "target_rate" in filtered.columns
    has_stop_rate = "stop_rate" in filtered.columns

    rows_html = []
    for _, r in filtered.iterrows():
        peak_color = "#22c55e" if r["peak_pct"] >= 20 else ("#eab308" if r["peak_pct"] >= 10 else "#ef4444")
        low_color = "#ef4444" if r["min_low_pct"] < -5 else "#7a8599"
        date_str = x.strftime("%m/%d")
        grade = r.get("grade", "-") or "-"
        grade_colors = {"A": "#22c55e", "B": "#eab308", "C": "#ef4444"}
        g_color = grade_colors.get(grade, "#7a8599")
        tgt_rate = f"{float(r['target_rate']):.1f}%" if has_target_rate and pd.notna(r.get("target_rate")) else "-"
        stp_rate = f"{float(r['stop_rate']):.1f}%" if has_stop_rate and pd.notna(r.get("stop_rate")) else "-"
        rr_val = float(r.get("rr_ratio", 0)) if pd.notna(r.get("rr_ratio")) else 0
        rr_str = f"{rr_val:.2f}"
        rr_color = "#22c55e" if rr_val >= 2.0 else ("#eab308" if rr_val >= 1.5 else "#ef4444")
        ev_val = float(r.get("expected_value", 0)) if has_ev and pd.notna(r.get("expected_value")) else 0
        ev_str = f"{ev_val:.1f}"
        ev_color = "#22c55e" if ev_val >= 15 else ("#eab308" if ev_val >= 5 else "#7a8599")
        res_badge = result_badge(r["result"])
        sell_ma_cell = ""
        if show_sell_ma:
            sell_ma = r.get("sell_ma", "") or ""
            sell_ma_cell = f'<td style="padding:6px 4px;color:#a78bfa;font-size:10px;text-align:left;">{sell_ma}</td>'

        # 등급 A일 경우 종목명에 빨간색 투명도 30% 음영처리
        name_style = 'padding:6px 4px;color:#e2e8f0;font-weight:500;font-size:12px;text-align:left;'
        if grade == "A":
            name_style += 'background:rgba(239,68,68,0.30);border-radius:3px;'

        rows_html.append(
            f'<tr style="border-bottom:1px solid #1e2530;">'
            f'<td style="padding:6px 4px;font-size:11px;text-align:center;">{market_badge(r["market"])}</td>'
            f'<td style="padding:6px 4px;color:#7a8599;font-size:11px;text-align:center;">{date_str}</td>'
            f'<td style="{name_style}">{r["name"]}</td>'
            f'<td style="padding:6px 4px;color:#7a8599;font-size:10px;text-align:left;">{r["code"]}</td>'
            f'<td style="padding:6px 4px;color:{g_color};font-weight:600;font-size:11px;text-align:center;">{grade}</td>'
            f'<td style="padding:6px 4px;color:#e2e8f0;text-align:right;font-size:11px;">{r["gap_rate"]:.1f}%</td>'
            f'<td style="padding:6px 4px;color:#e2e8f0;text-align:right;font-size:11px;">₩{r["entry_price"]:,}</td>'
            f'<td class="hl" style="padding:6px 4px;color:#14b8a6;text-align:right;font-size:11px;font-weight:600;">{tgt_rate}</td>'
            f'<td style="padding:6px 4px;color:#14b8a6;text-align:right;font-size:11px;">₩{r["target_price"]:,}</td>'
            f'<td style="padding:6px 4px;color:#ef4444;text-align:right;font-size:11px;">₩{r["stop_price"]:,}</td>'
            f'<td style="padding:6px 4px;color:#ef4444;text-align:right;font-size:11px;">{stp_rate}</td>'
            f'<td class="hl" style="padding:6px 4px;color:{rr_color};text-align:center;font-size:11px;font-weight:600;">{rr_str}</td>'
            f'<td class="hl" style="padding:6px 4px;color:{ev_color};text-align:right;font-size:11px;font-weight:600;">{ev_str}</td>'
            f'<td style="padding:6px 4px;color:{peak_color};text-align:right;font-size:11px;font-weight:600;">{r["peak_pct"]:+.1f}%</td>'
            f'<td style="padding:6px 4px;color:{low_color};text-align:right;font-size:11px;">{r["min_low_pct"]:+.1f}%</td>'
            f'<td style="padding:6px 4px;text-align:center;font-size:11px;">{res_badge}</td>'
            f'<td style="padding:6px 4px;color:#7a8599;text-align:center;font-size:11px;">{r["days_to_target"]}일</td>'
            f'<td style="padding:6px 4px;color:#7a8599;font-size:9px;text-align:left;">{r["ma_pattern"]}</td>'
            f'{sell_ma_cell}'
            f'<td style="padding:6px 4px;color:#7a8599;font-size:11px;text-align:left;">{r["sector"]}</td>'
            f'</tr>'
        )

    sell_ma_header = '<th style="padding:6px 4px;color:#a78bfa;text-align:left;font-size:11px;">MA(매도)</th>' if show_sell_ma else ""

    # 테이블 높이 계산
    table_height = 40 + len(filtered) * 36 + 20
    table_height = min(table_height, 800)

    table_css = """
    <style>
    body { margin:0; padding:0; background:transparent; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; }
    .badge-win{background:#22c55e22;color:#22c55e;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600;}
    .badge-lose{background:#ef444422;color:#ef4444;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:600;}
    .badge-ing{background:#3b82f622;color:#3b82f6;padding:2px 8px;border-radius:4px;font-size:12px;font-weight:700;}
    .badge-kospi{background:#3b82f622;color:#3b82f6;padding:1px 4px;border-radius:3px;font-size:9px;font-weight:600;}
    .badge-kosdaq{background:#8b5cf622;color:#a78bfa;padding:1px 4px;border-radius:3px;font-size:9px;font-weight:600;}
    .badge-nasdaq{background:#14b8a622;color:#14b8a6;padding:1px 4px;border-radius:3px;font-size:9px;font-weight:600;}
    .badge-btc{background:#eab30822;color:#eab308;padding:1px 4px;border-radius:3px;font-size:9px;font-weight:600;}
    .hl{background:rgba(20,184,166,0.06);}
    table{width:100%;border-collapse:collapse;font-size:12px;font-variant-numeric:tabular-nums;white-space:nowrap;}
    thead tr{border-bottom:2px solid #1e2530;background:#111820;}
    th{padding:6px 4px;color:#7a8599;font-size:11px;}
    </style>
    """

    table_html = (
        table_css
        + '<div style="overflow-x:auto;border:1px solid #1e2530;border-radius:8px;background:#0a0e14;">'
        + '<table>'
        + '<thead><tr>'
        + '<th style="text-align:center;">시장</th>'
        + '<th style="text-align:center;">날짜</th>'
        + '<th style="text-align:left;">종목</th>'
        + '<th style="text-align:left;">코드</th>'
        + '<th style="text-align:center;">등급</th>'
        + '<th style="text-align:right;">갭</th>'
        + '<th style="text-align:right;">진입가</th>'
        + '<th class="hl" style="color:#14b8a6;text-align:right;font-weight:600;">목표율</th>'
        + '<th style="text-align:right;">목표가</th>'
        + '<th style="text-align:right;">손절가</th>'
        + '<th style="text-align:right;">손절율</th>'
        + '<th class="hl" style="color:#14b8a6;text-align:center;font-weight:600;">손익비</th>'
        + '<th class="hl" style="color:#14b8a6;text-align:right;font-weight:600;">기대값</th>'
        + '<th style="text-align:right;">최고</th>'
        + '<th style="text-align:right;">최저</th>'
        + '<th style="text-align:center;">결과</th>'
        + '<th style="text-align:center;">소요일</th>'
        + '<th style="text-align:left;">MA</th>'
        + sell_ma_header
        + '<th style="text-align:left;">섹터</th>'
        + '</tr></thead>'
        + '<tbody>'
        + "\n".join(rows_html)
        + '</tbody></table></div>'
    )

    st.components.v1.html(table_html, height=table_height, scrolling=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 거래 달력 (개선된 월별 달력 뷰) ──────────────────
    st.markdown("#### ▸ 거래 달력")

    cal_data = trades.copy()
    cal_data["month"] = cal_data["date"].dt.to_period("M")
    months = sorted(cal_data["month"].unique(), reverse=True)

    display_months = months[:3]
    cal_cols = st.columns(len(display_months))

    for col_idx, month_period in enumerate(display_months):
        with cal_cols[col_idx]:
            year = month_period.year
            month = month_period.month
            month_str = f"{str(year)[2:]}년 {month}월"
            st.markdown(f"<div style='color:#e2e8f0; font-size:13px; font-weight:600; margin-bottom:8px; text-align:center;'>{month_str}</div>",
                        unsafe_allow_html=True)

            dow_header = "".join(
                f"<span style='display:inline-block; width:28px; text-align:center; color:#7a8599; font-size:10px; margin:1px;'>{d}</span>"
                for d in ["월", "화", "수", "목", "금", "토", "일"]
            )
            st.markdown(f"<div style='text-align:center;'>{dow_header}</div>", unsafe_allow_html=True)

            month_trades = cal_data[cal_data["month"] == month_period]
            trade_dates = {}
            for _, t in month_trades.iterrows():
                d = t["date"].day
                if d not in trade_dates:
                    trade_dates[d] = []
                trade_dates[d].append(t["result"])

            cal_obj = calendar.monthcalendar(year, month)
            cal_html = ""
            for week in cal_obj:
                for day in week:
                    if day == 0:
                        cal_html += '<span class="calendar-day cal-empty">·</span>'
                    else:
                        if day in trade_dates:
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

            st.markdown(f"<div style='text-align:center; line-height:1.8;'>{cal_html}</div>", unsafe_allow_html=True)

            w = len(month_trades[month_trades["result"] == "승"])
            l = len(month_trades[month_trades["result"] == "패"])
            p = len(month_trades[month_trades["result"] == "잉"])
            st.markdown(f"""
            <div style='text-align:center; margin-top:6px; font-size:11px;'>
                <span style='color:#22c55e;'>승 {w}</span> ·
                <span style='color:#ef4444;'>패 {l}</span> ·
                <span style='color:#3b82f6;'>잉 {p}</span>
            </div>""", unsafe_allow_html=True)
