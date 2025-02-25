# Web Deep Research システム起動スクリプト

# 現在のディレクトリを保存
$currentDir = Get-Location

Write-Output "Web Deep Research システムを起動しています..."

# ポートが使用中かどうかを確認する関数
function Test-PortInUse {
    param (
        [int]$Port
    )
    
    $connections = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -eq $Port }
    return $null -ne $connections
}

# ポートが使用中の場合、プロセスを終了する関数
function Stop-ProcessUsingPort {
    param (
        [int]$Port
    )
    
    $connections = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $_.LocalPort -eq $Port }
    if ($connections) {
        $processes = @()
        foreach ($connection in $connections) {
            $process = Get-Process -Id $connection.OwningProcess -ErrorAction SilentlyContinue
            if ($process) {
                $processes += $process
            }
        }
        
        foreach ($process in $processes) {
            Write-Output "ポート $Port を使用しているプロセス $($process.Id) ($($process.Name)) を終了します..."
            Stop-Process -Id $process.Id -Force
        }
        
        # プロセスが終了するまで少し待機
        Start-Sleep -Seconds 2
    }
}

# バックエンドポートが使用中の場合、プロセスを終了
if (Test-PortInUse -Port 8002) {
    Write-Output "ポート 8002 は既に使用されています。"
    Stop-ProcessUsingPort -Port 8002
}

# フロントエンドポートが使用中の場合、プロセスを終了
if (Test-PortInUse -Port 3005) {
    Write-Output "ポート 3005 は既に使用されています。"
    Stop-ProcessUsingPort -Port 3005
}

# バックエンドを起動（新しいウィンドウで）
Write-Output "バックエンドを起動しています..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$currentDir\backend'; python main.py"

# 少し待機
Start-Sleep -Seconds 3

# フロントエンドを起動（新しいウィンドウで）
Write-Output "フロントエンドを起動しています..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$currentDir\frontend'; npm run dev"

Write-Output "システムが起動しました！"
Write-Output "バックエンド: http://localhost:8002"
Write-Output "フロントエンド: http://localhost:3005"
Write-Output "各ウィンドウを閉じることでサービスを停止できます。" 