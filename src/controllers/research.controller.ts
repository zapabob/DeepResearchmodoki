import { GeminiService } from '../services/gemini.service';
import { CacheService } from '../services/cache.service';
import { SearchResult, AnalyzedData } from '../types';

export class ResearchController {
  constructor(
    private geminiService: GeminiService,
    private cacheService: CacheService
  ) {}

  async handleResearch(req: any, res: any) {
    try {
      const { query } = req.body;
      if (!query) {
        return res.status(400).json({ error: '検索クエリが必要です' });
      }

      const cachedResults = await this.cacheService.get(query);
      if (cachedResults) {
        return res.json(JSON.parse(cachedResults));
      }

      const results = await this.geminiService.search(query);
      await this.cacheService.set(query, JSON.stringify(results));
      return res.json(results);
    } catch (error) {
      console.error('Research error:', error);
      return res.status(500).json({ error: '検索中にエラーが発生しました' });
    }
  }

  async handleDeepResearch(req: any, res: any) {
    try {
      const { query } = req.body;
      if (!query) {
        return res.status(400).json({ error: '検索クエリが必要です' });
      }

      const results = await this.geminiService.deepSearch(query);
      const analysis: AnalyzedData = await this.geminiService.analyzeResults(results);
      
      return res.json({ results, analysis });
    } catch (error) {
      console.error('Deep research error:', error);
      return res.status(500).json({ error: 'ディープリサーチ中にエラーが発生しました' });
    }
  }

  async getResearchStatus(req: any, res: any) {
    try {
      const { id } = req.params;
      const status = await this.cacheService.get(`status:${id}`);
      return res.json({ status: status || 'not_found' });
    } catch (error) {
      console.error('Status check error:', error);
      return res.status(500).json({ error: 'ステータス確認中にエラーが発生しました' });
    }
  }

  async getResearchResults(req: any, res: any) {
    try {
      const { id } = req.params;
      const results = await this.cacheService.get(`results:${id}`);
      if (!results) {
        return res.status(404).json({ error: '結果が見つかりません' });
      }
      return res.json(JSON.parse(results));
    } catch (error) {
      console.error('Results retrieval error:', error);
      return res.status(500).json({ error: '結果の取得中にエラーが発生しました' });
    }
  }
} 