#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
data/stock_history.csv から在庫推移グラフを作るおまけスクリプト。

使い方:
    pip install matplotlib pandas
    python scripts/plot_history.py

data/stock_history.png が生成されます。
"""

import os

import pandas as pd
import matplotlib.pyplot as plt

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "stock_history.csv")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "stock_history.png")


def main() -> None:
    df = pd.read_csv(DATA_FILE, parse_dates=["timestamp_jst"])

    plt.figure(figsize=(12, 6))
    plt.plot(df["timestamp_jst"], df["in_stock"], label="在庫あり", marker="o", markersize=3)
    plt.plot(df["timestamp_jst"], df["out_of_stock"], label="在庫切れ", marker="o", markersize=3)
    plt.xlabel("日時")
    plt.ylabel("商品数")
    plt.title("i-BLOOM 在庫推移")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=150)
    print(f"グラフを保存しました: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
