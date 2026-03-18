# 과거 특정일 기준 신호 탐지 (테스트 / 디버그용) today str 날짜 기준으로 신호 종목 출력 (포워드 체크 없음)
import time
import numpy as np
import pandas as pd
from pykiwoom.kiwoom import Kiwoom

# ──────────────────────────────────────────
# 0. 키움 연결
# ──────────────────────────────────────────
kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

# ──────────────────────────────────────────
# 1. 시총 CSV에서 코드 + 500억 필터
# ──────────────────────────────────────────
mc = pd.read_csv(
    r"D:\auto_ht_projt\pycharm\marketcap_kospi_20260312.csv",
    encoding="cp949",
    dtype={"code": str}
)
mc["code"] = mc["code"].str.zfill(6)
mc = mc[mc["code"].str.match(r"^\d{6}$")]  # ← 추가: 숫자 6자리만

large_df       = mc[mc["market_cap_100m"] >= 500]
filtered_codes = large_df["code"].tolist()

print(f"CSV 내 종목 수: {len(mc)}개, 시총 500억↑: {len(filtered_codes)}개")

# ──────────────────────────────────────────
# 2. 백테스트 메인 루프
# ──────────────────────────────────────────
signals      = []
today_str    = "20260311"              # 기준일자
target_codes = filtered_codes   # 테스트용 100개, 전체는 filtered_codes

for i, code in enumerate(target_codes):
    if i % 10 == 0:
        print(f"진행 중: {i}/{len(target_codes)}번째")  # ★ 추가
    try:
        # 2-1) 일봉 1번만 조회 (연속 조회 없음)
        df = kiwoom.block_request(
            "opt10081",
            종목코드=code,
            기준일자=today_str,
            수정주가구분=1,
            output="주식일봉차트조회",
            next=0
        )
        time.sleep(0.35)  # 0.1 → 0.35 (안정적인 속도)
        print(f"{code} raw df:\n{df}")
        if df is None or df.empty:
            print(f"{code} → df 없음")  # ★
            continue

        df = df.sort_values("일자").reset_index(drop=True)

        # 2-2) 숫자형 변환
        for col in ["시가", "고가", "저가", "현재가", "거래량", "전일종가"]:
            df[col] = pd.to_numeric(
                df[col].astype(str)
                       .str.strip()
                       .str.replace(',', '', regex=False)
                       .str.replace('+', '', regex=False)
                       .str.replace('-', '', regex=False),
                errors="coerce"
            )

        # 2-3) NaN 제거 + 길이 체크
        df = df.dropna(subset=["시가", "현재가", "거래량"])
        df = df.reset_index(drop=True)

        if len(df) < 30:
            print(f"{code} → 데이터 부족: {len(df)}개")  # ★
            continue

        # 2-4) 전일 / 당일 기준행
        today = df.iloc[-1]
        prev = df.iloc[-2]

        gap_rate = (today["시가"] - prev["현재가"]) / prev["현재가"] * 100
        print(f"{code} | {today['일자']} | 갭:{round(gap_rate, 2)}%")

        # 이평선
        df["MA5"] = df["현재가"].rolling(5).mean()
        df["MA20"] = df["현재가"].rolling(20).mean()
        df["MA40"] = df["현재가"].rolling(40).mean()
        df["MA60"] = df["현재가"].rolling(60).mean()
        df["MA120"] = df["현재가"].rolling(120).mean()

        prev_bull = prev["현재가"] > prev["시가"]
        vol_ma20 = df["거래량"].tail(20).mean()
        vol_cond = today["거래량"] >= vol_ma20 * 2
        ma_cond = (
                df["MA5"].iloc[-1] > df["MA20"].iloc[-1] >
                df["MA40"].iloc[-1] > df["MA60"].iloc[-1] >
                df["MA120"].iloc[-1]
        )

        cond = prev_bull and (gap_rate >= 2.0) and vol_cond and ma_cond

        print(f"{code} | 갭:{round(gap_rate, 2)}% | 전일양봉:{prev_bull} | 거래량2배:{vol_cond}")

        if cond:
            signals.append((code, today["시가"], today["일자"], round(gap_rate, 2),
                            int(today["거래량"]), round(vol_ma20, 0)))

    except Exception as e:
        print(f"에러: {code} → {e}")
        continue

# ──────────────────────────────────────────
# 3. 결과 출력
# ──────────────────────────────────────────
print(f"\n총 매수 신호 수: {len(signals)}개")
for s in signals[:20]:
    code, price, date, gap_r, vol, vol20 = s
    print(f"{code} | {date} | 매수가:{price} | 갭:{gap_r}% | V:{vol} | V20:{vol20}")
