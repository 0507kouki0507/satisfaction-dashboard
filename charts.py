"""Plotly グラフ生成"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


PALETTE = ["#4F46E5", "#06B6D4", "#F59E0B", "#10B981", "#F43F5E", "#8B5CF6"]
SATISFACTION_COLOR = "#4F46E5"
EFFORT_COLOR = "#06B6D4"

_FONT = dict(family="Inter, -apple-system, sans-serif", size=12, color="#475569")

# 凡例は下部、タイトルは上部のみ（重ならない設計）
_LAYOUT = dict(
    font=_FONT,
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=44, b=48, l=12, r=40),
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
    # 凡例を下部中央に配置
    legend=dict(
        bgcolor="rgba(255,255,255,0)",
        borderwidth=0,
        font=dict(size=11, color="#64748B"),
        orientation="h",
        yanchor="top",
        y=-0.18,
        xanchor="center",
        x=0.5,
    ),
    # タイトルは左上のみ（凡例と重ならない）
    title=dict(
        font=dict(size=13, color="#1E293B", family="Inter, sans-serif"),
        x=0.01,
        xanchor="left",
        y=0.98,
        yanchor="top",
    ),
)


def _base(fig: go.Figure, **kw) -> go.Figure:
    layout = {**_LAYOUT, **kw}
    # 深いネストのdictはマージする
    for key in ("xaxis", "yaxis", "legend", "title", "hoverlabel"):
        if key in kw and key in _LAYOUT and isinstance(_LAYOUT[key], dict):
            layout[key] = {**_LAYOUT[key], **kw[key]}
    fig.update_layout(**layout)
    return fig


def line_chart_monthly_trend(df: pd.DataFrame) -> go.Figure:
    monthly = (
        df.assign(month=df["date"].dt.to_period("M").dt.to_timestamp())
        .groupby(["month", "project_name"])["score"]
        .mean()
        .reset_index()
    )
    monthly["score"] = monthly["score"].round(2)

    projects = monthly["project_name"].unique().tolist()

    fig = go.Figure()
    for i, proj in enumerate(projects):
        color = PALETTE[i % len(PALETTE)]
        sub = monthly[monthly["project_name"] == proj]
        fig.add_trace(go.Scatter(
            x=sub["month"], y=sub["score"],
            name=proj,
            mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=7, color=color, line=dict(width=2, color="white")),
            hovertemplate="%{x|%Y年%m月}<br>スコア: <b>%{y:.1f}</b><extra>" + proj + "</extra>",
        ))

    fig.add_hline(
        y=8, line_dash="dot", line_color="#CBD5E1", line_width=1.5,
        annotation_text="目標 8.0", annotation_font_size=10,
        annotation_font_color="#94A3B8", annotation_position="top right",
    )
    return _base(
        fig,
        title=dict(text="月別推移"),
        yaxis=dict(range=[0, 10.5]),
        hovermode="x unified",
    )


def line_chart_self_effort_trend(df: pd.DataFrame) -> go.Figure:
    monthly = (
        df.assign(month=df["date"].dt.to_period("M").dt.to_timestamp())
        .groupby(["month", "project_name"])["self_effort_score"]
        .mean()
        .reset_index()
    )
    monthly["self_effort_score"] = monthly["self_effort_score"].round(1)

    projects = monthly["project_name"].unique().tolist()

    fig = go.Figure()
    for i, proj in enumerate(projects):
        color = PALETTE[i % len(PALETTE)]
        sub = monthly[monthly["project_name"] == proj]
        fig.add_trace(go.Scatter(
            x=sub["month"], y=sub["self_effort_score"],
            name=proj,
            mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=7, color=color, line=dict(width=2, color="white")),
            hovertemplate="%{x|%Y年%m月}<br>スコア: <b>%{y:.1f}</b><extra>" + proj + "</extra>",
        ))

    fig.add_hline(
        y=70, line_dash="dot", line_color="#CBD5E1", line_width=1.5,
        annotation_text="目標 70", annotation_font_size=10,
        annotation_font_color="#94A3B8", annotation_position="top right",
    )
    return _base(
        fig,
        title=dict(text="月別推移"),
        yaxis=dict(range=[0, 110]),
        hovermode="x unified",
    )


def bar_chart_project_comparison(df: pd.DataFrame) -> go.Figure:
    df = df.copy()
    df["month"] = df["date"].dt.to_period("M")
    latest = df["month"].drop_duplicates().nlargest(2).tolist()

    if not latest:
        fig = go.Figure()
        return _base(fig, title=dict(text="データなし"))

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
    )
    fig.update_traces(
        marker_line_width=0,
        # inside に変更してはみ出しを防ぐ
        text=agg["score"],
        texttemplate="%{text:.1f}",
        textposition="inside",
        textfont=dict(size=12, color="white", family="Inter, sans-serif"),
        insidetextanchor="middle",
    )
    return _base(
        fig,
        title=dict(text="PJ別 満足度比較（今月 vs 前月）"),
        yaxis=dict(range=[0, 11]),
        bargap=0.25,
        bargroupgap=0.06,
    )


def histogram_score_distribution(df: pd.DataFrame) -> go.Figure:
    fig = px.histogram(
        df, x="score", nbins=10,
        labels={"score": "スコア", "count": "件数"},
        color_discrete_sequence=[SATISFACTION_COLOR],
    )
    fig.update_traces(marker_line_width=0, opacity=0.75)
    return _base(
        fig,
        title=dict(text="スコア分布"),
        xaxis=dict(tickvals=list(range(1, 11))),
        bargap=0.08,
        showlegend=False,
    )


def histogram_self_effort_distribution(df: pd.DataFrame) -> go.Figure:
    fig = px.histogram(
        df, x="self_effort_score", nbins=20,
        labels={"self_effort_score": "スコア", "count": "件数"},
        color_discrete_sequence=[EFFORT_COLOR],
    )
    fig.update_traces(marker_line_width=0, opacity=0.75)
    return _base(
        fig,
        title=dict(text="スコア分布"),
        xaxis=dict(range=[0, 100]),
        bargap=0.05,
        showlegend=False,
    )


def bar_chart_category_scores(df: pd.DataFrame) -> go.Figure:
    """カテゴリ別満足度（動画・サポート・システム）"""
    cats = {
        "video_score":   ("動画", "#4F46E5"),
        "support_score": ("サポート", "#06B6D4"),
        "system_score":  ("システム", "#10B981"),
    }

    rows = []
    for col, (label, color) in cats.items():
        if col in df.columns and df[col].notna().any():
            rows.append({"カテゴリ": label, "平均スコア": round(df[col].mean(), 2), "color": color})

    if not rows:
        fig = go.Figure()
        return _base(fig, title=dict(text="データなし"))

    fig = go.Figure()
    for row in rows:
        fig.add_trace(go.Bar(
            x=[row["カテゴリ"]],
            y=[row["平均スコア"]],
            name=row["カテゴリ"],
            marker_color=row["color"],
            marker_line_width=0,
            text=[f"{row['平均スコア']:.1f}"],
            textposition="inside",
            textfont=dict(size=13, color="white", family="Inter, sans-serif"),
            insidetextanchor="middle",
            showlegend=False,
        ))

    return _base(
        fig,
        title=dict(text="カテゴリ別スコア"),
        yaxis=dict(range=[0, 11]),
        bargap=0.3,
    )


def line_chart_category_trend(df: pd.DataFrame) -> go.Figure:
    """動画・サポート・システム 月別推移"""
    cats = {
        "video_score":   ("動画", "#4F46E5"),
        "support_score": ("サポート", "#06B6D4"),
        "system_score":  ("システム", "#10B981"),
    }

    monthly = df.assign(month=df["date"].dt.to_period("M").dt.to_timestamp())
    fig = go.Figure()

    for col, (label, color) in cats.items():
        if col not in df.columns or df[col].isna().all():
            continue
        agg = monthly.groupby("month")[col].mean().round(2).reset_index()
        fig.add_trace(go.Scatter(
            x=agg["month"], y=agg[col],
            name=label,
            mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=7, color=color, line=dict(width=2, color="white")),
            hovertemplate="%{x|%Y年%m月}<br>" + label + ": <b>%{y:.1f}</b><extra></extra>",
        ))

    fig.add_hline(
        y=8, line_dash="dot", line_color="#CBD5E1", line_width=1.5,
        annotation_text="目標 8.0", annotation_font_size=10,
        annotation_font_color="#94A3B8", annotation_position="top right",
    )
    return _base(
        fig,
        title=dict(text="カテゴリ別 月別推移"),
        yaxis=dict(range=[0, 10.5]),
        hovermode="x unified",
    )
