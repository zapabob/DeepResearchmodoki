import os
import logging
from typing import List, Dict, Any

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

class OpenAIService:
    """OpenAI API based analysis service"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.llm = ChatOpenAI(openai_api_key=self.api_key, model_name=model)

        self.analysis_prompt = PromptTemplate(
            input_variables=["results"],
            template="""以下の検索結果を詳細に分析してください:\n\n{results}\n"""
        )
        self.analysis_chain = LLMChain(llm=self.llm, prompt=self.analysis_prompt)

    async def analyze(self, results: List[Dict[str, Any]] | str) -> Dict[str, Any]:
        try:
            if isinstance(results, list):
                text = "\n\n".join([
                    f"タイトル: {r.get('title','')}\nURL: {r.get('url','')}\n内容: {r.get('content','')}"
                    for r in results
                ])
            else:
                text = str(results)

            analysis_result = await self.analysis_chain.arun(results=text)
            return {"raw_analysis": analysis_result}
        except Exception as e:
            self.logger.error(f"OpenAI analysis failed: {e}")
            return {"error": str(e)}
