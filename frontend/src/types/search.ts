export interface SearchRequest {
  query: string;
  max_pages?: number;
  hypothesis?: string;
  use_cot?: boolean;
}

export interface SearchResult {
  url: string;
  title: string;
  content: string;
  snippet?: string;
  timestamp: string;
  source?: string;
  analysis?: string;
  metadata?: {
    sentiment?: string;
    source?: string;
    summary?: string;
    [key: string]: any;
  };
}

export interface SearchResponse {
  query: string;
  timestamp: string;
  results: SearchResult[];
  summary: string;
  additional_findings?: Array<{
    summary: string;
    confidence: number;
  }>;
  metadata: {
    max_pages: number;
    use_cot: boolean;
    hypothesis?: string;
    [key: string]: any;
  };
}
