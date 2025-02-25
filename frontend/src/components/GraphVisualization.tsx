import React, { useEffect, useRef } from "react";
import * as d3 from "d3";
import { GraphData, GraphNode, GraphLink } from "../types";
import { Box, Paper, Typography } from "@mui/material";

interface GraphVisualizationProps {
  data: GraphData;
}

export const GraphVisualization: React.FC<GraphVisualizationProps> = ({ data }) => {
  const svgRef = useRef<SVGSVGElement>(null);

  useEffect(() => {
    if (!svgRef.current || !data) return;

    const width = 800;
    const height = 600;
    const svg = d3.select(svgRef.current);

    // Clear previous content
    svg.selectAll("*").remove();

    // Create simulation
    const simulation = d3.forceSimulation<GraphNode>(data.nodes as GraphNode[])
      .force("link", d3.forceLink<GraphNode, GraphLink>(data.links as GraphLink[])
        .id(d => d.id)
        .distance(100))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2));

    // Draw links
    const links = svg.append("g")
      .selectAll("line")
      .data(data.links)
      .enter()
      .append("line")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", d => Math.sqrt((d as GraphLink).weight || 1));

    // Draw nodes
    const nodes = svg.append("g")
      .selectAll("circle")
      .data(data.nodes)
      .enter()
      .append("circle")
      .attr("r", d => Math.sqrt((d as GraphNode).weight || 1) * 5)
      .attr("fill", d => getNodeColor((d as GraphNode).type))
      .call(d3.drag<SVGCircleElement, any>()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended));

    // Add labels
    const labels = svg.append("g")
      .selectAll("text")
      .data(data.nodes)
      .enter()
      .append("text")
      .text(d => (d as GraphNode).label)
      .attr("font-size", "12px")
      .attr("dx", 15)
      .attr("dy", 4);

    // Update positions
    simulation.on("tick", () => {
      links
        .attr("x1", d => (d.source as any).x)
        .attr("y1", d => (d.source as any).y)
        .attr("x2", d => (d.target as any).x)
        .attr("y2", d => (d.target as any).y);

      nodes
        .attr("cx", (d: any) => d.x)
        .attr("cy", (d: any) => d.y);

      labels
        .attr("x", (d: any) => d.x)
        .attr("y", (d: any) => d.y);
    });

    // Drag functions
    function dragstarted(event: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }

    function dragged(event: any) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }

    function dragended(event: any) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }

    return () => {
      simulation.stop();
    };
  }, [data]);

  // ノードの種類に応じて色を返す関数
  const getNodeColor = (type: string): string => {
    const colors: { [key: string]: string } = {
      PERSON: "#ff7f0e",
      ORGANIZATION: "#1f77b4",
      LOCATION: "#2ca02c",
      CONCEPT: "#d62728",
      EVENT: "#9467bd",
      PRODUCT: "#8c564b",
      DEFAULT: "#7f7f7f",
    };
    return colors[type] || colors.DEFAULT;
  };

  return (
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        知識グラフ可視化
      </Typography>
      <Box sx={{ width: "100%", height: "600px", overflow: "hidden" }}>
        <svg
          ref={svgRef}
          style={{
            width: '100%',
            height: '600px',
            border: '1px solid #ddd',
            borderRadius: '4px'
          }}
        />
      </Box>
      <Typography variant="caption" color="text.secondary">
        ノードをドラッグして移動できます。ホイールでズームイン/アウト
      </Typography>
    </Paper>
  );
};

export default GraphVisualization;
