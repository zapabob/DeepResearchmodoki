@echo off
chcp 65001 > nul
echo フロントエンドとバックエンドの統合を開始しています...

REM プロジェクトのルートディレクトリに移動
cd %~dp0..
set PYTHONPATH=%CD%

REM 実行中のPythonプロセスとポート8002を使用しているプロセスを終了
echo 実行中のPythonプロセスを終了しています...
taskkill /F /IM python.exe 2>nul
echo ポート8002を使用しているプロセスを終了しています...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8002') do (
    echo PID: %%a のプロセスを終了しています
    taskkill /F /PID %%a 2>nul
)

REM ポートが解放されるのを待つ
timeout /t 2 /nobreak > nul

REM バックエンドの依存関係をインストール
echo バックエンドの依存関係をインストールしています...
cd %CD%\backend
pip install -r requirements.txt
pip install chromedriver-autoinstaller

REM バックエンドサーバーを起動
echo バックエンドサーバーを起動しています...
start cmd /k "chcp 65001 > nul && cd %CD% && set PYTHONPATH=%CD%\.. && python main.py"

REM バックエンドが起動するのを待つ
echo バックエンドの起動を待っています...
timeout /t 5 /nobreak > nul

REM フロントエンドサーバーを起動
echo フロントエンドサーバーを起動しています...
cd %CD%\..\frontend
echo フロントエンドの依存関係をインストールしています...
call npm install --force
echo フロントエンド開発サーバーを起動しています...
start cmd /k "chcp 65001 > nul && cd %CD% && npm run dev"

echo.
echo 統合が完了しました。
echo バックエンド: http://localhost:8002
echo フロントエンド: http://localhost:3000
echo.
echo 終了するには、開いたコマンドプロンプトウィンドウを閉じてください。 