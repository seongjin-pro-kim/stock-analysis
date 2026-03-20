"""🌐 시장 개요 — 톤다운 아이콘, KOSPI/KOSDAQ/NASDAQ/BTC, 섹터 차트"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils import init_state, df_state


def _safe_num(x, default=0.0):
    try:
        if pd.isna(x):
            return default
        return float(x)
    except Exception:
        return default


def _panel(title, value, delta=None, color="#e2e8f0"):
    delta_html = ""
    if delta is not None:
        delta_html = f'<div style="margin-top:4px;color:{color};font-size:12px;font-weight:600;">{delta}</div>'
    return f"""
    <div style="background:#0f141b;border:1px solid #1e2530;border-radius:12px;padding:14px 14px 12px 14px;">
        <div style="color:#7a8599;font-size:12px;margin-bottom:6px;">{title}</div>
        <div style="color:#e2e8f0;font-size:28px;font-weight:700;line-height:1;">{value}</div>
        {delta_html}
    </div>
    """


def render():
    init_state()
    st.markdown("### ▸ 시장 개요")

    st.markdown(
        """
        <style>
        .section-title{
            color:#e2e8f0;font-size:18px;font-weight:700;margin:6px 0 10px 0;
        }
        .subtle{
            color:#7a8599;font-size:12px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    indices = [
        {"name": "KOSPI", "value": 2685.42, "change": +12.35, "color": "#3b82f6"},
        {"name": "KOSDAQ", "value": 872.15, "change": -3.21, "color": "#a855f7"},
        {"name": "NASDAQ", "value": 18245.80, "change": +85.50, "color": "#14b8a6"},
        {"name": "BTC", "value": 87420.50, "change": +1250.30, "color": "#eab308"},
    ]

    st.markdown("#### ▸ 주요 시장 지표")
    cols = st.columns(4)
    for c, idx in zip(cols, indices):
        sign = "+" if idx["change"] >= 0 else ""
        if idx["name"] == "BTC":
            value = f"${idx['value']:,.1f}"
            delta = f"{sign}${idx['change']:,.1f}"
        elif idx["name"] == "NASDAQ":
            value = f"{idx['value']:,.2f}"
            delta = f"{sign}{idx['change']:,.2f}"
        else:
            value = f"{idx['value']:,.2f}"
            delta = f"{sign}{idx['change']:.2f}"
        c.markdown(_panel(idx["name"], value, delta, idx["color"]), unsafe_allow_html=True)

    market_df = df_state("major_indices")
    if not market_df.empty and "date" in market_df.columns:
        st.markdown("#### ▸ 지수 차트")
        market_df = market_df.copy()
        market_df["date"] = pd.to_datetime(market_df["date"], errors="coerce")
        fig = go.Figure()
        for name, color in [("KOSPI", "#3b82f6"), ("KOSDAQ", "#a855f7"), ("NASDAQ", "#14b8a6"), ("BTC", "#eab308")]:
            if name in market_df.columns:
                fig.add_trace(go.Scatter(
                    x=market_df["date"],
                    y=market_df[name],
                    name=name,
                    mode="lines",
                    line=dict(width=2, color=color),
                    hovertemplate=f"{name}: %{{y:.2f}}<extra></extra>",
                ))
        fig.update_layout(
            template="plotly_dark",
            hovermode="x unified",
            height=340,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="#0a0e14",
            plot_bgcolor="#0a0e14",
            legend=dict(orientation="h", y=1.08),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("시장 지표 데이터가 없습니다.")

    st.markdown("#### ▸ 섹터별 등락률")
    sector_df = df_state("sector_overview")
    if not sector_df.empty and {"sector", "return_pct"}.issubset(sector_df.columns):
        sector_df = sector_df.copy()
        sector_df["return_pct"] = pd.to_numeric(sector_df["return_pct"], errors="coerce")
        sector_df = sector_df.dropna(subset=["sector", "return_pct"]).sort_values("return_pct", ascending=False)

        if not sector_df.empty:
            bar = go.Figure()
            bar.add_trace(go.Bar(
                x=sector_df["sector"],
                y=sector_df["return_pct"],
                marker_color=["#22c55e" if v >= 0 else "#ef4444" for v in sector_df["return_pct"]],
                hovertemplate="섹터: %{x}<br>등락률: %{y:.2f}%<extra></extra>",
                name="섹터 등락률",
            ))
            bar.update_layout(
                template="plotly_dark",
                height=330,
                margin=dict(l=20, r=20, t=20, b=60),
                paper_bgcolor="#0a0e14",
                plot_bgcolor="#0a0e14",
                xaxis_tickangle=-20,
                showlegend=False,
            )
            st.plotly_chart(bar, use_container_width=True)
    else:
        st.info("섹터별 등락률 데이터가 없습니다.")

    st.markdown("#### ▸ 시장 요약")
    st.caption("KOSPI/KOSDAQ/NASDAQ/BTC 지표와 섹터 흐름을 같이 확인합니다.")
