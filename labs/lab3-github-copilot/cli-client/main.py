import os
import sys
from pathlib import Path
from urllib.parse import urlparse

from azure.ai.projects import AIProjectClient
from azure.core.exceptions import AzureError, ClientAuthenticationError
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APIStatusError,
    AuthenticationError,
    NotFoundError,
    OpenAIError,
    PermissionDeniedError,
    omit,
)


def main() -> int:
    try:
        load_dotenv(
            dotenv_path=Path(__file__).resolve().parent / ".env",
            override=False,
            encoding="utf-8-sig",
        )
    except (OSError, UnicodeError) as error:
        print(f"設定エラー: .env を読み込めませんでした: {error}", file=sys.stderr)
        return 1

    endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT", "").strip()
    agent_name = os.environ.get("FOUNDRY_AGENT_NAME", "").strip()
    missing = [
        name
        for name, value in (
            ("FOUNDRY_PROJECT_ENDPOINT", endpoint),
            ("FOUNDRY_AGENT_NAME", agent_name),
        )
        if not value
    ]
    if missing:
        print(
            f"設定エラー: {', '.join(missing)} を設定してください。"
            ".env.example と README.md を参照してください。",
            file=sys.stderr,
        )
        return 1

    try:
        parsed = urlparse(endpoint)
    except ValueError as error:
        print(
            f"設定エラー: FOUNDRY_PROJECT_ENDPOINT が不正です: {error}",
            file=sys.stderr,
        )
        return 1
    if parsed.scheme != "https" or not parsed.netloc:
        print(
            "設定エラー: FOUNDRY_PROJECT_ENDPOINT には HTTPS の"
            "プロジェクト URL を指定してください。例: "
            "https://<resource>.services.ai.azure.com/api/projects/<project>",
            file=sys.stderr,
        )
        return 1

    try:
        with (
            DefaultAzureCredential() as credential,
            AIProjectClient(endpoint=endpoint, credential=credential) as project,
            project.get_openai_client(timeout=120.0, max_retries=0) as client,
        ):
            print(f"{agent_name} との対話を開始します。終了するには 'exit' と入力してください。")
            previous_response_id: str | None = None
            while True:
                try:
                    message = input("あなた> ").strip()
                except EOFError:
                    print()
                    break
                if message.lower() == "exit":
                    break
                if not message:
                    continue

                response = client.responses.create(
                    input=message,
                    previous_response_id=(
                        previous_response_id
                        if previous_response_id is not None
                        else omit
                    ),
                    extra_body={
                        "agent_reference": {
                            "name": agent_name,
                            "type": "agent_reference",
                        }
                    },
                )
                if response.status != "completed":
                    print(
                        f"エージェントの応答が完了しませんでした（状態: {response.status}）。"
                        f"詳細: {response.error or response.incomplete_details}。"
                        "会話の参照は更新していません。もう一度入力してください。",
                        file=sys.stderr,
                    )
                    continue

                previous_response_id = response.id
                if response.output_text:
                    print(f"{agent_name}> {response.output_text}")
                else:
                    print(
                        "エージェントの応答は完了しましたが、テキストがありません。"
                        "エージェントの設定とツールを確認してください。",
                        file=sys.stderr,
                    )
    except KeyboardInterrupt:
        print("\n対話を中断しました。")
        return 130
    except (ClientAuthenticationError, AuthenticationError) as error:
        print(
            "認証に失敗しました。適切なアカウントで 'az login' を実行するか、"
            f"DefaultAzureCredential の認証設定を確認してください: {error}",
            file=sys.stderr,
        )
        return 1
    except PermissionDeniedError as error:
        print(
            f"アクセスが拒否されました。Foundry プロジェクトのロール割り当てを確認してください: {error}",
            file=sys.stderr,
        )
        return 1
    except NotFoundError as error:
        print(
            "プロジェクトまたはエージェントが見つかりません。FOUNDRY_PROJECT_ENDPOINT と "
            f"FOUNDRY_AGENT_NAME を確認してください: {error}",
            file=sys.stderr,
        )
        return 1
    except APIConnectionError as error:
        print(
            "接続に失敗したか、タイムアウトしました。ネットワークとプロジェクトの"
            f"エンドポイントを確認してから再起動してください: {error}",
            file=sys.stderr,
        )
        return 1
    except APIStatusError as error:
        print(
            f"Foundry へのリクエストが失敗しました（HTTP {error.status_code}）。"
            f"HTTP 429 の場合は、時間をおいてから再起動してください: {error}",
            file=sys.stderr,
        )
        return 1
    except (AzureError, OpenAIError) as error:
        print(f"Foundry SDK エラー: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
