"""Text analysis module using Google AI Studio's GeminiPro"""
from typing import Dict, List, Optional
import json

from google.cloud import aiplatform
from google.cloud.aiplatform import TextGenerationModel
from pydantic import BaseModel


class AnalyzerConfig(BaseModel):
    """Analyzer configuration settings"""
    project_id: str
    location: str = "us-central1"
    api_endpoint: str = "us-central1-aiplatform.googleapis.com"
    model_name: str = "gemini-pro"
    temperature: float = 0.3
    max_output_tokens: int = 1024


class TextAnalyzer:
    """Text analysis implementation using GeminiPro"""
    
    def __init__(self, config: AnalyzerConfig):
        self.config = config
        aiplatform.init(
            project=config.project_id,
            location=config.location,
            api_endpoint=config.api_endpoint
        )
        self.model = TextGenerationModel.from_pretrained(config.model_name)
        
    async def analyze(self, text: str) -> Dict:
        """
        Analyze text using GeminiPro
        
        Args:
            text: Input text to analyze
            
        Returns:
            Analysis results including summary, entities, and sentiment
        """
        # テキスト解析のプロンプトを作成
        prompt = f"""
以下のテキストを解析し、以下の形式でJSONを生成してください：
1. 要約（最大200文字）
2. 重要なエンティティ（人物、組織、場所、概念など）
3. 感情分析（positive/negative/neutral）
4. エンティティ間の関係性

テキスト:
{text}

出力形式:
{{
    "summary": "テキストの要約",
    "entities": [
        {{"name": "エンティティ名", "type": "エンティティタイプ", "importance": 0.0-1.0}}
    ],
    "sentiment": {{"label": "感情ラベル", "score": 0.0-1.0}},
    "relationships": [
        {{"source": "エンティティ1", "target": "エンティティ2", "type": "関係タイプ", "weight": 0.0-1.0}}
    ]
}}
"""
        
        # GeminiProで解析を実行
        response = await self.model.predict_async(
            prompt,
            temperature=self.config.temperature,
            max_output_tokens=self.config.max_output_tokens
        )
        
        try:
            # レスポンスをJSONとしてパース
            result = json.loads(response.text)
            return result
        except json.JSONDecodeError:
            # JSONパースに失敗した場合のフォールバック
            return {
                "summary": response.text[:200],
                "entities": [],
                "sentiment": {"label": "neutral", "score": 0.5},
                "relationships": []
            }
        
    async def generate_summary(self, text: str, max_length: int = 200) -> str:
        """
        Generate a concise summary of the text
        
        Args:
            text: Input text to summarize
            max_length: Maximum length of the summary
            
        Returns:
            Generated summary
        """
        prompt = f"""
以下のテキストを{max_length}文字以内で要約してください：

{text}
"""
        
        response = await self.model.predict_async(
            prompt,
            temperature=self.config.temperature,
            max_output_tokens=max_length
        )
        
        return response.text[:max_length]
        
    async def extract_entities(self, text: str) -> List[Dict]:
        """
        Extract named entities from the text
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of extracted entities with their types and importance scores
        """
        prompt = f"""
以下のテキストから重要なエンティティ（人物、組織、場所、概念など）を抽出し、
JSONリスト形式で出力してください。各エンティティには重要度（0.0-1.0）を付与してください。

テキスト:
{text}

出力形式:
[
    {{"name": "エンティティ名", "type": "エンティティタイプ", "importance": 0.0-1.0}}
]
"""
        
        response = await self.model.predict_async(
            prompt,
            temperature=self.config.temperature
        )
        
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            return [] 