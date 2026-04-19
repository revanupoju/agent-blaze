"use client";

import { useState, useEffect } from "react";
import {
  ArrowRight,
  Calendar,
  FileText,
  Loader2,
  PenTool,
  Sparkles,
  Users,
  Zap,
} from "lucide-react";
import { useUIStore } from "@/stores/ui-store";
import { getHealth, getOutputs } from "@/lib/api";

function useFormattedDate() {
  const [date, setDate] = useState("");
  useEffect(() => {
    setDate(new Date().toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" }));
  }, []);
  return date;
}

export function DashboardHome() {
  const { setActiveAgent, userName } = useUIStore();
  const firstName = (userName || "there").split(" ")[0];
  const formattedDate = useFormattedDate();
  const [health, setHealth] = useState<any>(null);
  const [socialCount, setSocialCount] = useState(0);
  const [articleCount, setArticleCount] = useState(0);
  const [communityCount, setCommunityCount] = useState(0);
  const [pipelineRunning, setPipelineRunning] = useState(false);

  useEffect(() => {
    getHealth().then(setHealth).catch(() => {});
    getOutputs("social_media").then((d: any) => setSocialCount(d.count)).catch(() => {});
    getOutputs("articles").then((d: any) => setArticleCount(d.count)).catch(() => {});
    getOutputs("community").then((d: any) => setCommunityCount(d.count)).catch(() => {});
  }, []);

  const [pipelineStatus, setPipelineStatus] = useState("");

  const handleRunPipeline = async () => {
    setPipelineRunning(true);
    setPipelineStatus("Starting all agents...");
    try {
      const { runPipeline } = await import("@/lib/api");
      setPipelineStatus("Running Vortex, Draft, Rally, Freq...");
      const result = await runPipeline();
      const tools = result.tools_called || [];
      setPipelineStatus(`Done — ${tools.length} tools executed`);
      // Refresh counts
      getOutputs("social_media").then((d: any) => setSocialCount(d.count)).catch(() => {});
      getOutputs("articles").then((d: any) => setArticleCount(d.count)).catch(() => {});
      getOutputs("community").then((d: any) => setCommunityCount(d.count)).catch(() => {});
      setTimeout(() => setPipelineStatus(""), 3000);
    } catch (e: any) {
      setPipelineStatus(e.name === "AbortError" ? "Timed out — try again" : "Error — try again");
      setTimeout(() => setPipelineStatus(""), 3000);
    } finally {
      setPipelineRunning(false);
    }
  };

  return (
    <div className="mx-auto max-w-[960px] px-8 py-10 stagger-children">
      {/* Greeting */}
      <div className="mb-10">
        <h1 className="text-[42px] text-foreground leading-[1.15]" style={{ fontFamily: "var(--font-serif)" }}>
          Hey {firstName}, what are we creating today?
        </h1>
        <p className="mt-3 text-[16px] text-muted-foreground">
          {formattedDate}
        </p>
      </div>

      {/* Agent suggestion cards */}
      <div className="space-y-2 mb-10 max-w-[640px] mx-auto">
        {[
          { id: "social", label: "Chat with Vortex — Social Media content", svg: "/vortex.svg", anim: "agent-icon-vortex" },
          { id: "seo", label: "Chat with Draft — SEO Articles & Blogs", svg: "/draft.svg", anim: "agent-icon-draft" },
          { id: "community", label: "Chat with Rally — Community Responses", svg: "/rally.svg", anim: "agent-icon-rally" },
          { id: "research", label: "Chat with Freq — Trends & Research", svg: "/freq.svg", anim: "agent-icon-freq" },
          { id: "calendar", label: "Content Calendar — Plan your week", svg: null, anim: "" },
        ].map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => setActiveAgent(item.id)}
            className="group w-full flex items-center gap-4 rounded-xl px-6 py-5 text-left text-[16px] text-foreground glass glow-accent hover:border-[var(--surface-border-prominent)] transition-all duration-200"
          >
            {item.svg ? (
              <img src={item.svg} alt="" className={`h-5 w-5 shrink-0 opacity-40 group-hover:opacity-70 transition-opacity ${item.anim}`} style={{ filter: "brightness(0) saturate(100%)" }} />
            ) : (
              <Calendar className="h-5 w-5 text-muted-foreground/40 group-hover:text-muted-foreground/70 shrink-0 transition-colors" />
            )}
            <span>{item.label}</span>
          </button>
        ))}
      </div>

      {/* Bottom row: stats + pipeline */}
      <div className="grid grid-cols-4 gap-3 max-w-[640px] mx-auto">
        {[
          { label: "Vortex", value: socialCount, icon: PenTool },
          { label: "Draft", value: articleCount, icon: FileText },
          { label: "Rally", value: communityCount, icon: Users },
        ].map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.label} className="rounded-xl p-4 glass">
              <div className="flex items-center gap-1.5 mb-2">
                <Icon className="h-3 w-3 text-muted-foreground/50" />
                <span className="text-[11px] text-muted-foreground">{stat.label}</span>
              </div>
              <p className="text-[28px] font-semibold text-foreground tabular-nums" style={{ fontFamily: "var(--font-sans)" }}>
                {stat.value}
              </p>
            </div>
          );
        })}
        <button
          type="button"
          onClick={handleRunPipeline}
          disabled={pipelineRunning}
          data-coach="pipeline"
          className="rounded-xl accent-gradient text-white p-4 flex flex-col items-center justify-center gap-1.5 hover:opacity-90 disabled:opacity-50 transition-all shadow-md shadow-accent/15"
          style={{ color: "#FFF" }}
        >
          {pipelineRunning ? <Loader2 className="h-5 w-5 animate-spin" /> : <Zap className="h-5 w-5" />}
          <span className="text-[11px] font-medium">
            {pipelineRunning ? "Running..." : pipelineStatus || "Run All"}
          </span>
        </button>
      </div>
      {pipelineStatus && (
        <div className="text-center mt-3 max-w-[640px] mx-auto animate-fade-up">
          <p className="text-[12px] text-muted-foreground">{pipelineStatus}</p>
          {pipelineStatus.includes("Done") && (
            <div className="flex items-center justify-center gap-3 mt-3">
              <button onClick={() => setActiveAgent("social")} className="text-[12px] text-accent hover:underline">View Vortex outputs</button>
              <span className="text-muted-foreground/30">·</span>
              <button onClick={() => setActiveAgent("seo")} className="text-[12px] text-accent hover:underline">View Draft outputs</button>
              <span className="text-muted-foreground/30">·</span>
              <button onClick={() => setActiveAgent("community")} className="text-[12px] text-accent hover:underline">View Rally outputs</button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function Search(props: { className?: string }) {
  return <Sparkles {...props} />;
}
