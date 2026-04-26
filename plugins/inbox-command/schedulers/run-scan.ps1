# Wrapper invoked by the Windows scheduled task.
# Runs `claude -p "/inbox-command:scan"` headlessly and writes a log.

$ErrorActionPreference = "Stop"

$stateDir = Join-Path $env:LOCALAPPDATA "inbox-command"
if (-not (Test-Path $stateDir)) {
    New-Item -ItemType Directory -Path $stateDir -Force | Out-Null
}

$logPath = Join-Path $stateDir "last-run.log"
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

"=== $timestamp — Inbox Command run ===" | Out-File -FilePath $logPath -Encoding utf8

# Resolve `claude` on PATH. If you installed Claude Code somewhere non-standard,
# edit $claudeExe below (e.g. "C:\Users\<you>\AppData\Local\Programs\claude\claude.exe").
$claudeExe = "claude"

try {
    & $claudeExe -p "/inbox-command:scan" --permission-mode acceptEdits 2>&1 |
        Tee-Object -FilePath $logPath -Append
    "=== $timestamp — Scan complete ===" | Out-File -FilePath $logPath -Append -Encoding utf8
    exit 0
}
catch {
    "ERROR: $_" | Out-File -FilePath $logPath -Append -Encoding utf8
    exit 1
}
