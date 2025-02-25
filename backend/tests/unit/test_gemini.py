import pytest
from unittest.mock import Mock, patch
from services.gemini import GeminiService

@pytest.fixture
def gemini_service():
    return GeminiService(api_key="test_key")

@pytest.mark.asyncio
async def test_analyze_success(gemini_service):
    # モックデータの準備
    mock_crawled_data = [
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

    mock_response = {
        "summary": "テストの要約",
        "keywords": ["キーワード1", "キーワード2"],
        "sentiment": "positive",
        "insights": ["洞察1", "洞察2"]
    }

    # Gemini APIのモック
    with patch('services.gemini.ChatGoogleGenerativeAI') as mock_gemini:
        mock_model = Mock()
        mock_model.generate_content.return_value.response.text.return_value = str(mock_response)
        mock_gemini.return_value = mock_model
        
        # テストの実行
        analysis = await gemini_service.analyze(mock_crawled_data)
        
        # 結果の検証
        assert analysis["summary"] == "テストの要約"
        assert len(analysis["keywords"]) == 2
        assert analysis["sentiment"] == "positive"
        assert len(analysis["insights"]) == 2

@pytest.mark.asyncio
async def test_analyze_empty_data(gemini_service):
    # 空のデータでのテスト
    with pytest.raises(ValueError) as exc_info:
        await gemini_service.analyze([])
    assert str(exc_info.value) == "分析するデータが空です"

@pytest.mark.asyncio
async def test_analyze_api_error(gemini_service):
    mock_crawled_data = [
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

    # APIエラーのモック
    with patch('services.gemini.ChatGoogleGenerativeAI') as mock_gemini:
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_gemini.return_value = mock_model
        
        # エラーハンドリングの検証
        with pytest.raises(Exception) as exc_info:
            await gemini_service.analyze(mock_crawled_data)
        assert str(exc_info.value) == "API Error"

@pytest.mark.asyncio
async def test_generate_summary_success(gemini_service):
    test_text = "要約するテストテキスト"
    expected_summary = "テキストの要約"

    # Gemini APIのモック
    with patch('services.gemini.ChatGoogleGenerativeAI') as mock_gemini:
        mock_model = Mock()
        mock_model.generate_content.return_value.response.text.return_value = expected_summary
        mock_gemini.return_value = mock_model
        
        # テストの実行
        summary = await gemini_service.generate_summary(test_text)
        
        # 結果の検証
        assert summary == expected_summary
        mock_model.generate_content.assert_called_once() 