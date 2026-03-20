<<<<<<< HEAD
"""◈ 메인 대시보드 — 톤다운 아이콘, 균일 KPI, MA 넘버링, 정렬 개선, 3배 간격"""
=======
>>>>>>> 259691f (style: unify dashboard theme)
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils import result_badge, market_badge, fmt_date_short, archive_result_badge


DARK_AIRY_PALETTE = [
    "#3B82F6", "#4F86FF", "#5B8CFF", "#6A94FF", "#7A9BFF",
    "#8AA3FF", "#9AAAFE", "#A9B2FE", "#B7BAFF", "#C4C2FF",
]

def render():
    trades = st.session_state.trades
    equity = st.session_state.equity_curve
    positions = st.session_state.positions
    signal_archive = st.session_state.signal_archive

<<<<<<< HEAD
    # ── 1. 지수 차트 (최상단 4개: KOSPI, KOSDAQ, NASDAQ, BTC) ──
    st.markdown("### ▸ 시장 지수")
    idx_configs = [
        {"name": "KOSPI", "value": 2685.42, "change": +12.35, "color": "#3b82f6", "seed": 101},
        {"name": "KOSDAQ", "value": 872.15, "change": -3.21, "color": "#a78bfa", "seed": 102},
        {"name": "NASDAQ", "value": 18245.80, "change": +85.50, "color": "#14b8a6", "seed": 103},
        {"name": "BTC", "value": 87420.50, "change": +1250.30, "color": "#eab308", "seed": 104},
    ]
    idx_cols = st.columns(4)
    for col, cfg in zip(idx_cols, idx_configs):
        with col:
            sign = "+" if cfg["change"] >= 0 else ""
            pct = cfg["change"] / cfg["value"] * 100
            c_cls = "positive" if cfg["change"] >= 0 else "negative"

            # 통화 포맷
            if cfg["name"] == "BTC":
                val_str = f"${cfg['value']:,.1f}"
                chg_str = f"{sign}${cfg['change']:,.1f}"
            elif cfg["name"] == "NASDAQ":
                val_str = f"{cfg['value']:,.2f}"
                chg_str = f"{sign}{cfg['change']:,.2f}"
            else:
                val_str = f"{cfg['value']:,.2f}"
                chg_str = f"{sign}{cfg['change']:.2f}"

            st.markdown(f"""
            <div class="kpi-card" style="padding:12px 16px;">
                <div class="kpi-label">{cfg['name']}</div>
                <div style="font-size:18px; font-weight:700; color:{cfg['color']}; font-variant-numeric:tabular-nums;">{val_str}</div>
                <div class="kpi-sub {c_cls}">{chg_str} ({sign}{pct:.2f}%)</div>
            </div>""", unsafe_allow_html=True)

            # 미니차트
            np.random.seed(cfg["seed"])
            vals = [cfg["value"] * 0.97]
            for _ in range(29):
                vals.append(vals[-1] * (1 + np.random.normal(0.001, 0.008)))
            hex_c = cfg["color"].lstrip("#")
            rgb = ",".join(str(int(hex_c[i:i+2], 16)) for i in (0, 2, 4))
            fig = go.Figure(go.Scatter(
                y=vals, mode="lines", fill="tozeroy",
                fillcolor=f"rgba({rgb},0.08)",
                line=dict(color=cfg["color"], width=1.5),
            ))
            fig.update_layout(
                plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
                height=80, margin=dict(l=0, r=0, t=2, b=0),
                xaxis=dict(showticklabels=False, showgrid=False),
                yaxis=dict(showticklabels=False, showgrid=False),
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── 2. 핵심 지표 KPI (6개: 기존 5개 + Best MA) ────────
    st.markdown("### ▸ 핵심 지표")

    # 거래 계산 (진행중 제외)
    completed = trades[trades["result"].isin(["승", "패"])]
    total_trades = len(completed)
    wins_df = completed[completed["result"] == "승"]
    losses_df = completed[completed["result"] == "패"]
    wins = len(wins_df)
    losses = len(losses_df)
=======
    total_trades = len(trades)
    wins = len(trades[trades["result"] == "승"])
    losses = len(trades[trades["result"] == "패"])
>>>>>>> 259691f (style: unify dashboard theme)
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    avg_days = wins_df["days_to_target"].mean() if wins > 0 else 0

<<<<<<< HEAD
    # 자산 계산
    total_eq = equity.groupby("date")["value"].sum().reset_index()
    total_pnl = total_eq["value"].iloc[-1] - total_eq["value"].iloc[0]
    pnl_pct = (total_pnl / total_eq["value"].iloc[0]) * 100 if total_eq["value"].iloc[0] > 0 else 0
    current_capital = total_eq["value"].iloc[-1]

    # Best MA 계산 (1.승리횟수 순, 2.평균수익 순)
    if len(completed) > 0:
        ma_grp = completed.groupby("ma_pattern").agg(
            win_cnt=("result", lambda x: (x == "승").sum()),
            avg_profit=("peak_pct", "mean"),
        ).reset_index()
        best_by_wins = ma_grp.sort_values("win_cnt", ascending=False).iloc[0] if len(ma_grp) else None
        best_by_profit = ma_grp.sort_values("avg_profit", ascending=False).iloc[0] if len(ma_grp) else None
    else:
        best_by_wins = best_by_profit = None

    c1, c2, c3, c4, c5, c6 = st.columns(6)
=======
    st.markdown("### 📊 핵심 지표")
    c1, c2, c3, c4, c5 = st.columns(5)
>>>>>>> 259691f (style: unify dashboard theme)

    def _kpi(col, label, value, sub="", color_class="neutral"):
        with col:
            st.markdown(
                f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
                f'<div class="kpi-value {color_class}">{value}</div>'
                f'<div class="kpi-sub">{sub}</div></div>',
                unsafe_allow_html=True
            )

    _kpi(c1, "총 거래", f"{total_trades}건", f"승 {wins} · 패 {losses}", "neutral")
<<<<<<< HEAD
    _kpi(c2, "승률", f"{win_rate:.1f}%", "20봉 기준",
         "positive" if win_rate >= 60 else "negative")
    _kpi(c3, "평균 도달일",
         f"{avg_days:.1f}일" if pd.notna(avg_days) and avg_days > 0 else "—",
         "목표 도달까지", "neutral")
    _kpi(c4, "총 손익", f"₩{total_pnl/1e4:,.0f}만",
         f"{pnl_pct:+.1f}%", "positive" if total_pnl >= 0 else "negative")
    _kpi(c5, "현재 자산", f"₩{current_capital/1e4:,.0f}만", "합산 기준", "neutral")

    # Best MA 카드 — 아이콘 → 넘버링
    with c6:
        if best_by_wins is not None:
            ma1 = best_by_wins["ma_pattern"][:20] + ("…" if len(str(best_by_wins["ma_pattern"])) > 20 else "")
            ma2 = best_by_profit["ma_pattern"][:20] + ("…" if len(str(best_by_profit["ma_pattern"])) > 20 else "")
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Best MA</div>
                <div style="font-size:11px; color:#e2e8f0; margin-top:4px;">
                    <span style="color:#14b8a6; font-weight:700;">1.</span> {ma1}<br>
                    <span style="font-size:10px; color:#7a8599;">{int(best_by_wins['win_cnt'])}승</span>
                </div>
                <div style="font-size:11px; color:#e2e8f0; margin-top:2px;">
                    <span style="color:#eab308; font-weight:700;">2.</span> {ma2}<br>
                    <span style="font-size:10px; color:#7a8599;">avg {best_by_profit['avg_profit']:.1f}%</span>
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            _kpi(c6, "Best MA", "—", "데이터 부족", "neutral")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 3. 계좌별 자산 추이 ───────────────────────────────
    st.markdown("### ▸ 자산 추이 (계좌별)")
=======
    _kpi(c2, "승률", f"{win_rate:.1f}%", "20봉 기준", "positive" if win_rate >= 60 else "negative")
    _kpi(c3, "평균 도달일", f"{avg_days:.1f}일" if pd.notna(avg_days) else "—", "목표 도달까지", "neutral")
    _kpi(c4, "총 손익", f"₩{total_pnl/1e4:,.0f}만", f"{pnl_pct:+.1f}%", "positive" if total_pnl >= 0 else "negative")
    _kpi(c5, "현재 자산", f"₩{current_capital/1e4:,.0f}만", "평가 기준", "neutral")

    st.markdown("<br>", unsafe_allow_html=True)

    col_chart, col_pos = st.columns([3, 1])
>>>>>>> 259691f (style: unify dashboard theme)

    account_colors = {"1234": "#14b8a6", "5678": "#3b82f6", "9012": "#a78bfa", "3456": "#eab308"}
    fig_eq = go.Figure()
    for acc_id in equity["account_id"].unique():
        acc_data = equity[equity["account_id"] == acc_id]
        clr = account_colors.get(acc_id, "#7a8599")
        fig_eq.add_trace(go.Scatter(
            x=acc_data["date"], y=acc_data["value"],
            name=f"계좌 {acc_id}",
            mode="lines",
<<<<<<< HEAD
            line=dict(color=clr, width=2),
            hovertemplate=f"계좌 {acc_id}<br>날짜: %{{x|%m/%d}}<br>자산: ₩%{{y:,.0f}}<extra></extra>",
        ))
    fig_eq.update_layout(
        plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
        margin=dict(l=0, r=0, t=10, b=0),
        height=280,
        xaxis=dict(showgrid=False, color="#7a8599"),
        yaxis=dict(showgrid=True, gridcolor="#1e2530", color="#7a8599", tickformat=",.0f"),
        font=dict(color="#e2e8f0"),
        legend=dict(font=dict(color="#7a8599", size=11), orientation="h", y=-0.12),
    )
    st.plotly_chart(fig_eq, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 4. 보유 포지션 + 옵션 만기일/이벤트 테이블 ────────
    col_pos, col_exp = st.columns(2)
=======
            fill="tozeroy",
            fillcolor="rgba(59,130,246,0.10)",
            line=dict(color=DARK_AIRY_PALETTE[0], width=2),
            hovertemplate="날짜: %{x|%m/%d}<br>자산: ₩%{y:,.0f}<extra></extra>",
        ))
        fig.update_layout(
            plot_bgcolor="#0a0e14",
            paper_bgcolor="#0a0e14",
            margin=dict(l=0, r=0, t=10, b=0),
            height=300,
            xaxis=dict(showgrid=False, color="#7a8599"),
            yaxis=dict(showgrid=True, gridcolor="#1e2530", color="#7a8599", tickformat=",.0f"),
            font=dict(color="#e2e8f0"),
        )
        st.plotly_chart(fig, use_container_width=True)
