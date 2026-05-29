import pandas as pd
url = 'https://docs.google.com/spreadsheets/d/11okpDWHaDWemwIJc9pcZx_4GNFNPjp1po03tws1P5oE/export?format=csv&gid=564753256'
df = pd.read_csv(url)

# Print current calculation
is_donation = df['チケット名'].str.contains('投げ銭で応援', na=False)
duplicated_orders = df.duplicated(subset=['注文番号'], keep=False)
is_free = df['チケット名'].str.contains('イベント参加チケット【無料】', na=False)
is_duplicated_free = duplicated_orders & is_free
to_drop = is_donation | is_duplicated_free
df_orig = df[~to_drop]
total = pd.to_numeric(df_orig['枚数'], errors='coerce').fillna(0).sum()
print('Original total:', total)

# Let's see what is dropped
print('\nDropped free tickets:')
print(df[is_duplicated_free][['注文番号', 'チケット名', '枚数']])

print('\nAll rows for duplicated orders:')
dupe_orders = df[is_duplicated_free]['注文番号'].unique()
for order in dupe_orders:
    print('---', order)
    print(df[df['注文番号'] == order][['チケット名', '枚数']])
