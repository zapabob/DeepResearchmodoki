from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class Node(BaseModel):
    id: str
    label: str
    type: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    class Config:
        arbitrary_types_allowed = True

class Edge(BaseModel):
    source: str
    target: str
    type: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    weight: float = 1.0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Graph(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SearchResult(BaseModel):
    title: str
    url: str
    content: str
    metadata: Dict[str, Any]
    score: float = 0.0
    created_at: datetime = Field(default_factory=datetime.now)

class Analysis(BaseModel):
    query: str
    summary: str
    keywords: List[str]
    sentiment: str
    insights: List[str]
    graph: Optional[Graph]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)

class ResearchResult(BaseModel):
    query: str
    results: List[SearchResult]
    analysis: Analysis
    created_at: datetime = Field(default_factory=datetime.now)
    processing_time: float 