import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
import os
from pathlib import Path

# ページの設定
st.set_page_config(page_title="Tech Camp 2026 申し込みダッシュボード", layout="wide")

# 背景画像を Base64 エンコードして読み込む（パスが見つからない場合はフォールバック）
def _get_b64_image(path) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

_hero_img_b64 = ""
try:
    # pathlib で確実にパスを解決する（dashboard.py と同じフォルダに画像を配置）
    _hero_img_path = Path(__file__).resolve().parent / "ノンプロキャンプ2026ロゴ_main_title.png"
    if _hero_img_path.exists():
        _hero_img_b64 = _get_b64_image(_hero_img_path)
    else:
        st.warning(f"背景画像が見つかりません: {_hero_img_path}")
except Exception as _e:
    st.warning(f"背景画像の読み込みに失敗しました: {_e}")

# データの読み込み
@st.cache_data(ttl=600)  # 10分間データをキャッシュ
def load_data():
    url = "https://docs.google.com/spreadsheets/d/11okpDWHaDWemwIJc9pcZx_4GNFNPjp1po03tws1P5oE/export?format=csv&gid=564753256"
    try:
        df = pd.read_csv(url)
        
        # 「投げ銭で応援」は参加枠ではないため、無条件で除外する
        is_donation = df['チケット名'].str.contains('投げ銭で応援', na=False)
        df = df[~is_donation]
        
        # 注文番号が同一（他のチケットと同時購入）、かつ「イベント参加チケット【無料】」のレコードを除外（人数を重複カウントしないため）
        duplicated_orders = df.duplicated(subset=['注文番号'], keep=False)
        is_free = df['チケット名'].str.contains('イベント参加チケット【無料】', na=False)
        
        # 削除条件を適用して除外
        df = df[~(duplicated_orders & is_free)]

        
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
    # --- データの最新日付を取得 ---
    if '申込日' in df.columns:
        latest_update = pd.to_datetime(df['申込日'], errors='coerce').max().strftime("%Y-%m-%d")
    else:
        latest_update = "不明"

    # 枚数を数値化して総数を計算
    df['枚数_num'] = pd.to_numeric(df['枚数'], errors='coerce').fillna(0)
    actual_total_tickets = int(df['枚数_num'].sum())

    # --- デバッグモード (本番では非表示にするためコメントアウト) ---
    # st.sidebar.markdown("---")
    # st.sidebar.subheader("🛠 デバッグモード")
    # use_debug = st.sidebar.checkbox("チケット枚数を手動でテストする")
    # if use_debug:
    #     total_tickets = st.sidebar.slider("テスト用チケット枚数", 0, 250, 100)
    # else:
    #     total_tickets = actual_total_tickets

    # 本番用: 実際のチケット枚数をそのまま使用
    total_tickets = actual_total_tickets

    # ---- ヒーローセクション用: ミルストーンメッセージの内容を決定 ----
    if total_tickets >= 200:
        milestone_bg   = "rgba(0, 160, 80, 0.82)"
        milestone_left = "#00c864"
        milestone_msg  = "✨🎉 祝！最大目標の200名を達成しました！運営チームの皆様、本当にお疲れ様です！ 🎉✨"
    elif total_tickets >= 150:
        milestone_bg   = "rgba(0, 160, 80, 0.82)"
        milestone_left = "#00c864"
        milestone_msg  = "🔥 祝！目標の150名をクリア！最大目標の200名まであと少しです！この調子でいきましょう🚀"
    elif total_tickets >= 100:
        milestone_bg   = "rgba(0, 160, 80, 0.82)"
        milestone_left = "#00c864"
        milestone_msg  = "👍 祝！達成目標の100名をクリア！次は目標の150名を目指して頑張りましょう！"
    elif total_tickets >= 50:
        milestone_bg   = "rgba(0, 90, 200, 0.80)"
        milestone_left = "#3399ff"
        milestone_msg  = "💪 最低目標の50名に到達！次は達成目標の100名を目指していきましょう！"
    elif total_tickets >= 25:
        milestone_bg   = "rgba(0, 90, 200, 0.80)"
        milestone_left = "#3399ff"
        milestone_msg  = "🌱 中間地点の25名を突破！引き続き発信を続けていきましょう！応援しています！"
    else:
        milestone_bg   = "rgba(180, 110, 0, 0.82)"
        milestone_left = "#f0a500"
        milestone_msg  = "🚀 まずは25名を目指して発信を続けましょう！皆さんの力が必要です！"

    # ---- ヒーローセクション: タイトル〜中間地点メッセージを背景画像付きで一括表示 ----
    st.markdown(f"""
    <style>
    .hero-section {{
        background-color: #ffffff; /* 画像の背景に馴染むように白色ベースに設定 */
        background-image: url("data:image/png;base64,{_hero_img_b64}");
        background-size: contain; /* 画像全体が枠内に収まるように変更 */
        background-position: center; /* 中央に配置 */
        background-repeat: no-repeat;
        border-radius: 14px;
        padding: 44px 52px;
        margin-bottom: 20px;
        position: relative;
    }}
    .hero-section::before {{
        content: '';
        position: absolute;
        inset: 0;
        background: rgba(255, 255, 255, 0.4); /* 文字が読みやすいように白のオーバーレイを少し濃く調整 */
        border-radius: 14px;
        z-index: 0;
    }}
    .hero-content {{
        position: relative;
        z-index: 1;
    }}
    .hero-title {{
        font-size: 2.1em;
        font-weight: bold;
        color: #003d7a;
        text-shadow: 0 1px 4px rgba(255,255,255,0.9), 0 0 12px rgba(255,255,255,0.7);
        margin: 0 0 14px 0;
    }}
    .hero-desc {{
        font-size: 1.05em;
        color: #003060;
        background: rgba(255,255,255,0.60);
        border-radius: 8px;
        padding: 10px 16px;
        margin-bottom: 12px;
        line-height: 1.7;
    }}
    .hero-cheering {{
        background: rgba(0, 80, 180, 0.78);
        border-left: 4px solid #66b3ff;
        border-radius: 8px;
        padding: 12px 18px;
        color: #ffffff;
        font-size: 1em;
        margin-bottom: 12px;
        text-shadow: 0 1px 3px rgba(0,0,0,0.5);
    }}
    .hero-milestone {{
        background: {milestone_bg};
        border-left: 5px solid {milestone_left};
        border-radius: 8px;
        padding: 13px 18px;
        color: #ffffff;
        font-size: 1.05em;
        font-weight: bold;
        text-shadow: 0 1px 3px rgba(0,0,0,0.5);
    }}
    </style>
    <div class="hero-section">
        <div class="hero-content">
            <div class="hero-title">🎉 Nonpro Camp 2026 申し込みダッシュボード 🚀</div>
            <div class="hero-desc">運営チームの皆様、お疲れ様です！このダッシュボードで現在地を確認し、最高目標の<strong>200名</strong>達成に向けてみんなで盛り上がっていきましょう！🔥</div>
            <div class="hero-cheering">💡 <strong>応援メッセージ</strong>: 日々の発信お疲れ様です！数字の動きを楽しみながら、みんなでキャンプを大成功させましょう！（データ最終更新日: {latest_update}）</div>
            <div class="hero-milestone">{milestone_msg}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---- 目標達成時のアニメーション演出（テキストはヒーローセクションに統合済み） ----
    if total_tickets >= 200:
        # 200名: 花丸をつける
        st.markdown(
            """
            <style>
            .hanamaru-container {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                z-index: 99999;
                pointer-events: none;
                animation: pop-hanamaru 6s ease-out forwards;
            }
            @keyframes pop-hanamaru {
                0% { opacity: 0; transform: translate(-50%, -50%) scale(0.1) rotate(-90deg); }
                15% { opacity: 1; transform: translate(-50%, -50%) scale(1.2) rotate(10deg); }
                30% { opacity: 1; transform: translate(-50%, -50%) scale(1) rotate(0deg); }
                85% { opacity: 1; transform: translate(-50%, -50%) scale(1) rotate(0deg); }
                100% { opacity: 0; transform: translate(-50%, -50%) scale(1.5) rotate(0deg); visibility: hidden; }
            }
            </style>
            <div class="hanamaru-container">
                <span style="font-size: 400px; line-height: 1; text-shadow: 0px 10px 30px rgba(0,0,0,0.3);">💮</span>
            </div>
            """,
            unsafe_allow_html=True
        )
    elif total_tickets >= 150:
        # 150名: バルーンを飛ばす
        st.balloons()
        st.markdown(
            """
            <style>
            [data-testid="stBalloons"] div {
                animation-duration: 24s !important; /* スピードを1/3にするため時間を3倍に */
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    elif total_tickets >= 100:
        # 100名: 花火を打ち上げる
        st.markdown(
            """
            <style>
            .firework-container {
                position: fixed;
                bottom: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                pointer-events: none;
                z-index: 99999;
                overflow: hidden;
            }
            .firework {
                position: absolute;
                bottom: -200px;
                background-color: transparent !important; /* 背景色なし */
                animation: shoot-firework 5s ease-out forwards;
            }
            .fw-1 { left: 15%; animation-delay: 0s; font-size: 200px; }
            .fw-2 { left: 45%; animation-delay: 1.5s; font-size: 320px; }
            .fw-3 { left: 80%; animation-delay: 0.5s; font-size: 240px; }
            .fw-4 { left: 30%; animation-delay: 2.5s; font-size: 220px; }
            .fw-5 { left: 65%; animation-delay: 3s; font-size: 280px; }

            @keyframes shoot-firework {
                0% { transform: translateY(0) scale(0.5); opacity: 1; }
                40% { transform: translateY(-50vh) scale(1); opacity: 1; }
                70% { transform: translateY(-60vh) scale(1.5); opacity: 0; }
                100% { transform: translateY(-60vh) scale(2); opacity: 0; visibility: hidden; }
            }
            </style>
            <div class="firework-container">
                <div class="firework fw-1">🎆</div>
                <div class="firework fw-2">🎆</div>
                <div class="firework fw-3">🎆</div>
                <div class="firework fw-4">🎆</div>
                <div class="firework fw-5">🎆</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    elif total_tickets >= 50:
        # 50名: 波を立てる
        st.markdown(
            """
            <style>
            .wave-container {
                position: fixed;
                bottom: 0;
                left: 0;
                width: 100vw;
                height: 70vh; /* 大波にするため高さを上げる */
                overflow: hidden;
                pointer-events: none;
                z-index: 99999;
                /* 波が下から押し寄せて、最後に引いていくアニメーション (半分の時間に短縮) */
                animation: fade-out-wave 6s forwards;
            }
            .wave {
                position: absolute;
                bottom: 0;
                left: 0;
                width: 300vw;
                height: 100%;
                /* 少し荒々しい波の形 */
                background: url('data:image/svg+xml;utf8,<svg viewBox="0 0 1440 320" xmlns="http://www.w3.org/2000/svg"><path fill="%230099ff" fill-opacity="0.6" d="M0,192L48,181.3C96,171,192,149,288,160C384,171,480,213,576,224C672,235,768,213,864,181.3C960,149,1056,107,1152,112C1248,117,1344,171,1392,197.3L1440,224L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"></path></svg>');
                background-size: 33.33% 100%;
                /* スピードを倍に(時間は半分: 4秒) */
                animation: move-wave-left 4s linear 2 forwards;
            }
            .wave-2 {
                bottom: -20px;
                opacity: 0.4;
                /* 後ろの波も時間は半分(6秒) */
                animation: move-wave-left 6s linear 1 forwards reverse;
            }
            @keyframes move-wave-left {
                0% { transform: translateX(0); }
                100% { transform: translateX(-33.33%); }
            }
            @keyframes fade-out-wave {
                0% { opacity: 0; transform: translateY(30vh); }
                10% { opacity: 1; transform: translateY(0); }
                80% { opacity: 1; transform: translateY(0); }
                100% { opacity: 0; transform: translateY(30vh); visibility: hidden; }
            }
            </style>
            <div class="wave-container">
                <div class="wave"></div>
                <div class="wave wave-2"></div>
            </div>
            """,
            unsafe_allow_html=True
        )

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

        # ドーナツグラフと画像を配置するためのカラム（比率で画像サイズを元の約75%に調整）
        d_col1, d_col_img, d_col2 = st.columns([4.5, 1, 4.5])
        
        with d_col1:
            st.markdown("**🎯 購入枚数進捗**")
            goal_ph = st.empty()
            
        with d_col_img:
            # グラフの縦方向の中央付近に配置するため、少し余白を入れる
            for _ in range(5):
                st.write("")
                
            # pngとwebpの両方に対応
            _avatar_path = Path(__file__).resolve().parent / "avatar.png"
            _avatar_path_webp = Path(__file__).resolve().parent / "avatar.webp"
            
            if _avatar_path.exists():
                st.image(str(_avatar_path), use_container_width=True)
            elif _avatar_path_webp.exists():
                st.image(str(_avatar_path_webp), use_container_width=True)
            else:
                st.caption("※ここに画像が入ります")
                
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
            
            text = alt.Chart(pd.DataFrame({'t': [f"{curr_tot}名"]})).mark_text(size=30, fontWeight='bold', color='#4A90D9').encode(text='t')
            goal_ph.altair_chart(g_chart + thresh_chart + text, use_container_width=True)
            
            # Breakdown Donut
            b_df = pd.DataFrame({'id':[1,2,3], 'コミュニティ':['ノンプロ研','元ノンプロ研','その他'], '人数':[curr_nonpro, curr_ex, curr_oth]})
            # 0だと表示が崩れるのを防ぐ
            if b_df['人数'].sum() > 0:
                b_base = alt.Chart(b_df).encode(
                    theta=alt.Theta(field="人数", type="quantitative", stack=True),
                    color=alt.Color(field="コミュニティ", type="nominal", sort=['ノンプロ研','元ノンプロ研','その他'], scale=alt.Scale(domain=['ノンプロ研','元ノンプロ研','その他'], range=['#00C49F','#FFBB28','#FF8042']), legend=alt.Legend(title=None, orient="bottom")),
                    order=alt.Order(field='id', type='quantitative')
                )
                b_arc = b_base.mark_arc(innerRadius=60)
                # 各セグメントの人数ラベルをグラフ内部に表示（0名のセグメントは非表示）
                b_label_df = b_df[b_df['人数'] > 0].copy()
                b_label_base = alt.Chart(b_label_df).encode(
                    theta=alt.Theta(field="人数", type="quantitative", stack=True),
                    order=alt.Order(field='id', type='quantitative')
                )
                b_label = b_label_base.mark_text(radius=100, size=15, fontWeight='bold', color='white').encode(
                    text=alt.Text(field="人数", type="quantitative", format=".0f")
                )
                b_chart = (b_arc + b_label).properties(height=300)
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
            
        st.divider()
        # バナー画像を中央に、画面幅の半分程度で表示する
        _banner_path = Path(__file__).resolve().parent / "banner.png"
        _banner_path_webp = Path(__file__).resolve().parent / "banner.webp"
        
        # 左右に空白のカラムを配置して中央に寄せる（比率 1:2:1 ＝ 画像が50%）
        b_spacer1, b_img_col, b_spacer2 = st.columns([1, 2, 1])
        
        with b_img_col:
            if _banner_path.exists():
                st.image(str(_banner_path), use_container_width=True)
            elif _banner_path_webp.exists():
                st.image(str(_banner_path_webp), use_container_width=True)
            else:
                st.caption("※ここにバナー画像が入ります")
        
        # 集計結果テーブルをアコーディオンで隠す
        with st.expander("集計結果テーブルを表示"):
            st.dataframe(daily_counts.set_index('日付'))
        
    else:
        st.error("データ内に「申込日」という列が見つかりません。列名を確認してください。")
else:
    st.info("データが読み込めていません。スプレッドシートの権限設定などを確認してください。")
