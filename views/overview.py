"""메인 대시보드 — views/overview.py"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils import result_badge, market_badge, fmt_date_short, archive_result_badge


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


def _card(title, value, delta=None, delta_color="#9aa5b4"):
    delta_html = (
        f'<div style="margin-top:4px;color:{delta_color};font-size:11px;font-weight:600;">{delta}</div>'
        if delta is not None else ""
    )
    return f"""
    <div style="background:#0f141b;border:1px solid #1e2530;border-radius:10px;padding:14px 16px 12px 16px;">
        <div style="color:#566270;font-size:11px;margin-bottom:5px;letter-spacing:.4px;">{title}</div>
        <div style="color:#dde3ed;font-size:26px;font-weight:700;line-height:1;">{value}</div>
        {delta_html}
    </div>
    """


def _sparkline(values, color):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(values))),
        y=values,
        mode="lines",
        line=dict(color=color, width=2),
        hoverinfo="skip",
    ))
    fig.update_layout(
        template="plotly_dark",
        margin=dict(l=0, r=0, t=0, b=0),
        height=56,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True),
    )
    return fig


def _best_ma_cards(trades):
    if trades.empty or "ma_pattern" not in trades.columns or "result" not in trades.columns:
        return []
    df = trades[trades["result"].isin(["승", "패"])].copy()
    if df.empty:
        return []
    if "peak_pct" not in df.columns:
        df["peak_pct"] = np.nan
    g = df.groupby("ma_pattern").agg(
        wins=("result", lambda s: (s == "승").sum()),
        total=("result", "count"),
        avg_ret=("peak_pct", "mean"),
    ).reset_index()
    top_wins = g.sort_values(["wins", "avg_ret"], ascending=[False, False]).head(1)
    top_avg = g.sort_values(["avg_ret", "wins"], ascending=[False, False]).head(1)
    picked = pd.concat([top_wins, top_avg]).drop_duplicates("ma_pattern")
    return picked.sort_values(["wins", "avg_ret"], ascending=[False, False]).head(2).to_dict("records")


def render():
    trades = st.session_state.trades.copy()
    equity = st.session_state.equity_curve.copy()
    signal_archive = st.session_state.signal_archive.copy()

    if "date" in trades.columns:
        trades["date"] = pd.to_datetime(trades["date"], errors="coerce")
    if "date" in equity.columns:
        equity["date"] = pd.to_datetime(equity["date"], errors="coerce")
    if "signal_date" in signal_archive.columns:
        signal_archive["signal_date"] = pd.to_datetime(signal_archive["signal_date"], errors="coerce")
    if "expiry_date" in trades.columns:
        trades["expiry_date"] = pd.to_datetime(trades["expiry_date"], errors="coerce")

    st.markdown("### ▸ 메인 대시보드")

    st.markdown("#### ▸ 주요 시장 지표")
    idx_configs = [
        {"name": "KOSPI", "value": 5781.00, "change": 17.80, "color": "#7a9fc0", "series": [5650, 5688, 5720, 5756, 5781]},
        {"name": "KOSDAQ", "value": 1156.46, "change": 0.34, "color": "#9b8fc4", "series": [1122, 1130, 1141, 1152, 1156]},
        {"name": "NASDAQ", "value": 18245.80, "change": 85.50, "color": "#6aada5", "series": [17980, 18060, 18140, 18210, 18246]},
        {"name": "BTC", "value": 70416.89, "change": 1046.75, "color": "#b8a96a", "series": [68200, 68850, 69400, 70050, 70417]},
    ]
    cols = st.columns(4)
    for c, cfg in zip(cols, idx_configs):
        sign = "+" if cfg["change"] >= 0 else ""
        d_color = "#6aad8a" if cfg["change"] >= 0 else "#c98a8a"
        if cfg["name"] == "BTC":
            value = f"${cfg['value']:,.1f}"
            delta = f"{sign}${cfg['change']:,.1f}"
        elif cfg["name"] == "NASDAQ":
            value = f"{cfg['value']:,.2f}"
            delta = f"{sign}{cfg['change']:,.2f}"
        else:
            value = f"{cfg['value']:,.2f}"
            delta = f"{sign}{cfg['change']:.2f}"
        c.markdown(_card(cfg["name"], value, delta, d_color), unsafe_allow_html=True)
        c.plotly_chart(_sparkline(cfg["series"], cfg["color"]), use_container_width=True)

    st.markdown("#### ▸ 핵심 KPI")
    total = len(trades)
    win_cnt = int((trades["result"] == "승").sum()) if "result" in trades.columns else 0
    lose_cnt = int((trades["result"] == "패").sum()) if "result" in trades.columns else 0
    ing_cnt = int((trades["result"] == "잉").sum()) if "result" in trades.columns else 0
    win_rate = (win_cnt / max(win_cnt + lose_cnt, 1)) * 100
    rr_avg = _safe_num(trades["rr_ratio"].mean()) if "rr_ratio" in trades.columns else 0.0
    ev_avg = _safe_num(trades["expected_value"].mean()) if "expected_value" in trades.columns else 0.0

    ma_best = _best_ma_cards(trades)
    k1, k2, k3, k4, k5, k6, k7, k8 = st.columns(8)
    k1.metric("총 매매", f"{total}건")
    k2.metric("승/패", f"{win_cnt}/{lose_cnt}")
    k3.metric("진행중", f"{ing_cnt}건")
    k4.metric("승률", f"{win_rate:.1f}%")
    k5.metric("RR 평균", f"{rr_avg:.2f}")
    k6.metric("기대값", f"{ev_avg:.1f}")
    if len(ma_best) >= 1:
        k7.markdown(_card("Best MA", f"{ma_best[0]['ma_pattern']}", f"승 {int(ma_best[0]['wins'])} / 평균 {ma_best[0]['avg_ret']:.1f}%", "#6aad8a"), unsafe_allow_html=True)
    else:
        k7.markdown(_card("Best MA", "-", "데이터 없음", "#566270"), unsafe_allow_html=True)
    if len(ma_best) >= 2:
        k8.markdown(_card("", f"{ma_best[1]['ma_pattern']}", f"승 {int(ma_best[1]['wins'])} / 평균 {ma_best[1]['avg_ret']:.1f}%", "#6aada5"), unsafe_allow_html=True)
    else:
        k8.markdown(_card("", "-", "", "#566270"), unsafe_allow_html=True)

    st.markdown("#### ▸ 옵션 만기 / 주요 이벤트")
    if not trades.empty and any(c in trades.columns for c in ["expiry_date", "event"]):
        ev = trades.copy()
        if "expiry_date" in ev.columns:
            ev = ev.sort_values("expiry_date", ascending=True)
        ev = ev[[c for c in ["market", "name", "expiry_date", "event"] if c in ev.columns]].head(5)
        rows = []
        for _, r in ev.iterrows():
            rows.append(
                "<tr>"
                f"<td style='padding:6px 5px;text-align:center;'>{market_badge(r.get('market',''))}</td>"
                f"<td style='padding:6px 5px;color:#dde3ed;font-weight:600;'>{r.get('name','-')}</td>"
                f"<td style='padding:6px 5px;color:#566270;text-align:center;'>{fmt_date_short(r.get('expiry_date'))}</td>"
                f"<td style='padding:6px 5px;color:#7a8599;text-align:left;'>{r.get('event','-')}</td>"
                "</tr>"
            )
        st.markdown(
            f"""
            <div class="table-wrap">
            <table class="table-dark">
            <thead><tr>
                <th style="text-align:center;">시장</th>
                <th style="text-align:left;">종목</th>
                <th style="text-align:center;">만기일</th>
                <th style="text-align:left;">이벤트</th>
            </tr></thead>
            <tbody>{''.join(rows)}</tbody>
            </table>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("옵션 만기 / 이벤트 데이터가 없습니다.")

    st.markdown("#### ▸ 최근 매매 / Signal Archive")
    left, right = st.columns([1, 1])

    with left:
        st.markdown("최근 매매")
        if not trades.empty:
            recent = trades.sort_values("date", ascending=False).head(10) if "date" in trades.columns else trades.head(10)
            rows = []
            for _, r in recent.iterrows():
                rows.append(
                    "<tr>"
                    f"<td style='padding:6px 5px;text-align:center;'>{market_badge(r.get('market',''))}</td>"
                    f"<td style='padding:6px 5px;color:#566270;font-size:10px;text-align:center;'>{fmt_date_short(r.get('date'))}</td>"
                    f"<td style='padding:6px 5px;color:#dde3ed;font-weight:600;text-align:left;'>{r.get('name','-')}</td>"
                    f"<td style='padding:6px 5px;color:#7a8599;text-align:right;'>{_safe_num(r.get('gap_rate')):.1f}%</td>"
                    f"<td style='padding:6px 5px;color:#6aada5;font-weight:600;text-align:right;'>{_safe_num(r.get('target_rate')):.1f}%</td>"
                    f"<td style='padding:6px 5px;color:#8fbf8f;font-weight:700;text-align:center;'>{_safe_num(r.get('rr_ratio')):.2f}</td>"
                    f"<td style='padding:6px 5px;text-align:center;'>{result_badge(r.get('result','-'))}</td>"
                    f"<td style='padding:6px 5px;color:#8fbf8f;font-weight:600;text-align:right;'>{_safe_num(r.get('progress_pct', r.get('peak_pct', 0))):+.1f}%</td>"
                    f"<td style='padding:6px 5px;color:#566270;text-align:center;'>{_safe_int(r.get('days_to_target'))}일</td>"
                    "</tr>"
                )
            st.markdown(
                f"""
                <div class="table-wrap">
                <table class="table-dark">
                <thead><tr>
                    <th style="text-align:center;">시장</th>
                    <th style="text-align:center;">날짜</th>
                    <th style="text-align:left;">종목</th>
                    <th style="text-align:right;">갭비율</th>
                    <th style="text-align:right;color:#6aada5;">목표율</th>
                    <th style="text-align:center;color:#8fbf8f;">손익비</th>
                    <th style="text-align:center;">결과</th>
                    <th style="text-align:right;">현재 수익</th>
                    <th style="text-align:center;">소요일</th>
                </tr></thead>
                <tbody>{''.join(rows)}</tbody>
                </table>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("최근 매매 데이터가 없습니다.")

    with right:
        st.markdown("Siganl Achive")
        if not signal_archive.empty:
            view = signal_archive.sort_values("signal_date", ascending=False).head(10) if "signal_date" in signal_archive.columns else signal_archive.head(10)
            rows = []
            for _, r in view.iterrows():
                rows.append(
                    "<tr>"
                    f"<td style='padding:6px 5px;text-align:center;'>{market_badge(r.get('market',''))}</td>"
                    f"<td style='padding:6px 5px;color:#566270;font-size:10px;text-align:center;'>{fmt_date_short(r.get('signal_date'))}</td>"
                    f"<td style='padding:6px 5px;color:#dde3ed;font-weight:600;text-align:left;'>{r.get('name','-')}</td>"
                    f"<td style='padding:6px 5px;color:#7a8599;text-align:right;'>{_safe_num(r.get('gap_rate')):.1f}%</td>"
                    f"<td style='padding:6px 5px;color:#6aada5;font-weight:600;text-align:right;'>{_safe_num(r.get('target_rate')):.1f}%</td>"
                    f"<td style='padding:6px 5px;color:#8fbf8f;font-weight:600;text-align:right;'>{_safe_num(r.get('progress_pct')):.0f}%</td>"
                    f"<td style='padding:6px 5px;color:#566270;text-align:center;'>{_safe_int(r.get('days_elapsed'))}일</td>"
                    f"<td style='padding:6px 5px;text-align:center;'>{archive_result_badge(r.get('archive_result','-'))}</td>"
                    "</tr>"
                )
            st.markdown(
                f"""
                <div class="table-wrap">
                <table class="table-dark">
                <thead><tr>
                    <th style="text-align:center;">시장</th>
                    <th style="text-align:center;">sig. date</th>
                    <th style="text-align:left;">종목명</th>
                    <th style="text-align:right;">갭비율</th>
                    <th style="text-align:right;color:#6aada5;">목표율</th>
                    <th style="text-align:right;color:#8fbf8f;">진행율</th>
                    <th style="text-align:center;">소요일</th>
                    <th style="text-align:center;">목표 결과</th>
                </tr></thead>
                <tbody>{''.join(rows)}</tbody>
                </table>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("Signal Archive 데이터가 없습니다.")

    st.markdown("#### ▸ 계좌별 자산추이")
    if not equity.empty:
        if "account" in equity.columns:
            acc_col = "account"
        elif "account_id" in equity.columns:
            acc_col = "account_id"
        elif "acct" in equity.columns:
            acc_col = "acct"
        else:
            acc_col = None

        y_col = None
        for cand in ["equity", "asset", "balance", "value"]:
            if cand in equity.columns:
                y_col = cand
                break

        fig = go.Figure()
        if acc_col and y_col and "date" in equity.columns:
            eq = equity.copy()
            eq["date"] = pd.to_datetime(eq["date"], errors="coerce")
            eq[acc_col] = eq[acc_col].astype(str).str.replace(r"\D", "", regex=True).str[-4:]
            palette = ["#7a9fc0", "#9b8fc4", "#6aada5", "#b8a96a"]
            for i, (acc, sub) in enumerate(eq.dropna(subset=["date"]).sort_values("date").groupby(acc_col)):
                fig.add_trace(go.Scatter(
                    x=sub["date"],
                    y=sub[y_col],
                    name=str(acc),
                    mode="lines",
                    line=dict(width=2, color=palette[i % len(palette)]),
                    hovertemplate=f"{acc}: %{{y:,.0f}}<extra></extra>",
                ))
        elif y_col and "date" in equity.columns:
            fig.add_trace(go.Scatter(
                x=equity["date"],
                y=equity[y_col],
                name=y_col,
                mode="lines",
                line=dict(width=2, color="#7a9fc0"),
            ))
        fig.update_layout(
            template="plotly_dark",
            hovermode="x unified",
            height=300,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="#0a0e14",
            plot_bgcolor="#0a0e14",
            legend=dict(orientation="h", y=1.08, font=dict(size=11, color="#7a8599")),
            xaxis=dict(gridcolor="#1e2530", color="#566270"),
            yaxis=dict(gridcolor="#1e2530", color="#566270"),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("계좌 추이 데이터가 없습니다.")
