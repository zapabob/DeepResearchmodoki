# PowerShellスクリプト for Web Deep Research
# UTF-8エンコーディングを設定
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "フロントエンドとバックエンドの統合を開始しています..."

# プロジェクトのルートディレクトリに移動
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootPath = Split-Path -Parent $scriptPath
Set-Location $rootPath
$env:PYTHONPATH = $rootPath

# 実行中のPythonプロセスとポート8002を使用しているプロセスを終了
Write-Host "実行中のPythonプロセスを終了しています..."
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host "ポート8002を使用しているプロセスを終了しています..."
$processes = Get-NetTCPConnection -LocalPort 8002 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
foreach ($process in $processes) {
    Write-Host "PID: $process のプロセスを終了しています"
    Stop-Process -Id $process -Force -ErrorAction SilentlyContinue
}

# ポートが解放されるのを待つ
Start-Sleep -Seconds 2

# バックエンドの依存関係をインストール
Write-Host "バックエンドの依存関係をインストールしています..."
Set-Location "$rootPath\backend"
pip install -r requirements.txt
pip install chromedriver-autoinstaller

# バックエンドサーバーを起動
Write-Host "バックエンドサーバーを起動しています..."
$backendCmd = "cd '$rootPath\backend'; `$env:PYTHONPATH='$rootPath'; python main.py"
$backendProcess = Start-Process powershell -ArgumentList "-Command", $backendCmd -PassThru

# バックエンドが起動するのを待つ
Write-Host "バックエンドの起動を待っています..."
Start-Sleep -Seconds 5

# フロントエンドサーバーを起動
Write-Host "フロントエンドサーバーを起動しています..."
Set-Location "$rootPath\frontend"
Write-Host "フロントエンドの依存関係をインストールしています..."
npm install --force
Write-Host "フロントエンド開発サーバーを起動しています..."
$frontendCmd = "cd '$rootPath\frontend'; npm run dev"
$frontendProcess = Start-Process powershell -ArgumentList "-Command", $frontendCmd -PassThru

Write-Host ""
Write-Host "統合が完了しました。"
Write-Host "バックエンド: http://localhost:8002"
Write-Host "フロントエンド: http://localhost:3000"
Write-Host "終了するには、開いたPowerShellウィンドウを閉じてください。"

# プロセスを監視し、Ctrl+Cが押されたら両方のプロセスを終了
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    if ($null -ne $backendProcess) {
        Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    }
    if ($null -ne $frontendProcess) {
        Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue
    }
} 