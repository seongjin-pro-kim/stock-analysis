"""시그널+매매기록 머지 스크립트
수동 실행: python trade_signal_merge.py
추후 배치/자동화 대응 가능하도록 경로만 교체하면 됩니다.
"""
from pathlib import Path
import pandas as pd

# ── 경로 설정 ──────────────────────────────────────────
trades_path  = Path(r"D:/auto_ht_projt/board/streamlit-dashboard/csv_etc/trades_formatted_v1.csv")
signals_path = Path(r"D:/auto_ht_projt/pycharm/live_signals/live_signals_YYYYMMDD.csv")  # 날짜만 교체
output_path  = Path(r"D:/auto_ht_projt/board/streamlit-dashboard/csv_etc/trades_enriched_v1.csv")

print("trades exists :", trades_path.exists())
print("signals exists:", signals_path.exists())

# ── 1. CSV 로드 (시그널은 한글+영문 2줄 헤더 구조) ─────
trades  = pd.read_csv(trades_path,  encoding="cp949")
signals = pd.read_csv(signals_path, encoding="cp949", header=1)

# ── 2. 컬럼 정리 ──────────────────────────────────────
signals.columns = [c.strip() for c in signals.columns]
signals["signal_date"] = pd.to_datetime(signals["signal_date"], format="%Y%m%d")

# 코드 타입 통일 (문자열)
trades["종목코드"] = trades["종목코드"].astype(str).str.replace("'", "").str.strip()
signals["code"]   = signals["code"].astype(str).str.replace(".0", "", regex=False).str.strip()

# ── 3. (market, code)별 최신 시그널 1건 선택 ───────────
latest_signals = (
    signals.sort_values("signal_date")
           .groupby(["market", "code"], as_index=False)
           .tail(1)
)

# ── 4. 매매기록과 조인 (시장+종목코드 기준) ────────────
merged = pd.merge(
    trades,
    latest_signals,
    left_on=["시장", "종목코드"],
    right_on=["market", "code"],
    how="left",
    suffixes=("", "_sig"),
)

# ── 5. 컬럼 이름 변경 ─────────────────────────────────
rename_map = {
    "to_target_pct": "target_pct",
    "ma_arr": "ma_entry",
}
merged = merged.rename(columns=rename_map)

# ── 6. 저장 ───────────────────────────────────────────
merged.to_csv(output_path, index=False, encoding="utf-8-sig")
print("saved:", output_path)
