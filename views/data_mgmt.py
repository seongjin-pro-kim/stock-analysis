"""💾 데이터 관리 — 계좌별 CSV 업로드, 확장 필수컬럼, MA 셀렉터, 포지션 설명, NASDAQ/BTC"""
import streamlit as st
import pandas as pd
import io


# MA 패턴 셀렉터용 MA 옵션
MA_OPTIONS = ["MA5", "MA10", "MA20", "MA40", "MA60", "MA120"]


def render():
    st.markdown("### 💾 데이터 관리")

    tab1, tab2, tab3, tab4 = st.tabs(["📤 CSV 업로드", "✏️ 직접 입력", "📌 포지션 관리", "📊 데이터 요약"])

    # ── CSV 업로드 (파일명에서 계좌번호 자동 감지) ─────────
    with tab1:
        st.markdown("#### CSV 파일 업로드")
        st.markdown("""
        <div style="background:#111820; border:1px solid #1e2530; border-radius:8px; padding:12px; font-size:12px; color:#7a8599; margin-bottom:12px;">
            <strong style="color:#e2e8f0;">업로드 방식:</strong> 파일명에 4자리 계좌번호를 포함하면 자동으로 계좌를 구분합니다.<br>
            예) <code style="color:#14b8a6;">trades_1234.csv</code>, <code style="color:#14b8a6;">1234_매매기록.csv</code><br>
            파일명에 계좌번호가 없으면, 파일 내 <code>account_id</code> 컬럼을 참조합니다.
        </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#111820; border:1px solid #1e2530; border-radius:8px; padding:12px; font-size:11px; color:#7a8599; margin-bottom:16px;">
            <strong style="color:#e2e8f0;">필수 컬럼:</strong><br>
            <code>date, code, name, market, gap_rate, entry_price, target_price, stop_price,
            target_rate, stop_rate, rr_ratio, expected_value,
            result, result_detail, days_to_target, peak_pct, min_low_pct,
            ma_pattern, sell_ma, volume_spike, sector, grade, is_core,
            signal_date, account_id</code><br><br>
            <strong style="color:#e2e8f0;">선택 컬럼:</strong>
            <code>option_expiry, event_note</code>
        </div>""", unsafe_allow_html=True)

        uploaded = st.file_uploader("CSV 파일 선택", type=["csv"], key="csv_upload",
                                     accept_multiple_files=True)

        if uploaded:
            for f in uploaded:
                try:
                    new_df = pd.read_csv(f)

                    # 파일명에서 계좌번호 추출 (4자리 숫자)
                    import re
                    match = re.search(r'(\d{4})', f.name)
                    if match and "account_id" not in new_df.columns:
                        new_df["account_id"] = match.group(1)

                    acc_id = new_df["account_id"].iloc[0] if "account_id" in new_df.columns else "미지정"

                    st.markdown(f"""
                    <div style='color:#14b8a6; font-size:13px; margin-bottom:4px;'>
                        ✅ <strong>{f.name}</strong> — {len(new_df)}건 로드 (계좌: {acc_id})
                    </div>""", unsafe_allow_html=True)

                    st.dataframe(new_df.head(5), use_container_width=True, hide_index=True)

                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button(f"기존 데이터에 추가 ({f.name})", key=f"append_{f.name}"):
                            new_df["date"] = pd.to_datetime(new_df["date"])
                            if "signal_date" in new_df.columns:
                                new_df["signal_date"] = pd.to_datetime(new_df["signal_date"], errors="coerce")
                            st.session_state.trades = pd.concat(
                                [st.session_state.trades, new_df], ignore_index=True
                            ).drop_duplicates(subset=["date", "code"], keep="last")
                            st.success(f"✅ {len(new_df)}건이 추가되었습니다.")
                            st.rerun()

                    with col_b:
                        if st.button(f"기존 데이터 교체 ({f.name})", key=f"replace_{f.name}"):
                            new_df["date"] = pd.to_datetime(new_df["date"])
                            if "signal_date" in new_df.columns:
                                new_df["signal_date"] = pd.to_datetime(new_df["signal_date"], errors="coerce")
                            st.session_state.trades = new_df
                            st.success(f"✅ 전체 데이터가 {len(new_df)}건으로 교체되었습니다.")
                            st.rerun()

                except Exception as e:
                    st.error(f"파일 읽기 오류 ({f.name}): {e}")

        # CSV 템플릿 다운로드
        st.markdown("<br>", unsafe_allow_html=True)
        template_cols = [
            "date", "code", "name", "market", "gap_rate",
            "entry_price", "target_price", "stop_price",
            "target_rate", "stop_rate", "rr_ratio", "expected_value",
            "result", "result_detail", "days_to_target",
            "peak_pct", "min_low_pct",
            "ma_pattern", "sell_ma", "volume_spike", "sector",
            "grade", "is_core", "signal_date", "account_id",
            "option_expiry", "event_note",
        ]
        template_data = {col: [""] for col in template_cols}
        template_data["date"] = ["2026-03-19"]
        template_data["code"] = ["005930"]
        template_data["name"] = ["삼성전자"]
        template_data["market"] = ["KOSPI"]
        template_data["gap_rate"] = [5.0]
        template_data["entry_price"] = [68200]
        template_data["target_price"] = [72400]
        template_data["stop_price"] = [64800]
        template_data["target_rate"] = [6.2]
        template_data["stop_rate"] = [-5.0]
        template_data["rr_ratio"] = [3.21]
        template_data["expected_value"] = [15.9]
        template_data["result"] = ["승"]
        template_data["result_detail"] = ["reached_20"]
        template_data["days_to_target"] = [5]
        template_data["peak_pct"] = [24.3]
        template_data["min_low_pct"] = [-2.1]
        template_data["ma_pattern"] = ["MA5>MA20>MA60>MA120"]
        template_data["sell_ma"] = ["MA5>MA20>MA60>MA120"]
        template_data["volume_spike"] = [True]
        template_data["sector"] = ["반도체"]
        template_data["grade"] = ["A"]
        template_data["is_core"] = [True]
        template_data["signal_date"] = ["2026-03-18"]
        template_data["account_id"] = ["1234"]
        template_data["option_expiry"] = [""]
        template_data["event_note"] = [""]

        template_df = pd.DataFrame(template_data)
        csv_buf = io.StringIO()
        template_df.to_csv(csv_buf, index=False, encoding="utf-8-sig")
        st.download_button(
            "📥 CSV 템플릿 다운로드",
            csv_buf.getvalue(),
            "trade_template_v2.csv",
            "text/csv",
        )

    # ── 직접 입력 ──────────────────────────────────────
    with tab2:
        st.markdown("#### 신규 매매 직접 입력")

        with st.form("trade_entry", clear_on_submit=True):
            r1c1, r1c2, r1c3, r1c4 = st.columns(4)
            with r1c1:
                t_date = st.date_input("거래일")
            with r1c2:
                t_code = st.text_input("종목코드", placeholder="005930")
            with r1c3:
                t_name = st.text_input("종목명", placeholder="삼성전자")
            with r1c4:
                t_market = st.selectbox("시장", ["KOSPI", "KOSDAQ"])

            r2c1, r2c2, r2c3, r2c4 = st.columns(4)
            with r2c1:
                t_gap = st.number_input("갭비율 (%)", value=5.0, step=0.1, min_value=0.0)
            with r2c2:
                t_sector = st.text_input("섹터", placeholder="반도체")
            with r2c3:
                t_grade = st.selectbox("등급", ["A", "B", "C"])
            with r2c4:
                t_core = st.checkbox("코어 종목")

            r3c1, r3c2, r3c3 = st.columns(3)
            with r3c1:
                t_entry = st.number_input("진입가", value=0, step=100, format="%d")
            with r3c2:
                t_target = st.number_input("목표가", value=0, step=100, format="%d")
            with r3c3:
                t_stop = st.number_input("손절가", value=0, step=100, format="%d")

            # 자동 계산
            if t_entry > 0 and t_target > 0 and t_stop > 0:
                t_target_rate = round((t_target - t_entry) / t_entry * 100, 1)
                t_stop_rate = round((t_stop - t_entry) / t_entry * 100, 1)
                t_rr = round(abs(t_target_rate / t_stop_rate), 2) if t_stop_rate != 0 else 0
                t_ev = round(t_target_rate * 0.79 + t_stop_rate * 0.21, 1) if t_rr > 0 else 0
                st.markdown(f"""
                <div style="background:#111820; border:1px solid #1e2530; border-radius:8px; padding:8px 12px; font-size:12px; color:#7a8599; margin:8px 0;">
                    자동계산: 목표율 <span style="color:#14b8a6;">{t_target_rate}%</span> ·
                    손절율 <span style="color:#ef4444;">{t_stop_rate}%</span> ·
                    손익비 <span style="color:#e2e8f0;">{t_rr}</span> ·
                    기대값 <span style="color:#e2e8f0;">{t_ev}</span>
                </div>""", unsafe_allow_html=True)
            else:
                t_target_rate = t_stop_rate = t_rr = t_ev = 0

            r4c1, r4c2, r4c3, r4c4 = st.columns(4)
            with r4c1:
                t_result = st.selectbox("결과", ["잉", "승", "패"])
            with r4c2:
                t_detail = st.selectbox("상세", ["in_progress", "reached_20", "reached_80", "stopped"])
            with r4c3:
                t_days = st.number_input("소요일", value=0, step=1, min_value=0)
            with r4c4:
                t_account = st.text_input("계좌번호 (4자리)", placeholder="1234", max_chars=4)

            r5c1, r5c2, r5c3 = st.columns(3)
            with r5c1:
                t_peak = st.number_input("최고수익 (%)", value=0.0, step=0.1)
            with r5c2:
                t_low = st.number_input("최저 (%)", value=0.0, step=0.1)
            with r5c3:
                t_vol = st.checkbox("볼륨 스파이크")

            # MA 패턴 순차 셀렉터
            st.markdown("**MA 패턴 (순서대로 선택)**")
            ma_cols = st.columns(6)
            ma_selections = []
            for i, ma_col in enumerate(ma_cols):
                with ma_col:
                    sel = st.selectbox(
                        f"MA {i+1}",
                        ["선택안함"] + MA_OPTIONS,
                        key=f"ma_sel_{i}",
                        label_visibility="collapsed",
                    )
                    if sel != "선택안함":
                        ma_selections.append(sel)

            t_ma = ">".join(ma_selections) if ma_selections else ""
            if t_ma:
                st.markdown(f"<div style='color:#14b8a6; font-size:12px;'>패턴: {t_ma}</div>",
                            unsafe_allow_html=True)

            t_signal_date = st.date_input("신호일", key="signal_date_input")

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
                        "entry_price": t_entry,
                        "target_price": t_target,
                        "stop_price": t_stop,
                        "target_rate": t_target_rate,
                        "stop_rate": t_stop_rate,
                        "rr_ratio": t_rr,
                        "expected_value": t_ev,
                        "result": t_result,
                        "result_detail": t_detail,
                        "days_to_target": t_days,
                        "peak_pct": t_peak,
                        "min_low_pct": t_low,
                        "ma_pattern": t_ma,
                        "sell_ma": "",
                        "volume_spike": t_vol,
                        "sector": t_sector,
                        "grade": t_grade,
                        "is_core": t_core,
                        "signal_date": pd.to_datetime(t_signal_date),
                        "account_id": t_account or "0000",
                    }])
                    st.session_state.trades = pd.concat(
                        [st.session_state.trades, new_trade], ignore_index=True
                    )
                    st.success(f"✅ {t_name} ({t_code}) 매매가 추가되었습니다.")
                    st.rerun()

    # ── 포지션 관리 (설명 추가) ────────────────────────────
    with tab3:
        st.markdown("#### 보유 포지션 관리")
        st.markdown("""
        <div style="background:#111820; border:1px solid #1e2530; border-radius:8px; padding:12px; font-size:12px; color:#7a8599; margin-bottom:12px;">
            <strong style="color:#e2e8f0;">포지션 관리 기능 안내</strong><br>
            • <strong>포지션 추가</strong>: 새로 매수한 종목의 비중, 손익, 투자금액을 등록합니다.<br>
            • <strong>포지션 삭제</strong>: 매도 완료된 종목을 보유 목록에서 제거합니다.<br>
            • 이 데이터는 <em>메인 대시보드</em>의 보유 포지션 차트와 <em>리스크 관리</em>의 비중 분석에 반영됩니다.
        </div>""", unsafe_allow_html=True)

        positions = st.session_state.positions

        if len(positions) > 0:
            st.dataframe(positions, use_container_width=True, hide_index=True)

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
            pc1, pc2, pc3 = st.columns(3)
            with pc1:
                p_name = st.text_input("종목명", key="pos_name", placeholder="삼성전자")
                p_code = st.text_input("종목코드", key="pos_code", placeholder="005930")
            with pc2:
                p_weight = st.number_input("비중 (%)", value=10.0, step=1.0, min_value=0.0, max_value=100.0)
                p_pnl = st.number_input("손익 (%)", value=0.0, step=0.1)
            with pc3:
                p_amount = st.number_input("투자 금액 (원)", value=0, step=100000, format="%d")
                p_account = st.text_input("계좌번호", placeholder="1234", max_chars=4)

            pc4, pc5 = st.columns(2)
            with pc4:
                p_expiry = st.date_input("옵션 만기일 (선택)", key="pos_expiry", value=None)
            with pc5:
                p_event = st.text_input("주요 이벤트 (선택)", placeholder="실적발표 04/28")

            pos_submit = st.form_submit_button("➕ 포지션 추가", use_container_width=True)
            if pos_submit:
                if not p_name:
                    st.error("종목명은 필수입니다.")
                else:
                    new_pos = pd.DataFrame([{
                        "name": p_name, "code": p_code,
                        "weight": p_weight, "pnl": p_pnl, "amount": p_amount,
                        "account_id": p_account or "0000",
                        "option_expiry": str(p_expiry) if p_expiry else "",
                        "event_note": p_event or "",
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
            (sc2, "기간", f"{trades['date'].min().strftime('%y-%m-%d')} ~ {trades['date'].max().strftime('%y-%m-%d')}"),
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

        # 시장별 분포 (NASDAQ/BTC 포함)
        st.markdown("##### 시장별 분포")
        all_markets = ["KOSPI", "KOSDAQ", "NASDAQ", "BTC"]
        market_colors = {"KOSPI": "#3b82f6", "KOSDAQ": "#a78bfa", "NASDAQ": "#14b8a6", "BTC": "#eab308"}
        market_dist = trades["market"].value_counts()

        for m in all_markets:
            c = market_dist.get(m, 0)
            pct = (c / len(trades) * 100) if len(trades) > 0 else 0
            clr = market_colors.get(m, "#7a8599")
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
                <span style="color:#7a8599; font-size:12px; min-width:70px;">{m}</span>
                <div style="flex:1; background:#1e2530; border-radius:4px; height:8px; overflow:hidden;">
                    <div style="background:{clr}; width:{pct}%; height:100%; border-radius:4px;"></div>
                </div>
                <span style="color:#e2e8f0; font-size:12px;">{c}건 ({pct:.0f}%)</span>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 계좌별 분포
        if "account_id" in trades.columns:
            st.markdown("##### 계좌별 분포")
            acc_dist = trades["account_id"].value_counts()
            for acc, cnt in acc_dist.items():
                pct = cnt / len(trades) * 100
                st.markdown(f"""
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
                    <span style="color:#7a8599; font-size:12px; min-width:70px;">계좌 {acc}</span>
                    <div style="flex:1; background:#1e2530; border-radius:4px; height:8px; overflow:hidden;">
                        <div style="background:#14b8a6; width:{pct}%; height:100%; border-radius:4px;"></div>
                    </div>
                    <span style="color:#e2e8f0; font-size:12px;">{cnt}건 ({pct:.0f}%)</span>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 전체 데이터 다운로드
        csv_out = io.StringIO()
        trades.to_csv(csv_out, index=False, encoding="utf-8-sig")
        st.download_button(
            "📥 전체 데이터 CSV 다운로드",
            csv_out.getvalue(),
            "gap_rzone_trades_v2.csv",
            "text/csv",
            use_container_width=True,
        )

        # 데이터 초기화
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 샘플 데이터로 초기화", key="reset_data"):
            from sample_data import (
                get_sample_trades, get_sample_equity_curve,
                get_sample_positions, get_sample_signals,
                get_sample_signal_archive,
            )
            st.session_state.trades = get_sample_trades()
            st.session_state.equity_curve = get_sample_equity_curve()
            st.session_state.positions = get_sample_positions()
            st.session_state.signals = get_sample_signals()
            st.session_state.signal_archive = get_sample_signal_archive()
            st.success("✅ 샘플 데이터로 초기화되었습니다.")
            st.rerun()
