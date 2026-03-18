"""
거래 데이터 보강 스크립트 (한 장 버전)
- live_signal CSV에 필요한 데이터 필드 추가
- 거래 내역 CSV에 매도시점 MA 데이터 반영
- 실현손익 데이터 수집
- 피크 수익율 추적 (목표 달성 후 상위 5개)

사용법:
  python automation/trade_data_enricher.py

필요 패키지: pip install pandas numpy
키움 OpenAPI 연동 시: pip install pykiwoom (별도 설정 필요)

=== 사용자 PC (D:\\auto_ht_projt\\pycharm\\)에서 실행 ===
이 스크립트는 call_test.py, reach_test.py와 동일 환경에서 동작합니다.
"""
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ── 설정 ──────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_DIR = os.path.join(BASE_DIR, "csv_etc")
os.makedirs(CSV_DIR, exist_ok=True)

# 파일 경로
LIVE_SIGNAL_CSV = os.path.join(CSV_DIR, "live_signals.csv")
TRADES_CSV = os.path.join(CSV_DIR, "trades_enriched_v1.csv")
PEAK_TRACKING_CSV = os.path.join(CSV_DIR, "peak_tracking.csv")
REALIZED_PNL_CSV = os.path.join(CSV_DIR, "realized_pnl.csv")

# MA 기간 설정
MA_PERIODS = [5, 10, 20, 40, 60, 120]


# ══════════════════════════════════════════════════════════
# 1. 종목별 MA 배열 계산
# ══════════════════════════════════════════════════════════
def calculate_ma_pattern(close_prices: pd.Series) -> str:
    """종가 시리즈로부터 MA 배열 패턴 문자열 생성
    
    Args:
        close_prices: 최소 120일 이상의 종가 시리즈 (오름차순 날짜)
    
    Returns:
        "MA5>MA20>MA60>MA120" 형태의 패턴 문자열
    """
    if len(close_prices) < max(MA_PERIODS):
        return ""
    
    ma_values = {}
    for period in MA_PERIODS:
        ma_val = close_prices.tail(period).mean()
        ma_values[f"MA{period}"] = ma_val
    
    # 내림차순 정렬
    sorted_mas = sorted(ma_values.items(), key=lambda x: x[1], reverse=True)
    pattern = ">".join([name for name, _ in sorted_mas])
    return pattern


def calculate_disparity(close_prices: pd.Series) -> dict:
    """이격도 계산 (현재가 / MA × 100)"""
    if len(close_prices) < max(MA_PERIODS):
        return {}
    
    current = close_prices.iloc[-1]
    result = {}
    for period in MA_PERIODS:
        ma_val = close_prices.tail(period).mean()
        if ma_val > 0:
            result[f"disparity_{period}"] = round(current / ma_val * 100, 2)
    return result


# ══════════════════════════════════════════════════════════
# 2. live_signal CSV 필드 보강
# ══════════════════════════════════════════════════════════
def enrich_live_signals(signal_df: pd.DataFrame) -> pd.DataFrame:
    """live_signal CSV에 필요한 데이터 필드 추가
    
    추가 필드:
    - target_rate: 목표 수익율 (%)
    - stop_rate: 손절율 (%)
    - rr_ratio: 손익비
    - expected_value: 기대값
    - grade: 등급 (A/B/C)
    """
    df = signal_df.copy()
    
    # target_rate 계산
    if "entry_price" in df.columns and "target_price" in df.columns:
        df["target_rate"] = ((df["target_price"] - df["entry_price"]) / df["entry_price"] * 100).round(1)
    
    # stop_rate 계산
    if "entry_price" in df.columns and "stop_price" in df.columns:
        df["stop_rate"] = ((df["stop_price"] - df["entry_price"]) / df["entry_price"] * 100).round(1)
    
    # rr_ratio 계산
    if "target_rate" in df.columns and "stop_rate" in df.columns:
        df["rr_ratio"] = (df["target_rate"].abs() / df["stop_rate"].abs()).round(2)
        df["rr_ratio"] = df["rr_ratio"].replace([np.inf, -np.inf], 0)
    
    # expected_value 계산 (승률 79% 기준)
    WIN_RATE = 0.79
    if "target_rate" in df.columns and "stop_rate" in df.columns:
        df["expected_value"] = (
            df["target_rate"] * WIN_RATE + df["stop_rate"] * (1 - WIN_RATE)
        ).round(1)
    
    # grade 자동 등급 부여
    if "rr_ratio" in df.columns:
        conditions = [
            df["rr_ratio"] >= 3.0,
            df["rr_ratio"] >= 1.5,
        ]
        choices = ["A", "B"]
        df["grade"] = np.select(conditions, choices, default="C")
    
    return df


