"use client";

import { useState } from "react";
import { ArrowRight, ArrowUp, Layers, Play, Loader2 } from "lucide-react";

const traceLines = [
  { type: "sys", text: "Apollo Cash Marketing Agent v1.0" },
  { type: "blank" },
  { type: "input", text: '> "Generate 5 Instagram posts for gig workers about salary delays"' },
  { type: "blank" },
  { type: "step", label: "INTENT", text: "social media content, segment=gig_workers, salary theme" },
  { type: "step", label: "MEMORY", text: "loaded 3 prior posts, engagement data — avoid repetition" },
  { type: "step", label: "REASON", text: "need 5 posts, mix formats: 2 carousels + 1 reel + 1 meme + 1 whatsapp" },
  { type: "blank" },
  { type: "tool", text: "-> generate_social_posts(count=5, segment=gig_workers, themes=salary)" },
  { type: "result", text: "  OK 5 posts generated, saved to output/social_media/" },
  { type: "blank" },
  { type: "step", label: "VERIFY", text: "quality: relatable tone, no corporate speak, real scenarios" },
  { type: "step", label: "PERSIST", text: "saved to memory, updated content history" },
  { type: "blank" },
  { type: "done", text: "Done — 5 posts returned in 14.2s" },
];

const layers = [
  { n: "01", name: "Serving", desc: "FastAPI + Next.js", color: "border-l-accent" },
  { n: "02", name: "Orchestration", desc: "ReAct Loop", color: "border-l-status-info" },
  { n: "03", name: "Memory", desc: "Short + Long term", color: "border-l-[#A855F7]" },
  { n: "04", name: "Tools", desc: "14 callable tools", color: "border-l-status-live" },
  { n: "05", name: "LLM Core", desc: "Claude / GPT-4o", color: "border-l-status-pending" },
];

export function HarnessView() {
  const [goal, setGoal] = useState("Generate a full week of marketing content for all segments");
  const [running, setRunning] = useState(false);

  return (
    <div className="mx-auto max-w-[1440px] p-6 stagger-children">
      <div className="mb-6">
        <h1 className="text-[22px] font-extrabold tracking-tight text-foreground">Agent Harness</h1>
        <p className="mt-1 text-[12px] text-muted-foreground">Run the orchestrator — it plans, reasons, calls tools, and verifies output</p>
      </div>

      {/* Goal Input */}
      <div className="rounded-lg border border-border bg-card p-4 mb-4">
        <label className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider block mb-2">Goal</label>
        <div className="flex gap-2">
          <input
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            className="flex-1 bg-muted border border-border rounded-md px-3 py-2 text-[13px] text-foreground focus:outline-none focus:border-[var(--surface-border-prominent)]"
          />
          <button
            type="button"
            onClick={() => { setRunning(true); setTimeout(() => setRunning(false), 3000); }}
            disabled={running}
            className="flex items-center gap-2 rounded-md bg-accent text-primary-foreground px-4 py-2 text-[12px] font-medium transition-colors hover:bg-accent-hover disabled:opacity-50"
          >
            {running ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Play className="h-3.5 w-3.5" />}
            {running ? "Running..." : "Run"}
          </button>
        </div>
      </div>

      {/* Terminal Trace */}
      <div className="rounded-lg border border-border bg-[var(--surface-sunken)] overflow-hidden mb-6">
        <div className="px-4 py-2 bg-card border-b border-border flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-status-rejected" />
          <div className="w-2.5 h-2.5 rounded-full bg-status-pending" />
          <div className="w-2.5 h-2.5 rounded-full bg-status-live" />
          <span className="text-[10px] text-muted-foreground ml-2 font-mono">harness trace</span>
        </div>
        <div className="p-5 font-mono text-[12px] space-y-0.5">
          {traceLines.map((line, i) => {
            if (line.type === "blank") return <div key={i} className="h-2.5" />;
            if (line.type === "sys") return <p key={i} className="text-muted-foreground opacity-50">{line.text}</p>;
            if (line.type === "input") return <p key={i} className="text-foreground font-medium">{line.text}</p>;
            if (line.type === "step") return <p key={i}><span className="text-accent">[{line.label}]</span><span className="text-muted-foreground ml-2">{line.text}</span></p>;
            if (line.type === "tool") return <p key={i} className="text-status-info">{line.text}</p>;
            if (line.type === "result") return <p key={i} className="text-status-live">{line.text}</p>;
            if (line.type === "done") return <p key={i} className="text-foreground font-medium">{line.text}</p>;
            return null;
          })}
        </div>
      </div>

      {/* Architecture + Tools */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        <div className="rounded-lg border border-border bg-card p-5">
          <h2 className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider mb-3">Architecture Layers</h2>
          <div className="space-y-1.5">
            {layers.map((l) => (
              <div key={l.n} className={`border-l-2 ${l.color} rounded-md bg-muted px-4 py-2.5 flex items-center gap-3`}>
                <span className="text-[10px] font-mono text-muted-foreground">{l.n}</span>
                <div>
                  <p className="text-[12px] font-medium text-foreground">{l.name}</p>
                  <p className="text-[10px] text-muted-foreground">{l.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="rounded-lg border border-border bg-card p-5">
          <h2 className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider mb-3">Harness Loop</h2>
          <div className="flex flex-wrap items-center gap-1.5 mb-4">
            {["User Goal", "Intent", "Memory", "LLM Reasoning", "Tools", "Verify", "Loop"].map((s, i) => (
              <div key={s} className="flex items-center gap-1.5">
                <span className={`text-[10px] px-2 py-1 rounded-md border ${
                  s === "LLM Reasoning" ? "bg-accent-muted text-accent border-accent/20" : "bg-muted text-muted-foreground border-border"
                }`}>{s}</span>
                {i < 6 && <ArrowRight className="h-2.5 w-2.5 text-muted-foreground opacity-30" />}
              </div>
            ))}
          </div>
          <h2 className="text-[10px] font-medium text-muted-foreground uppercase tracking-wider mb-3 mt-4 pt-3 border-t border-border">14 Tools</h2>
          <div className="grid grid-cols-2 gap-1">
            {[
              "generate_social_posts", "generate_variations", "weekly_calendar",
              "generate_article", "keyword_analysis", "community_responses",
              "discover_threads", "research_trends", "audience_sentiment",
              "adapt_strategy", "list_segments", "list_keywords",
              "list_communities", "read_output",
            ].map((t) => (
              <div key={t} className="bg-muted rounded-md px-2.5 py-1.5 text-[10px] font-mono text-muted-foreground">{t}</div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
