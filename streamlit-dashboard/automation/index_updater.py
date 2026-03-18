"""
지수 자동 업데이트 스크립트 (1일 1회)
- KOSPI, KOSDAQ, NASDAQ, BTC 지수 데이터를 수집하여 CSV에 저장
- 대시보드에서 이 CSV를 읽어 실시간 차트에 반영

사용법: 
  python automation/index_updater.py
  
스케줄러 설정 (crontab 또는 Windows Task Scheduler):
  매일 오전 9시: 0 9 * * * cd /path/to/project && python automation/index_updater.py

필요 패키지: pip install yfinance pandas
"""
import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# yfinance 설치 확인
try:
    import yfinance as yf
except ImportError:
    print("yfinance 패키지가 필요합니다: pip install yfinance")
    sys.exit(1)

# 저장 경로
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_DIR = os.path.join(BASE_DIR, "csv_etc")
os.makedirs(CSV_DIR, exist_ok=True)

INDEX_CSV = os.path.join(CSV_DIR, "index_data.csv")

# 지수 티커 매핑
TICKERS = {
    "KOSPI":  "^KS11",
    "KOSDAQ": "^KQ11",
    "NASDAQ": "^IXIC",
    "BTC":    "BTC-USD",
}


def fetch_index_data(period="3mo"):
    """최근 3개월 지수 데이터 다운로드"""
    all_data = []
    
    for name, ticker in TICKERS.items():
        try:
            data = yf.download(ticker, period=period, interval="1d", progress=False)
            if len(data) > 0:
                df = data[["Close"]].reset_index()
                df.columns = ["date", "close"]
                df["index_name"] = name
                df["ticker"] = ticker
                all_data.append(df)
                print(f"  ✅ {name} ({ticker}): {len(df)}일치 데이터")
            else:
                print(f"  ⚠️ {name}: 데이터 없음")
        except Exception as e:
            print(f"  ❌ {name} 오류: {e}")
    
    if all_data:
        result = pd.concat(all_data, ignore_index=True)
        return result
    return pd.DataFrame()


def update_index_csv():
    """지수 CSV 업데이트"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] 지수 데이터 업데이트 시작...")
    
    df = fetch_index_data()
    
    if len(df) > 0:
        df.to_csv(INDEX_CSV, index=False, encoding="utf-8-sig")
        print(f"  💾 저장 완료: {INDEX_CSV} ({len(df)}행)")
    else:
        print("  ⚠️ 데이터를 가져오지 못했습니다.")
    
    return df


if __name__ == "__main__":
    update_index_csv()
"""

사용 예시 (대시보드에서 읽기):

import pandas as pd
import os

INDEX_CSV = os.path.join("csv_etc", "index_data.csv")
if os.path.exists(INDEX_CSV):
    index_df = pd.read_csv(INDEX_CSV)
    # 예: KOSPI 데이터
    kospi = index_df[index_df["index_name"] == "KOSPI"]
"""
