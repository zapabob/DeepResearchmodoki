import networkx as nx

class GraphService:
    def __init__(self):
        pass

    async def analyze(self, data):
        # ダミー実装のため、与えられたデータをそのまま返す
        return data

    def generate_graph(self, analysis_result):
        if not analysis_result:
            print("Warning: Empty analysis result")
            return self._create_empty_graph()
            
        try:
            print("Starting graph generation...")
            # グラフのクリア
            self.graph.clear()
            
            # エンティティをノードとして追加
            entities = analysis_result.get('entities', [])
            if not isinstance(entities, list):
                print("Warning: entities is not a list")
                return self._create_empty_graph()
                
            print(f"Processing {len(entities)} entities...")
            for entity in entities:
                if isinstance(entity, str):
                    # 文字列の場合は単純なノードとして追加
                    self.graph.add_node(
                        entity,
                        label=entity,
                        type='DEFAULT',
                        weight=1
                    )
                elif isinstance(entity, dict):
                    # 辞書の場合は属性付きノードとして追加
                    self.graph.add_node(
                        entity.get('name', str(entity)),
                        label=entity.get('name', str(entity)),
                        type=entity.get('type', 'DEFAULT'),
                        weight=entity.get('relevance', 1)
                    )
            
            # 関係性をエッジとして追加
            relationships = analysis_result.get('relationships', [])
            if not isinstance(relationships, list):
                print("Warning: relationships is not a list")
                relationships = []
                
            print(f"Processing {len(relationships)} relationships...")
            for rel in relationships:
                if isinstance(rel, dict) and 'source' in rel and 'target' in rel:
                    self.graph.add_edge(
                        rel['source'],
                        rel['target'],
                        type=rel.get('type', 'default'),
                        weight=rel.get('weight', 1)
                    )
            
            # グラフデータの形式を整える
            result = {
                'nodes': [
                    {
                        'id': node,
                        'label': self.graph.nodes[node].get('label', node),
                        'type': self.graph.nodes[node].get('type', 'DEFAULT'),
                        'weight': self.graph.nodes[node].get('weight', 1)
                    }
                    for node in self.graph.nodes
                ],
                'links': [
                    {
                        'source': edge[0],
                        'target': edge[1],
                        'type': self.graph.edges[edge].get('type', 'default'),
                        'weight': self.graph.edges[edge].get('weight', 1)
                    }
                    for edge in self.graph.edges
                ]
            }
            
            print("Graph generation completed successfully")
            return result
            
        except Exception as e:
            error_msg = f"グラフ生成中にエラーが発生しました: {str(e)}"
            print(error_msg)
            print(f"Error type: {type(e).__name__}")
            return self._create_empty_graph()
            
    def _create_empty_graph(self):
        return {
            'nodes': [],
            'links': []
        }

    async def create_graph(self, analysis):
        # ダミー実装: 与えられた分析結果から空のグラフ情報を返す
        return {} 