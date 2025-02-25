import { SimulationNodeDatum, SimulationLinkDatum } from 'd3';

// リサーチのフィルター
export interface ResearchFilters {
  academic: boolean;
  news: boolean;
  blog: boolean;
  social: boolean;
}

// リサーチの状態
export interface ResearchStatus {
  id: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  progress: number;
  startedAt: string;
  completedAt?: string;
  error?: string;
}

// リサーチの結果
export interface ResearchResults {
  query: string;
  filters: ResearchFilters;
  summary: string;
  keyInsights: string[];
  topics: Array<{
    name: string;
    relevance: number;
    keywords: string[];
  }>;
  graphData: {
    nodes: Array<{
      id: string;
      label: string;
      type: 'topic' | 'entity' | 'source';
      properties: Record<string, any>;
    }>;
    edges: Array<{
      source: string;
      target: string;
      type: string;
      properties: Record<string, any>;
    }>;
  };
  sentiment: {
    score: number;
    label: 'positive' | 'neutral' | 'negative';
  };
  sources: Array<{
    url: string;
    title: string;
    snippet: string;
    relevance: number;
  }>;
  metadata: {
    totalSources: number;
    processingTime: number;
    timestamp: string;
  };
}

// APIレスポンス型
export interface ApiResponse<T> {
  data: T;
  status: 'success';
  timestamp: string;
}

export interface ApiError {
  error: {
    message: string;
    code?: string;
    details?: any;
  };
  status: 'error';
  timestamp: string;
}

export interface ResearchTask {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  result?: any;
  error?: string;
}

export interface Entity {
  name: string;
  type: string;
  relevance: number;
  mentions: number;
  context: string[];
}

export interface GraphData {
  nodes: Array<{
    id: string;
    label: string;
    type: string;
    weight: number;
  }>;
  links: Array<{
    source: string;
    target: string;
    type: string;
    weight: number;
  }>;
}

export interface AnalysisResult {
  summary: string;
  keywords: string[];
  entities: Entity[];
  insights: string[];
  relationships: Array<{
    source: string;
    target: string;
    type: string;
  }>;
  graphData?: GraphData;
  metadata?: {
    totalPages: number;
    processedEntities: number;
    startTime: Date;
    endTime: Date;
  };
}

export interface ResearchResult {
  query: string;
  crawlResults: Array<{
    title: string;
    url: string;
    content: string;
    metadata?: {
      keywords: string[];
      summary: string;
    };
  }>;
  analysis: {
    summary: string;
    sentiment: string;
    keywords: string[];
    entities: Entity[];
    insights: string[];
    relationships: Array<{
      source: string;
      target: string;
      type: string;
    }>;
  };
  insights: {
    summary: string;
    keyFindings: string[];
    recommendations: string[];
  };
  graphData: GraphData;
  metadata: {
    totalPages: number;
    processedEntities: number;
    startTime: Date;
    endTime: Date;
  };
}

export interface ResearchRequest {
  query: string;
  max_pages?: number;
  language?: string;
  deep_search?: boolean;
  filters?: string[];
}

export interface ResearchFormProps {
  onSubmit: (request: ResearchRequest) => Promise<void>;
  loading: boolean;
  disabled?: boolean;
}

export interface GraphNode extends SimulationNodeDatum {
  id: string;
  label: string;
  type: string;
  weight?: number;
}

export interface GraphLink extends SimulationLinkDatum<GraphNode> {
  source: string;
  target: string;
  type: string;
  weight?: number;
}

export interface Relationship {
  source: string;
  target: string;
  type: string;
}
