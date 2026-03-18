import pandas as pd

path = r"D:\auto_ht_projt\pycharm\backtest_result\backtest_results＿ans.csv"

# 1) 두 번째 줄을 헤더로 사용
df = pd.read_csv(path, header=1, encoding="cp949")

# 2) 불필요한 완전 빈 행들 제거
df = df.dropna(how="all")

# 3) TRUE/FALSE 문자열을 bool로 변환
for col in ["reached_20", "reached_80", "stopped", "near_miss", "strategy_full", "vol_spike_hist"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.upper().map({"TRUE": True, "FALSE": False})

# 4) 숫자 컬럼 정리
num_cols = ["gap_rate","rise_2to1","rise_1to0","target_price","stop_price",
            "peak_pct","days_to_reach","min_low_pct",
            "total_range","prev_range","high_pt","low_pt"]
for col in num_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# =============== 1) peak 상위 TOP5 ===============
win20 = df[df["reached_20"] == True].copy()
win20_sorted = win20.sort_values("peak_pct", ascending=False)
peak_top5 = win20_sorted.head(5)

print("\n[피크 상위 TOP5]")
print(peak_top5[["market","code","date","gap_rate","rise_2to1","rise_1to0",
                 "target_price","stop_price","peak_pct","min_low_pct","ma_arr","vol_spike_hist"]]
      .to_string(index=False))

# =============== 2) 20봉 이내 도달 후 추가 상승량 ===============
win20["extra_over_target_pct"] = win20["peak_pct"] - 100

summary = {
    "count_win20":  int(len(win20)),
    "extra_mean":   round(win20["extra_over_target_pct"].mean(), 2),
    "extra_median": round(win20["extra_over_target_pct"].median(), 2),
    "extra_q25":    round(win20["extra_over_target_pct"].quantile(0.25), 2),
    "extra_q75":    round(win20["extra_over_target_pct"].quantile(0.75), 2),
}

print("\n[20봉 이내 도달 후 목표 대비 추가 상승률(peak_pct - 100) 통계]")
for k, v in summary.items():
    print(f"  {k}: {v}")

peak_top5.to_csv(
    r"D:\auto_ht_projt\pycharm\backtest_result\peak_top5_from_ans.csv",
    index=False,
    encoding="utf-8-sig"
)
