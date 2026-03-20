import streamlit as st
import pandas as pd
from utils import init_state, df_state


def render():
    init_state()
    st.markdown("### ▸ 리스크")

    risk = st.session_state.get("risk_metrics", {}) or {}
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("MDD", f"{risk.get('mdd', 0):.2f}%")
    c2.metric("VaR", f"{risk.get('var', 0):.2f}%")
    c3.metric("승률", f"{risk.get('win_rate', 0):.1f}%")
    c4.metric("RR 평균", f"{risk.get('rr_avg', 0):.2f}")
