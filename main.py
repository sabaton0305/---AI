import config
from analysis import analyze_stock
from line_notify import send_line_message


def format_message(name, result):
    """LINE通知用メッセージを作成"""

    message = f"""📈 {name}

判定：{result['judgment']}
スコア：{result['score']}点

現在値：{result['close']:.2f}円
トレンド：{result['trend']}

RSI：{result['rsi']:.2f}
MACD：{result['macd']:.2f}
シグナル：{result['signal']:.2f}

出来高倍率：{result['volume_ratio']:.2f}倍

■コメント
"""

    if result["comments"]:
        for comment in result["comments"]:
            message += f"・{comment}\n"
    else:
        message += "・特になし"

    return message


def main():
    print("株価分析開始")

    for name, ticker in config.STOCKS.items():
        print(f"{name} を分析中...")

        result = analyze_stock(ticker, config)

        if result is None:
            print(f"{name} の取得に失敗")
            continue

        message = format_message(name, result)

        print(message)

        send_line_message(message)

    print("分析終了")


if __name__ == "__main__":
    main()
