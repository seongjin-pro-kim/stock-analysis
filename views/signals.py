import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils import init_state, df_state


def render():
    init_state()
    df = df_state("signals")
    if df.empty:
        st.info("시그널 데이터가 없습니다.")
        return
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    st.markdown("### ▸ 시그널")
    fig = go.Figure()
    if "signal_type" in df.columns and "count" in df.columns:
        for name, color in [("매수", "#22c55e"), ("매도", "#ef4444"), ("관망", "#a78bfa")]:
            sub = df[df["signal_type"] == name]
            if len(sub):
                fig.add_trace(go.Bar(
                    x=sub["date"], y=sub["count"], name=name, marker_color=color,
                    hovertemplate="날짜: %{x|%m/%d}<br>건수: %{y}<extra></extra>"
                ))
    fig.update_layout(template="plotly_dark", barmode="group", height=360, margin=dict(l=20, r=20, t=20, b=40), paper_bgcolor="#0a0e14", plot_bgcolor="#0a0e14")
    st.plotly_chart(fig, use_container_width=True)
