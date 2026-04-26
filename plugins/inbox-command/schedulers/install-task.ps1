# Registers the "Inbox Command - 3x daily" Windows scheduled task under the
# current user. Triggers at 08:00, 13:00, 17:00 local time.
#
# Run from PowerShell (no admin required for user-level tasks):
#   powershell -ExecutionPolicy Bypass -File .\install-task.ps1
#
# To uninstall:
#   Unregister-ScheduledTask -TaskName "Inbox Command - 3x daily" -Confirm:$false

$ErrorActionPreference = "Stop"

$taskName = "Inbox Command - 3x daily"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$runScan = Join-Path $scriptDir "run-scan.ps1"

if (-not (Test-Path $runScan)) {
    throw "run-scan.ps1 not found at $runScan"
}

$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument "-ExecutionPolicy Bypass -WindowStyle Hidden -File `"$runScan`""

$triggers = @(
    New-ScheduledTaskTrigger -Daily -At 8:00am
    New-ScheduledTaskTrigger -Daily -At 1:00pm
    New-ScheduledTaskTrigger -Daily -At 5:00pm
)

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 30)

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Write-Host "Task '$taskName' already exists — re-registering."
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

Register-ScheduledTask `
    -TaskName $taskName `
    -Description "Runs /inbox-command:scan three times a day." `
    -Action $action `
    -Trigger $triggers `
    -Settings $settings `
    -Principal $principal | Out-Null

Write-Host "Registered '$taskName' with triggers at 08:00, 13:00, 17:00."
Write-Host "Trigger a manual run from Task Scheduler -> right-click -> Run, then check %LOCALAPPDATA%\inbox-command\last-run.log"
