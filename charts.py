"""Plotly グラフ生成"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# 統一カラーパレット
PALETTE = ["#4F46E5", "#06B6D4", "#F59E0B", "#10B981", "#F43F5E", "#8B5CF6"]
SATISFACTION_COLOR = "#4F46E5"
EFFORT_COLOR = "#06B6D4"

_LAYOUT_BASE = dict(
    font=dict(family="sans-serif", size=13, color="#0F172A"),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=48, b=32, l=16, r=16),
    legend=dict(
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="#E2E8F0",
        borderwidth=1,
        font=dict(size=12),
    ),
    xaxis=dict(
        showgrid=False,
        linecolor="#E2E8F0",
        tickfont=dict(size=11),
    ),
    yaxis=dict(
        gridcolor="#F1F5F9",
        linecolor="#E2E8F0",
        tickfont=dict(size=11),
    ),
    hoverlabel=dict(
        bgcolor="white",
        bordercolor="#E2E8F0",
        font=dict(size=12),
    ),
    title=dict(
        font=dict(size=15, color="#1E293B"),
        x=0,
        xanchor="left",
        pad=dict(l=4),
    ),
)


def _apply_base_layout(fig: go.Figure, **extra) -> go.Figure:
    layout = {**_LAYOUT_BASE, **extra}
    fig.update_layout(**layout)
    return fig


def line_chart_monthly_trend(df: pd.DataFrame) -> go.Figure:
    """月別満足度推移（PJ別色分け）折れ線グラフ"""
    monthly = (
        df.assign(month=df["date"].dt.to_period("M").dt.to_timestamp())
        .groupby(["month", "project_name"])["score"]
        .mean()
        .reset_index()
    )
    monthly["score"] = monthly["score"].round(2)

    fig = px.line(
        monthly,
        x="month",
        y="score",
        color="project_name",
        markers=True,
        color_discrete_sequence=PALETTE,
        labels={"month": "", "score": "平均スコア（1〜10）", "project_name": "プロジェクト"},
        title="月別満足度推移",
    )
    fig.update_traces(line=dict(width=2.5), marker=dict(size=7))
    _apply_base_layout(
        fig,
        yaxis=dict(**_LAYOUT_BASE["yaxis"], range=[0, 10]),
        hovermode="x unified",
        legend_title_text="",
    )
    return fig


def line_chart_self_effort_trend(df: pd.DataFrame) -> go.Figure:
    """月別「自身の取り組み」スコア推移（PJ別色分け）折れ線グラフ"""
    monthly = (
        df.assign(month=df["date"].dt.to_period("M").dt.to_timestamp())
        .groupby(["month", "project_name"])["self_effort_score"]
        .mean()
        .reset_index()
    )
    monthly["self_effort_score"] = monthly["self_effort_score"].round(1)

    fig = px.line(
        monthly,
        x="month",
        y="self_effort_score",
        color="project_name",
        markers=True,
        color_discrete_sequence=PALETTE,
        labels={"month": "", "self_effort_score": "平均スコア（1〜100）", "project_name": "プロジェクト"},
        title="月別「自身の取り組み」推移",
    )
    fig.update_traces(line=dict(width=2.5), marker=dict(size=7))
    _apply_base_layout(
        fig,
        yaxis=dict(**_LAYOUT_BASE["yaxis"], range=[0, 100]),
        hovermode="x unified",
        legend_title_text="",
    )
    return fig


def bar_chart_project_comparison(df: pd.DataFrame) -> go.Figure:
    """PJ別スコア比較（今月 vs 前月）棒グラフ"""
    df = df.copy()
    df["month"] = df["date"].dt.to_period("M")
    latest_months = df["month"].drop_duplicates().nlargest(2).tolist()

    if not latest_months:
        fig = go.Figure()
        _apply_base_layout(fig, title=dict(text="PJ別満足度比較（データなし）", **_LAYOUT_BASE["title"]))
        return fig

    labels = {latest_months[0]: "今月", latest_months[1]: "前月"} if len(latest_months) == 2 else {latest_months[0]: "今月"}
    filtered = df[df["month"].isin(latest_months)].copy()
    filtered["期間"] = filtered["month"].map(labels)

    agg = (
        filtered.groupby(["project_name", "期間"])["score"]
        .mean()
        .round(2)
        .reset_index()
    )

    fig = px.bar(
        agg,
        x="project_name",
        y="score",
        color="期間",
        barmode="group",
        color_discrete_sequence=["#4F46E5", "#C7D2FE"],
        labels={"project_name": "", "score": "平均スコア（1〜10）"},
        title="PJ別満足度比較（今月 vs 前月）",
    )
    fig.update_traces(marker_line_width=0)
    _apply_base_layout(
        fig,
        yaxis=dict(**_LAYOUT_BASE["yaxis"], range=[0, 10]),
        bargap=0.25,
        bargroupgap=0.1,
        legend_title_text="",
    )
    return fig


def histogram_score_distribution(df: pd.DataFrame) -> go.Figure:
    """満足度スコア分布ヒストグラム"""
    fig = px.histogram(
        df,
        x="score",
        nbins=10,
        labels={"score": "スコア（1〜10）", "count": "件数"},
        title="満足度スコア分布",
        color_discrete_sequence=[SATISFACTION_COLOR],
    )
    fig.update_traces(marker_line_width=0, opacity=0.85)
    _apply_base_layout(
        fig,
        xaxis=dict(**_LAYOUT_BASE["xaxis"], tickvals=list(range(1, 11))),
        bargap=0.08,
    )
    return fig


def histogram_self_effort_distribution(df: pd.DataFrame) -> go.Figure:
    """「自身の取り組み」スコア分布ヒストグラム"""
    fig = px.histogram(
        df,
        x="self_effort_score",
        nbins=20,
        labels={"self_effort_score": "スコア（1〜100）", "count": "件数"},
        title="「自身の取り組み」スコア分布",
        color_discrete_sequence=[EFFORT_COLOR],
    )
    fig.update_traces(marker_line_width=0, opacity=0.85)
    _apply_base_layout(
        fig,
        xaxis=dict(**_LAYOUT_BASE["xaxis"], range=[0, 100]),
        bargap=0.04,
    )
    return fig
