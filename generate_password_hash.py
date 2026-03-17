"""
config.yaml に設定するパスワードハッシュを生成するユーティリティスクリプト。
使い方: uv run python generate_password_hash.py
"""

import bcrypt


def hash_password(plain_password: str) -> str:
    hashed = bcrypt.hashpw(plain_password.encode(), bcrypt.gensalt())
    return hashed.decode()


if __name__ == "__main__":
    password = input("ハッシュ化するパスワードを入力してください: ")
    print(f"\nハッシュ化されたパスワード:\n{hash_password(password)}")
    print("\nこの文字列を config.yaml の password フィールドに設定してください。")
