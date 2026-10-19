#!/usr/bin/env bash
set -euo pipefail

# Uses the existing Azure CLI sign-in. The caller ID is its Entra principal object ID.
: "${FOUNDRY_NAME:?Specify FOUNDRY_NAME.}"
: "${FOUNDRY_PROJECT_NAME:?Specify FOUNDRY_PROJECT_NAME.}"
: "${CALLER_AGENT_OBJECT_ID:?Specify CALLER_AGENT_OBJECT_ID.}"

if [[ ! "$CALLER_AGENT_OBJECT_ID" =~ ^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$ ||
      "$CALLER_AGENT_OBJECT_ID" == "00000000-0000-0000-0000-000000000000" ]]; then
  echo "Specify CALLER_AGENT_OBJECT_ID using the calling agent's Microsoft Entra principal object ID." >&2
  exit 1
fi

ACCOUNT_ID=$(az cognitiveservices account list \
  --query "[?name=='$FOUNDRY_NAME'].id" -o tsv)
if [[ -z "$ACCOUNT_ID" || "$ACCOUNT_ID" == *$'\n'* ]]; then
  echo "Expected exactly one Foundry account named '$FOUNDRY_NAME' in the selected subscription." >&2
  exit 1
fi

PROJECT_SCOPE="$ACCOUNT_ID/projects/$FOUNDRY_PROJECT_NAME"
ROLE_ID="eed3b665-ab3a-47b6-8f48-c9382fb1dad6" # Foundry Agent Consumer

echo "Assigning Foundry Agent Consumer to $CALLER_AGENT_OBJECT_ID at $PROJECT_SCOPE"
az role assignment create \
  --assignee-object-id "$CALLER_AGENT_OBJECT_ID" \
  --assignee-principal-type ServicePrincipal \
  --role "$ROLE_ID" \
  --scope "$PROJECT_SCOPE"
echo "SUCCESS: Foundry Agent Consumer assigned."