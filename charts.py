"""Plotly グラフ生成"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


PALETTE = ["#4F46E5", "#06B6D4", "#F59E0B", "#10B981", "#F43F5E", "#8B5CF6"]
SATISFACTION_COLOR = "#4F46E5"
EFFORT_COLOR = "#06B6D4"

_FONT = dict(family="Inter, -apple-system, sans-serif", size=12, color="#475569")

_LAYOUT = dict(
    font=_FONT,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=52, b=24, l=8, r=8),
    xaxis=dict(
        showgrid=False,
        linecolor="#E2E8F0",
        tickfont=dict(size=11, color="#94A3B8"),
        tickangle=0,
    ),
    yaxis=dict(
        gridcolor="#F1F5F9",
        gridwidth=1,
        linecolor="rgba(0,0,0,0)",
        tickfont=dict(size=11, color="#94A3B8"),
        zeroline=False,
    ),
    hoverlabel=dict(
        bgcolor="white",
        bordercolor="#E2E8F0",
        font=dict(size=12, family="Inter, sans-serif"),
    ),
    legend=dict(
        bgcolor="rgba(255,255,255,0)",
        borderwidth=0,
        font=dict(size=11, color="#64748B"),
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
    ),
    title=dict(
        font=dict(size=14, color="#1E293B", family="Inter, sans-serif"),
        x=0,
        xanchor="left",
        pad=dict(l=4, b=12),
    ),
)


def _base(fig: go.Figure, **kw) -> go.Figure:
    fig.update_layout(**{**_LAYOUT, **kw})
    return fig


def line_chart_monthly_trend(df: pd.DataFrame) -> go.Figure:
    monthly = (
        df.assign(month=df["date"].dt.to_period("M").dt.to_timestamp())
        .groupby(["month", "project_name"])["score"]
        .mean()
        .reset_index()
    )
    monthly["score"] = monthly["score"].round(2)

    fig = px.line(
        monthly,
        x="month", y="score", color="project_name",
        markers=True,
        color_discrete_sequence=PALETTE,
        labels={"month": "", "score": "平均スコア", "project_name": ""},
        title="満足度スコア 月別推移",
    )
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8, line=dict(width=2, color="white")),
        fill="tozeroy",
        fillcolor="rgba(79,70,229,0.05)",
    )
    # 目標ライン
    fig.add_hline(
        y=8, line_dash="dot", line_color="#CBD5E1", line_width=1.5,
        annotation_text="目標 8.0", annotation_font_size=10,
        annotation_font_color="#94A3B8", annotation_position="right",
    )
    return _base(fig, yaxis=dict(**_LAYOUT["yaxis"], range=[0, 10.5]), hovermode="x unified")


def line_chart_self_effort_trend(df: pd.DataFrame) -> go.Figure:
    monthly = (
        df.assign(month=df["date"].dt.to_period("M").dt.to_timestamp())
        .groupby(["month", "project_name"])["self_effort_score"]
        .mean()
        .reset_index()
    )
    monthly["self_effort_score"] = monthly["self_effort_score"].round(1)

    fig = px.line(
        monthly,
        x="month", y="self_effort_score", color="project_name",
        markers=True,
        color_discrete_sequence=PALETTE,
        labels={"month": "", "self_effort_score": "平均スコア", "project_name": ""},
        title="自身の取り組み 月別推移",
    )
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8, line=dict(width=2, color="white")),
        fill="tozeroy",
        fillcolor="rgba(6,182,212,0.05)",
    )
    fig.add_hline(
        y=70, line_dash="dot", line_color="#CBD5E1", line_width=1.5,
        annotation_text="目標 70", annotation_font_size=10,
        annotation_font_color="#94A3B8", annotation_position="right",
    )
    return _base(fig, yaxis=dict(**_LAYOUT["yaxis"], range=[0, 105]), hovermode="x unified")


def bar_chart_project_comparison(df: pd.DataFrame) -> go.Figure:
    df = df.copy()
    df["month"] = df["date"].dt.to_period("M")
    latest = df["month"].drop_duplicates().nlargest(2).tolist()

    if not latest:
        fig = go.Figure()
        return _base(fig, title=dict(text="データなし", **_LAYOUT["title"]))

    labels = {latest[0]: "今月"} | ({latest[1]: "前月"} if len(latest) == 2 else {})
    filtered = df[df["month"].isin(latest)].copy()
    filtered["期間"] = filtered["month"].map(labels)

    agg = (
        filtered.groupby(["project_name", "期間"])["score"]
        .mean().round(2).reset_index()
    )

    fig = px.bar(
        agg, x="project_name", y="score", color="期間",
        barmode="group",
        color_discrete_map={"今月": "#4F46E5", "前月": "#C7D2FE"},
        labels={"project_name": "", "score": "平均スコア"},
        title="PJ別 満足度比較（今月 vs 前月）",
        text="score",
    )
    fig.update_traces(
        marker_line_width=0,
        texttemplate="%{text:.1f}",
        textposition="outside",
        textfont=dict(size=11, color="#64748B"),
    )
    return _base(
        fig,
        yaxis=dict(**_LAYOUT["yaxis"], range=[0, 12]),
        bargap=0.3, bargroupgap=0.08,
        uniformtext_minsize=10, uniformtext_mode="hide",
    )


def histogram_score_distribution(df: pd.DataFrame) -> go.Figure:
    fig = px.histogram(
        df, x="score", nbins=10,
        labels={"score": "スコア", "count": "件数"},
        title="スコア分布",
        color_discrete_sequence=[SATISFACTION_COLOR],
    )
    fig.update_traces(marker_line_width=0, opacity=0.8)
    return _base(
        fig,
        xaxis=dict(**_LAYOUT["xaxis"], tickvals=list(range(1, 11))),
        bargap=0.1,
    )


def histogram_self_effort_distribution(df: pd.DataFrame) -> go.Figure:
    fig = px.histogram(
        df, x="self_effort_score", nbins=20,
        labels={"self_effort_score": "スコア", "count": "件数"},
        title="スコア分布",
        color_discrete_sequence=[EFFORT_COLOR],
    )
    fig.update_traces(marker_line_width=0, opacity=0.8)
    return _base(
        fig,
        xaxis=dict(**_LAYOUT["xaxis"], range=[0, 100]),
        bargap=0.05,
    )
