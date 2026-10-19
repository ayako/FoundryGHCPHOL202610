param(
    [string]$FOUNDRY_NAME = "your-foundry-name",
    [string]$FOUNDRY_PROJECT_NAME = "your-foundry-project-name"
)

$ErrorActionPreference = "Stop"

if ($FOUNDRY_NAME -eq "your-foundry-name" -or
    $FOUNDRY_PROJECT_NAME -eq "your-foundry-project-name" -or
    [string]::IsNullOrWhiteSpace($FOUNDRY_NAME) -or
    [string]::IsNullOrWhiteSpace($FOUNDRY_PROJECT_NAME)) {
    throw "Specify FOUNDRY_NAME and FOUNDRY_PROJECT_NAME."
}

$BaseUrl = "https://$FOUNDRY_NAME.services.ai.azure.com/api/projects/$FOUNDRY_PROJECT_NAME"

$Token = az account get-access-token --resource "https://ai.azure.com" --query accessToken -o tsv
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($Token)) {
    throw "Failed to acquire an Azure access token. Run az login and check the selected subscription."
}

$Headers = @{
    Authorization = "Bearer $Token"
}

$Agents = @(
    @{
        Name = "FaqAnswerAgent"
        Description = "製品の仕様・使い方・成分・安全性・社内手順に関する質問に答えるエージェント"
        SkillId = "faq-answer"
        SkillName = "FAQ Answer"
        SkillDescription = "製品の仕様・使い方・成分・安全性・社内手順に関する質問に回答します"
    },
    @{
        Name = "HistoryAnalysisAgent"
        Description = "問い合わせ履歴データの集計・傾向分析を行うエージェント"
        SkillId = "history-analysis"
        SkillName = "History Analysis"
        SkillDescription = "問い合わせ履歴データを集計し、傾向を分析します"
    },
    @{
        Name = "DraftingAgent"
        Description = "関係部署へのエスカレーション報告文を作成するエージェント"
        SkillId = "escalation-drafting"
        SkillName = "Escalation Drafting"
        SkillDescription = "問い合わせ内容をもとに関係部署へのエスカレーション報告文を作成します"
    }
)

foreach ($A in $Agents) {
    Write-Host ""
    Write-Host "Configuring: $($A.Name)" -ForegroundColor Cyan

    $Body = @{
        agent_card = @{
            description = $A.Description
            version = "1.0"
            skills = @(
                @{
                    id = $A.SkillId
                    name = $A.SkillName
                    description = $A.SkillDescription
                }
            )
        }
        agent_endpoint = @{
            protocol_configuration = @{
                responses = @{}
                a2a = @{}
            }
        }
    } | ConvertTo-Json -Depth 10

    try {
        Invoke-RestMethod -Method Patch -Uri "$BaseUrl/agents/$($A.Name)?api-version=v1" -Headers $Headers -ContentType "application/json; charset=utf-8" -Body ([System.Text.Encoding]::UTF8.GetBytes($Body))
        Write-Host "SUCCESS: $($A.Name)" -ForegroundColor Green
    }
    catch {
        Write-Host "FAILED: $($A.Name)" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        if ($_.ErrorDetails.Message) {
            Write-Host $_.ErrorDetails.Message -ForegroundColor Red
        }
        throw
    }
}
