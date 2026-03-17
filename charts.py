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
            "score": "平均スコア（1〜10）",
            "project_name": "プロジェクト",
        },
        title="月別満足度推移",
    )
    fig.update_layout(
        yaxis=dict(range=[1, 10]),
        hovermode="x unified",
        legend_title_text="プロジェクト",
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
        labels={
            "month": "月",
            "self_effort_score": "平均スコア（1〜100）",
            "project_name": "プロジェクト",
        },
        title="月別「自身の取り組み」推移",
    )
    fig.update_layout(
        yaxis=dict(range=[0, 100]),
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
            "score": "平均スコア（1〜10）",
        },
        title="PJ別満足度比較（今月 vs 前月）",
    )
    fig.update_layout(yaxis=dict(range=[0, 10]))
    return fig


def histogram_score_distribution(df: pd.DataFrame) -> go.Figure:
    """満足度スコア分布ヒストグラム"""
    fig = px.histogram(
        df,
        x="score",
        nbins=10,
        labels={"score": "スコア（1〜10）", "count": "件数"},
        title="満足度スコア分布",
        color_discrete_sequence=["#636EFA"],
    )
    fig.update_layout(
        xaxis=dict(tickvals=list(range(1, 11))),
        bargap=0.1,
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
        color_discrete_sequence=["#EF553B"],
    )
    fig.update_layout(
        xaxis=dict(range=[0, 100]),
        bargap=0.05,
    )
    return fig
