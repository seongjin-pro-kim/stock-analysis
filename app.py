import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 페이지 기본 설정
st.set_page_config(page_title="Money Lens Dashboard", layout="wide")

# --- 1. 디자인 스타일링 (첫 번째 이미지의 카드 디자인 반영) ---
st.markdown("""
    <style>
    /* 메인 배경 및 카드 스타일 */
    .stApp { background-color: #000000; }
    
    div[data-testid="stMetric"] {
        background: rgba(26, 28, 35, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    /* 사이드바 스타일 커스텀 */
    section[data-testid="stSidebar"] {
        background-color: #0B0E14 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* 탭 디자인 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 사이드바 메뉴 (두 번째 이미지 메뉴 반영) ---
with st.sidebar:
    st.title("GAP R-Zone")
    st.markdown("---")
    menu = st.radio(
        "Menu",
        ["대시보드", "매매성과", "매매기록", "시그널", "시장개요", "리스크", "데이터관리"],
        index=0
    )
    st.markdown("---")
    st.caption("Created with Streamlit")

# --- 3. 메인 콘텐츠 (첫 번째 이미지 레이아웃 반영) ---

if menu == "대시보드":
    st.title("Hi, User 👋")
    
    # 상단 총 잔고 영역
    col_bal, col_empty = st.columns([2, 3])
    with col_bal:
        st.subheader("Total Balance")
        st.markdown("## 0.97689522 BTC")
        st.caption("$40,098.36")

    # 레이아웃 분할 (중앙 차트 7 : 우측 지표 3)
    left_main, right_sub = st.columns([7, 3])

    with left_main:
        # 탭 메뉴 (1H, 1D, 1W 등)
        tab1, tab2, tab3 = st.tabs(["1W", "1M", "All"])
        
        with tab1:
            # 첫 번째 이미지의 네온 라인 차트 재현
            df = pd.DataFrame({
                'Day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                'Line A': [200, 450, 400, 600, 300, 550, 480],
                'Line B': [300, 250, 550, 350, 450, 200, 400]
            })
            fig = px.line(df, x='Day', y=['Line A', 'Line B'], 
                          color_discrete_sequence=['#FF4BFF', '#00FFA3'],
                          template="plotly_dark")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig, use_container_width=True)

        # 하단 테이블 (CoinMarketCap 스타일)
        st.subheader("Market Constituents")
        market_data = pd.DataFrame({
            "Coin": ["Bitcoin", "Polygon", "XRP Ledger", "Avalanche"],
            "Price": ["$39,486.21", "$43,759.19", "$71,825.40", "$30,123.98"],
            "Trend": ["+0.96%", "-0.91%", "+0.72%", "-0.42%"]
        })
        st.table(market_data)

    with right_sub:
        # 우측 최근 입금 내역 및 자산 카드
        st.subheader("Recent Deposits")
        with st.container():
            st.write("🪙 Bitcoin: +$244.00")
            st.caption("Today 13:15 PM")
            st.divider()
            st.write("🔷 Ethereum: +0.4213 ETH")
            st.caption("Today 11:18 PM")
        
        st.markdown("### Assets")
        st.info("Crypto Card Detail") # 첫 번째 이미지 우측 하단 카드 영역

else:
    # 다른 메뉴 선택 시 표시될 공간 (추후 전달해주실 내용이 들어갈 곳)
    st.header(f"📍 {menu}")
    st.info("이 메뉴의 세부 내역을 정리해서 전달해 주시면 바로 구현해 드릴게요!")
