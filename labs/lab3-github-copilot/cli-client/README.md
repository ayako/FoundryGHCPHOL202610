# ReceptionAgent Python CLI

Microsoft Foundry に作成済みの `ReceptionAgent` と対話する CLI です。
`DefaultAzureCredential` と `AIProjectClient.get_openai_client()` を使い、
Responses API の `agent_reference` にエージェント名を指定します。
classic API のエージェント ID、threads、runs は使用しません。

## 前提

- Python 3.10 以降。
- Microsoft Foundry のプロジェクトと、その中に作成済みの `ReceptionAgent`。
- プロジェクトにアクセスできる Microsoft Entra ID アカウントと適切なロール。
- ローカル認証に Azure CLI を使う場合は、Azure CLI のインストールと `az login`。
  認証には `DefaultAzureCredential` が使用できるほかの認証方法も利用できます。

## セットアップと実行（PowerShell）

このディレクトリで、利用者が次を実行してください。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

`.env` の次の値を実際のプロジェクトに合わせて編集します。

```dotenv
FOUNDRY_PROJECT_ENDPOINT=https://<resource-name>.services.ai.azure.com/api/projects/<project-name>
FOUNDRY_AGENT_NAME=ReceptionAgent
```

`FOUNDRY_PROJECT_ENDPOINT` は Foundry プロジェクトのホーム画面で確認する
`https://<resource-name>.services.ai.azure.com/api/projects/<project-name>` 形式の URL です。
モデルのエンドポイントではありません。`FOUNDRY_AGENT_NAME` は ID ではなく名前です。
両方の環境変数が必須です。

```powershell
az login
.\.venv\Scripts\python.exe main.py
```

起動時に `python-dotenv` で `main.py` と同じフォルダーの `.env` を自動読み込みします。
別の作業ディレクトリから起動しても読み込み先は変わりません。
すでに設定済みのプロセス環境変数を優先し、`.env` の値で上書きしません。
`.env` がなくても、必要な環境変数が設定済みなら実行できます。
UTF-8（BOM あり・なし）の `.env` に対応しています。

## 対話とエラー

- `あなた>` にメッセージを入力します。空入力は無視します。
- CLI の案内・エラーメッセージは日本語です。エージェントの回答と SDK のエラー詳細は原文のまま表示します。
- 完了したレスポンスの ID を次の `previous_response_id` に渡して会話を継続します。
  初回は `previous_response_id` を送信しません（`null` は API の検証エラーになります）。
  会話の参照は実行中のメモリだけに保持し、再起動時は新しい会話になります。
  サービス側のレスポンスを削除する処理は行いません。
- `exit`（大文字・小文字は区別しません）、入力の終端、または `Ctrl+C` で終了します。
- 設定不足、不正な URL、認証、権限、対象不在、通信、API のエラーは標準エラーに表示します。
  SDK の例外では終了コード `1`、`Ctrl+C` では `130`、通常終了では `0` を返します。
- 未完了・失敗レスポンスは詳細を表示して会話の参照を進めず、次の入力を受け付けます。
  完了してもテキストがない場合は、その旨を表示します。
- 通信タイムアウトは 120 秒です。意図しない二重送信を避けるため SDK の自動リトライは無効です。
  通信失敗時にはサービス側で処理された可能性があるため、再送前に状況を確認してください。

`.env`、仮想環境、Python キャッシュは `.gitignore` で除外しています。
認証情報を `.env.example` やソースコードに記載しないでください。

## ユニットテスト

テストは `tests/test_main.py` に配置しています。利用者が次を実行してください。

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest tests -q
```

必須環境変数の未設定・空白値、日本語のエラー表示、エージェント名による送信、
初回の省略値と会話継続 ID、未完了応答、空入力・終了、認証エラーを検証します。
`.env` の読み込み、認証、API クライアントをモック化しているため、
実際の `.env` や Azure アカウントは不要で、API は呼び出しません。

## 依存関係と公式リファレンス

2026-10-20 に公式ドキュメントで確認した安定版を `requirements.txt` に固定しています。

| パッケージ | バージョン |
| --- | --- |
| `azure-ai-projects` | `2.9.0` |
| `azure-identity` | `1.26.0` |
| `python-dotenv` | `1.2.1` |

OpenAI クライアントと Azure Core は `azure-ai-projects` の依存関係として導入されます。

- [Azure AI Projects Python SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-projects-readme?view=azure-python)
- [AIProjectClient と get_openai_client](https://learn.microsoft.com/en-us/python/api/azure-ai-projects/azure.ai.projects.aiprojectclient?view=azure-python)
- [エージェント名を agent_reference に指定する公式サンプル](https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/azure-functions?pivots=python#code-samples)
- [Azure Identity Python SDK](https://learn.microsoft.com/en-us/python/api/overview/azure/identity-readme?view=azure-python)
- [python-dotenv（自動読み込みと環境変数の優先順位）](https://pypi.org/project/python-dotenv/1.2.1/)

今回のファイル作成では、依存関係のインストールおよび Azure への接続テストは実施していません。
