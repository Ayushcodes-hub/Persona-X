import React, { useEffect, useRef, useState } from 'react';
import { ZoomIn, ZoomOut, RotateCcw, X, ExternalLink } from 'lucide-react';
import type { GraphData, GraphNode, GraphEdge } from '../types';

interface EvidenceGraphCanvasProps {
  graphData: GraphData;
  onNodeSelect?: (node: GraphNode) => void;
}

const TYPE_COLORS: Record<string, string> = {
  person: '#00f0ff',
  source: '#3b82f6',
  evidence: '#10b981',
  claim: '#f59e0b',
  statement: '#a855f7',
  initiative: '#ec4899',
  timeline: '#14b8a6',
};

export const EvidenceGraphCanvas: React.FC<EvidenceGraphCanvasProps> = ({
  graphData,
  onNodeSelect,
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [hoveredNode, setHoveredNode] = useState<GraphNode | null>(null);
  const [filterType, setFilterType] = useState<string>('all');

  // Simulation state
  const nodesRef = useRef<GraphNode[]>([]);
  const edgesRef = useRef<GraphEdge[]>([]);
  const transformRef = useRef({ x: 0, y: 0, k: 1 });
  const isDraggingRef = useRef(false);
  const dragNodeRef = useRef<GraphNode | null>(null);
  const lastMousePosRef = useRef({ x: 0, y: 0 });

  // Initialize simulation positions
  useEffect(() => {
    if (!graphData || !graphData.nodes) return;

    const width = 800;
    const height = 500;
    const angleStep = (2 * Math.PI) / Math.max(graphData.nodes.length - 1, 1);

    nodesRef.current = graphData.nodes.map((node, i) => {
      if (node.type === 'person') {
        return { ...node, x: width / 2, y: height / 2, vx: 0, vy: 0 };
      }
      const radius = 120 + (i % 3) * 60;
      const angle = i * angleStep;
      return {
        ...node,
        x: width / 2 + Math.cos(angle) * radius + (Math.random() - 0.5) * 40,
        y: height / 2 + Math.sin(angle) * radius + (Math.random() - 0.5) * 40,
        vx: 0,
        vy: 0,
      };
    });

    edgesRef.current = [...(graphData.edges || [])];
    transformRef.current = { x: 0, y: 0, k: 1 };
  }, [graphData]);

  // Main canvas render & simple force relaxation loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;

    const tick = () => {
      // Simple force simulation step
      const nodes = nodesRef.current;
      const edges = edgesRef.current;

      // Repulsion between nodes
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = (nodes[j].x || 0) - (nodes[i].x || 0);
          const dy = (nodes[j].y || 0) - (nodes[i].y || 0);
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          if (dist < 180) {
            const force = (180 - dist) / dist * 0.04;
            if (nodes[i].type !== 'person' && dragNodeRef.current !== nodes[i]) {
              nodes[i].x = (nodes[i].x || 0) - dx * force;
              nodes[i].y = (nodes[i].y || 0) - dy * force;
            }
            if (nodes[j].type !== 'person' && dragNodeRef.current !== nodes[j]) {
              nodes[j].x = (nodes[j].x || 0) + dx * force;
              nodes[j].y = (nodes[j].y || 0) + dy * force;
            }
          }
        }
      }

      // Spring attraction along edges
      for (const edge of edges) {
        const source = nodes.find((n) => n.id === edge.source);
        const target = nodes.find((n) => n.id === edge.target);
        if (source && target) {
          const dx = (target.x || 0) - (source.x || 0);
          const dy = (target.y || 0) - (source.y || 0);
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          const targetDist = 90;
          const force = (dist - targetDist) * 0.015;
          if (source.type !== 'person' && dragNodeRef.current !== source) {
            source.x = (source.x || 0) + (dx / dist) * force;
            source.y = (source.y || 0) + (dy / dist) * force;
          }
          if (target.type !== 'person' && dragNodeRef.current !== target) {
            target.x = (target.x || 0) - (dx / dist) * force;
            target.y = (target.y || 0) - (dy / dist) * force;
          }
        }
      }

      // Draw canvas frame
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.save();
      ctx.translate(transformRef.current.x, transformRef.current.y);
      ctx.scale(transformRef.current.k, transformRef.current.k);

      // 1. Draw Edges
      for (const edge of edges) {
        const source = nodes.find((n) => n.id === edge.source);
        const target = nodes.find((n) => n.id === edge.target);
        if (source && target && (filterType === 'all' || source.type === filterType || target.type === filterType)) {
          ctx.beginPath();
          ctx.moveTo(source.x || 0, source.y || 0);
          ctx.lineTo(target.x || 0, target.y || 0);
          ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      }

      // 2. Draw Nodes
      for (const node of nodes) {
        if (filterType !== 'all' && node.type !== 'person' && node.type !== filterType) {
          continue;
        }

        const isPerson = node.type === 'person';
        const isHovered = hoveredNode?.id === node.id;
        const isSelected = selectedNode?.id === node.id;
        const radius = isPerson ? 20 : 10;
        const color = TYPE_COLORS[node.type] || '#94a3b8';

        // Outer glow on hover or person node
        if (isPerson || isHovered || isSelected) {
          ctx.beginPath();
          ctx.arc(node.x || 0, node.y || 0, radius + 6, 0, 2 * Math.PI);
          ctx.fillStyle = color;
          ctx.globalAlpha = 0.25;
          ctx.fill();
          ctx.globalAlpha = 1.0;
        }

        // Inner circle
        ctx.beginPath();
        ctx.arc(node.x || 0, node.y || 0, radius, 0, 2 * Math.PI);
        ctx.fillStyle = color;
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = isSelected ? 2 : 1;
        ctx.stroke();

        // Label text
        ctx.font = isPerson ? 'bold 12px sans-serif' : '10px sans-serif';
        ctx.fillStyle = '#f8fafc';
        ctx.textAlign = 'center';
        ctx.fillText(
          (node.label || '').slice(0, 18) + ((node.label || '').length > 18 ? '...' : ''),
          node.x || 0,
          (node.y || 0) + radius + 14
        );
      }

      ctx.restore();
      animId = requestAnimationFrame(tick);
    };

    animId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animId);
  }, [hoveredNode, selectedNode, filterType]);

  // Mouse / Drag handlers
  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mouseX = (e.clientX - rect.left - transformRef.current.x) / transformRef.current.k;
    const mouseY = (e.clientY - rect.top - transformRef.current.y) / transformRef.current.k;

    const clicked = nodesRef.current.find((n) => {
      const dx = (n.x || 0) - mouseX;
      const dy = (n.y || 0) - mouseY;
      return Math.sqrt(dx * dx + dy * dy) <= (n.type === 'person' ? 22 : 12);
    });

    if (clicked) {
      dragNodeRef.current = clicked;
      setSelectedNode(clicked);
      if (onNodeSelect) onNodeSelect(clicked);
    } else {
      isDraggingRef.current = true;
      lastMousePosRef.current = { x: e.clientX, y: e.clientY };
    }
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mouseX = (e.clientX - rect.left - transformRef.current.x) / transformRef.current.k;
    const mouseY = (e.clientY - rect.top - transformRef.current.y) / transformRef.current.k;

    if (dragNodeRef.current) {
      dragNodeRef.current.x = mouseX;
      dragNodeRef.current.y = mouseY;
      return;
    }

    if (isDraggingRef.current) {
      const dx = e.clientX - lastMousePosRef.current.x;
      const dy = e.clientY - lastMousePosRef.current.y;
      transformRef.current.x += dx;
      transformRef.current.y += dy;
      lastMousePosRef.current = { x: e.clientX, y: e.clientY };
      return;
    }

    // Check hover
    const hovered = nodesRef.current.find((n) => {
      const dx = (n.x || 0) - mouseX;
      const dy = (n.y || 0) - mouseY;
      return Math.sqrt(dx * dx + dy * dy) <= (n.type === 'person' ? 22 : 12);
    });
    setHoveredNode(hovered || null);
  };

  const handleMouseUp = () => {
    isDraggingRef.current = false;
    dragNodeRef.current = null;
  };

  const handleWheel = (e: React.WheelEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
    transformRef.current.k = Math.max(0.4, Math.min(3.0, transformRef.current.k * zoomFactor));
  };

  return (
    <div className="glass-panel" style={{ position: 'relative', overflow: 'hidden', height: '560px', display: 'flex', flexDirection: 'column' }}>
      {/* Top Controls Toolbar */}
      <div style={{
        position: 'absolute',
        top: 14,
        left: 14,
        right: 14,
        zIndex: 10,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        pointerEvents: 'none',
      }}>
        {/* Filter Pills */}
        <div style={{ display: 'flex', gap: '6px', pointerEvents: 'auto', flexWrap: 'wrap' }}>
          {['all', 'source', 'evidence', 'claim', 'statement', 'initiative'].map((type) => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              style={{
                padding: '4px 10px',
                borderRadius: '6px',
                fontSize: '11px',
                fontWeight: 600,
                textTransform: 'uppercase',
                background: filterType === type ? 'var(--accent-cyan)' : 'rgba(18, 24, 36, 0.85)',
                color: filterType === type ? '#07090e' : 'var(--text-secondary)',
                border: '1px solid var(--border-medium)',
                backdropFilter: 'blur(8px)',
              }}
            >
              {type}
            </button>
          ))}
        </div>

        {/* Zoom & Reset Controls */}
        <div style={{ display: 'flex', gap: '6px', pointerEvents: 'auto' }}>
          <button
            onClick={() => { transformRef.current.k *= 1.2; }}
            style={{ padding: '6px', borderRadius: '6px', background: 'rgba(18, 24, 36, 0.85)', border: '1px solid var(--border-medium)', color: '#f8fafc' }}
          >
            <ZoomIn size={14} />
          </button>
          <button
            onClick={() => { transformRef.current.k *= 0.8; }}
            style={{ padding: '6px', borderRadius: '6px', background: 'rgba(18, 24, 36, 0.85)', border: '1px solid var(--border-medium)', color: '#f8fafc' }}
          >
            <ZoomOut size={14} />
          </button>
          <button
            onClick={() => { transformRef.current = { x: 0, y: 0, k: 1 }; }}
            style={{ padding: '6px', borderRadius: '6px', background: 'rgba(18, 24, 36, 0.85)', border: '1px solid var(--border-medium)', color: '#f8fafc' }}
          >
            <RotateCcw size={14} />
          </button>
        </div>
      </div>

      {/* Canvas Element */}
      <canvas
        ref={canvasRef}
        width={960}
        height={560}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onWheel={handleWheel}
        style={{ width: '100%', height: '100%', cursor: dragNodeRef.current ? 'grabbing' : isDraggingRef.current ? 'move' : 'crosshair' }}
      />

      {/* Node Inspector Drawer */}
      {selectedNode && (
        <div
          className="glass-panel"
          style={{
            position: 'absolute',
            bottom: 14,
            right: 14,
            width: '320px',
            maxHeight: '260px',
            overflowY: 'auto',
            padding: '14px',
            border: '1px solid var(--border-glow)',
            zIndex: 20,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span className="badge" style={{ background: `${TYPE_COLORS[selectedNode.type]}20`, color: TYPE_COLORS[selectedNode.type] }}>
              {selectedNode.type}
            </span>
            <button onClick={() => setSelectedNode(null)} style={{ color: 'var(--text-muted)' }}>
              <X size={14} />
            </button>
          </div>
          <h4 style={{ fontSize: '13px', fontWeight: 600, color: '#f8fafc', marginBottom: '4px' }}>
            {selectedNode.label}
          </h4>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '8px' }}>
            Confidence: {(selectedNode.confidence * 100).toFixed(0)}% • ID: {selectedNode.id}
          </div>
          {selectedNode.metadata?.url && (
            <a
              href={selectedNode.metadata.url}
              target="_blank"
              rel="noreferrer"
              style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '11px', color: 'var(--text-cyan)', textDecoration: 'none' }}
            >
              <span>View Captured Source</span>
              <ExternalLink size={11} />
            </a>
          )}
        </div>
      )}
    </div>
  );
};
