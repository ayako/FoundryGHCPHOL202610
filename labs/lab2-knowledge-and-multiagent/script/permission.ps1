# Uses the existing Azure CLI sign-in. The caller ID is its Entra principal object ID.
param(
    [string]$FOUNDRY_NAME,
    [string]$FOUNDRY_PROJECT_NAME,
    [guid]$CALLER_AGENT_OBJECT_ID = [guid]::Empty
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($FOUNDRY_NAME) -or
    [string]::IsNullOrWhiteSpace($FOUNDRY_PROJECT_NAME) -or
    $CALLER_AGENT_OBJECT_ID -eq [guid]::Empty) {
    throw "Specify FOUNDRY_NAME, FOUNDRY_PROJECT_NAME, and CALLER_AGENT_OBJECT_ID."
}

$AccountsJson = az cognitiveservices account list --output json
if ($LASTEXITCODE -ne 0) {
    throw "Failed to list Foundry accounts. Check the existing Azure CLI sign-in, selected subscription, and resource access."
}
$Accounts = @($AccountsJson | ConvertFrom-Json | Where-Object { $_.name -eq $FOUNDRY_NAME })
if ($Accounts.Count -ne 1 -or [string]::IsNullOrWhiteSpace($Accounts[0].id)) {
    throw "Expected exactly one Foundry account named '$FOUNDRY_NAME' in the selected subscription."
}

$ProjectScope = "$($Accounts[0].id)/projects/$FOUNDRY_PROJECT_NAME"
$RoleId = "eed3b665-ab3a-47b6-8f48-c9382fb1dad6" # Foundry Agent Consumer

Write-Host "Assigning Foundry Agent Consumer to $CALLER_AGENT_OBJECT_ID at $ProjectScope"
az role assignment create `
    --assignee-object-id $CALLER_AGENT_OBJECT_ID.ToString() `
    --assignee-principal-type ServicePrincipal `
    --role $RoleId `
    --scope $ProjectScope
if ($LASTEXITCODE -ne 0) {
    throw "Failed to assign Foundry Agent Consumer. Check the project scope, caller object ID, and role-assignment permissions."
}
Write-Host "SUCCESS: Foundry Agent Consumer assigned." -ForegroundColor Green