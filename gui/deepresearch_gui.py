import sys
import os
import json
import requests
from PyQt6 import QtWidgets, QtCore

# プロジェクトのルートディレクトリをPythonパスに追加
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)


class DeepResearchGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('DeepResearch GUI')
        self.setGeometry(100, 100, 800, 600)
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)

        # 検索入力部分
        search_layout = QtWidgets.QHBoxLayout()
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText('検索クエリを入力してください')
        search_button = QtWidgets.QPushButton('検索開始')
        search_button.clicked.connect(self.execute_search)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)

        # 結果表示エリア
        self.result_area = QtWidgets.QTextEdit()
        self.result_area.setReadOnly(True)
        layout.addWidget(self.result_area)

        # ステータスバー
        self.statusBar().showMessage('準備完了')

    def execute_search(self):
        query = self.search_input.text()
        if not query.strip():
            QtWidgets.QMessageBox.warning(self, '警告', '検索クエリを入力してください')
            return

        self.result_area.clear()
        self.statusBar().showMessage('検索中...')
        self.search_thread = SearchThread(query)
        self.search_thread.resultReady.connect(self.handle_results)
        self.search_thread.finished.connect(lambda: self.statusBar().showMessage('検索完了'))
        self.search_thread.start()

    def handle_results(self, results: str):
        self.result_area.setPlainText(results)


class SearchThread(QtCore.QThread):
    resultReady = QtCore.pyqtSignal(str)

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        try:
            payload = {"query": self.query, "max_pages": 10, "language": "ja"}
            response = requests.post("http://localhost:8001/api/cot_deepresearch", json=payload)
            if response.ok:
                data = response.json()
                output = json.dumps(data, ensure_ascii=False, indent=2)
            else:
                output = f"エラー: {response.status_code} {response.text}"
        except Exception as e:
            output = f"通信エラー: {str(e)}"
        self.resultReady.emit(output)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    gui = DeepResearchGUI()
    gui.show()
    sys.exit(app.exec()) 