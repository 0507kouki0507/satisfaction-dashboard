"""Plotly グラフ生成"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


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
        labels={
            "month": "月",
            "score": "平均スコア（1〜5）",
            "project_name": "プロジェクト",
        },
        title="月別満足度推移",
    )
    fig.update_layout(
        yaxis=dict(range=[1, 5]),
        hovermode="x unified",
        legend_title_text="プロジェクト",
    )
    return fig


def bar_chart_project_comparison(df: pd.DataFrame) -> go.Figure:
    """PJ別スコア比較（今月 vs 前月）棒グラフ"""
    df = df.copy()
    df["month"] = df["date"].dt.to_period("M")
    latest_months = df["month"].drop_duplicates().nlargest(2).tolist()

    if len(latest_months) == 0:
        fig = go.Figure()
        fig.update_layout(title="PJ別スコア比較（データなし）")
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
        labels={
            "project_name": "プロジェクト",
            "score": "平均スコア（1〜5）",
        },
        title="PJ別スコア比較（今月 vs 前月）",
    )
    fig.update_layout(yaxis=dict(range=[0, 5]))
    return fig


def histogram_score_distribution(df: pd.DataFrame) -> go.Figure:
    """スコア分布ヒストグラム"""
    fig = px.histogram(
        df,
        x="score",
        nbins=5,
        labels={"score": "スコア（1〜5）", "count": "件数"},
        title="スコア分布",
        color_discrete_sequence=["#636EFA"],
    )
    fig.update_layout(
        xaxis=dict(tickvals=[1, 2, 3, 4, 5]),
        bargap=0.1,
    )
    return fig
