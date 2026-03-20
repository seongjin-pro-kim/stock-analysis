"""💾 데이터 관리 — 계좌별 CSV 업로드, 직접입력, 포지션 관리, 데이터 요약"""

import io
import os
import re
import streamlit as st
import pandas as pd

from utils import init_state, df_state

MA_OPTIONS = ["MA5", "MA10", "MA20", "MA40", "MA60", "MA120"]

REQUIRED_TRADES_COLS = [
    "date", "code", "name", "market", "gap_rate", "entry_price", "target_price", "stop_price",
    "target_rate", "stop_rate", "rr_ratio", "expected_value", "result", "result_detail",
    "days_to_target", "peak_pct", "min_low_pct", "ma_pattern", "sell_ma", "volume_spike",
    "sector", "grade", "is_core", "signal_date", "account_id", "option_expiry", "event_note",
]

def _ensure_cols(df, cols):
    for c in cols:
        if c not in df.columns:
            df[c] = pd.NA
    return df

def _guess_account_id(filename):
    m = re.search(r"(\d{2,6})", filename or "")
    return m.group(1) if m else ""

def _normalize_trades(df, account_id=""):
    if df is None or df.empty:
        return pd.DataFrame(columns=REQUIRED_TRADES_COLS)

    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    df = _ensure_cols(df, REQUIRED_TRADES_COLS)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    if "signal_date" in df.columns:
        df["signal_date"] = pd.to_datetime(df["signal_date"], errors="coerce")
    if "option_expiry" in df.columns:
        df["option_expiry"] = pd.to_datetime(df["option_expiry"], errors="coerce")

    if account_id:
        df["account_id"] = df["account_id"].fillna(account_id)
    if "account_id" not in df.columns:
        df["account_id"] = account_id

    for c in ["gap_rate", "entry_price", "target_price", "stop_price", "target_rate", "stop_rate", "rr_ratio", "expected_value", "peak_pct", "min_low_pct", "days_to_target"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    for c in ["is_core", "volume_spike"]:
        if c in df.columns:
            df[c] = df[c].astype("boolean")

    return df

def _append_trades(new_df):
    cur = df_state("trades")
    if cur.empty:
        st.session_state.trades = new_df.copy()
    else:
        merged = pd.concat([cur, new_df], ignore_index=True, sort=False)
        if "date" in merged.columns:
            merged["date"] = pd.to_datetime(merged["date"], errors="coerce")
        st.session_state.trades = merged

def _empty_positions():
    return pd.DataFrame(columns=["account_id", "symbol", "name", "qty", "avg_price", "market", "note"])

def render():
    init_state()
    st.markdown("### ▸ 데이터 관리")

    tabs = st.tabs(["📤 CSV 업로드", "✏️ 직접 입력", "📌 포지션 관리", "📊 데이터 요약"])

    with tabs[0]:
        st.markdown("#### CSV 파일 업로드")
        st.markdown(
            """
            - 파일명에서 계좌번호를 자동 추출합니다.
            - 예: `trades_1234.csv`, `1234_매매기록.csv`
            - 필요 컬럼 예시: `date, code, name, market, gap_rate, entry_price, target_price, stop_price, target_rate, stop_rate, rr_ratio, expected_value, result, result_detail, days_to_target, peak_pct, min_low_pct, ma_pattern, sell_ma, volume_spike, sector, grade, is_core, signal_date, account_id, option_expiry, event_note`
            """,
            unsafe_allow_html=False,
        )
        up = st.file_uploader("CSV 선택", type=["csv"])
        if up is not None:
            filename = getattr(up, "name", "")
            account_id = _guess_account_id(filename)
            try:
                raw = pd.read_csv(up, encoding="utf-8-sig")
            except Exception:
                up.seek(0)
                raw = pd.read_csv(up, encoding="cp949")

            raw = _normalize_trades(raw, account_id=account_id)
            st.success(f"업로드 완료: {filename}")
            st.write(f"감지된 계좌번호: {account_id or '-'}")
            st.dataframe(raw.head(20), use_container_width=True, hide_index=True)

            if st.button("업로드 데이터를 trades에 반영"):
                _append_trades(raw)
                st.success("반영 완료")
                st.rerun()

    with tabs[1]:
        st.markdown("#### 직접 입력")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            date = st.date_input("날짜")
            account_id = st.text_input("계좌번호")
        with c2:
            market = st.selectbox("시장", ["KOSPI", "KOSDAQ", "NASDAQ", "BTC"])
            result = st.selectbox("결과", ["승", "패", "잉"])
        with c3:
            code = st.text_input("코드")
            name = st.text_input("종목명")
        with c4:
            sector = st.text_input("섹터")
            grade = st.selectbox("등급", ["A", "B", "C"])

        c5, c6, c7, c8 = st.columns(4)
        with c5:
            gap_rate = st.number_input("갭%", value=0.0, step=0.1)
            entry_price = st.number_input("진입가", value=0.0, step=100.0)
        with c6:
            target_rate = st.number_input("목표율%", value=0.0, step=0.1)
            target_price = st.number_input("목표가", value=0.0, step=100.0)
        with c7:
            stop_rate = st.number_input("손절율%", value=0.0, step=0.1)
            stop_price = st.number_input("손절가", value=0.0, step=100.0)
        with c8:
            rr_ratio = st.number_input("RR", value=0.0, step=0.1)
            expected_value = st.number_input("기대값", value=0.0, step=0.1)

        ma_pattern = st.text_input("MA 패턴", "MA5>MA20>MA60>MA120")
        sell_ma = st.text_input("MA(매도)", "")
        volume_spike = st.checkbox("거래량 스파이크")
        is_core = st.checkbox("코어")
        result_detail = st.text_input("결과 상세", "")
        days_to_target = st.number_input("소요일", value=0, step=1)
        peak_pct = st.number_input("최고%", value=0.0, step=0.1)
        min_low_pct = st.number_input("최저%", value=0.0, step=0.1)
        signal_date = st.date_input("시그널 날짜")
        option_expiry = st.date_input("옵션만기")
        event_note = st.text_input("이벤트 메모", "")

        if st.button("입력값을 trades에 추가"):
            row = pd.DataFrame([{
                "date": pd.to_datetime(date),
                "account_id": account_id,
                "market": market,
                "code": code,
                "name": name,
                "sector": sector,
                "grade": grade,
                "gap_rate": gap_rate,
                "entry_price": entry_price,
                "target_rate": target_rate,
                "target_price": target_price,
                "stop_rate": stop_rate,
                "stop_price": stop_price,
                "rr_ratio": rr_ratio,
                "expected_value": expected_value,
                "result": result,
                "result_detail": result_detail,
                "days_to_target": days_to_target,
                "peak_pct": peak_pct,
                "min_low_pct": min_low_pct,
                "ma_pattern": ma_pattern,
                "sell_ma": sell_ma,
                "volume_spike": volume_spike,
                "is_core": is_core,
                "signal_date": pd.to_datetime(signal_date),
                "option_expiry": pd.to_datetime(option_expiry),
                "event_note": event_note,
            }])
            row = _normalize_trades(row, account_id=account_id)
            _append_trades(row)
            st.success("추가 완료")
            st.rerun()

    with tabs[2]:
        st.markdown("#### 포지션 관리")
        pos = df_state("positions")
        if pos.empty:
            pos = _empty_positions()
        if "account_id" not in pos.columns:
            pos["account_id"] = ""
        if "market" not in pos.columns:
            pos["market"] = ""
        if "note" not in pos.columns:
            pos["note"] = ""

        edited = st.data_editor(
            pos,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            column_config={
                "market": st.column_config.SelectboxColumn("시장", options=["KOSPI", "KOSDAQ", "NASDAQ", "BTC"], required=False),
                "qty": st.column_config.NumberColumn("수량", min_value=0, step=1),
                "avg_price": st.column_config.NumberColumn("평단가", min_value=0.0, step=100.0),
            },
        )
        if st.button("포지션 저장"):
            st.session_state.positions = edited.copy()
            st.success("저장 완료")
            st.rerun()

    with tabs[3]:
        st.markdown("#### 데이터 요약")
        trades = df_state("trades")
        signals = df_state("signals")
        archive = df_state("signal_archive")
        positions = df_state("positions")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("trades", f"{len(trades)}")
        c2.metric("signals", f"{len(signals)}")
        c3.metric("archive", f"{len(archive)}")
        c4.metric("positions", f"{len(positions)}")

        st.markdown("##### trades 컬럼")
        st.code(", ".join(trades.columns.tolist()) if not trades.empty else "비어있음")
        st.markdown("##### signals 컬럼")
        st.code(", ".join(signals.columns.tolist()) if not signals.empty else "비어있음")
        st.markdown("##### archive 컬럼")
        st.code(", ".join(archive.columns.tolist()) if not archive.empty else "비어있음")
