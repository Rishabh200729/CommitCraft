import React from 'react';
import { Button } from '../ui/Button';
import { HealthCheck } from '../ui/HealthCheck';

export function TopNav() {
  return (
    <header className="h-[56px] border-b border-hairline bg-canvas flex items-center justify-between px-6 sticky top-0 z-50">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-gradient-to-br from-hero-stripe-start to-hero-stripe-end" />
          <span className="text-ink font-medium text-body-strong tracking-wide">GitScribe</span>
        </div>
        <HealthCheck />
      </div>
      
      <nav className="hidden md:flex items-center gap-6">
        <a href="#features" className="text-on-dark text-body-sm-strong hover:text-ink transition-colors">Features</a>
        <a href="#ai" className="text-on-dark text-body-sm-strong hover:text-ink transition-colors">AI Analysis</a>
        <a href="#graph" className="text-on-dark text-body-sm-strong hover:text-ink transition-colors">Graph Engine</a>
        <a href="#changelog" className="text-on-dark text-body-sm-strong hover:text-ink transition-colors">Changelog</a>
      </nav>

      <div className="flex items-center gap-4">
        <a href="/login" className="text-on-dark text-body-sm-strong hidden sm:block hover:text-ink transition-colors">Sign in</a>
        <Button variant="primary">Install GitScribe</Button>
      </div>
    </header>
  );
}