>>>>>>> 259691f (style: unify dashboard theme)

    with col_pos:
        st.markdown("### ▸ 보유 포지션")
        if len(positions) > 0:
            fig_pie = go.Figure(go.Pie(
                labels=positions["name"],
                values=positions["weight"],
                hole=0.55,
<<<<<<< HEAD
                marker=dict(colors=["#14b8a6", "#3b82f6", "#a78bfa", "#eab308", "#ef4444"]),
                textinfo="label+percent",
                textfont=dict(size=11, color="#e2e8f0"),
            ))
            fig_pie.update_layout(
                plot_bgcolor="#0a0e14", paper_bgcolor="#0a0e14",
=======
                marker=dict(colors=[
                    DARK_AIRY_PALETTE[0], DARK_AIRY_PALETTE[2], DARK_AIRY_PALETTE[4],
                    DARK_AIRY_PALETTE[6], DARK_AIRY_PALETTE[8]
                ]),
                textinfo="label+percent",
                textfont=dict(size=11, color="#e2e8f0"),
            ))
            fig2.update_layout(
                plot_bgcolor="#0a0e14",
                paper_bgcolor="#0a0e14",
>>>>>>> 259691f (style: unify dashboard theme)
                margin=dict(l=0, r=0, t=10, b=0),
                height=220, showlegend=False, font=dict(color="#e2e8f0"),
            )
            st.plotly_chart(fig_pie, use_container_width=True)

            for _, p in positions.iterrows():
                color = "#22c55e" if p["pnl"] >= 0 else "#ef4444"
                st.markdown(
                    f'<div style="display:flex; justify-content:space-between; padding:4px 0; font-size:13px;">'
                    f'<span style="color:#e2e8f0">{p["name"]}</span>'
                    f'<span style="color:{color}; font-weight:600">{p["pnl"]:+.1f}%</span></div>',
                    unsafe_allow_html=True
                )
        else:
            st.info("보유 포지션이 없습니다.")

    with col_exp:
        st.markdown("### ▸ 옵션 만기 / 주요 이벤트")
        if len(positions) > 0 and "option_expiry" in positions.columns:
            exp_df = positions.copy()
            exp_df = exp_df[exp_df["option_expiry"].notna() & (exp_df["option_expiry"] != "")]
            if len(exp_df) > 0:
                exp_df["expiry_dt"] = pd.to_datetime(exp_df["option_expiry"], errors="coerce")
                exp_df = exp_df.dropna(subset=["expiry_dt"]).sort_values("expiry_dt").head(5)

                rows_html = ""
                for _, e in exp_df.iterrows():
                    days_left = (e["expiry_dt"] - pd.Timestamp.now()).days
                    urgency_color = "#ef4444" if days_left < 14 else ("#eab308" if days_left < 30 else "#7a8599")
                    event_str = e.get("event_note", "") or ""
                    rows_html += f"""
                    <tr style="border-bottom:1px solid #1e2530;">
                        <td style="padding:6px; color:#e2e8f0; font-weight:500;">{e['name']}</td>
                        <td style="padding:6px; color:{urgency_color}; font-weight:600;">{e['expiry_dt'].strftime('%y-%m-%d')}</td>
                        <td style="padding:6px; color:{urgency_color}; text-align:right;">{days_left}일</td>
                        <td style="padding:6px; color:#7a8599; font-size:11px;">{event_str}</td>
                    </tr>"""

                st.markdown(f"""
                <div style="overflow-x:auto; border:1px solid #1e2530; border-radius:8px;">
                <table style="width:100%; border-collapse:collapse; font-size:12px; font-variant-numeric:tabular-nums;">
                    <thead>
                        <tr style="border-bottom:2px solid #1e2530; background:#111820;">
                            <th style="padding:6px; color:#7a8599; text-align:left;">종목</th>
                            <th style="padding:6px; color:#7a8599; text-align:left;">만기일</th>
                            <th style="padding:6px; color:#7a8599; text-align:right;">D-day</th>
                            <th style="padding:6px; color:#7a8599; text-align:left;">이벤트</th>
                        </tr>
                    </thead>
                    <tbody>{rows_html}</tbody>
                </table>
                </div>""", unsafe_allow_html=True)
            else:
                st.info("옵션 만기일 데이터가 없습니다.")
        else:
            st.info("포지션 데이터에 만기일 정보가 없습니다.")

    st.markdown("<br>", unsafe_allow_html=True)