# ══════════════════════════════════════════════════════════
# 3. 매도시점 MA 데이터 수집
# ══════════════════════════════════════════════════════════
def add_sell_ma_to_trades(trades_df: pd.DataFrame, 
                          get_close_prices_fn=None) -> pd.DataFrame:
    """거래 내역에 매도시점 MA 패턴 추가
    
    Args:
        trades_df: 거래 내역 DataFrame
        get_close_prices_fn: 종목코드, 날짜를 받아 종가 시리즈 반환하는 함수
                             (키움 API 연동 시 구현)
    
    Example get_close_prices_fn:
        def get_prices(code, date):
            # 키움 API로 date 기준 최근 120일 종가 가져오기
            return pd.Series([...])
    """
    df = trades_df.copy()
    
    if "sell_ma" not in df.columns:
        df["sell_ma"] = ""
    
    # 매도 완료된 건 중 sell_ma가 비어있는 것만 처리
    mask = (df["result"].isin(["승", "패"])) & (df["sell_ma"].isna() | (df["sell_ma"] == ""))
    
    if get_close_prices_fn is None:
        print("  ⚠️ 종가 데이터 함수가 없어 매도 MA를 계산할 수 없습니다.")
        print("     키움 API 연동 후 get_close_prices_fn을 구현해주세요.")
        return df
    
    for idx in df[mask].index:
        code = df.loc[idx, "code"]
        sell_date = df.loc[idx, "date"]
        
        try:
            prices = get_close_prices_fn(code, sell_date)
            if len(prices) >= 120:
                pattern = calculate_ma_pattern(prices)
                df.loc[idx, "sell_ma"] = pattern
                print(f"  ✅ {df.loc[idx, 'name']} 매도MA: {pattern}")
        except Exception as e:
            print(f"  ❌ {df.loc[idx, 'name']} 오류: {e}")
    
    return df


# ══════════════════════════════════════════════════════════
# 4. 피크 수익율 추적 (목표 달성 이후)
# ══════════════════════════════════════════════════════════
def track_post_target_peaks(trades_df: pd.DataFrame,
                            get_close_prices_fn=None) -> pd.DataFrame:
    """목표 달성 후 피크 수익율 상위 5개 추적
    
    - 목표 달성 직후부터 현재까지의 MA 배열, 이격도, 캔들 관계 수집
    """
    completed_wins = trades_df[trades_df["result"] == "승"].copy()
    top5 = completed_wins.sort_values("peak_pct", ascending=False).head(5)
    
    results = []
    for _, trade in top5.iterrows():
        entry = {
            "code": trade["code"],
            "name": trade["name"],
            "entry_date": trade["date"],
            "peak_pct": trade["peak_pct"],
            "target_price": trade["target_price"],
        }
        
        if get_close_prices_fn is not None:
            try:
                # 목표 달성 이후의 가격 데이터
                prices = get_close_prices_fn(trade["code"], datetime.now())
                if len(prices) >= 120:
                    entry["current_ma"] = calculate_ma_pattern(prices)
                    disparities = calculate_disparity(prices)
                    entry.update(disparities)
                    
                    # 캔들 관계 (최근 5일)
                    recent = prices.tail(5)
                    entry["recent_trend"] = "상승" if recent.iloc[-1] > recent.iloc[0] else "하락"
                    entry["candle_body_avg"] = round(
                        (recent.diff().abs().mean() / recent.mean() * 100), 2
                    )
            except Exception as e:
                entry["error"] = str(e)
        
        results.append(entry)
    
    return pd.DataFrame(results)


