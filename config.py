import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

# 監視する銘柄
STOCKS = {
    "ACSL": "6232.T",
    "Liberaware": "218A.T",
}

# LINE設定
# ※Messaging APIを使う場合は後で本物の値に変更してください
LINE_TOKEN = os.getenv("LINE_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")

# 株価取得期間
HISTORY_PERIOD = "6mo"

# 移動平均線
MA_SHORT = 5
MA_LONG = 25

# RSI
RSI_PERIOD = 14

# 出来高平均日数
VOLUME_PERIOD = 20
