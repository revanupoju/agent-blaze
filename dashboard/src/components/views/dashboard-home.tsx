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
  const { setActiveAgent } = useUIStore();
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

  const handleRunPipeline = async () => {
    setPipelineRunning(true);
    try {
      const { runPipeline } = await import("@/lib/api");
      await runPipeline();
      getOutputs("social_media").then((d: any) => setSocialCount(d.count)).catch(() => {});
      getOutputs("articles").then((d: any) => setArticleCount(d.count)).catch(() => {});
      getOutputs("community").then((d: any) => setCommunityCount(d.count)).catch(() => {});
    } catch (e) {
      console.error(e);
    } finally {
      setPipelineRunning(false);
    }
  };

  return (
    <div className="mx-auto max-w-[960px] px-8 py-10 stagger-children">
      {/* Greeting */}
      <div className="mb-10">
        <h1 className="text-[42px] text-foreground leading-[1.15]" style={{ fontFamily: "var(--font-serif)" }}>
          Hey Revnth, what are we creating today?
        </h1>
        <p className="mt-3 text-[16px] text-muted-foreground">
          {formattedDate}
        </p>
      </div>

      {/* Agent suggestion cards — like Goose */}
      <div className="space-y-2 mb-10 max-w-[640px] mx-auto">
        {[
          { id: "social", label: "Generate social media posts with Vortex", icon: PenTool },
          { id: "seo", label: "Write an SEO article with Draft", icon: FileText },
          { id: "community", label: "Create community responses with Rally", icon: Users },
          { id: "research", label: "Research trending topics with Freq", icon: Search },
          { id: "calendar", label: "Generate a weekly content calendar", icon: Calendar },
        ].map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => setActiveAgent(item.id)}
            className="w-full flex items-center gap-3.5 rounded-xl px-6 py-5 text-left text-[16px] text-foreground glass glow-accent hover:border-[var(--surface-border-prominent)] transition-all duration-200"
          >
            <item.icon className="h-4 w-4 text-muted-foreground/50 shrink-0" />
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
        >
          {pipelineRunning ? <Loader2 className="h-5 w-5 animate-spin" /> : <Zap className="h-5 w-5" />}
          <span className="text-[11px] font-medium">{pipelineRunning ? "Running..." : "Run All"}</span>
        </button>
      </div>
    </div>
  );
}

function Search(props: { className?: string }) {
  return <Sparkles {...props} />;
}