# ══════════════════════════════════════════════════════════
# 5. 실현손익 일별 수집
# ══════════════════════════════════════════════════════════
def collect_realized_pnl(trades_df: pd.DataFrame) -> pd.DataFrame:
    """일별 실현손익 데이터 생성"""
    completed = trades_df[trades_df["result"].isin(["승", "패"])].copy()
    
    if len(completed) == 0:
        return pd.DataFrame()
    
    # 매도일 기준 집계
    completed["sell_date"] = completed["date"] + pd.to_timedelta(completed["days_to_target"], unit="D")
    
    daily_pnl = completed.groupby("sell_date").agg(
        거래수=("result", "count"),
        승리수=("result", lambda x: (x == "승").sum()),
        패배수=("result", lambda x: (x == "패").sum()),
        평균수익=("peak_pct", "mean"),
        평균손실=("min_low_pct", "mean"),
        총수익건_수익합=("peak_pct", lambda x: x[x > 0].sum()),
        총손실건_손실합=("min_low_pct", lambda x: x[x < 0].sum()),
    ).reset_index()
    
    daily_pnl = daily_pnl.rename(columns={"sell_date": "date"})
    return daily_pnl


# ══════════════════════════════════════════════════════════
# 메인 실행
# ══════════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print(f"거래 데이터 보강 스크립트 — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    # 1. 거래 내역 로드
    if os.path.exists(TRADES_CSV):
        trades = pd.read_csv(TRADES_CSV, encoding="utf-8-sig")
        trades["date"] = pd.to_datetime(trades["date"])
        print(f"\n📂 거래 내역 로드: {len(trades)}건")
    else:
        print(f"\n⚠️ 거래 내역 파일 없음: {TRADES_CSV}")
        print("  샘플 데이터로 생성합니다...")
        sys.path.insert(0, BASE_DIR)
        from sample_data import get_sample_trades
        trades = get_sample_trades()
    
    # 2. 필드 보강
    print("\n🔧 데이터 필드 보강 중...")
    trades = enrich_live_signals(trades)
    print("  ✅ target_rate, stop_rate, rr_ratio, expected_value, grade 계산 완료")
    
    # 3. 매도 MA (키움 API 없이는 스킵)
    print("\n📊 매도시점 MA 패턴...")
    trades = add_sell_ma_to_trades(trades, get_close_prices_fn=None)
    
    # 4. 피크 추적
    print("\n📈 피크 수익율 추적...")
    peak_df = track_post_target_peaks(trades, get_close_prices_fn=None)
    if len(peak_df) > 0:
        peak_df.to_csv(PEAK_TRACKING_CSV, index=False, encoding="utf-8-sig")
        print(f"  💾 피크 추적 데이터 저장: {PEAK_TRACKING_CSV}")
    
    # 5. 실현손익
    print("\n💰 일별 실현손익 집계...")
    pnl_df = collect_realized_pnl(trades)
    if len(pnl_df) > 0:
        pnl_df.to_csv(REALIZED_PNL_CSV, index=False, encoding="utf-8-sig")
        print(f"  💾 실현손익 데이터 저장: {REALIZED_PNL_CSV}")
    
    # 6. 보강된 거래 내역 저장
    trades.to_csv(TRADES_CSV, index=False, encoding="utf-8-sig")
    print(f"\n💾 보강된 거래 내역 저장: {TRADES_CSV}")
    
    print("\n✅ 완료!")
    print("-" * 60)
    print("📌 키움 API 연동 시 추가 필요 사항:")
    print("   - get_close_prices_fn 함수 구현")
    print("   - call_test.py에서 live_signal CSV 생성 시 enrich_live_signals() 호출")
    print("   - 매도 시 add_sell_ma_to_trades()로 매도 MA 기록")
    print("-" * 60)


if __name__ == "__main__":
    main()
