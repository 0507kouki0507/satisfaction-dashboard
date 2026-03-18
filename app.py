"""メインアプリ・ページルーティング"""

import pandas as pd
import streamlit as st

from auth import setup_authenticator, show_login_page, show_logout_button
from charts import (
    bar_chart_category_scores,
    bar_chart_project_comparison,
    histogram_score_distribution,
    histogram_self_effort_distribution,
    line_chart_category_trend,
    line_chart_monthly_trend,
    line_chart_self_effort_trend,
)
from data import _is_demo_mode, debug_sheet_info, filter_data, get_nps_score, get_response_rate, load_all_data


st.set_page_config(
    page_title="満足度ダッシュボード",
    page_icon="📊",
    layout="wide",
)

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ===== BASE ===== */
html, body, [class*="css"], .stMarkdown, .stText {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
.main .block-container {
    padding: 0 2.5rem 3rem !important;
    max-width: 1440px !important;
}
[data-testid="stHeader"] { background: transparent !important; border: none !important; }
[data-testid="stAppViewContainer"] { background: #F1F5F9 !important; }

/* ===== SIDEBAR ===== */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%) !important;
    border-right: none !important;
    box-shadow: 4px 0 32px rgba(0,0,0,0.2) !important;
}
[data-testid="stSidebar"] section { padding-top: 0 !important; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] small { color: #94A3B8 !important; }
[data-testid="stSidebar"] [data-baseweb="tag"] {
    background: rgba(79,70,229,0.35) !important;
    border: 1px solid rgba(79,70,229,0.5) !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] [data-baseweb="tag"] span { color: #C7D2FE !important; }
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.05) !important;
    border-color: rgba(255,255,255,0.08) !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] button {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #94A3B8 !important;
    border-radius: 8px !important;
    width: 100% !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 8px 14px !important;
    transition: all .2s !important;
}
[data-testid="stSidebar"] button:hover {
    background: rgba(79,70,229,0.25) !important;
    border-color: rgba(79,70,229,0.6) !important;
    color: #E2E8F0 !important;
}
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.07) !important; margin: 12px 0 !important; }

