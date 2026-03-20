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


def _safe_int(x, default=0):
    try:
        if pd.isna(x):
            return default
        return int(x)
    except Exception:
        return default


def render():
    init_state()
    st.markdown("### ▸ 대시보드")

    trades = df_state("trades")
    signals = df_state("signals")
    archive = df_state("signal_archive")
    idx = df_state("major_indices")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총 매매", f"{len(trades)}건")
    c2.metric("진행중", f"{_safe_int((trades['result'] == '잉').sum()) if not trades.empty and 'result' in trades.columns else 0}건")
    c3.metric("시그널", f"{len(signals)}건")
    c4.metric("아카이브", f"{len(archive)}건")

    st.markdown(
        """
        <style>
        .card{
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

    if not idx.empty and "date" in idx.columns:
        idx = idx.copy()
        idx["date"] = pd.to_datetime(idx["date"], errors="coerce")

        fig = go.Figure()
        series_colors = {
            "KOSPI": "#3b82f6",
            "KOSDAQ": "#a855f7",
            "NASDAQ": "#14b8a6",
            "S&P500": "#f59e0b",
        }

        for name, color in series_colors.items():
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

    if not archive.empty:
        st.markdown("#### ▸ Signal Archive")
        st.dataframe(archive, use_container_width=True, hide_index=True)

    if not signals.empty and "signal_type" in signals.columns:
        st.markdown("#### ▸ 시그널 요약")
        vc = signals["signal_type"].value_counts()
        pie = go.Figure(data=[go.Pie(
            labels=vc.index,
            values=vc.values,
            hole=.55,
            textinfo="label+percent",
            marker=dict(colors=["#22c55e", "#ef4444", "#3b82f6", "#a855f7"]),
        )])
        pie.update_layout(
            template="plotly_dark",
            height=300,
            margin=dict(l=10, r=10, t=10, b=50),
            paper_bgcolor="#0a0e14",
            plot_bgcolor="#0a0e14",
            showlegend=True,
        )
        st.plotly_chart(pie, use_container_width=True)
