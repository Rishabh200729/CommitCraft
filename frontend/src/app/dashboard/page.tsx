'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Loader2, GitPullRequest, Search, AlertCircle } from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const [session, setSession] = useState<{authenticated: boolean, user?: any} | null>(null);
  const [repos, setRepos] = useState<any[]>([]);
  const [selectedRepo, setSelectedRepo] = useState<any | null>(null);
  const [prs, setPrs] = useState<any[]>([]);
  const [loadingRepos, setLoadingRepos] = useState(true);
  const [loadingPrs, setLoadingPrs] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Check session
  useEffect(() => {
    fetch('/api/auth/session')
      .then(res => res.json())
      .then(data => {
        if (!data.authenticated) {
          router.push('/');
        } else {
          setSession(data);
          fetchRepos();
        }
      })
      .catch(() => router.push('/'));
  }, [router]);

  const fetchRepos = async () => {
    setLoadingRepos(true);
    try {
      const res = await fetch('/api/github/repos');
      const data = await res.json();
      if (res.ok) {
        setRepos(data.repos || []);
      } else {
        setError(data.error || 'Failed to fetch repos');
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setLoadingRepos(false);
    }
  };

  const fetchPrs = async (repo: any) => {
    setSelectedRepo(repo);
    setLoadingPrs(true);
    setPrs([]);
    try {
      const res = await fetch(`/api/github/${repo.owner}/${repo.name}/pulls`);
      const data = await res.json();
      if (res.ok) {
        setPrs(data.pulls || []);
      } else {
        setError(data.error || 'Failed to fetch PRs');
      }
    } catch (err) {
      setError('Network error');
    } finally {
      setLoadingPrs(false);
    }
  };

  const handlePrClick = (pr: any) => {
    router.push(`/dashboard/${selectedRepo.owner}/${selectedRepo.name}/${pr.number}`);
  };

  if (!session) {
    return <div className="flex items-center justify-center h-screen bg-canvas"><Loader2 className="w-8 h-8 animate-spin text-ink" /></div>;
  }

  const filteredRepos = repos.filter(r => r.full_name.toLowerCase().includes(searchQuery.toLowerCase()));

  return (
    <div className="flex h-screen bg-canvas overflow-hidden">
      {/* Sidebar: Repos */}
      <div className="w-[350px] border-r border-hairline-soft bg-surface-base flex flex-col h-full">
        <div className="p-4 border-b border-hairline-soft flex items-center justify-between">
          <div className="flex items-center gap-3">
            {session.user?.avatar_url && (
              <img src={session.user.avatar_url} alt="Avatar" className="w-8 h-8 rounded-full border border-hairline-soft" />
            )}
            <span className="text-body-md text-ink font-medium">{session.user?.login}</span>
          </div>
          <Button variant="ghost" size="sm" onClick={() => window.location.href = '/api/auth/logout'}>Logout</Button>
        </div>
        
        <div className="p-4 border-b border-hairline-soft">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-mute" />
            <input 
              type="text" 
              placeholder="Search repositories..." 
              className="w-full bg-surface-card border border-hairline-soft rounded-md py-2 pl-9 pr-3 text-body-sm text-ink outline-none focus:border-accent-blue"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-2">
          {loadingRepos ? (
            <div className="flex justify-center p-4"><Loader2 className="w-6 h-6 animate-spin text-mute" /></div>
          ) : filteredRepos.length > 0 ? (
            <div className="flex flex-col gap-1">
              {filteredRepos.map(repo => (
                <button
                  key={repo.id}
                  onClick={() => fetchPrs(repo)}
                  className={`text-left px-3 py-2 rounded-md text-body-sm truncate transition-colors ${selectedRepo?.id === repo.id ? 'bg-surface-raised text-ink border border-hairline-soft shadow-sm' : 'text-mute hover:bg-surface-card hover:text-ink'}`}
                >
                  {repo.full_name}
                </button>
              ))}
            </div>
          ) : (
            <div className="text-center p-4 text-body-sm text-mute">No repositories found.</div>
          )}
        </div>
      </div>

      {/* Main Content: PRs */}
      <div className="flex-1 flex flex-col h-full bg-canvas">
        {!selectedRepo ? (
          <div className="flex-1 flex items-center justify-center text-body-lg text-mute">
            Select a repository to view Pull Requests
          </div>
        ) : (
          <>
            <div className="p-6 border-b border-hairline-soft bg-surface-base">
              <h2 className="text-heading-lg text-ink">{selectedRepo.full_name}</h2>
              <p className="text-body-sm text-mute mt-1">Open Pull Requests</p>
            </div>
            
            <div className="flex-1 overflow-y-auto p-6">
              {loadingPrs ? (
                <div className="flex justify-center p-8"><Loader2 className="w-8 h-8 animate-spin text-mute" /></div>
              ) : prs.length > 0 ? (
                <div className="flex flex-col gap-4 max-w-4xl">
                  {prs.map(pr => (
                    <Card key={pr.number} variant="feature" className="p-4 cursor-pointer hover:border-accent-blue transition-colors flex items-start gap-4" onClick={() => handlePrClick(pr)}>
                      <GitPullRequest className="w-5 h-5 text-accent-green mt-1 shrink-0" />
                      <div className="flex flex-col flex-1">
                        <div className="flex justify-between items-start">
                          <h3 className="text-heading-md text-ink font-medium leading-tight mb-1">{pr.title}</h3>
                          <span className="text-caption-md text-mute shrink-0">#{pr.number}</span>
                        </div>
                        <div className="flex gap-4 text-caption-md text-mute mt-2">
                          <span>By {pr.author}</span>
                          <span>Updated {new Date(pr.updated_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-64 text-center">
                  <GitPullRequest className="w-12 h-12 text-mute opacity-50 mb-4" />
                  <p className="text-body-lg text-ink font-medium">No open pull requests</p>
                  <p className="text-body-sm text-mute mt-1">This repository doesn't have any open PRs.</p>
                </div>
              )}
            </div>
          </>
        )}
      </div>

      {error && (
        <div className="absolute bottom-4 right-4 bg-surface-raised border border-status-error text-status-error px-4 py-3 rounded-md shadow-lg flex items-center gap-2 text-body-sm">
          <AlertCircle className="w-4 h-4" />
          {error}
          <button onClick={() => setError(null)} className="ml-4 opacity-70 hover:opacity-100">×</button>
        </div>
      )}
    </div>
  );
}
