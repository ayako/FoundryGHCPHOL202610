# Lab 3: GitHub Copilot でエージェントを呼び出す

> Lab 2 で作ったエージェントを呼び出すクライアントを、GitHub Copilot に書かせます。コードを自分で書くのではなく、**エージェントに書かせる** 体験が目的です。

セットアップ・演習の流れは [ルート README](../../README.md) を参照してください。

---

> ⚠️ **シェル環境について**: 本 Lab のコマンド例は **PowerShell** を前提としています。macOS / Linux / Codespaces (bash, zsh) の方は、環境変数の設定 (`$env:VAR="..."` → `export VAR=...`) などを読み替えて実行してください。Codespaces の起動・認証手順は [事前準備](../../setup.md#codespaces-を使う場合任意) を参照してください。

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
| GitHub Copilot | ライセンス割り当て済み | VS Code 右下の Copilot アイコン |
| GitHub アカウント | 組織に参加済み | `gh auth status` |
| Foundry プロジェクト | Lab 2 完了済み | エージェント一覧に 4 体 |

### GitHub Copilot のサインイン確認

#### 手順

1. VS Code を開く
2. 画面右下のステータスバーにある **Copilot アイコン** をクリック
3. サインイン済みであることを確認する

**✅ 成功確認:**
- Copilot アイコンにエラーマーク（斜線）が付いていない
- 左サイドバーに **Copilot Chat** のアイコンが表示されている

> ⚠️ **サインインできない場合**: 組織のライセンス割り当てが済んでいない可能性があります。講師にお声がけください。

---

## 演習 0: 接続情報を控える (5min)

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

### 0.2 エージェント ID を取得する

#### 手順

1. 左ナビゲーションの **「エージェント」** をクリック
2. **「受付エージェント」** を選択する
3. 設定パネル上部の **エージェント ID**（`asst_` で始まる文字列）をコピーする

**✅ 成功確認:**
- `asst_` で始まる文字列が取得できた

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

---

## 演習 1: エージェントモードでクライアントを生成する (20min)

### 1.1 エージェントモードを開く

#### 手順

1. VS Code の左サイドバーで **Copilot Chat** アイコンをクリック
2. チャットパネル上部のモード切替から **「エージェント」** (Agent) を選択する

**✅ 成功確認:**
- 入力欄の上に「エージェント」と表示されている
- 送信ボタンの横にツールのアイコンが表示される

> 💡 **モードの違い**: 「質問」モードは会話のみ、「編集」モードは指定したファイルを編集します。**「エージェント」モードはファイルの作成・コマンド実行まで自律的に行います。** 今回はこれを使います。

### 1.2 プロンプトを投げる

#### 手順

Copilot Chat の入力欄に、次をそのまま貼り付けて送信します。

```text
Microsoft Foundry の Agent Service に接続して、対話できる CLI クライアントを Python で作ってください。

要件:
- azure-ai-projects と azure-identity を使う
- 認証は DefaultAzureCredential
- 接続先は環境変数から読む
  - FOUNDRY_PROJECT_ENDPOINT: プロジェクトのエンドポイント
  - FOUNDRY_AGENT_ID: 呼び出すエージェントの ID
- 起動したら対話ループに入り、ユーザーの入力をエージェントに送って応答を表示する
- "exit" と入力したら終了する
- エラー時は分かりやすいメッセージを表示する
- requirements.txt と .env.example も一緒に作ってください
- .gitignore を作り、.env、仮想環境、Python のキャッシュを Git の対象から除外してください（.env.example は残す）
- README.md に使い方を書いてください
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

> ⚠️ **このハンズオンのルート `.gitignore` は、演習 4 で作る別リポジトリには適用されません。** `sunlight-client` 内にも `.gitignore` が作られていることを確認してください。

> 💡 **一発で完璧なコードは出ません**: それで構いません。**動かして、エラーを見て、直させる** のがこの演習の主題です。

### 1.3 生成されたコードを読む

#### 手順

1. `main.py` を開く
2. 次の観点で目を通す

| 観点 | 確認すること |
|------|---------|
| 認証 | `DefaultAzureCredential` を使っているか |
| 接続 | エンドポイントを環境変数から読んでいるか |
| 対話 | スレッド（会話）を作成・再利用しているか |
| 終了 | `exit` で抜けられるか |

> ⚠️ **ここで理解しようとしすぎないでください。** 分からない箇所があれば、次のように Copilot に聞けば答えます。
>
> ```
> main.py の 23 行目で何をしているか説明してください。
> ```

### 1.4 環境変数を設定して実行する

#### 手順

```powershell
# 依存パッケージをインストール
pip install -r requirements.txt

# Azure にサインイン
az login

# 環境変数を設定（演習 0 で控えた値）
$env:FOUNDRY_PROJECT_ENDPOINT = "https://<リソース名>.services.ai.azure.com/api/projects/<プロジェクト名>"
$env:FOUNDRY_AGENT_ID = "asst_xxxxxxxxxxxx"

# 実行
python main.py
```

Codespaces / macOS / Linux の bash では、環境変数を次のように設定します（`pip install` と `az login --use-device-code` も Codespace 内で実行します）。

```bash
export FOUNDRY_PROJECT_ENDPOINT="https://<リソース名>.services.ai.azure.com/api/projects/<プロジェクト名>"
export FOUNDRY_AGENT_ID="asst_xxxxxxxxxxxx"
python main.py
```

**✅ 期待される出力:**

```
サンライト株式会社 お客様相談室アシスタント
終了するには exit と入力してください。

> 詰め替えの保管期限は？
[FAQ回答エージェント]
詰め替え後は6か月以内を目安にお使いください。
（出典: 製品FAQ_アクアクリア）

>
```

> ⚠️ **エラーが出たら、そのまま Copilot に貼ってください。** 次の演習 2 がまさにその作業です。

---

## 演習 2: エラーを直させる・テストを書かせる (15min)

### 2.1 エラーを Copilot に投げる

演習 1.4 でエラーが出た場合、**エラーメッセージ全文をコピーして** Copilot Chat に貼り付けます。

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
| `PermissionDenied` | ロールが割り当てられていない（講師に連絡） |

### 2.2 わざとエラーを作って直させる

正常に動いた方は、意図的に壊してから直させてみてください。

#### 手順

1. `main.py` の中で、環境変数名を 1 文字変更する（例: `FOUNDRY_AGENT_ID` → `FOUNDRY_AGENT_IDX`）
2. 実行してエラーを出す
3. エラーを Copilot に貼って直させる

> 💡 **Copilot はエラーメッセージを読んで原因を特定します。** 人間と同じです。エラーを隠さず、全文を渡すほど精度が上がります。

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
pip install pytest
pytest -v
```

**✅ 期待される出力:**

```
tests/test_main.py::test_missing_endpoint PASSED
tests/test_main.py::test_missing_agent_id PASSED
tests/test_main.py::test_chat_sends_message PASSED

========== 3 passed in 0.42s ==========
```

> 💡 **テストが落ちたら、それも Copilot に投げてください。** テストを直すのか、実装を直すのかも含めて提案してきます。

---

## 演習 3: Copilot CLI でターミナルから指示する (10min)

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

## 演習 4: Issue から PR までを一周する (10min)

### 4.1 リポジトリを作成する

#### 手順

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

### 4.2 Issue を立てる

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

## 演習 5: デプロイを見る（デモ）

> ⚠️ **この演習は手を動かしません。** 講師のデモをご覧ください。

実際の業務では、作ったエージェントをアプリに組み込み、運用します。デモでは次をご紹介します。

| 項目 | 内容 |
|------|------|
| アプリへの組み込み | Web アプリからエージェントを呼び出す構成 |
| 運用の可視化 | Tracing / Application Insights でトークン数・レイテンシ・ツール呼び出しを追跡 |
| コスト | 1 回の応答あたりのトークン消費と、月次の概算 |
| Fabric 連携 | 文書は Foundry、数字は Fabric という役割分担 |

---

## 📝 まとめ

| やったこと | 使った技術 |
|------|------|
| ゼロからクライアントを生成した | VS Code エージェントモード |
| エラーを貼って直させた | Copilot Chat |
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

**原因**: プロジェクトエンドポイントの末尾にスラッシュが付いている、またはエージェント ID が誤っている。

**解決方法**:
1. エンドポイントの末尾の `/` を削除する
2. エージェント ID が `asst_` で始まっているか確認する
3. 環境変数が正しく設定されているか確認する

```powershell
echo $env:FOUNDRY_PROJECT_ENDPOINT
echo $env:FOUNDRY_AGENT_ID
```

### エラー: `ModuleNotFoundError: No module named 'azure'`

**原因**: 依存パッケージがインストールされていない。

**解決方法**:

```powershell
pip install -r requirements.txt
```

仮想環境を使っている場合は、有効化されているか確認してください。

### Copilot がファイルを作成してくれない

**原因**: モードが「質問」になっている。

**解決方法**: チャットパネル上部のモード切替で **「エージェント」** を選択してください。「質問」モードは回答のみで、ファイル操作は行いません。

### Copilot の提案が的外れ

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
2. 切り分けのため、環境変数 `FOUNDRY_AGENT_ID` を **FAQ回答エージェント** の ID に変更して試す
3. それで速ければ、マルチエージェント構成による遅延です（正常な挙動です）
