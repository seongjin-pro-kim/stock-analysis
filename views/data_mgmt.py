"""💾 데이터 관리 — CSV 업로드, 직접 입력, 포지션 관리, 데이터 요약"""
import streamlit as st
import pandas as pd
import io

def render():
    st.markdown("### 💾 데이터 관리")

    tab1, tab2, tab3, tab4 = st.tabs(["📤 CSV 업로드", "✏️ 직접 입력", "📌 포지션 관리", "📊 데이터 요약"])

    # ── CSV 업로드 ─────────────────────────────────────
    with tab1:
        st.markdown("#### CSV 파일 업로드")
        st.markdown("""
        <div style="background:#111820; border:1px solid #1e2530; border-radius:8px; padding:12px; font-size:12px; color:#7a8599; margin-bottom:16px;">
            <strong style="color:#e2e8f0;">필수 컬럼:</strong> date, code, name, market, gap_rate, target_price, stop_price, entry_price, result, result_detail, days_to_target, peak_pct, min_low_pct, ma_pattern, volume_spike, sector
        </div>""", unsafe_allow_html=True)

        uploaded = st.file_uploader("CSV 파일 선택", type=["csv"], key="csv_upload")

        if uploaded:
            try:
                new_df = pd.read_csv(uploaded)
                st.markdown(f"<div style='color:#14b8a6; font-size:13px;'>✅ {len(new_df)}건 로드됨</div>",
                            unsafe_allow_html=True)

                # 미리보기
                st.dataframe(new_df.head(10), use_container_width=True, hide_index=True)

                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("기존 데이터에 추가", key="append_csv"):
                        new_df["date"] = pd.to_datetime(new_df["date"])
                        st.session_state.trades = pd.concat(
                            [st.session_state.trades, new_df], ignore_index=True
                        ).drop_duplicates(subset=["date", "code"], keep="last")
                        st.success(f"✅ {len(new_df)}건이 추가되었습니다.")
                        st.rerun()

                with col_b:
                    if st.button("기존 데이터 교체", key="replace_csv"):
                        new_df["date"] = pd.to_datetime(new_df["date"])
                        st.session_state.trades = new_df
                        st.success(f"✅ 전체 데이터가 {len(new_df)}건으로 교체되었습니다.")
                        st.rerun()

            except Exception as e:
                st.error(f"파일 읽기 오류: {e}")

        # CSV 템플릿 다운로드
        st.markdown("<br>", unsafe_allow_html=True)
        template = st.session_state.trades.head(2).copy()
        csv_buf = io.StringIO()
        template.to_csv(csv_buf, index=False)
        st.download_button(
            "📥 CSV 템플릿 다운로드",
            csv_buf.getvalue(),
            "trade_template.csv",
            "text/csv",
        )

    # ── 직접 입력 ──────────────────────────────────────
    with tab2:
        st.markdown("#### 신규 매매 직접 입력")

        with st.form("trade_entry", clear_on_submit=True):
            r1c1, r1c2, r1c3 = st.columns(3)
            with r1c1:
                t_date = st.date_input("거래일")
            with r1c2:
                t_code = st.text_input("종목코드", placeholder="005930")
            with r1c3:
                t_name = st.text_input("종목명", placeholder="삼성전자")

            r2c1, r2c2, r2c3 = st.columns(3)
            with r2c1:
                t_market = st.selectbox("시장", ["KOSPI", "KOSDAQ"])
            with r2c2:
                t_gap = st.number_input("갭비율 (%)", value=5.0, step=0.1, min_value=0.0)
            with r2c3:
                t_sector = st.text_input("섹터", placeholder="반도체")

            r3c1, r3c2, r3c3 = st.columns(3)
            with r3c1:
                t_entry = st.number_input("진입가", value=0, step=100, format="%d")
            with r3c2:
                t_target = st.number_input("목표가", value=0, step=100, format="%d")
            with r3c3:
                t_stop = st.number_input("손절가", value=0, step=100, format="%d")

            r4c1, r4c2, r4c3 = st.columns(3)
            with r4c1:
                t_result = st.selectbox("결과", ["승", "패", "진행"])
            with r4c2:
                t_detail = st.selectbox("상세", ["reached_20", "reached_80", "stopped", "in_progress"])
            with r4c3:
                t_days = st.number_input("소요일", value=0, step=1, min_value=0)

            r5c1, r5c2, r5c3 = st.columns(3)
            with r5c1:
                t_peak = st.number_input("최고수익 (%)", value=0.0, step=0.1)
            with r5c2:
                t_low = st.number_input("최저 (%)", value=0.0, step=0.1)
            with r5c3:
                t_vol = st.checkbox("볼륨 스파이크")

            t_ma = st.text_input("MA 패턴", placeholder="MA5>MA20>MA60>MA120")

            submitted = st.form_submit_button("💾 매매 추가", use_container_width=True)

            if submitted:
                if not t_code or not t_name:
                    st.error("종목코드와 종목명은 필수입니다.")
                else:
                    new_trade = pd.DataFrame([{
                        "date": pd.to_datetime(t_date),
                        "code": t_code,
                        "name": t_name,
                        "market": t_market,
                        "gap_rate": t_gap,
                        "target_price": t_target,
                        "stop_price": t_stop,
                        "entry_price": t_entry,
                        "result": t_result,
                        "result_detail": t_detail,
                        "days_to_target": t_days,
                        "peak_pct": t_peak,
                        "min_low_pct": t_low,
                        "ma_pattern": t_ma,
                        "volume_spike": t_vol,
                        "sector": t_sector,
                    }])
                    st.session_state.trades = pd.concat(
                        [st.session_state.trades, new_trade], ignore_index=True
                    )
                    st.success(f"✅ {t_name} ({t_code}) 매매가 추가되었습니다.")
                    st.rerun()

    # ── 포지션 관리 ────────────────────────────────────
    with tab3:
        st.markdown("#### 보유 포지션 관리")

        positions = st.session_state.positions

        if len(positions) > 0:
            st.dataframe(positions, use_container_width=True, hide_index=True)

            # 포지션 삭제
            del_name = st.selectbox("삭제할 포지션", positions["name"].tolist(), key="del_pos")
            if st.button("🗑️ 포지션 삭제", key="del_pos_btn"):
                st.session_state.positions = positions[positions["name"] != del_name].reset_index(drop=True)
                st.success(f"✅ {del_name} 포지션이 삭제되었습니다.")
                st.rerun()
        else:
            st.info("보유 포지션이 없습니다.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 포지션 추가")

        with st.form("add_position", clear_on_submit=True):
            pc1, pc2 = st.columns(2)
            with pc1:
                p_name = st.text_input("종목명", key="pos_name", placeholder="삼성전자")
                p_code = st.text_input("종목코드", key="pos_code", placeholder="005930")
            with pc2:
                p_weight = st.number_input("비중 (%)", value=10.0, step=1.0, min_value=0.0, max_value=100.0)
                p_pnl = st.number_input("손익 (%)", value=0.0, step=0.1)
            p_amount = st.number_input("투자 금액 (원)", value=0, step=100000, format="%d")

            pos_submit = st.form_submit_button("➕ 포지션 추가", use_container_width=True)
            if pos_submit:
                if not p_name:
                    st.error("종목명은 필수입니다.")
                else:
                    new_pos = pd.DataFrame([{
                        "name": p_name, "code": p_code,
                        "weight": p_weight, "pnl": p_pnl, "amount": p_amount,
                    }])
                    st.session_state.positions = pd.concat(
                        [st.session_state.positions, new_pos], ignore_index=True
                    )
                    st.success(f"✅ {p_name} 포지션이 추가되었습니다.")
                    st.rerun()

    # ── 데이터 요약 ────────────────────────────────────
    with tab4:
        st.markdown("#### 데이터 요약")
        trades = st.session_state.trades

        sc1, sc2, sc3, sc4 = st.columns(4)
        kpis = [
            (sc1, "총 거래 수", f"{len(trades)}건"),
            (sc2, "기간", f"{trades['date'].min().strftime('%Y-%m-%d')} ~ {trades['date'].max().strftime('%Y-%m-%d')}"),
            (sc3, "종목 수", f"{trades['code'].nunique()}개"),
            (sc4, "보유 포지션", f"{len(st.session_state.positions)}건"),
        ]
        for col, label, val in kpis:
            with col:
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-label">{label}</div>
                    <div class="kpi-value neutral">{val}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 시장별 분포
        st.markdown("##### 시장별 분포")
        market_dist = trades["market"].value_counts()
        for m, c in market_dist.items():
            pct = c / len(trades) * 100
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
                <span style="color:#7a8599; font-size:12px; min-width:70px;">{m}</span>
                <div style="flex:1; background:#1e2530; border-radius:4px; height:8px; overflow:hidden;">
                    <div style="background:{'#3b82f6' if m=='KOSPI' else '#a78bfa'}; width:{pct}%; height:100%; border-radius:4px;"></div>
                </div>
                <span style="color:#e2e8f0; font-size:12px;">{c}건 ({pct:.0f}%)</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 전체 데이터 다운로드
        csv_out = io.StringIO()
        trades.to_csv(csv_out, index=False)
        st.download_button(
            "📥 전체 데이터 CSV 다운로드",
            csv_out.getvalue(),
            "gap_rzone_trades.csv",
            "text/csv",
            use_container_width=True,
        )

        # 데이터 초기화
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 샘플 데이터로 초기화", key="reset_data"):
            from sample_data import (
                get_sample_trades, get_sample_equity_curve,
                get_sample_positions, get_sample_signals,
            )
            st.session_state.trades = get_sample_trades()
            st.session_state.equity_curve = get_sample_equity_curve()
            st.session_state.positions = get_sample_positions()
            st.session_state.signals = get_sample_signals()
            st.success("✅ 샘플 데이터로 초기화되었습니다.")
            st.rerun()
