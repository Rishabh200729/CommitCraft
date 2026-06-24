import React from 'react';
import { Card } from './Card';
import { Badge } from './Badge';

export function CommandPaletteMockup() {
  return (
    <Card variant="commandPalette" className="w-full max-w-[700px] overflow-hidden border-hairline-strong">
      {/* Header bar */}
      <div className="h-12 border-b border-hairline flex items-center px-4 gap-4 bg-surface-card">
        {/* macOS traffic lights */}
        <div className="flex gap-2">
          <div className="w-3 h-3 rounded-full bg-[#ff5f56]" />
          <div className="w-3 h-3 rounded-full bg-[#ffbd2e]" />
          <div className="w-3 h-3 rounded-full bg-[#27c93f]" />
        </div>
        {/* Mock Search */}
        <div className="flex-1 flex items-center">
          <span className="text-mute text-body-lg">Review Pull Request...</span>
        </div>
        <Badge variant="pro">PRO</Badge>
      </div>
      
      {/* Body / List */}
      <div className="p-2 flex flex-col gap-1 bg-surface">
        <div className="px-2 py-1">
          <span className="text-mute text-caption-md">Suggested Actions</span>
        </div>
        
        <div className="flex items-center justify-between bg-surface-card rounded-sm px-3 py-2 cursor-pointer border border-hairline-soft">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-md bg-accent-blue-soft flex items-center justify-center">
              <span className="text-accent-blue text-body-lg">⚡</span>
            </div>
            <span className="text-ink text-body-md font-medium">Analyze Blast Radius</span>
          </div>
          <Badge variant="keycap">⏎</Badge>
        </div>

        <div className="flex items-center justify-between hover:bg-surface-card rounded-sm px-3 py-2 cursor-pointer transition-colors">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-md bg-accent-yellow-soft flex items-center justify-center">
              <span className="text-accent-yellow text-body-lg">🧠</span>
            </div>
            <span className="text-ink text-body-md">Request AI Verdict</span>
          </div>
          <Badge variant="keycap">⌘ V</Badge>
        </div>

        <div className="flex items-center justify-between hover:bg-surface-card rounded-sm px-3 py-2 cursor-pointer transition-colors">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-md bg-surface-elevated flex items-center justify-center">
              <span className="text-mute text-body-lg">📊</span>
            </div>
            <span className="text-ink text-body-md">View Dependency Graph</span>
          </div>
          <Badge variant="keycap">⌘ G</Badge>
        </div>
      </div>
      
      {/* Footer */}
      <div className="h-8 border-t border-hairline flex items-center justify-end px-3 gap-3 bg-surface text-mute text-caption-sm">
        <span>GitScribe v2.0</span>
        <div className="flex items-center gap-1">
          <Badge variant="keycap">⌘</Badge>
          <Badge variant="keycap">K</Badge>
          <span>Actions</span>
        </div>
      </div>
    </Card>
  );
}
