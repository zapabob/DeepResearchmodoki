export interface ConfigOptions {
  geminiApiKey: string;
  crawlerApiKey: string;
  neo4j: {
    uri: string;
    username: string;
    password: string;
  };
}

export class ConfigService {
  private static instance: ConfigService;
  private config: ConfigOptions;

  private constructor() {
    this.config = {
      geminiApiKey: process.env.GEMINI_API_KEY || '',
      crawlerApiKey: process.env.CRAWLER_API_KEY || '',
      neo4j: {
        uri: process.env.NEO4J_URI || 'bolt://localhost:7687',
        username: process.env.NEO4J_USERNAME || 'neo4j',
        password: process.env.NEO4J_PASSWORD || ''
      }
    };

    this.validateConfig();
  }

  static getInstance(): ConfigService {
    if (!ConfigService.instance) {
      ConfigService.instance = new ConfigService();
    }
    return ConfigService.instance;
  }

  private validateConfig(): void {
    if (!this.config.geminiApiKey) {
      throw new Error('GEMINI_API_KEY is required');
    }
    if (!this.config.crawlerApiKey) {
      throw new Error('CRAWLER_API_KEY is required');
    }
    if (!this.config.neo4j.password) {
      throw new Error('NEO4J_PASSWORD is required');
    }
  }

  getConfig(): ConfigOptions {
    return this.config;
  }

  getGeminiApiKey(): string {
    return this.config.geminiApiKey;
  }

  getCrawlerApiKey(): string {
    return this.config.crawlerApiKey;
  }

  getNeo4jConfig(): ConfigOptions['neo4j'] {
    return this.config.neo4j;
  }
}

export const config = ConfigService.getInstance();
