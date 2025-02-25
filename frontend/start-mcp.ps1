# Docker環境のクリーンアップ
Write-Host "Cleaning up Docker environment..."
docker-compose -f docker-compose.mcp.yml down -v
docker system prune -f

# 環境変数の読み込み
Write-Host "Loading environment variables..."
Get-Content .env.mcp | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.+)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        [Environment]::SetEnvironmentVariable($key, $value, "Process")
    }
}

# Docker Composeの実行
Write-Host "Starting services with Docker Compose..."
docker-compose -f docker-compose.mcp.yml up -d --build

# サービスの起動を待機
Write-Host "Waiting for services to be healthy..."
Start-Sleep -Seconds 30

# サービスの状態確認
Write-Host "Checking service status..."
docker-compose -f docker-compose.mcp.yml ps

# ヘルスチェックのURL表示
Write-Host "`Service URLs:"
Write-Host "Frontend: http://localhost:3000"
Write-Host "Backend Health: http://localhost:3001/api/health"
Write-Host "Neo4j Browser: http://localhost:7474 (default credentials: neo4j/password)"
Write-Host "Redis Commander: http://localhost:6379"

# ログの表示
Write-Host "`nShowing logs (Ctrl+C to exit)..."
docker-compose -f docker-compose.mcp.yml logs -f 