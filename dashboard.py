import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ページの設定
st.set_page_config(page_title="Tech Camp 2026 申し込みダッシュボード", layout="wide")

st.title("🎉 Nonpro Camp 2026 申し込みダッシュボード 🚀")
st.markdown("運営チームの皆様、お疲れ様です！このダッシュボードで現在地を確認し、最高目標の**200名**達成に向けてみんなで盛り上がっていきましょう！🔥")

# データの読み込み
@st.cache_data(ttl=600)  # 10分間データをキャッシュ
def load_data():
    url = "https://docs.google.com/spreadsheets/d/11okpDWHaDWemwIJc9pcZx_4GNFNPjp1po03tws1P5oE/export?format=csv&gid=564753256"
    try:
        df = pd.read_csv(url)
        
        # 注文番号が同一、かつチケット名に「イベント参加チケット【無料】」または「投げ銭で応援」と書いてあるレコードを削除
        duplicated_orders = df.duplicated(subset=['注文番号'], keep=False)
        is_free_or_donation = df['チケット名'].str.contains('イベント参加チケット【無料】|投げ銭で応援', na=False)
        to_drop = duplicated_orders & is_free_or_donation
        df = df[~to_drop]
        

        
        # コミュニティ集計用に「属性」から「コミュニティ」列を作成
        if '属性' in df.columns:
            def map_community(attr):
                if pd.isna(attr):
                    return 'その他'
                attr_str = str(attr)
                if attr_str == 'ノンプロ研のメンバー':
                    return 'ノンプロ研'
                elif 'OB' in attr_str or 'OG' in attr_str or '元' in attr_str:
                    return '元ノンプロ研'
                else:
                    return 'その他'
            df['コミュニティ'] = df['属性'].apply(map_community)
            
        return df
    except Exception as e:
        st.error(f"データの読み込みに失敗しました: {e}")
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- ワクワク感の演出とKPIの表示 ---
    # データの最新日付を取得
    if '申込日' in df.columns:
        latest_update = pd.to_datetime(df['申込日'], errors='coerce').max().strftime("%Y-%m-%d")
    else:
        latest_update = "不明"
        
    st.info(f"💡 **応援メッセージ**: 日々の発信お疲れ様です！数字の動きを楽しみながら、みんなでキャンプを大成功させましょう！ (データ最終更新日: {latest_update})")

    # 枚数を数値化して総数を計算
    df['枚数_num'] = pd.to_numeric(df['枚数'], errors='coerce').fillna(0)
    total_tickets = int(df['枚数_num'].sum())
    
    # 目標達成時のエフェクト
    if total_tickets >= 200:
        st.balloons()
        st.markdown(
            """
            <style>
            [data-testid="stBalloons"] div {
                animation-duration: 8s !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        st.success("✨🎉 祝！最大目標の200名を達成しました！運営チームの皆様、本当にお疲れ様です！ 🎉✨")
    elif total_tickets >= 150:
        st.success("🔥 祝！目標の150名をクリア！最大目標の200名まであと少しです！この調子でいきましょう🚀")
    elif total_tickets >= 100:
        st.success("👍 祝！達成目標の100名をクリア！次は目標の150名を目指して頑張りましょう！")
    elif total_tickets >= 50:
        st.info("💪 最低目標の50名に到達！次は達成目標の100名を目指していきましょう！")
    elif total_tickets >= 25:
        st.info("🌱 中間地点の25名を突破！引き続き発信を続けていきましょう！応援しています！")
    else:
        st.warning("🚀 まずは25名を目指して発信を続けましょう！皆さんの力が必要です！")

    # コミュニティ内訳の計算
    nonpro_count = int(df[df['コミュニティ'] == 'ノンプロ研']['枚数_num'].sum())
    ex_nonpro_count = int(df[df['コミュニティ'] == '元ノンプロ研']['枚数_num'].sum())
    other_count = int(df[df['コミュニティ'] == 'その他']['枚数_num'].sum())

    # 懇親会申込者数の集計（チケット名に「懇親会チケット」を含む、かつ会員 IDが重複しないレコード数）
    if '会員 ID' in df.columns and 'チケット名' in df.columns:
        konsin_df = df[df['チケット名'].str.contains('懇親会チケット', na=False)]
        konsin_count = konsin_df['会員 ID'].nunique()
    else:
        konsin_count = 0

    st.subheader("🎯 申込状況")
    col1, col2, col3 = st.columns(3)
    
    progress_150 = min(100.0, round((total_tickets / 150) * 100, 1))
    
    with col1:
        with st.container(border=True):
            st.metric("総申込数", f"{total_tickets} 名")
    with col2:
        with st.container(border=True):
            st.metric("達成率（目標:150名）", f"{progress_150} %")
    with col3:
        with st.container(border=True):
            st.metric("懇親会申込者数", f"{konsin_count} 名")
    
    st.progress(min(total_tickets / 200.0, 1.0))
    st.divider()

    # 日別集計データの作成
    if '申込日' in df.columns:
        df['申込日_dt'] = pd.to_datetime(df['申込日'], errors='coerce')
        df_valid_dates = df.dropna(subset=['申込日_dt']).copy()
        df_valid_dates['日付'] = df_valid_dates['申込日_dt'].dt.date
        daily_counts = df_valid_dates.groupby('日付').size().reset_index(name='申し込み件数')
        daily_counts = daily_counts.sort_values('日付')
        daily_counts['累計申し込み件数'] = daily_counts['申し込み件数'].cumsum()
        
        import altair as alt
        import time

        # ドーナツグラフのプレースホルダー
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            st.markdown("**🎯 購入枚数進捗**")
            goal_ph = st.empty()
        with d_col2:
            st.markdown("**👥 参加者内訳**")
            break_ph = st.empty()

        st.divider()
        st.subheader("📊 申込者数推移")
        chart_ph = st.empty()

        # ======== アニメーション描画 ========
        
        # 1. ドーナツグラフのアニメーション（0からギュイーンと伸びる）
        frames = 20
        for step in range(1, frames + 1):
            curr_tot = int(total_tickets * (step / frames))
            curr_nonpro = int(nonpro_count * (step / frames))
            curr_ex = int(ex_nonpro_count * (step / frames))
            curr_oth = int(other_count * (step / frames))
            
            # Goal Donut
            vis_tot = min(curr_tot, 200)
            val_to_min = max(0, 100 - vis_tot)
            val_to_tgt = max(0, 150 - max(vis_tot, 100))
            val_to_max = max(0, 200 - max(vis_tot, 150))
            g_df = pd.DataFrame({'id':[1,2,3,4], 'カテゴリ':['現在の購入数','100名まで','150名まで','200名まで'], '人数':[vis_tot, val_to_min, val_to_tgt, val_to_max]})
            g_df = g_df[g_df['人数'] > 0]
            g_chart = alt.Chart(g_df).mark_arc(innerRadius=60).encode(
                theta=alt.Theta(field="人数", type="quantitative"),
                color=alt.Color(field="カテゴリ", type="nominal", sort=['現在の購入数','100名まで','150名まで','200名まで'], scale=alt.Scale(domain=['現在の購入数','100名まで','150名まで','200名まで'], range=['#636EFA','#FFD700','#FFB6C1','#D3D3D3']), legend=alt.Legend(title=None, orient="bottom")),
                order=alt.Order(field='id', type='quantitative')
            ).properties(height=300)
            
            # 最低100、目標150、最大200が判別できる閾値ライン
            thresh_df = pd.DataFrame({'id':[1,2,3], '人数':[100, 50, 50]})
            thresh_chart = alt.Chart(thresh_df).mark_arc(innerRadius=60, fillOpacity=0, stroke='#333333', strokeWidth=2).encode(
                theta=alt.Theta(field="人数", type="quantitative"),
                order=alt.Order(field='id', type='quantitative')
            )
            
            text = alt.Chart(pd.DataFrame({'t': [f"{curr_tot}名"]})).mark_text(size=30, fontWeight='bold').encode(text='t')
            goal_ph.altair_chart(g_chart + thresh_chart + text, use_container_width=True)
            
            # Breakdown Donut
            b_df = pd.DataFrame({'id':[1,2,3], 'コミュニティ':['ノンプロ研','元ノンプロ研','その他'], '人数':[curr_nonpro, curr_ex, curr_oth]})
            # 0だと表示が崩れるのを防ぐ
            if b_df['人数'].sum() > 0:
                b_chart = alt.Chart(b_df).mark_arc(innerRadius=60).encode(
                    theta=alt.Theta(field="人数", type="quantitative"),
                    color=alt.Color(field="コミュニティ", type="nominal", sort=['ノンプロ研','元ノンプロ研','その他'], scale=alt.Scale(domain=['ノンプロ研','元ノンプロ研','その他'], range=['#00C49F','#FFBB28','#FF8042']), legend=alt.Legend(title=None, orient="bottom")),
                    order=alt.Order(field='id', type='quantitative')
                ).properties(height=300)
                break_ph.altair_chart(b_chart, use_container_width=True)
            
            time.sleep(0.01)

        # 2. グラフのアニメーション（棒グラフは下から上へ、折れ線は左から右へ描画）
        num_days = len(daily_counts)
        
        # グラフの枠組み（軸）を最初から固定表示するため、スケール用の最大・最小値を計算
        min_date = "2026-05-08"
        max_date = "2026-07-04"
        max_bar_y = float(daily_counts['申し込み件数'].max()) * 1.1 if not daily_counts.empty else 10.0
        max_line_y = float(max(200, daily_counts['累計申し込み件数'].max() if not daily_counts.empty else 0)) * 1.1

        # 7日間おきの区切り線データ
        dividers = pd.date_range(start=min_date, end=max_date, freq='7D')
        div_df = pd.DataFrame({'日付': dividers})

        for i in range(1, num_days + 1):
            # 折れ線グラフ用：左から右へ徐々にデータが増える
            line_data = daily_counts.iloc[:i].copy()
            
            # 棒グラフ用：全日付を表示し、高さを下から上へ伸ばす（i / num_days の割合で高さを計算）
            bar_data = daily_counts.copy()
            progress_ratio = i / num_days
            bar_data['表示用申し込み件数'] = bar_data['申し込み件数'] * progress_ratio
            
            # X軸のスケールを固定したベースチャート
            base_line = alt.Chart(line_data).encode(
                x=alt.X('日付:T', title='日付', scale=alt.Scale(domain=[min_date, max_date]))
            )
            base_bar = alt.Chart(bar_data).encode(
                x=alt.X('日付:T', title='日付', scale=alt.Scale(domain=[min_date, max_date]))
            )
            
            # Y軸のスケールも固定してガタツキを防ぐ
            bar = base_bar.mark_bar(color='#636EFA', opacity=0.8).encode(
                y=alt.Y('表示用申し込み件数:Q', title='日別申し込み件数（件）', scale=alt.Scale(domain=[0, max_bar_y]))
            )
            line = base_line.mark_line(color='#EF553B', strokeWidth=4).encode(
                y=alt.Y('累計申し込み件数:Q', title='累計申し込み件数（件）', scale=alt.Scale(domain=[0, max_line_y]))
            )
            
            # 目標ライン (中間25, 最低50, 達成100, 目標150, 最大200)
            rule_25  = alt.Chart(pd.DataFrame({'y': [25]})).mark_rule(color='#AAAAAA', strokeDash=[4, 4]).encode(y='y')
            rule_50  = alt.Chart(pd.DataFrame({'y': [50]})).mark_rule(color='#FF8C00', strokeDash=[5, 5]).encode(y='y')
            rule_100 = alt.Chart(pd.DataFrame({'y': [100]})).mark_rule(color='#1E90FF', strokeDash=[5, 5]).encode(y='y')
            rule_150 = alt.Chart(pd.DataFrame({'y': [150]})).mark_rule(color='#32CD32', strokeDash=[5, 5]).encode(y='y')
            rule_200 = alt.Chart(pd.DataFrame({'y': [200]})).mark_rule(color='#FF3333', strokeDash=[5, 5]).encode(y='y')

            # ラインのラベル（fontSize=15で見やすく）
            text_25  = alt.Chart(pd.DataFrame({'y': [25],  'text': ['中間:25名']})).mark_text(align='left', baseline='bottom', color='#888888', dx=5, dy=-3, fontSize=15, fontWeight='bold').encode(y='y', text='text')
            text_50  = alt.Chart(pd.DataFrame({'y': [50],  'text': ['最低:50名']})).mark_text(align='left', baseline='bottom', color='#FF8C00', dx=5, dy=-3, fontSize=15, fontWeight='bold').encode(y='y', text='text')
            text_100 = alt.Chart(pd.DataFrame({'y': [100], 'text': ['達成:100名']})).mark_text(align='left', baseline='bottom', color='#1E90FF', dx=5, dy=-3, fontSize=15, fontWeight='bold').encode(y='y', text='text')
            text_150 = alt.Chart(pd.DataFrame({'y': [150], 'text': ['目標:150名']})).mark_text(align='left', baseline='bottom', color='#32CD32', dx=5, dy=-3, fontSize=15, fontWeight='bold').encode(y='y', text='text')
            text_200 = alt.Chart(pd.DataFrame({'y': [200], 'text': ['最大:200名']})).mark_text(align='left', baseline='bottom', color='#FF3333', dx=5, dy=-3, fontSize=15, fontWeight='bold').encode(y='y', text='text')

            # 7日おきの区切り線
            rule_div = alt.Chart(div_df).mark_rule(color='gray', strokeDash=[2, 2], opacity=0.5).encode(x='日付:T')

            all_rules = rule_25 + text_25 + rule_50 + text_50 + rule_100 + text_100 + rule_150 + text_150 + rule_200 + text_200 + rule_div
            layered = alt.layer(bar, line + all_rules).resolve_scale(y='independent')
            chart_ph.altair_chart(layered, use_container_width=True)
            time.sleep(0.05)
        
        # 集計結果テーブルをアコーディオンで隠す
        with st.expander("集計結果テーブルを表示"):
            st.dataframe(daily_counts.set_index('日付'))
        
    else:
        st.error("データ内に「申込日」という列が見つかりません。列名を確認してください。")
else:
    st.info("データが読み込めていません。スプレッドシートの権限設定などを確認してください。")
