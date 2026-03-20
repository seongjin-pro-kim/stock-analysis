import streamlit as st
import pandas as pd
import plotly.graph_objects as go


from utils import init_state, df_state
from views import overview, performance, trade_log, signals, risk

st.set_page_config(page_title="Stock Analysis", layout="wide")

init_state()

def render_dashboard():
    st.markdown("### ▸ 메인 대시보드")

    trades = df_state("trades")
    signals_df = df_state("signals")
    archive = df_state("signal_archive")
    idx = df_state("major_indices")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총 매매", f"{len(trades)}건")
    c2.metric("진행중", f"{int((trades['result'] == '잉').sum()) if not trades.empty and 'result' in trades.columns else 0}건")
    c3.metric("시그널", f"{len(signals_df)}건")
    c4.metric("아카이브", f"{len(archive)}건")

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

def main():
    render_dashboard()
    performance.render()
    trade_log.render()
    signals.render()
    risk.render()

if __name__ == "__main__":
    main()
