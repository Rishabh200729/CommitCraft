import React from 'react';
import { Button } from '../ui/Button';

export function Footer() {
  return (
    <footer className="bg-canvas border-t border-hairline pt-16 pb-8 px-6 md:px-12 mt-section">
      <div className="max-w-[1240px] mx-auto grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-8 mb-16">
        <div className="flex flex-col gap-4">
          <span className="text-on-dark text-body-sm-strong">Product</span>
          <a href="#" className="text-body text-body-sm hover:text-ink transition-colors">Features</a>
          <a href="#" className="text-body text-body-sm hover:text-ink transition-colors">Integrations</a>
          <a href="#" className="text-body text-body-sm hover:text-ink transition-colors">Pricing</a>
          <a href="#" className="text-body text-body-sm hover:text-ink transition-colors">Changelog</a>
        </div>
        <div className="flex flex-col gap-4">
          <span className="text-on-dark text-body-sm-strong">Intelligence</span>
          <a href="#" className="text-body text-body-sm hover:text-ink transition-colors">Blast Radius</a>
          <a href="#" className="text-body text-body-sm hover:text-ink transition-colors">Critic Agent</a>
          <a href="#" className="text-body text-body-sm hover:text-ink transition-colors">Graph Engine</a>
        </div>
        <div className="flex flex-col gap-4">
          <span className="text-on-dark text-body-sm-strong">Company</span>
          <a href="#" className="text-body text-body-sm hover:text-ink transition-colors">About</a>
          <a href="#" className="text-body text-body-sm hover:text-ink transition-colors">Blog</a>
          <a href="#" className="text-body text-body-sm hover:text-ink transition-colors">Careers</a>
        </div>
        <div className="flex flex-col gap-4">
          <span className="text-on-dark text-body-sm-strong">Resources</span>
          <a href="#" className="text-body text-body-sm hover:text-ink transition-colors">Documentation</a>
          <a href="#" className="text-body text-body-sm hover:text-ink transition-colors">API Reference</a>
          <a href="#" className="text-body text-body-sm hover:text-ink transition-colors">Community</a>
        </div>
      </div>
      
      <div className="max-w-[1240px] mx-auto border-t border-hairline-soft pt-8 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded bg-gradient-to-br from-hero-stripe-start to-hero-stripe-end grayscale opacity-50" />
          <span className="text-mute text-body-sm">© 2026 GitScribe Inc.</span>
        </div>
        
        <div className="flex flex-col sm:flex-row items-center gap-3">
          <span className="text-mute text-body-sm">Subscribe to our newsletter</span>
          <div className="flex items-center gap-2">
            <input 
              type="email" 
              placeholder="Email address" 
              className="bg-surface border border-hairline rounded-md px-3 py-1.5 text-body-sm outline-none focus:border-hairline-strong text-ink placeholder:text-mute"
            />
            <Button variant="primary">Subscribe</Button>
          </div>
        </div>
      </div>
    </footer>
  );
}
