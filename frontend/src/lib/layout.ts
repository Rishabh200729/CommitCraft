import dagre from 'dagre';
import { Node, Edge } from '@xyflow/react';

export const getLayoutedElements = (nodes: Node[], edges: Edge[], direction = 'TB') => {
  const dagreGraph = new dagre.graphlib.Graph();
  dagreGraph.setDefaultEdgeLabel(() => ({}));

  const isHorizontal = direction === 'LR';
  dagreGraph.setGraph({ rankdir: direction, nodesep: 60, ranksep: 100 });

  nodes.forEach((node) => {
    // Hardcode matching the w-[250px] from FileNode
    dagreGraph.setNode(node.id, { width: 250, height: 72 });
  });

  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target);
  });

  dagre.layout(dagreGraph);

  nodes.forEach((node) => {
    const nodeWithPosition = dagreGraph.node(node.id);
    
    // React Flow anchors nodes at top-left, dagre anchors at center
    node.position = {
      x: nodeWithPosition.x - 125,
      y: nodeWithPosition.y - 36,
    };
  });

  return { nodes, edges };
};
