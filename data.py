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

# 想定列名マッピング（実際のシートの列名 → 正規化後の列名）
COLUMN_MAP = {
    "日付": "date",
    "date": "date",
    "Date": "date",
    "プロジェクト名": "project_name",
    "project_name": "project_name",
    "Project": "project_name",
    "満足度スコア": "score",
    "score": "score",
    "score_1_to_10": "score",
    "Score": "score",
    "自身の取り組み": "self_effort_score",
    "self_effort_score": "self_effort_score",
    "取り組みスコア": "self_effort_score",
    "NPSスコア": "nps_score",
    "nps_score": "nps_score",
    "NPS": "nps_score",
    "コメント": "comment",
    "comment": "comment",
    "Comment": "comment",
    "受講生数": "total_students",
    "total_students": "total_students",
    "回答者数": "respondents",
    "respondents": "respondents",
}

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
        total = rng.randint(80, 150)
        for month_offset in range(12):
            date = pd.Timestamp("2025-03-01") + pd.DateOffset(months=month_offset)
            respondents = rng.randint(int(total * 0.5), total)
            for _ in range(respondents // 10):
                rows.append({
                    "date": date,
                    "project_name": project,
                    "score": round(rng.gauss(8.1, 1.2), 1),
                    "self_effort_score": round(rng.gauss(72, 15), 0),
                    "nps_score": rng.randint(1, 10),
                    "comment": rng.choice(_DEMO_COMMENTS) if rng.random() > 0.6 else None,
                    "total_students": total,
                    "respondents": respondents,
                })

    df = pd.DataFrame(rows)
    df["score"] = df["score"].clip(1, 10)
    df["self_effort_score"] = df["self_effort_score"].clip(1, 100)
    return df.sort_values("date").reset_index(drop=True)


def _is_demo_mode() -> bool:
    """secrets に Google 認証情報が設定されていない場合はデモモードで動作する"""
    try:
        _ = st.secrets["gcp_service_account"]
        key = st.secrets["gcp_service_account"].get("private_key", "")
        return not key or "YOUR_PRIVATE_KEY" in key
    except Exception:
        return True


def _get_gspread_client() -> gspread.Client:
    credentials_info: dict[str, Any] = dict(st.secrets["gcp_service_account"])
    credentials = Credentials.from_service_account_info(
        credentials_info, scopes=SCOPES
    )
    return gspread.authorize(credentials)


def _normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """列名を正規化し、型変換を行う"""
    df = df.rename(columns={col: COLUMN_MAP[col] for col in df.columns if col in COLUMN_MAP})

    required_cols = ["date", "project_name", "score", "self_effort_score", "nps_score", "comment", "total_students", "respondents"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = pd.NA

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df["self_effort_score"] = pd.to_numeric(df["self_effort_score"], errors="coerce")
    df["nps_score"] = pd.to_numeric(df["nps_score"], errors="coerce")
    df["total_students"] = pd.to_numeric(df["total_students"], errors="coerce")
    df["respondents"] = pd.to_numeric(df["respondents"], errors="coerce")

    df = df.dropna(subset=["date", "score"])
    return df[required_cols]


@st.cache_data(ttl=300)
def load_all_data() -> pd.DataFrame:
    """
    secrets.toml に登録された全スプレッドシートからデータを取得し、
    結合した DataFrame を返す。5分ごとに自動更新。
    Google 認証情報が未設定の場合はデモデータを返す。
    """
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
        return pd.DataFrame(columns=["date", "project_name", "score", "self_effort_score", "nps_score", "comment", "total_students", "respondents"])

    combined = pd.concat(dfs, ignore_index=True)
    combined = combined.sort_values("date").reset_index(drop=True)
    return combined


def filter_data(
    df: pd.DataFrame,
    projects: list[str] | None = None,
    months: list[str] | None = None,
) -> pd.DataFrame:
    """フィルター条件でデータを絞り込む"""
    result = df.copy()

    if projects:
        result = result[result["project_name"].isin(projects)]

    if months:
        result = result[result["date"].dt.strftime("%Y-%m").isin(months)]

    return result


def get_response_rate(df: pd.DataFrame) -> float:
    """回答率を計算する（回答者数 / 受講生数）"""
    total = df["total_students"].sum()
    responded = df["respondents"].sum()
    if total == 0 or pd.isna(total):
        return 0.0
    return float(responded / total * 100)


def get_nps_score(df: pd.DataFrame) -> float | None:
    """NPS スコアを計算する（推薦者割合 - 批判者割合）"""
    nps_vals = df["nps_score"].dropna()
    if nps_vals.empty:
        return None
    promoters = (nps_vals >= 9).sum()
    detractors = (nps_vals <= 6).sum()
    total = len(nps_vals)
    return float((promoters - detractors) / total * 100)
