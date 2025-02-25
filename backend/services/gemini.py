import os
import logging
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from langchain.llms.base import BaseLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

class GeminiService:
    """Gemini APIを使用したAI分析サービス"""
    
    def __init__(self):
        """GeminiServiceを初期化する"""
        self.logger = logging.getLogger(__name__)
        
        # APIキーの取得
        self.api_key = os.getenv("GOOGLE_AISTUDIO_API_KEY")
        if not self.api_key:
            self.logger.error("GOOGLE_AISTUDIO_API_KEYが設定されていません")
            raise ValueError("GOOGLE_AISTUDIO_API_KEY environment variable is required")
            
        self.logger.info(f"Initializing GeminiService with Google AI Studio API key: {self.api_key[:10]}...")
        
        # Gemini LLMの初期化
        try:
            from backend.services.crawler import GeminiLLM
            self.llm = GeminiLLM(google_api_key=self.api_key)
            
            # 分析用プロンプトテンプレートの設定
            self.analysis_prompt = PromptTemplate(
                input_variables=["results"],
                template="""以下の検索結果を詳細に分析し、重要な洞察、パターン、関連性を特定してください。
                
検索結果:
{results}

分析結果を以下の形式で提供してください:
1. 要約: 検索結果全体の簡潔で具体的な要約（200-300文字程度）
2. 主要な洞察: 検索結果から得られる重要な洞察のリスト（少なくとも3つ）
   - 各洞察は具体的で、検索結果に基づいた事実を含むこと
   - 単なる「情報がない」という否定的な洞察ではなく、実際に得られた情報に基づく洞察を提供すること
3. パターンと関連性: 検索結果間の関連性やパターン（少なくとも2つ）
   - 複数の情報源間で一貫して現れるテーマや概念
   - 矛盾する情報がある場合はそれも指摘
4. 信頼性評価: 情報源の信頼性と情報の質の評価
   - 学術的情報源、専門家の意見、一次資料などの信頼性の高い情報源を特定
   - 情報の新しさや関連性も評価
5. 追加調査が必要な領域: さらなる調査が必要な領域や質問（少なくとも2つ）
   - 検索結果で十分にカバーされていない重要な側面
   - 追加情報が役立つ可能性のある具体的な質問

重要: 「情報がない」「役立たない」などの否定的な分析は避け、実際に得られた情報に基づいて建設的な分析を提供してください。検索結果が限られている場合でも、その中から最大限の洞察を引き出してください。

日本語で回答してください。"""
            )
            
            # 分析チェーンの設定
            self.analysis_chain = LLMChain(llm=self.llm, prompt=self.analysis_prompt)
            self.logger.info("GeminiService initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize GeminiService: {str(e)}")
            raise
    
    async def analyze(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """検索結果を分析する"""
        try:
            # 結果をテキスト形式に変換
            results_text = ""
            if isinstance(results, list):
                results_text = "\n\n".join([
                    f"タイトル: {result.get('title', 'No Title')}\n"
                    f"URL: {result.get('url', 'No URL')}\n"
                    f"内容: {result.get('content', 'No Content')}\n"
                    for result in results
                ])
            elif isinstance(results, str):
                results_text = results
            else:
                self.logger.warning(f"Unexpected results type: {type(results)}")
                results_text = str(results)
            
            # 分析の実行
            analysis_result = await self.analysis_chain.arun(results=results_text)
            
            # 結果の解析
            lines = analysis_result.split("\n")
            summary = ""
            insights = []
            patterns = []
            reliability = ""
            further_research = []
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if "要約:" in line or "1." in line and "要約" in line:
                    current_section = "summary"
                    summary = line.split(":", 1)[1].strip() if ":" in line else ""
                elif "主要な洞察:" in line or "2." in line and "洞察" in line:
                    current_section = "insights"
                elif "パターンと関連性:" in line or "3." in line and "パターン" in line:
                    current_section = "patterns"
                elif "信頼性評価:" in line or "4." in line and "信頼性" in line:
                    current_section = "reliability"
                elif "追加調査:" in line or "5." in line and "調査" in line:
                    current_section = "further_research"
                elif current_section == "summary" and not summary:
                    summary = line
                elif current_section == "insights":
                    if line.startswith("-") or line.startswith("*"):
                        insights.append(line[1:].strip())
                    elif line and not any(line.startswith(x) for x in ["1.", "2.", "3.", "4.", "5."]):
                        insights.append(line)
                elif current_section == "patterns":
                    if line.startswith("-") or line.startswith("*"):
                        patterns.append(line[1:].strip())
                    elif line and not any(line.startswith(x) for x in ["1.", "2.", "3.", "4.", "5."]):
                        patterns.append(line)
                elif current_section == "reliability":
                    if not reliability:
                        reliability = line
                elif current_section == "further_research":
                    if line.startswith("-") or line.startswith("*"):
                        further_research.append(line[1:].strip())
                    elif line and not any(line.startswith(x) for x in ["1.", "2.", "3.", "4.", "5."]):
                        further_research.append(line)
            
            return {
                "summary": summary,
                "insights": insights,
                "patterns": patterns,
                "reliability": reliability,
                "further_research": further_research,
                "raw_analysis": analysis_result
            }
            
        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}")
        return {
                "error": f"分析中にエラーが発生しました: {str(e)}",
                "summary": "分析できませんでした",
                "insights": [],
                "patterns": [],
                "reliability": "評価できません",
                "further_research": []
        } 
        
    async def generate_text(self, prompt: str) -> str:
        """指定されたプロンプトに基づいてテキストを生成する"""
        try:
            self.logger.info(f"Generating text with prompt: {prompt[:100]}...")
            
            # Gemini APIの設定
            genai.configure(api_key=self.api_key)
            
            # モデルの選択
            model = genai.GenerativeModel('gemini-pro')
            
            # テキスト生成
            response = model.generate_content(prompt)
            
            # レスポンスからテキストを抽出
            if hasattr(response, 'text'):
                return response.text
            elif hasattr(response, 'parts'):
                return ''.join([part.text for part in response.parts])
            else:
                return str(response)
                
        except Exception as e:
            self.logger.error(f"Text generation failed: {str(e)}")
            return f"テキスト生成中にエラーが発生しました: {str(e)}" 