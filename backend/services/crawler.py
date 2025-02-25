from bs4 import BeautifulSoup
import json
from urllib.parse import quote_plus
import time
import re
import os
import httpx
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
import google.generativeai as genai
from langchain.chains import LLMChain
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from datetime import datetime
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, PrivateAttr
from typing import List, Optional, Any
from selenium import webdriver
from selenium.webdriver.edge.service import Service
# EdgeOptionsの正しいインポート
try:
    from selenium.webdriver.edge.options import Options as EdgeOptions
except ImportError:
    # Edge用のOptionsが利用できない場合の対応
    EdgeOptions = None
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from langchain.llms.base import BaseLLM
import chromedriver_autoinstaller
import asyncio

# Firecrawl APIクライアント（存在する場合）
try:
    from firecrawl import FirecrawlApp
except ImportError:
    class FirecrawlApp:
        def __init__(self, *args, **kwargs):
            print("Warning: Firecrawl API client not available", flush=True)
        def search(self, query, max_results=5):
            return []

# Dummy implementation for GoogleGenerativeAI if not available
try:
    from langchain_community.llms import GoogleGenerativeAI
except ImportError:
    class GoogleGenerativeAI:
         def __init__(self, *args, **kwargs):
             print("Warning: Using dummy GoogleGenerativeAI", flush=True)
         def generate_content(self, prompt):
             class DummyResponse:
                 text = "Dummy response for prompt: " + prompt
             return DummyResponse()

class SearchResult(BaseModel):
    url: str = Field(description="The URL of the search result")
    title: str = Field(description="The title of the search result")
    content: str = Field(description="The main content of the search result")
    snippet: Optional[str] = Field(description="A relevant snippet from the content")
    timestamp: str = Field(description="The timestamp of when this result was found")
    source: Optional[str] = Field(description="The source of this information")
    analysis: Optional[str] = Field(description="AI analysis of this result")

class GeminiLLM(BaseLLM):
    """Gemini APIをLangChainで使用するためのカスタムLLMクラス"""
    
    google_api_key: str = None
    logger: Any = None
    model: Any = None
    
    def __init__(self, google_api_key: str):
        """
        GeminiLLMを初期化する
        
        Args:
            google_api_key: Google AI Studio API key
        """
        super().__init__()
        self.google_api_key = google_api_key
        self.logger = logging.getLogger(__name__)
        
        try:
            genai.configure(api_key=self.google_api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            self.logger.info("GeminiLLM initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize GeminiLLM: {str(e)}")
            raise ValueError(f"Failed to initialize Gemini API: {str(e)}")
    
    def _llm_type(self) -> str:
        return "gemini"
    
    def _generate(self, prompts, stop=None, run_manager=None, **kwargs):
        """
        LangChainの抽象メソッドを実装
        
        Args:
            prompts: プロンプトのリスト
            stop: 停止トークンのリスト
            run_manager: 実行マネージャー
            
        Returns:
            生成結果
        """
        from langchain_core.outputs import LLMResult, Generation
        
        generations = []
        for prompt in prompts:
            text = self._call(prompt, stop=stop, **kwargs)
            generations.append([Generation(text=text)])
        
        return LLMResult(generations=generations)
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> str:
        """
        LangChainからの呼び出しに対応するメソッド
        
        Args:
            prompt: プロンプト文字列
            stop: 停止トークンのリスト（Geminiでは未サポート）
            
        Returns:
            生成されたテキスト
        """
        try:
            generation_config = {
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.95),
                "top_k": kwargs.get("top_k", 40),
                "max_output_tokens": kwargs.get("max_tokens", 2048),
            }
            
            response = self.model.generate_content(prompt, generation_config=generation_config)
            
            if not response:
                raise ValueError("Empty response from Gemini API")
                
            response_text = response.text if hasattr(response, 'text') else str(response)
            return response_text
            
        except Exception as e:
            self.logger.error(f"Error in GeminiLLM._call: {str(e)}")
            raise ValueError(f"Error calling Gemini API: {str(e)}")
    
    async def _acall(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> str:
        """
        LangChainからの非同期呼び出しに対応するメソッド
        
        Args:
            prompt: プロンプト文字列
            stop: 停止トークンのリスト（Geminiでは未サポート）
            
        Returns:
            生成されたテキスト
        """
        try:
            generation_config = {
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.95),
                "top_k": kwargs.get("top_k", 40),
                "max_output_tokens": kwargs.get("max_tokens", 2048),
            }
            
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=generation_config
            )
            
            if not response:
                raise ValueError("Empty response from Gemini API")
                
            response_text = response.text if hasattr(response, 'text') else str(response)
            return response_text
            
        except Exception as e:
            self.logger.error(f"Error in GeminiLLM._acall: {str(e)}")
            raise ValueError(f"Error calling Gemini API: {str(e)}")

