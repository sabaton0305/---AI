import config
from analysis import analyze_stock

for name, ticker in config.STOCKS.items():

    result = analyze_stock(ticker, config)

    print("=" * 50)
    print(name)

    if result is None:
        print("取得失敗")
        continue

    print(f"終値     : {result['close']:.0f}")
    print(f"高値     : {result['high']:.0f}")
    print(f"安値     : {result['low']:.0f}")
    print(f"出来高   : {int(result['volume'])}")

    print(f"5日線    : {result['ma5']:.1f}")
    print(f"25日線   : {result['ma25']:.1f}")

    print(f"RSI      : {result['rsi']:.1f}")
    print(f"MACD     : {result['macd']:.2f}")
    print(f"Signal   : {result['signal']:.2f}")
    print(f"トレンド : {result['trend']}")

    print(f"判定     : {result['decision']}")
    print(f"エントリー: {result['entry']:.0f}円")
    print(f"損切り   : {result['stop_loss']:.0f}円")
    print(f"利確目標 : {result['take_profit']:.0f}円")
    print(f"\n総合点数 : {result['score']}/100")
