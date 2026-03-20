import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils import init_state, df_state


def render():
    init_state()
    st.markdown("### ▸ 시장개요")

    df = df_state("major_indices")
    if df.empty:
        st.info("시장 지표 데이터가 없습니다.")
        return

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    st.markdown(
        """
        <style>
        .idx-card{
            background:#0f141b;
            border:1px solid #1e2530;
            border-radius:10px;
            padding:10px 12px;
            margin-bottom:10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    for col, name in zip([c1, c2, c3, c4], ["KOSPI", "KOSDAQ", "NASDAQ", "S&P500"]):
        if name in df.columns:
            last = df[name].dropna().iloc[-1] if not df[name].dropna().empty else None
            prev = df[name].dropna().iloc[-2] if len(df[name].dropna()) > 1 else None
            chg = ((last - prev) / prev * 100) if last is not None and prev not in [None, 0] else 0
            col.metric(name, f"{last:.2f}" if last is not None else "-", f"{chg:.2f}%")
        else:
            col.metric(name, "-")

    fig = go.Figure()
    series_colors = {
        "KOSPI": "#3b82f6",
        "KOSDAQ": "#a855f7",
        "NASDAQ": "#14b8a6",
        "S&P500": "#f59e0b",
    }

    for name, color in series_colors.items():
        if name in df.columns:
            fig.add_trace(go.Scatter(
                x=df["date"],
                y=df[name],
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

    if "sector" in df.columns and "sector_return" in df.columns:
        sectors = df.dropna(subset=["sector", "sector_return"]).copy()
        if not sectors.empty:
            sectors = sectors.sort_values("sector_return", ascending=False)
            bar = go.Figure()
            bar.add_trace(go.Bar(
                x=sectors["sector"],
                y=sectors["sector_return"],
                marker_color=["#22c55e" if v >= 0 else "#ef4444" for v in sectors["sector_return"]],
                hovertemplate="섹터: %{x}<br>등락률: %{y:.2f}%<extra></extra>",
                name="섹터 등락률",
            ))
            bar.update_layout(
                template="plotly_dark",
                height=320,
                margin=dict(l=20, r=20, t=20, b=60),
                paper_bgcolor="#0a0e14",
                plot_bgcolor="#0a0e14",
                xaxis_tickangle=-20,
                showlegend=False,
            )
            st.plotly_chart(bar, use_container_width=True)
