# Microsoft Foundry Boot Camp — Day 1 ハンズオン

> Microsoft Foundry でエージェントを作り、社内文書をナレッジとして与え、GitHub Copilot でそれを呼び出すクライアントまで作る、4 時間のハンズオンです。

架空の日用消費財メーカー「サンライト株式会社 お客様相談室」を題材に、**一次対応エージェント** を段階的に育てていきます。

---

## 🎯 このハンズオンのゴール

- Microsoft Foundry で動くエージェントを、**自分の手で 1 体つくる**
- ナレッジを与えると回答が **根拠を持つ** ようになることを体感する
- ナレッジの品質が回答の品質を決めることを、**実際の矛盾** を通じて理解する
- **GitHub Copilot をエージェントとして使う** 感覚をつかむ

## 📚 Lab 一覧

| # | タイトル | 所要 | 内容 |
|---|------|------|---------|
| 1 | [Microsoft Foundry でエージェントを作る](labs/lab1-foundry-basics/README.md) | 30min | ポータル操作のみ。エージェント作成、モデル選択、Instructions |
| 2 | [ナレッジとマルチエージェント](labs/lab2-knowledge-and-multiagent/README.md) | 65min | File Search、Code Interpreter、Connected Agents |
| 3 | [GitHub Copilot でエージェントを呼び出す](labs/lab3-github-copilot/README.md) | 60min | エージェントモード、Copilot CLI、Issue → PR |

> 💡 **Lab 1 と Lab 2 はコードを書きません。** すべてブラウザ上の操作で完結します。エディタを使うのは Lab 3 からです。

## 🎬 シナリオ

| 項目 | 内容 |
|------|------|
| 企業 | サンライト株式会社（架空の日用消費財メーカー） |
| 部門 | お客様相談室 |
| 課題 | 問い合わせの一次対応に時間がかかり、担当者によって回答の質がばらつく |
| 扱う製品 | 衣料用液体洗剤「アクアクリア」／食器用洗剤「キュットフォーム」／ヘアケア「モイストヴェール」 |
| つくるもの | 一次対応を支援するマルチエージェント構成 |

### 最終的にできあがる構成

```mermaid
flowchart TB
    orchestrator["受付エージェント<br>（オーケストレーター）"]

    faq["FAQ回答エージェント<br><br><b>Knowledge:</b><br>FAQ・仕様シート<br>対応マニュアル<br>社内ルール"]
    history["履歴分析エージェント<br><br><b>Tool:</b><br>Code Interpreter<br>問い合わせ履歴 200件"]
    draft["起案エージェント<br><br><b>Instructions:</b><br>エスカレーション<br>報告文の下書き"]

    orchestrator --> faq
    orchestrator --> history
    orchestrator --> draft
```

> ⚠️ **本ハンズオンで使用する企業名・製品名・文書・データは、研修のために作成した架空のものです。** 実在の企業・製品とは一切関係ありません。

## 📋 事前準備

参加者側での事前準備は **[setup.md](setup.md)** を参照してください。

Azure リソース（Foundry プロジェクト、モデルデプロイ、権限）は **すべて主催側で用意済み** です。参加者の皆さんが作成する必要はありません。

## 📁 リポジトリ構成

```
.
├── README.md                          # このファイル
├── setup.md                           # 事前準備
├── troubleshooting.md                 # 共通トラブルシューティング
├── knowledge/                         # ナレッジ用ファイル（当日配布）
│   ├── 製品FAQ_アクアクリア.docx
│   ├── 製品FAQ_キュットフォーム.docx
│   ├── 製品FAQ_モイストヴェール.docx
│   ├── 製品仕様シート_アクアクリア.pdf
│   ├── 製品仕様シート_キュットフォーム.pdf
│   ├── 製品仕様シート_モイストヴェール.pdf
│   ├── 対応マニュアル.docx
│   ├── 社内ルール.docx
│   └── 問い合わせ履歴.csv
└── labs/
    ├── lab1-foundry-basics/
    │   └── README.md
    ├── lab2-knowledge-and-multiagent/
    │   └── README.md
    └── lab3-github-copilot/
        └── README.md
```

## 🚶 進め方

1. 各 Lab の README を **上から順に** 読み進めてください
2. 各手順の末尾にある **`✅ 成功確認`** で、自分の状態を確かめてください
3. つまずいたら、まず各 Lab 末尾の **トラブルシューティング** を確認してください
4. 解決しない場合は、遠慮なくサポーターにお声がけください
5. 時間が余った方は、各所にある **「（任意）」** の演習に進んでください

> 💡 **完走が目的ではありません。** 特に Lab 2 の演習 2「ナレッジの質が、回答の質を決める」は、手を動かすより **起きたことの意味を考える** 時間にしてください。

## 🔗 参考リンク

- [Microsoft Foundry ドキュメント](https://learn.microsoft.com/ja-jp/azure/ai-foundry/)
- [Foundry Agent Service](https://learn.microsoft.com/ja-jp/azure/ai-foundry/agents/overview)
- [GitHub Copilot ドキュメント](https://docs.github.com/ja/copilot)
- [Microsoft Learn: AI エージェント ラーニングパス](https://learn.microsoft.com/ja-jp/training/)

---

## 📝 ライセンスと注意事項

- 本ハンズオンの教材は、研修目的で作成されたものです
- 登場する企業・製品・文書・データはすべて架空です
- 記載されている製品仕様・画面構成は、執筆時点（2026年10月）のものです
