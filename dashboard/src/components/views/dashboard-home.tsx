"use client";

import { useState, useEffect } from "react";
import { ArrowRight, FileText, Loader2, PenTool, Send, Users, Zap } from "lucide-react";
import { useUIStore } from "@/stores/ui-store";
import { getHealth, getOutputs } from "@/lib/api";

function useFormattedDate() {
  const [date, setDate] = useState("");
  useEffect(() => {
    setDate(new Date().toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" }));
  }, []);
  return date;
}

const agents = [
  { id: "social", name: "Vortex", desc: "Social Media", svg: "/vortex.svg" },
  { id: "seo", name: "Draft", desc: "SEO Writer", svg: "/draft.svg" },
  { id: "community", name: "Rally", desc: "Community", svg: "/rally.svg" },
  { id: "research", name: "Freq", desc: "Research", svg: "/freq.svg" },
  { id: "email", name: "Pulse", desc: "Email", svg: "/pulse.svg" },
  { id: "dispatch", name: "Dispatch", desc: "Publisher", svg: "/dispatch.svg" },
];

export function DashboardHome() {
  const { setActiveAgent, userName } = useUIStore();
  const firstName = (userName || "there").split(" ")[0];
  const formattedDate = useFormattedDate();
  const [health, setHealth] = useState<any>(null);
  const [socialCount, setSocialCount] = useState(0);
  const [articleCount, setArticleCount] = useState(0);
  const [communityCount, setCommunityCount] = useState(0);
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [pipelineStatus, setPipelineStatus] = useState("");

  useEffect(() => {
    getHealth().then(setHealth).catch(() => {});
    getOutputs("social_media").then((d: any) => setSocialCount(d.count)).catch(() => {});
    getOutputs("articles").then((d: any) => setArticleCount(d.count)).catch(() => {});
    getOutputs("community").then((d: any) => setCommunityCount(d.count)).catch(() => {});
  }, []);

  const handleRunPipeline = async () => {
    setPipelineRunning(true);
    setPipelineStatus("Running all agents...");
    try {
      const { runPipeline } = await import("@/lib/api");
      const result = await runPipeline();
      setPipelineStatus(`Done — ${(result.tools_called || []).length} tools`);
      getOutputs("social_media").then((d: any) => setSocialCount(d.count)).catch(() => {});
      getOutputs("articles").then((d: any) => setArticleCount(d.count)).catch(() => {});
      getOutputs("community").then((d: any) => setCommunityCount(d.count)).catch(() => {});
      setTimeout(() => setPipelineStatus(""), 3000);
    } catch (e: any) {
      setPipelineStatus("Error — try again");
      setTimeout(() => setPipelineStatus(""), 3000);
    } finally {
      setPipelineRunning(false);
    }
  };

  return (
    <div className="mx-auto max-w-[960px] px-8 py-10 stagger-children">
      {/* Greeting */}
      <div className="mb-8">
        <h1 className="text-[36px] text-foreground leading-tight" style={{ fontFamily: "var(--font-serif)" }}>
          Hey {firstName}, what are we creating?
        </h1>
        <p className="mt-2 text-[14px] text-muted-foreground">{formattedDate}</p>
      </div>

      {/* Bento Grid */}
      <div className="grid grid-cols-3 gap-3 mb-8">
        {agents.map((agent) => (
          <button
            key={agent.id}
            type="button"
            onClick={() => setActiveAgent(agent.id)}
            className="group glass glow-accent rounded-2xl p-5 text-left transition-all duration-200 hover:shadow-lg"
          >
            <img
              src={agent.svg}
              alt={agent.name}
              className="h-7 w-7 mb-3 opacity-50 group-hover:opacity-80 transition-opacity"
              style={{ filter: "brightness(0) saturate(100%)" }}
            />
            <p className="text-[15px] font-semibold text-foreground">{agent.name}</p>
            <p className="text-[12px] text-muted-foreground mt-0.5">{agent.desc}</p>
          </button>
        ))}
      </div>

      {/* Publish + Stats row */}
      <div className="grid grid-cols-5 gap-3 mb-6">
        {[
          { label: "Vortex", value: socialCount },
          { label: "Draft", value: articleCount },
          { label: "Rally", value: communityCount },
        ].map((stat) => (
          <div key={stat.label} className="glass rounded-xl p-4">
            <p className="text-[11px] text-muted-foreground">{stat.label}</p>
            <p className="text-[24px] font-semibold text-foreground mt-1 tabular-nums">{stat.value}</p>
          </div>
        ))}
        <button
          type="button"
          onClick={() => setActiveAgent("calendar")}
          className="glass rounded-xl p-4 text-left hover:shadow-md transition-all group"
        >
          <Send className="h-4 w-4 text-muted-foreground/50 group-hover:text-accent mb-1 transition-colors" />
          <p className="text-[13px] font-medium text-foreground">Publish</p>
          <p className="text-[10px] text-muted-foreground">Schedule posts</p>
        </button>
        <button
          type="button"
          onClick={handleRunPipeline}
          disabled={pipelineRunning}
          className="rounded-xl accent-gradient p-4 flex flex-col items-center justify-center gap-1.5 hover:opacity-90 disabled:opacity-50 transition-all shadow-md shadow-accent/15"
          style={{ color: "#FFF" }}
        >
          {pipelineRunning ? <Loader2 className="h-5 w-5 animate-spin" /> : <Zap className="h-5 w-5" />}
          <span className="text-[11px] font-medium">{pipelineStatus || "Run All"}</span>
        </button>
      </div>
    </div>
  );
}
