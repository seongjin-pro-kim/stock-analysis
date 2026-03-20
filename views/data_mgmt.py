import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils import init_state, df_state


def _safe_num(x, default=0.0):
    try:
        if pd.isna(x):
            return default
        return float(x)
    except Exception:
        return default


def render():
    init_state()
    st.markdown("### ▸ 데이터 관리")

    trades = df_state("trades")
    signals = df_state("signals")
    archive = df_state("signal_archive")
    idx = df_state("major_indices")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("매매 데이터", f"{len(trades)}행")
    c2.metric("시그널 데이터", f"{len(signals)}행")
    c3.metric("아카이브", f"{len(archive)}행")
    c4.metric("지수 데이터", f"{len(idx)}행")

    st.markdown(
        """
        <div style="margin:8px 0 10px 0;color:#7a8599;font-size:12px;">
        데이터가 비어 있으면 sample_data 또는 로딩 단계부터 확인합니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns(2)

    with left:
        st.markdown("#### ▸ trades")
        if trades.empty:
            st.info("trades 데이터가 없습니다.")
        else:
            st.dataframe(trades, use_container_width=True, hide_index=True)

    with right:
        st.markdown("#### ▸ signals")
        if signals.empty:
            st.info("signals 데이터가 없습니다.")
        else:
            st.dataframe(signals, use_container_width=True, hide_index=True)

    st.markdown("#### ▸ 아카이브")
    if archive.empty:
        st.info("signal_archive 데이터가 없습니다.")
    else:
        st.dataframe(archive, use_container_width=True, hide_index=True)

    if not idx.empty and "date" in idx.columns:
        idx = idx.copy()
        idx["date"] = pd.to_datetime(idx["date"], errors="coerce")
        fig = go.Figure()
        for name, color in [("KOSPI", "#3b82f6"), ("KOSDAQ", "#a855f7"), ("NASDAQ", "#14b8a6"), ("S&P500", "#f59e0b")]:
            if name in idx.columns:
                fig.add_trace(go.Scatter(
                    x=idx["date"],
                    y=idx[name],
                    name=name,
                    mode="lines",
                    line=dict(width=2, color=color),
                    hovertemplate=f"{name}: %{{y:.2f}}<extra></extra>",
                ))
        fig.update_layout(
            template="plotly_dark",
            hovermode="x unified",
            height=320,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="#0a0e14",
            plot_bgcolor="#0a0e14",
            legend=dict(orientation="h", y=1.08),
        )
        st.plotly_chart(fig, use_container_width=True)
