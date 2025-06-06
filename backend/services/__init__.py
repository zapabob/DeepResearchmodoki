from .orchestrator import OrchestratorService
from .gemini import GeminiService
from .openai_service import OpenAIService
import os
from .graph import GraphService
from .crawler import CrawlerService
from .cot_deepresearch import CoTDeepResearchService

def get_ai_service():
    provider = os.getenv("AI_PROVIDER", "gemini").lower()
    if provider == "openai":
        return OpenAIService()
    return GeminiService()

__all__ = [
    'OrchestratorService', 'GeminiService', 'OpenAIService',
    'GraphService', 'CrawlerService', 'CoTDeepResearchService', 'get_ai_service'
]
