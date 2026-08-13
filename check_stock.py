#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
i-BLOOM SQUISHY SHOP 在庫監視bot
- https://i-bloom.shop/collections/all-items の「在庫あり」「在庫切れ」フィルター件数を取得
- Discordへ通知
- data/stock_history.csv に履歴として追記
"""

import csv
import os
import re
import sys
from datetime import datetime, timezone, timedelta

import requests

COLLECTION_URL = "https://i-bloom.shop/collections/all-items"
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "stock_history.csv")
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# ページ内の「在庫あり (32個の商品)」「在庫切れ (331個の商品)」を抜き出す正規表現
IN_STOCK_PATTERN = re.compile(r"在庫あり\s*\((\d+)個の商品\)")
OUT_OF_STOCK_PATTERN = re.compile(r"在庫切れ\s*\((\d+)個の商品\)")

JST = timezone(timedelta(hours=9))


def fetch_stock_counts() -> tuple[int, int]:
    """商品一覧ページを取得し、在庫あり/在庫切れの件数を返す"""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    resp = requests.get(COLLECTION_URL, headers=headers, timeout=30)
    resp.raise_for_status()
    html = resp.text

    in_stock_matches = IN_STOCK_PATTERN.findall(html)
    out_of_stock_matches = OUT_OF_STOCK_PATTERN.findall(html)

    if not in_stock_matches or not out_of_stock_matches:
        raise RuntimeError(
            "在庫件数のテキストがページから見つかりませんでした。"
            "サイトのHTML構造が変わった可能性があります。"
        )

    # 同じ数字がページ内に複数回(PC表示/モバイル表示など)出現するので最初の値を採用
    in_stock = int(in_stock_matches[0])
    out_of_stock = int(out_of_stock_matches[0])
    return in_stock, out_of_stock


def append_history(timestamp: str, in_stock: int, out_of_stock: int) -> None:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    file_exists = os.path.isfile(DATA_FILE)
    with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp_jst", "in_stock", "out_of_stock", "total"])
        writer.writerow([timestamp, in_stock, out_of_stock, in_stock + out_of_stock])


def notify_discord(timestamp: str, in_stock: int, out_of_stock: int) -> None:
    if not DISCORD_WEBHOOK_URL:
        print("DISCORD_WEBHOOK_URL が設定されていないため通知をスキップしました。", file=sys.stderr)
        return

    total = in_stock + out_of_stock
    content = (
        f"📦 **i-BLOOM 在庫チェック** ({timestamp} JST)\n"
        f"✅ 在庫あり: **{in_stock}**件\n"
        f"❌ 在庫切れ: **{out_of_stock}**件\n"
        f"🔢 合計: {total}件"
    )
    resp = requests.post(DISCORD_WEBHOOK_URL, json={"content": content}, timeout=15)
    resp.raise_for_status()


def main() -> None:
    timestamp = datetime.now(JST).strftime("%Y-%m-%d %H:%M:%S")
    in_stock, out_of_stock = fetch_stock_counts()
    print(f"{timestamp} in_stock={in_stock} out_of_stock={out_of_stock}")

    append_history(timestamp, in_stock, out_of_stock)
    notify_discord(timestamp, in_stock, out_of_stock)


if __name__ == "__main__":
    main()
