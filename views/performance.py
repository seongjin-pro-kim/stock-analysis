import streamlit as st
import pandas as pd
from utils import init_state, df_state

def render():
    init_state()
    trades = df_state("trades")
    if trades.empty:
        st.info("데이터가 없습니다.")
        return

    if "date" in trades.columns:
        trades["date"] = pd.to_datetime(trades["date"], errors="coerce")

    st.markdown("### ▸ 매매 기록")
    st.markdown("""<style>
    .filter-box{background:#0f141b;border:1px solid #1e2530;border-radius:10px;padding:12px 12px 6px 12px;margin-bottom:10px;}
    .badge-win{background:#22c55e22;color:#22c55e;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:600;}
    .badge-lose{background:#ef444422;color:#ef4444;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:600;}
    .badge-ing{background:#3b82f622;color:#3b82f6;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:700;}
    table{width:100%;border-collapse:collapse;font-size:11px;font-variant-numeric:tabular-nums;white-space:nowrap;}
    thead tr{border-bottom:2px solid #1e2530;background:#111820;}
    th{padding:6px 4px;color:#7a8599;font-size:10px;}
    .hl{background:rgba(20,184,166,0.06);}
    </style>""", unsafe_allow_html=True)

    fc1, fc2, fc3, fc4, fc5, fc6, fc7 = st.columns(7)
    with fc1:
        market_filter = st.selectbox("시장", ["전체", "KOSPI", "KOSDAQ"])
    with fc2:
        result_filter = st.selectbox("결과", ["전체", "승", "패", "잉"])
    with fc3:
        sector_filter = st.selectbox("섹터", ["전체"] + sorted(trades["sector"].dropna().unique().tolist()) if "sector" in trades.columns else ["전체"])
    with fc4:
        grade_filter = st.selectbox("등급", ["전체"] + sorted(trades["grade"].dropna().unique().tolist()) if "grade" in trades.columns else ["전체"])
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

    sort_map = {"날짜 (최신)": ("date", False), "날짜 (오래된)": ("date", True), "갭비율 ↓": ("gap_rate", False), "최고수익 ↓": ("peak_pct", False), "손익비 ↓": ("rr_ratio", False), "기대값 ↓": ("expected_value", False), "소요일 ↑": ("days_to_target", True)}
    sort_col, sort_asc = sort_map.get(sort_by, ("date", False))
    if sort_col in filtered.columns:
        filtered = filtered.sort_values(sort_col, ascending=sort_asc)

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
        peak_pct = float(r.get("peak_pct", 0) or 0)
        min_low_pct = float(r.get("min_low_pct", 0) or 0)
        gap_rate = float(r.get("gap_rate", 0) or 0)
        rr_val = float(r.get("rr_ratio", 0) or 0) if pd.notna(r.get("rr_ratio")) else 0
        ev_val = float(r.get("expected_value", 0) or 0) if has_ev and pd.notna(r.get("expected_value")) else 0

        name_style = 'padding:5px 4px;color:#e2e8f0;font-weight:500;font-size:12px;text-align:left;'
        if grade == "A":
            name_style += 'background:rgba(239,68,68,0.16);border-radius:4px;'

        sell_ma_cell = f'<td style="padding:5px 4px;color:#a78bfa;font-size:10px;text-align:left;">{r.get("sell_ma", "") or ""}</td>' if show_sell_ma else ""

        rows_html.append(
            f'<tr style="border-bottom:1px solid #1e2530;">'
            f'<td style="padding:5px 4px;font-size:10px;text-align:center;">{market_badge(r.get("market", ""))}</td>'
            f'<td style="padding:5px 4px;color:#7a8599;font-size:10px;text-align:center;">{date_str}</td>'
            f'<td style="{name_style}">{r.get("name", "-")}</td>'
            f'<td style="padding:5px 4px;color:#7a8599;font-size:10px;text-align:left;">{r.get("code", "-")}</td>'
            f'<td style="padding:5px 4px;color:{grade_colors.get(grade, "#7a8599")};font-weight:600;font-size:10px;text-align:center;">{grade}</td>'
            f'<td style="padding:5px 4px;color:#e2e8f0;text-align:right;font-size:10px;">{gap_rate:.1f}%</td>'
            f'<td style="padding:5px 4px;color:#e2e8f0;text-align:right;font-size:10px;">₩{int(r.get("entry_price", 0) or 0):,}</td>'
            f'<td class="hl" style="padding:5px 4px;color:#14b8a6;text-align:right;font-size:10px;font-weight:600;">{f"{float(r["target_rate"]):.1f}%" if has_target_rate and pd.notna(r.get("target_rate")) else "-"}</td>'
            f'<td style="padding:5px 4px;color:#14b8a6;text-align:right;font-size:10px;">₩{int(r.get("target_price", 0) or 0):,}</td>'
            f'<td style="padding:5px 4px;color:#ef4444;text-align:right;font-size:10px;">₩{int(r.get("stop_price", 0) or 0):,}</td>'
            f'<td style="padding:5px 4px;color:#ef4444;text-align:right;font-size:10px;">{f"{float(r["stop_rate"]):.1f}%" if has_stop_rate and pd.notna(r.get("stop_rate")) else "-"}</td>'
            f'<td class="hl" style="padding:5px 4px;color:#22c55e;text-align:center;font-size:10px;font-weight:600;">{rr_val:.2f}</td>'
            f'<td class="hl" style="padding:5px 4px;color:#38bdf8;text-align:right;font-size:10px;font-weight:600;">{ev_val:.1f}</td>'
            f'<td style="padding:5px 4px;color:#22c55e;text-align:right;font-size:10px;font-weight:600;">{peak_pct:+.1f}%</td>'
            f'<td style="padding:5px 4px;color:#ef4444;text-align:right;font-size:10px;">{min_low_pct:+.1f}%</td>'
            f'<td style="padding:5px 4px;text-align:center;font-size:10px;">{result_badge(r.get("result", "-"))}</td>'
            f'<td style="padding:5px 4px;color:#7a8599;text-align:center;font-size:10px;">{int(r.get("days_to_target", 0) or 0)}일</td>'
            f'<td style="padding:5px 4px;color:#7a8599;font-size:9px;text-align:left;">{r.get("ma_pattern", "-")}</td>'
            f'{sell_ma_cell}'
            f'<td style="padding:5px 4px;color:#7a8599;font-size:10px;text-align:left;">{r.get("sector", "-")}</td>'
            f'</tr>'
        )
