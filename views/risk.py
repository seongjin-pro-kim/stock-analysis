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
    st.markdown("### ▸ 리스크")

    risk = st.session_state.get("risk_metrics", {}) or {}
    trades = df_state("trades")

    win_cnt = int((trades["result"] == "승").sum()) if not trades.empty and "result" in trades.columns else 0
    lose_cnt = int((trades["result"] == "패").sum()) if not trades.empty and "result" in trades.columns else 0
    ing_cnt = int((trades["result"] == "잉").sum()) if not trades.empty and "result" in trades.columns else 0
    total = len(trades)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("MDD", f"{_safe_num(risk.get('mdd')):.2f}%")
    c2.metric("VaR", f"{_safe_num(risk.get('var')):.2f}%")
    c3.metric("승률", f"{_safe_num(risk.get('win_rate')):.1f}%")
    c4.metric("RR 평균", f"{_safe_num(risk.get('rr_avg')):.2f}")

    st.markdown(
        """
        <div style="margin:8px 0 12px 0;color:#7a8599;font-size:12px;">
        손실 제한, 변동성, 승률, 손익비를 중심으로 위험도를 확인합니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

    a1, a2, a3 = st.columns(3)
    a1.metric("총 매매", f"{total}건")
    a2.metric("진행중", f"{ing_cnt}건")
    a3.metric("승/패", f"{win_cnt}/{lose_cnt}")

    if "risk_curve" in risk and risk["risk_curve"]:
        df = pd.DataFrame(risk["risk_curve"])
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")

        fig = go.Figure()
        val_col = "value" if "value" in df.columns else df.columns[-1]
        fig.add_trace(go.Scatter(
            x=df["date"] if "date" in df.columns else df.index,
            y=df[val_col],
            mode="lines+markers",
            name="리스크 추이",
            line=dict(color="#38bdf8", width=2),
            hovertemplate="날짜: %{x|%m/%d}<br>값: %{y:.2f}<extra></extra>",
        ))
        fig.update_layout(
            template="plotly_dark",
            height=320,
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="#0a0e14",
            plot_bgcolor="#0a0e14",
            legend=dict(orientation="h", y=1.05),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("리스크 추이 데이터가 없습니다.")

    st.markdown("#### ▸ 위험 요약")
    summary = [
        f"- MDD: {_safe_num(risk.get('mdd')):.2f}%",
        f"- VaR: {_safe_num(risk.get('var')):.2f}%",
        f"- 승률: {_safe_num(risk.get('win_rate')):.1f}%",
        f"- RR 평균: {_safe_num(risk.get('rr_avg')):.2f}",
    ]
    st.markdown("\n".join(summary))
