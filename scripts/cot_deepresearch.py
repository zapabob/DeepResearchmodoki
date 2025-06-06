import os
import sys
import logging
import json
import argparse
from datetime import datetime

# プロジェクトのルートディレクトリをPythonパスに追加（最初に実行）
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

# 依存ライブラリのインポート
import nest_asyncio

# バックエンドサービスのインポート
from backend.services.crawler import CrawlerService
from backend.services import get_ai_service

# 非同期処理の設定
nest_asyncio.apply()

# ログディレクトリの作成
log_dir = os.path.join(root_dir, "logs")
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "cot_deepresearch.log")

logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CoTDeepResearch:
    def __init__(self):
        self.logger = logger
        self.logger.info('CoTDeepResearchインスタンスが作成されました。')
        
    async def execute(self, query, max_pages=15, depth=2):
        """Chain-of-Thought Deep Researchを実行する"""
        self.logger.info(f'CoTDeepResearch開始: クエリ="{query}", max_pages={max_pages}, depth={depth}')
        
        try:
            # クローラーサービスの初期化
            crawler = CrawlerService()
            self.logger.info('クローラーサービスを初期化しました。')
            
            # 検索の実行
            self.logger.info(f'検索を開始します: {query}')
            results = crawler.crawl(query, max_pages=max_pages)
            self.logger.info(f'検索結果: {len(results)}件取得')
            
            # 検索結果のフィードバック生成
            crawler_feedback = self._generate_feedback(results)
            
            # 検索結果からChain-of-Thought用の入力テキストを生成
            combined_text = self._generate_combined_text(results)
            
            # Chain-of-Thought推論の実行
            self.logger.info('Chain-of-Thought推論を開始します。')
            gemini = get_ai_service()
            
            # CoTプロンプトの作成
            prompt = self._create_cot_prompt(query, combined_text, depth)
            
            # 分析の実行
            analysis = await gemini.analyze(prompt)
            self.logger.info('Chain-of-Thought推論が完了しました。')
            
            # 結果の保存
            results_dict = {
                "query": query,
                "crawler_feedback": crawler_feedback,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "max_pages": max_pages,
                    "depth": depth,
                    "result_count": len(results)
                }
            }
            
            # 保存先ディレクトリの作成
            output_dir = os.path.join(root_dir, "data", "research_results")
            os.makedirs(output_dir, exist_ok=True)
            
            # ファイル名を作成して結果を保存
            filename = f"cot_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(output_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(results_dict, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f'結果を保存しました: {filepath}')
            
            return {
                "message": "CoTDeepResearch診断完了。",
                "feedback": crawler_feedback,
                "analysis": analysis,
                "filepath": filepath
            }
            
        except Exception as e:
            self.logger.error(f'CoTDeepResearch実行中にエラーが発生しました: {str(e)}', exc_info=True)
            return {
                "error": str(e),
                "message": "CoTDeepResearch実行中にエラーが発生しました。"
            }
    
    def _generate_feedback(self, results):
        """検索結果からフィードバックを生成する"""
        feedback = ""
        for i, res in enumerate(results, 1):
            title = res.get('title', 'N/A')
            url = res.get('url', 'N/A')
            summary = res.get('metadata', {}).get('summary')
            if not summary:
                summary = res.get('content', '')[:200]
            feedback_line = f"結果 {i}:\nタイトル: {title}\nURL: {url}\n概要: {summary}\n" + ("-" * 40) + "\n"
            feedback += feedback_line
        return feedback
    
    def _generate_combined_text(self, results):
        """検索結果から結合テキストを生成する"""
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
        return combined_text
    
    def _create_cot_prompt(self, query, combined_text, depth):
        """Chain-of-Thoughtプロンプトを作成する"""
        depth_str = "詳細" if depth >= 2 else "基本"
        
        prompt = (
            f"# Chain-of-Thought Deep Research: {query}\n\n"
            f"以下の幅広いウェブ検索結果に基づいて、{depth_str}な分析と仮説検証を行ってください。\n\n"
            "## ステップ1: 検索結果の整理\n"
            "まず、提供された検索結果を整理し、各情報源の信頼性、関連性、最新性を評価してください。\n\n"
            "## ステップ2: 主要な事実の抽出\n"
            "各検索結果から主要な事実、主張、データポイントを抽出してください。矛盾する情報がある場合は特に注記してください。\n\n"
            "## ステップ3: 複数の仮説の形成\n"
            f"抽出した事実に基づいて、少なくとも{3 if depth >= 2 else 2}つの異なる仮説を形成してください。各仮説は明確に区別され、検証可能であるべきです。\n\n"
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
        
        if depth >= 3:
            # 深度3以上の場合、より詳細な分析を要求
            prompt += (
                "\n## 追加の分析要件:\n"
                "1. 各情報源のバイアスや視点の違いを特定し、それが結論にどのように影響するか分析してください。\n"
                "2. 時系列的な変化や傾向があれば特定してください。\n"
                "3. 複数の視点から問題を検討し、異なる文化的・社会的文脈での解釈の違いを考慮してください。\n"
                "4. 結論の実用的な応用や影響について考察してください。\n"
            )
        
        return prompt

async def main():
    parser = argparse.ArgumentParser(description='Chain-of-Thought Deep Research')
    parser.add_argument('query', nargs='?', help='検索クエリ')
    parser.add_argument('--max-pages', type=int, default=15, help='最大ページ数')
    parser.add_argument('--depth', type=int, default=2, choices=[1, 2, 3], help='分析の深さ (1=基本, 2=詳細, 3=高度)')
    args = parser.parse_args()
    
    query = args.query
    if not query:
        query = input('検索クエリを入力してください: ')
    
    cot = CoTDeepResearch()
    result = await cot.execute(query, args.max_pages, args.depth)
    
    if "error" in result:
        print(f"エラー: {result['error']}")
        return
    
    print("\nCoTDeepResearch診断完了。\n")
    print("【Crawlerからの検索結果フィードバック】")
    print(result["feedback"])
    print("\n【仮説検証の結果】")
    
    # 分析結果の表示
    analysis = result["analysis"]
    if isinstance(analysis, dict) and "full_analysis" in analysis:
        print(analysis["full_analysis"])
    else:
        print(json.dumps(analysis, ensure_ascii=False, indent=2))
    
    print(f"\n結果は以下のファイルに保存されました: {result['filepath']}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 