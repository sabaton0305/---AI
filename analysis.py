import pandas as pd
import yfinance as yf
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, EMAIndicator, ADXIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import MFIIndicator


def fetch_history(ticker: str, period: str = "6mo", auto_adjust: bool = False) -> pd.DataFrame:
    t = yf.Ticker(ticker)
    return t.history(period=period, auto_adjust=auto_adjust)


def compute_indicators(df: pd.DataFrame, config) -> pd.DataFrame:
    df = df.copy()
    df[f"MA{config.MA_SHORT}"] = df["Close"].rolling(config.MA_SHORT).mean()
    df[f"MA{config.MA_LONG}"] = df["Close"].rolling(config.MA_LONG).mean()
    df["RSI"] = RSIIndicator(df["Close"], window=config.RSI_PERIOD).rsi()
    stoch = StochasticOscillator(
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        window=14,
        smooth_window=3,
    )
    df["STOCH_K"] = stoch.stoch()
    df["STOCH_D"] = stoch.stoch_signal()
    macd = MACD(df["Close"])
    df["MACD"] = macd.macd()
    df["Signal"] = macd.macd_signal()
    bb = BollingerBands(df["Close"], window=20, window_dev=2)
    df["BB_UPPER"] = bb.bollinger_hband()
    df["BB_LOWER"] = bb.bollinger_lband()
    df["BB_MIDDLE"] = bb.bollinger_mavg()
    atr = AverageTrueRange(high=df["High"], low=df["Low"], close=df["Close"], window=14)
    df["ATR"] = atr.average_true_range()
    adx = ADXIndicator(high=df["High"], low=df["Low"], close=df["Close"], window=14)
    df["ADX"] = adx.adx()
    mfi = MFIIndicator(
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        volume=df["Volume"],
        window=14,
    )
    df["MFI"] = mfi.money_flow_index()
    ema20 = EMAIndicator(df["Close"], window=20)
    ema50 = EMAIndicator(df["Close"], window=50)
    df["EMA20"] = ema20.ema_indicator()
    df["EMA50"] = ema50.ema_indicator()
    # Normalize column names to MA5/MA25 for compatibility
    df["MA5"] = df[f"MA{config.MA_SHORT}"]
    df["MA25"] = df[f"MA{config.MA_LONG}"]
    df["MA75"] = df["Close"].rolling(75).mean()
    return df


