import time
import pandas as pd
from datetime import datetime
from pykiwoom.kiwoom import Kiwoom

# ──────────────────────────────────────────
# 0. 키움 연결
# ──────────────────────────────────────────
kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

# ──────────────────────────────────────────
# 1. 코스피 + 코스닥 종목 코드 수집
# ──────────────────────────────────────────
kospi_codes  = [(c, "코스피")  for c in kiwoom.GetCodeListByMarket('0')  if c.strip()]
kosdaq_codes = [(c, "코스닥") for c in kiwoom.GetCodeListByMarket('10') if c.strip()]

all_codes = kospi_codes + kosdaq_codes   # (코드, 시장명) 튜플 리스트
print(f"코스피: {len(kospi_codes)}개 | 코스닥: {len(kosdaq_codes)}개 | 합계: {len(all_codes)}개")

# ──────────────────────────────────────────
# 2. 시가총액 + 종목명 조회 함수
# ──────────────────────────────────────────
def get_basic_info(code, market_label):
    raw_mc = ""
    try:
        df = kiwoom.block_request(
            "opt10001",
            종목코드=code,
            output="주식기본정보",
            next=0
        )
        if df is None or df.empty:
            print(f"빈 DF: {code}")
            return None

        name   = str(df['종목명'].iloc[0]).strip()
        raw_mc = str(df['시가총액'].iloc[0]).replace(',', '').replace('+', '').replace('-', '').strip()

        mc_100m = abs(int(raw_mc))       # 시가총액 (억 원)
        mc_krw  = mc_100m * 100_000_000  # 시가총액 (원)

        return {
            "code":            code,
            "name":            name,
            "market":          market_label,
            "market_cap_krw":  mc_krw,
            "market_cap_100m": mc_100m,
        }
    except Exception as e:
        print(f"예외: {code} ({market_label}) | {e} | raw_mc={raw_mc!r}")
        return None

# ──────────────────────────────────────────
# 3. 코스피 + 코스닥 전 종목 시총 스냅샷 수집
# ──────────────────────────────────────────
records    = []
start_time = time.time()

for i, (code, market_label) in enumerate(all_codes):
    if i % 100 == 0:
        elapsed = (time.time() - start_time) / 60
        print(f"▶ 수집 중... {i}/{len(all_codes)}개 | 경과 {elapsed:.1f}분")

    time.sleep(0.2)   # TR 제한 여유
    info = get_basic_info(code, market_label)
    if info:
        records.append(info)

print(f"\n✅ 수집 완료: {len(records)}개 종목")

# ──────────────────────────────────────────
# 4. CSV 저장
# ──────────────────────────────────────────
df_mc     = pd.DataFrame(records)
today_str = datetime.now().strftime("%Y%m%d")
fname     = f"marketcap_kospi_kosdaq_{today_str}.csv"

df_mc.to_csv(fname, index=False, encoding="cp949")

print(f"\n📁 저장 완료: {fname}")
print(df_mc.groupby("market")[["code"]].count().rename(columns={"code": "종목수"}))
print(df_mc.head())
