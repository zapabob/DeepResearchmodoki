import os
import sys
import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

# プロジェクトのルートディレクトリをPythonパスに追加（必要な場合）
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# バックエンドサービスのインポート
from scripts.cot_deepresearch import CoTDeepResearch
from backend.services.langgraph_utils import generate_graph_from_text

class CoTDeepResearchService:
    """
    Chain-of-Thought Deep Researchをバックエンドサービスとして提供するクラス
    """
    
    def __init__(self):
        """
        CoTDeepResearchServiceを初期化する
        """
        # ロガーの設定
        self.logger = logging.getLogger(__name__)
        self.logger.info('CoTDeepResearchServiceが初期化されました。')
        
        # 基本となるCoTDeepResearchクラスのインスタンスを作成
        self.cot_deepresearch = CoTDeepResearch()
    
    async def execute_research(self, 
                        query: str, 
                        max_pages: int = 15, 
                        depth: int = 2, 
                        language: str = "ja") -> Dict[str, Any]:
        """
        Chain-of-Thought Deep Researchを実行する

        Args:
            query (str): 検索クエリ
            max_pages (int): 検索する最大ページ数
            depth (int): 分析の深さ (1=基本, 2=詳細, 3=高度)
            language (str): 検索言語

        Returns:
            Dict[str, Any]: 研究結果を含む辞書
        """
        self.logger.info(f'CoTDeepResearch実行: クエリ="{query}", max_pages={max_pages}, depth={depth}, language={language}')
        
        try:
            # 基本クラスのexecuteメソッドを呼び出す
            result = await self.cot_deepresearch.execute(query, max_pages, depth)

            # 言語情報を追加
            if "metadata" in result:
                result["metadata"]["language"] = language

            # 生成した分析からLangGraphでグラフ生成を試みる
            analysis_text = result.get("analysis", "")
            graph = generate_graph_from_text(str(analysis_text))
            if graph is not None:
                result["langgraph"] = graph

            return result
            
        except Exception as e:
            self.logger.error(f'CoTDeepResearch実行中にエラーが発生しました: {str(e)}', exc_info=True)
            return {
                "error": str(e),
                "message": "CoTDeepResearch実行中にエラーが発生しました。"
            }
    
    def format_results(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        CoTDeepResearchの結果をフォーマットする

        Args:
            result (Dict[str, Any]): CoTDeepResearchからの生の結果

        Returns:
            Dict[str, Any]: フォーマットされた結果
        """
        if "error" in result:
            return result
            
        # 分析結果の整形
        analysis = result.get("analysis", {})
        if isinstance(analysis, dict) and "full_analysis" in analysis:
            analysis_content = analysis["full_analysis"]
        else:
            analysis_content = json.dumps(analysis, ensure_ascii=False)
            
        # メタデータの整形
        metadata = {
            "query": result.get("query", ""),
            "max_pages": result.get("metadata", {}).get("max_pages", 0),
            "depth": result.get("metadata", {}).get("depth", 0),
            "result_count": result.get("metadata", {}).get("result_count", 0),
            "timestamp": datetime.now().isoformat(),
            "filepath": result.get("filepath", "")
        }
        
        # 検索結果の整形
        results = []
        feedback = result.get("feedback", "")
        for line in feedback.split("-" * 40):
            if not line.strip():
                continue
            parts = line.split("\n")
            if len(parts) >= 4:
                title_part = parts[1].replace("タイトル: ", "").strip()
                url_part = parts[2].replace("URL: ", "").strip()
                summary_part = parts[3].replace("概要: ", "").strip()
                
                results.append({
                    "title": title_part,
                    "url": url_part,
                    "content": summary_part,
                    "metadata": {
                        "summary": summary_part[:100] + "..." if len(summary_part) > 100 else summary_part
                    }
                })
        
        # 最終的なレスポンス形式
        formatted_result = {
            "results": results,
            "analysis": {
                "summary": analysis_content[:200] + "..." if len(analysis_content) > 200 else analysis_content,
                "full_analysis": analysis_content,
                "keywords": analysis.get("keywords", []) if isinstance(analysis, dict) else [],
                "insights": analysis.get("insights", []) if isinstance(analysis, dict) else [],
                "sentiment": analysis.get("sentiment", "neutral") if isinstance(analysis, dict) else "neutral"
            },
            "metadata": metadata
        }
        
        return formatted_result 