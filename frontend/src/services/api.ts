import axios from 'axios';
import { SearchRequest, SearchResponse } from '../types/search';
import { ResearchRequest, ResearchResponse } from '../types/research';

// Next.jsの環境変数を使用
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

// Axiosインスタンスの設定
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// レスポンスインターセプター
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error);
    if (error.response) {
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
    } else if (error.request) {
      console.error('Request error:', error.request);
    }
    return Promise.reject(error);
  }
);

export const searchApi = {
  search: async (request: SearchRequest): Promise<SearchResponse> => {
    try {
      console.log('Sending search request to:', `${API_BASE_URL}/api/search`);
      console.log('Request data:', request);
      const response = await api.post('/api/search', request);
      console.log('Search response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Search error:', error);
      throw error;
    }
  }
};

export const researchApi = {
  /**
   * 深層リサーチを実行します
   */
  conductResearch: async (request: ResearchRequest): Promise<ResearchResponse> => {
    const response = await api.post('/api/cot_deepresearch', request);
    return response.data;
  },

  /**
   * 簡易検索を実行します
   */
  conductSearch: async (request: SearchRequest): Promise<SearchResponse> => {
    const response = await api.post<SearchResponse>('/api/search', request);
    return response.data;
  },

  /**
   * 指定されたIDのリサーチ結果を取得します
   */
  getResearchResult: async (id: string): Promise<ResearchResponse> => {
    const response = await api.get<ResearchResponse>(`/api/research/${id}`);
    return response.data;
  },

  /**
   * サーバーの健康状態を確認します
   */
  checkHealth: async (): Promise<{ status: string }> => {
    const response = await api.get<{ status: string }>('/api/health');
    return response.data;
  },

  llmSummary: async (request: ResearchRequest): Promise<any> => {
    const response = await api.post('/api/llm_summary', request);
    return response.data;
  }
};

export default { searchApi, researchApi };