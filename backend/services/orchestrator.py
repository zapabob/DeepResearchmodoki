from datetime import datetime

class OrchestratorService:
    def __init__(self):
        pass

    def execute_research(self, task):
        if not task or not isinstance(task, dict):
            raise ValueError("task must be a non-empty dictionary")
            
        if 'query' not in task or not task['query']:
            raise ValueError("task must contain a non-empty 'query' field")
            
        try:
            print(f"Starting research for query: {task['query']}")
            
            # クローリング
            print("Starting crawling...")
            crawl_results = self.crawler_service.crawl(task['query'])
            if not crawl_results:
                print("Warning: No crawl results found")
                crawl_results = []
            print(f"Crawling completed. Found {len(crawl_results)} results")
            
            # テキスト分析
            print("Starting text analysis...")
            analysis_result = self.gemini_service.analyze(crawl_results)
            if not analysis_result:
                raise Exception("Text analysis failed: No results returned")
            print("Text analysis completed")
            
            # グラフ生成
            print("Generating graph...")
            graph_data = self.graph_service.generate_graph(analysis_result)
            if not graph_data:
                print("Warning: No graph data generated")
                graph_data = {}
            print("Graph generation completed")
            
            # 結果の集約
            result = {
                'query': task['query'],
                'crawlResults': crawl_results,
                'analysis': {
                    'summary': analysis_result.get('summary', ''),
                    'sentiment': analysis_result.get('sentiment', ''),
                    'keywords': analysis_result.get('keywords', []),
                    'entities': analysis_result.get('entities', []),
                    'insights': analysis_result.get('insights', []),
                    'relationships': analysis_result.get('relationships', [])
                },
                'graphData': graph_data,
                'insights': {
                    'summary': analysis_result.get('summary', ''),
                    'keyFindings': analysis_result.get('insights', []),
                    'recommendations': analysis_result.get('recommendations', [])
                },
                'metadata': {
                    'totalPages': len(crawl_results),
                    'processedEntities': len(analysis_result.get('entities', [])),
                    'startTime': analysis_result.get('startTime') if isinstance(analysis_result.get('startTime'), str) else (analysis_result.get('startTime').isoformat() if analysis_result.get('startTime') else datetime.now().isoformat()),
                    'endTime': analysis_result.get('endTime') if isinstance(analysis_result.get('endTime'), str) else (analysis_result.get('endTime').isoformat() if analysis_result.get('endTime') else datetime.now().isoformat())
                }
            }
            
            # crawlResults の各項目を、必要な情報だけに絞り込む (例)
            simplified_crawl_results = []
            for item in crawl_results:
                simplified_item = {
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'snippet': item.get('snippet', ''), # firecrawlの'text'を想定
                    # 必要に応じて他のフィールドも追加
                }
                simplified_crawl_results.append(simplified_item)

            result['crawlResults'] = simplified_crawl_results # 上書き

            print("Research execution completed successfully")
            return result
            
        except Exception as e:
            error_msg = f"研究の実行中にエラーが発生しました: {str(e)}"
            print(f"Error during research execution: {error_msg}")
            print(f"Error type: {type(e).__name__}")
            raise Exception(error_msg) 