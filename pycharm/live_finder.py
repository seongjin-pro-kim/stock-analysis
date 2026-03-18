# ─────────────────────────────────────────────────────────
# 실전 신호 스캐너 | 오늘 기준 -20 거래일 신호 탐지
# ─────────────────────────────────────────────────────────
import time
import pandas as pd
import numpy as np
from datetime import datetime
from pykiwoom.kiwoom import Kiwoom

kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

# ── 설정 ─────────────────────────────────────────────────
TODAY_STR  = datetime.now().strftime("%Y%m%d")
SCAN_DAYS  = 5         # 최근 N 거래일 스캔
MIN_CAP    = 500         # 시총 최소 (억)
SLEEP_SEC  = 0.35
CSV_PATH_MC   = r"D:\auto_ht_projt\pycharm\marketcap_kospi_kosdaq_20260316.csv"
CSV_PATH_OHLC = r"D:\auto_ht_projt\pycharm\ohlcv_master_23_26.csv"  # ← 600봉 마스터
ALLOW_MA = {
    "MA20>MA40>MA60>MA5>MA120",
    "MA60>MA120>MA40>MA20>MA5",
    "MA5>MA40>MA20>MA60>MA120",
    "MA120>MA60>MA40>MA20>MA5",
    "MA5>MA20>MA60>MA40>MA120",
    "MA5>MA40>MA60>MA20>MA120",
    "MA5>MA60>MA40>MA20>MA120",
}

# ── 시총 필터 ─────────────────────────────────────────────
mc = pd.read_csv(CSV_PATH_MC, encoding="cp949", dtype={"code": str})
mc["code"] = mc["code"].str.zfill(6)
mc = mc[mc["code"].str.match(r"^\d{6}$")]
all_codes   = mc[mc["market_cap_100m"] >= MIN_CAP]["code"].tolist()
code_market = mc.set_index("code")["market"].to_dict()

print(f"스캔 대상: {len(all_codes)}개 | 기준일: {TODAY_STR} | 스캔범위: -{SCAN_DAYS} 거래일")

# ── 600봉 마스터 로드 ─────────────────────────────────────
ohlc = pd.read_csv(CSV_PATH_OHLC, encoding="utf-8-sig")
# 종목코드 → code로 통일
ohlc["code"] = ohlc["code"].astype(str).str.zfill(6)

ohlc = ohlc.sort_values(["code", "일자"]).reset_index(drop=True)



# ── ETF/ETN 필터 ─────────────────────────────────────────
code_name_cache = {}

def is_etf_or_etn(code):
    if code in code_name_cache:
        name = code_name_cache[code]
    else:
        name = kiwoom.GetMasterCodeName(code)
        code_name_cache[code] = name
    if "ETF" in name or "ETN" in name:
        return True
    return False

# ── 신호 탐지 함수 ────────────────────────────────────────
def detect_signals(code, df, scan_days):
    signals = []
    n = len(df)
    if n < 125:
        return signals

    df = df.copy()
    df["MA5"]   = df["현재가"].rolling(5).mean()
    df["MA20"]  = df["현재가"].rolling(20).mean()
    df["MA40"]  = df["현재가"].rolling(40).mean()
    df["MA60"]  = df["현재가"].rolling(60).mean()
    df["MA120"] = df["현재가"].rolling(120).mean()

    scan_start = max(122, n - scan_days)
    scan_end   = n

    for idx in range(scan_start, scan_end):
        r0 = df.iloc[idx]
        r1 = df.iloc[idx - 1]
        r2 = df.iloc[idx - 2]

        # ── 기본 신호 조건 ──────────────────────────
        prev_bull      = r1["현재가"] > r1["시가"]
        gap_candle     = r0["현재가"] > r0["시가"]
        gap_rate       = (r0["시가"] - r1["현재가"]) / r1["현재가"] * 100
        lower_tail_ok  = r0["저가"] > r1["현재가"]
        vol_ma20       = df["거래량"].iloc[idx-20:idx].mean()
        vol_cond       = r0["거래량"] >= vol_ma20 * 2

        if not (prev_bull and gap_candle and gap_rate >= 0.5 and vol_cond and lower_tail_ok):
            continue

        # ── MA 배열 ────────────────────────────────
        ma_vals = {k: df[k].iloc[idx] for k in ["MA5","MA20","MA40","MA60","MA120"]}
        if any(pd.isna(v) for v in ma_vals.values()):
            continue
        ma_arr = ">".join([k for k, _ in sorted(ma_vals.items(), key=lambda x: x[1], reverse=True)])
        if ma_arr not in ALLOW_MA:
            continue

        # ── 거래량 급등 이력 필터 ──────────────────
        vol_hist       = df["거래량"].iloc[idx-10:idx]
        vol_hist_ma20  = df["거래량"].iloc[idx-30:idx-10].mean()
        vol_spike_hist = (vol_hist >= vol_hist_ma20 * 5).any()
        if gap_rate < 5.0 and vol_spike_hist:
            continue

        # ★ 코어 구간 필터: 5~10% 갭 + 급등 없음만 우선 체크
        #if not (5.0 <= gap_rate < 10.0 and not vol_spike_hist):
         #   continue

        # ── 전략 지표 계산 ─────────────────────────
        total_range  = r0["현재가"] - r1["시가"]
        prev_range_v = r1["고가"]   - r1["저가"]
        high_pt      = r0["현재가"] + prev_range_v
        r1_to_r0_low = r0["저가"]   - r1["시가"]
        low_pt       = high_pt - (total_range + r1_to_r0_low)
        body_range   = r0["현재가"] - r0["시가"]

        cur_price         = r0["현재가"]
        target_price_base = r1["고가"] + (prev_range_v * 3 + body_range)

        gap_price         = r0["시가"] - r1["현재가"]
        target_price_gap3 = cur_price + gap_price * 3 + body_range

        target_price      = max(target_price_base, target_price_gap3)
        min_target_pct    = 2.0
        min_target_price  = cur_price * (1 + min_target_pct / 100)
        if target_price <= min_target_price:
            target_price = min_target_price

        half_point  = (r1["시가"] + cur_price) / 2
        stop_price  = half_point - (cur_price - r1["시가"])

        rise_2to1   = (r1["현재가"] - r2["현재가"]) / r2["현재가"] * 100
        rise_1to0   = (cur_price   - r1["현재가"]) / r1["현재가"] * 100

        # ── 현재가 기준 목표/손절 거리 ─────────────
        to_target = round((target_price - cur_price) / cur_price * 100, 2)
        to_stop   = round((cur_price   - stop_price) / cur_price * 100, 2)

        if to_target <= 0 or to_stop <= 0:
            continue

        rr = round(to_target / to_stop, 2)
        if rr < 1.0:
            continue

        # ★ 등급 플래그
        is_core = (5.0 <= gap_rate < 10.0) and (not vol_spike_hist)
        grade = "A" if is_core else "B"

        signals.append({
            "market":        code_market.get(code, "UNKNOWN"),
            "code":          code,
            "signal_date":   str(r0["일자"]),
            "cur_price":     int(cur_price),
            "gap_rate":      round(gap_rate, 2),
            "rise_2to1":     round(rise_2to1, 2),
            "rise_1to0":     round(rise_1to0, 2),
            "target_price":  round(target_price),
            "stop_price":    round(stop_price),
            "to_target_pct": to_target,
            "to_stop_pct":   to_stop,
            "rr_ratio":      rr,
            "ma_arr":        ma_arr,
            "total_range":   round(total_range),
            "prev_range":    round(prev_range_v),
            "high_pt":       round(high_pt),
            "low_pt":        round(low_pt),
            "vol_spike_hist": vol_spike_hist,
            "grade": grade,  # ★ 추가
            "is_core": is_core,  # 원하면 bool도 같이
        })
    return signals

