import pytest
from unittest.mock import Mock, patch
from services.crawler import CrawlerService

@pytest.fixture
def crawler_service():
    return CrawlerService(
        firecrawl_api_key="test_key",
        use_default_browser=False,
        selenium_browser="chrome"
    )

@pytest.mark.asyncio
async def test_crawl_success(crawler_service):
    # モックデータの準備
    mock_results = [
        {
            "title": "テスト記事1",
            "url": "https://example.com/1",
            "content": "テストコンテンツ1",
            "metadata": {
                "source": "test",
                "score": 0.8
            }
        },
        {
            "title": "テスト記事2",
            "url": "https://example.com/2",
            "content": "テストコンテンツ2",
            "metadata": {
                "source": "test",
                "score": 0.9
            }
        }
    ]

    # FirecrawlAPIのモック
    with patch('services.crawler.FirecrawlApp') as mock_firecrawl:
        mock_firecrawl.return_value.search.return_value = mock_results
        
        # テストの実行
        results = await crawler_service.crawl("テストクエリ", max_pages=2)
        
        # 結果の検証
        assert len(results) == 2
        assert results[0]["title"] == "テスト記事1"
        assert results[1]["title"] == "テスト記事2"
        
        # APIが正しく呼び出されたことを確認
        mock_firecrawl.return_value.search.assert_called_once_with(
            query="テストクエリ",
            language="ja",
            include_metadata=True
        )

@pytest.mark.asyncio
async def test_crawl_empty_results(crawler_service):
    # 空の結果を返すモック
    with patch('services.crawler.FirecrawlApp') as mock_firecrawl:
        mock_firecrawl.return_value.search.return_value = []
        
        # テストの実行
        results = await crawler_service.crawl("テストクエリ", max_pages=2)
        
        # 結果の検証
        assert len(results) == 0

@pytest.mark.asyncio
async def test_crawl_api_error(crawler_service):
    # エラーを発生させるモック
    with patch('services.crawler.FirecrawlApp') as mock_firecrawl:
        mock_firecrawl.return_value.search.side_effect = Exception("API Error")
        
        # エラーハンドリングの検証
        with pytest.raises(Exception) as exc_info:
            await crawler_service.crawl("テストクエリ", max_pages=2)
        
        assert str(exc_info.value) == "API Error"

@pytest.mark.asyncio
async def test_deep_crawl_success(crawler_service):
    # モックデータの準備
    mock_results = [
        {
            "title": "深層テスト記事1",
            "url": "https://example.com/deep/1",
            "content": "深層テストコンテンツ1",
            "metadata": {
                "source": "deep_web",
                "score": 0.95
            }
        }
    ]

    # Seleniumのモック
    with patch('services.crawler.webdriver') as mock_webdriver:
        mock_driver = Mock()
        mock_driver.page_source = "<html>Test</html>"
        mock_webdriver.Chrome.return_value = mock_driver
        
        # FirecrawlAPIのモック
        with patch('services.crawler.FirecrawlApp') as mock_firecrawl:
            mock_firecrawl.return_value.search.return_value = mock_results
            
            # テストの実行
            results = await crawler_service.deep_crawl("深層テストクエリ", max_pages=1)
            
            # 結果の検証
            assert len(results) == 1
            assert results[0]["title"] == "深層テスト記事1"
            assert results[0]["metadata"]["source"] == "deep_web" 