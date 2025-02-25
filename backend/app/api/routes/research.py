from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
from app.services.crawler_service import CrawlerService  # ウェブクロール処理用
from app.services.gemini_service import GeminiService    # Geminiによるテキスト分析用
from app.services.googleai_service import GoogleAIService  # Google AIによる追加インサイト取得用
from app.services.graph_service import GraphService        # ナレッジグラフ生成用

class ResearchRequest(BaseModel):
    query: str

router = APIRouter()

# サービスのインスタンス化
crawler_service = CrawlerService()
gemini_service = GeminiService()
graph_service = GraphService()
googleai_service = GoogleAIService()

@router.post("/research")
async def perform_research(request: ResearchRequest) -> Dict[str, Any]:
    try:
        # Step 1: Web crawling
        crawl_results = await crawler_service.crawl(request.query)
        
        # Step 2: Text analysis with Gemini
        analysis_result = await gemini_service.analyze(crawl_results)
        
        # Step 3: Additional insights with Google AI
        additional_insights = await googleai_service.analyze_query(request.query, " ".join(crawl_results))
        
        # Step 4: Knowledge graph generation
        graph_data = graph_service.generate_graph(analysis_result)
        
        return {
            "query": request.query,
            "crawled_data": crawl_results,
            "analysis": analysis_result,
            "additional_insights": additional_insights,
            "knowledge_graph": graph_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 