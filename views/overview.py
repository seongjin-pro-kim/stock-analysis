import streamlit as st
import pandas as pd
from utils import init_state, df_state


def render():
    init_state()
    st.markdown("### ▸ 매매 성과 분석")

    df = df_state("trades")
    if df.empty:
        st.info("데이터가 없습니다.")
        return

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    profit_col = "profit_pct" if "profit_pct" in df.columns else None
    equity_col = "equity" if "equity" in df.columns else None

    fig = go.Figure()
    if profit_col:
        win = df[df.get("result", "") == "승"]
        lose = df[df.get("result", "") == "패"]
        if len(win):
            fig.add_trace(go.Bar(
                x=win["date"], y=win[profit_col], name="승리",
                marker_color="#22c55e",
                hovertemplate="날짜: %{x|%m/%d}<br>수익: %{y:.2f}%<extra></extra>"
            ))
        if len(lose):
            fig.add_trace(go.Bar(
                x=lose["date"], y=lose[profit_col], name="패배",
                marker_color="#7f1d1d",
                hovertemplate="날짜: %{x|%m/%d}<br>수익: %{y:.2f}%<extra></extra>"
            ))

    if equity_col:
        fig.add_trace(go.Scatter(
            x=df["date"], y=df[equity_col], name="누적", mode="lines+markers",
            line=dict(color="#38bdf8", width=2),
            hovertemplate="날짜: %{x|%m/%d}<br>누적: %{y:.2f}<extra></extra>"
        ))

    fig.update_layout(
        template="plotly_dark", barmode="group", hovermode="x unified", height=420,
        margin=dict(l=20, r=20, t=30, b=20),
        paper_bgcolor="#0a0e14", plot_bgcolor="#0a0e14",
        legend=dict(orientation="h", y=1.05)
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### ▸ 수익 인자")
    st.caption("손익비, 기대값, 승률, 보유기간이 성과에 미치는 영향을 보여줍니다.")
