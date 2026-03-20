"""📡 시그널 — 확장 카드, 프리뷰, 톤다운 아이콘, 단일색 차트, 실패MA 패턴"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils import init_state, df_state, market_badge, fmt_date_short, archive_result_badge


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


def _mini_table(rows, headers):
    thead = "".join([f"<th style='padding:6px 4px;text-align:left;color:#7a8599;font-size:10px;'>{h}</th>" for h in headers])
    body = "".join(rows)
    return f"""
    <div style="background:#0a0e14;border:1px solid #1e2530;border-radius:10px;overflow-x:auto;">
    <table style="width:100%;border-collapse:collapse;white-space:nowrap;font-variant-numeric:tabular-nums;font-size:11px;">
    <thead><tr style="border-bottom:2px solid #1e2530;background:#111820;">{thead}</tr></thead>
    <tbody>{body}</tbody>
    </table>
    </div>
    """


def render():
    init_state()
    signals = df_state("signals")
    trades = df_state("trades")

    st.markdown("### ▸ 시그널")

    st.markdown(
        """
        <style>
        .sig-kpi{
            background:#0f141b;border:1px solid #1e2530;border-radius:12px;padding:14px 14px 12px 14px;
        }
        .sig-sub{
            color:#7a8599;font-size:12px;margin:6px 0 10px 0;
        }
        .sig-box{
            background:#0f141b;border:1px solid #1e2530;border-radius:12px;padding:12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if signals.empty:
        st.info("시그널 데이터가 없습니다.")
        return

    if "date" in signals.columns:
        signals["date"] = pd.to_datetime(signals["date"], errors="coerce")
    if "signal_date" in signals.columns:
        signals["signal_date"] = pd.to_datetime(signals["signal_date"], errors="coerce")

    total_sig = len(signals)
    strong_cnt = int((signals["strength"] == "강").sum()) if "strength" in signals.columns else 0
    medium_cnt = int((signals["strength"] == "중").sum()) if "strength" in signals.columns else 0
    weak_cnt = int((signals["strength"] == "약").sum()) if "strength" in signals.columns else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="sig-kpi"><div style="color:#7a8599;font-size:12px;">총 시그널</div><div style="color:#e2e8f0;font-size:28px;font-weight:700;">{total_sig}건</div></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="sig-kpi"><div style="color:#7a8599;font-size:12px;">매수</div><div style="color:#e2e8f0;font-size:28px;font-weight:700;">{strong_cnt}건</div></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="sig-kpi"><div style="color:#7a8599;font-size:12px;">매도</div><div style="color:#e2e8f0;font-size:28px;font-weight:700;">{medium_cnt}건</div></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="sig-kpi"><div style="color:#7a8599;font-size:12px;">관망</div><div style="color:#e2e8f0;font-size:28px;font-weight:700;">{weak_cnt}건</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="sig-sub">시그널은 hover 팝업으로 확인하고, 표 대신 차트 중심으로 봅니다.</div>', unsafe_allow_html=True)

    # --- Summary chart
    if "strength" in signals.columns:
        vc = signals["strength"].value_counts()
        order = ["강", "중", "약"]
        values = [int(vc.get(k, 0)) for k in order]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=order,
            y=values,
            marker_color=["#22c55e", "#f59e0b", "#6b7280"],
            hovertemplate="강도: %{x}<br>건수: %{y}<extra></extra>",
        ))
        fig.update_layout(
            template="plotly_dark",
            height=320,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="#0a0e14",
            plot_bgcolor="#0a0e14",
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- signal detail cards
    st.markdown("#### ▸ 최근 시그널")
    sig_rows = []
    view = signals.sort_values("date", ascending=False).head(8) if "date" in signals.columns else signals.head(8)

    for _, r in view.iterrows():
        strength = r.get("strength", "-")
        strength_color = {"강": "#22c55e", "중": "#f59e0b", "약": "#6b7280"}.get(strength, "#7a8599")
        sig_rows.append(
            "<tr style='border-bottom:1px solid #1e2530;'>"
            f"<td style='padding:6px 4px;text-align:center;'>{market_badge(r.get('market',''))}</td>"
            f"<td style='padding:6px 4px;color:#7a8599;text-align:center;font-size:10px;'>{fmt_date_short(r.get('date'))}</td>"
            f"<td style='padding:6px 4px;color:#e2e8f0;text-align:left;font-weight:600;'>{r.get('name','-')}</td>"
            f"<td style='padding:6px 4px;color:#7a8599;text-align:left;font-size:10px;'>{r.get('code','-')}</td>"
            f"<td style='padding:6px 4px;color:{strength_color};text-align:center;font-weight:700;'>{strength}</td>"
            f"<td style='padding:6px 4px;color:#14b8a6;text-align:right;font-weight:600;'>{_safe_num(r.get('gap_rate')):.1f}%</td>"
            f"<td style='padding:6px 4px;color:#22c55e;text-align:center;font-weight:600;'>{r.get('ma_pattern','-')}</td>"
            f"<td style='padding:6px 4px;color:#7a8599;text-align:left;'>{r.get('sector','-')}</td>"
            "</tr>"
        )

    st.markdown(
        _mini_table(sig_rows, ["시장", "날짜", "종목", "코드", "강도", "갭%", "MA", "섹터"]),
        unsafe_allow_html=True,
    )

    # --- archive
    st.markdown("#### ▸ Signal Archive")
    archive = df_state("signal_archive")
    if archive.empty:
        st.info("Signal Archive 데이터가 없습니다.")
    else:
        if "signal_date" in archive.columns:
            archive["signal_date"] = pd.to_datetime(archive["signal_date"], errors="coerce")

        arch_rows = []
        for _, r in archive.sort_values("signal_date", ascending=False).head(8).iterrows():
            arch_rows.append(
                "<tr style='border-bottom:1px solid #1e2530;'>"
                f"<td style='padding:6px 4px;text-align:center;'>{market_badge(r.get('market',''))}</td>"
                f"<td style='padding:6px 4px;color:#7a8599;text-align:center;font-size:10px;'>{fmt_date_short(r.get('signal_date'))}</td>"
                f"<td style='padding:6px 4px;color:#e2e8f0;text-align:left;font-weight:600;'>{r.get('name','-')}</td>"
                f"<td style='padding:6px 4px;color:#7a8599;text-align:right;'>{_safe_num(r.get('gap_rate')):.1f}</td>"
                f"<td style='padding:6px 4px;color:#14b8a6;text-align:right;font-weight:600;'>{_safe_num(r.get('target_rate')):.1f}</td>"
                f"<td style='padding:6px 4px;color:#22c55e;text-align:right;font-weight:600;'>{_safe_num(r.get('progress_pct')):.0f}%</td>"
                f"<td style='padding:6px 4px;color:#7a8599;text-align:center;'>{_safe_int(r.get('days_elapsed'))}일</td>"
                f"<td style='padding:6px 4px;text-align:center;'>{archive_result_badge(r.get('archive_result','-'))}</td>"
                "</tr>"
            )

        st.markdown(
            _mini_table(arch_rows, ["시장", "날짜", "종목", "갭%", "목표율", "진행율", "소요일", "결과"]),
            unsafe_allow_html=True,
        )

    # --- options / notes
    st.markdown("#### ▸ 시그널 메모")
    st.caption("시그널 hover 팝업은 Plotly 차트 위주로 유지하고, 표는 최소화했습니다.")
