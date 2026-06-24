import React from 'react';
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { CommandPaletteMockup } from "@/components/ui/CommandPaletteMockup";
import { Activity, ShieldAlert, GitMerge, FileCode2 } from "lucide-react";

export default function Home() {
  return (
    <main className="flex flex-col w-full pb-section overflow-hidden">
      
      {/* Hero Section */}
      <section className="relative w-full min-h-[800px] flex flex-col items-center pt-section">
        {/* Red Stripe Gradient Band */}
        <div className="absolute top-0 left-0 right-0 h-[600px] bg-canvas overflow-hidden pointer-events-none">
          <div className="absolute top-[-20%] left-[-10%] right-[-10%] h-[150%] bg-gradient-to-br from-hero-stripe-start to-hero-stripe-end opacity-15 transform -skew-y-[8deg]" />
          <div className="absolute top-[10%] left-[-10%] right-[-10%] h-[150%] bg-gradient-to-br from-hero-stripe-start to-hero-stripe-end opacity-10 transform -skew-y-[8deg]" />
          <div className="absolute top-[40%] left-[-10%] right-[-10%] h-[150%] bg-gradient-to-br from-hero-stripe-start to-hero-stripe-end opacity-5 transform -skew-y-[8deg]" />
        </div>

        {/* Hero Content */}
        <div className="relative z-10 flex flex-col items-center text-center px-6 max-w-[800px] mb-xl">
          <h1 className="text-display-xl text-ink mb-md leading-tight" style={{ fontFeatureSettings: '"calt", "kern", "ss02", "ss08"' }}>
            Review architecture, <br/>not just syntax.
          </h1>
          <p className="text-body-lg text-mute mb-lg max-w-[600px]">
            GitScribe acts as the intelligence layer between AI code generation and human code review. Understand blast radius and merge risks in seconds.
          </p>
          <div className="flex items-center gap-4">
            <a href="/dashboard">
              <Button variant="primary">Launch Dashboard</Button>
            </a>
            <Button variant="secondary">View Documentation</Button>
          </div>
        </div>

        {/* Command Palette Mockup */}
        <div className="relative z-10 w-full px-6 flex justify-center mt-xl">
          <CommandPaletteMockup />
        </div>
      </section>

      {/* Feature Section */}
      <section className="max-w-[1240px] mx-auto px-6 w-full mt-[120px] flex flex-col gap-xl" id="features">
        <div className="flex flex-col gap-xs mb-lg">
          <h2 className="text-display-lg text-ink">Intelligence Layer</h2>
          <p className="text-body-lg text-mute max-w-[600px]">Everything you need to understand large pull requests without reading thousands of lines.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-lg">
          
          <Card variant="featureElevated" className="flex flex-col">
            <div className="w-12 h-12 rounded-md bg-surface-card flex items-center justify-center mb-6">
              <Activity className="w-6 h-6 text-accent-blue" />
            </div>
            <h3 className="text-heading-xl text-ink mb-sm">Blast Radius</h3>
            <p className="text-body-md text-mute mb-lg flex-grow">
              Deterministic dependency graphs powered by Neo4j show exactly what upstream and downstream services are affected by a change.
            </p>
            <Button variant="tertiary" className="w-fit">View Graph →</Button>
          </Card>

          <Card variant="feature" className="flex flex-col">
            <div className="w-12 h-12 rounded-md bg-surface-card flex items-center justify-center mb-6">
              <ShieldAlert className="w-6 h-6 text-accent-yellow" />
            </div>
            <h3 className="text-heading-xl text-ink mb-sm">Critic Agent</h3>
            <p className="text-body-md text-mute mb-lg flex-grow">
              Adversarial AI validation reviews every line for security concerns, logic flaws, and architectural regressions before merge.
            </p>
            <Button variant="tertiary" className="w-fit">See Critic in action →</Button>
          </Card>

          <Card variant="featureElevated" className="flex flex-col">
            <div className="w-12 h-12 rounded-md bg-surface-card flex items-center justify-center mb-6">
              <GitMerge className="w-6 h-6 text-accent-green" />
            </div>
            <h3 className="text-heading-xl text-ink mb-sm">PR Verdicts</h3>
            <p className="text-body-md text-mute mb-lg flex-grow">
              Senior Engineer agents combine blast radius data with logic analysis to produce a final, graph-verified risk assessment.
            </p>
            <Button variant="tertiary" className="w-fit">Read Sample Verdict →</Button>
          </Card>

        </div>
      </section>

      {/* Integration Store Section */}
      <section className="max-w-[1240px] mx-auto px-6 w-full mt-section flex flex-col gap-xl">
        <div className="flex flex-col gap-xs mb-lg">
          <h2 className="text-display-lg text-ink">Works where you do</h2>
          <p className="text-body-lg text-mute max-w-[600px]">Install GitScribe directly into your version control system.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-lg">
          
          {/* GitHub Mock */}
          <Card variant="store" className="flex items-center gap-6">
            <div className="w-16 h-16 bg-surface-card rounded-md flex items-center justify-center shrink-0 border border-hairline-soft">
              <FileCode2 className="w-8 h-8 text-ink" />
            </div>
            <div className="flex flex-col gap-1 flex-grow">
              <span className="text-heading-md text-ink">GitHub Integration</span>
              <span className="text-caption-md text-mute">by GitScribe • 10k+ installs</span>
              <span className="text-body-sm text-body truncate">Automatic PR review hooks.</span>
            </div>
            <Button variant="install">Install</Button>
          </Card>

          {/* IDE Mock */}
          <Card variant="store" className="flex items-center gap-6">
            <div className="w-16 h-16 bg-surface-card rounded-md flex items-center justify-center shrink-0 border border-hairline-soft">
              <div className="w-8 h-8 rounded bg-accent-blue" />
            </div>
            <div className="flex flex-col gap-1 flex-grow">
              <span className="text-heading-md text-ink">VS Code Extension</span>
              <span className="text-caption-md text-mute">by GitScribe • 5k+ installs</span>
              <span className="text-body-sm text-body truncate">View architecture graphs locally.</span>
            </div>
            <Button variant="install">Install</Button>
          </Card>

        </div>
      </section>

    </main>
  );
}
