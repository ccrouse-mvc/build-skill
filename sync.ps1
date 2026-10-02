# sync.ps1 - copy the live /build and /build-sonnet skills and their agents from ~/.claude
# into this repo. The live copies in ~/.claude are what Claude Code loads; this repo is the
# history. /build-sonnet is generated: run `python make_sonnet.py` first if /build changed.
# Run, review `git diff`, commit.
$ErrorActionPreference = 'Stop'
$src = Join-Path $env:USERPROFILE '.claude'
$dst = $PSScriptRoot
$files = @(
    'skills\build\SKILL.md', 'skills\build-sonnet\SKILL.md',
    'agents\coder.md', 'agents\coder-ui.md', 'agents\verifier.md',
    'agents\coder-sonnet.md', 'agents\coder-ui-sonnet.md'
)
foreach ($f in $files) {
    $to = Join-Path $dst $f
    New-Item -ItemType Directory -Force (Split-Path $to) | Out-Null
    Copy-Item (Join-Path $src $f) $to -Force
}
Write-Output ('synced: ' + (($files | ForEach-Object { $_ -replace '\\', '/' }) -join ', '))
