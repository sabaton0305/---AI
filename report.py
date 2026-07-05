from pathlib import Path
import pandas as pd


def save_csv(df, path: Path, analysis: dict = None):
    path.parent.mkdir(parents=True, exist_ok=True)
    # append analysis fields to the last row for reference
    df_out = df.copy()
    # Ensure columns exist (use NA to allow numeric values)
    for col in ("entry", "stop_loss", "take_profit", "decision", "score"):
        if col not in df_out.columns:
            df_out[col] = pd.NA

    if analysis is not None and len(df_out) > 0:
        last_idx = df_out.index[-1]
        df_out.at[last_idx, "entry"] = analysis.get("entry")
        df_out.at[last_idx, "stop_loss"] = analysis.get("stop_loss")
        df_out.at[last_idx, "take_profit"] = analysis.get("take_profit")
        df_out.at[last_idx, "decision"] = analysis.get("decision")
        df_out.at[last_idx, "score"] = analysis.get("score")

    df_out.to_csv(path, index=True)


def save_report(name: str, analysis: dict, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    latest = analysis.get("latest")
    with path.open("w", encoding="utf-8") as f:
        f.write(f"{name} 分析レポート\n")
        f.write("=\n")
        f.write(f"総合スコア: {analysis.get('score')}/100\n")
        f.write(f"判定: {analysis.get('judgment')}\n\n")
        f.write("最新データ:\n")
        if latest is not None:
            f.write(latest.to_string())
            f.write("\n\n")
        f.write("コメント:\n")
        for c in analysis.get("comments", []):
            f.write(f"- {c}\n")

        # Trade suggestions
        entry = analysis.get("entry")
        stop_loss = analysis.get("stop_loss")
        take_profit = analysis.get("take_profit")
        decision = analysis.get("decision")

        f.write("\n取引提案:\n")
        if entry is not None:
            f.write(f"- エントリー(想定): {entry:.0f}\n")
        if stop_loss is not None:
            f.write(f"- 損切り(想定): {stop_loss:.2f}\n")
        if take_profit is not None:
            f.write(f"- 利確(想定): {take_profit:.2f}\n")
        if decision:
            f.write(f"- 判定: {decision}\n")
