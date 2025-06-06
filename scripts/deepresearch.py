import os
import sys
import logging
import json
import subprocess
from datetime import datetime
import argparse

# プロジェクトのルートディレクトリをPythonパスに追加（最初に実行）
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

# 依存ライブラリのインポート
import pkg_resources
import langchain_community
import langchain_community.document_loaders
import langchain.text_splitter
import langchain_community.vectorstores
import langchain_community.embeddings
import langchain_community.llms
import langchain_community.chains
import langchain_community.agents
import langchain_community.callbacks
import PyQt6
import PyQt6.QtWidgets
import PyQt6.QtCore
import PyQt6.QtGui
import PyQt6.QtWebEngineWidgets
import PyQt6.QtWebEngineCore
import PyQt6.QtWebChannel
import nest_asyncio
import asyncio

# 依存バックエンドサービスのインポート
from backend.services.crawler import CrawlerService
from backend.services import get_ai_service

# 非同期処理の設定
nest_asyncio.apply()

# ログディレクトリの作成
log_dir = os.path.join(root_dir, "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "deepresearch.log")

logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def check_dependency_conflicts():
    try:
        # langchainの依存関係を確認
        pkg_resources.require('langchain')
        print('langchainは正常にインストールされています。')
    except pkg_resources.VersionConflict as e:
        print('langchainのバージョンに衝突が発生しています:')
        print(e)
        logging.error('langchain VersionConflict: %s', e)
    except pkg_resources.DistributionNotFound as e:
        print('langchainがインストールされていません。')
        logging.error('langchain DistributionNotFound: %s', e)


def run_pip_check():
    try:
        result = subprocess.run(['pip', 'check'], capture_output=True, text=True)
        if result.returncode != 0:
            print('pip checkで依存関係の問題が検出されました:')
            print(result.stdout)
            print(result.stderr)
            logging.error('pip check errors: stdout: %s, stderr: %s', result.stdout, result.stderr)
        else:
            print('pip checkで依存関係に問題は検出されませんでした。')
    except Exception as e:
        print('pip checkの実行中にエラーが発生しました:')
        print(e)
        logging.error('pip check execution error: %s', e)


def parse_args():
    """コマンドライン引数の解析"""
    parser = argparse.ArgumentParser(description='DeepResearch - ウェブ検索と分析ツール')
    parser.add_argument('query', nargs='?', help='検索クエリ')
    parser.add_argument('--max-pages', type=int, default=5, help='最大ページ数')
    return parser.parse_args()


class DeepResearch:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler())
        
        # ログファイルハンドラーを追加
        log_file_handler = logging.FileHandler(log_file)
        self.logger.addHandler(log_file_handler)
        
        self.logger.info('DeepResearchインスタンスが作成されました。')

    async def deep_research(self, query=None):
        self.logger.info('DeepResearch機能: ウェブ全体の詳細検索とCoTによる仮説検証思考を開始します。')
        if query is None:
            import sys
            if sys.stdin.isatty():
                query = input('検索クエリを入力してください: ')
            else:
                query = '最新のテクノロジーニュース'
        if not query.strip():
            self.logger.warning('検索クエリが入力されていません。処理を終了します。')
            return

        self.logger.info(f'検索クエリ: {query}')
        crawler = CrawlerService()
        results = crawler.crawl(query, max_pages=15)

        # Crawlerから得られた検索結果のフィードバックを生成
        crawler_feedback = ""
        self.logger.info('検索結果（Crawlerからのフィードバック）:')
        for i, res in enumerate(results, 1):
            title = res.get('title', 'N/A')
            url = res.get('url', 'N/A')
            summary = res.get('metadata', {}).get('summary')
            if not summary:
                summary = res.get('content', '')[:200]
            feedback_line = f"結果 {i}:\nタイトル: {title}\nURL: {url}\n概要: {summary}\n" + ("-" * 40) + "\n"
            crawler_feedback += feedback_line
            self.logger.info(feedback_line)

        # 検索結果からChain-of-Thought用の入力テキストを生成
        combined_text = ""
        for res in results:
            title = res.get('title', '')
            url = res.get('url', '')
            summary = res.get('metadata', {}).get('summary', res.get('content', ''))
            pub_date = res.get('metadata', {}).get('date', '')
            author = res.get('metadata', {}).get('author', '')

            combined_text += f"タイトル: {title}\nURL: {url}\n概要: {summary}\n"
            if pub_date:
                combined_text += f"発行日時: {pub_date}\n"
            if author:
                combined_text += f"著者: {author}\n"
            combined_text += "\n"

        self.logger.info('Chain-of-Thought推論を開始します。')
        gemini = get_ai_service()
        prompt = (
            "# Chain-of-Thought Deep Research\n\n"
            "以下の幅広いウェブ検索結果に基づいて、詳細な分析と仮説検証を行ってください。\n\n"
            "## ステップ1: 検索結果の整理\n"
            "まず、提供された検索結果を整理し、各情報源の信頼性、関連性、最新性を評価してください。\n\n"
            "## ステップ2: 主要な事実の抽出\n"
            "各検索結果から主要な事実、主張、データポイントを抽出してください。矛盾する情報がある場合は特に注記してください。\n\n"
            "## ステップ3: 複数の仮説の形成\n"
            "抽出した事実に基づいて、少なくとも3つの異なる仮説を形成してください。各仮説は明確に区別され、検証可能であるべきです。\n\n"
            "## ステップ4: 仮説の検証\n"
            "各仮説について、支持する証拠と反証する証拠を検索結果から特定し、評価してください。\n"
            "- 仮説を支持する証拠は何か\n"
            "- 仮説に反する証拠は何か\n"
            "- 証拠の強さと信頼性はどうか\n\n"
            "## ステップ5: 最も可能性の高い結論\n"
            "証拠の評価に基づいて、最も可能性の高い結論を導き出してください。不確実性がある場合は、その程度も示してください。\n\n"
            "## ステップ6: 追加調査が必要な領域\n"
            "結論を強化するために追加の調査が必要な領域や、現在の情報では答えられない重要な質問を特定してください。\n\n"
            "## 検索結果:\n" + combined_text
        )
        # ここでawaitキーワードを使ってコルーチンを実行する
        analysis = await gemini.analyze(prompt)
        self.logger.info('仮説検証の結果: %s', analysis)
        self.logger.info('DeepResearch診断完了。')
        
        # JSON互換性を確保するため、分析結果を文字列化
        if isinstance(analysis, dict):
            analysis_json = analysis
        else:
            # 文字列や他の形式であれば、辞書形式に変換
            analysis_json = {"full_analysis": str(analysis)}
        
        results_dict = {
            "query": query,
            "crawler_feedback": crawler_feedback,
            "analysis": analysis_json,
            "timestamp": datetime.now().isoformat()
        }
        # 保存先ディレクトリの作成（data/research_results）
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = os.path.join(base_dir, "data", "research_results")
        os.makedirs(output_dir, exist_ok=True)

        # ファイル名を作成して結果を保存
        filename = f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(results_dict, f, ensure_ascii=False, indent=2)
        return (
            "DeepResearch診断完了。\n\n"
            "【Crawlerからの検索結果フィードバック】\n" + crawler_feedback +
            "\n【仮説検証の結果】\n" + json.dumps(analysis_json, ensure_ascii=False, indent=2) +
            "\n\n結果は以下のファイルに保存されました: " + filepath
        )


