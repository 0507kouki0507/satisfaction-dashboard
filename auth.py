"""ログイン認証ロジック"""

from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


def load_auth_config() -> dict:
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path) as f:
        return yaml.load(f, Loader=SafeLoader)


def setup_authenticator() -> tuple[stauth.Authenticate, dict]:
    config = load_auth_config()
    authenticator = stauth.Authenticate(
        config["credentials"],
        cookie_name=config["cookie"]["name"],
        cookie_key=config["cookie"]["key"],
        cookie_expiry_days=config["cookie"]["expiry_days"],
        auto_hash=True,
    )
    return authenticator, config


def show_login_page() -> tuple[str | None, bool, str | None]:
    """
    ログイン画面を表示し、認証状態を返す。

    Returns:
        (name, authentication_status, username)
    """
    authenticator, _ = setup_authenticator()

    name, authentication_status, username = authenticator.login(
        location="main",
        fields={
            "Form name": "顧客満足度ダッシュボード ログイン",
            "Username": "ユーザー名",
            "Password": "パスワード",
            "Login": "ログイン",
        },
    )

    if authentication_status is False:
        st.error("ユーザー名またはパスワードが正しくありません")
    elif authentication_status is None:
        st.info("ユーザー名とパスワードを入力してください")

    return name, authentication_status, username


def show_logout_button(authenticator: stauth.Authenticate) -> None:
    authenticator.logout("ログアウト", location="sidebar")
