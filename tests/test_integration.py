"""Integration test cases for Web Deep Research System"""
import os
import sys
import json
import pytest
import aiohttp
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

# プロジェクトルートをPythonパスに追加
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.api import app
from src.crawler import CrawlerConfig
from src.analyzer import AnalyzerConfig
from src.knowledge_graph import GraphConfig

@pytest.fixture
def test_client():
    """FastAPI test client"""
    return TestClient(app)

@pytest.fixture
def mock_html_content():
    """Sample HTML content for testing"""
    return """
    <html>
        <head>
            <title>AIと機械学習の最新動向</title>
            <meta name="description" content="人工知能と機械学習の最新研究と応用事例">
        </head>
        <body>
            <p>GoogleのGeminiは、マルチモーダルAIの新時代を切り開いています。</p>
            <p>OpenAIは、GPT-4の研究開発を継続的に進めています。</p>
            <p>Microsoftは、Azure AIプラットフォームを通じて企業のAI導入を支援しています。</p>
        </body>
    </html>
    """

@pytest.fixture
def mock_analysis_response():
    """Mock GeminiPro analysis response"""
    return Mock(
        text=json.dumps({
            "summary": "AIと機械学習の分野では、GoogleのGemini、OpenAIのGPT-4、MicrosoftのAzure AIなど、主要企業による革新的な開発が進んでいます。",
            "entities": [
                {"name": "Gemini", "type": "Technology", "importance": 0.9},
                {"name": "Google", "type": "Organization", "importance": 0.8},
                {"name": "GPT-4", "type": "Technology", "importance": 0.8},
                {"name": "OpenAI", "type": "Organization", "importance": 0.7},
                {"name": "Microsoft", "type": "Organization", "importance": 0.7}
            ],
            "sentiment": {"label": "positive", "score": 0.8},
            "relationships": [
                {"source": "Google", "target": "Gemini", "type": "develops", "weight": 0.9},
                {"source": "OpenAI", "target": "GPT-4", "type": "develops", "weight": 0.8},
                {"source": "Microsoft", "target": "Azure AI", "type": "provides", "weight": 0.7}
            ]
        })
    )

@pytest.mark.asyncio
async def test_research_workflow(test_client, mock_html_content, mock_analysis_response):
    """Test the complete research workflow"""
    
    # クローラーのモックを設定
    with patch("aiohttp.ClientSession.post") as mock_crawler:
        mock_crawler.return_value.__aenter__.return_value.json.return_value = {
            "html": mock_html_content,
            "metadata": {"status": 200},
            "links": []
        }
        
        # アナライザーのモックを設定
        with patch("google.cloud.aiplatform.init"):
            with patch("google.cloud.aiplatform.TextGenerationModel.from_pretrained") as mock_model:
                instance = mock_model.return_value
                instance.predict_async.return_value = mock_analysis_response
                
                # リサーチリクエストを送信
                response = test_client.post(
                    "/api/research",
                    json={
                        "query": "AIと機械学習の最新動向",
                        "urls": ["https://example.com/ai-news"],
                        "max_depth": 2
                    }
                )
                
                # レスポンスを検証
                assert response.status_code == 200
                data = response.json()
                
                # 結果の構造を検証
                assert "summary" in data
                assert "entities" in data
                assert "graph_data" in data
                
                # エンティティの検証
                assert len(data["entities"]) >= 3
                assert all("name" in entity for entity in data["entities"])
                assert all("type" in entity for entity in data["entities"])
                assert all("importance" in entity for entity in data["entities"])
                
                # グラフデータの検証
                graph_data = data["graph_data"]
                assert "nodes" in graph_data
                assert "edges" in graph_data
                assert "metadata" in graph_data
                
                # ノードとエッジの関係を検証
                nodes = {node["id"] for node in graph_data["nodes"]}
                for edge in graph_data["edges"]:
                    assert edge["source"] in nodes
                    assert edge["target"] in nodes

@pytest.mark.asyncio
async def test_error_handling(test_client):
    """Test error handling in the research workflow"""
    
    # クローラーでエラーを発生させる
    with patch("aiohttp.ClientSession.post") as mock_crawler:
        mock_crawler.side_effect = aiohttp.ClientError("接続エラー")
        
        # リサーチリクエストを送信
        response = test_client.post(
            "/api/research",
            json={
                "query": "AIと機械学習の最新動向",
                "urls": ["https://example.com/ai-news"],
                "max_depth": 2
            }
        )
        
        # エラーレスポンスを検証
        assert response.status_code == 500
        data = response.json()
        assert "detail" in data

@pytest.mark.asyncio
async def test_metrics_endpoint(test_client):
    """Test metrics endpoint functionality"""
    # メトリクスエンドポイントにアクセス
    response = test_client.get("/metrics")
    
    # レスポンスを検証
    assert response.status_code == 200
    metrics_text = response.text
    
    # 必要なメトリクスが含まれているか確認
    assert "research_requests_total" in metrics_text
    assert "research_duration_seconds" in metrics_text
    assert "crawled_pages_total" in metrics_text
    assert "analyzed_texts_total" in metrics_text
    assert "graphs_generated_total" in metrics_text 