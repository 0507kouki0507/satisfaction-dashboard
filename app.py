"""メインアプリ・ページルーティング"""

import pandas as pd
import streamlit as st

from auth import setup_authenticator, show_login_page, show_logout_button
from charts import bar_chart_project_comparison, histogram_score_distribution, line_chart_monthly_trend
from data import filter_data, get_nps_score, get_response_rate, load_all_data, _is_demo_mode


st.set_page_config(
    page_title="顧客満足度ダッシュボード",
    page_icon="📊",
    layout="wide",
)


def show_kpi_cards(df: pd.DataFrame) -> None:
    col1, col2, col3, col4 = st.columns(4)

    avg_score = df["score"].mean()
    median_score = df["score"].median()
    response_rate = get_response_rate(df)
    nps = get_nps_score(df)

    with col1:
        st.metric(
            label="平均スコア",
            value=f"{avg_score:.2f}" if not pd.isna(avg_score) else "—",
            help="1〜5点スケール",
        )
    with col2:
        st.metric(
            label="中央値スコア",
            value=f"{median_score:.2f}" if not pd.isna(median_score) else "—",
        )
    with col3:
        st.metric(
            label="回答率",
            value=f"{response_rate:.1f}%" if response_rate > 0 else "—",
            help="回答者数 ÷ 受講生数",
        )
    with col4:
        st.metric(
            label="NPS スコア",
            value=f"{nps:.1f}" if nps is not None else "—",
            help="推薦者割合(%) - 批判者割合(%)",
        )


def show_comments(df: pd.DataFrame) -> None:
    st.subheader("コメント一覧")
    comments = df[["date", "project_name", "comment"]].dropna(subset=["comment"])
    comments = comments[comments["comment"].astype(str).str.strip() != ""]

    if comments.empty:
        st.info("表示できるコメントがありません")
        return

    comments = comments.sort_values("date", ascending=False).reset_index(drop=True)
    for _, row in comments.iterrows():
        date_str = row["date"].strftime("%Y-%m-%d") if pd.notna(row["date"]) else ""
        with st.expander(f"[{row['project_name']}] {date_str}"):
            st.write(row["comment"])


def show_dashboard(name: str) -> None:
    authenticator, _ = setup_authenticator()

    with st.sidebar:
        st.title("📊 満足度 Dashboard")
        st.write(f"ようこそ、**{name}** さん")
        show_logout_button(authenticator)
        st.divider()

        # データ読み込み
        with st.spinner("データを読み込み中..."):
            df = load_all_data()
            if _is_demo_mode():
                st.info("デモモード: サンプルデータを表示しています。Google Sheets を設定すると実データに切り替わります。", icon="ℹ️")

        if df.empty:
            st.error("データが取得できませんでした。Google Sheets の設定を確認してください。")
            return

        # フィルター: PJ選択
        all_projects = sorted(df["project_name"].dropna().unique().tolist())
        selected_projects = st.multiselect(
            "プロジェクト",
            options=all_projects,
            default=all_projects,
            placeholder="すべて選択",
        )

        # フィルター: 月選択
        all_months = sorted(df["date"].dt.strftime("%Y-%m").unique().tolist(), reverse=True)
        selected_months = st.multiselect(
            "月",
            options=all_months,
            default=all_months[:6] if len(all_months) >= 6 else all_months,
            placeholder="すべて選択",
        )

        st.caption("⏱ データは5分ごとに自動更新されます")

    # フィルター適用
    filtered_df = filter_data(
        df,
        projects=selected_projects if selected_projects else None,
        months=selected_months if selected_months else None,
    )

    st.title("顧客満足度ダッシュボード")

    if filtered_df.empty:
        st.warning("選択した条件に一致するデータがありません")
        return

    # KPI カード
    st.subheader("KPI サマリー")
    show_kpi_cards(filtered_df)

    st.divider()

    # グラフ
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.plotly_chart(line_chart_monthly_trend(filtered_df), use_container_width=True)
    with col_right:
        st.plotly_chart(histogram_score_distribution(filtered_df), use_container_width=True)

    st.plotly_chart(bar_chart_project_comparison(filtered_df), use_container_width=True)

    st.divider()

    # コメント一覧
    show_comments(filtered_df)


def main() -> None:
    # 認証チェック
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = None

    name, authentication_status, username = show_login_page()

    if authentication_status:
        show_dashboard(name)
    elif authentication_status is False:
        st.stop()
    else:
        st.stop()


if __name__ == "__main__":
    main()
