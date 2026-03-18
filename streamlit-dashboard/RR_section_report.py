import pandas as pd
from pathlib import Path

# 1) 파일 경로 설정
BASE_DIR = Path(".")  # 필요하면 바꿔 쓰기
trades_path = BASE_DIR / "trades_formatted_v1.csv"
signals_path = BASE_DIR / "live_signals_20260316_check.csv"  # 날짜에 맞게 수정
output_path = BASE_DIR / "trades_enriched_v1.csv"

# 2) CSV 로드 (헤더 줄 상황에 맞게 header 옵션 조정)
trades = pd.read_csv(trades_path)          # 이미 헤더 정리돼 있으면 기본값
signals = pd.read_csv(signals_path)

# 3) 시그널 컬럼명 표준화 (필요 시 소문자 변환 등)
signals.columns = [c.strip() for c in signals.columns]

# 4) 조인 키 준비
# trades에 signal_date가 아직 없다고 가정하고, 일단 code 기준 최근 시그널 하나를 붙이는 예시
# (나중에 date_entry 생기면 market+code+date_entry == signal_date로 바꾸면 됨)

# 시그널에서 code별 최신 signal_date 한 건씩만 사용
signals["signal_date"] = pd.to_datetime(signals["signal_date"])
latest_signals = (
    signals.sort_values("signal_date")
           .groupby(["market", "code"], as_index=False)
           .tail(1)
)

# 5) 조인 실행 (left join)
merged = pd.merge(
    trades,
    latest_signals,
    on=["market", "code"],
    how="left",
    suffixes=("", "_sig"),
)

# 6) 컬럼 리네이밍 / 선택
rename_map = {
    "to_target_pct": "target_pct",
    "ma_arr": "ma_entry",
}
merged = merged.rename(columns=rename_map)

# 이후 대시보드에서 쓸 컬럼 예시:
# ['signal_date', 'gap_rate', 'target_price', 'stop_price',
#  'target_pct', 'rr_ratio', 'ma_entry',
#  'total_range', 'prev_range', 'high_pt', 'low_pt',
#  'vol_spike_hist', 'is_core']

# 7) 저장
merged.to_csv(output_path, index=False)
print(f"saved: {output_path}")
