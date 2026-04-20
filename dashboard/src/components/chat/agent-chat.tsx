"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { ArrowUp, Check, CheckCircle2, ChevronDown, Copy, Image as ImageIcon, Loader2, Paperclip, Sparkles, Video } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { cn } from "@/lib/utils";
import { useUIStore } from "@/stores/ui-store";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  displayContent?: string; // For streaming animation
  loading?: boolean;
  streaming?: boolean;
}

interface AgentConfig {
  name: string;
  description: string;
  color: string;
  icon?: string;
  suggestions: string[];
  apiEndpoint: string;
}

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ── Agent icon (uses custom SVG if available) ──────────────────

function AgentIcon({ config, size = 20 }: { config: AgentConfig; size?: number }) {
  if (config.icon) {
    return <img src={config.icon} alt={config.name} style={{ width: size, height: size, filter: "brightness(0) saturate(100%)" }} />;
  }
  return <Sparkles style={{ width: size, height: size, color: config.color }} />;
}

const MODELS = [
  { id: "cerebras:qwen-3-235b-a22b-instruct-2507", label: "Qwen 3 235B", provider: "Cerebras", badge: "Recommended" },
  { id: "cerebras:llama3.1-8b", label: "Llama 3.1 8B", provider: "Cerebras", badge: "Fast" },
  { id: "ollama:llama3.1", label: "Llama 3.1", provider: "Ollama", badge: "Local" },
];

// ── Markdown renderer ──────────────────────────────────────────

function MarkdownContent({ content }: { content: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        h1: ({ children }) => <h1 className="text-[26px] font-bold text-foreground mt-8 mb-4" style={{ fontFamily: "var(--font-serif)" }}>{children}</h1>,
        h2: ({ children }) => <h2 className="text-[22px] font-bold text-foreground mt-7 mb-3" style={{ fontFamily: "var(--font-serif)" }}>{children}</h2>,
        h3: ({ children }) => <h3 className="text-[18px] font-semibold text-foreground mt-6 mb-2" style={{ fontFamily: "var(--font-serif)" }}>{children}</h3>,
        p: ({ children }) => <p className="text-[14px] leading-[1.85] text-foreground/80 mb-4 last:mb-0">{children}</p>,
        strong: ({ children }) => <strong className="font-semibold text-foreground">{children}</strong>,
        em: ({ children }) => <em className="italic text-foreground/65">{children}</em>,
        ul: ({ children }) => <ul className="list-disc list-outside pl-5 mb-4 space-y-2">{children}</ul>,
        ol: ({ children }) => <ol className="list-decimal list-outside pl-5 mb-4 space-y-2">{children}</ol>,
        li: ({ children }) => <li className="text-[14px] leading-[1.8] text-foreground/80">{children}</li>,
        blockquote: ({ children }) => <blockquote className="border-l-2 border-accent/20 pl-5 my-5 text-foreground/60 italic">{children}</blockquote>,
        code: ({ children, className }) => {
          const isBlock = className?.includes("language-");
          if (isBlock) {
            return <pre className="bg-foreground/[0.03] rounded-xl p-5 my-4 overflow-x-auto text-[12px] font-mono leading-relaxed">{children}</pre>;
          }
          return <code className="bg-foreground/[0.04] text-accent px-1.5 py-0.5 rounded-md text-[13px] font-mono">{children}</code>;
        },
        hr: () => <div className="my-6" />,
        a: ({ children, href }) => <a href={href} className="text-accent underline underline-offset-2 hover:text-accent-hover">{children}</a>,
        table: ({ children }) => <div className="overflow-x-auto my-4"><table className="w-full text-[13px] border-collapse">{children}</table></div>,
        thead: ({ children }) => <thead className="bg-foreground/[0.03]">{children}</thead>,
        th: ({ children }) => <th className="text-left px-3 py-2.5 font-semibold text-foreground border-b border-border">{children}</th>,
        td: ({ children }) => <td className="px-3 py-2.5 text-foreground/75 border-b border-border/30">{children}</td>,
      }}
    >
      {content}
    </ReactMarkdown>
  );
}

