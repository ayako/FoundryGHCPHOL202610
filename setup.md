# 事前準備

> 学習を始める前に済ませてください。PC 側の準備は所要 15 分程度です。Azure／Foundry の作成・権限設定は、別ページの **[Azure サブスクリプションと Foundry の事前設定](azure-setup.md)** に従って準備してください（所要時間は環境や権限の承認状況により異なります）。

---

## 📋 学習環境の事前準備

### 必須（Lab 1・Lab 2 用）

| 項目 | 要件 | 確認方法 |
|------|------|---------|
| ブラウザ | Microsoft Edge または Google Chrome の最新版 | ヘルプ → バージョン情報 |
| ネットワーク | `ai.azure.com` にアクセスできること | 下記参照 |
| Foundry 用アカウント | 利用する Azure サブスクリプション・Foundry プロジェクトへのアクセス権があること | [Azure／Foundry の事前設定](azure-setup.md) を参照 |
| GitHub アカウント | Lab 2 の教材取得と Lab 3 で使用。未登録なら [GitHub の登録画面](https://github.com/signup) で無料アカウントを作成 | https://github.com/ にサインイン |

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

GitHub アカウントに Codespaces と GitHub Copilot を利用できる権限が必要です。個人アカウントでは [Codespaces の無料利用枠と課金条件](https://docs.github.com/ja/billing/managing-billing-for-your-products/managing-billing-for-github-codespaces/about-billing-for-github-codespaces) を確認してください。組織で利用する場合は管理者に確認します。Copilot Free と Codespaces の利用枠は別です。
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

4. Lab 3 で Foundry に接続する前に、**Foundry 用アカウント** で Codespace 内の Azure CLI にサインインする

```bash
az login --use-device-code
```

> ⚠️ **Codespaces の GitHub 認証と Azure 認証は別です。** `gh auth status` が成功しても `az login` は必要です。Foundry 用アカウントのテナントを指定する必要がある場合は `az login --tenant <テナントID> --use-device-code` を使用してください。認証情報や `.env` を Git にコミットしないでください。

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

#### GitHub Copilot Free（無償版）を利用する場合

有料プランや組織の Copilot ライセンスがない個人アカウントでは、**Copilot Free** で学習を始められます。

1. GitHub アカウントがなければ [GitHub](https://github.com/signup) で無料アカウントを作成する
2. VS Code の **Copilot アイコン**（上部またはステータスバー）をクリックし、**Sign up for Copilot Free（Copilot Free にサインアップ）** を選ぶ
3. ブラウザで **GitHub アカウント** にサインインし、表示される利用条件・認証の案内に従って有効化する
4. VS Code に戻り、Copilot Chat で質問して応答が返ることを確認する

表示が異なる場合は、[公式の Copilot プラン開始手順](https://docs.github.com/ja/copilot/how-tos/manage-your-account/get-started-with-a-copilot-plan) を参照してください。すでに組織のライセンスや有料プランを利用している場合は、Free に登録し直す必要はありません。Enterprise Managed Users など、Free の対象外のアカウントでは管理者に利用方法を確認してください。

> ⚠️ **Free には利用量・モデル・機能の制限があります。** Lab 3 を最後まで無料枠だけで完了できることは保証されません。[最新のプラン比較](https://docs.github.com/ja/copilot/get-started/plans) と VS Code の利用状況を確認し、上限に達した場合は枠のリセットを待つか、必要に応じて有料プランを検討してください。有料プランの無料試用を選ぶ場合は、期間終了後の課金・解約条件も確認してください。

#### 手順

1. VS Code 右下の **Copilot アイコン** をクリック
2. **「Sign in to GitHub」** を選択
3. ブラウザが開くので、GitHub アカウントで認証する

**✅ 成功確認:**
- Copilot アイコンに斜線（無効マーク）が付いていない
- 適当な Python ファイルを開いてコメントを書くと、補完が提案される

> ⚠️ **「No access to GitHub Copilot」と表示される場合**: サインイン中の GitHub アカウントと Copilot のプランを確認し、個人利用では上記の Free の登録、組織利用では管理者へのライセンス・ポリシー確認を行ってください。

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

Lab 3 を始める前に、利用する PC／Codespace で次のコマンドをすべて実行して、エラーが出ないことを確認してください。

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

Lab 1・2 の開始前には、[Azure／Foundry のチェックリスト](azure-setup.md#6-lab-を始める前のチェックリスト) に従い、プロジェクト・権限・モデルデプロイを確認してください。

---

## 💻 学習に必要なもの

| 項目 | 備考 |
|------|------|
| ノート PC | 上記のセットアップ済みのもの |
| 電源・安定したネットワーク | モデルの呼び出しやパッケージの取得に必要 |

> 💡 **インストール権限を確認してください**: 追加のパッケージインストールが必要になる場合があります。管理対象 PC では事前に情報システム部門にご確認ください。

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

**原因**: 別の GitHub アカウントでサインインしている、Copilot Free が利用できない、組織のライセンス・ポリシーに制限がある可能性があります。

**解決方法**: 上の「GitHub Copilot Free（無償版）を利用する場合」を確認し、利用する GitHub アカウントでサインインし直してください。組織のアカウントでは管理者にライセンス・ポリシーを確認してください。

---

## 📞 解決しない場合

まず [トラブルシューティング](troubleshooting.md) と各サービスの公式ドキュメントを確認してください。教材の不明点は、このリポジトリの Issue に、該当する手順とエラーメッセージを添えて報告できます。認証情報や個人情報は含めないでください。
