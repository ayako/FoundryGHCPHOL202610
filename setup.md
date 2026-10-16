# 事前準備

> 当日スムーズに始められるよう、**開催前日まで** に済ませておいてください。所要 15 分程度です。

---

## 📋 参加者の事前準備

### 必須（Lab 1・Lab 2 用）

| 項目 | 要件 | 確認方法 |
|------|------|---------|
| ブラウザ | Microsoft Edge または Google Chrome の最新版 | ヘルプ → バージョン情報 |
| ネットワーク | `ai.azure.com` にアクセスできること | 下記参照 |
| Azure サブスクリプション / GitHub アカウント | お持ちのアカウントでサインイン、利用できること | 下記 **アクセス確認** を参照 |

#### アクセス確認

ブラウザで次の URL を開き、サインイン画面が表示されることを確認してください。

```
https://ai.azure.com/
```

> ⚠️ **社内プロキシでブロックされる場合があります。** 開けない場合は事前に御社情報システム部門にご相談いただくか、別途 Wi-Fi などをご利用ください。

### 必須（Lab 3 用）

ローカル PC で Lab 3 を進める場合は、次を準備してください。GitHub Codespaces を使う場合は、下の「Codespaces を使う場合」を参照してください。

| 項目 | 要件 | 確認コマンド |
|------|------|---------|
| Python | 3.11 以上 | `python --version` |
| VS Code | 最新版 | ヘルプ → バージョン情報 |
| GitHub Copilot 拡張 | インストール済み | 拡張機能パネルで確認 |
| Azure CLI | 2.60 以上 | `az version` |
| GitHub CLI | 2.x 以上 | `gh --version` |
| Git | インストール済み | `git --version` |

### Codespaces を使う場合（任意）

GitHub アカウントに Codespaces と GitHub Copilot を利用できる権限が必要です。Codespaces の利用枠・課金条件は、事前に組織の管理者へ確認してください。
(※Lab 1・2 はブラウザで Foundry ポータルを使用しますので、環境は不要です。)

1. GitHub でこのリポジトリを開き、**Code → Codespaces → Create codespace on main** を選ぶ
2. コンテナーの初回作成が完了するまで待つ（`.devcontainer/devcontainer.json` で Python 3.11、Azure CLI、GitHub CLI、VS Code 拡張を準備します）
3. Codespace の VS Code で GitHub Copilot にサインインし、ターミナルで次を確認する

```bash
python --version
az version
gh --version
gh auth status
```

4. Lab 3 で Foundry に接続する前に、**Azure サブスクリプション / Foundry が利用できるアカウント** で Codespace 内の Azure CLI にサインインする

```bash
az login --use-device-code
```

> ⚠️ **Codespaces の GitHub 認証と Azure 認証は別です。** `gh auth status` が成功しても `az login` は必要です。配布されたテナントを指定する必要がある場合は `az login --tenant <テナントID> --use-device-code` を使用してください。認証情報や `.env` を Git にコミットしないでください。

> 💡 **Codespaces のターミナルは bash です。** Lab 3 の PowerShell の環境変数設定は `$env:NAME = "値"` の代わりに `export NAME="値"` を使います。Lab 3 の作業フォルダは Codespace 内のリポジトリ配下に作り、ブラウザ版 VS Code では `code .` の代わりにエクスプローラーから開いてください。

---

## 🔧 インストール手順

### 1. Python

[python.org](https://www.python.org/downloads/) から 3.11 以上をインストールします。

```powershell
python --version
```

**✅ 期待される出力:**

```
Python 3.11.9
```

> ⚠️ **Windows の場合**: インストーラーで **「Add Python to PATH」** に必ずチェックを入れてください。

### 2. VS Code と GitHub Copilot 拡張

1. [code.visualstudio.com](https://code.visualstudio.com/) から VS Code をインストール
2. VS Code を起動し、左サイドバーの **拡張機能** アイコンをクリック
3. `GitHub Copilot` を検索してインストール
4. あわせて `GitHub Copilot Chat` もインストール
5. `Python` 拡張機能もインストール

**✅ 成功確認:**
- 画面右下のステータスバーに Copilot アイコンが表示される

### 3. GitHub Copilot のサインイン

#### 手順

1. VS Code 右下の **Copilot アイコン** をクリック
2. **「Sign in to GitHub」** を選択
3. ブラウザが開くので、GitHub アカウントで認証する

**✅ 成功確認:**
- Copilot アイコンに斜線（無効マーク）が付いていない
- 適当な Python ファイルを開いてコメントを書くと、補完が提案される

> ⚠️ **ライセンスが割り当てられていない場合**: 「No access to GitHub Copilot」と表示されます。開催前に講師までご連絡ください。

### 4. Azure CLI

```powershell
# Windows (winget)
winget install Microsoft.AzureCLI

# macOS (Homebrew)
brew install azure-cli
```

```powershell
az version
```

**✅ 期待される出力:**

```
{
  "azure-cli": "2.64.0",
  ...
}
```

### 5. GitHub CLI

```powershell
# Windows (winget)
winget install GitHub.cli

# macOS (Homebrew)
brew install gh
```

```powershell
gh --version
gh auth login
```

**✅ 成功確認:**

```powershell
gh auth status
```

```
github.com
  ✓ Logged in to github.com as <your-account>
```

---

## ✅ 事前チェックリスト

当日の朝、次のコマンドをすべて実行して、エラーが出ないことを確認してください。

```powershell
python --version
az version
gh --version
git --version
gh auth status
```

あわせて、ブラウザで次が開けることを確認してください。

- https://ai.azure.com/
- https://github.com/

---

## 💻 当日お持ちいただくもの

| 持ち物 | 備考 |
|------|------|
| ノート PC | 上記のセットアップ済みのもの |
| 電源アダプタ | 会場に電源をご用意しています |
| 社員証 | 入館に必要です |

> 💡 **ローカル管理者権限があると安心です**: 当日、追加のパッケージインストールが必要になる場合があります。権限がない場合は事前に御社情報システム部門にご確認ください。

---

## 🚨 準備でつまずいたら

### `python` コマンドが見つからない

**原因**: PATH が通っていない。

**解決方法**: Python を再インストールし、**「Add Python to PATH」** にチェックを入れてください。既にインストール済みの場合は、`py --version` で動くか試してください。

### `winget` が使えない

**原因**: Windows のバージョンが古い、またはアプリインストーラーが未導入。

**解決方法**: Microsoft Store から **「アプリ インストーラー」** を入れるか、各ツールの公式サイトから個別にインストールしてください。

### 社内プロキシでインストールが失敗する

**解決方法**: プロキシ設定を行ってください。

```powershell
# pip
pip config set global.proxy http://<proxy>:<port>

# npm
npm config set proxy http://<proxy>:<port>

# git
git config --global http.proxy http://<proxy>:<port>
```

不明な場合は、御社情報システム部門にご確認ください。

### GitHub Copilot にサインインできない

**原因**: 組織のライセンスが割り当てられていない可能性があります。

**解決方法**: 開催前に講師までご連絡ください。当日の対応では間に合わないことがあります。

---

## 📞 お問い合わせ

準備で不明な点があれば、開催前日までに講師までご連絡ください。
