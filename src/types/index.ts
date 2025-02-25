export interface CrawledData {
  content: string;
  metadata: {
    source?: string;
    rank?: number;
    score?: number;
  };
}

export interface AnalyzedData {
  summary: string;
  sentiment: string;
  keywords: string[];
  insights: string[];
}

export interface SearchResult {
  results: CrawledData[];
  analysis: AnalyzedData;
}

export interface IGeminiService {
  search(query: string): Promise<SearchResult>;
  deepSearch(query: string): Promise<SearchResult>;
  analyzeResults(results: CrawledData[]): Promise<AnalyzedData>;
  generateSummary(text: string): Promise<string>;
} 