<<<<<<< HEAD
    # ── 5. 최근 매매 (좌) + Signal Archive (우) ───────────
    # 정렬 규칙: 시장·날짜·손익비·소요일=가운데, 종목=좌측, 갭·목표·진행·수익=우측
    col_recent, col_archive = st.columns(2)

    with col_recent:
        st.markdown("### ▸ 최근 매매")
        recent = trades.sort_values("date", ascending=False).head(10).copy()

        rows_html = ""
        for _, r in recent.iterrows():
            pnl_val = r["peak_pct"] if r["result"] == "승" else r["min_low_pct"]
            pnl_color = "#22c55e" if pnl_val >= 0 else "#ef4444"
            if r["result"] == "잉":
                current_pnl = r["peak_pct"]
                pnl_color = "#3b82f6"
            else:
                current_pnl = pnl_val

            rr = r.get("rr_ratio", 0)
            rr_str = f"{float(rr):.1f}" if pd.notna(rr) else "-"
            tgt_rate = r.get("target_rate", 0)
            tgt_str = f"{float(tgt_rate):.1f}%" if pd.notna(tgt_rate) else "-"

            if r["entry_price"] > 0 and r["target_price"] > r["entry_price"]:
                progress = (r["peak_pct"] / ((r["target_price"] - r["entry_price"]) / r["entry_price"] * 100)) * 100
                progress = min(max(progress, 0), 100)
            else:
                progress = 0

            rows_html += f"""
            <tr style="border-bottom:1px solid #1e2530;">
                <td style="padding:6px; font-size:11px; text-align:center;">{market_badge(r['market'])}</td>
                <td style="padding:6px; color:#7a8599; font-size:11px; text-align:center;">{fmt_date_short(r['date'])}</td>
                <td style="padding:6px; color:#e2e8f0; font-weight:500; font-size:12px; text-align:left;">{r['name']}</td>
                <td style="padding:6px; color:#e2e8f0; text-align:right; font-size:11px;">{r['gap_rate']:.1f}%</td>
                <td style="padding:6px; color:#14b8a6; text-align:right; font-size:11px;">{tgt_str}</td>
                <td style="padding:6px; color:#e2e8f0; text-align:center; font-size:11px;">{rr_str}</td>
                <td style="padding:6px; text-align:right; font-size:11px; color:#7a8599;">{progress:.0f}%</td>
                <td style="padding:6px; color:{pnl_color}; text-align:right; font-size:11px; font-weight:600;">{current_pnl:+.1f}%</td>
                <td style="padding:6px; color:#7a8599; text-align:center; font-size:11px;">{r['days_to_target']}일</td>
            </tr>"""

        st.markdown(f"""
        <div style="overflow-x:auto; border:1px solid #1e2530; border-radius:8px;">
        <table style="width:100%; border-collapse:collapse; font-size:12px; font-variant-numeric:tabular-nums; white-space:nowrap;">
            <thead>
                <tr style="border-bottom:2px solid #1e2530; background:#111820;">
                    <th style="padding:6px; color:#7a8599; text-align:center;">시장</th>
                    <th style="padding:6px; color:#7a8599; text-align:center;">날짜</th>
                    <th style="padding:6px; color:#7a8599; text-align:left;">종목</th>
                    <th style="padding:6px; color:#7a8599; text-align:right;">갭%</th>
                    <th style="padding:6px; color:#7a8599; text-align:right;">목표율</th>
                    <th style="padding:6px; color:#7a8599; text-align:center;">손익비</th>
                    <th style="padding:6px; color:#7a8599; text-align:right;">진행</th>
                    <th style="padding:6px; color:#7a8599; text-align:right;">수익%</th>
                    <th style="padding:6px; color:#7a8599; text-align:center;">소요일</th>
                </tr>
            </thead>
            <tbody>{rows_html}</tbody>
        </table>
        </div>""", unsafe_allow_html=True)

    with col_archive:
        st.markdown("### ▸ Signal Archive")
        if len(signal_archive) > 0:
            archive = signal_archive.sort_values("signal_date", ascending=False).head(10)
            rows_html = ""
            for _, a in archive.iterrows():
                rows_html += f"""
                <tr style="border-bottom:1px solid #1e2530;">
                    <td style="padding:6px; font-size:11px; text-align:center;">{market_badge(a['market'])}</td>
                    <td style="padding:6px; color:#7a8599; font-size:11px; text-align:center;">{fmt_date_short(a['signal_date'])}</td>
                    <td style="padding:6px; color:#e2e8f0; font-weight:500; font-size:12px; text-align:left;">{a['name']}</td>
                    <td style="padding:6px; color:#e2e8f0; text-align:right; font-size:11px;">{a['gap_rate']:.1f}%</td>
                    <td style="padding:6px; color:#14b8a6; text-align:right; font-size:11px;">{a['target_rate']:.1f}%</td>
                    <td style="padding:6px; color:#e2e8f0; text-align:right; font-size:11px;">{a['progress_pct']:.0f}%</td>
                    <td style="padding:6px; color:#7a8599; text-align:center; font-size:11px;">{a['days_elapsed']}일</td>
                    <td style="padding:6px; text-align:center; font-size:11px;">{archive_result_badge(a['archive_result'])}</td>
                </tr>"""

            st.markdown(f"""
            <div style="overflow-x:auto; border:1px solid #1e2530; border-radius:8px;">
            <table style="width:100%; border-collapse:collapse; font-size:12px; font-variant-numeric:tabular-nums; white-space:nowrap;">
                <thead>
                    <tr style="border-bottom:2px solid #1e2530; background:#111820;">
                        <th style="padding:6px; color:#7a8599; text-align:center;">시장</th>
                        <th style="padding:6px; color:#7a8599; text-align:center;">날짜</th>
                        <th style="padding:6px; color:#7a8599; text-align:left;">종목</th>
                        <th style="padding:6px; color:#7a8599; text-align:right;">갭%</th>
                        <th style="padding:6px; color:#7a8599; text-align:right;">목표율</th>
                        <th style="padding:6px; color:#7a8599; text-align:right;">진행율</th>
                        <th style="padding:6px; color:#7a8599; text-align:center;">소요일</th>
                        <th style="padding:6px; color:#7a8599; text-align:center;">결과</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
            </div>""", unsafe_allow_html=True)
        else:
            st.info("시그널 아카이브 데이터가 없습니다.")
