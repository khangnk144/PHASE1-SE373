param([int]$Port = 1081)
$ErrorActionPreference = 'Stop'
if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) {
    Write-Host "Port $Port is already listening. Check that it is your UIT SOCKS tunnel."
    exit 0
}
$tunnelProcess = Start-Process -FilePath 'ssh.exe' -ArgumentList @(
    '-N', '-D', "127.0.0.1:$Port", '-o', 'BatchMode=yes',
    '-o', 'ExitOnForwardFailure=yes', '-o', 'ServerAliveInterval=30',
    'baotg@192.168.20.150'
) -WindowStyle Hidden -PassThru
Start-Sleep -Seconds 2
if ($tunnelProcess.HasExited) { throw 'SSH tunnel failed. Check network and SSH key.' }
Write-Host "UIT SOCKS tunnel started on 127.0.0.1:$Port; PID $($tunnelProcess.Id)."
Write-Host "Stop it when finished: Stop-Process -Id $($tunnelProcess.Id)"
