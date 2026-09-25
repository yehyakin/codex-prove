#requires -Version 5.1
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$installScript = Join-Path $repoRoot "scripts/install.ps1"
$validateScript = Join-Path $repoRoot "scripts/validate.ps1"
$uninstallScript = Join-Path $repoRoot "scripts/uninstall.ps1"
$engine = (Get-Process -Id $PID).Path
$testRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("codex-prove-v100-windows-" + [Guid]::NewGuid().ToString("N"))
[System.IO.Directory]::CreateDirectory($testRoot) | Out-Null

function Assert-True {
    param(
        [Parameter(Mandatory = $true)][bool]$Condition,
        [Parameter(Mandatory = $true)][string]$Message
    )
    if (-not $Condition) { throw $Message }
}

function Assert-PathExists {
    param([Parameter(Mandatory = $true)][string]$Path)
    Assert-True (Test-Path -LiteralPath $Path) "expected path is missing: $Path"
}

function Assert-PathAbsent {
    param([Parameter(Mandatory = $true)][string]$Path)
    Assert-True (-not (Test-Path -LiteralPath $Path)) "unexpected path exists: $Path"
}

function Write-TestText {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][string]$Text
    )
    $parent = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $parent)) { [System.IO.Directory]::CreateDirectory($parent) | Out-Null }
    [System.IO.File]::WriteAllText($Path, $Text, (New-Object System.Text.UTF8Encoding($false)))
}

