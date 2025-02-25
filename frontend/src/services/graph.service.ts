import neo4j, { Driver, Session } from 'neo4j-driver';
import { SimulationNodeDatum, SimulationLinkDatum } from 'd3-force';

export interface Entity {
  id: string;
  label: string;
  type: string;
  properties: Record<string, any>;
}

export interface Relationship {
  source: string;
  target: string;
  type: string;
  properties: Record<string, any>;
}

export interface GraphData {
  nodes: SimulationNodeDatum[];
  links: SimulationLinkDatum<SimulationNodeDatum>[];
}

interface CustomNode extends SimulationNodeDatum {
  id: string;
  [key: string]: any;
}

export class GraphService {
  private driver: Driver;
  private session: Session;

  constructor(uri: string, username: string, password: string) {
    this.driver = neo4j.driver(uri, neo4j.auth.basic(username, password));
    this.session = this.driver.session();
  }

  async addEntity(entity: Entity): Promise<void> {
    const query = `
      CREATE (n:${entity.type} {
        id: $id,
        label: $label,
        ...properties
      })
    `;

    try {
      await this.session.run(query, {
        id: entity.id,
        label: entity.label,
        properties: entity.properties
      });
    } catch (error) {
      console.error('Failed to add entity:', error);
      throw error;
    }
  }

  async addRelationship(relationship: Relationship): Promise<void> {
    const query = `
      MATCH (source), (target)
      WHERE source.id = $sourceId AND target.id = $targetId
      CREATE (source)-[r:${relationship.type} $properties]->(target)
    `;

    try {
      await this.session.run(query, {
        sourceId: relationship.source,
        targetId: relationship.target,
        properties: relationship.properties
      });
    } catch (error) {
      console.error('Failed to add relationship:', error);
      throw error;
    }
  }

  async getGraphData(): Promise<GraphData> {
    const query = `
      MATCH (n)
      OPTIONAL MATCH (n)-[r]->(m)
      RETURN n, r, m
    `;

    try {
      const result = await this.session.run(query);
      const nodes = new Map<string, SimulationNodeDatum>();
      const links: SimulationLinkDatum<SimulationNodeDatum>[] = [];

      result.records.forEach(record => {
        const source = record.get('n');
        const relationship = record.get('r');
        const target = record.get('m');

        if (!nodes.has(source.properties.id)) {
          nodes.set(source.properties.id, {
            ...source.properties,
            id: source.properties.id
          });
        }

        if (target && !nodes.has(target.properties.id)) {
          nodes.set(target.properties.id, {
            ...target.properties,
            id: target.properties.id
          });
        }

        if (relationship && target) {
          links.push({
            source: nodes.get(source.properties.id)!,
            target: nodes.get(target.properties.id)!,
            ...relationship.properties
          });
        }
      });

      return {
        nodes: Array.from(nodes.values()),
        links
      };
    } catch (error) {
      console.error('Failed to get graph data:', error);
      throw error;
    }
  }

  async findRelatedEntities(entityId: string, depth: number = 2): Promise<GraphData> {
    const query = `
      MATCH path = (start)-[*1..${depth}]-(related)
      WHERE start.id = $entityId
      RETURN path
    `;

    try {
      const result = await this.session.run(query, { entityId });
      const nodes = new Map<string, CustomNode>();
      const links: SimulationLinkDatum<SimulationNodeDatum>[] = [];

      result.records.forEach(record => {
        const path = record.get('path');
        path.segments.forEach((segment: {
          start: { properties: { id: string } };
          end: { properties: { id: string } };
          relationship: { properties: Record<string, any> };
        }) => {
          const start = segment.start;
          const end = segment.end;
          const relationship = segment.relationship;

          if (!nodes.has(start.properties.id)) {
            nodes.set(start.properties.id, {
              ...start.properties,
              id: start.properties.id
            });
          }

          if (!nodes.has(end.properties.id)) {
            nodes.set(end.properties.id, {
              ...end.properties,
              id: end.properties.id
            });
          }

          links.push({
            source: nodes.get(start.properties.id)!,
            target: nodes.get(end.properties.id)!,
            ...relationship.properties
          });
        });
      });

      return {
        nodes: Array.from(nodes.values()),
        links
      };
    } catch (error) {
      console.error('Failed to find related entities:', error);
      throw error;
    }
  }

  async close(): Promise<void> {
    await this.session.close();
    await this.driver.close();
  }

  async createGraph(analysisResult: any) {
    // 検索結果からグラフデータを生成
    const nodes = (analysisResult.entities || []).map((entity: any) => ({
      id: entity.name,
      label: entity.name,
      type: entity.type,
      weight: entity.relevance || 1
    }));

    const links = (analysisResult.relationships || []).map((rel: any) => ({
      source: rel.source,
      target: rel.target,
      type: rel.type || 'default',
      weight: rel.weight || 1
    }));

    return { nodes, links };
  }
}
