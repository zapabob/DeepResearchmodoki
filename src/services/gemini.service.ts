import { GoogleGenerativeAI } from '@google/generative-ai';
import { IGeminiService, SearchResult, CrawledData, AnalyzedData } from '../types';

export class GeminiService implements IGeminiService {
  private genAI: GoogleGenerativeAI;
  private model: any;

  constructor(apiKey: string) {
    this.genAI = new GoogleGenerativeAI(apiKey);
    this.model = this.genAI.getGenerativeModel({ model: 'gemini-pro' });
  }

  async search(query: string): Promise<SearchResult> {
    try {
      const result = await this.model.generateContent(query);
      const response = await result.response;
      return {
        results: [
          {
            content: response.text(),
            metadata: {
              source: 'gemini',
              score: 1.0
            }
          }
        ],
        analysis: await this.analyzeResults([response.text()])
      };
    } catch (error) {
      console.error('Search error:', error);
      throw new Error('検索中にエラーが発生しました');
    }
  }

  async deepSearch(query: string): Promise<SearchResult> {
    try {
      const result = await this.model.generateContent({
        contents: [{ role: 'user', parts: [{ text: `Deep search: ${query}` }] }]
      });
      const response = await result.response;
      const results = [response.text()];
      return {
        results: results.map(r => ({
          content: r,
          metadata: {
            source: 'gemini-deep',
            score: 1.0
          }
        })),
        analysis: await this.analyzeResults(results)
      };
    } catch (error) {
      console.error('Deep search error:', error);
      throw new Error('ディープサーチ中にエラーが発生しました');
    }
  }

  async analyzeResults(results: CrawledData[]): Promise<AnalyzedData> {
    try {
      const content = results.map(r => r.content).join('\n\n');
      const result = await this.model.generateContent({
        contents: [
          {
            role: 'user',
            parts: [{ text: `Analyze this content and provide summary, sentiment, keywords, and insights:\n\n${content}` }]
          }
        ]
      });
      const response = await result.response;
      const analysis = JSON.parse(response.text());
      return {
        summary: analysis.summary || '',
        sentiment: analysis.sentiment || 'neutral',
        keywords: analysis.keywords || [],
        insights: analysis.insights || []
      };
    } catch (error) {
      console.error('Analysis error:', error);
      throw new Error('結果の分析中にエラーが発生しました');
    }
  }

  async generateSummary(text: string): Promise<string> {
    try {
      const result = await this.model.generateContent({
        contents: [
          {
            role: 'user',
            parts: [{ text: `Summarize this text:\n\n${text}` }]
          }
        ]
      });
      const response = await result.response;
      return response.text();
    } catch (error) {
      console.error('Summary generation error:', error);
      throw new Error('要約の生成中にエラーが発生しました');
    }
  }
} 