"""FastAPI-based API server"""
from typing import Dict, List, Optional
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .analyzer import TextAnalyzer, AnalyzerConfig
from .crawler import WebCrawler, CrawlerConfig
from .knowledge_graph import KnowledgeGraph, GraphConfig

app = FastAPI(
    title="Web Deep Research API",
    description="API for web research and knowledge graph generation",
    version="0.1.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切なオリジンを指定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# フロントエンドのビルドディレクトリをマウント
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "build")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")


class ResearchRequest(BaseModel):
    """Research request parameters"""
    query: str
    urls: List[str]
    max_depth: int = 3


class ResearchResponse(BaseModel):
    """Research response data"""
    summary: str
    entities: List[Dict]
    graph_data: Dict


@app.post("/api/research", response_model=ResearchResponse)
async def conduct_research(request: ResearchRequest) -> ResearchResponse:
    """
    Conduct web research based on query and URLs
    
    Args:
        request: Research request parameters
        
    Returns:
        Research results including summary and knowledge graph
    """
    try:
        # Initialize components
        crawler = WebCrawler(CrawlerConfig(base_url="", api_key=""))  # TODO: Configure
        analyzer = TextAnalyzer(AnalyzerConfig(project_id=""))  # TODO: Configure
        graph = KnowledgeGraph(GraphConfig())
        
        # Crawl URLs
        crawled_data = []
        for url in request.urls:
            data = await crawler.crawl(url)
            crawled_data.extend(data)
            
        # Analyze text
        analysis_results = []
        for data in crawled_data:
            result = await analyzer.analyze(data["text"])
            analysis_results.append(result)
            
        # Generate knowledge graph
        for result in analysis_results:
            graph.add_entities(result["entities"])
            graph.add_relationships(result["relationships"])
            
        visualization = graph.generate_visualization()
        
        return ResearchResponse(
            summary="",  # TODO: Generate summary
            entities=[],  # TODO: Extract entities
            graph_data=visualization
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/{path:path}")
async def serve_frontend(path: str):
    """Serve frontend static files"""
    if not os.path.exists(frontend_path):
        raise HTTPException(status_code=404, detail="Frontend not built")
        
    file_path = os.path.join(frontend_path, path)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return FileResponse(os.path.join(frontend_path, "index.html")) 