=======
    st.markdown("### 🕐 최근 매매")
    recent = trades.sort_values("date", ascending=False).head(8).copy()
    recent["date_str"] = recent["date"].dt.strftime("%m/%d")

    from utils import result_badge, market_badge
    rows_html = ""
    for _, r in recent.iterrows():
        pnl_color = "#22c55e" if r["peak_pct"] >= 20 else "#ef4444"
        rows_html += (
            f'<tr style="border-bottom:1px solid #1e2530;">'
            f'<td style="padding:8px; color:#7a8599;">{r["date_str"]}</td>'
            f'<td style="padding:8px; color:#e2e8f0; font-weight:500;">{r["name"]}</td>'
            f'<td style="padding:8px;">{market_badge(r["market"])}</td>'
            f'<td style="padding:8px; color:#e2e8f0; text-align:right;">{r["gap_rate"]:.1f}%</td>'
            f'<td style="padding:8px; text-align:center;">{result_badge(r["result"])}</td>'
            f'<td style="padding:8px; color:{pnl_color}; text-align:right; font-weight:600;">{r["peak_pct"]:+.1f}%</td>'
            f'<td style="padding:8px; color:#7a8599; text-align:right;">{r["days_to_target"]}일</td>'
            f'</tr>'
        )

    st.markdown(
        f'<div style="overflow-x:auto;"><table style="width:100%; border-collapse:collapse; font-size:13px; font-variant-numeric:tabular-nums;">'
        f'<thead><tr style="border-bottom:2px solid #1e2530;">'
        f'<th style="padding:8px; color:#7a8599; text-align:left;">날짜</th>'
        f'<th style="padding:8px; color:#7a8599; text-align:left;">종목</th>'
        f'<th style="padding:8px; color:#7a8599; text-align:left;">시장</th>'
        f'<th style="padding:8px; color:#7a8599; text-align:right;">갭비율</th>'
        f'<th style="padding:8px; color:#7a8599; text-align:center;">결과</th>'
        f'<th style="padding:8px; color:#7a8599; text-align:right;">최고수익</th>'
        f'<th style="padding:8px; color:#7a8599; text-align:right;">소요일</th>'
        f'</tr></thead><tbody>{rows_html}</tbody></table></div>',
        unsafe_allow_html=True
    )
>>>>>>> 259691f (style: unify dashboard theme)
