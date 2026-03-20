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
    st.markdown("### ▸ 시그널")

    signals = df_state("signals")
    if signals.empty:
        st.info("시그널 데이터가 없습니다.")
        return

    if "date" in signals.columns:
        signals["date"] = pd.to_datetime(signals["date"], errors="coerce")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총 시그널", f"{len(signals)}건")
    c2.metric("매수", f"{_safe_int((signals['signal_type'] == '매수').sum()) if 'signal_type' in signals.columns else 0}건")
    c3.metric("매도", f"{_safe_int((signals['signal_type'] == '매도').sum()) if 'signal_type' in signals.columns else 0}건")
    c4.metric("관망", f"{_safe_int((signals['signal_type'] == '관망').sum()) if 'signal_type' in signals.columns else 0}건")

    st.markdown(
        """
        <div style="margin:8px 0 10px 0;color:#7a8599;font-size:12px;">
        시그널은 hover 팝업으로 확인하고, 표 대신 차트 중심으로 봅니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <style>
        .sig-box{
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

    fig = go.Figure()
    if "signal_type" in signals.columns and "count" in signals.columns:
        for name, color in [("매수", "#22c55e"), ("매도", "#ef4444"), ("관망", "#a78bfa")]:
            sub = signals[signals["signal_type"] == name]
            if not sub.empty:
                fig.add_trace(go.Bar(
                    x=sub["date"] if "date" in sub.columns else sub.index,
                    y=sub["count"],
                    name=name,
                    marker_color=color,
                    hovertemplate="날짜: %{x|%m/%d}<br>건수: %{y}<extra></extra>",
                ))
    elif "count" in signals.columns:
        fig.add_trace(go.Bar(
            x=signals["date"] if "date" in signals.columns else signals.index,
            y=signals["count"],
            name="시그널",
            marker_color="#3b82f6",
            hovertemplate="날짜: %{x|%m/%d}<br>건수: %{y}<extra></extra>",
        ))

    fig.update_layout(
        template="plotly_dark",
        barmode="group",
        height=360,
        margin=dict(l=20, r=20, t=20, b=40),
        paper_bgcolor="#0a0e14",
        plot_bgcolor="#0a0e14",
        legend=dict(orientation="h", y=1.05),
    )
    st.plotly_chart(fig, use_container_width=True)

    if "category" in signals.columns:
        vc = signals["category"].value_counts(dropna=True)
        if not vc.empty:
            pie = go.Figure(data=[go.Pie(
                labels=vc.index,
                values=vc.values,
                hole=.55,
                textinfo="label+percent",
                marker=dict(colors=["#38bdf8", "#a855f7", "#f59e0b", "#22c55e"]),
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
