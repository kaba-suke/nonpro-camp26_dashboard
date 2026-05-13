import pandas as pd
url = "https://docs.google.com/spreadsheets/d/11okpDWHaDWemwIJc9pcZx_4GNFNPjp1po03tws1P5oE/export?format=csv&gid=564753256"
df = pd.read_csv(url)
print("属性 uniques:", df['属性'].unique())
col_name = "参加者の皆さまに合わせたサポートを行うため、ノンプロ研との関わりについて差し支えない範囲で教えてください。"
print("関わり uniques:", df[col_name].unique())
