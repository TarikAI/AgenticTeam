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
  [ValidateSet('claude-code','codex','opencode','antigravity','gemini-cli','pi','generic','copilot','cursor','factory','kiro','qwen-code','junie')]
  [string]$Harness = 'claude-code',
  [ValidateSet('inherit','balanced','max-quality','economy')]
  [string]$ModelProfile,
  [switch]$List
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Cli = Join-Path $PSScriptRoot 'agentic_team.py'

# Resolve a Python that actually RUNS. On Windows, `python` and `python3` can resolve to the
# Microsoft Store alias stub: Get-Command finds it, and every invocation then fails. So probe
# each candidate by executing it, and require Python 3.10+.
$Probe = 'import sys; sys.exit(0 if sys.version_info[:2] >= (3, 10) else 1)'
$PythonCommand = $null
foreach ($candidate in @(@('py', '-3'), @('python'), @('python3'))) {
  if (-not (Get-Command $candidate[0] -ErrorAction SilentlyContinue)) { continue }
  $prefix = @()
  if ($candidate.Count -gt 1) { $prefix = $candidate[1..($candidate.Count - 1)] }
  try {
    & $candidate[0] @prefix -c $Probe 2>$null | Out-Null
    if ($LASTEXITCODE -eq 0) { $PythonCommand = $candidate; break }
  } catch {
    continue
  }
}
if (-not $PythonCommand) {
  throw 'Python 3.10+ is required but no working interpreter was found (tried py -3, python, python3).'
}
$PythonExe = $PythonCommand[0]
$PythonPrefix = @()
if ($PythonCommand.Count -gt 1) { $PythonPrefix = $PythonCommand[1..($PythonCommand.Count - 1)] }

if ($List) {
  & $PythonExe @PythonPrefix $Cli --source $Root list agents
  Write-Host "`nPresets:" -ForegroundColor Cyan
  & $PythonExe @PythonPrefix $Cli --source $Root list presets
  Write-Host "`nHarnesses:" -ForegroundColor Cyan
  & $PythonExe @PythonPrefix $Cli --source $Root list harnesses
  exit $LASTEXITCODE
}

if (-not $Target) { throw 'Provide -Target <project path>, or use -List.' }

$arguments = @($Cli, '--source', $Root, 'install', $Target, '--harness', $Harness)
if ($ModelProfile) { $arguments += @('--model-profile', $ModelProfile) }
if ($Agents) {
  foreach ($agent in $Agents) {
    foreach ($name in ($agent -split ',' | Where-Object { $_ })) {
      $arguments += @('--only-agent', $name.Trim())
    }
  }
} else {
  $arguments += @('--preset', $Preset)
}

& $PythonExe @PythonPrefix @arguments
exit $LASTEXITCODE
