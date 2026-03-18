import time
import numpy as np
import pandas as pd
from pykiwoom.kiwoom import Kiwoom

# ──────────────────────────────────────────
# 0. 키움 연결
# ──────────────────────────────────────────
kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

CODE = "200880"          # 서연이화
BASE_DATE = "20260228"   # opt10081 단독 테스트와 동일 기준일

# ──────────────────────────────────────────
# 1. opt10081로 일봉 데이터 직접 받기
# ──────────────────────────────────────────
print("요청 시작")

raw_df = kiwoom.block_request(
    "opt10081",
    종목코드=CODE,
    기준일자=BASE_DATE,
    수정주가구분=1,
    output="주식일봉차트조회",
    next=0
)

print("원시 DF 행 개수:", 0 if raw_df is None else len(raw_df))

if raw_df is None or len(raw_df) == 0:
    print("opt10081에서 일봉 데이터를 못 받았습니다.")
    raise SystemExit

# ──────────────────────────────────────────
# 2. 컬럼 정리 및 정렬
# ──────────────────────────────────────────
df = raw_df[['일자','현재가','시가','고가','저가','거래량']].copy()
df.columns = ['date','close','open','high','low','volume']
for col in ['close','open','high','low','volume']:
    df[col] = (
        df[col]
        .astype(str)
        .str.replace(',', '', regex=False)
        .str.replace('+', '', regex=False)
        .str.replace('-', '', regex=False)
    )
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int).abs()
df = df.sort_values('date').reset_index(drop=True)

print(f"정리된 일봉 개수: {len(df)}")
print("\n=== 최근 25일 OHL C ===")
print(df.tail(25)[['date','open','high','low','close']])

print("\n=== 2026-02-10 opt10081 데이터 ===")
print(df[df['date'] == '20260210'][['date','open','high','low','close']])

# ──────────────────────────────────────────
# 3. 조건별 상태 출력 (c1>o1, c0>o0, c1<o0)
# ──────────────────────────────────────────
pattern_cnt = 0

print("\n=== 서연이화 조건 체크 (전체 구간) ===")

for idx in range(1, len(df)):
    b1, b0 = idx-1, idx

    o1,c1,h1,l1,v1 = df.loc[b1, ['open','close','high','low','volume']]
    o0,c0,h0,l0,v0 = df.loc[b0, ['open','close','high','low','volume']]

    cond_b1_bull    = (c1 > o1)      # 1봉전 양봉
    cond_b0_bull    = (c0 > o0)      # 0봉 양봉
    cond_gap_c1_o0  = (c1 < o0)      # 전일 종가 < 오늘 시가

    date0 = df.loc[b0, 'date']

    # 2월 구간만 보고 싶으면 아래 주석 해제
    if date0 < "20260201" or date0 > "20260229":
         continue

    print(date0,
          "| b1 O/C:", o1, c1,
          "b0 O/C:", o0, c0,
          "| cond_b1_bull:", cond_b1_bull,
          "cond_b0_bull:", cond_b0_bull,
          "cond_gap(c1<o0):", cond_gap_c1_o0)

    if cond_b1_bull and cond_b0_bull and cond_gap_c1_o0:
        pattern_cnt += 1
        print("  → 패턴 통과!")

print("\n=== 서연이화 조건 체크 종료 ===")
print("  조건 통과 패턴 수:", pattern_cnt)
