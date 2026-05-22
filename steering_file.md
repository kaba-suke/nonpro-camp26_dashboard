# Dashboard Development Steering File

## 1. Project Goal
イベント「26.05ブートキャンプ」の申込状況をリアルタイムで可視化し、運営メンバー全員が「現在地」を把握して、目標達成に向けた施策（集客・フォローアップ）を迅速に行えるようにする。

## 2. Background & Objectives (Based on Worksheet)
- **現状の課題**: 申込状況が属人化していたり、確認に手間がかかる状態を解消したい。
- **期待する効果**:
    - 数字の透明化による運営メンバーの士気向上。
    - 最大目標200名に対する進捗率の明確化。
    - 最低目標150名に対する進捗率の明確化。
    - 日次推移を追うことで、広告や告知の反応を分析可能にする。

## 3. Core Features (Must-Have)
- **KPI Metrics**: 
    - 総申込数 (Total Registrations)
    - 目標達成率 (%)
    - 残り枠数 (Remaining Slots)
- **Visualizations**:
    - 日別申込推移グラフ (Line Chart: Daily trend)
    - 累計申込推移グラフ (Area Chart: Cumulative growth towards 200)
- **Interactivity**:
    - データの更新日時表示
    - 運営メンバーへの応援メッセージ（イラスト・テキスト）

## 4. Technical Specifications
- **Tool Stack**: Python, Streamlit
- **Data Source**: Google Sheets (Linked to Google Forms)
- **Environment**: Antigravity (Development) -> Streamlit Community Cloud (Production)
- **UI Design**: 
    - 直感的にわかる大きな数字。
    - イベントの雰囲気に合わせた明るいデザイン。

## 5. Deployment & Sharing
- **Access**: URLを知っている運営メンバーがブラウザから閲覧。
- **Cost**: 0円（Streamlit Community Cloud / Free tier）。
- **Security**: 簡易パスワードによる保護の実装。

## 6. Success Metrics
- 運営メンバー全員が毎日1回以上ダッシュボードを確認している状態。
- ダッシュボードの数値を元にした改善策が運営会議で提案されること。
