@echo off
echo Web Deep Research システムを起動しています...

REM ポートが使用中かどうかを確認
echo ポートの確認中...
set BACKEND_PORT=8002
set FRONTEND_PORT=3005

REM バックエンドポートが使用中の場合、プロセスを終了
netstat -ano | findstr :%BACKEND_PORT% > nul
if %ERRORLEVEL% EQU 0 (
    echo ポート %BACKEND_PORT% は既に使用されています。プロセスを終了します...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%BACKEND_PORT%') do (
        taskkill /F /PID %%a
    )
    timeout /t 2 /nobreak > nul
)

REM フロントエンドポートが使用中の場合、プロセスを終了
netstat -ano | findstr :%FRONTEND_PORT% > nul
if %ERRORLEVEL% EQU 0 (
    echo ポート %FRONTEND_PORT% は既に使用されています。プロセスを終了します...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%FRONTEND_PORT%') do (
        taskkill /F /PID %%a
    )
    timeout /t 2 /nobreak > nul
)

echo バックエンドを起動しています...
start cmd /k "cd %~dp0backend && python main.py"

echo 少し待機しています...
timeout /t 3 /nobreak > nul

echo フロントエンドを起動しています...
start cmd /k "cd %~dp0frontend && npm run dev"

echo.
echo システムが起動しました！
echo バックエンド: http://localhost:%BACKEND_PORT%
echo フロントエンド: http://localhost:%FRONTEND_PORT%
echo 各ウィンドウを閉じることでサービスを停止できます。
echo. 