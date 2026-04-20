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

function DispatchChannels({ refreshKey }: { refreshKey: number }) {
  const [channels, setChannels] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetch(`${API}/api/postiz/channels`)
      .then(r => r.json())
      .then(d => { setChannels(Array.isArray(d.channels) ? d.channels : []); setLoading(false); })
      .catch(() => setLoading(false));
  }, [refreshKey]);

  if (loading) return <div className="flex items-center gap-2 text-[12px] text-muted-foreground"><Loader2 className="h-3 w-3 animate-spin" /> Loading channels...</div>;

  if (channels.length === 0) {
    return (
      <div className="glass rounded-xl p-4 text-center">
        <p className="text-[13px] text-muted-foreground">No channels connected yet</p>
        <p className="text-[11px] text-muted-foreground/60 mt-1">Click "Add Channel" above to connect Instagram, Twitter, etc.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      {channels.map((ch: any, i: number) => (
        <div key={i} className="flex items-center gap-2 glass-pill px-3 py-1.5 rounded-lg">
          <CheckCircle2 className="h-3 w-3 text-green-500" />
          <span className="text-[12px] font-medium text-foreground">{ch.name || ch.providerName || "Channel"}</span>
        </div>
      ))}
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
                  <div className="flex items-center justify-between mb-3">
                    <p className="text-[12px] font-medium text-muted-foreground/60 uppercase tracking-wider">Connected Channels</p>
                    <button
                      type="button"
                      onClick={() => {
                        const popup = window.open("https://srv1317892.hstgr.cloud/auth/login", "postiz_connect", "width=900,height=750,scrollbars=yes");
                        const timer = setInterval(() => { if (popup?.closed) { clearInterval(timer); setChannelRefresh(r => r + 1); } }, 1000);
                      }}
                      className="flex items-center gap-1 text-[11px] text-accent hover:underline"
                    >
                      <span className="text-[11px]">+</span> Add Channel
                    </button>
                  </div>
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
