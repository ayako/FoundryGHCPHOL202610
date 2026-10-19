#!/usr/bin/env bash
set -euo pipefail

FOUNDRY_NAME="${FOUNDRY_NAME:-your-foundry-name}"
FOUNDRY_PROJECT_NAME="${FOUNDRY_PROJECT_NAME:-your-foundry-project-name}"

if [[ "$FOUNDRY_NAME" == "your-foundry-name" || "$FOUNDRY_PROJECT_NAME" == "your-foundry-project-name" ]]; then
  echo "Specify FOUNDRY_NAME and FOUNDRY_PROJECT_NAME." >&2
  exit 1
fi

BASE_URL="https://$FOUNDRY_NAME.services.ai.azure.com/api/projects/$FOUNDRY_PROJECT_NAME"

TOKEN=$(az account get-access-token \
  --resource "https://ai.azure.com" \
  --query accessToken \
  -o tsv)
if [[ -z "$TOKEN" ]]; then
  echo "Failed to acquire an Azure access token. Run az login and check the selected subscription." >&2
  exit 1
fi

set_a2a() {
  AGENT_NAME="$1"
  DESCRIPTION="$2"
  SKILL_ID="$3"
  SKILL_NAME="$4"
  SKILL_DESCRIPTION="$5"

  echo ""
  echo "Configuring: $AGENT_NAME"

  curl --fail-with-body -X PATCH \
    "$BASE_URL/agents/$AGENT_NAME?api-version=v1" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"agent_card\": {
        \"description\": \"$DESCRIPTION\",
        \"version\": \"1.0\",
        \"skills\": [
          {
            \"id\": \"$SKILL_ID\",
            \"name\": \"$SKILL_NAME\",
            \"description\": \"$SKILL_DESCRIPTION\"
          }
        ]
      },
      \"agent_endpoint\": {
        \"protocol_configuration\": {
          \"responses\": {},
          \"a2a\": {}
        }
      }
    }"

  echo ""
  echo "SUCCESS: $AGENT_NAME"
}

set_a2a \
  "FaqAnswerAgent" \
  "製品の仕様・使い方・成分・安全性・社内手順に関する質問に答えるエージェント" \
  "faq-answer" \
  "FAQ Answer" \
  "製品の仕様・使い方・成分・安全性・社内手順に関する質問に回答します"

set_a2a \
  "HistoryAnalysisAgent" \
  "問い合わせ履歴データの集計・傾向分析を行うエージェント" \
  "history-analysis" \
  "History Analysis" \
  "問い合わせ履歴データを集計し、傾向を分析します"

set_a2a \
  "DraftingAgent" \
  "関係部署へのエスカレーション報告文を作成するエージェント" \
  "escalation-drafting" \
  "Escalation Drafting" \
  "問い合わせ内容をもとに関係部署へのエスカレーション報告文を作成します"
