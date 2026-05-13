# -*- coding: utf-8 -*-
"""
export_data.py
--------------
クレンジング後のデータをCSVに出力する確認用スクリプト。
Streamlitなしで単独実行できます。

実行方法:
    .venv\Scripts\python.exe export_data.py
"""

import pandas as pd

# ===== データ読み込み =====
url = "https://docs.google.com/spreadsheets/d/11okpDWHaDWemwIJc9pcZx_4GNFNPjp1po03tws1P5oE/export?format=csv&gid=564753256"

print("データを読み込み中...")
df = pd.read_csv(url)
print(f"  読み込み完了: {len(df)} 行")

# ===== クレンジング =====
# 注文番号が同一、かつチケット名に「イベント参加チケット【無料】」または「投げ銭で応援」が含まれるレコードを削除
duplicated_orders = df.duplicated(subset=['注文番号'], keep=False)
is_free_or_donation = df['チケット名'].str.contains('イベント参加チケット【無料】|投げ銭で応援', na=False)
to_drop = duplicated_orders & is_free_or_donation
df = df[~to_drop]
print(f"  クレンジング後: {len(df)} 行（{to_drop.sum()} 行を除外）")

# ===== CSV出力 =====
output_path = "csdata.csv"
df.to_csv(output_path, index=False, encoding="utf-8-sig")
print(f"\n[完了] 出力完了: {output_path}")
print(f"   行数: {len(df)}, 列数: {len(df.columns)}")
print("\n[列名一覧]")
for col in df.columns:
    print(f"   - {col}")
