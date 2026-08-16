<#
.SYNOPSIS
  Compile and install AgenticTeam for a supported AI coding harness.

.EXAMPLE
  .\install.ps1 -Target C:\projects\app -Harness codex -Preset full-platform
  .\install.ps1 -Target C:\projects\app -Agents ceo,cto-architect,fullstack-engineer
  .\install.ps1 -List
#>
param(
  [string]$Preset = 'full-company',
  [string[]]$Agents,
  [string]$Target,
  [ValidateSet('claude-code','codex','opencode','antigravity','gemini-cli','pi','generic')]
  [string]$Harness = 'claude-code',
  [switch]$List
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Cli = Join-Path $PSScriptRoot 'agentic_team.py'

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  throw 'Python 3 is required to run the AgenticTeam compiler.'
}

if ($List) {
  & python $Cli --source $Root list agents
  Write-Host "`nPresets:" -ForegroundColor Cyan
  & python $Cli --source $Root list presets
  Write-Host "`nHarnesses:" -ForegroundColor Cyan
  & python $Cli --source $Root list harnesses
  exit $LASTEXITCODE
}

if (-not $Target) { throw 'Provide -Target <project path>, or use -List.' }

$arguments = @($Cli, '--source', $Root, 'install', $Target, '--harness', $Harness)
if ($Agents) {
  foreach ($agent in $Agents) {
    foreach ($name in ($agent -split ',' | Where-Object { $_ })) {
      $arguments += @('--only-agent', $name.Trim())
    }
  }
} else {
  $arguments += @('--preset', $Preset)
}

& python @arguments
exit $LASTEXITCODE
