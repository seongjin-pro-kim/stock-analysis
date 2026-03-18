import pandas as pd
from pathlib import Path

# ==== 0. 설정 ====
KIWOOM_CSV_PATH = r"D:\auto_ht_projt\board\streamlit-dashboard\kw_deal_data\260318_deal_data.csv"  # 원본 거래내역
OUT_CSV_PATH    = r"D:\auto_ht_projt\board\streamlit-dashboard\csv_etc\trades_formatted_v1.csv"

ACCOUNT_NUMBER  = "12345678"  # 실제 네 계좌번호로 교체
ACCOUNT_ID      = ACCOUNT_NUMBER[-4:]  # 뒤 4자리

# ==== 1. 키움 거래내역 불러오기 ====
df_raw = pd.read_csv(KIWOOM_CSV_PATH, encoding="cp949")  # 키움은 보통 cp949

print("원본 컬럼:", list(df_raw.columns))

# 컬럼 이름이 다를 경우 여기서 rename 해줘야 함
# 예시는 네가 준 구조를 그대로 쓴 것
df = df_raw.rename(columns={
    "일자": "date_exit_raw",
    "종목코드": "code",
    "종목명": "name",
    "수량": "qty",
    "매입가": "entry_price_raw",
    "매도체결가": "exit_price_raw",
    "실현손익": "pnl_raw",
    "수익률": "ret_raw",
})

# ==== 2. 기본 가공 ====

# 계좌 ID
df["account_id"] = ACCOUNT_ID

# market: 종목코드로 코스피/코스닥 구분 (간단 버전)
# - 실제로는 별도 종목마스터를 참조하는 게 정확함
def guess_market(code: str) -> str:
    try:
        c = int(code)
    except ValueError:
        return "UNKNOWN"
    # 예시 룰: 0~19999 코스피, 20000~ 코스닥 이런 식 (나중에 정확한 룰/맵으로 교체)
    return "코스피" if c < 200000 else "코스닥"

df["market"] = df["code"].astype(str).apply(guess_market)

# 날짜: date_exit (YY-MM-DD로 가공)
# 키움 '일자'가 '20260318' 같은 포맷이라고 가정
df["date_exit"] = pd.to_datetime(df["date_exit_raw"].astype(str)).dt.strftime("%y-%m-%d")

# 아직 date_entry는 없음 → 빈 값으로 두고, 나중에 포지션/시그널 로그와 합칠 때 채움
df["date_entry"] = ""

# 콤마/공백 제거용 헬퍼
def to_float(x):
    if pd.isna(x):
        return 0.0
    return float(str(x).replace(",", "").strip())

# entry_price, exit_price 가공 부분을 이렇게 교체
df["entry_price"] = df["entry_price_raw"].apply(to_float)
df["exit_price"]  = df["exit_price_raw"].apply(to_float)

# 수익률도 콤마 제거 후 %→소수로
df["ret"] = df["ret_raw"].apply(to_float) / 100.0

# 결과 승/패/잉 (지금은 완료된 거래만 있다고 보고 승/패만)
def result_from_ret(r):
    if r > 0:
        return "승"
    elif r < 0:
        return "패"
    else:
        return "잉"

df["result"] = df["ret"].apply(result_from_ret)

# days_held, max_runup_pct, max_dd_pct, expectancy 등은 아직 없음 → 기본값/빈 값
df["days_held"]     = 0
df["max_runup_pct"] = 0.0
df["max_dd_pct"]    = 0.0
df["expectancy"]    = ""

# 아직 없는 컬럼들(시그널/전략 쪽에서 나중에 채울 것들)
df["grade"]        = ""
df["gap_rate"]     = 0.0
df["target_pct"]   = 0.0
df["target_price"] = 0.0
df["stop_pct"]     = 0.0
df["stop_price"]   = 0.0
df["rr_ratio"]     = 0.0
df["ret_R"]        = ""
df["ma_entry"]     = ""
df["ma_exit"]      = ""
df["sector"]       = ""

# ==== 3. 최종 컬럼 순서 맞추기 ====

cols_final = [
    "account_id",
    "market",
    "date_entry",
    "date_exit",
    "code",
    "name",
    "grade",
    "gap_rate",
    "entry_price",
    "target_pct",
    "target_price",
    "stop_pct",
    "stop_price",
    "rr_ratio",
    "ret",
    "ret_R",
    "expectancy",
    "max_runup_pct",
    "max_dd_pct",
    "days_held",
    "result",
    "ma_entry",
    "ma_exit",
    "sector",
]

rdf = df[cols_final].copy()

# ==== 4. 저장 (한글 헤더 1행 추가) ====
from pathlib import Path

Path(OUT_CSV_PATH).parent.mkdir(parents=True, exist_ok=True)

korean_header = {
    "account_id":    "계좌ID",
    "market":        "시장",
    "date_entry":    "진입일",
    "date_exit":     "청산일",
    "code":          "종목코드",
    "name":          "종목명",
    "grade":         "그레이드",
    "gap_rate":      "갭비율",
    "entry_price":   "진입가",
    "target_pct":    "목표율",
    "target_price":  "목표가",
    "stop_pct":      "손절율",
    "stop_price":    "손절가",
    "rr_ratio":      "손익비",
    "ret":           "수익률",
    "ret_R":         "R수익",
    "expectancy":    "기대값",
    "max_runup_pct": "최고수익률",
    "max_dd_pct":    "최대낙폭률",
    "days_held":     "소요일",
    "result":        "결과",
    "ma_entry":      "MA(매수)",
    "ma_exit":       "MA(매도)",
    "sector":        "섹터",
}

# 1행: 한글 헤더, 2행부터: 실제 데이터
with open(OUT_CSV_PATH, "w", encoding="cp949", newline="") as f:
    # 한글 헤더 1행
    f.write(",".join(korean_header[c] for c in cols_final) + "\n")
    # 영문 헤더 + 데이터
    rdf.to_csv(f, index=False)


print(f"완료: {OUT_CSV_PATH}")
