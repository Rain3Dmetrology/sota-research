# Deep Market Research Skill - Windows one-click installer
# Detects installed agent platforms and copies the skill into their skills/ directory.

$SkillDir = "deep-market-research"
$Src = Split-Path -Parent $MyInvocation.MyCommand.Path
$Files = @("SKILL.md", "README.md", "README_EN.md", "references", "LICENSE", "CONTRIBUTING.md", ".gitignore")

$Targets = @(
  "$env:USERPROFILE\.claude\skills",
  "$env:USERPROFILE\.codex\skills",
  "$env:USERPROFILE\.trae\skills",
  "$env:USERPROFILE\.qoder\skills",
  "$env:USERPROFILE\.workbuddy\skills"
)

$installed = 0
foreach ($base in $Targets) {
  if (Test-Path $base) {
    $dest = Join-Path $base $SkillDir
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    foreach ($f in $Files) {
      $srcPath = Join-Path $Src $f
      if (Test-Path $srcPath) {
        Copy-Item -Recurse -Force $srcPath $dest
      }
    }
    Write-Host "Installed to $dest"
    $installed++
  }
}

if ($installed -eq 0) {
  Write-Host "No supported agent skills directory found. Manually copy this folder to your agent's skills directory."
  exit 1
}
Write-Host "Done. Restart your agent to load 'deep-market-research'."
