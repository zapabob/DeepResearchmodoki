#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import time
import signal
import platform
import logging
import atexit
import shutil
from pathlib import Path

# スクリプトの実行パスを確認
script_path = Path(__file__).resolve()
script_dir = script_path.parent
project_root = script_dir.parent

# カレントディレクトリをプロジェクトルートに変更
os.chdir(project_root)
sys.path.insert(0, str(project_root))

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("integration")
logger.info(f"スクリプトパス: {script_path}")
logger.info(f"カレントディレクトリを {project_root} に変更しました")

# プロセスリスト
processes = []

def cleanup_processes():
    """起動したプロセスをすべて終了する"""
    logger.info("プロセスをクリーンアップしています...")
    for proc in processes:
        if proc.poll() is None:  # プロセスがまだ実行中の場合
            try:
                if platform.system() == "Windows":
                    proc.terminate()
                else:
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
                logger.info(f"プロセス {proc.pid} を終了しました")
            except Exception as e:
                logger.error(f"プロセス終了中にエラーが発生しました: {e}")

# 終了時にプロセスをクリーンアップする
atexit.register(cleanup_processes)

def find_project_root():
    """プロジェクトのルートディレクトリを見つける"""
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    return project_root

def find_npm_executable():
    """npmコマンドの実行可能ファイルを見つける"""
    npm_cmd = "npm"
    if platform.system() == "Windows":
        # Windowsの場合は.cmdや.exeの拡張子を追加
        npm_cmd = "npm.cmd"
        # PATHからnpmを探す
        npm_path = shutil.which(npm_cmd)
        if not npm_path:
            # 一般的なNode.jsのインストールパスを確認
            common_paths = [
                os.path.join(os.environ.get('APPDATA', ''), 'npm'),
                os.path.join(os.environ.get('ProgramFiles', ''), 'nodejs'),
                os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'nodejs'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'nodejs')
            ]
            for path in common_paths:
                potential_npm = os.path.join(path, npm_cmd)
                if os.path.exists(potential_npm):
                    return potential_npm
            
            # それでも見つからない場合はエラー
            logger.error("npmコマンドが見つかりません。Node.jsがインストールされていることを確認してください。")
            return None
        return npm_path
    else:
        # Linux/Macの場合
        return shutil.which(npm_cmd)

def kill_process_on_port(port):
    """指定されたポートを使用しているプロセスを終了する"""
    logger.info(f"ポート {port} を使用しているプロセスを終了しています...")
    
    try:
        if platform.system() == "Windows":
            # Windowsの場合
            output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode()
            if output:
                for line in output.splitlines():
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        pid = parts[4]
                        try:
                            subprocess.run(f"taskkill /F /PID {pid}", shell=True, check=False)
                            logger.info(f"PID {pid} のプロセスを終了しました")
                        except Exception as e:
                            logger.error(f"プロセス終了中にエラーが発生しました: {e}")
        else:
            # Linux/Macの場合
            output = subprocess.check_output(f"lsof -i :{port} -t", shell=True).decode()
            if output:
                for pid in output.splitlines():
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        logger.info(f"PID {pid} のプロセスを終了しました")
                    except Exception as e:
                        logger.error(f"プロセス終了中にエラーが発生しました: {e}")
    except subprocess.CalledProcessError:
        # コマンドが失敗した場合（プロセスが見つからない場合など）
        pass

