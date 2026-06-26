'use client';

import React, { useState } from 'react';
import axios from 'axios';
import { Button } from '@/components/ui/Button';
import { ReactFlowProvider, ReactFlow, Background, Controls, Node, Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { FileNode } from '@/components/ui/FileNode';
import { getLayoutedElements } from '@/lib/layout';
import { Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';
import { diff } from '@/lib/test';
import { usePRPolling } from '@/hooks/usePRPolling';
const nodeTypes = {
  modified: FileNode,
  added: FileNode,
  removed: FileNode,
  impacted: FileNode,
  dependency: FileNode,
};

export default function DashboardPage() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [triggerError, setTriggerError] = useState<string | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const { jobStatus, isProcessing, verdict, isCompleted, error: pollingError } = usePRPolling(jobId);

  const triggerAnalysis = async () => {
    setTriggerError(null);
    try {
      const payload = {
        repository_id: "test-repo",
        pr_number: 99,
        target_file: "frontend/src/components/PaymentForm.tsx",
        diff
      };
      
      const res = await axios.post(`${API_URL}/api/webhooks/pr`, payload);
      setJobId(res.data.job_id);
    } catch (err) {
      console.error("Failed to trigger webhook", err);
      setTriggerError("Failed to trigger API. Check console.");
    }
  };

  // Compute Layout if graph data is ready
  let nodes: Node[] = [];
  let edges: Edge[] = [];
  
  if (isCompleted && jobStatus?.analysis?.graph) {
    const rawNodes = jobStatus.analysis.graph.nodes || [];
    const rawEdges = jobStatus.analysis.graph.edges || [];
    const layouted = getLayoutedElements(rawNodes, rawEdges, 'TB');
    nodes = layouted.nodes;
    edges = layouted.edges;
  }

  return (
    <div className="flex w-full h-[calc(100vh-64px)] overflow-hidden bg-canvas">
      {/* Sidebar: Trigger */}
      <div className="w-[300px] shrink-0 border-r border-hairline bg-surface p-6 flex flex-col gap-6">
        <div>
          <h2 className="text-heading-lg text-ink mb-2">PR Intelligence</h2>
          <p className="text-body-sm text-mute">
            Trigger a graph-verified architectural code review.
          </p>
        </div>
        
        <Button 
          variant="primary" 
          className="w-full" 
          onClick={triggerAnalysis}
          disabled={isProcessing}
        >
          {isProcessing ? (
            <span className="flex items-center justify-center gap-2 w-full"><Loader2 className="w-4 h-4 animate-spin" /> Analyzing...</span>
          ) : "Trigger PR Analysis"}
        </Button>
        
        {(jobStatus?.status === 'failed' || triggerError || pollingError) && (
          <div className="p-4 rounded-[8px] border border-hairline bg-accent-red-soft flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-accent-red shrink-0" />
            <span className="text-body-sm text-accent-red">{triggerError || pollingError || jobStatus?.error || "Job failed"}</span>
          </div>
        )}
      </div>

      {/* Main Graph Canvas */}
      <div className="flex-grow relative border-r border-hairline bg-canvas">
        <ReactFlowProvider>
          {nodes.length > 0 ? (
            <ReactFlow
              nodes={nodes}
              edges={edges}
              nodeTypes={nodeTypes}
              fitView
              minZoom={0.5}
            >
              <Background color="#ccc" gap={16} />
              <Controls />
            </ReactFlow>
          ) : (
            <div className="absolute inset-0 flex flex-col items-center justify-center text-mute gap-4">
               {isProcessing ? (
                  <>
                    <Loader2 className="w-10 h-10 animate-spin text-accent-blue" />
                    <span className="text-heading-md">AI Agents are reviewing the code...</span>
                  </>
               ) : (
                  <>
                    <div className="w-16 h-16 rounded-full bg-surface-card border border-hairline flex items-center justify-center">
                        <CheckCircle2 className="w-6 h-6 opacity-20" />
                    </div>
                    <span className="text-body-lg">Click trigger to run analysis.</span>
                  </>
               )}
            </div>
          )}
        </ReactFlowProvider>
      </div>

      {/* AI Verdict Panel */}
      <div className="w-[450px] shrink-0 bg-surface p-6 overflow-y-auto">
        <h3 className="text-heading-lg text-ink mb-6">AI Verdict</h3>
        
        {isProcessing ? (
          <div className="flex flex-col gap-6 animate-pulse">
            <div>
              <div className="h-4 w-24 bg-surface-card border border-hairline-soft rounded mb-2"></div>
              <div className="h-8 w-20 bg-surface-card border border-hairline-soft rounded"></div>
            </div>
            <div>
              <div className="h-4 w-40 bg-surface-card border border-hairline-soft rounded mb-2"></div>
              <div className="h-24 w-full bg-surface-card border border-hairline-soft rounded"></div>
            </div>
            <div>
              <div className="h-4 w-32 bg-surface-card border border-hairline-soft rounded mb-2"></div>
              <div className="flex flex-col gap-3">
                <div className="h-12 w-full bg-surface-card border border-hairline-soft rounded"></div>
                <div className="h-12 w-full bg-surface-card border border-hairline-soft rounded"></div>
              </div>
            </div>
          </div>
        ) : !verdict ? (
          <div className="text-body-sm text-mute italic border border-hairline rounded p-4 text-center bg-surface-card">
            Waiting for LangGraph response...
          </div>
        ) : (
          <div className="flex flex-col gap-6">
            {/* Risk Level Badge */}
            <div>
              <span className="text-caption-sm text-mute uppercase block mb-2">Risk Level</span>
              <div className={`px-3 py-1 rounded-[6px] text-caption-md font-bold w-fit ${
                verdict.risk_level === 'High' || verdict.risk_level === 'Critical' 
                  ? 'bg-accent-red-soft text-accent-red'
                  : verdict.risk_level === 'Medium'
                  ? 'bg-accent-yellow-soft text-accent-yellow'
                  : 'bg-accent-green-soft text-accent-green'
              }`}>
                {verdict.risk_level}
              </div>
            </div>

            {/* Architectural Summary */}
            <div>
              <span className="text-caption-sm text-mute uppercase block mb-2">Architectural Summary</span>
              <p className="text-body-md text-ink leading-relaxed">
                {verdict.architectural_summary}
              </p>
            </div>

            {/* Impacted User Flows */}
            {verdict.impacted_flows?.length > 0 && (
              <div>
                <span className="text-caption-sm text-mute uppercase block mb-2">Impacted User Flows</span>
                <div className="flex flex-wrap gap-2">
                  {verdict.impacted_flows.map((flow: string, idx: number) => (
                    <span key={idx} className="bg-surface-elevated border border-hairline px-3 py-1 rounded-[6px] text-body-sm font-medium text-ink">
                      {flow}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Affected Teams */}
            {verdict.owners?.length > 0 && (
              <div>
                <span className="text-caption-sm text-mute uppercase block mb-2">Required Reviewers (Teams)</span>
                <div className="flex flex-wrap gap-2">
                  {verdict.owners.map((team: string, idx: number) => (
                    <span key={idx} className="bg-accent-blue-soft text-accent-blue px-3 py-1 rounded-[6px] text-body-sm font-medium">
                      {team}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Critical Findings */}
            {verdict.critical_findings?.length > 0 && (
              <div>
                <span className="text-caption-sm text-mute uppercase block mb-2">Critical Findings</span>
                <ul className="flex flex-col gap-3">
                  {verdict.critical_findings.map((finding: string, idx: number) => (
                    <li key={idx} className="p-3 rounded bg-surface-card border border-hairline-soft text-body-sm text-ink flex items-start gap-2">
                       <AlertCircle className="w-4 h-4 text-accent-red shrink-0 mt-0.5" />
                       {finding}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Recommendations */}
            {verdict.recommendations?.length > 0 && (
              <div>
                <span className="text-caption-sm text-mute uppercase block mb-2">Recommendations</span>
                <ul className="flex flex-col gap-3">
                  {verdict.recommendations.map((rec: string, idx: number) => (
                    <li key={idx} className="p-3 rounded bg-surface-card border border-hairline-soft text-body-sm text-ink flex items-start gap-2">
                       <CheckCircle2 className="w-4 h-4 text-accent-green shrink-0 mt-0.5" />
                       {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
