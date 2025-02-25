from functools import lru_cache
from typing import Generator
from config.settings import get_settings
from services.crawler import CrawlerService
from services.gemini import GeminiService
from services.graph import GraphService

@lru_cache()
def get_crawler_service() -> CrawlerService:
    """
    クローラーサービスのインスタンスを取得します。
    """
    settings = get_settings()
    return CrawlerService(
        firecrawl_api_key=settings.FIRECRAWL_API_KEY,
        use_default_browser=settings.USE_DEFAULT_BROWSER,
        selenium_browser=settings.SELENIUM_BROWSER
    )

@lru_cache()
def get_gemini_service() -> GeminiService:
    """
    Geminiサービスのインスタンスを取得します。
    """
    settings = get_settings()
    return GeminiService(
        api_key=settings.GOOGLE_AISTUDIO_API_KEY
    )

@lru_cache()
def get_graph_service() -> GraphService:
    """
    グラフサービスのインスタンスを取得します。
    """
    settings = get_settings()
    return GraphService(
        uri=settings.NEO4J_URI,
        user=settings.NEO4J_USER,
        password=settings.NEO4J_PASSWORD
    ) 