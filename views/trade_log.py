import streamlit as st
import pandas as pd
from utils import init_state, df_state


def render():
    init_state()
    trades = pd.DataFrame(st.session_state.trades).copy()
    if trades.empty:
        st.info("데이터가 없습니다.")
        return

    if "date" in trades.columns:
        trades["date"] = pd.to_datetime(trades["date"], errors="coerce")

    st.markdown("### ▸ 매매 기록")
    # 이하 필터/테이블/달력은 직전 버전 그대로 사용
