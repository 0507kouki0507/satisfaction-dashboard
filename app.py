"""メインアプリ・ページルーティング"""

import pandas as pd
import streamlit as st

from auth import setup_authenticator, show_login_page, show_logout_button
from charts import (
    bar_chart_project_comparison,
    histogram_score_distribution,
    histogram_self_effort_distribution,
    line_chart_monthly_trend,
    line_chart_self_effort_trend,
)
from data import _is_demo_mode, filter_data, get_nps_score, get_response_rate, load_all_data


st.set_page_config(
    page_title="顧客満足度ダッシュボード",
    page_icon="📊",
    layout="wide",
)

_CSS = """
<style>
/* ---------- 全体 ---------- */
[data-testid="stAppViewContainer"] {
    background: #F8FAFC;
}
[data-testid="stHeader"] {
    background: transparent;
}

/* ---------- サイドバー ---------- */
[data-testid="stSidebar"] {
    background: #0F172A;
    border-right: none;
}
[data-testid="stSidebar"] * {
    color: #CBD5E1 !important;
}
[data-testid="stSidebar"] .stMultiSelect span {
    background: #1E293B !important;
    color: #94A3B8 !important;
}
[data-testid="stSidebar"] hr {
    border-color: #1E293B;
}
[data-testid="stSidebar"] [data-testid="stButton"] button {
    background: #1E293B;
    border: 1px solid #334155;
    color: #94A3B8 !important;
    border-radius: 6px;
    width: 100%;
}
[data-testid="stSidebar"] [data-testid="stButton"] button:hover {
    border-color: #4F46E5;
    color: #E2E8F0 !important;
}

/* ---------- KPI カード ---------- */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 14px;
    margin-bottom: 8px;
}
.kpi-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 20px 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    border-top: 3px solid var(--accent);
    transition: box-shadow .2s;
}
.kpi-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.kpi-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: .06em;
    text-transform: uppercase;
    color: #94A3B8;
    margin-bottom: 8px;
}
.kpi-value {
    font-size: 32px;
    font-weight: 700;
    color: #0F172A;
    line-height: 1;
}
.kpi-sub {
    font-size: 11px;
    color: #94A3B8;
    margin-top: 6px;
}

/* ---------- セクションヘッダー ---------- */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 32px 0 16px;
}
.section-header-bar {
    width: 4px;
    height: 22px;
    border-radius: 2px;
    background: var(--bar-color, #4F46E5);
    flex-shrink: 0;
}
.section-header-text {
    font-size: 17px;
    font-weight: 700;
    color: #1E293B;
}
.section-header-sub {
    font-size: 12px;
    color: #94A3B8;
    margin-left: auto;
}

/* ---------- コメントカード ---------- */
.comment-card {
    background: #FFFFFF;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    border-left: 3px solid #4F46E5;
}
.comment-meta {
    font-size: 11px;
    color: #94A3B8;
    margin-bottom: 6px;
    display: flex;
    gap: 12px;
}
.comment-badge {
    background: #EEF2FF;
    color: #4F46E5;
    padding: 1px 8px;
    border-radius: 20px;
    font-weight: 600;
}
.comment-text {
    font-size: 14px;
    color: #334155;
    line-height: 1.6;
}

/* ---------- ページタイトル ---------- */
.page-title {
    font-size: 26px;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 2px;
}
.page-subtitle {
    font-size: 13px;
    color: #94A3B8;
    margin-bottom: 28px;
}

/* ---------- デモバナー ---------- */
.demo-banner {
    background: linear-gradient(135deg, #EEF2FF, #E0F2FE);
    border: 1px solid #C7D2FE;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 11px;
    color: #4338CA;
    margin-bottom: 12px;
}

/* ---------- グラフコンテナ ---------- */
[data-testid="stPlotlyChart"] {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}

/* ---------- divider ---------- */
hr {
    border-color: #E2E8F0 !important;
    margin: 24px 0 !important;
}
</style>
"""


