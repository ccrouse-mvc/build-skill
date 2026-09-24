# sync.ps1 - copy the live /build skill and its agents from ~/.claude into this repo.
# The live copies in ~/.claude are what Claude Code loads; this repo is the history.
# Run, review `git diff`, commit.
$ErrorActionPreference = 'Stop'
$src = Join-Path $env:USERPROFILE '.claude'
$dst = $PSScriptRoot
New-Item -ItemType Directory -Force (Join-Path $dst 'skills\build'), (Join-Path $dst 'agents') | Out-Null
Copy-Item (Join-Path $src 'skills\build\SKILL.md') (Join-Path $dst 'skills\build\SKILL.md') -Force
foreach ($a in @('coder', 'coder-ui', 'verifier')) {
    Copy-Item (Join-Path $src "agents\$a.md") (Join-Path $dst "agents\$a.md") -Force
}
Write-Output 'synced: skills/build/SKILL.md, agents/coder.md, agents/coder-ui.md, agents/verifier.md'
