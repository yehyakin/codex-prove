#requires -Version 5.1
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

function Assert-Condition {
    param(
        [Parameter(Mandatory = $true)][bool]$Condition,
        [Parameter(Mandatory = $true)][string]$Message
    )
    if (-not $Condition) { throw $Message }
}

function Get-Text {
    param([Parameter(Mandatory = $true)][string]$Path)
    return [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8)
}

function Assert-Regex {
    param(
        [Parameter(Mandatory = $true)][string]$Text,
        [Parameter(Mandatory = $true)][string]$Pattern,
        [Parameter(Mandatory = $true)][string]$Message
    )
    if ($Text -notmatch $Pattern) { throw $Message }
}

function Get-Frontmatter {
    param([Parameter(Mandatory = $true)][string]$Path)
    $lines = [System.IO.File]::ReadAllLines($Path, [System.Text.Encoding]::UTF8)
    Assert-Condition ($lines.Count -ge 4 -and $lines[0] -eq "---") "invalid Skill frontmatter opener"
    $closing = -1
    for ($index = 1; $index -lt $lines.Count; $index++) {
        if ($lines[$index] -eq "---") { $closing = $index; break }
    }
    Assert-Condition ($closing -gt 1) "invalid Skill frontmatter closer"
    $result = @{}
    for ($index = 1; $index -lt $closing; $index++) {
        if ([string]::IsNullOrWhiteSpace($lines[$index])) { continue }
        Assert-Condition ($lines[$index] -match "^(?<key>[a-z_]+):\s*(?<value>.+)$") "invalid Skill frontmatter line"
        Assert-Condition (-not $result.ContainsKey($Matches.key)) "duplicate Skill frontmatter key"
        $result[$Matches.key] = $Matches.value.Trim().Trim('"')
    }
    Assert-Condition ($result.Count -eq 2 -and $result.ContainsKey("name") -and $result.ContainsKey("description")) "Skill frontmatter must contain only name and description"
    return $result
}

$requiredFiles = @(
    ".agents/skills/codex-prove/SKILL.md",
    ".agents/skills/codex-prove/agents/openai.yaml",
    ".agents/skills/codex-prove/references/orchestration.md",
    ".agents/skills/codex-prove/references/runtime-notes.md",
    ".agents/skills/codex-prove/references/ponytail-license.txt",
    ".agents/skills/sol-control/SKILL.md",
    ".agents/skills/sol-control/agents/openai.yaml",
    ".codex/agents/prove-controller.toml",
    ".codex/agents/prove-complex-worker.toml",
    ".codex/agents/prove-efficient-worker.toml",
    ".codex/agents/prove-specialist-worker.toml",
    "scripts/install.sh",
    "scripts/validate.sh",
    "scripts/validate_source.py",
    "scripts/uninstall.sh",
    "scripts/install.ps1",
    "scripts/validate.ps1",
    "scripts/uninstall.ps1",
    "scripts/test.sh",
    "scripts/benchmark_ab.py",
    "README.md",
    "README.en.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "SUPPORT.md",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/pull_request_template.md",
    "tests/windows-lifecycle.ps1",
    "tests/fixtures/forward-cases.json",
    "tests/fixtures/v100-ab-benchmark.json",
    "tests/v100-ab-benchmark.md",
    "tests/v100-live-smoke.md",
    "tests/test_v100_benchmark.py",
    "tests/test_v100_evidence_control.py",
    "CODEX_PROVE_V1_IMPLEMENTATION_REPORT.md",
    ".github/workflows/windows-validation.yml",
    ".github/workflows/posix-validation.yml",
    "NOTICE",
    "LICENSE"
)
foreach ($relative in $requiredFiles) {
    $path = Join-Path $repoRoot $relative
    Assert-Condition (Test-Path -LiteralPath $path -PathType Leaf) "missing required file: $relative"
}

foreach ($relative in @(
    ".agents/skills/sol-luna",
    ".agents/skills/orchestrate-sol-luna",
    ".codex/agents/sol-controller.toml",
    ".codex/agents/terra-high-worker.toml",
    ".codex/agents/luna-max-worker.toml",
    ".codex/agents/sol-planner.toml"
)) {
    Assert-Condition (-not (Test-Path -LiteralPath (Join-Path $repoRoot $relative))) "legacy runtime source remains: $relative"
}

