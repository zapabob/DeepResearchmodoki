import os
import sys
import logging
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
from dotenv import load_dotenv

# プロジェクトのルートディレクトリをPythonパスに追加
root_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(root_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# FastAPIのインポート
from fastapi import FastAPI, HTTPException, Request, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# サービスのインポート
from backend.services.crawler import CrawlerService, SearchResult
from backend.services.gemini import GeminiService
from backend.services.graph import GraphService
from backend.services.cot_deepresearch import CoTDeepResearchService

# 環境変数の読み込み
load_dotenv()

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("backend.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# FastAPIアプリケーションの作成
app = FastAPI(title="Web Deep Research API", version="1.0.0")

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では特定のオリジンに制限すべき
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# リクエスト/レスポンスモデルの定義
class ResearchRequest(BaseModel):
    query: str
    max_pages: Optional[int] = 5
    language: Optional[str] = "ja"

class ResearchResponse(BaseModel):
    results: List[dict]
    analysis: dict
    metadata: Optional[dict] = None

class SearchRequest(BaseModel):
    query: str
    max_pages: Optional[int] = 5
    hypothesis: Optional[str] = None
    use_cot: Optional[bool] = False

class SearchResponse(BaseModel):
    query: str
    timestamp: str
    results: List[SearchResult]
    summary: str
    additional_findings: Optional[List[dict]] = None
    metadata: dict

# サービスのインスタンス
crawler_service = CrawlerService()
gemini_service = GeminiService()
graph_service = GraphService()
cot_service = CoTDeepResearchService()

# ルーターのインポート
from backend.routes.research import router as research_router

# ルーターの登録
app.include_router(research_router, prefix="/research", tags=["research"])

# エンドポイントの定義
@app.post("/api/research", response_model=ResearchResponse)
async def research(request: ResearchRequest):
    """
    指定されたクエリに基づいて研究を実行します。
    """
    try:
        logger.info(f"Research request received: {request.query}")
        results = await crawler_service.deep_crawl(request.query, request.max_pages)
        analysis = await gemini_service.analyze(results)
        
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "query": request.query,
            "max_pages": request.max_pages,
            "language": request.language
        }
        
        return {
            "results": results,
            "analysis": analysis,
            "metadata": metadata
        }
    except Exception as e:
        logger.error(f"Error in research endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/deepresearch", response_model=ResearchResponse)
async def deep_research(request: ResearchRequest):
    """
    より詳細な研究を実行します。
    """
    try:
        logger.info(f"Deep research request received: {request.query}")
        results = await crawler_service.deep_crawl(request.query, request.max_pages)
        
        # 結果のテキストを結合
        combined_text = "\n\n".join([
            f"タイトル: {result.get('title', '')}\n"
            f"URL: {result.get('url', '')}\n"
            f"内容: {result.get('content', '')}"
            for result in results
        ])
        
        # Geminiによる分析
        analysis = await gemini_service.analyze(combined_text)
        
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "query": request.query,
            "max_pages": request.max_pages,
            "language": request.language
        }
        
        return {
            "results": results,
            "analysis": analysis,
            "metadata": metadata
        }
    except Exception as e:
        logger.error(f"Error in deep_research endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/research/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    検索を実行します。
    """
    try:
        logger.info(f"Search request received: {request.query}")
        results = await crawler_service.deep_crawl(request.query, request.max_pages)
        
        # 結果の要約
        summary = "検索結果はありませんでした。別のキーワードで試してください。"
        if results:
            # Geminiサービスを使用して要約を生成
            try:
                content_for_summary = "\n\n".join([
                    f"タイトル: {r.get('title', 'No title')}\n"
                    f"URL: {r.get('url', 'No URL')}\n"
                    f"内容: {r.get('content', 'No content')[:300]}..."
                    for r in results[:5]  # 最初の5件のみ使用
                ])
                
                prompt = f"""
                以下の検索結果を日本語で簡潔に要約してください。
                検索クエリ: {request.query}
                
                {content_for_summary}
                
                要約:
                """
                
                summary = await gemini_service.generate_text(prompt)
                if not summary or len(summary.strip()) < 10:
                    summary = f"{len(results)}件の結果が見つかりました。"
            except Exception as e:
                logger.error(f"Error generating summary: {str(e)}")
                summary = f"{len(results)}件の結果が見つかりました。"
        
        timestamp = datetime.now().isoformat()
        
        # 追加の発見事項を生成
        additional_findings = []
        if results and len(results) >= 2:
            try:
                # 結果から追加の発見事項を抽出
                content_for_findings = "\n\n".join([
                    f"タイトル: {r.get('title', 'No title')}\n"
                    f"内容: {r.get('content', 'No content')[:200]}..."
                    for r in results[:3]  # 最初の3件のみ使用
                ])
                
                findings_prompt = f"""
                以下の検索結果から、興味深い発見や洞察を3つ抽出してください。
                検索クエリ: {request.query}
                
                {content_for_findings}
                
                発見事項（JSON形式で返してください）:
                [
                  {{"summary": "発見1の説明", "confidence": 0.9}},
                  {{"summary": "発見2の説明", "confidence": 0.8}},
                  {{"summary": "発見3の説明", "confidence": 0.7}}
                ]
                """
                
                findings_text = await gemini_service.generate_text(findings_prompt)
                try:
                    # JSON形式の文字列をパース
                    import json
                    findings_json = json.loads(findings_text)
                    if isinstance(findings_json, list):
                        additional_findings = findings_json
                except Exception as json_err:
                    logger.error(f"Error parsing findings JSON: {str(json_err)}")
            except Exception as e:
                logger.error(f"Error generating additional findings: {str(e)}")
        
        return {
            "query": request.query,
            "timestamp": timestamp,
            "results": results,
            "summary": summary,
            "additional_findings": additional_findings,
            "metadata": {
                "depth": request.max_pages,
                "total_sources": len(results),
                "execution_time": int((datetime.now() - datetime.fromisoformat(timestamp)).total_seconds() * 1000)
            }
        }
    except Exception as e:
        logger.error(f"Error in search endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/cot_deepresearch", response_model=ResearchResponse)
async def cot_deep_research(request: ResearchRequest):
    """
    Chain-of-Thought Deep Researchを実行します。
    """
    try:
        logger.info(f"CoT Deep Research request received: {request.query}")
        
        # CoTDeepResearchServiceを使用
        result = await cot_service.execute_research(
            query=request.query,
            max_pages=request.max_pages,
            language=request.language
        )
        
        # 結果のフォーマット
        formatted_result = cot_service.format_results(result)
        
        return formatted_result
    except Exception as e:
        logger.error(f"Error in cot_deep_research endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    """
    サーバーの健康状態を確認します。
    """
    return {"status": "ok"}

@app.get("/")
async def index():
    """
    APIのルートエンドポイント
    """
    return {"message": "Web Deep Research API"}

@app.post("/api/search", response_model=SearchResponse)
async def api_search(request: SearchRequest):
    """
    APIを通じて検索を実行します。
    """
    try:
        logger.info(f"API Search request received: {request.query}")
        
        # 検索の実行
        results = await crawler_service.deep_crawl(request.query, request.max_pages)
        
        # 結果の要約
        summary = "検索結果の要約"
        if results:
            # Geminiによる要約
            combined_text = "\n\n".join([
                f"タイトル: {result.get('title', '')}\n"
                f"URL: {result.get('url', '')}\n"
                f"内容: {result.get('content', '')}"
                for result in results
            ])
            
            analysis = await gemini_service.analyze(combined_text)
            summary = analysis.get("summary", f"{len(results)}件の結果が見つかりました。")
        
        timestamp = datetime.now().isoformat()
        
        return {
            "query": request.query,
            "timestamp": timestamp,
            "results": results,
            "summary": summary,
            "metadata": {
                "max_pages": request.max_pages,
                "use_cot": request.use_cot,
                "hypothesis": request.hypothesis
            }
        }
    except Exception as e:
        logger.error(f"Error in api_search endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """
    APIの健康状態を確認します。
    """
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# サーバー起動部分
if __name__ == "__main__":
    import uvicorn
    
    # ポート番号を8002に変更
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True) 