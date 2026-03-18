"""Google Sheets データ取得・整形"""

import random
from typing import Any

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]

# 実際のシート列名 → 正規化後の列名
COLUMN_MAP = {
    # 日付
    "回答日時": "date",
    "日付": "date",
    "date": "date",
    "Date": "date",
    # プロジェクト名（列があれば使う、なければシート名を使う）
    "プロジェクト名": "project_name",
    "project_name": "project_name",
    # 取り組み度（100点満点）
    "ここまでの学習を振り返ってみて、あなたの取り組み方は何点でしたか？（100点満点中）": "self_effort_score",
    "自身の取り組み": "self_effort_score",
    "self_effort_score": "self_effort_score",
    "取り組みスコア": "self_effort_score",
    # 満足度カテゴリ（各10段階）
    "動画カリキュラムの満足度はいかがですか？（10段階）": "video_score",
    "video_score": "video_score",
    "サポートの満足度はいかがですか？（10段階）": "support_score",
    "support_score": "support_score",
    "システムの使いやすさはいかがですか？（10段階）": "system_score",
    "system_score": "system_score",
    # 総合満足度（列があれば使う。なければ上の3つから計算）
    "満足度スコア": "score",
    "score": "score",
    "score_1_to_10": "score",
    # NPS（友人への推薦度 0〜10）
    "あなたは当校をどの程度友人や知人に勧めますか？": "nps_score",
    "NPSスコア": "nps_score",
    "nps_score": "nps_score",
    "NPS": "nps_score",
    # コメント（動画カリキュラム改善点を主コメントとして使用）
    "動画カリキュラムについて、改善点や加えてほしい箇所などがあれば、お聞かせください。": "comment",
    "コメント": "comment",
    "comment": "comment",
    # 受講生数・回答者数（列があれば使う）
    "受講生数": "total_students",
    "total_students": "total_students",
    "回答者数": "respondents",
    "respondents": "respondents",
}

REQUIRED_COLS = [
    "date", "project_name",
    "score", "video_score", "support_score", "system_score",
    "self_effort_score", "nps_score",
    "comment", "total_students", "respondents",
]

_DEMO_COMMENTS = [
    "説明がわかりやすく、実践的な内容で大変満足しています。",
    "課題のフィードバックが丁寧で助かりました。",
    "もう少し応用例を増やしてほしいです。",
    "質問への返答が早くてよかったです。",
    "動画の音質を改善してほしいです。",
    "グループワークが楽しく、同期との交流が増えました。",
    "教材のボリュームがちょうどよかったです。",
    "次のコースも受講したいと思います。",
    "スケジュールが少しタイトでした。",
    "サポートが充実していて安心して学べました。",
]


def _generate_demo_data() -> pd.DataFrame:
    """Google Sheets なしで動作確認できるデモデータを生成する"""
    rng = random.Random(42)
    projects = ["Pythonコース", "データ分析コース", "AIコース"]
    rows = []
    for project in projects:
        for month_offset in range(12):
            date = pd.Timestamp("2025-03-01") + pd.DateOffset(months=month_offset)
            for _ in range(rng.randint(8, 15)):
                v = round(rng.gauss(7.8, 1.2), 1)
                s = round(rng.gauss(8.2, 1.0), 1)
                sy = round(rng.gauss(7.5, 1.3), 1)
                rows.append({
                    "date": date,
                    "project_name": project,
                    "video_score": max(1, min(10, v)),
                    "support_score": max(1, min(10, s)),
                    "system_score": max(1, min(10, sy)),
                    "self_effort_score": max(1, min(100, round(rng.gauss(72, 15)))),
                    "nps_score": rng.randint(0, 10),
                    "comment": rng.choice(_DEMO_COMMENTS) if rng.random() > 0.55 else None,
                    "total_students": pd.NA,
                    "respondents": pd.NA,
                })

    df = pd.DataFrame(rows)
    df["score"] = df[["video_score", "support_score", "system_score"]].mean(axis=1).round(2)
    return df.sort_values("date").reset_index(drop=True)


def _is_demo_mode() -> bool:
    try:
        key = st.secrets["gcp_service_account"].get("private_key", "")
        return not key or "YOUR_PRIVATE_KEY" in key
    except Exception:
        return True


def _get_gspread_client() -> gspread.Client:
    credentials_info: dict[str, Any] = dict(st.secrets["gcp_service_account"])
    credentials = Credentials.from_service_account_info(credentials_info, scopes=SCOPES)
    return gspread.authorize(credentials)


def _normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """列名を正規化し、型変換・スコア計算を行う"""
    df = df.rename(columns={col: COLUMN_MAP[col] for col in df.columns if col in COLUMN_MAP})

    for col in REQUIRED_COLS:
        if col not in df.columns:
            df[col] = pd.NA

    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    for col in ["score", "video_score", "support_score", "system_score",
                "self_effort_score", "nps_score", "total_students", "respondents"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # video/support/system の3つから総合スコアを計算（score列がなければ）
    sub_scores = ["video_score", "support_score", "system_score"]
    if df["score"].isna().all():
        df["score"] = df[sub_scores].mean(axis=1)

    df = df.dropna(subset=["date", "score"])
    return df[REQUIRED_COLS]


@st.cache_data(ttl=300)
def load_all_data() -> pd.DataFrame:
    """全スプレッドシートからデータを取得し結合する。5分ごとに自動更新。"""
    if _is_demo_mode():
        return _generate_demo_data()

    client = _get_gspread_client()
    spreadsheet_ids: list[str] = list(st.secrets["sheets"]["spreadsheet_ids"])

    dfs: list[pd.DataFrame] = []
    for sheet_id in spreadsheet_ids:
        try:
            spreadsheet = client.open_by_key(sheet_id)
            for worksheet in spreadsheet.worksheets():
                records = worksheet.get_all_records()
                if not records:
                    continue
                df = pd.DataFrame(records)
                df = _normalize_dataframe(df)
                if df["project_name"].isna().all():
                    df["project_name"] = worksheet.title
                dfs.append(df)
        except Exception as e:
            st.warning(f"スプレッドシート {sheet_id} の読み込みに失敗しました: {e}")

    if not dfs:
        return pd.DataFrame(columns=REQUIRED_COLS)

    combined = pd.concat(dfs, ignore_index=True)
    return combined.sort_values("date").reset_index(drop=True)


def filter_data(
    df: pd.DataFrame,
    projects: list[str] | None = None,
    years: list[int] | None = None,
    months: list[int] | None = None,
) -> pd.DataFrame:
    result = df.copy()
    if projects:
        result = result[result["project_name"].isin(projects)]
    if years:
        result = result[result["date"].dt.year.isin(years)]
    if months:
        result = result[result["date"].dt.month.isin(months)]
    return result


def get_response_rate(df: pd.DataFrame) -> float:
    """回答率（total_students がある場合のみ計算）"""
    total = df["total_students"].sum()
    responded = df["respondents"].sum()
    if pd.isna(total) or total == 0:
        return 0.0
    return float(responded / total * 100)


def get_nps_score(df: pd.DataFrame) -> float | None:
    """NPS スコア（推薦者% − 批判者%）"""
    vals = df["nps_score"].dropna()
    if vals.empty:
        return None
    promoters = (vals >= 9).sum()
    detractors = (vals <= 6).sum()
    return float((promoters - detractors) / len(vals) * 100)