$skillPath = Join-Path $repoRoot ".agents/skills/codex-prove/SKILL.md"
$skillMeta = Get-Frontmatter $skillPath
Assert-Condition ($skillMeta.name -eq "codex-prove") "canonical Skill name is invalid"
Assert-Condition ($skillMeta.description.StartsWith("Use only when") -and $skillMeta.description.Contains('$codex-prove')) "canonical Skill description is invalid"

$compatSkillPath = Join-Path $repoRoot ".agents/skills/sol-control/SKILL.md"
$compatMeta = Get-Frontmatter $compatSkillPath
Assert-Condition ($compatMeta.name -eq "sol-control" -and $compatMeta.description.Contains('$sol-control')) "compatibility Skill frontmatter is invalid"

$skillText = Get-Text $skillPath
$contractText = Get-Text (Join-Path $repoRoot ".agents/skills/codex-prove/references/orchestration.md")
$runtimeText = Get-Text (Join-Path $repoRoot ".agents/skills/codex-prove/references/runtime-notes.md")
$combined = $skillText + "`n" + $contractText + "`n" + $runtimeText
foreach ($marker in @(
    "Planning", "Routing", "Ownership", "Verification", "Evidence",
    "Requirement ID", "one owner", "Native Nested", "Compatibility",
    'fork_turns="none"', "Fail Closed", "PASS | FIX | BLOCKED",
    "prove-controller", "prove-complex-worker", "prove-efficient-worker", "prove-specialist-worker"
)) {
    Assert-Condition ($combined.IndexOf($marker, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) "orchestration contract is missing: $marker"
}

$openaiText = Get-Text (Join-Path $repoRoot ".agents/skills/codex-prove/agents/openai.yaml")
foreach ($pattern in @(
    '(?m)^interface:\s*$',
    '(?m)^\s{2}display_name:\s*"Codex PROVE"\s*$',
    '(?m)^\s{2}short_description:\s*"[^"\r\n]{25,64}"\s*$',
    '(?m)^\s{2}default_prompt:\s*".*\$codex-prove.*"\s*$',
    '(?m)^policy:\s*$',
    '(?m)^\s{2}allow_implicit_invocation:\s*false\s*$'
)) {
    Assert-Regex $openaiText $pattern "canonical openai.yaml is invalid"
}

$compatText = Get-Text (Join-Path $repoRoot ".agents/skills/sol-control/agents/openai.yaml")
Assert-Regex $compatText '\$sol-control' "compatibility openai.yaml misses old invocation"
Assert-Regex $compatText '\$codex-prove' "compatibility openai.yaml misses canonical invocation"
Assert-Regex $compatText '(?m)^\s{2}allow_implicit_invocation:\s*false\s*$' "compatibility openai.yaml permits implicit invocation"

# Use the same TOML, source-scope and credential checks as the POSIX surface.
$pythonCommand = $null
foreach ($candidate in @("python3.14", "python3.13", "python3.12", "python3.11", "python3", "python")) {
    $command = Get-Command $candidate -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($null -eq $command) { continue }
    & $command.Source -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' 2>$null
    if ($LASTEXITCODE -eq 0) { $pythonCommand = $command.Source; break }
}
Assert-Condition ($null -ne $pythonCommand) "Python 3.11 or newer is required"
& $pythonCommand (Join-Path $PSScriptRoot "validate_source.py") $repoRoot
Assert-Condition ($LASTEXITCODE -eq 0) "source content validation failed; see diagnostic above"

foreach ($script in @(
    "scripts/install.ps1",
    "scripts/validate.ps1",
    "scripts/uninstall.ps1",
    "tests/windows-lifecycle.ps1"
)) {
    $path = Join-Path $repoRoot $script
    $tokens = $null
    $errors = $null
    [System.Management.Automation.Language.Parser]::ParseFile($path, [ref]$tokens, [ref]$errors) | Out-Null
    Assert-Condition ($errors.Count -eq 0) "PowerShell syntax failed: $script"
}

$forwardCases = Get-Content -LiteralPath (Join-Path $repoRoot "tests/fixtures/forward-cases.json") -Raw | ConvertFrom-Json
Assert-Condition ($forwardCases.Count -ge 13) "forward test fixture is incomplete"
$benchmark = Get-Content -LiteralPath (Join-Path $repoRoot "tests/fixtures/v100-ab-benchmark.json") -Raw | ConvertFrom-Json
Assert-Condition ($null -ne $benchmark) "benchmark fixture is invalid"

Write-Output "PowerShell syntax: PASS"
Write-Output "YAML/TOML/JSON structure: PASS"
Write-Output "Validation: PASS"
exit 0
