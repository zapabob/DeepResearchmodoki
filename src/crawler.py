"""Web crawler module using FirecrawllAPI"""
from typing import Dict, List, Optional
import json
import asyncio

import aiohttp
from bs4 import BeautifulSoup
from pydantic import BaseModel


class CrawlerConfig(BaseModel):
    """Crawler configuration settings"""
    base_url: str
    api_key: str
    max_depth: int = 3
    timeout: int = 30
    headers: Optional[Dict[str, str]] = None
    max_concurrent_requests: int = 5


class WebCrawler:
    """Web crawler implementation using FirecrawllAPI"""
    
    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.session = None
        self.semaphore = asyncio.Semaphore(config.max_concurrent_requests)
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                **(self.config.headers or {})
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def _fetch_page(self, url: str) -> Dict:
        """
        Fetch a single page using FirecrawllAPI
        
        Args:
            url: Target URL to fetch
            
        Returns:
            Page data including content and metadata
        """
        async with self.semaphore:
            endpoint = f"{self.config.base_url}/crawl"
            params = {
                "url": url,
                "depth": self.config.max_depth
            }
            
            async with self.session.post(endpoint, json=params) as response:
                response.raise_for_status()
                data = await response.json()
                
                # HTMLコンテンツをパース
                soup = BeautifulSoup(data["html"], "html.parser")
                
                # メタデータを抽出
                title = soup.title.string if soup.title else ""
                description = soup.find("meta", {"name": "description"})
                description = description["content"] if description else ""
                
                # 本文を抽出（シンプルな実装）
                text = " ".join([p.get_text() for p in soup.find_all("p")])
                
                return {
                    "url": url,
                    "title": title,
                    "description": description,
                    "text": text,
                    "metadata": data.get("metadata", {}),
                    "links": data.get("links", [])
                }
    
    async def crawl(self, url: str) -> List[Dict]:
        """
        Crawl the specified URL using FirecrawllAPI
        
        Args:
            url: Target URL to crawl
            
        Returns:
            List of crawled data
        """
        if not self.session:
            async with self:
                return await self._crawl(url)
        return await self._crawl(url)
        
    async def _crawl(self, url: str) -> List[Dict]:
        """Internal crawl implementation"""
        try:
            # 単一ページのクロール
            page_data = await self._fetch_page(url)
            results = [page_data]
            
            # 設定された深さまでリンクを追跡
            if self.config.max_depth > 1:
                tasks = []
                for link in page_data["links"][:10]:  # 最大10個のリンクまで
                    if link.startswith(("http://", "https://")):
                        tasks.append(self._fetch_page(link))
                
                if tasks:
                    additional_pages = await asyncio.gather(*tasks, return_exceptions=True)
                    for page in additional_pages:
                        if isinstance(page, Dict):
                            results.append(page)
            
            return results
            
        except aiohttp.ClientError as e:
            # エラーハンドリング
            return [{
                "url": url,
                "error": str(e),
                "text": "",
                "metadata": {}
            }] 