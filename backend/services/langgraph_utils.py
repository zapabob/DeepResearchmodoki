import logging

try:
    from langgraph import Graph
except Exception:  # pragma: no cover - library optional
    Graph = None

logger = logging.getLogger(__name__)

def generate_graph_from_text(text: str):
    """Generate a knowledge graph using langgraph if available."""
    if Graph is None:
        logger.warning("langgraph package not installed; skipping graph generation")
        return None
    try:
        g = Graph({})
        return g.query({"queryText": text})
    except Exception as e:  # pragma: no cover - best effort
        logger.error("LangGraph generation failed: %s", e)
        return None
