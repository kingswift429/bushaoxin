# ============================================================
# 推送到 GitHub（已内置代理配置）
#
# 用法:
#   powershell -ExecutionPolicy Bypass -File verify/push.ps1 -RepoUrl "https://github.com/你的用户名/bushaoxin.git"
#
# 前提:
#   1. 先在 GitHub 上建一个空仓库（不要勾 README / gitignore）
#   2. 凭据用 Personal Access Token，不是账号密码
#      https://github.com/settings/tokens  勾选 repo 权限
#   3. 或者用 SSH: 把 ~/.ssh/id_ed25519.pub 加到 https://github.com/settings/keys
# ============================================================

param(
    [string]$RepoUrl = "",
    [string]$Proxy   = "http://127.0.0.1:7897"
)

$ErrorActionPreference = "Stop"

if (-not $RepoUrl) {
    Write-Host "Please pass -RepoUrl, e.g.:" -ForegroundColor Yellow
    Write-Host '  powershell -ExecutionPolicy Bypass -File verify/push.ps1 -RepoUrl "https://github.com/yourname/bushaoxin.git"'
    exit 1
}

# 回到项目根（本脚本在 verify/ 下）
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "Project : $root"
Write-Host "Remote  : $RepoUrl"

# ---------- 1. 配置代理 ----------
Write-Host ""
Write-Host "Configuring git proxy: $Proxy"
git config --global http.proxy  $Proxy
git config --global https.proxy $Proxy

# SSH 走代理（若之后改用 SSH 地址）
$sshConfig = Join-Path $env:USERPROFILE ".ssh\config"
if (-not (Test-Path $sshConfig)) {
    New-Item -ItemType File -Path $sshConfig -Force | Out-Null
}
$existing = Get-Content $sshConfig -Raw -ErrorAction SilentlyContinue
if (-not $existing -or $existing -notmatch "github\.com") {
    $block = "`nHost github.com`n    HostName github.com`n    User git`n"
    Add-Content -Path $sshConfig -Value $block
    Write-Host "Appended SSH host block to $sshConfig"
}

# ---------- 2. 检查工作区 ----------
Write-Host ""
Write-Host "Checking working tree"
$dirty = git status --porcelain
if ($dirty) {
    Write-Host "Uncommitted changes found, committing..." -ForegroundColor Yellow
    git add -A
    git commit -m "Auto commit before push"
} else {
    Write-Host "Working tree clean"
}

# ---------- 3. 分支命名为 main ----------
Write-Host ""
Write-Host "Switching to branch main"
git branch -M main

# ---------- 4. 配置远端 ----------
Write-Host ""
Write-Host "Setting remote origin"
$remotes = git remote
if ($remotes -contains "origin") {
    git remote set-url origin $RepoUrl
} else {
    git remote add origin $RepoUrl
}
Write-Host "  $(git remote get-url origin)"

# ---------- 5. 推送 ----------
Write-Host ""
Write-Host "Pushing (will ask for username + Personal Access Token)" -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "PUSH OK" -ForegroundColor Green
    Write-Host "Next: open the repo on GitHub -> Actions -> Build iOS -> Run workflow"
} else {
    Write-Host ""
    Write-Host "PUSH FAILED (exit $LASTEXITCODE)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Common causes:"
    Write-Host "  1. Auth failed   -> use a Personal Access Token, not your password"
    Write-Host "                      https://github.com/settings/tokens (scope: repo)"
    Write-Host "  2. Repo missing  -> create an empty repo on GitHub first"
    Write-Host "  3. Proxy down    -> check that 127.0.0.1:7897 is listening"
    Write-Host "  4. Repo has files-> git pull --rebase origin main --allow-unrelated-histories"
}
