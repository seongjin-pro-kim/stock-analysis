from pathlib import Path
BASE_DIR = Path("D:/auto_ht_projt/board/streamlit-dashboard").resolve()

trades_path = BASE_DIR / "csv_etc" / "trades_formatted_v1.csv"
signals_path = BASE_DIR / "csv_etc" / "live_signals_20260316_check.csv"
output_path = BASE_DIR / "csv_etc" / "trades_enriched_v1.csv"

print(trades_path)
print(trades_path.exists())