def _section_header(title: str, subtitle: str = "", color: str = "#4F46E5") -> None:
    sub_html = f'<span class="section-header-sub">{subtitle}</span>' if subtitle else ""
    st.markdown(
        f"""
        <div class="section-header">
            <div class="section-header-bar" style="background:{color}"></div>
            <span class="section-header-text">{title}</span>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _kpi_card(label: str, value: str, sub: str = "", accent: str = "#4F46E5") -> str:
    return f"""
    <div class="kpi-card" style="--accent:{accent}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {f'<div class="kpi-sub">{sub}</div>' if sub else ""}
    </div>
    """


def show_kpi_cards(df: pd.DataFrame) -> None:
    avg_score = df["score"].mean()
    median_score = df["score"].median()
    avg_effort = df["self_effort_score"].mean()
    response_rate = get_response_rate(df)
    nps = get_nps_score(df)

    cards = (
        _kpi_card("平均満足度スコア", f"{avg_score:.1f}" if not pd.isna(avg_score) else "—", "1〜10点スケール", "#4F46E5")
        + _kpi_card("中央値スコア", f"{median_score:.1f}" if not pd.isna(median_score) else "—", "1〜10点スケール", "#6366F1")
        + _kpi_card("自身の取り組み", f"{avg_effort:.1f}" if not pd.isna(avg_effort) else "—", "1〜100点スケール", "#06B6D4")
        + _kpi_card("回答率", f"{response_rate:.1f}%" if response_rate > 0 else "—", "回答者 ÷ 受講生", "#10B981")
        + _kpi_card("NPS スコア", f"{nps:.1f}" if nps is not None else "—", "推薦者% − 批判者%", "#F59E0B")
    )
    st.markdown(f'<div class="kpi-grid">{cards}</div>', unsafe_allow_html=True)


def show_comments(df: pd.DataFrame) -> None:
    _section_header("フリーコメント", f"{len(df)}件中 抜粋", "#8B5CF6")

    comments = df[["date", "project_name", "comment"]].dropna(subset=["comment"])
    comments = comments[comments["comment"].astype(str).str.strip() != ""]

    if comments.empty:
        st.info("表示できるコメントがありません")
        return

    comments = comments.sort_values("date", ascending=False).reset_index(drop=True)
    for _, row in comments.iterrows():
        date_str = f"{row['date'].year}年{row['date'].month}月{row['date'].day}日" if pd.notna(row["date"]) else ""
        st.markdown(
            f"""
            <div class="comment-card">
                <div class="comment-meta">
                    <span class="comment-badge">{row['project_name']}</span>
                    <span>{date_str}</span>
                </div>
                <div class="comment-text">{row['comment']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def show_dashboard(name: str, authenticator) -> None:
    st.markdown(_CSS, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("### 📊 満足度 Dashboard")
        st.markdown(f"<small>ようこそ、**{name}** さん</small>", unsafe_allow_html=True)
        st.markdown("---")
        show_logout_button(authenticator)
        st.markdown("---")

        with st.spinner("読み込み中…"):
            df = load_all_data()

        if _is_demo_mode():
            st.markdown(
                '<div class="demo-banner">ℹ️ デモモード表示中</div>',
                unsafe_allow_html=True,
            )

        if df.empty:
            st.error("データが取得できませんでした")
            return

        st.markdown("**フィルター**")

        all_projects = sorted(df["project_name"].dropna().unique().tolist())
        selected_projects = st.multiselect(
            "プロジェクト",
            options=all_projects,
            default=all_projects,
        )

        all_months = sorted(df["date"].dt.strftime("%Y-%m").unique().tolist(), reverse=True)
        selected_months = st.multiselect(
            "期間",
            options=all_months,
            default=all_months[:6] if len(all_months) >= 6 else all_months,
        )

        st.markdown("---")
        st.caption("⏱ 5分ごとに自動更新")

    filtered_df = filter_data(
        df,
        projects=selected_projects if selected_projects else None,
        months=selected_months if selected_months else None,
    )

    st.markdown('<div class="page-title">顧客満足度ダッシュボード</div>', unsafe_allow_html=True)
    period_label = f"{selected_months[-1]} 〜 {selected_months[0]}" if selected_months else "全期間"
    st.markdown(f'<div class="page-subtitle">{period_label} ／ {", ".join(selected_projects) if selected_projects else "全プロジェクト"}</div>', unsafe_allow_html=True)

    if filtered_df.empty:
        st.warning("選択した条件に一致するデータがありません")
        return

    # KPI
    _section_header("KPI サマリー")
    show_kpi_cards(filtered_df)

    st.markdown("<br>", unsafe_allow_html=True)

    # 満足度グラフ
    _section_header("満足度スコア", "1〜10点", "#4F46E5")
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.plotly_chart(line_chart_monthly_trend(filtered_df), use_container_width=True)
    with col_r:
        st.plotly_chart(histogram_score_distribution(filtered_df), use_container_width=True)
    st.plotly_chart(bar_chart_project_comparison(filtered_df), use_container_width=True)

    # 自身の取り組みグラフ
    _section_header("自身の取り組みスコア", "1〜100点", "#06B6D4")
    col_l2, col_r2 = st.columns([2, 1])
    with col_l2:
        st.plotly_chart(line_chart_self_effort_trend(filtered_df), use_container_width=True)
    with col_r2:
        st.plotly_chart(histogram_self_effort_distribution(filtered_df), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # コメント
    show_comments(filtered_df)


def main() -> None:
    authenticator, _ = setup_authenticator()

    name, authentication_status, username = show_login_page(authenticator)

    if authentication_status:
        show_dashboard(name, authenticator)
    elif authentication_status is False:
        st.stop()
    else:
        st.stop()


if __name__ == "__main__":
    main()