def analyze_latest(df: pd.DataFrame, config) -> dict:
    latest = df.iloc[-1]
    previous = df.iloc[-2]

    score = 50
    comments = []

    # RSI
    rsi = latest.get("RSI")
    if pd.notna(rsi):
        if rsi <= 20:
            score += 30
        elif rsi <= 25:
            score += 25
        elif rsi <= 30:
            score += 20
        elif rsi <= 35:
            score += 10
        elif rsi >= 85:
            score -= 30
        elif rsi >= 80:
            score -= 25
        elif rsi >= 75:
            score -= 20
        elif rsi >= 70:
            score -= 15

        if rsi >= 85:
            comments.append("RSIが85以上で極端な買われ過ぎです。")
        elif rsi >= 70:
            comments.append("RSIが70以上で買われ過ぎです。")
        elif rsi <= 20:
            comments.append("RSIが20以下で極端な売られ過ぎです。")
        elif rsi <= 30:
            comments.append("RSIが30以下で売られ過ぎです。")

    # Moving averages
    ma5 = latest.get("MA5")
    ma25 = latest.get("MA25")
    ma75 = latest.get("MA75")
    ema20 = latest.get("EMA20")
    ema50 = latest.get("EMA50")
    adx = latest.get("ADX")
    stoch_k = latest.get("STOCH_K")
    stoch_d = latest.get("STOCH_D")
    mfi = latest.get("MFI")

    # RSI + ストキャス
    if (
        pd.notna(rsi)
        and pd.notna(stoch_k)
        and rsi < 30
        and stoch_k < 20
    ):
        score += 10
        comments.append("売られ過ぎシグナル一致")
    if pd.notna(ma5) and pd.notna(ma25):
        if ma5 > ma25:
            score += 15
        else:
            score -= 15

    # MA25とMA75で中長期トレンド判定
    if pd.notna(ma25) and pd.notna(ma75):
        if ma25 > ma75:
            score += 10
        else:
            score -= 10

    if pd.notna(ema20) and pd.notna(ema50):
        if ema20 > ema50:
            score += 10
            comments.append("EMAは上昇トレンドです。")
        else:
            score -= 10

    prev_ma5 = previous.get("MA5")
    prev_ma25 = previous.get("MA25")

    if (
        pd.notna(prev_ma5)
        and pd.notna(prev_ma25)
        and pd.notna(ma5)
        and pd.notna(ma25)
    ):
        if prev_ma5 <= prev_ma25 and ma5 > ma25:
            score += 20
            comments.append("ゴールデンクロス発生")

            # ゴールデンクロス + ADX
            if pd.notna(adx) and adx >= 25:
                score += 10
                comments.append("ゴールデンクロス＋強いトレンド")

        elif prev_ma5 >= prev_ma25 and ma5 < ma25:
            score -= 20
            comments.append("デッドクロス発生")

    # MACD
    macd = latest.get("MACD")
    signal = latest.get("Signal")
    if pd.notna(macd) and pd.notna(signal):
        if macd > signal:
            score += 15
            comments.append("MACDは上昇トレンドを示しています。")
        else:
            score -= 15

    # ADX（トレンドの強さ）
    if pd.notna(adx):
        if adx >= 40:
            score += 20
            comments.append("非常に強いトレンドです。")
        elif adx >= 30:
            score += 15
            comments.append("強いトレンドです。")
        elif adx >= 25:
            score += 10
            comments.append("トレンドが発生しています。")
        elif adx < 20:
            score -= 10
            comments.append("レンジ相場の可能性があります。")

    # ストキャスティクス
    if pd.notna(stoch_k) and pd.notna(stoch_d):
        if stoch_k < 20 and stoch_d < 20:
            score += 15
            comments.append("ストキャスは売られ過ぎです。")
        elif stoch_k > 80 and stoch_d > 80:
            score -= 15
            comments.append("ストキャスは買われ過ぎです。")

    # MFI（資金流入）
    if pd.notna(mfi):
        if mfi < 20:
            score += 15
            comments.append("資金流入の初動です。")
        elif mfi < 30:
            score += 10
            comments.append("資金流入が始まっています。")
        elif mfi > 80:
            score -= 15
            comments.append("資金流出に注意。")

    # MFIのあと
    bb_upper = latest.get("BB_UPPER")
    bb_lower = latest.get("BB_LOWER")
    atr = latest.get("ATR")
    close = latest.get("Close")

    # 20日高値
    recent_high = df["High"].iloc[-21:-1].max()

    if pd.notna(close) and close > recent_high:
        score += 20
        comments.append("20日高値をブレイクしました。")

    # Volume vs configured-period average
    avg_volume = df["Volume"].tail(config.VOLUME_PERIOD).mean()
    vol = latest.get("Volume")
    volume_ratio = None
    if pd.notna(vol) and pd.notna(avg_volume):
        volume_ratio = vol / avg_volume

    # ブレイクアウト + 出来高急増
    if (
        volume_ratio is not None
        and volume_ratio >= 2
        and pd.notna(close)
        and close > recent_high
    ):
        score += 15
        comments.append("ブレイクアウト＋出来高急増")

    if volume_ratio is not None:
        if volume_ratio >= 3:
            score += 20
            comments.append("出来高が平均の3倍以上です。")

        elif volume_ratio >= 2:
            score += 15
            comments.append("出来高が平均の2倍以上です。")

        elif volume_ratio >= 1.5:
            score += 10
            comments.append("出来高が平均の1.5倍です。")

        elif volume_ratio >= 1.2:
            score += 5

        else:
            score -= 5

    if pd.notna(close):
        if pd.notna(bb_lower) and close < bb_lower:
            score += 15
            comments.append("ボリンジャーバンド下限を下抜け。反発期待。")

        elif pd.notna(bb_upper) and close > bb_upper:
            score -= 10
            comments.append("ボリンジャーバンド上限突破。過熱気味。")

    # すべての score += が終わる
    score = int(max(0, min(score, 100)))

    # judgment判定
    if score >= 80:
        judgment = "★★★★★ 強い買い"
    elif score >= 65:
        judgment = "★★★★☆ 買い"
    elif score >= 45:
        judgment = "★★★☆☆ ホールド"
    elif score >= 30:
        judgment = "★★☆☆☆ 注意"
    else:
        judgment = "★☆☆☆☆ 売り寄り"

    
    if pd.notna(rsi) and rsi > 70:
        comments.append("買われ過ぎの水準です。")
    elif pd.notna(rsi) and rsi < 30:
        comments.append("売られ過ぎのため反発に期待できます。")
    if pd.notna(ma5) and pd.notna(ma25):
        if ma5 > ma25:
            comments.append("短期トレンドは上向きです。")
        else:
            comments.append("短期トレンドは弱めです。")
    if pd.notna(ma25) and pd.notna(ma75):
        if ma25 > ma75:
            comments.append("中長期トレンドも上向きです。")
        else:
            comments.append("中長期トレンドは下降傾向です。")

    # Trend judgment based on Close vs MA25
    trend = None
    close = latest.get("Close")
    if pd.notna(close) and pd.notna(ma25):
        if close > ma25:
            trend = "上昇トレンド"
        elif close < ma25:
            trend = "下降トレンド"
        else:
            trend = "レンジ"

    # 52-week high/low distances
    high52 = df["High"].max()
    low52 = df["Low"].min()
    distance_high = None
    distance_low = None
    if pd.notna(close) and pd.notna(high52) and pd.notna(low52):
        distance_high = (close / high52 - 1) * 100
        distance_low = (close / low52 - 1) * 100

    # Simple trade suggestion
    entry = latest.get("Close")
    if pd.notna(entry) and pd.notna(atr):
        stop_loss = entry - atr * 1.5
        take_profit = entry + atr * 3
    else:
        stop_loss = None
        take_profit = None

    # Simple decision mapping (without stars)
    if score >= 80:
        decision = "強い買い"
    elif score >= 65:
        decision = "買い"
    elif score >= 45:
        decision = "ホールド"
    else:
        decision = "様子見"

    return {
        "score": score,
        "judgment": judgment,
        "decision": decision,
        "trend": trend,
        "comments": comments,
        "latest": latest,
        "avg_volume": avg_volume,
        "close": latest.get("Close"),
        "volume_ratio": volume_ratio,
        "high": latest.get("High"),
        "low": latest.get("Low"),
        "volume": latest.get("Volume"),
        "ma5": ma5,
        "ma25": ma25,
        "ma75": ma75,
        "rsi": rsi,
        "macd": macd,
        "signal": signal,
        "atr": atr,
        "ema20": ema20,
        "ema50": ema50,
        "adx": adx,
        "stoch_k": stoch_k,
        "stoch_d": stoch_d,
        "mfi": mfi,
        "bb_upper": bb_upper,
        "bb_lower": bb_lower,
        "entry": entry,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "52high": high52,
        "52low": low52,
        "distance_high": distance_high,
        "distance_low": distance_low,
    }



def analyze_stock(ticker, config):
    df = fetch_history(ticker, period=config.HISTORY_PERIOD, auto_adjust=False)

    if df.empty:
        return None

    df2 = compute_indicators(df, config)
    analysis = analyze_latest(df2, config)

    return analysis