def start_backend(project_root):
    """バックエンドサーバーを起動する"""
    logger.info("バックエンドサーバーを起動しています...")
    
    backend_dir = project_root / "backend"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)
    
    # バックエンドの依存関係をインストール
    logger.info("バックエンドの依存関係をインストールしています...")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        cwd=project_root,
        check=False
    )
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "chromedriver-autoinstaller"],
        check=False
    )
    
    # バックエンドサーバーを起動
    backend_cmd = [sys.executable, "main.py"]
    backend_process = subprocess.Popen(
        backend_cmd,
        cwd=backend_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    processes.append(backend_process)
    logger.info(f"バックエンドサーバーを起動しました (PID: {backend_process.pid})")
    
    # 非同期でログを出力するスレッドを開始
    def log_output(process, prefix):
        for line in iter(process.stdout.readline, ""):
            logger.info(f"{prefix}: {line.strip()}")
    
    import threading
    backend_log_thread = threading.Thread(
        target=log_output,
        args=(backend_process, "バックエンド"),
        daemon=True
    )
    backend_log_thread.start()
    
    return backend_process

def start_frontend(project_root):
    """フロントエンドサーバーを起動する"""
    logger.info("フロントエンドサーバーを起動しています...")
    
    frontend_dir = project_root / "frontend"
    
    # npmコマンドを見つける
    npm_executable = find_npm_executable()
    if not npm_executable:
        logger.error("npmコマンドが見つからないため、フロントエンドを起動できません。")
        logger.error("Node.jsがインストールされていることを確認してください。")
        return None
    
    logger.info(f"npmコマンドを見つけました: {npm_executable}")
    
    # フロントエンドの依存関係をインストール
    logger.info("フロントエンドの依存関係をインストールしています...")
    try:
        # まずviteパッケージを明示的にインストール
        logger.info("viteパッケージをインストールしています...")
        vite_install_cmd = [npm_executable, "install", "vite", "--save-dev"]
        subprocess.run(vite_install_cmd, cwd=frontend_dir, check=False)
        
        # 次に他の依存関係をインストール
        npm_install_cmd = [npm_executable, "install", "--force"]
        subprocess.run(npm_install_cmd, cwd=frontend_dir, check=False)
        
        # フロントエンド開発サーバーを起動
        npm_run_cmd = [npm_executable, "run", "dev"]
        frontend_process = subprocess.Popen(
            npm_run_cmd,
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            env=os.environ.copy()  # 環境変数を明示的に渡す
        )
        
        processes.append(frontend_process)
        logger.info(f"フロントエンド開発サーバーを起動しました (PID: {frontend_process.pid})")
        
        # 非同期でログを出力するスレッドを開始
        def log_output(process, prefix):
            for line in iter(process.stdout.readline, ""):
                logger.info(f"{prefix}: {line.strip()}")
        
        import threading
        frontend_log_thread = threading.Thread(
            target=log_output,
            args=(frontend_process, "フロントエンド"),
            daemon=True
        )
        frontend_log_thread.start()
        
        return frontend_process
    except Exception as e:
        logger.error(f"フロントエンドの起動中にエラーが発生しました: {e}")
        return None

def main():
    """メイン関数"""
    logger.info("Web Deep Research 統合スクリプトを開始しています...")
    
    # プロジェクトのルートディレクトリを取得
    project_root = find_project_root()
    logger.info(f"プロジェクトルート: {project_root}")
    
    # 既存のプロセスを終了
    kill_process_on_port(8002)  # バックエンドポート
    kill_process_on_port(3000)  # フロントエンドポート
    
    # 少し待機してポートが解放されるのを待つ
    time.sleep(2)
    
    # バックエンドサーバーを起動
    backend_process = start_backend(project_root)
    
    # バックエンドが起動するのを待つ
    logger.info("バックエンドの起動を待っています...")
    time.sleep(5)
    
    # フロントエンドサーバーを起動
    frontend_process = start_frontend(project_root)
    
    if frontend_process is None:
        logger.error("フロントエンドの起動に失敗しました。バックエンドのみで続行します。")
        logger.info("\n部分的な統合が完了しました。")
        logger.info("バックエンド: http://localhost:8002")
        logger.info("終了するには Ctrl+C を押してください。")
        
        try:
            # メインスレッドを実行し続ける
            while True:
                # プロセスの状態を確認
                if backend_process.poll() is not None:
                    logger.error(f"バックエンドプロセスが終了しました (終了コード: {backend_process.returncode})")
                    break
                
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Ctrl+C が押されました。終了しています...")
        finally:
            # プロセスをクリーンアップ
            cleanup_processes()
        return
    
    logger.info("\n統合が完了しました。")
    logger.info("バックエンド: http://localhost:8002")
    logger.info("フロントエンド: http://localhost:3000")
    logger.info("終了するには Ctrl+C を押してください。")
    
    try:
        # メインスレッドを実行し続ける
        while True:
            # プロセスの状態を確認
            if backend_process.poll() is not None:
                logger.error(f"バックエンドプロセスが終了しました (終了コード: {backend_process.returncode})")
                break
            
            if frontend_process.poll() is not None:
                logger.error(f"フロントエンドプロセスが終了しました (終了コード: {frontend_process.returncode})")
                break
            
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Ctrl+C が押されました。終了しています...")
    finally:
        # プロセスをクリーンアップ
        cleanup_processes()

if __name__ == "__main__":
    main() 