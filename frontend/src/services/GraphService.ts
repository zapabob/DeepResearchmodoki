import { Driver, auth } from 'neo4j-driver';
import neo4j from 'neo4j-driver';

export class GraphService {
  private driver: Driver;

  constructor(uri: string, username: string, password: string) {
    this.driver = neo4j.driver(uri, auth.basic(username, password));
  }

  async createGraph(analysisResult: any) {
    try {
      // エンティティをノードに変換
      const nodes = (analysisResult.metadata.entities || []).map((entity: any) => ({
        id: entity.name,
        label: entity.name,
        type: entity.type || 'unknown',
        weight: entity.relevance || 1
      }));

      // 関係をリンクに変換
      const links = (analysisResult.metadata.relationships || []).map((rel: any) => ({
        source: rel.source,
        target: rel.target,
        type: rel.type || 'default',
        weight: rel.weight || 1
      }));

      // キーワードをノードとして追加
      const keywordNodes = (analysisResult.metadata.keywords || []).map((keyword: string) => ({
        id: keyword,
        label: keyword,
        type: 'keyword',
        weight: 0.8
      }));

      // キーワード間の関係を追加
      const keywordLinks = [];
      for (let i = 0; i < keywordNodes.length; i++) {
        for (let j = i + 1; j < keywordNodes.length; j++) {
          keywordLinks.push({
            source: keywordNodes[i].id,
            target: keywordNodes[j].id,
            type: 'related',
            weight: 0.5
          });
        }
      }

      // インサイトをノードとして追加
      const insightNodes = (analysisResult.metadata.insights || []).map((insight: string) => ({
        id: `insight_${insight.substring(0, 30)}`,
        label: insight,
        type: 'insight',
        weight: 0.9
      }));

      // インサイトとキーワードの関係を追加
      const insightLinks = insightNodes.flatMap((insight: any) => {
        const relatedKeywords = keywordNodes.filter((keyword: any) => 
          insight.label.toLowerCase().includes(keyword.label.toLowerCase())
        );
        return relatedKeywords.map((keyword: any) => ({
          source: insight.id,
          target: keyword.id,
          type: 'contains',
          weight: 0.6
        }));
      });

      // すべてのノードとリンクを結合
      const allNodes = [...nodes, ...keywordNodes, ...insightNodes];
      const allLinks = [...links, ...keywordLinks, ...insightLinks];

      // Neo4jにデータを保存
      const session = this.driver.session();
      try {
        await session.run(
          `MATCH (n) DETACH DELETE n`
        );

        for (const node of allNodes) {
          await session.run(
            `CREATE (n:Node {
              id: $id,
              label: $label,
              type: $type,
              weight: $weight
            })`,
            node
          );
        }

        for (const link of allLinks) {
          await session.run(
            `MATCH (source:Node {id: $source})
             MATCH (target:Node {id: $target})
             CREATE (source)-[r:RELATES_TO {
               type: $type,
               weight: $weight
             }]->(target)`,
            link
          );
        }
      } finally {
        await session.close();
      }

      return {
        nodes: allNodes,
        links: allLinks
      };
    } catch (error) {
      console.error('Error creating graph:', error);
      return {
        nodes: [],
        links: []
      };
    }
  }

  async close() {
    await this.driver.close();
  }
} 