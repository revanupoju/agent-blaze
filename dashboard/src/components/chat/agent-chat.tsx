"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { ArrowUp, Check, ChevronDown, Copy, Loader2, Sparkles } from "lucide-react";
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
  { id: "cerebras:llama3.1-8b", label: "Llama 3.1 8B", provider: "Cerebras", badge: "Fast" },
  { id: "cerebras:qwen-3-235b-a22b-instruct-2507", label: "Qwen 3 235B", provider: "Cerebras", badge: "Powerful" },
  { id: "ollama:llama3.1", label: "Llama 3.1", provider: "Ollama", badge: "Local" },
];

// ── Markdown renderer ──────────────────────────────────────────

function MarkdownContent({ content }: { content: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        h1: ({ children }) => <h1 className="text-[20px] font-bold text-foreground mt-6 mb-3" style={{ fontFamily: "var(--font-serif)" }}>{children}</h1>,
        h2: ({ children }) => <h2 className="text-[17px] font-bold text-foreground mt-6 mb-3" style={{ fontFamily: "var(--font-serif)" }}>{children}</h2>,
        h3: ({ children }) => <h3 className="text-[15px] font-semibold text-foreground mt-5 mb-2">{children}</h3>,
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

// ── Streaming message bubble ───────────────────────────────────

function StreamingBubble({ content, color }: { content: string; color: string }) {
  const { displayed, done } = useStreamingText(content, true, 15);

  return (
    <div className="glass rounded-2xl overflow-hidden">
      <div className="px-5 py-4">
        <MarkdownContent content={displayed} />
        {!done && <span className="inline-block w-1 h-4 bg-accent animate-pulse ml-0.5 -mb-0.5" />}
      </div>
      {done && (
        <div className="flex items-center justify-end px-3 py-2 border-t border-black/5">
          <CopyButton text={content} />
        </div>
      )}
    </div>
  );
}

// ── Main chat component ────────────────────────────────────────

export function AgentChat({ agent, config }: { agent: string; config: AgentConfig }) {
  const { activeThreadId, threads, createThread, updateThread } = useUIStore();

  const activeThread = threads.find((t) => t.id === activeThreadId && t.agent === agent);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [lang, setLang] = useState<"english" | "hinglish">("english");
  const [model, setModel] = useState("cerebras:llama3.1-8b");
  const [latestStreamId, setLatestStreamId] = useState<string | null>(null);
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
      const res = await fetch(`${API}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: chatHistory, agent, model }),
      });
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
        m.id === assistantId ? { ...m, content: `**Error:** ${err.message}\n\nMake sure the backend is running:\n\`python3 server.py\``, loading: false } : m
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
                        <div className="glass rounded-2xl overflow-hidden">
                          <div className="px-5 py-4">
                            <MarkdownContent content={msg.content} />
                          </div>
                          <div className="flex items-center justify-end px-3 py-2 border-t border-black/5">
                            <CopyButton text={msg.content} />
                          </div>
                        </div>
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
          <div className="flex items-end gap-2 rounded-2xl p-3 glass-input transition-colors duration-150">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={`Message ${config.name}...`}
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
