import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_research_endpoint():
    test_request = {
        "query": "テストクエリ",
        "max_pages": 2,
        "language": "ja"
    }

    mock_results = [
        {
            "title": "テスト記事",
            "url": "https://example.com",
            "content": "テストコンテンツ",
            "metadata": {
                "source": "test",
                "score": 0.8
            }
        }
    ]

    mock_analysis = {
        "summary": "テストの要約",
        "keywords": ["キーワード1", "キーワード2"],
        "sentiment": "positive",
        "insights": ["洞察1", "洞察2"]
    }

    # サービスのモック
    with patch('services.crawler.CrawlerService.crawl') as mock_crawl:
        with patch('services.gemini.GeminiService.analyze') as mock_analyze:
            mock_crawl.return_value = mock_results
            mock_analyze.return_value = mock_analysis

            response = client.post("/api/v1/research", json=test_request)
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["results"]) == 1
            assert data["analysis"]["summary"] == "テストの要約"

def test_research_invalid_request():
    invalid_request = {
        "query": "",  # 空のクエリ
        "max_pages": 2,
        "language": "ja"
    }

    response = client.post("/api/v1/research", json=invalid_request)
    assert response.status_code == 422  # バリデーションエラー

@pytest.mark.asyncio
async def test_deep_research_endpoint():
    test_request = {
        "query": "深層テストクエリ",
        "max_pages": 2,
        "language": "ja"
    }

    mock_results = [
        {
            "title": "深層テスト記事",
            "url": "https://example.com/deep",
            "content": "深層テストコンテンツ",
            "metadata": {
                "source": "deep_web",
                "score": 0.95
            }
        }
    ]

    mock_analysis = {
        "summary": "深層テストの要約",
        "keywords": ["深層キーワード1", "深層キーワード2"],
        "sentiment": "neutral",
        "insights": ["深層洞察1", "深層洞察2"]
    }

    mock_graph = {
        "nodes": [{"id": "1", "label": "テスト"}],
        "edges": []
    }

    # サービスのモック
    with patch('services.crawler.CrawlerService.deep_crawl') as mock_crawl:
        with patch('services.gemini.GeminiService.analyze') as mock_analyze:
            with patch('services.graph.GraphService.create_graph') as mock_graph_create:
                mock_crawl.return_value = mock_results
                mock_analyze.return_value = mock_analysis
                mock_graph_create.return_value = mock_graph

                response = client.post("/api/v1/deepresearch", json=test_request)
                
                assert response.status_code == 200
                data = response.json()
                assert len(data["results"]) == 1
                assert data["analysis"]["summary"] == "深層テストの要約"
                assert "graph" in data["metadata"] 