// ── Copy button ────────────────────────────────────────────────

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      type="button"
      onClick={() => { navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 2000); }}
      className="flex items-center gap-1 px-2 py-1 rounded-md text-[10px] text-muted-foreground hover:text-foreground hover:bg-foreground/5 transition-colors"
    >
      {copied ? <Check className="h-3 w-3 text-status-live" /> : <Copy className="h-3 w-3" />}
      {copied ? "Copied" : "Copy"}
    </button>
  );
}

// ── Model selector ─────────────────────────────────────────────

function ModelSelector({ model, onChange }: { model: string; onChange: (m: string) => void }) {
  const [open, setOpen] = useState(false);
  const current = MODELS.find((m) => m.id === model) || MODELS[0];

  return (
    <div className="relative">
      <button type="button" onClick={() => setOpen(!open)} className="flex items-center gap-1.5 text-[11px] text-muted-foreground hover:text-foreground transition-colors">
        <span>{current.label}</span>
        <span className="opacity-40">·</span>
        <span className="opacity-60">{current.provider}</span>
        <ChevronDown className="h-3 w-3" />
      </button>
      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="absolute bottom-full left-0 mb-2 z-50 w-[240px] rounded-xl glass-tooltip p-1.5 shadow-xl">
            {MODELS.map((m) => (
              <button key={m.id} type="button" onClick={() => { onChange(m.id); setOpen(false); }}
                className={cn("w-full flex items-center justify-between rounded-lg px-3 py-2 text-left transition-colors",
                  model === m.id ? "bg-accent/8 text-accent" : "text-foreground hover:bg-muted")}>
                <div>
                  <p className="text-[12px] font-medium">{m.label}</p>
                  <p className="text-[10px] text-muted-foreground">{m.provider}</p>
                </div>
                {m.badge && (
                  <span className={cn("text-[9px] font-medium px-1.5 py-0.5 rounded-full",
                    m.badge === "Fast" ? "bg-status-live/10 text-status-live"
                    : m.badge === "Powerful" ? "bg-accent/10 text-accent"
                    : "bg-muted text-muted-foreground")}>{m.badge}</span>
                )}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

// ── Streaming animation hook ───────────────────────────────────

function useStreamingText(fullText: string, active: boolean, speed: number = 12) {
  const [displayed, setDisplayed] = useState("");
  const [done, setDone] = useState(false);

  useEffect(() => {
    if (!active || !fullText) { setDisplayed(fullText); setDone(true); return; }
    setDisplayed("");
    setDone(false);
    let i = 0;
    const interval = setInterval(() => {
      // Stream by chunks of words for natural feel
      const nextSpace = fullText.indexOf(" ", i + 1);
      const end = nextSpace === -1 ? fullText.length : nextSpace + 1;
      setDisplayed(fullText.slice(0, end));
      i = end;
      if (i >= fullText.length) { setDone(true); clearInterval(interval); }
    }, speed);
    return () => clearInterval(interval);
  }, [fullText, active, speed]);

  return { displayed, done };
}

// ── Source extraction & panel ──────────────────────────────────

interface Source {
  num: number;
  title: string;
  url: string;
  domain: string;
}

function extractSources(content: string): { cleanContent: string; sources: Source[] } {
  const sources: Source[] = [];

  // Find the Sources section and extract links
  const sourcesMatch = content.match(/\n(?:\*\*)?Sources(?:\*\*)?[\s\n]+([\s\S]*?)$/i);
  let cleanContent = content;

  if (sourcesMatch) {
    cleanContent = content.slice(0, sourcesMatch.index || content.length).trim();
    const sourceBlock = sourcesMatch[1];
    const linkRegex = /\d+\.\s*\[([^\]]+)\]\(([^)]+)\)/g;
    let match;
    let num = 1;
    while ((match = linkRegex.exec(sourceBlock)) !== null) {
      const url = match[2];
      let domain = "web";
      try {
        domain = new URL(url).hostname.replace("www.", "").replace("reddit.com", "reddit").replace("trends.google.com", "google trends");
      } catch {}
      sources.push({ num: num++, title: match[1], url, domain });
    }
  }

  return { cleanContent, sources };
}

function SourcesPill({ sources }: { sources: Source[] }) {
  const [expanded, setExpanded] = useState(false);

  if (sources.length === 0) return null;

  return (
    <div className="mt-4">
      {/* Collapsed: horizontal scrollable strip */}
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full glass-pill text-[12px] font-medium text-foreground/60 hover:text-foreground transition-colors"
      >
        <span className="w-1.5 h-1.5 rounded-full bg-accent" />
        <span>{sources.length} sources</span>
        <ChevronDown className={cn("h-3 w-3 transition-transform", expanded && "rotate-180")} />
      </button>

      {/* Expanded: source cards grid inline */}
      {expanded && (
        <div className="mt-3 grid grid-cols-2 gap-2 animate-fade-up">
          {sources.map((s) => (
            <a
              key={s.num}
              href={s.url}
              target="_blank"
              rel="noopener noreferrer"
              className="block rounded-xl border border-border bg-background p-3 hover:bg-muted transition-colors group"
            >
              <div className="flex items-center gap-1.5 mb-1">
                <span className="w-1 h-1 rounded-full bg-accent shrink-0" />
                <span className="text-[10px] text-muted-foreground truncate">{s.domain}</span>
              </div>
              <p className="text-[12px] font-medium text-foreground group-hover:text-accent transition-colors leading-snug line-clamp-2">
                {s.title}
              </p>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}

// ── Streaming message bubble ───────────────────────────────────

function StreamingBubble({ content, color }: { content: string; color: string }) {
  const { displayed, done } = useStreamingText(content, true, 15);
  const { cleanContent, sources } = extractSources(content);
  const { cleanContent: displayedClean } = extractSources(displayed);

  return (
    <div className="glass rounded-2xl overflow-hidden">
      <div className="px-5 py-4">
        <MarkdownContent content={done ? cleanContent : displayedClean} />
        {!done && <span className="inline-block w-1 h-4 bg-accent animate-pulse ml-0.5 -mb-0.5" />}
        {done && sources.length > 0 && <SourcesPill sources={sources} />}
      </div>
      {done && (
        <div className="flex items-center justify-end px-3 py-2 border-t border-black/5">
          <CopyButton text={content} />
        </div>
      )}
    </div>
  );
}

function PublishButton({ content }: { content: string }) {
  const [status, setStatus] = useState<"idle" | "publishing" | "done">("idle");
  const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const handlePublish = async () => {
    setStatus("publishing");
    try {
      await fetch(`${API_URL}/api/publish`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ platform: "instagram", content: { text: content.slice(0, 500), caption: content.slice(0, 300) } }),
      });
      setStatus("done");
      setTimeout(() => setStatus("idle"), 3000);
    } catch {
      setStatus("idle");
    }
  };

  return (
    <button
      type="button"
      onClick={handlePublish}
      disabled={status !== "idle"}
      className="flex items-center gap-1 px-2 py-1 rounded-md text-[10px] text-muted-foreground hover:text-accent hover:bg-accent/5 transition-colors disabled:opacity-50"
    >
      {status === "publishing" ? (
        <><Loader2 className="h-3 w-3 animate-spin" /> Publishing...</>
      ) : status === "done" ? (
        <><Check className="h-3 w-3 text-green-500" /> Queued</>
      ) : (
        <><ArrowUp className="h-3 w-3" /> Publish</>
      )}
    </button>
  );
}

function StaticBubble({ content }: { content: string }) {
  const { cleanContent, sources } = extractSources(content);

  return (
    <div className="glass rounded-2xl overflow-hidden">
      <div className="px-5 py-4">
        <MarkdownContent content={cleanContent} />
        {sources.length > 0 && <SourcesPill sources={sources} />}
      </div>
      <div className="flex items-center justify-between px-3 py-2 border-t border-black/5">
        <PublishButton content={content} />
        <CopyButton text={content} />
      </div>
    </div>
  );
}

// ── Dispatch channels widget ───────────────────────────────────

const SOCIAL_PLATFORMS = [
  { id: "x", name: "X", color: "text-foreground", icon: (cn: string) => <svg className={cn} viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg> },
  { id: "instagram", name: "Instagram", color: "text-pink-500", icon: (cn: string) => <svg className={cn} viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg> },
  { id: "linkedin", name: "LinkedIn", color: "text-blue-700", icon: (cn: string) => <svg className={cn} viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg> },
  { id: "facebook", name: "Facebook", color: "text-blue-600", icon: (cn: string) => <svg className={cn} viewBox="0 0 24 24" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg> },
  { id: "reddit", name: "Reddit", color: "text-orange-500", icon: (cn: string) => <svg className={cn} viewBox="0 0 24 24" fill="currentColor"><path d="M12 0A12 12 0 000 12a12 12 0 0012 12 12 12 0 0012-12A12 12 0 0012 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 01-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 01.042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 014.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 01.14-.197.35.35 0 01.238-.042l2.906.617a1.214 1.214 0 011.108-.701z"/></svg> },
];

function DispatchChannels({ refreshKey }: { refreshKey: number }) {
  const [channels, setChannels] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    fetch(`${API}/api/postiz/channels`)
      .then(r => r.json())
      .then(d => { setChannels(Array.isArray(d.channels) ? d.channels : []); setLoading(false); })
      .catch(() => setLoading(false));
  }, [refreshKey]);

  const connectPlatform = async (platformId: string) => {
    setConnecting(platformId);
    try {
      const r = await fetch(`${API}/api/connect/${platformId}`);
      const data = await r.json();
      if (data.url) {
        // Redirect directly to OAuth (e.g. Twitter login)
        window.location.href = data.url;
      } else if (r.redirected) {
        window.location.href = r.url;
      }
    } catch {
      setConnecting(null);
    }
  };

  if (loading) return <div className="flex items-center gap-2 text-[12px] text-muted-foreground"><Loader2 className="h-3 w-3 animate-spin" /> Loading channels...</div>;

  // Show connected channels as pills
  const connectedIds = channels.map((ch: any) => (ch.providerIdentifier || ch.providerName || "").toLowerCase());

  return (
    <div className="space-y-3">
      {/* Connected channels */}
      {channels.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {channels.map((ch: any, i: number) => {
            const pid = (ch.identifier || ch.providerIdentifier || ch.providerName || "").toLowerCase();
            const platform = SOCIAL_PLATFORMS.find(p => pid.includes(p.id));
            return (
              <div key={i} className="flex items-center gap-2 glass-pill px-3 py-1.5 rounded-lg">
                {platform ? platform.icon(`h-3.5 w-3.5 ${platform.color}`) : <CheckCircle2 className="h-3 w-3 text-green-500" />}
                <span className="text-[12px] font-medium text-foreground">{ch.name || ch.providerName || "Channel"}</span>
                <CheckCircle2 className="h-3 w-3 text-green-500" />
              </div>
            );
          })}
        </div>
      )}
      {/* Platform buttons to connect */}
      <div className="flex flex-wrap gap-2">
        {SOCIAL_PLATFORMS.map((p) => {
          const isConnected = connectedIds.includes(p.id);
          if (isConnected) return null;
          return (
            <button
              key={p.id}
              onClick={() => connectPlatform(p.id)}
              disabled={connecting !== null}
              className="flex items-center gap-2 glass rounded-xl px-4 py-2.5 hover:shadow-md transition-all group cursor-pointer disabled:opacity-50"
            >
              {connecting === p.id ? (
                <Loader2 className="h-4 w-4 animate-spin text-accent" />
              ) : (
                p.icon(`h-4 w-4 ${p.color} opacity-70 group-hover:opacity-100 transition-opacity`)
              )}
              <span className="text-[12px] font-medium text-foreground">{p.name}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}

// ── Main chat component ────────────────────────────────────────

export function AgentChat({ agent, config }: { agent: string; config: AgentConfig }) {
  const { activeThreadId, threads, createThread, updateThread, pendingMessage, setActiveAgent } = useUIStore();

  const activeThread = threads.find((t) => t.id === activeThreadId && t.agent === agent);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [lang, setLang] = useState<"english" | "hinglish">("english");
  const [model, setModel] = useState("cerebras:qwen-3-235b-a22b-instruct-2507");
  const [latestStreamId, setLatestStreamId] = useState<string | null>(null);
  const [mediaFiles, setMediaFiles] = useState<File[]>([]);
  const [channelRefresh, setChannelRefresh] = useState(0);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (activeThread) {
      setMessages(activeThread.messages.map((m, i) => ({
        id: `restored-${i}`, role: m.role as "user" | "assistant", content: m.content,
      })));
      setLatestStreamId(null);
    } else {
      setMessages([]);
      setLatestStreamId(null);
    }
  }, [activeThreadId, agent]);

  // Auto-send pending message (from "View outputs" link)
  const pendingHandled = useRef(false);
  useEffect(() => {
    if (pendingMessage && !pendingHandled.current && messages.length === 0 && !loading) {
      pendingHandled.current = true;
      setTimeout(() => {
        send(pendingMessage);
        setActiveAgent(agent); // Clear the pending message
      }, 500);
    }
  }, [pendingMessage, messages.length, loading]);

  useEffect(() => {
    pendingHandled.current = false;
  }, [agent]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, latestStreamId]);

  const persistMessages = (msgs: Message[], threadId: string) => {
    updateThread(threadId, msgs.filter(m => !m.loading).map(m => ({ role: m.role, content: m.content })));
  };

  const send = async (text: string) => {
    if (!text.trim() || loading) return;

    const userMsg: Message = { id: crypto.randomUUID(), role: "user", content: text.trim() };
    const assistantId = crypto.randomUUID();
    const placeholder: Message = { id: assistantId, role: "assistant", content: "", loading: true };
    const newMessages = [...messages, userMsg, placeholder];
    setMessages(newMessages);
    setInput("");
    setLoading(true);

    let threadId = activeThreadId;
    if (!threadId || !threads.find(t => t.id === threadId && t.agent === agent)) {
      threadId = createThread(agent, text.trim());
    }

    try {
      const chatHistory = newMessages.filter(m => !m.loading).map(m => ({ role: m.role, content: m.content }));
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 120000); // 2 min timeout
      const res = await fetch(`${API}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: chatHistory, agent, model }),
        signal: controller.signal,
      });
      clearTimeout(timeout);
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data = await res.json();
      const content = data.response || "No response.";

      const finalMessages = newMessages.map(m =>
        m.id === assistantId ? { ...m, content, loading: false, streaming: true } : m
      );
      setMessages(finalMessages);
      setLatestStreamId(assistantId);
      persistMessages(finalMessages, threadId);
    } catch (err: any) {
      const errorMessages = newMessages.map(m =>
        m.id === assistantId ? { ...m, content: err.name === "AbortError"
          ? "**Timed out** — the agent is doing heavy processing (Reddit scraping + content generation + quality check). Try a simpler prompt or switch to **Llama 3.1 8B** for faster responses."
          : `**Error:** ${err.message}\n\nThis might be temporary — try again in a few seconds.`, loading: false } : m
      );
      setMessages(errorMessages);
      persistMessages(errorMessages, threadId);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(input); }
  };

  return (
    <div className="flex flex-col h-screen">
      <div ref={scrollRef} className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-3xl px-6 py-8">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center min-h-[65vh]">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl mb-5" style={{ background: `${config.color}10` }}>
                <AgentIcon config={config} size={28} />
              </div>
              <h2 className="text-[26px] text-foreground mb-2" style={{ fontFamily: "var(--font-serif)" }}>{config.name}</h2>
              <p className="text-[14px] text-muted-foreground mb-10 text-center max-w-md leading-relaxed">{config.description}</p>
              {/* Connected channels for Dispatch */}
              {agent === "dispatch" && (
                <div className="w-full max-w-xl mb-6">
                  <p className="text-[12px] font-medium text-muted-foreground/60 uppercase tracking-wider mb-3">Channels</p>
                  <DispatchChannels refreshKey={channelRefresh} />
                </div>
              )}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 w-full max-w-xl">
                {config.suggestions.map((s) => (
                  <button key={s} type="button" onClick={() => send(s)}
                    className="text-left rounded-xl p-4 text-[13px] text-muted-foreground hover:text-foreground glass glow-accent transition-all duration-200">
                    <AgentIcon config={config} size={14} />
                    {s}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((msg) => (
                <div key={msg.id} className={cn("flex gap-3 animate-fade-up", msg.role === "user" ? "justify-end" : "justify-start")}>
                  {msg.role === "assistant" && (
                    <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl mt-1" style={{ background: `${config.color}10` }}>
                      {msg.loading
                        ? <Loader2 className="h-4 w-4 animate-spin" style={{ color: config.color }} />
                        : <AgentIcon config={config} size={18} />}
                    </div>
                  )}
                  <div className={cn(
                    "text-[14px] leading-[1.8]",
                    msg.role === "user"
                      ? "bg-accent/8 text-foreground px-5 py-3 rounded-2xl max-w-[70%]"
                      : "max-w-[90%]",
                  )}>
                    {msg.loading ? (
                      <div className="flex items-center gap-3 text-muted-foreground py-3 px-2">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 rounded-full bg-accent/40 animate-bounce" style={{ animationDelay: "0ms" }} />
                          <div className="w-2 h-2 rounded-full bg-accent/40 animate-bounce" style={{ animationDelay: "150ms" }} />
                          <div className="w-2 h-2 rounded-full bg-accent/40 animate-bounce" style={{ animationDelay: "300ms" }} />
                        </div>
                        <span className="text-[13px]">Thinking...</span>
                      </div>
                    ) : msg.role === "assistant" ? (
                      msg.streaming && msg.id === latestStreamId ? (
                        <StreamingBubble content={msg.content} color={config.color} />
                      ) : (
                        <StaticBubble content={msg.content} />
                      )
                    ) : (
                      <span>{msg.content}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Input */}
      <div className="px-6 py-4">
        <div className="mx-auto max-w-3xl">
          {/* Media preview for Dispatch */}
          {agent === "dispatch" && mediaFiles.length > 0 && (
            <div className="flex gap-2 mb-2 flex-wrap mx-auto max-w-3xl">
              {mediaFiles.map((file, i) => (
                <div key={i} className="relative w-14 h-14 rounded-lg overflow-hidden border border-border glass">
                  {file.type.startsWith("image/") ? (
                    <img src={URL.createObjectURL(file)} alt="" className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-muted">
                      <Video className="h-4 w-4 text-muted-foreground" />
                    </div>
                  )}
                  <button
                    onClick={() => setMediaFiles(prev => prev.filter((_, j) => j !== i))}
                    className="absolute top-0.5 right-0.5 w-4 h-4 rounded-full bg-black/60 text-white flex items-center justify-center text-[8px]"
                  >×</button>
                </div>
              ))}
            </div>
          )}
          <div className="flex items-end gap-2 rounded-2xl p-3 glass-input transition-colors duration-150">
            {/* Media upload button for Dispatch */}
            {agent === "dispatch" && (
              <label className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-muted text-muted-foreground hover:text-foreground cursor-pointer transition-colors">
                <Paperclip className="h-4 w-4" />
                <input
                  type="file"
                  accept="image/*,video/*"
                  multiple
                  className="hidden"
                  onChange={(e) => { if (e.target.files) setMediaFiles(prev => [...prev, ...Array.from(e.target.files!)]); }}
                />
              </label>
            )}
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={agent === "dispatch" ? "Write your post or paste content to publish..." : `Message ${config.name}...`}
              rows={1}
              disabled={loading}
              className="flex-1 resize-none bg-transparent px-2 py-1.5 text-[14px] text-foreground placeholder:text-muted-foreground/60 focus:outline-none disabled:opacity-50"
              style={{ minHeight: 38, maxHeight: 140 }}
            />
            <button
              type="button"
              onClick={() => send(input)}
              disabled={!input.trim() || loading}
              className={cn(
                "flex h-9 w-9 shrink-0 items-center justify-center rounded-xl transition-all duration-150",
                loading ? "bg-foreground/10 text-muted-foreground"
                  : input.trim() ? "accent-gradient text-white shadow-md shadow-accent/20"
                  : "bg-muted text-muted-foreground",
              )}
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <ArrowUp className="h-4 w-4" />}
            </button>
          </div>
          <div className="mt-2 flex items-center justify-between px-1">
            <ModelSelector model={model} onChange={setModel} />
            <button
              type="button"
              onClick={() => setLang(lang === "english" ? "hinglish" : "english")}
              className="text-[11px] text-muted-foreground hover:text-foreground transition-colors"
            >
              {lang === "english" ? "English" : "Hinglish"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
