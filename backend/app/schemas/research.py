from pydantic import BaseModel, Field
from typing import Optional, List

class ResearchRequest(BaseModel):
    query: str = Field(..., description="検索クエリ")
    max_pages: int = Field(default=5, ge=1, le=20, description="取得する最大ページ数")
    language: str = Field(default="ja", description="検索言語")
    deep_search: bool = Field(default=False, description="深層検索を実行するかどうか")
    filters: Optional[List[str]] = Field(default=None, description="検索フィルター")

    class Config:
        schema_extra = {
            "example": {
                "query": "人工知能の最新動向",
                "max_pages": 5,
                "language": "ja",
                "deep_search": True,
                "filters": ["academic", "news"]
            }
        } 