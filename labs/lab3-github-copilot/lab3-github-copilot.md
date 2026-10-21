# Lab 3: GitHub Copilot でエージェントを呼び出す

> Lab 2 で作ったエージェントを呼び出すクライアントを、GitHub Copilot に書かせます。コードを自分で書くのではなく、**エージェントに書かせる** 体験が目的です。

セットアップ・演習の流れは [ルート README](../../README.md) を参照してください。

---

> ⚠️ **Shell 環境について**: 本 Lab のコマンド例は **PowerShell** を前提としています。macOS / Linux / Codespaces (bash, zsh) の方は、環境変数の設定 (`$env:VAR="..."` → `export VAR=...`) などを読み替えて実行してください。Codespaces の起動・認証手順は [事前準備](../../setup.md#codespaces-を使う場合任意) を参照してください。

> ❗ **前提**: [Lab 2](../lab2-knowledge-and-multiagent/README.md) が完了し、受付エージェントが動作していること。

## 🎯 このパートのゴール

- **VS Code のエージェントモード** で、ゼロからコードを生成させる
- 生成されたコードに対して、**テストを書かせる／エラーを直させる**
- **Copilot CLI** で、ターミナルからファイル横断の作業を指示する
- **Issue → 修正 → PR** までの一連の流れを Copilot と進める
- Foundry と GitHub Copilot の役割分担を理解する

## 📋 前提条件

| 項目 | 要件 | 確認方法 |
|------|------|---------|
| Python | 3.11 以上 | `python --version` |
| VS Code | GitHub Copilot 拡張機能インストール済み | 拡張機能パネルで確認 |
| GitHub Copilot | Copilot Free または有料／組織プランが利用可能 | [登録・制限の確認](../../setup.md#3-github-copilot-のサインイン) |
| GitHub アカウント | 自分の演習用リポジトリを作成できる（組織への参加は不要） | `gh auth status` |
| Foundry プロジェクト | Lab 2 完了済み | エージェント一覧に 4 体 |

### GitHub Copilot にサインインする

#### 手順

1. VS Code を開く
2. タイトルバーの **Chat** ボタンをクリックしてチャットを開く
3. 未サインインの場合は、表示される GitHub へのサインイン案内に従う。案内が表示されない場合は、VS Code の **アカウント** メニューから **「Sign in with GitHub to use GitHub Copilot」** を選択する（表示名は UI の言語やバージョンによって異なります）
4. ブラウザーで、Copilot を利用する GitHub アカウントにサインインし、VS Code からの認証要求を確認して承認する
5. VS Code に戻り、Copilot の利用開始やプラン選択を求められた場合は画面の案内に従う。すでにサインイン済みの場合は、利用中のアカウントとプランを確認する

**✅ 成功確認:**
- VS Code のアカウントメニューで、使用する GitHub アカウントにサインイン済みであることを確認できる
- チャットで **Ask** を選び、「こんにちは」と送信すると応答が返る

> 💡 **サインイン先は用途ごとに異なります**: ここでは VS Code の GitHub Copilot にサインインします。`gh auth login`（GitHub CLI）、Copilot CLI の認証、`az login`（Azure CLI）は別途必要です。各ツールの演習で、それぞれの認証状態を確認してください。

> ⚠️ **サインインできない場合**: [Copilot Free の登録・サインイン手順](../../setup.md#3-github-copilot-のサインイン) を確認してください。組織プランでは管理者にライセンス・ポリシーを確認します。Free の利用枠や機能制限によって、演習を中断する必要がある場合があります。

---

## 演習 0: 接続情報を記録する（5 分）

Copilot にコードを書かせる前に、Foundry への接続情報を手元に用意します。

### 0.1 プロジェクトエンドポイントを取得する

#### 手順

1. [Microsoft Foundry ポータル](https://ai.azure.com/) でプロジェクトを開く
2. 左ナビゲーションの **「概要」** (Overview) をクリック
3. **「Microsoft Foundry プロジェクト エンドポイント」** の値をコピーする

```
https://<リソース名>.services.ai.azure.com/api/projects/<プロジェクト名>
```

**✅ 成功確認:**
- `https://` で始まり `/api/projects/` を含む URL が取得できた

> ⚠️ **末尾にスラッシュを付けないでください。** 付いているとエラーになります。

### 0.2 エージェント名を確認する

#### 手順

1. 左ナビゲーションの **「エージェント」** をクリック
2. **`ReceptionAgent`** を選択する
3. 呼び出すエージェントの名前が `ReceptionAgent` であることを確認する

**✅ 成功確認:**
- 呼び出し先のエージェント名 `ReceptionAgent` を確認できた

> ⚠️ **Entra エージェント ID と呼び出し先の指定は別です。** Entra エージェント ID は認証・権限設定に使う ID です。この Lab では、Foundry Agent の Responses API を使い、プロジェクトエンドポイントとエージェント名で呼び出し先を指定します。

### 0.3 作業フォルダを用意する

#### 手順

```powershell
# 作業用フォルダを作成
mkdir sunlight-client
cd sunlight-client

# VS Code で開く
code .
```

> 💡 **Codespaces の場合**: リポジトリ配下で `sunlight-client` を作成し、ブラウザ版 VS Code のエクスプローラーからフォルダを開いてください。ターミナルでは `cd sunlight-client` で作業を続けます。

**✅ 成功確認:**
- VS Code で空のフォルダが開いている

### 0.4 MCP サーバーを設定する（任意）

MCP（Model Context Protocol）サーバーを設定すると、Agent モードの Copilot が外部のツールや情報源を利用できます。ここでは次の 4 つを追加します。

| サーバー | 用途 | 接続方式 | 認証・前提 |
|---|---|---|---|
| **Microsoft Learn** | 公式ドキュメントの検索。演習 1 で SDK の最新仕様を確認する際に役立ちます | HTTP（リモート） | 不要 |
| **Azure MCP Server** | Azure リソースやロール割り当ての確認、Azure ドキュメントの参照 | `npx`（ローカル） | `az login` 済みであること。Node.js（LTS）が必要 |
| **Foundry MCP Server**（プレビュー） | Foundry のモデル、エージェント、評価の参照・操作 | HTTP（リモート） | Microsoft Entra ID でサインイン。対象プロジェクトの Contributor 以上のロールが必要 |
| **GitHub MCP Server** | リポジトリ、Issue、PR の参照・操作。演習 4 で使えます | HTTP（リモート） | GitHub アカウントで承認 |

#### 手順

1. Node.js の LTS 版が入っていることを確認する（Azure MCP Server で使用）

   ```powershell
   node --version
   ```

2. コマンドパレット（Windows／Linux: `Ctrl+Shift+P`、macOS: `Command+Shift+P`）を開き、**「MCP: ユーザー構成を開く** (Open User Configuration) **」** を実行する
3. 開いた `mcp.json` に、次の内容を記載、保存する。すでに `servers` がある場合は、足りない項目だけを追加する

   ```json
   {
     "servers": {
       "MSLearn": {
         "type": "http",
         "url": "https://learn.microsoft.com/api/mcp"
       },
       "AzureMCP": {
         "type": "stdio",
         "command": "npx",
         "args": ["-y", "@azure/mcp@latest", "server", "start"]
       },
       "FoundryMCP": {
         "type": "http",
         "url": "https://mcp.ai.azure.com"
       },
       "GitHubMCP": {
         "type": "http",
         "url": "https://api.githubcopilot.com/mcp/"
       }
     }
   }
   ```

4. 各サーバー名の上に表示される **「Start」** をクリックして起動する。信頼を確認するダイアログが表示されたら、接続先を確認して **「Trust」** を選択する
5. `FoundryMCP` と `GitHubMCP` では、ブラウザーでのサインインや承認を求められる。Lab で使うアカウントで承認する
6. Chat を開き、モードで **「Agent」** を選択する
7. チャット入力欄の **「ツールの構成」**（ツールのアイコン）をクリックし、4 つのサーバーのツールが有効になっていることを確認する

**✅ 成功確認:**
- コマンドパレットの **「MCP: List Servers」** で、4 つのサーバーが **Running** と表示される
- ツールの一覧に、各サーバーのツールが表示される
- Agent で次のように送信すると、対応する MCP ツールの使用確認が表示される
  - 「Microsoft Learn で azure-ai-projects の Responses API の使い方を調べて」
  - 「Azure のサブスクリプションを一覧して」
  - 「Foundry のプロジェクトにあるエージェントを一覧して」
  - 「GitHub で自分のリポジトリを一覧して」

> 💡 **設定の保存先**: **MCP: ユーザー構成を開く** ではすべてのワークスペースで使うユーザー設定を開いています。特定のリポジトリだけで使う場合は、**MCP: ワークスペースフォルダーMCP構成を開く** (Open Workspace Folder MCP Configuration) で `.vscode/mcp.json` を作成します。サーバーは **MCP: Add Server** のガイドや、拡張機能ビューの `@mcp` 検索からも追加できます。

> ⚠️ **MCP サーバーは信頼できるものだけを追加してください。** MCP サーバーはツールとしてコマンドや外部サービスを呼び出す場合があります。接続先と提供元を確認し、不明なサーバーは起動しないでください。組織の管理するアカウントでは、ポリシーにより MCP が制限されている場合があります。

> 💡 **ツールが多いと動作が不安定になることがあります。** 演習中に Agent の応答が遅い、または意図しないツールが選ばれる場合は、ツールの構成で使わないサーバーを無効にしてください。

> 🚨 **接続できない場合**: Azure MCP Server は `az login` と `npx` が使えるかを確認します。Foundry MCP Server は、サインイン先のテナントとプロジェクトのロール（Contributor 以上）を確認します。GitHub MCP Server は、組織のアカウントの場合に MCP の利用ポリシーが無効になっていないか管理者に確認します。

---

## 演習 1: エージェントモードでクライアントを生成する (20min)

### 1.1 エージェントモードを開く

#### 手順

1. VS Code のタイトルバーにある **Chat** ボタンをクリックしてチャットを開く（Windows／Linux: `Ctrl+Alt+I`、macOS: `Control+Command+I`）
2. チャット入力欄のモード選択から **「Agent」** を選択する

**✅ 成功確認:**
- モード選択に **「Agent」** と表示されている
- 送信ボタンの横にツールのアイコンが表示される

> 💡 **Ask と Agent の違い**: **Ask** はコードの説明や質問への回答に使います。**Agent** はコードベースを調べ、ファイルの作成・編集やコマンド実行を進めます。今回は **Agent** を使います。ツールや操作によっては承認を求められます。

### 1.2 プロンプトを入力して送信する

#### 手順

Copilot Chat の入力欄に、次をそのまま貼り付けて送信します。

```text
Microsoft Foundry の `ReceptionAgent` と対話する Python CLI を、次のファイルに実装してください。

- 現行の安定版 `azure-ai-projects` と `azure-identity` を使う。必要な API とバージョンだけ公式ドキュメントで確認し、バージョンを `requirements.txt` に固定する
- `DefaultAzureCredential` と `AIProjectClient` を使い、Responses API からエージェント名で呼び出す。旧 classic API（`asst_`、threads、runs）は使わない
- `FOUNDRY_PROJECT_ENDPOINT` と `FOUNDRY_AGENT_NAME` を環境変数から読み、会話を継続できる CLI にする。`exit` で終了し、エラーは分かりやすく表示する
- `main.py`、`requirements.txt`、`.env.example`、`.gitignore`、`README.md` を作る。.env、`.venv`、Python キャッシュは Git 対象外にする。README に仮想環境の作成・有効化方法を書く
- 今回は依存関係のインストールや Azure への接続テストをせず、ファイル作成後に要点だけ報告する
```

**✅ 期待される挙動:**
- Copilot がファイルの作成を提案し、承認を求めてくる
- 承認すると、次のようなファイルが生成される

```
sunlight-client/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

> 💡 **最初から完成したコードが生成されるとは限りません。** 実行してエラーを確認し、修正を依頼する過程も、この演習の学習内容です。

> 💡 **SDK のバージョンは実施時に確認します**: 最新安定版を使い、必要な API の公式ドキュメントで呼び出し方法を確認してください。SDK の網羅的な調査や Azure への接続テストは、この生成手順では行いません。

### 1.3 生成されたコードを読む

#### 手順

1. `main.py` を開く
2. 次の観点で目を通す

| 観点 | 確認すること |
|------|---------|
| 認証 | `DefaultAzureCredential` を使っているか |
| 接続 | プロジェクトエンドポイントとエージェント名を環境変数から読んでいるか |
| 対話 | Responses API を使い、conversation または previous_response_id で会話を継続しているか |
| 終了 | `exit` で抜けられるか |

> ⚠️ **ここで理解しようとしすぎないでください。** 分からない箇所があれば、次のように Copilot に聞けば答えます。
>
> ```
> main.py の 23 行目で何をしているか説明してください。
> ```

### 1.4 環境変数を設定して実行する

#### 手順

```powershell
# 仮想環境を作成して有効化
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 仮想環境に依存パッケージをインストール
python -m pip install -r requirements.txt
python -m pip check

# Azure にサインイン
az login

# 環境変数を設定（演習 0 で控えた値）
$env:FOUNDRY_PROJECT_ENDPOINT = "https://<リソース名>.services.ai.azure.com/api/projects/<プロジェクト名>"
$env:FOUNDRY_AGENT_NAME = "ReceptionAgent"

# 実行
python main.py
```

Codespaces / macOS / Linux の bash では、仮想環境を作成・有効化してから実行します。Azure CLI の認証も同じ環境で行ってください。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check

az login --use-device-code

export FOUNDRY_PROJECT_ENDPOINT="https://<リソース名>.services.ai.azure.com/api/projects/<プロジェクト名>"
export FOUNDRY_AGENT_NAME="ReceptionAgent"
python main.py
```

**✅ 期待される出力:**

```
サンライト株式会社 お客様相談室アシスタント
終了するには exit と入力してください。

> 詰め替えの保管期限は？
[FaqAnswerAgent]
詰め替え後は6か月以内を目安にお使いください。
（出典: 製品FAQ_アクアクリア）

>
```

> ⚠️ **エラーが出た場合は、メッセージ全文を Copilot に共有してください。** 次の演習 2 で、その手順を実践します。

---

## 演習 2: エラーの修正とテストの作成（15 分）

### 2.1 エラーを Copilot に伝えて修正を依頼する

演習 1.4 でエラーが出た場合は、**エラーメッセージ全文をコピーして** Copilot Chat に貼り付け、修正を依頼します。

#### 手順

```text
実行したら次のエラーが出ました。原因を調べて修正してください。

<ここにエラーメッセージを貼り付け>
```

**✅ 期待される挙動:**
- Copilot が原因を説明し、修正案を提示する
- 承認すると、ファイルが書き換えられる

**よくあるエラーと対処:**

| エラー | 原因 |
|------|---------|
| `DefaultAzureCredential failed` | `az login` していない |
| `404 Not Found` | エンドポイントの末尾にスラッシュが付いている |
| `ModuleNotFoundError` | `pip install` が未実行 |
| `PermissionDenied` | Foundry 用アカウントの権限を確認する（[設定手順](../../azure-setup.md#4-foundry-用アカウントに利用権限を設定する)） |

### 2.2 わざとエラーを作って直させる

正常に動作した場合は、意図的にエラーを発生させ、Copilot に修正を依頼してください。

#### 手順

1. `main.py` の中で、環境変数名を 1 文字変更する（例: `FOUNDRY_AGENT_NAME` → `FOUNDRY_AGENT_NAMEX`）
2. 実行してエラーを出す
3. エラーメッセージ全文を Copilot に共有し、修正を依頼する

> 💡 **Copilot はエラーメッセージをもとに原因を特定します。** エラーを省略せず、全文を共有すると、より適切な修正案を得やすくなります。

### 2.3 テストコードを書かせる

#### 手順

Copilot Chat に次を送信します。

```text
main.py のユニットテストを pytest で書いてください。

- 環境変数が未設定のときに分かりやすいエラーが出ることを検証する
- エージェントへの送信部分はモックにして、実際の API は呼ばない
- tests/ フォルダに配置してください
```

**✅ 期待される挙動:**
- `tests/test_main.py` が生成される
- モックを使ったテストが書かれている

#### テストを実行する

```powershell
python -m pip install pytest
python -m pytest -v
```

**✅ 期待される出力:**

```
tests/test_main.py::test_missing_endpoint PASSED
tests/test_main.py::test_missing_agent_id PASSED
tests/test_main.py::test_chat_sends_message PASSED

========== 3 passed in 0.42s ==========
```

> 💡 **テストが失敗した場合は、エラー内容を Copilot に共有してください。** テストと実装のどちらを修正すべきかも含めて、対応案を提案します。

---

## 演習 3: Copilot CLI でターミナルから指示する（10 分）

VS Code の外でも Copilot は使えます。

### 3.1 Copilot CLI をインストールする

#### 手順

```powershell
# GitHub CLI の拡張としてインストール
gh extension install github/gh-copilot

# 動作確認
gh copilot --version
```

**✅ 成功確認:**
- バージョン番号が表示される

> ⚠️ **`gh` が見つからない場合**: [GitHub CLI](https://cli.github.com/) をインストールし、`gh auth login` でサインインしてください。

### 3.2 ファイル横断の修正を依頼する

#### 手順

```powershell
gh copilot suggest "main.py のログ出力を print から logging モジュールに置き換えて、ログレベルを環境変数 LOG_LEVEL で制御できるようにする"
```

**✅ 期待される挙動:**
- 変更内容の提案が表示される
- 実行するかどうかを尋ねられる

### 3.3 README を生成させる

#### 手順

```powershell
gh copilot suggest "このフォルダの構成を読み取って、README.md にセットアップ手順・環境変数の一覧・実行方法・トラブルシューティングを追記する"
```

> 💡 **CLI と VS Code の使い分け**: 対話しながら作り込むなら VS Code、定型作業を一括で流すなら CLI が向きます。CI やスクリプトに組み込めるのも CLI の利点です。

---

## 演習 4: Issue の作成から PR までを実践する（10 分）

### 4.1 リポジトリを作成する

#### 手順

> ⚠️ **ここで `sunlight-client` を独立した GitHub リポジトリにします。** このハンズオンのルートにある `.gitignore` は独立したリポジトリには適用されないため、演習 1.2 で `sunlight-client` 内に作成した `.gitignore` を使います。

```powershell
# Git 初期化
git init
git add .
git status --short
git commit -m "初回コミット: Foundry クライアント"

# GitHub にリポジトリを作成してプッシュ
gh repo create sunlight-client --private --source=. --push
```

> ⚠️ **`git status --short` でコミット対象を確認**し、`.env`、仮想環境、キャッシュ、Azure の認証情報が含まれていたらコミットせず、`.gitignore` を修正してから再度 `git add .` してください。`.env.example` は含めて構いません。

**✅ 成功確認:**
- `gh repo view --web` でブラウザが開き、リポジトリが表示される

### 4.2 Issue を作成する

#### 手順

```powershell
gh issue create --title "会話履歴をファイルに保存できるようにする" --body "対話の内容を JSON Lines 形式で保存し、次回起動時に読み込めるようにしたい。保存先は環境変数 HISTORY_PATH で指定する。"
```

**✅ 成功確認:**
- Issue 番号（`#1` など）が表示される

### 4.3 Copilot に実装させる

#### 手順

VS Code の Copilot Chat（エージェントモード）で次を送信します。

```text
Issue #1 の内容を実装してください。

- 対話の内容を JSON Lines 形式で保存する
- 保存先は環境変数 HISTORY_PATH で指定（未指定なら ./history.jsonl）
- 起動時に既存の履歴があれば読み込んで表示する
- 実装したらテストも追加してください
```

### 4.4 ブランチを切って PR を作る

#### 手順

```powershell
# ブランチを作成
git checkout -b feature/save-history

# 変更をコミット
git add .
git commit -m "feat: 会話履歴の保存と読み込みを追加 (#1)"

# プッシュして PR を作成
git push -u origin feature/save-history
gh pr create --fill
```

**✅ 成功確認:**
- PR の URL が表示される

### 4.5 レビューコメントを書かせる（任意）

#### 手順

```powershell
gh pr diff | gh copilot explain
```

または VS Code の Copilot Chat で：

```text
この変更のコードレビューをしてください。
バグ、エラーハンドリングの漏れ、命名の一貫性の観点で指摘してください。
```

> 💡 **Copilot はレビュアーにもなります**: 自分の書いたコードを客観的に見る目として使えます。ただし **最終判断は人間が行ってください。**

---

## 演習 5: デプロイと運用を学ぶ（任意）

> 💡 **この演習は任意です。** 講師付きの場合はデモを見学します。セルフラーニングでは、下記の参考資料で運用時に必要な観点を確認してください。追加の Azure リソースの作成は必須ではありません。

実際の業務では、作ったエージェントをアプリに組み込み、運用します。次の観点を確認します。

| 項目 | 内容 |
|------|------|
| アプリへの組み込み | Web アプリからエージェントを呼び出す構成 |
| 運用の可視化 | Tracing / Application Insights でトークン数・レイテンシ・ツール呼び出しを追跡 |
| コスト | 1 回の応答あたりのトークン消費と、月次の概算 |
| Fabric 連携 | 文書は Foundry、数字は Fabric という役割分担 |

参考資料:
- [Foundry Agent Service の概要](https://learn.microsoft.com/azure/ai-foundry/agents/overview)
- [Foundry のトレース](https://learn.microsoft.com/azure/ai-foundry/observability/concepts/trace-agent-concept)
- [Foundry の料金](https://azure.microsoft.com/pricing/details/ai-foundry/)

---

## 📝 まとめ

| やったこと | 使った技術 |
|------|------|
| ゼロからクライアントを生成した | VS Code エージェントモード |
| エラー内容を共有して修正を依頼した | Copilot Chat |
| ユニットテストを書かせた | Copilot Chat / pytest |
| ターミナルから一括修正を指示した | Copilot CLI |
| Issue → 実装 → PR を一周した | GitHub CLI / Copilot |

**この Lab で分かったこと:**

- コードを **自分で書かずに、指示して作らせる** 進め方ができる
- エラーは隠さず **そのまま渡すほど** 解決が速い
- **Microsoft Foundry がエージェントを「つくる」側**、**GitHub Copilot はそれをつくる「自分」を加速する側**

## 🔗 参考リンク

- [GitHub Copilot ドキュメント](https://docs.github.com/ja/copilot)
- [VS Code のエージェントモード](https://code.visualstudio.com/docs/copilot/chat/chat-agent-mode)
- [GitHub Copilot CLI](https://docs.github.com/ja/copilot/using-github-copilot/using-github-copilot-in-the-command-line)
- [Azure AI Projects SDK (Python)](https://learn.microsoft.com/ja-jp/python/api/overview/azure/ai-projects-readme)

---

## 🚨 トラブルシューティング

### エラー: `DefaultAzureCredential failed to retrieve a token`

**原因**: Azure にサインインしていない、または別のテナントにサインインしている。

**解決方法**:

```powershell
az login --tenant <テナントID>
az account show --query "{name:name, tenantId:tenantId}" -o table
```

### エラー: `404 Not Found` / `Resource not found`

**原因**: プロジェクトエンドポイントの末尾にスラッシュが付いている、またはエージェント名が誤っている。

**解決方法**:
1. エンドポイントの末尾の `/` を削除する
2. エージェント名が対象プロジェクト内の名前（`ReceptionAgent`）と一致しているか確認する。Entra エージェント ID や旧 classic API の ID は指定しません
3. 環境変数が正しく設定されているか確認する

```powershell
echo $env:FOUNDRY_PROJECT_ENDPOINT
echo $env:FOUNDRY_AGENT_NAME
```

### エラー: `ModuleNotFoundError: No module named 'azure'`

**原因**: 依存パッケージがインストールされていない。

**解決方法**:

```powershell
python -m pip install -r requirements.txt
```

仮想環境を使っている場合は、有効化されているか確認してください。

### Copilot がファイルを作成してくれない

**原因**: モードが「質問」になっている。

**解決方法**: チャットパネル上部のモード切替で **「エージェント」** を選択してください。「質問」モードは回答のみで、ファイル操作は行いません。

### Copilot の提案が意図と異なる

**原因**: 文脈が渡っていない。

**解決方法**:
1. 対象ファイルをエディタで開いてから指示する
2. `#file:main.py` のようにファイルを明示的に参照する
3. 「何を」「なぜ」を含めて指示する（「直して」だけでは伝わりません）

### `gh: command not found`

**原因**: GitHub CLI が未インストール。

**解決方法**: [cli.github.com](https://cli.github.com/) からインストールし、`gh auth login` でサインインしてください。

### 応答が遅い / タイムアウトする

**原因**: 受付エージェントが複数の接続エージェントを順に呼んでいる。

**解決方法**:
1. 1 分ほど待つ
2. 切り分けのため、環境変数 `FOUNDRY_AGENT_NAME` を `FaqAnswerAgent` に変更して試す
3. それで速ければ、マルチエージェント構成による遅延です（正常な挙動です）

---

## 演習 1・2 の実行結果例

演習 1・2 で作成する CLI クライアントとテストコードの実行結果例を、[cli-client](./cli-client/) フォルダーに用意しています。実行方法は [サンプルの README](./cli-client/README.md) を参照してください。
