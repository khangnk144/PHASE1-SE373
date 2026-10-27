param([int]$Port = 1081)
$ErrorActionPreference = 'Stop'
if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) {
    Write-Host "Port $Port is already listening. Check that it is your UIT SOCKS tunnel."
    exit 0
}
$tunnelProcess = Start-Process -FilePath 'ssh.exe' -ArgumentList @(
    '-N', '-D', "127.0.0.1:$Port", '-o', 'BatchMode=yes',
    '-o', 'ExitOnForwardFailure=yes', '-o', 'ServerAliveInterval=30',
    '-o', 'ConnectTimeout=10', '-o', 'ConnectionAttempts=1',
    'baotg@192.168.20.150'
) -WindowStyle Hidden -PassThru
$deadline = (Get-Date).AddSeconds(15)
$ready = $false
while ((Get-Date) -lt $deadline) {
    $tunnelProcess.Refresh()
    if ($tunnelProcess.HasExited) { throw 'SSH tunnel failed. Check network and SSH key.' }
    $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue |
        Where-Object { $_.OwningProcess -eq $tunnelProcess.Id }
    if ($listener) { $ready = $true; break }
    Start-Sleep -Milliseconds 300
}
if (-not $ready) {
    $tunnelProcess.Refresh()
    if (-not $tunnelProcess.HasExited) { Stop-Process -Id $tunnelProcess.Id }
    throw 'SSH did not open the SOCKS port within 15 seconds. Check network and SSH key.'
}
Write-Host "UIT SOCKS tunnel started on 127.0.0.1:$Port; PID $($tunnelProcess.Id)."
Write-Host "Stop it when finished: Stop-Process -Id $($tunnelProcess.Id)"
