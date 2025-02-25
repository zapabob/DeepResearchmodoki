import { SearchResult } from './search';

export interface Node {
  id: string;
  label: string;
  type: string;
  properties: Record<string, any>;
}

export interface Edge {
  source: string;
  target: string;
  type: string;
  properties: Record<string, any>;
  weight: number;
}

export interface Graph {
  nodes: Node[];
  edges: Edge[];
  metadata: Record<string, any>;
}

export interface Analysis {
  query: string;
  summary: string;
  keywords: string[];
  sentiment: string;
  insights: string[];
  graph?: Graph;
  metadata: Record<string, any>;
}

export interface ResearchRequest {
  query: string;
  max_pages?: number;
  language?: string;
}

export interface ResearchResult extends Omit<SearchResult, 'content'> {
  fullContent?: string;
  analyzed?: boolean;
  content: string;
  metadata?: {
    source: string;
    summary: string;
    [key: string]: any;
  };
}

export interface ResearchResponse {
  results: SearchResult[];
  analysis: {
    summary: string;
    insights: string[];
    patterns: string[];
    reliability: string;
    further_research: string[];
    raw_analysis?: string;
  };
  metadata?: {
    query: string;
    max_pages?: number;
    depth?: number;
    language?: string;
    timestamp: string;
    [key: string]: any;
  };
} 