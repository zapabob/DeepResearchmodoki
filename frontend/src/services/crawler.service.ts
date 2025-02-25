import axios from 'axios';

export interface CrawlOptions {
  url: string;
  depth?: number;
  filterDomain?: string[];
  maxPages?: number;
}

export interface CrawlResult {
  url: string;
  title: string;
  content: string;
  metadata: {
    lastModified?: string;
    author?: string;
    keywords?: string[];
  };
  links: string[];
}

export class CrawlerService {
  private apiKey: string;
  private baseUrl: string;

  constructor(apiKey: string, baseUrl: string = 'https://api.firecrawll.com/v1') {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl;
  }

  async crawlWebsite(options: CrawlOptions): Promise<CrawlResult[]> {
    try {
      const response = await axios.post(
        `${this.baseUrl}/crawl`,
        {
          ...options,
          filterContent: true, // HTMLタグの除去
          extractMetadata: true // メタデータの抽出
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );

      return response.data.results;
    } catch (error) {
      console.error('Crawling failed:', error);
      throw error;
    }
  }

  async extractMainContent(html: string): Promise<string> {
    try {
      const response = await axios.post(
        `${this.baseUrl}/extract`,
        {
          html,
          options: {
            removeAds: true,
            removeNavigation: true,
            removeFooter: true
          }
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );

      return response.data.content;
    } catch (error) {
      console.error('Content extraction failed:', error);
      throw error;
    }
  }

  async searchWebsites(query: string, options: {
    domains?: string[];
    dateRange?: {
      start: string;
      end: string;
    };
    language?: string;
    maxResults?: number;
  }): Promise<CrawlResult[]> {
    try {
      const response = await axios.post(
        `${this.baseUrl}/search`,
        {
          query,
          ...options
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );

      return response.data.results;
    } catch (error) {
      console.error('Search failed:', error);
      throw error;
    }
  }

  async monitorWebsite(url: string, options: {
    frequency: 'hourly' | 'daily' | 'weekly';
    checkForChanges: boolean;
    notifyOnChange?: boolean;
  }): Promise<{ monitoringId: string }> {
    try {
      const response = await axios.post(
        `${this.baseUrl}/monitor`,
        {
          url,
          ...options
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          }
        }
      );

      return { monitoringId: response.data.monitoringId };
    } catch (error) {
      console.error('Monitoring setup failed:', error);
      throw error;
    }
  }
}