/* ===== PAGE HEADER ===== */
.page-header {
    background: linear-gradient(135deg, #4338CA 0%, #7C3AED 100%);
    border-radius: 20px;
    padding: 32px 36px;
    margin: 24px 0 8px;
    color: white;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(79,70,229,0.35);
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.page-header::before {
    content: '';
    position: absolute;
    top: -50px; right: -30px;
    width: 220px; height: 220px;
    background: rgba(255,255,255,0.07);
    border-radius: 50%;
}
.page-header::after {
    content: '';
    position: absolute;
    bottom: -70px; right: 80px;
    width: 180px; height: 180px;
    background: rgba(255,255,255,0.04);
    border-radius: 50%;
}
.page-header-eyebrow {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: .1em;
    text-transform: uppercase;
    opacity: 0.65;
    margin-bottom: 8px;
}
.page-header-title {
    font-size: 30px;
    font-weight: 800;
    letter-spacing: -.025em;
    margin-bottom: 8px;
    line-height: 1.1;
}
.page-header-meta {
    font-size: 13px;
    opacity: 0.6;
    font-weight: 400;
}
.page-header-left {
    flex: 1;
    min-width: 0;
    padding-right: 24px;
}
.page-header-score {
    text-align: right;
    flex-shrink: 0;
    z-index: 1;
}
.page-header-score-value {
    font-size: 52px;
    font-weight: 900;
    letter-spacing: -.04em;
    line-height: 1;
}
.page-header-score-label {
    font-size: 11px;
    opacity: 0.6;
    margin-top: 4px;
    font-weight: 500;
    letter-spacing: .04em;
    text-transform: uppercase;
}

/* ===== KPI GRID ===== */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 12px;
    margin: 20px 0 8px;
}
@media (max-width: 1200px) {
    .kpi-grid { grid-template-columns: repeat(3, 1fr); }
}
.kpi-card {
    background: white;
    border-radius: 16px;
    padding: 18px 16px 14px;
    box-shadow: 0 1px 3px rgba(15,23,42,0.06), 0 4px 16px rgba(15,23,42,0.04);
    position: relative;
    overflow: hidden;
    transition: transform .18s, box-shadow .18s;
    cursor: default;
    min-width: 0;
}
.kpi-card:hover { transform: translateY(-3px); box-shadow: 0 12px 40px rgba(15,23,42,0.1); }
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--accent);
    border-radius: 16px 16px 0 0;
}
.kpi-icon { font-size: 20px; margin-bottom: 10px; display: block; }
.kpi-label {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .06em;
    text-transform: uppercase;
    color: #94A3B8;
    margin-bottom: 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.kpi-value {
    font-size: 28px;
    font-weight: 800;
    color: var(--value-color, #0F172A);
    line-height: 1;
    letter-spacing: -.03em;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.kpi-delta {
    font-size: 11px;
    font-weight: 600;
    margin-top: 8px;
    display: flex;
    align-items: center;
    gap: 3px;
    white-space: nowrap;
    overflow: hidden;
}
.kpi-delta.up   { color: #10B981; }
.kpi-delta.down { color: #EF4444; }
.kpi-delta.neutral { color: #94A3B8; }
.kpi-sub {
    font-size: 10px;
    color: #CBD5E1;
    margin-top: 4px;
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* ===== SECTION HEADER ===== */
.sec-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 40px 0 16px;
    padding-bottom: 14px;
    border-bottom: 1.5px solid #E2E8F0;
}
.sec-bar {
    width: 4px; height: 26px;
    border-radius: 99px;
    flex-shrink: 0;
}
.sec-title {
    font-size: 17px;
    font-weight: 700;
    color: #0F172A;
    letter-spacing: -.015em;
}
.sec-badge {
    font-size: 10.5px;
    font-weight: 700;
    padding: 3px 11px;
    border-radius: 99px;
    letter-spacing: .05em;
    text-transform: uppercase;
}

/* ===== CHART CONTAINERS ===== */
[data-testid="stPlotlyChart"] > div {
    background: white !important;
    border-radius: 16px !important;
    padding: 8px !important;
    box-shadow: 0 1px 3px rgba(15,23,42,0.06), 0 4px 16px rgba(15,23,42,0.04) !important;
}

/* ===== COMMENT GRID ===== */
.comment-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
    margin-top: 8px;
}
.comment-card {
    background: white;
    border-radius: 16px;
    padding: 22px 24px 20px;
    box-shadow: 0 1px 4px rgba(15,23,42,0.06), 0 4px 16px rgba(15,23,42,0.04);
    position: relative;
    transition: transform .18s, box-shadow .18s;
    overflow: hidden;
}
.comment-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--bcolor);
    border-radius: 16px 16px 0 0;
}
.comment-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(15,23,42,0.10);
}
.comment-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 14px;
}
.comment-pj {
    font-size: 10.5px;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 99px;
    letter-spacing: .04em;
}
.comment-date {
    font-size: 11px;
    color: #94A3B8;
    margin-left: auto;
    font-weight: 500;
}
.comment-text {
    font-size: 13.5px;
    color: #334155;
    line-height: 1.8;
}

/* ===== SIDEBAR CUSTOM COMPONENTS ===== */
.sb-logo {
    padding: 24px 20px 18px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 4px;
}
.sb-logo-mark {
    font-size: 20px;
    font-weight: 800;
    color: white;
    letter-spacing: -.02em;
    line-height: 1;
}
.sb-logo-sub {
    font-size: 10px;
    color: #475569;
    margin-top: 4px;
    font-weight: 500;
    letter-spacing: .06em;
    text-transform: uppercase;
}
.sb-user {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 10px 14px;
    margin: 12px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.sb-avatar {
    width: 34px; height: 34px;
    background: linear-gradient(135deg, #4F46E5, #7C3AED);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; font-weight: 800; color: white;
    flex-shrink: 0;
}
.sb-name { font-size: 13px; font-weight: 600; color: #E2E8F0; }
.sb-role { font-size: 10px; color: #475569; margin-top: 1px; }
.sb-section-label {
    font-size: 10px !important;
    font-weight: 700 !important;
    letter-spacing: .1em !important;
    text-transform: uppercase !important;
    color: #475569 !important;
    margin: 16px 0 8px !important;
}
.sb-footer {
    padding: 16px 0 0;
    border-top: 1px solid rgba(255,255,255,0.06);
    margin-top: 16px;
}
.sb-update { font-size: 10.5px; color: #475569 !important; font-weight: 500; }
.sb-demo {
    background: rgba(79,70,229,0.18);
    border: 1px solid rgba(79,70,229,0.3);
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 11px;
    color: #A5B4FC;
    font-weight: 500;
    margin: 8px 0;
}

/* ===== BACKGROUND WATERMARK ===== */
[data-testid="stAppViewContainer"]::before {
    content: 'PdC';
    position: fixed;
    bottom: -40px;
    right: -20px;
    font-size: 320px;
    font-weight: 900;
    font-family: 'Inter', sans-serif;
    color: #4F46E5;
    opacity: 0.03;
    letter-spacing: -.05em;
    pointer-events: none;
    z-index: 0;
    line-height: 1;
    user-select: none;
}

/* ===== PdC LOGO ===== */
.pdc-logo {
    padding: 20px 20px 16px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 4px;
}
.pdc-logo-inner {
    display: flex;
    align-items: center;
    gap: 11px;
}
.pdc-icon {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px;
    font-weight: 900;
    color: white;
    letter-spacing: -.03em;
    flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(79,70,229,0.4);
}
.pdc-name {
    font-size: 18px;
    font-weight: 800;
    color: white;
    letter-spacing: -.02em;
    line-height: 1.1;
}
.pdc-sub {
    font-size: 9.5px;
    color: #475569;
    margin-top: 2px;
    font-weight: 600;
    letter-spacing: .1em;
    text-transform: uppercase;
}

/* ===== MISC ===== */
[data-testid="stInfo"] { border-radius: 12px !important; }
[data-testid="stWarning"] { border-radius: 12px !important; }
.stSpinner > div { border-top-color: #4F46E5 !important; }
</style>
"""

_PROJECT_COLORS = ["#4F46E5", "#06B6D4", "#F59E0B", "#10B981", "#F43F5E", "#8B5CF6"]


def _color_for_ratio(ratio: float) -> str:
    if ratio >= 0.75: return "#10B981"
    if ratio >= 0.5:  return "#F59E0B"
    return "#EF4444"


def _month_delta(df: pd.DataFrame, col: str) -> tuple[float | None, str]:
    tmp = df.copy()
    tmp["m"] = tmp["date"].dt.to_period("M")
    months = tmp["m"].drop_duplicates().nlargest(2).tolist()
    if len(months) < 2:
        return None, "neutral"
    cur = tmp[tmp["m"] == months[0]][col].mean()
    prv = tmp[tmp["m"] == months[1]][col].mean()
    if pd.isna(cur) or pd.isna(prv):
        return None, "neutral"
    d = cur - prv
    return d, ("up" if d > 0.05 else "down" if d < -0.05 else "neutral")


def _delta_html(delta: float | None, direction: str, unit: str = "") -> str:
    if delta is None:
        return '<div class="kpi-delta neutral">— 前月比データなし</div>'
    arrow = "▲" if direction == "up" else "▼" if direction == "down" else "―"
    return f'<div class="kpi-delta {direction}">{arrow}&nbsp;{abs(delta):.1f}{unit}&nbsp;前月比</div>'


def _section(title: str, badge: str = "", color: str = "#4F46E5", badge_bg: str = "#EEF2FF") -> None:
    badge_html = (
        f'<span class="sec-badge" style="background:{badge_bg};color:{color}">{badge}</span>'
        if badge else ""
    )
    st.markdown(
        f'<div class="sec-header">'
        f'<div class="sec-bar" style="background:linear-gradient(180deg,{color},{color}aa)"></div>'
        f'<span class="sec-title">{title}</span>{badge_html}</div>',
        unsafe_allow_html=True,
    )


def show_page_header(df: pd.DataFrame, period_label: str, project_label: str) -> None:
    avg = df["score"].mean()
    avg_str = f"{avg:.1f}" if not pd.isna(avg) else "—"
    st.markdown(
        f"""
        <div class="page-header">
            <div class="page-header-left">
                <div class="page-header-eyebrow">📊 Satisfaction Dashboard</div>
                <div class="page-header-title">プロジェクト別顧客満足度ダッシュボード</div>
                <div class="page-header-meta">{period_label}　／　{project_label}</div>
            </div>
            <div class="page-header-score">
                <div class="page-header-score-value">{avg_str}</div>
                <div class="page-header-score-label">平均満足度 / 10</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_kpi_cards(df: pd.DataFrame) -> None:
    avg_score    = df["score"].mean()
    median_score = df["score"].median()
    avg_effort   = df["self_effort_score"].median()
    rr           = get_response_rate(df)
    nps          = get_nps_score(df)

    # 回答者数・受講生数
    total_students = df["total_students"].sum()
    respondents    = df["respondents"].sum() if df["respondents"].notna().any() else len(df)
    has_total      = not pd.isna(total_students) and total_students > 0

    sd, sdir = _month_delta(df, "score")
    ed, edir = _month_delta(df, "self_effort_score")

    sc = _color_for_ratio(avg_score / 10) if not pd.isna(avg_score) else "#94A3B8"
    ec = _color_for_ratio(avg_effort / 100) if not pd.isna(avg_effort) else "#94A3B8"
    nc = _color_for_ratio((nps + 100) / 200) if nps is not None else "#94A3B8"
    rr_val = f"{rr:.1f}%" if rr > 0 else "—"
    rr_color = _color_for_ratio(rr / 100) if rr > 0 else "#94A3B8"

    def card(icon, label, value, sub, accent, vcolor, delta=""):
        return (
            f'<div class="kpi-card" style="--accent:{accent};--value-color:{vcolor}">'
            f'<span class="kpi-icon">{icon}</span>'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div>'
            f'{delta}'
            f'<div class="kpi-sub">{sub}</div>'
            f'</div>'
        )

    if has_total:
        resp_value = f"{int(respondents):,}"
        resp_sub   = f"受講生 {int(total_students):,} 人中"
    else:
        resp_value = f"{int(respondents):,}"
        resp_sub   = "アンケート回答数"

    html = (
        card("⭐", "平均満足度",
             f"{avg_score:.1f}" if not pd.isna(avg_score) else "—",
             "/ 10点満点", "#4F46E5", sc, _delta_html(sd, sdir))
        + card("📊", "中央値スコア",
               f"{median_score:.1f}" if not pd.isna(median_score) else "—",
               "/ 10点満点", "#6366F1", "#0F172A")
        + card("💪", "自身の取り組み",
               f"{avg_effort:.1f}" if not pd.isna(avg_effort) else "—",
               "中央値 / 100点満点", "#06B6D4", ec, _delta_html(ed, edir, "pt"))
        + card("👥", "回答者数",
               resp_value, resp_sub, "#8B5CF6", "#0F172A")
        + card("📝", "回答率",
               rr_val,
               "アンケート回答者 ÷ 受講生", "#10B981", rr_color)
        + card("📣", "NPS スコア",
               f"{nps:.1f}" if nps is not None else "—",
               "おすすめ度 中央値 / 10", "#F59E0B", nc)
    )
    st.markdown(f'<div class="kpi-grid">{html}</div>', unsafe_allow_html=True)


def show_comments(df: pd.DataFrame) -> None:
    cols_needed = [c for c in ["date", "project_name", "comment", "score"] if c in df.columns]
    comments = df[cols_needed].dropna(subset=["comment"])
    comments = comments[comments["comment"].astype(str).str.strip() != ""]
    if comments.empty:
        st.info("表示できるコメントがありません")
        return

    projects = df["project_name"].dropna().unique().tolist()
    color_map = {p: _PROJECT_COLORS[i % len(_PROJECT_COLORS)] for i, p in enumerate(projects)}

    comments = comments.sort_values("date", ascending=False).reset_index(drop=True)
    total = len(comments)
    _section("フリーコメント", f"{total}件", "#8B5CF6", "#F5F3FF")

    # 表示件数コントロール
    show_all = st.checkbox("すべて表示", value=False) if total > 10 else True
    display = comments if show_all else comments.head(10)

    cards = ""
    for _, row in display.iterrows():
        date_str = (
            f"{row['date'].year}年{row['date'].month}月{row['date'].day}日"
            if pd.notna(row["date"]) else ""
        )
        c = color_map.get(row["project_name"], "#4F46E5")
        score_html = ""
        if "score" in row and pd.notna(row["score"]):
            score_val = f"{row['score']:.1f}"
            score_html = (
                f'<span style="display:inline-flex;align-items:center;gap:4px;'
                f'background:{c}15;color:{c};border:1px solid {c}40;'
                f'font-size:11px;font-weight:700;padding:2px 10px;border-radius:99px;">'
                f'⭐ 満足度 {score_val}<span style="opacity:0.5;font-weight:400">/10</span></span>'
            )
        cards += (
            f'<div class="comment-card" style="--bcolor:{c}">'
            f'<div class="comment-meta">'
            f'<span class="comment-pj" style="background:{c}18;color:{c}">{row["project_name"]}</span>'
            f'{score_html}'
            f'<span class="comment-date">{date_str}</span>'
            f'</div>'
            f'<div class="comment-text">{row["comment"]}</div>'
            f'</div>'
        )
    st.markdown(f'<div class="comment-grid">{cards}</div>', unsafe_allow_html=True)

    if not show_all and total > 10:
        st.markdown(
            f'<p style="text-align:center;color:#94A3B8;font-size:12px;margin-top:12px">'
            f'残り {total - 10} 件 ／ 合計 {total} 件</p>',
            unsafe_allow_html=True,
        )


def show_dashboard(name: str, authenticator) -> None:
    st.markdown(_CSS, unsafe_allow_html=True)

    with st.sidebar:
        initials = name[0].upper() if name else "?"
        st.markdown(
            f'<div class="pdc-logo">'
            f'  <div class="pdc-logo-inner">'
            f'    <div class="pdc-icon">PdC</div>'
            f'    <div>'
            f'      <div class="pdc-name">PdC</div>'
            f'      <div class="pdc-sub">Satisfaction Dashboard</div>'
            f'    </div>'
            f'  </div>'
            f'</div>'
            f'<div class="sb-user">'
            f'<div class="sb-avatar">{initials}</div>'
            f'<div><div class="sb-name">{name}</div><div class="sb-role">Member</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        with st.spinner(""):
            df = load_all_data()

        if _is_demo_mode():
            st.markdown('<div class="sb-demo">ℹ️ デモモード表示中</div>', unsafe_allow_html=True)

        if df.empty:
            st.error("データが取得できませんでした")
            return

        # ── アンケートフェーズ ──
        st.markdown('<div class="sb-section-label">アンケートフェーズ</div>', unsafe_allow_html=True)
        all_projects = sorted(df["project_name"].dropna().unique().tolist())
        # 表示用ラベル（「満足度：」プレフィックスを除去）
        def _phase_label(p: str) -> str:
            return p.replace("満足度：", "").replace("満足度", "").strip() or p
        phase_labels = [_phase_label(p) for p in all_projects]
        label_to_project = dict(zip(phase_labels, all_projects))
        selected_phase_labels = st.multiselect(
            "フェーズ", phase_labels, default=phase_labels, label_visibility="collapsed"
        )
        selected_projects = [label_to_project[l] for l in selected_phase_labels]

        # ── 回答月 ──
        ym_pairs = (
            df["date"].dropna()
            .dt.to_period("M")
            .drop_duplicates()
            .sort_values(ascending=False)
            .tolist()
        )
        ym_labels = [f"{p.year}年{p.month}月" for p in ym_pairs]
        ym_options = ["全期間"] + ym_labels

        st.markdown('<div class="sb-section-label" style="margin-top:14px">回答月</div>', unsafe_allow_html=True)
        selected_ym = st.selectbox("回答月", ym_options, index=0, label_visibility="collapsed")

        if selected_ym == "全期間":
            selected_years: list[int] = []
            selected_months: list[int] = []
        else:
            matched = ym_pairs[ym_labels.index(selected_ym)]
            selected_years = [int(matched.year)]
            selected_months = [int(matched.month)]

        st.markdown(
            f'<div class="sb-footer">'
            f'<div class="sb-update">⏱ 5分ごとに自動更新</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        if authenticator is not None:
            show_logout_button(authenticator)

    # フィルター適用
    filtered = filter_data(
        df,
        projects=selected_projects if selected_projects else None,
        years=selected_years if selected_years else None,
        months=selected_months if selected_months else None,
    )

    period_label = selected_ym
    project_label = "、".join(selected_phase_labels) if selected_phase_labels else "全フェーズ"

    if filtered.empty:
        st.warning("選択した条件に一致するデータがありません")
        return

    show_page_header(filtered, period_label, project_label)
    show_kpi_cards(filtered)

    # 満足度セクション
    _section("満足度スコア", "1〜10点", "#4F46E5", "#EEF2FF")
    c1, c2 = st.columns([3, 1])
    with c1:
        st.plotly_chart(line_chart_monthly_trend(filtered), use_container_width=True)
    with c2:
        st.plotly_chart(histogram_score_distribution(filtered), use_container_width=True)
    st.plotly_chart(bar_chart_project_comparison(filtered), use_container_width=True)

    # カテゴリ別満足度セクション
    _section("カテゴリ別 満足度", "動画 / サポート / システム", "#6366F1", "#EEF2FF")
    c5, c6 = st.columns([2, 1])
    with c5:
        st.plotly_chart(line_chart_category_trend(filtered), use_container_width=True)
    with c6:
        st.plotly_chart(bar_chart_category_scores(filtered), use_container_width=True)

    # 自身の取り組みセクション
    _section("自身の取り組み", "1〜100点", "#06B6D4", "#ECFEFF")
    c3, c4 = st.columns([3, 1])
    with c3:
        st.plotly_chart(line_chart_self_effort_trend(filtered), use_container_width=True)
    with c4:
        st.plotly_chart(histogram_self_effort_distribution(filtered), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    show_comments(filtered)


def main() -> None:
    try:
        dev_mode = bool(st.secrets["app"]["dev_mode"])
    except Exception:
        dev_mode = False
    if dev_mode:
        st.markdown(_CSS, unsafe_allow_html=True)
        with st.expander("🔍 デバッグ情報（dev_mode）", expanded=True):
            infos = debug_sheet_info()
            for info in infos:
                if "error" in info:
                    st.error(info["error"])
                else:
                    matched = info.get("matches_filter", False)
                    icon = "✅" if matched else "⬜"
                    st.markdown(f"**{icon} タブ名:** `{info['tab']}`")
                    if matched:
                        st.markdown(f"- 行数: {info.get('rows', '?')}")
                        st.markdown(f"- 列名: `{info.get('headers', [])}`")
                        if "read_error" in info:
                            st.error(f"読み込みエラー: {info['read_error']}")
        show_dashboard("Developer", None)
        return

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
