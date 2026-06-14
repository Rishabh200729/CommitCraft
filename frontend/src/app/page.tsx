"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export default function Home() {
  const [diff, setDiff] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [commitMessage, setCommitMessage] = useState("");
  const [prDescription, setPrDescription] = useState("");
  const [prTab, setPrTab] = useState<'preview' | 'raw'>('preview');
  const [copiedCommit, setCopiedCommit] = useState(false);
  const [copiedPr, setCopiedPr] = useState(false);

  const handleGenerate = async () => {
    if (!diff.trim()) {
      setError("Please enter a git diff.");
      return;
    }
    
    setLoading(true);
    setError("");
    setCommitMessage("");
    setPrDescription("");

    try {
      const response = await fetch("http://localhost:8000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ diff }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to generate text");
      }

      setCommitMessage(data.commitMessage || "");
      setPrDescription(data.prDescription || "");
    } catch (err: any) {
      setError(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string, type: 'commit' | 'pr') => {
    navigator.clipboard.writeText(text);
    if (type === 'commit') {
      setCopiedCommit(true);
      setTimeout(() => setCopiedCommit(false), 2000);
    } else {
      setCopiedPr(true);
      setTimeout(() => setCopiedPr(false), 2000);
    }
  };

  return (
    <main className="min-h-screen flex flex-col p-6 md:p-12 lg:px-24">
      {/* Vercel-style Header */}
      <header className="flex flex-col gap-4 mb-12 mt-8">
        <h1 className="text-5xl md:text-6xl font-semibold tracking-[-2.4px] text-white">
          GitScribe.
        </h1>
        <p className="text-[18px] text-[#a1a1a1] max-w-2xl leading-relaxed">
          Paste your git diff below. AI will instantly generate a Conventional Commit message and a professional GitHub PR description.
        </p>
      </header>

      {/* Main Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8 xl:gap-12 flex-1 pb-12 items-start">
        
        {/* Left Column: Input */}
        <section className="flex flex-col gap-4">
          <label className="text-[12px] font-mono text-[#a1a1a1] uppercase tracking-wider">
            Git Diff Input
          </label>
          <div className="bg-[#111111] border border-[#333333] rounded-lg p-1 shadow-[0_1px_1px_#00000005] h-[400px]">
            <textarea
              className="w-full h-full bg-transparent text-[#ededed] p-4 font-mono text-[13px] leading-relaxed resize-none focus:outline-none"
              placeholder="diff --git a/file b/file..."
              value={diff}
              onChange={(e) => setDiff(e.target.value)}
            />
          </div>
          
          <button 
            onClick={handleGenerate} 
            disabled={loading}
            className="self-start mt-4 bg-white text-black font-medium text-[16px] px-8 py-3 rounded-full hover:bg-opacity-90 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_2px_4px_#0000001a]"
          >
            {loading ? "Generating..." : "Generate Description"}
          </button>
          
          {error && (
            <div className="mt-4 bg-[#ff1a1a]/10 border border-[#ff1a1a]/20 text-[#ff1a1a] text-sm p-4 rounded-md">
              {error}
            </div>
          )}
        </section>

        {/* Right Column: Output */}
        <section className="flex flex-col gap-8 h-full">
          {/* Commit Message Card */}
          <div className="flex flex-col gap-3">
             <div className="flex justify-between items-center">
               <label className="text-[12px] font-mono text-[#a1a1a1] uppercase tracking-wider">
                 Commit Message
               </label>
               {commitMessage && (
                 <button 
                   onClick={() => copyToClipboard(commitMessage, 'commit')}
                   className="text-[12px] text-[#a1a1a1] hover:text-white transition-colors flex items-center gap-1"
                 >
                   {copiedCommit ? "Copied!" : "Copy"}
                 </button>
               )}
             </div>
             
             <div className="bg-[#111111] border border-[#333333] rounded-lg p-6 min-h-[120px] shadow-[0_1px_2px_#0000000a]">
               {loading ? (
                 <div className="h-full flex items-center justify-center text-[#888888] animate-pulse text-[14px]">Analyzing diff...</div>
               ) : commitMessage ? (
                 <pre className="text-[14px] text-white whitespace-pre-wrap font-sans">{commitMessage}</pre>
               ) : (
                 <div className="text-[#888888] text-[14px]">No output yet.</div>
               )}
             </div>
          </div>

          {/* PR Description Card */}
          <div className="flex flex-col gap-3 flex-1">
             <div className="flex justify-between items-center">
               <div className="flex items-center gap-4">
                 <label className="text-[12px] font-mono text-[#a1a1a1] uppercase tracking-wider">
                   Pull Request Description
                 </label>
                 {prDescription && (
                   <div className="flex bg-[#222222] rounded-md p-1">
                     <button
                       onClick={() => setPrTab('preview')}
                       className={`text-[11px] px-3 py-1 rounded-sm transition-colors ${prTab === 'preview' ? 'bg-[#333333] text-white' : 'text-[#888888] hover:text-[#cccccc]'}`}
                     >
                       Preview
                     </button>
                     <button
                       onClick={() => setPrTab('raw')}
                       className={`text-[11px] px-3 py-1 rounded-sm transition-colors ${prTab === 'raw' ? 'bg-[#333333] text-white' : 'text-[#888888] hover:text-[#cccccc]'}`}
                     >
                       Raw
                     </button>
                   </div>
                 )}
               </div>
               {prDescription && (
                 <button 
                   onClick={() => copyToClipboard(prDescription, 'pr')}
                   className="text-[12px] text-[#a1a1a1] hover:text-white transition-colors flex items-center gap-1"
                 >
                   {copiedPr ? "Copied!" : "Copy"}
                 </button>
               )}
             </div>
             
             <div className="bg-[#111111] border border-[#333333] rounded-lg p-6 min-h-[300px] h-full flex-1 shadow-[0_1px_2px_#0000000a] overflow-auto">
               {loading ? (
                 <div className="h-full flex items-center justify-center text-[#888888] animate-pulse text-[14px]">Generating description...</div>
               ) : prDescription ? (
                 prTab === 'raw' ? (
                   <div className="text-[14px] text-[#e0e0e0] whitespace-pre-wrap font-mono leading-relaxed">{prDescription}</div>
                 ) : (
                   <div className="text-[14px] text-[#e0e0e0] whitespace-pre-wrap font-sans leading-relaxed markdown-preview">
                     <ReactMarkdown remarkPlugins={[remarkGfm]}>
                       {prDescription}
                     </ReactMarkdown>
                   </div>
                 )
               ) : (
                 <div className="text-[#888888] text-[14px]">No output yet.</div>
               )}
             </div>
          </div>
        </section>

      </div>
    </main>
  );
}
