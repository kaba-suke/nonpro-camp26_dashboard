import pandas as pd
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

url = "https://docs.google.com/spreadsheets/d/11okpDWHaDWemwIJc9pcZx_4GNFNPjp1po03tws1P5oE/export?format=csv&gid=564753256"
df = pd.read_csv(url)

print("Columns:", list(df.columns))

df['枚数_num'] = pd.to_numeric(df['枚数'], errors='coerce').fillna(0)
print("Raw Total Tickets:", df['枚数_num'].sum())

# 現在のダッシュボードのロジック
duplicated_orders = df.duplicated(subset=['注文番号'], keep=False)
is_free_or_donation = df['チケット名'].str.contains('イベント参加チケット【無料】|投げ銭で応援', na=False)
to_drop_current = duplicated_orders & is_free_or_donation
df_current = df[~to_drop_current]
print("Current Dashboard Total Tickets:", df_current['枚数_num'].sum())

# 本来あるべきロジック？（単独の無料・投げ銭もすべて削除する？）
# 懇親会チケットは含める？
# もし全ての無料・投げ銭チケットを削除した場合
to_drop_all_free = is_free_or_donation
df_all_free_dropped = df[~to_drop_all_free]
print("Total Tickets if ALL free/donation are dropped:", df_all_free_dropped['枚数_num'].sum())

# 差分（単独で無料・投げ銭を申し込んだ人）
diff_df = df_current[df_current['チケット名'].str.contains('イベント参加チケット【無料】|投げ銭で応援', na=False)]
print("Tickets kept in dashboard that are free/donation (single orders):")
print(diff_df[['注文番号', 'チケット名', '枚数']])