# ── 메인 루프 ─────────────────────────────────────────────
all_signals = []
start_time  = time.time()

for i, code in enumerate(all_codes):
    if is_etf_or_etn(code):
        continue
    if i % 100 == 0:
        elapsed = (time.time() - start_time) / 60
        print(f"▶ {i}/{len(all_codes)} | 경과 {elapsed:.1f}분 | 신호 {len(all_signals)}건")

    try:
        # ── 마스터에서 해당 종목 600봉 슬라이스 ──
        df = ohlc[ohlc["code"] == code].copy()
        if df.empty:
            continue

        # 일자 정렬 (이미 정렬되어 있어도 한 번 더 안전하게)
        df = df.sort_values("일자").reset_index(drop=True)

        # 컬럼 이름 통일 (이미 이 이름이면 생략 가능)
        # df.rename(columns={"종목코드": "code"}, inplace=True)

        for col in ["시가", "고가", "저가", "현재가", "거래량"]:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.strip()
                    .str.replace(",", "", regex=False)
                    .str.replace("+", "", regex=False)
                    .str.replace("-", "", regex=False),
                errors="coerce"
            )
        df = df.dropna(subset=["시가","고가","저가","현재가","거래량"]).reset_index(drop=True)

        sigs = detect_signals(code, df, SCAN_DAYS)
        all_signals.extend(sigs)

    except Exception as e:
        print(f"에러: {code} → {e}")
        continue


# ── 결과 저장 & 출력 ──────────────────────────────────────
rdf = pd.DataFrame(all_signals)

if rdf.empty:
    print("\n⚠️ 신호 없음")
else:
    rdf = rdf.sort_values(["signal_date","rr_ratio"], ascending=[False, False]).reset_index(drop=True)

    out_path = rf"D:\auto_ht_projt\pycharm\live_signals_{TODAY_STR}_v2 .csv"
    # ── 한글 헤더 1행 추가 ───────────────────────
    korean_header = {
        "market": "시장",
        "code": "종목코드",
        "signal_date": "신호일",
        "cur_price": "현재가",
        "gap_rate": "갭(%)",
        "to_target_pct": "목표까지(%)",
        "to_stop_pct": "손절까지(%)",
        "rr_ratio": "손익비",
        "ma_arr": "이평배열",
        "total_range": "전일시가→금일종가",
        "prev_range": "전일고가-저가",
        "high_pt": "전략상단",
        "low_pt": "전략하단",
        "vol_spike_hist": "직전10봉 거래량급등",
    }

    header_row = {col: korean_header.get(col, col) for col in rdf.columns}
    header_df = pd.DataFrame([header_row])
    export_df = pd.concat([header_df, rdf], ignore_index=True)

    export_df.to_csv(out_path, index=False, encoding="cp949")

    print(f"\n{'='*55}")
    print(f"✅ 완료 | 총 신호: {len(rdf)}건")
    print(f"📁 저장: {out_path}")
    print(f"\n[시장별]")
    print(rdf["market"].value_counts().to_string())
    print(f"\n[날짜별]")
    print(rdf["signal_date"].value_counts().sort_index(ascending=False).to_string())
    print(f"\n[상위 신호 (RR 높은 순)]")
    print(rdf[["market","code","signal_date","cur_price","gap_rate",
               "to_target_pct","to_stop_pct","rr_ratio","ma_arr"]].head(10).to_string())
