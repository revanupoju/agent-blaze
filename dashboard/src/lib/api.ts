const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function req<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    ...opts,
    headers: { "Content-Type": "application/json", ...opts?.headers },
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

// Orchestrator
export const orchestrate = (goal: string) =>
  req<any>("/api/orchestrate", { method: "POST", body: JSON.stringify({ goal }) });

// Social
export const generateSocial = (params: { count?: number; audience_segment?: string; formats?: string; themes?: string }) =>
  req<any>("/api/social/generate", { method: "POST", body: JSON.stringify(params) });

export const generateCalendar = () =>
  req<any>("/api/social/calendar", { method: "POST" });

// SEO
export const generateArticle = (params: { keyword: string; language?: string; audience_segment?: string; article_type?: string }) =>
  req<any>("/api/seo/article", { method: "POST", body: JSON.stringify(params) });

export const runKeywordAnalysis = () =>
  req<any>("/api/seo/keywords", { method: "POST" });

// Community
export const generateCommunity = (params: { count?: number; platforms?: string }) =>
  req<any>("/api/community/responses", { method: "POST", body: JSON.stringify(params) });

export const discoverThreads = () =>
  req<any>("/api/community/discover", { method: "POST" });

// Research
export const researchTrends = () => req<any>("/api/research/trends", { method: "POST" });
export const researchSentiment = (seg: string) => req<any>(`/api/research/sentiment/${seg}`, { method: "POST" });
export const adaptStrategy = () => req<any>("/api/research/adapt", { method: "POST" });

// Data
export const getOutputs = (agent: string) => req<any>(`/api/outputs/${agent}`);
export const getHealth = () => req<any>("/api/health");
export const getMemory = () => req<any>("/api/memory");
export const getRuns = () => req<any>("/api/runs");

// Pipeline
export const runPipeline = () => req<any>("/api/pipeline/run", { method: "POST" });