function Get-FileDigest {
    param([Parameter(Mandatory = $true)][string]$Path)
    return (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
}

function Get-BytesDigest {
    param([Parameter(Mandatory = $true)][byte[]]$Bytes)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { return ([System.BitConverter]::ToString($sha.ComputeHash($Bytes))).Replace("-", "").ToLowerInvariant() }
    finally { $sha.Dispose() }
}

function Get-TreeDigest {
    param([Parameter(Mandatory = $true)][string]$Path)
    $entries = New-Object System.Collections.Generic.List[string]
    foreach ($item in @(Get-ChildItem -LiteralPath $Path -Force -Recurse | Sort-Object -Property FullName)) {
        $relative = $item.FullName.Substring($Path.Length).TrimStart([char[]]"/\").Replace("\", "/")
        if ($item.PSIsContainer) { $entries.Add("D`t$relative`n") }
        else { $entries.Add("F`t$relative`t$(Get-FileDigest $item.FullName)`n") }
    }
    return Get-BytesDigest ([System.Text.Encoding]::UTF8.GetBytes(($entries -join "")))
}

function Invoke-LifecycleScript {
    param(
        [Parameter(Mandatory = $true)][string]$Script,
        [string[]]$Arguments = @(),
        [int]$ExpectedExitCode = 0
    )
    $oldPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        & $engine -NoLogo -NoProfile -NonInteractive -File $Script @Arguments *> $null
        $actual = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $oldPreference
    }
    if ($actual -ne $ExpectedExitCode) {
        throw "unexpected exit code for ${Script}: expected $ExpectedExitCode, got $actual"
    }
}

function Invoke-CheckProcess {
    param(
        [Parameter(Mandatory = $true)][string]$HomePath,
        [int]$ExpectedExitCode = 0
    )
    $oldHome = $env:ORCHESTRATE_HOME
    try {
        $env:ORCHESTRATE_HOME = $HomePath
        Invoke-LifecycleScript $installScript @("-Check") $ExpectedExitCode
    }
    finally {
        $env:ORCHESTRATE_HOME = $oldHome
    }
}

function Test-CheckModeReadOnly {
    $homePath = Join-Path $testRoot "check-only-home"
    Assert-PathAbsent $homePath
    Invoke-CheckProcess $homePath
    Assert-PathAbsent $homePath
}

function Test-CheckRejectsUnsafeParent {
    $homePath = Join-Path $testRoot "unsafe-check-parent"
    [System.IO.Directory]::CreateDirectory($homePath) | Out-Null
    Write-TestText (Join-Path $homePath ".agents") "user file`n"
    $before = Get-FileDigest (Join-Path $homePath ".agents")
    Invoke-CheckProcess $homePath 1
    Assert-True ((Get-FileDigest (Join-Path $homePath ".agents")) -eq $before) "check changed unsafe parent"
    Assert-PathAbsent (Join-Path $homePath ".codex")
}

function Install-At {
    param(
        [Parameter(Mandatory = $true)][string]$HomePath,
        [int]$ExpectedExitCode = 0,
        [string]$Failpoint = ""
    )
    $oldHome = $env:ORCHESTRATE_HOME
    $oldFailpoint = $env:ORCHESTRATE_FAILPOINT
    try {
        $env:ORCHESTRATE_HOME = $HomePath
        $env:ORCHESTRATE_FAILPOINT = $Failpoint
        Invoke-LifecycleScript $installScript @() $ExpectedExitCode
    }
    finally {
        $env:ORCHESTRATE_HOME = $oldHome
        $env:ORCHESTRATE_FAILPOINT = $oldFailpoint
    }
}

function Uninstall-At {
    param(
        [Parameter(Mandatory = $true)][string]$HomePath,
        [switch]$RestoreLatest,
        [int]$ExpectedExitCode = 0,
        [string]$Failpoint = ""
    )
    $oldHome = $env:ORCHESTRATE_HOME
    $oldFailpoint = $env:ORCHESTRATE_FAILPOINT
    try {
        $env:ORCHESTRATE_HOME = $HomePath
        $env:ORCHESTRATE_FAILPOINT = $Failpoint
        $arguments = @()
        if ($RestoreLatest) { $arguments = @("-RestoreLatest") }
        Invoke-LifecycleScript $uninstallScript $arguments $ExpectedExitCode
    }
    finally {
        $env:ORCHESTRATE_HOME = $oldHome
        $env:ORCHESTRATE_FAILPOINT = $oldFailpoint
    }
}

function Assert-V1Installed {
    param([Parameter(Mandatory = $true)][string]$HomePath)
    foreach ($relative in @(
        ".agents/skills/codex-prove/SKILL.md",
        ".agents/skills/sol-control/SKILL.md",
        ".codex/agents/prove-controller.toml",
        ".codex/agents/prove-complex-worker.toml",
        ".codex/agents/prove-efficient-worker.toml",
        ".codex/agents/prove-specialist-worker.toml",
        ".codex/codex-prove/install-state"
    )) { Assert-PathExists (Join-Path $HomePath $relative) }
    foreach ($relative in @(
        ".codex/agents/sol-controller.toml",
        ".codex/agents/terra-high-worker.toml",
        ".codex/agents/luna-max-worker.toml"
    )) { Assert-PathAbsent (Join-Path $HomePath $relative) }
    $state = Get-Content -LiteralPath (Join-Path $HomePath ".codex/codex-prove/install-state") -Raw
    Assert-True ($state -match '(?m)^version=6$') "v1.1 state version is invalid"
    foreach ($agent in @("prove-controller", "prove-specialist-worker", "prove-complex-worker", "prove-efficient-worker")) {
        $relative = ".codex/agents/$agent.toml"
        Assert-True ((Get-FileDigest (Join-Path $HomePath $relative)) -eq (Get-FileDigest (Join-Path $repoRoot $relative))) "installed agent differs from source"
    }
}

function Test-FreshLifecycle {
    $homePath = Join-Path $testRoot "fresh"
    [System.IO.Directory]::CreateDirectory($homePath) | Out-Null
    Write-TestText (Join-Path $homePath ".codex/config.toml") "# preserve me`n"
    Write-TestText (Join-Path $homePath ".codex/agents/other-agent.toml") "name = `"other-agent`"`n"
    $configBefore = Get-FileDigest (Join-Path $homePath ".codex/config.toml")
    $otherBefore = Get-FileDigest (Join-Path $homePath ".codex/agents/other-agent.toml")

    Install-At $homePath
    Assert-V1Installed $homePath
    Assert-True ((Get-FileDigest (Join-Path $homePath ".codex/config.toml")) -eq $configBefore) "config.toml changed"
    Assert-True ((Get-FileDigest (Join-Path $homePath ".codex/agents/other-agent.toml")) -eq $otherBefore) "unrelated agent changed"

    Install-At $homePath
    Assert-V1Installed $homePath
    Uninstall-At $homePath
    foreach ($relative in @(
        ".agents/skills/codex-prove",
        ".agents/skills/sol-control",
        ".codex/agents/prove-controller.toml",
        ".codex/agents/prove-complex-worker.toml",
        ".codex/agents/prove-efficient-worker.toml",
        ".codex/agents/prove-specialist-worker.toml",
        ".codex/codex-prove/install-state"
    )) { Assert-PathAbsent (Join-Path $homePath $relative) }
    Assert-True ((Get-FileDigest (Join-Path $homePath ".codex/config.toml")) -eq $configBefore) "config.toml changed during uninstall"
    Assert-True ((Get-FileDigest (Join-Path $homePath ".codex/agents/other-agent.toml")) -eq $otherBefore) "unrelated agent changed during uninstall"
}

function Test-ModifiedTargetRefusal {
    $homePath = Join-Path $testRoot "modified"
    [System.IO.Directory]::CreateDirectory($homePath) | Out-Null
    Install-At $homePath
    Add-Content -LiteralPath (Join-Path $homePath ".agents/skills/codex-prove/SKILL.md") -Value "user change"
    Install-At $homePath 1
    Assert-PathExists (Join-Path $homePath ".agents/skills/codex-prove/SKILL.md")
}

function New-TestDirectoryLink {
    param([string]$Path, [string]$Target)
    $kind = if ($env:OS -eq "Windows_NT") { "Junction" } else { "SymbolicLink" }
    New-Item -ItemType $kind -Path $Path -Target $Target | Out-Null
}

function Test-UnrelatedLinksDoNotBlockLifecycle {
    $homePath = Join-Path $testRoot "unrelated-links"
    $external = Join-Path $testRoot "unrelated-link-target"
    Write-TestText (Join-Path $external "user.txt") "leave this alone`n"
    $original = Get-FileDigest (Join-Path $external "user.txt")
    $links = @()
    try {
        foreach ($relative in @("DocumentsShortcut", ".codex/agents/other-link", ".agents/skills/other-skill")) {
            $link = Join-Path $homePath $relative
            [System.IO.Directory]::CreateDirectory((Split-Path -Parent $link)) | Out-Null
            New-TestDirectoryLink $link $external
            $links += $link
        }
        Invoke-CheckProcess $homePath
        Install-At $homePath
        Assert-V1Installed $homePath
        Uninstall-At $homePath
        foreach ($link in $links) {
            Assert-True (((Get-Item -LiteralPath $link -Force).Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) "unrelated link changed"
        }
        Assert-True ((Get-FileDigest (Join-Path $external "user.txt")) -eq $original) "unrelated linked content changed"
    }
    finally {
        # Remove each exact link itself before recursive fixture cleanup.
        foreach ($link in $links) { [System.IO.Directory]::Delete($link) }
    }
}

function Test-ManagedParentLinksFailClosed {
    $index = 0
    foreach ($relative in @(".agents", ".agents/skills", ".codex", ".codex/agents", ".codex/codex-prove", ".codex/codex-prove/backups")) {
        $homePath = Join-Path $testRoot "managed-link-$index"
        $external = Join-Path $testRoot "managed-link-target-$index"
        Install-At $homePath
        $parent = Join-Path $homePath $relative
        Move-Item -LiteralPath $parent -Destination $external
        New-TestDirectoryLink $parent $external
        try {
            $before = Get-TreeDigest $external
            Invoke-CheckProcess $homePath 1
            Install-At $homePath 1
            Uninstall-At $homePath -RestoreLatest -ExpectedExitCode 1
            Assert-True ((Get-TreeDigest $external) -eq $before) "managed link target changed after refusal"
            Assert-V1Installed $homePath
        }
        finally { [System.IO.Directory]::Delete($parent) }
        $index++
    }
}

function Test-InstallRollback {
    $homePath = Join-Path $testRoot "rollback"
    [System.IO.Directory]::CreateDirectory($homePath) | Out-Null
    Install-At $homePath
    $before = Get-FileDigest (Join-Path $homePath ".codex/agents/prove-controller.toml")
    Install-At $homePath 1 "after-replace"
    Assert-True ((Get-FileDigest (Join-Path $homePath ".codex/agents/prove-controller.toml")) -eq $before) "rollback did not restore controller"
    Assert-V1Installed $homePath
}

function Test-V050MigrationAndRestore {
    $homePath = Join-Path $testRoot "v050"
    [System.IO.Directory]::CreateDirectory($homePath) | Out-Null
    $oldSkill = Join-Path $homePath ".agents/skills/sol-control"
    Write-TestText (Join-Path $oldSkill "SKILL.md") "---`nname: sol-control`ndescription: old managed skill`n---`nold`n"
    Write-TestText (Join-Path $oldSkill "agents/openai.yaml") "interface:`n  default_prompt: old`n"
    $oldController = Join-Path $homePath ".codex/agents/sol-controller.toml"
    $oldComplex = Join-Path $homePath ".codex/agents/terra-high-worker.toml"
    $oldEfficient = Join-Path $homePath ".codex/agents/luna-max-worker.toml"
    Write-TestText $oldController "name = `"sol-controller`"`n"
    Write-TestText $oldComplex "name = `"terra-high-worker`"`n"
    Write-TestText $oldEfficient "name = `"luna-max-worker`"`n"
    $oldState = Join-Path $homePath ".codex/sol-control/install-state"
    $stateText = @(
        "version=4",
        "backup_id=old-v050",
        "skill_sha256=$(Get-TreeDigest $oldSkill)",
        "sol_sha256=$(Get-FileDigest $oldController)",
        "luna_sha256=$(Get-FileDigest $oldEfficient)",
        "terra_sha256=$(Get-FileDigest $oldComplex)"
    ) -join "`n"
    Write-TestText $oldState ($stateText + "`n")
    $oldSkillHash = Get-TreeDigest $oldSkill

    Install-At $homePath
    Assert-V1Installed $homePath
    Uninstall-At $homePath -RestoreLatest

    Assert-PathAbsent (Join-Path $homePath ".agents/skills/codex-prove")
    Assert-PathAbsent (Join-Path $homePath ".codex/agents/prove-controller.toml")
    Assert-PathExists $oldSkill
    Assert-PathExists $oldController
    Assert-PathExists $oldComplex
    Assert-PathExists $oldEfficient
    Assert-PathExists $oldState
    Assert-True ((Get-TreeDigest $oldSkill) -eq $oldSkillHash) "restore did not recover v0.5 Skill"
}

function New-V100Fixture {
    param([Parameter(Mandatory = $true)][string]$HomePath)
    foreach ($skill in @("codex-prove", "sol-control")) {
        Write-TestText (Join-Path $HomePath ".agents/skills/$skill/SKILL.md") "old $skill`n"
    }
    foreach ($agent in @("prove-controller", "prove-complex-worker", "prove-efficient-worker")) {
        Write-TestText (Join-Path $HomePath ".codex/agents/$agent.toml") "name = `"$agent`"`n"
    }
    $stateText = @(
        "version=5", "backup_id=v100-fixture",
        "skill_sha256=$(Get-TreeDigest (Join-Path $HomePath '.agents/skills/codex-prove'))",
        "compat_skill_sha256=$(Get-TreeDigest (Join-Path $HomePath '.agents/skills/sol-control'))",
        "controller_sha256=$(Get-FileDigest (Join-Path $HomePath '.codex/agents/prove-controller.toml'))",
        "complex_worker_sha256=$(Get-FileDigest (Join-Path $HomePath '.codex/agents/prove-complex-worker.toml'))",
        "efficient_worker_sha256=$(Get-FileDigest (Join-Path $HomePath '.codex/agents/prove-efficient-worker.toml'))"
    ) -join "`n"
    Write-TestText (Join-Path $HomePath '.codex/codex-prove/install-state') ($stateText + "`n")
}

function Test-V100FourTierMigration {
    $homePath = Join-Path $testRoot "v100-migration"
    New-V100Fixture $homePath
    $statePath = Join-Path $homePath ".codex/codex-prove/install-state"
    $controllerPath = Join-Path $homePath ".codex/agents/prove-controller.toml"
    $stateBefore = Get-FileDigest $statePath
    $controllerBefore = Get-FileDigest $controllerPath
    $specialist = Join-Path $homePath ".codex/agents/prove-specialist-worker.toml"

    Install-At $homePath 1 "after-state"
    Assert-True ((Get-FileDigest $statePath) -eq $stateBefore) "v1.0 state was not rolled back"
    Assert-True ((Get-FileDigest $controllerPath) -eq $controllerBefore) "v1.0 controller was not rolled back"
    Assert-PathAbsent $specialist
    Install-At $homePath
    Assert-V1Installed $homePath
    Uninstall-At $homePath -RestoreLatest
    Assert-True ((Get-FileDigest $statePath) -eq $stateBefore) "v1.0 state was not restored"
    Assert-True ((Get-FileDigest $controllerPath) -eq $controllerBefore) "v1.0 controller was not restored"
    Assert-PathAbsent $specialist

    Write-TestText $specialist "user-owned specialist`n"
    $userHash = Get-FileDigest $specialist
    Install-At $homePath 1
    Uninstall-At $homePath -ExpectedExitCode 1 -Failpoint "after-remove"
    Assert-True ((Get-FileDigest $specialist) -eq $userHash) "rollback changed unowned specialist"
    Assert-True ((Get-FileDigest $statePath) -eq $stateBefore) "uninstall rollback changed v1.0 state"
    Uninstall-At $homePath
    Assert-True ((Get-FileDigest $specialist) -eq $userHash) "uninstall removed unowned specialist"
}

function Test-ExceptionAfterMoveRestoresUnmarkedOriginal {
    $wrapper = Join-Path $testRoot "after-move.ps1"
    Write-TestText $wrapper @'
param([string]$ScriptFile)
$script:injected = $false
function Move-Item {
    [CmdletBinding()]
    param([string]$LiteralPath, [string]$Destination)
    Microsoft.PowerShell.Management\Move-Item -LiteralPath $LiteralPath -Destination $Destination -ErrorAction Stop
    if (-not $script:injected -and $Destination.Replace('\', '/') -match '/(old|current)/0$') {
        $script:injected = $true
        throw 'injected exception after successful move'
    }
}
& $ScriptFile
'@
    foreach ($operation in @("install", "uninstall")) {
        $homePath = Join-Path $testRoot "$operation-after-move"
        Install-At $homePath
        $statePath = Join-Path $homePath ".codex/codex-prove/install-state"
        $before = Get-FileDigest $statePath
        $script = if ($operation -eq "install") { $installScript } else { $uninstallScript }
        $oldHome = $env:ORCHESTRATE_HOME
        $oldFailpoint = $env:ORCHESTRATE_FAILPOINT
        try {
            $env:ORCHESTRATE_HOME = $homePath
            $env:ORCHESTRATE_FAILPOINT = ""
            Invoke-LifecycleScript $wrapper @("-ScriptFile", $script) 1
        }
        finally {
            $env:ORCHESTRATE_HOME = $oldHome
            $env:ORCHESTRATE_FAILPOINT = $oldFailpoint
        }
        Assert-V1Installed $homePath
        Assert-True ((Get-FileDigest $statePath) -eq $before) "post-move exception changed install state"
        Assert-True ((Get-TreeDigest (Join-Path $homePath ".agents/skills/codex-prove")) -eq (Get-TreeDigest (Join-Path $repoRoot ".agents/skills/codex-prove"))) "post-move exception lost the original skill"
    }
}

function Test-FailedRecoveryPreservesCopy {
    $wrapper = Join-Path $testRoot "failed-move.ps1"
    Write-TestText $wrapper @'
param([string]$ScriptFile, [string]$FailedSource, [string]$FailedDestination, [switch]$RestoreLatest)
function Move-Item {
    [CmdletBinding()]
    param([string]$LiteralPath, [string]$Destination)
    if (($FailedSource -and $LiteralPath.Replace('\', '/') -like $FailedSource) -or
        ($FailedDestination -and $Destination.Replace('\', '/') -like $FailedDestination)) {
        Write-Error 'injected recovery move failure'
        return
    }
    Microsoft.PowerShell.Management\Move-Item -LiteralPath $LiteralPath -Destination $Destination -ErrorAction Stop
}
if ($RestoreLatest) { & $ScriptFile -RestoreLatest }
else { & $ScriptFile }
'@
    foreach ($operation in @("install", "uninstall")) {
        foreach ($failure in @("restore", "evacuation")) {
            $homePath = Join-Path $testRoot "$operation-failed-$failure"
            Install-At $homePath
            $evacuation = $failure -eq "evacuation"
            if ($operation -eq "uninstall" -and $evacuation) { Install-At $homePath }
            $specialist = Join-Path $homePath ".codex/agents/prove-specialist-worker.toml"
            $original = Get-FileDigest $specialist
            $prefix = if ($operation -eq "install") { ".transaction." } else { ".uninstall." }
            $held = if ($operation -eq "install") { "old" } else { "current" }
            $script = if ($operation -eq "install") { $installScript } else { $uninstallScript }
            $arguments = @("-ScriptFile", $script)
            if ($evacuation) { $arguments += @("-FailedDestination", "*/$prefix*/failed/15/current") }
            else { $arguments += @("-FailedSource", "*/$prefix*/$held/15") }
            if ($operation -eq "uninstall" -and $evacuation) { $arguments += "-RestoreLatest" }
            $oldHome = $env:ORCHESTRATE_HOME
            $oldFailpoint = $env:ORCHESTRATE_FAILPOINT
            $oldPreference = $ErrorActionPreference
            try {
                $env:ORCHESTRATE_HOME = $homePath
                $env:ORCHESTRATE_FAILPOINT = if ($operation -eq "install") { "after-state" } else { "after-remove" }
                $ErrorActionPreference = "Continue"
                $output = (& $engine -NoLogo -NoProfile -NonInteractive -File $wrapper @arguments 2>&1 | Out-String)
                $actual = $LASTEXITCODE
            }
            finally {
                $env:ORCHESTRATE_HOME = $oldHome
                $env:ORCHESTRATE_FAILPOINT = $oldFailpoint
                $ErrorActionPreference = $oldPreference
            }
            Assert-True ($actual -ne 0) "injected failure unexpectedly succeeded"
            $stateRoot = Join-Path $homePath ".codex/codex-prove"
            $transactions = @(Get-ChildItem -LiteralPath $stateRoot -Directory -Force | Where-Object { $_.Name.StartsWith($prefix) })
            Assert-True ($transactions.Count -eq 1) "$operation/$failure deleted its recovery transaction"
            $recovery = $transactions[0].FullName
            Assert-True ((Get-FileDigest (Join-Path $recovery "$held/15")) -eq $original) "original recovery copy changed"
            Assert-True ($output.Contains("Recovery path: $recovery")) "recovery path was not reported"
            if ($evacuation) { Assert-True ((Get-FileDigest $specialist) -eq $original) "occupied target was overwritten" }
            else { Assert-PathAbsent $specialist }
            Assert-PathExists (Join-Path $homePath ".codex/agents/prove-controller.toml")
            Assert-PathExists (Join-Path $stateRoot "install-state")
        }
    }
}

try {
    Invoke-LifecycleScript $validateScript @() 0
    Test-CheckModeReadOnly
    Test-CheckRejectsUnsafeParent
    Test-UnrelatedLinksDoNotBlockLifecycle
    Test-ManagedParentLinksFailClosed
    Test-FreshLifecycle
    Test-ModifiedTargetRefusal
    Test-InstallRollback
    Test-V050MigrationAndRestore
    Test-V100FourTierMigration
    Test-ExceptionAfterMoveRestoresUnmarkedOriginal
    Test-FailedRecoveryPreservesCopy
    Write-Output "Windows lifecycle contract: PASS"
}
finally {
    if (Test-Path -LiteralPath $testRoot) { Remove-Item -LiteralPath $testRoot -Recurse -Force }
}