class CrawlerService:
    def __init__(self):
        """CrawlerServiceの初期化"""
        print("Initializing CrawlerService...")
        
        # 環境変数の読み込み
        load_dotenv()
        
        # ロガーの設定
        self.logger = logging.getLogger(__name__)
            
        # 環境変数の表示（デバッグ用）
        api_key = os.getenv('GOOGLE_AISTUDIO_API_KEY')
        print("Environment variables:")
        print(f"GOOGLE_AISTUDIO_API_KEY: {api_key[:10]}..." if api_key else "Not set")
        
        # HTTPクライアントの初期化
        self.client = httpx.Client(timeout=30.0)
        
        # WebDriverの初期化
        self.driver = None
        self.setup_browser()
        
        # LLMの設定
        self.setup_llm()
            
        # 初期化完了
        print("CrawlerService initialized successfully")
            
    def __del__(self):
        """クリーンアップ"""
        if hasattr(self, 'client'):
            self.client.close()
        if hasattr(self, 'driver') and self.driver is not None:
            self.driver.quit()

    def setup_browser(self):
        """ブラウザの設定を行う"""
        try:
            browser_type = os.getenv("SELENIUM_BROWSER", "chrome").lower()
            self.logger.info(f"Setting up browser: {browser_type}")
            
            if browser_type == "chrome":
                # ChromeDriverの自動インストール
                chromedriver_autoinstaller.install()
                
                # Chromeオプションの設定
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--disable-gpu")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--disable-extensions")
                chrome_options.add_argument("--disable-infobars")
                
                # 日本語対応
                chrome_options.add_argument("--lang=ja")
                chrome_options.add_argument("--accept-lang=ja")
                
                # UserAgentの設定
                chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
                
                try:
                    self.driver = webdriver.Chrome(options=chrome_options)
                    self.logger.info("Chrome WebDriver initialized successfully")
                except Exception as e:
                    self.logger.error(f"Failed to initialize Chrome WebDriver: {str(e)}")
                    self.setup_chrome_fallback()
            elif browser_type == "firefox":
                # ... 既存のFirefoxコード ...
                pass
            else:
                self.logger.warning(f"Unsupported browser type: {browser_type}, falling back to Chrome")
                self.setup_chrome_fallback()
                
        except Exception as e:
            self.logger.error(f"Error setting up browser: {str(e)}")
            self.setup_chrome_fallback()
    
    def setup_chrome_fallback(self):
        """ChromeDriverを使用してブラウザをセットアップする（フォールバック）"""
        try:
            self.logger.info("ChromeDriverを使用してブラウザをセットアップしています...")
            
            # ChromeDriverの自動インストール
            chromedriver_autoinstaller.install()
            
            # Chromeオプションの設定
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--lang=ja')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # WebDriverの初期化
            self.browser = webdriver.Chrome(options=chrome_options)
            self.logger.info("ChromeDriverの初期化に成功しました")
            return True
        except Exception as e:
            self.logger.error(f"ChromeWebDriverの初期化に失敗しました: {str(e)}")
            return False

    def setup_llm(self):
        """LLMの設定"""
        try:
            api_key = os.getenv("GOOGLE_AISTUDIO_API_KEY")
            self.llm = GeminiLLM(google_api_key=api_key)
            
            self.cot_template = """
            あなたは高度な研究アシスタントです。以下のウェブページの内容を分析し、Chain of Thought推論を用いて
            仮説を立て、検証してください。

            ウェブページの内容:
            {content}

            以下のステップで分析を行ってください：

            1. 主要な事実や主張の特定
            2. 潜在的な関連性や因果関係の推論
            3. 仮説の形成
            4. 仮説の検証
            5. 結論の導出

            各ステップでの思考過程を明確に示してください。

            分析結果:
            """

            self.cot_prompt = PromptTemplate(
                template=self.cot_template,
                input_variables=["content"]
            )

            try:
                self.cot_chain = LLMChain(llm=self.llm, prompt=self.cot_prompt)
            except Exception as e:
                logging.getLogger(__name__).warning(f"LLMChain (CoT) initialization failed, using DummyLLMChain for cot_chain: {e}")
                self.cot_chain = DummyLLMChain(llm=self.llm, prompt=self.cot_prompt)
            
            self.search_template = """
            あなたは検索エンジンの結果を分析するAIアシスタントです。
            以下の検索結果を分析し、最も関連性の高い情報を抽出してください。

            検索クエリ: {query}
            検索結果:
            {results}

            以下の形式で回答してください：
            1. 要約（200文字以内）
            2. 主要なポイント（箇条書き）
            3. 関連キーワード（カンマ区切り）
            4. 信頼性評価（高/中/低）

            分析結果:
            """

            self.search_prompt = PromptTemplate(
                template=self.search_template,
                input_variables=["query", "results"]
            )

            try:
                self.search_chain = LLMChain(llm=self.llm, prompt=self.search_prompt)
            except Exception as e:
                logging.getLogger(__name__).warning(f"LLMChain initialization failed, using DummyLLMChain for search_chain: {e}")
                self.search_chain = DummyLLMChain(llm=self.llm, prompt=self.search_prompt)
            
            # テキスト分割の設定
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=4000,
                chunk_overlap=200,
                length_function=len
            )
            
            print("LLM setup completed successfully")
        except Exception as e:
            error_msg = f"LLM setup failed: {str(e)}"
            self.logger.error(error_msg)
            print(error_msg)
            raise Exception(error_msg)

    def _selenium_search(self, query, max_pages=5):
        """Seleniumを使用した検索"""
        if self.driver is None:
            print("WebDriver is not initialized, falling back to alternative search methods")
            return self._fallback_search(query)
        
        results = []
        try:
            # Bingで検索
            self.driver.get(f"https://www.bing.com/search?q={quote_plus(query)}")
            
            # 検索結果を待機
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ol#b_results li.b_algo"))
            )
            
            # 指定されたページ数まで結果を取得
            for page in range(min(max_pages, 10)):  # 最大10ページまで
                # 現在のページの検索結果を解析
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                search_results = soup.select("ol#b_results li.b_algo")
                
                for result in search_results:
                    title_elem = result.select_one("h2 a")
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text()
                    url = title_elem.get('href', '')
                    
                    # URLが有効かチェック
                    if not url.startswith(('http://', 'https://')):
                        continue
                    
                    # 説明文を取得
                    snippet_elem = result.select_one(".b_caption p")
                    snippet = snippet_elem.get_text() if snippet_elem else ""
                    
                    # 結果を追加
                    results.append({
                        'title': title,
                        'url': url,
                        'content': snippet,
                        'metadata': {
                            'source': 'bing',
                            'page': page + 1,
                            'summary': snippet[:100] + "..." if len(snippet) > 100 else snippet
                        }
                    })
                
                # 次のページがあるか確認
                next_page = self.driver.find_elements(By.CSS_SELECTOR, "a.sb_pagN")
                if page < max_pages - 1 and next_page:
                    next_page[0].click()
                    time.sleep(2)  # ページ読み込みを待機
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "ol#b_results li.b_algo"))
                    )
                else:
                    break
            
            return results
        except Exception as e:
            error_msg = f"Selenium search failed: {str(e)}"
            self.logger.error(error_msg)
            print(error_msg)
            return self._fallback_search(query)

    def crawl(self, query, max_pages=5):
        """指定されたクエリでウェブ検索を実行し、結果を返す"""
        self.logger.info(f"Crawling for query: {query}, max_pages: {max_pages}")
        
        try:
            # WebDriverが初期化されていない場合は初期化を試みる
            if self.driver is None:
                browser_initialized = self.setup_browser()
                if not browser_initialized:
                    self.logger.warning("WebDriver initialization failed, using fallback search")
                    return self._fallback_search(query)
            
            # Seleniumを使用した検索
            results = self._selenium_search(query, max_pages)
            
            # 結果が少ない場合はFirecrawl APIを使用
            if len(results) < 3:
                print("Few results from Selenium search, trying Firecrawl API...")
                firecrawl_results = self._firecrawl_search(query, max_pages)
                results.extend(firecrawl_results)
            
            # 重複を除去
            unique_results = []
            urls = set()
            for result in results:
                url = result.get('url')
                if url and url not in urls:
                    urls.add(url)
                    unique_results.append(result)
            
            # 結果が空の場合
            if not unique_results:
                print("No results found, trying fallback search")
                return self._fallback_search(query)
            
            # 感情分析を追加
            for result in unique_results:
                sentiment = self._analyze_sentiment(result.get('content', ''))
                if 'metadata' not in result:
                    result['metadata'] = {}
                result['metadata']['sentiment'] = sentiment
            
            # インサイトを抽出
            insights = self._extract_insights("\n".join([r.get('content', '') for r in unique_results]))
            
            # 結果にタイムスタンプを追加
            timestamp = datetime.now().isoformat()
            for result in unique_results:
                if 'metadata' not in result:
                    result['metadata'] = {}
                result['metadata']['timestamp'] = timestamp
            
            self.logger.info(f"Crawling completed. Found {len(unique_results)} unique results.")
            return unique_results
            
        except Exception as e:
            error_msg = f"Error during crawling: {str(e)}"
            self.logger.error(error_msg)
            print(error_msg)
            
            # エラーが発生した場合は空の結果リストを返す
            print("Error occurred during crawling, returning empty results")
            return []

    def _analyze_sentiment(self, text):
        """テキストの感情分析を行う"""
        if not text:
            return "neutral"
        
        # 簡易的な感情分析
        positive_words = ["良い", "素晴らしい", "優れた", "最高", "成功", "幸せ", "positive", "excellent", "good", "great"]
        negative_words = ["悪い", "最悪", "失敗", "問題", "危険", "不満", "negative", "bad", "worst", "problem"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _extract_insights(self, text):
        """テキストからインサイトを抽出する"""
        if not text:
            return []
        
        # 簡易的なインサイト抽出
        insights = []
        
        # 文を分割
        sentences = re.split(r'[.!?。！？]', text)
        
        # 重要そうな文を選択（長さや特定のキーワードに基づく）
        important_keywords = ["重要", "主要", "特徴", "特性", "結論", "研究", "調査", "分析", "important", "key", "significant"]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 200:  # 適切な長さの文
                # 重要なキーワードを含む文を優先
                if any(keyword in sentence.lower() for keyword in important_keywords):
                    insights.append(sentence)
                # 一定数のインサイトを集めたら終了
                if len(insights) >= 5:
                    break
        
        # インサイトが少ない場合は、長さだけで選択
        if len(insights) < 3:
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 30 and sentence not in insights:
                    insights.append(sentence)
                if len(insights) >= 5:
                    break
        
        return insights

    def _extract_keywords(self, text):
        """テキストからキーワードを抽出する"""
        if not text:
            return []
        
        # 簡易的なキーワード抽出
        # ストップワードを定義
        stop_words = ["の", "に", "は", "を", "た", "が", "で", "て", "と", "し", "れ", "さ", "ある", "いる", "する", "から", "など", "まで", "として", "について", "the", "a", "an", "in", "on", "at", "of", "for", "with", "by", "to", "and", "or", "but"]
        
        # 単語を分割して頻度をカウント
        words = re.findall(r'\w+', text.lower())
        word_count = {}
        
        for word in words:
            if len(word) > 1 and word not in stop_words:
                word_count[word] = word_count.get(word, 0) + 1
        
        # 頻度順にソート
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        
        # 上位10個を返す
        return [word for word, count in sorted_words[:10]]

    def _fallback_search(self, query):
        """フォールバック検索を実行する"""
        try:
            print(f"Executing fallback search for query: {query}")
            
            # Bingでの検索URL
            search_url = f"https://www.bing.com/search?q={quote_plus(query)}&setlang=ja"
            
            # リクエストヘッダー
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
            }
            
            # リクエスト送信
            response = self.client.get(search_url, headers=headers)
            response.raise_for_status()
            
            # HTMLの解析
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 検索結果の抽出
            results = []
            for i, result in enumerate(soup.select("li.b_algo")):
                if i >= 5:  # 最大5件まで
                    break
                    
                # タイトルとURLを取得
                title_elem = result.select_one("h2 a")
                if not title_elem:
                    continue
                    
                title = title_elem.get_text()
                url = title_elem.get("href", "")
                
                # 説明文を取得
                snippet_elem = result.select_one(".b_caption p")
                snippet = snippet_elem.get_text() if snippet_elem else ""
                
                # 結果を追加
                results.append({
                    'title': title,
                    'url': url,
                    'content': snippet,
                    'metadata': {
                        'source': 'fallback',
                        'summary': snippet[:100] + "..." if len(snippet) > 100 else snippet
                    }
                })
            
            if not results:
                print("No results from fallback search")
                return []
                
            return results
            
        except Exception as e:
            error_msg = f"Fallback search failed: {str(e)}"
            self.logger.error(error_msg)
            print(error_msg)
            return []
    
    async def deep_crawl(self, query, max_pages=5):
        """非同期での深層クローリング"""
        # 同期メソッドを呼び出す
        return self.crawl(query, max_pages)
            
    def _create_error_result(self, query, error_message):
        """エラー結果を作成する"""
        return {
            'title': f"Error searching for '{query}'",
            'url': '',
            'content': error_message,
            'metadata': {
                'source': 'error',
                'query': query,
                'timestamp': datetime.now().isoformat()
            }
        }

    async def analyze_webpage(self, url: str) -> SearchResult:
        """指定されたURLのウェブページを分析する"""
        try:
            # ウェブページの取得
            response = self.client.get(url)
            response.raise_for_status()
            
            # HTMLの解析
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # タイトルの取得
            title = soup.title.string if soup.title else "No title"
            
            # メインコンテンツの取得（簡易的な実装）
            main_content = ""
            for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                main_content += tag.get_text() + "\n"
            
            # コンテンツが長すぎる場合は分割
            if len(main_content) > 10000:
                main_content = main_content[:10000] + "..."
            
            # Chain of Thought分析
            analysis = await self.cot_chain.arun(content=main_content)

            return SearchResult(
                url=url,
                title=title,
                content=main_content,
                snippet=main_content[:200] + "..." if len(main_content) > 200 else main_content,
                timestamp=datetime.now().isoformat(),
                source="web",
                analysis=analysis
            )

        except Exception as e:
            error_msg = f"Webpage analysis failed: {str(e)}"
            self.logger.error(error_msg)
            
            return SearchResult(
                url=url,
                title=f"Error analyzing {url}",
                content=error_msg,
                snippet=error_msg,
                timestamp=datetime.now().isoformat(),
                source="error",
                analysis=None
            )
    
    def _firecrawl_search(self, query, count):
        """Firecrawl APIを使用した検索"""
        try:
            api_key = os.getenv("FIRECRAWL_API_KEY")
            if not api_key:
                print("Firecrawl API key not found, skipping Firecrawl search")
                return []
            
            firecrawl = FirecrawlApp(api_key=api_key)
            firecrawl_results = firecrawl.search(query, count=count)
            
            # 結果の形式を統一
            formatted_results = []
            for result in firecrawl_results:
                formatted_result = {
                    'title': result.get('title', 'No Title'),
                    'url': result.get('url', ''),
                    'content': result.get('text', ''),
                    'snippet': result.get('text', '')[:200] if result.get('text') else '',
                    'metadata': {
                        'source': 'firecrawl',
                        'timestamp': datetime.now().isoformat()
                    }
                }
                formatted_results.append(formatted_result)
            
            return formatted_results
        except Exception as e:
            print(f"Firecrawl search error: {str(e)}")
            return []

    def _get_dummy_results(self, query):
        """APIが正常に動作するようにダミーの検索結果を返す"""
        self.logger.info(f"Generating dummy results for query: {query}")
        
        dummy_results = [
            {
                "title": f"Dummy result 1 for '{query}'",
                "url": "https://example.com/dummy1",
                "content": f"これは'{query}'に関するダミーの検索結果です。実際のクローラーが正常に動作していない場合に表示されます。",
                "metadata": {
                    "summary": f"'{query}'に関するダミーの検索結果。システム機能のテスト用です。",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "source_type": "dummy"
                }
            },
            {
                "title": f"Dummy result 2 for '{query}'",
                "url": "https://example.com/dummy2",
                "content": f"これは'{query}'に関する2つ目のダミー結果です。ブラウザドライバーの初期化に問題がある場合でもAPIテストが可能です。",
                "metadata": {
                    "summary": f"'{query}'に関する2つ目のダミー結果。ブラウザドライバーの問題をバイパスするために提供されています。",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "source_type": "dummy"
                }
            },
            {
                "title": f"Error searching for '{query}'",
                "url": "",
                "content": f"ブラウザドライバーが正しく初期化されていないため、実際の検索結果を取得できませんでした。環境設定を確認してください。",
                "metadata": {
                    "summary": "検索エンジンへのアクセスに失敗しました。",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "source_type": "error"
                }
            }
        ]
        
        return dummy_results

class DummyLLMChain:
    def __init__(self, llm, prompt):
        self.llm = llm
        self.prompt = prompt
    
    def invoke(self, inputs):
        return {"text": f"Dummy response for inputs: {inputs}"}
    
    async def arun(self, **kwargs):
        input_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        return f"Dummy async response for inputs: {input_str}" 