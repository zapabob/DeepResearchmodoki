import { CrawlerService, CrawlResult } from './crawler.service';
import { GeminiService } from './gemini.service';
import { GraphService, Entity, Relationship } from './graph.service';
import { LangChain } from './langchain.service';

export interface ResearchTask {
  query: string;
  domains?: string[];
  maxDepth?: number;
  maxPages?: number;
  language?: string;
}

export interface AnalysisResult {
  entities: Entity[];
  relationships: Relationship[];
  summary: string;
  insights: string[];
}

export class OrchestratorService {
  private crawler: CrawlerService;
  private gemini: GeminiService;
  private graph: GraphService;
  private chain: LangChain;

  constructor(
    crawlerApiKey: string,
    geminiApiKey: string,
    neo4jUri: string,
    neo4jUsername: string,
    neo4jPassword: string
  ) {
    this.crawler = new CrawlerService(crawlerApiKey);
    this.gemini = new GeminiService(geminiApiKey);
    this.graph = new GraphService(neo4jUri, neo4jUsername, neo4jPassword);
    this.chain = new LangChain();

    this.setupWorkflow();
  }

  private setupWorkflow(): void {
    this.chain
      .addStep('crawl', async (task: ResearchTask) => {
        return await this.crawler.crawlWebsite({
          url: task.query,
          depth: task.maxDepth,
          filterDomain: task.domains,
          maxPages: task.maxPages
        });
      })
      .addStep('analyze', async (results: CrawlResult[]) => {
        const analysisPromises = results.map(async (result) => {
          const [textAnalysis, entities] = await Promise.all([
            this.gemini.analyzeText(result.content),
            this.gemini.extractEntities(result.content)
          ]);

          return {
            url: result.url,
            analysis: textAnalysis,
            entities
          };
        });

        return await Promise.all(analysisPromises);
      })
      .addStep('buildGraph', async (analysisResults: any[]) => {
        const entities = new Map<string, Entity>();
        const relationships: Relationship[] = [];

        // エンティティの抽出と重複の除去
        analysisResults.forEach(result => {
          result.entities.forEach((entity: { name: string; type: string; relevance: number }) => {
            if (!entities.has(entity.name)) {
              entities.set(entity.name, {
                id: entity.name,
                label: entity.name,
                type: entity.type,
                properties: {
                  relevance: entity.relevance
                }
              });
            }
          });
        });

        // エンティティ間の関係性の構築
        analysisResults.forEach(result => {
          const sourceEntities = result.entities;
          sourceEntities.forEach((source: { name: string; type: string; relevance: number }, i: number) => {
            sourceEntities.slice(i + 1).forEach((target: { name: string; type: string; relevance: number }) => {
              relationships.push({
                source: source.name,
                target: target.name,
                type: 'RELATED_TO',
                properties: {
                  source_url: result.url,
                  confidence: (source.relevance + target.relevance) / 2
                }
              });
            });
          });
        });

        // グラフDBへの保存
        for (const entity of Array.from(entities.values())) {
          await this.graph.addEntity(entity);
        }

        for (const relationship of relationships) {
          await this.graph.addRelationship(relationship);
        }

        return {
          entities: Array.from(entities.values()),
          relationships
        };
      });
  }

  async executeResearch(task: ResearchTask): Promise<AnalysisResult> {
    try {
      const result = await this.chain.execute(task);
      const graphData = await this.graph.getGraphData();

      // 結果の要約生成
      const summaryPrompt = `
        以下の分析結果に基づいて、主要な発見と洞察を300文字以内で要約してください：
        - エンティティ数: ${graphData.nodes.length}
        - 関係性の数: ${graphData.links.length}
        - 主要エンティティ: ${graphData.nodes.slice(0, 5).map(n => (n as any).id).join(', ')}
      `;

      const summary = await this.gemini.analyzeText(summaryPrompt);

      return {
        entities: result.entities,
        relationships: result.relationships,
        summary: summary.summary,
        insights: summary.keywords
      };
    } catch (error) {
      console.error('Research execution failed:', error);
      throw error;
    }
  }

  async close(): Promise<void> {
    await this.graph.close();
  }
}
