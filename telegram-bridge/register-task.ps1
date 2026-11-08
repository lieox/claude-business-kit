# Registers the bridge as a Windows scheduled task that starts at logon and restarts if it stops.
# Run once from PowerShell inside the telegram-bridge folder:  .\register-task.ps1
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = (Get-Command python).Source
$action = New-ScheduledTaskAction -Execute $python -Argument "`"$here\bridge.py`"" -WorkingDirectory $here
$trigger = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME
$settings = New-ScheduledTaskSettingsSet -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit (New-TimeSpan -Days 0) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "ClaudeTelegramBridge" -Action $action -Trigger $trigger -Settings $settings -Force
Start-ScheduledTask -TaskName "ClaudeTelegramBridge"
Write-Host "Bridge registered and started. Log: $here\state\bridge.log"
