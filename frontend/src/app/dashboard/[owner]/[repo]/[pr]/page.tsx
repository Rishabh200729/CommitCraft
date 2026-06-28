'use client';

import React, { useEffect, useState, useCallback, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from "@/components/ui/Button";
import { Loader2, ArrowLeft, Play, FileCode, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import { 
  ReactFlow,
  Background, 
  Controls, 
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { FileNode } from '@/components/ui/FileNode'; // We will ensure this exists/update it
import { Card } from '@/components/ui/Card';

const nodeTypes = {
  added: FileNode,
  modified: FileNode,
  removed: FileNode,
  impacted: FileNode,
  dependency: FileNode,
};

export default function PrAnalysisPage({ params }: { params: { owner: string, repo: string, pr: string } }) {
  const router = useRouter();
  const { owner, repo, pr } = params;
  
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>('idle'); // idle, processing, completed, failed
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNodeData, setSelectedNodeData] = useState<any>(null);

  // Poll for job status
  useEffect(() => {
    let interval: NodeJS.Timeout;
    
    if (jobId && status === 'processing') {
      interval = setInterval(async () => {
        try {
          const res = await fetch(`/api/analyze?job_id=${jobId}`);
          const data = await res.json();
          
          if (data.status === 'completed') {
            setStatus('completed');
            setAnalysisData(data.analysis);
            clearInterval(interval);
          } else if (data.status === 'failed') {
            setStatus('failed');
            setError(data.error || 'Analysis failed');
            clearInterval(interval);
          }
        } catch (err) {
          console.error("Polling error", err);
        }
      }, 3000);
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [jobId, status]);

  // Layout graph when data arrives
  useEffect(() => {
    if (analysisData?.graph) {
      const g = analysisData.graph;
      
      // Basic horizontal layout algorithm (very simplified)
      const formattedNodes = g.nodes.map((node: any, idx: number) => {
        // Just spread them out a bit for the demo, React Flow handles the rest with drag
        // In a real app, use dagre for layout
        let x = 0;
        let y = idx * 100;
        
        if (node.type === 'added' || node.type === 'modified' || node.type === 'removed') {
          x = 400; // center
        } else if (node.type === 'dependency') {
          x = 100; // left
        } else if (node.type === 'impacted') {
          x = 700; // right
        }
        
        // Find corresponding findings for this file
        const finding = analysisData.final_annotations?.[node.id];
        
        return {
          ...node,
          position: { x, y },
          data: {
            ...node.data,
            finding,
            onClick: () => setSelectedNodeData({ ...node.data, finding, id: node.id })
          }
        };
      });
      
      const formattedEdges = g.edges.map((edge: any) => ({
        ...edge,
        animated: true,
        style: { stroke: '#8B949E' },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#8B949E' }
      }));
      
      setNodes(formattedNodes);
      setEdges(formattedEdges);
    }
  }, [analysisData, setNodes, setEdges]);

  const startAnalysis = async () => {
    setStatus('processing');
    setError(null);
    try {
      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ owner, repo, pr_number: parseInt(pr) })
      });
      const data = await res.json();
      
      if (res.ok) {
        setJobId(data.job_id);
      } else {
        setStatus('failed');
        setError(data.error || 'Failed to start analysis');
      }
    } catch (err) {
      setStatus('failed');
      setError('Network error');
    }
  };

  return (
    <div className="flex flex-col h-screen bg-canvas">
      {/* Header */}
      <header className="h-16 border-b border-hairline-soft bg-surface-base flex items-center justify-between px-6 shrink-0 z-10">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => router.push('/dashboard')}>
            <ArrowLeft className="w-4 h-4 mr-2" /> Back
          </Button>
          <div className="h-6 w-px bg-hairline-soft" />
          <h1 className="text-heading-md text-ink font-medium">
            {owner}/{repo} <span className="text-mute font-normal">#{pr}</span>
          </h1>
        </div>
        <div>
          {status === 'idle' && (
            <Button variant="primary" onClick={startAnalysis}>
              <Play className="w-4 h-4 mr-2" /> Start Review
            </Button>
          )}
          {status === 'processing' && (
            <div className="flex items-center gap-2 text-accent-blue text-body-sm font-medium">
              <Loader2 className="w-4 h-4 animate-spin" /> Analyzing PR...
            </div>
          )}
          {status === 'failed' && (
            <div className="text-status-error text-body-sm font-medium flex items-center gap-2">
              <XCircle className="w-4 h-4" /> {error}
            </div>
          )}
          {status === 'completed' && (
            <div className="text-status-success text-body-sm font-medium flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" /> Analysis Complete
            </div>
          )}
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* React Flow Graph */}
        <div className="flex-1 relative">
          {status === 'idle' ? (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <FileCode className="w-16 h-16 text-mute opacity-50 mx-auto mb-4" />
                <h2 className="text-heading-lg text-ink mb-2">Ready to Review</h2>
                <p className="text-body-md text-mute max-w-md mx-auto mb-6">
                  GitScribe will clone this repository, build a dependency graph, and analyze every changed file for logic flaws and architectural risks.
                </p>
                <Button variant="primary" onClick={startAnalysis}>
                  <Play className="w-4 h-4 mr-2" /> Start Review
                </Button>
              </div>
            </div>
          ) : (
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              nodeTypes={nodeTypes}
              fitView
              attributionPosition="bottom-right"
              className="bg-canvas"
            >
              <Background color="#30363D" gap={16} />
              <Controls />
            </ReactFlow>
          )}
        </div>

        {/* Sidebar: Verdict & Node Details */}
        {(status === 'completed' || selectedNodeData) && (
          <div className="w-[400px] border-l border-hairline-soft bg-surface-base flex flex-col z-10 overflow-y-auto">
            {/* Overall Verdict */}
            {analysisData?.overall_verdict && (
              <div className="p-6 border-b border-hairline-soft">
                <h3 className="text-heading-md text-ink mb-4">Overall Verdict</h3>
                <div className={`p-4 rounded-md border ${
                  analysisData.overall_verdict.decision === 'approve' 
                    ? 'bg-status-success/10 border-status-success/30 text-status-success' 
                    : analysisData.overall_verdict.decision === 'reject'
                      ? 'bg-status-error/10 border-status-error/30 text-status-error'
                      : 'bg-status-warning/10 border-status-warning/30 text-status-warning'
                }`}>
                  <div className="font-semibold uppercase tracking-wider text-sm mb-2">
                    {analysisData.overall_verdict.decision}
                  </div>
                  <p className="text-body-sm text-ink opacity-90">{analysisData.overall_verdict.summary}</p>
                </div>
              </div>
            )}

            {/* Selected Node Details */}
            {selectedNodeData && (
              <div className="p-6">
                <h3 className="text-heading-md text-ink mb-4 truncate" title={selectedNodeData.id}>
                  {selectedNodeData.label}
                </h3>
                
                {selectedNodeData.finding ? (
                  <div className="flex flex-col gap-4">
                    <Card variant="feature" className="p-4">
                      <h4 className="text-caption-md text-mute uppercase tracking-wider mb-2">Severity</h4>
                      <div className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                        selectedNodeData.finding.severity === 'high' ? 'bg-status-error/20 text-status-error' :
                        selectedNodeData.finding.severity === 'medium' ? 'bg-status-warning/20 text-status-warning' :
                        'bg-status-success/20 text-status-success'
                      }`}>
                        {selectedNodeData.finding.severity.toUpperCase()}
                      </div>
                    </Card>
                    
                    <Card variant="feature" className="p-4">
                      <h4 className="text-caption-md text-mute uppercase tracking-wider mb-2">Critic Analysis</h4>
                      <p className="text-body-sm text-ink whitespace-pre-wrap">{selectedNodeData.finding.critic_rationale}</p>
                    </Card>
                    
                    {selectedNodeData.finding.security_issues?.length > 0 && (
                      <Card variant="feature" className="p-4 border-status-error/30 bg-status-error/5">
                        <h4 className="text-caption-md text-status-error uppercase tracking-wider mb-2 flex items-center gap-2">
                          <AlertCircle className="w-4 h-4" /> Security Issues
                        </h4>
                        <ul className="list-disc pl-4 text-body-sm text-ink">
                          {selectedNodeData.finding.security_issues.map((issue: string, i: number) => (
                            <li key={i}>{issue}</li>
                          ))}
                        </ul>
                      </Card>
                    )}
                  </div>
                ) : (
                  <p className="text-body-sm text-mute">No detailed findings for this file.</p>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
