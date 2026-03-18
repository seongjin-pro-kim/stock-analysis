import pandas as pd

PATH = r"D:\auto_ht_projt\board\streamlit-dashboard\csv_etc\trades_formatted_v1.csv"

# 1행 한글 헤더 스킵, 2행을 컬럼으로 사용
df = pd.read_csv(PATH, encoding="cp949", header=1)

ret_col = "ret"  # 최종 수익률 (0.17 = +17%)

# 전체 통계
wins   = df[df[ret_col] > 0][ret_col]
losses = df[df[ret_col] < 0][ret_col]

num_trades = len(df)
win_rate   = len(wins) / num_trades if num_trades > 0 else 0.0
avg_win    = wins.mean() if len(wins) > 0 else 0.0
avg_loss   = losses.mean() if len(losses) > 0 else 0.0  # 음수

rr_ratio = avg_win / abs(avg_loss) if avg_loss < 0 else None
expectancy = win_rate * avg_win - (1 - win_rate) * abs(avg_loss)

print("=== 전체 성과 요약 ===")
print("총 트레이드 수:", num_trades)
print("승률:", round(win_rate * 100, 2), "%")
print("평균 이익:", round(avg_win, 4))
print("평균 손실:", round(avg_loss, 4))
print("손익비 (RR): 1 :",
      round(rr_ratio, 3) if rr_ratio is not None else "N/A")
print("기대값(트레이드당):", round(expectancy, 4))

# 선택: 승/패별 평균 소요일, 최대 낙폭 같은 것도 바로 뽑을 수 있음
if "days_held" in df.columns:
    print("\n승리 평균 소요일:", df[df[ret_col] > 0]["days_held"].mean())
    print("패배 평균 소요일:", df[df[ret_col] < 0]["days_held"].mean())