class DeepResearchGUI(PyQt6.QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.deep_research = DeepResearch()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('DeepResearch GUI')
        self.setGeometry(100, 100, 800, 600)
        central_widget = PyQt6.QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = PyQt6.QtWidgets.QVBoxLayout(central_widget)
        search_layout = PyQt6.QtWidgets.QHBoxLayout()
        self.search_input = PyQt6.QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText('検索クエリを入力してください')
        search_button = PyQt6.QtWidgets.QPushButton('検索開始')
        search_button.clicked.connect(self.execute_search)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)
        self.result_area = PyQt6.QtWidgets.QTextEdit()
        self.result_area.setReadOnly(True)
        layout.addWidget(self.result_area)
        self.statusBar().showMessage('準備完了')

    def execute_search(self):
        query = self.search_input.text()
        if not query.strip():
            PyQt6.QtWidgets.QMessageBox.warning(self, '警告', '検索クエリを入力してください')
            return
        self.result_area.clear()
        self.statusBar().showMessage('検索中...')
        self.search_thread = SearchThread(self.deep_research, query)
        self.search_thread.resultReady.connect(self.handle_results)
        self.search_thread.finished.connect(lambda: self.statusBar().showMessage('検索完了'))
        self.search_thread.start()

    def handle_results(self, results: str):
        self.result_area.setPlainText(results)


class SearchThread(PyQt6.QtCore.QThread):
    resultReady = PyQt6.QtCore.pyqtSignal(str)
    def __init__(self, deep_research, query):
        super().__init__()
        self.deep_research = deep_research
        self.query = query
    async def run(self):
        results = await self.deep_research.deep_research(self.query)
        self.resultReady.emit(str(results))


if __name__ == "__main__":
    args = parse_args()
    query = args.query

    deep_research = DeepResearch()
    
    # 非同期実行
    async def run_async():
        return await deep_research.deep_research(query)
    
    # 非同期関数を実行
    result = asyncio.run(run_async())
    
    print(result) 