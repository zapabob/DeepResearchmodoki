"""Knowledge graph generation module using langgraph"""
from typing import Dict, List, Optional
import json

import networkx as nx
from pydantic import BaseModel


class GraphConfig(BaseModel):
    """Knowledge graph configuration settings"""
    min_edge_weight: float = 0.5
    max_nodes: int = 1000
    layout_algorithm: str = "force"
    node_size_scale: float = 1000.0
    edge_width_scale: float = 2.0


class KnowledgeGraph:
    """Knowledge graph implementation"""
    
    def __init__(self, config: GraphConfig):
        self.config = config
        self.graph = nx.Graph()
        self.node_attributes = {}
        
    def add_entities(self, entities: List[Dict]):
        """
        Add entities to the knowledge graph
        
        Args:
            entities: List of entity information
        """
        for entity in entities:
            node_id = entity["name"]
            # 重要度に基づいてノードサイズを設定
            size = entity.get("importance", 0.5) * self.config.node_size_scale
            
            self.graph.add_node(
                node_id,
                type=entity.get("type", "unknown"),
                size=size,
                importance=entity.get("importance", 0.5)
            )
            self.node_attributes[node_id] = entity
        
    def add_relationships(self, relationships: List[Dict]):
        """
        Add relationships between entities
        
        Args:
            relationships: List of relationship information
        """
        for rel in relationships:
            source = rel["source"]
            target = rel["target"]
            weight = rel.get("weight", 0.5)
            
            # 最小重み以上の関係のみを追加
            if weight >= self.config.min_edge_weight:
                # エッジの幅を重みに基づいて設定
                width = weight * self.config.edge_width_scale
                
                self.graph.add_edge(
                    source,
                    target,
                    type=rel.get("type", "related"),
                    weight=weight,
                    width=width
                )
        
    def _apply_layout(self) -> Dict[str, List[float]]:
        """Apply layout algorithm to the graph"""
        if self.config.layout_algorithm == "force":
            layout = nx.spring_layout(self.graph, k=1/pow(self.graph.number_of_nodes(), 0.3))
        elif self.config.layout_algorithm == "circular":
            layout = nx.circular_layout(self.graph)
        else:
            layout = nx.random_layout(self.graph)
            
        # 座標を辞書に変換
        return {node: pos.tolist() for node, pos in layout.items()}
        
    def generate_visualization(self) -> Dict:
        """
        Generate visualization data for the knowledge graph
        
        Returns:
            Visualization data in a format suitable for frontend rendering
        """
        if self.graph.number_of_nodes() == 0:
            return {"nodes": [], "edges": []}
            
        # レイアウトを計算
        layout = self._apply_layout()
        
        # ノードデータを生成
        nodes = []
        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]
            position = layout[node]
            
            nodes.append({
                "id": node,
                "label": node,
                "type": node_data.get("type", "unknown"),
                "size": node_data.get("size", self.config.node_size_scale * 0.5),
                "importance": node_data.get("importance", 0.5),
                "x": position[0],
                "y": position[1],
                "attributes": self.node_attributes.get(node, {})
            })
        
        # エッジデータを生成
        edges = []
        for source, target, data in self.graph.edges(data=True):
            edges.append({
                "source": source,
                "target": target,
                "type": data.get("type", "related"),
                "weight": data.get("weight", 0.5),
                "width": data.get("width", self.config.edge_width_scale * 0.5)
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "layout_algorithm": self.config.layout_algorithm
            }
        }
        
    def get_central_entities(self, top_k: int = 5) -> List[Dict]:
        """
        Get the most central entities in the graph
        
        Args:
            top_k: Number of central entities to return
            
        Returns:
            List of central entities with their centrality scores
        """
        if self.graph.number_of_nodes() == 0:
            return []
            
        # 中心性を計算
        centrality = nx.eigenvector_centrality_numpy(self.graph)
        
        # 中心性でソート
        central_nodes = sorted(
            centrality.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_k]
        
        return [
            {
                "entity": node,
                "centrality": score,
                "attributes": self.node_attributes.get(node, {})
            }
            for node, score in central_nodes
        ] 