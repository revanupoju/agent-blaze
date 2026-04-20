"use client";

import { useState, useEffect } from "react";
import { ExternalLink, Send, Loader2, CheckCircle2, AlertCircle, Plus } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const POSTIZ_URL = "http://72.60.200.15:4007";

export function CalendarView() {
  const [status, setStatus] = useState<any>(null);
  const [channels, setChannels] = useState<any[]>([]);
  const [posts, setPosts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/postiz/status`).then(r => r.json()).catch(() => ({ connected: false })),
      fetch(`${API}/api/postiz/channels`).then(r => r.json()).catch(() => ({ channels: [] })),
      fetch(`${API}/api/postiz/posts`).then(r => r.json()).catch(() => ({ posts: [] })),
    ]).then(([s, c, p]) => {
      setStatus(s);
      setChannels(c.channels || []);
      setPosts(Array.isArray(p.posts) ? p.posts : []);
      setLoading(false);
    });
  }, []);

  return (
    <div className="mx-auto max-w-[960px] px-8 py-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-[28px] text-foreground" style={{ fontFamily: "var(--font-serif)" }}>
            Publish
          </h1>
          <p className="text-[14px] text-muted-foreground mt-1">
            Schedule and publish content across all social channels
          </p>
        </div>
        <div className="flex items-center gap-2">
          {status?.connected ? (
            <span className="flex items-center gap-1.5 text-[12px] text-green-600">
              <CheckCircle2 className="h-3.5 w-3.5" /> Postiz Connected
            </span>
          ) : loading ? (
            <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
          ) : (
            <span className="flex items-center gap-1.5 text-[12px] text-red-500">
              <AlertCircle className="h-3.5 w-3.5" /> Not Connected
            </span>
          )}
        </div>
      </div>

      {/* Open Postiz */}
      <a
        href={POSTIZ_URL}
        target="_blank"
        rel="noopener noreferrer"
        className="group block rounded-2xl glass glow-accent p-6 mb-6 hover:border-accent/20 transition-all"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-11 h-11 rounded-xl accent-gradient flex items-center justify-center" style={{ color: "#FFF" }}>
              <Send className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-[16px] font-semibold text-foreground">Open Publishing Dashboard</h2>
              <p className="text-[12px] text-muted-foreground mt-0.5">
                Calendar, scheduling, analytics, multi-channel posting — powered by Postiz
              </p>
            </div>
          </div>
          <ExternalLink className="h-4 w-4 text-muted-foreground group-hover:text-accent transition-colors" />
        </div>
      </a>

      {/* Connected Channels */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-[13px] font-medium text-muted-foreground/60 uppercase tracking-wider">Connected Channels</h3>
          <a href={POSTIZ_URL} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-[12px] text-accent hover:underline">
            <Plus className="h-3 w-3" /> Add Channel
          </a>
        </div>
        {channels.length > 0 ? (
          <div className="grid grid-cols-4 gap-3">
            {channels.map((ch: any, i: number) => (
              <div key={i} className="glass rounded-xl p-4 text-center">
                <p className="text-[13px] font-medium text-foreground">{ch.name || ch.providerName || "Channel"}</p>
                <p className="text-[10px] text-muted-foreground mt-0.5">{ch.type || ch.identifier || "Connected"}</p>
              </div>
            ))}
          </div>
        ) : (
          <a href={POSTIZ_URL} target="_blank" rel="noopener noreferrer" className="block glass rounded-xl p-8 text-center hover:shadow-md transition-all">
            <Send className="h-8 w-8 mx-auto mb-3 text-muted-foreground/30" />
            <p className="text-[14px] font-medium text-foreground">No channels connected yet</p>
            <p className="text-[12px] text-muted-foreground mt-1">Click here to connect Instagram, Twitter, Facebook, Reddit, and more</p>
          </a>
        )}
      </div>

      {/* Recent Posts */}
      <div className="mb-6">
        <h3 className="text-[13px] font-medium text-muted-foreground/60 uppercase tracking-wider mb-3">Scheduled Posts</h3>
        {posts.length > 0 ? (
          <div className="space-y-2">
            {posts.map((post: any, i: number) => (
              <div key={i} className="glass rounded-xl p-4 flex items-center justify-between">
                <div>
                  <p className="text-[13px] text-foreground">{post.content?.slice(0, 80) || "Post"}</p>
                  <p className="text-[11px] text-muted-foreground mt-0.5">{post.date || post.createdAt || ""}</p>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-accent/10 text-accent">{post.status || "scheduled"}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="glass rounded-xl p-6 text-center">
            <p className="text-[13px] text-muted-foreground">No posts scheduled yet. Generate content with an agent, then click Publish.</p>
          </div>
        )}
      </div>

      {/* How it works */}
      <div className="glass rounded-2xl p-6">
        <h3 className="text-[15px] font-semibold text-foreground mb-4" style={{ fontFamily: "var(--font-serif)" }}>How Publishing Works</h3>
        <div className="grid grid-cols-3 gap-6">
          {[
            { step: "1", title: "Generate", desc: "Chat with Vortex, Draft, Rally, or Pulse to create content" },
            { step: "2", title: "Publish", desc: "Click the Publish button on any response to send it to Postiz" },
            { step: "3", title: "Schedule & Post", desc: "Use the dashboard to schedule posts and auto-publish to all connected channels" },
          ].map((s) => (
            <div key={s.step} className="text-center">
              <div className="w-8 h-8 rounded-full accent-gradient mx-auto mb-3 flex items-center justify-center text-[13px] font-bold" style={{ color: "#FFF" }}>
                {s.step}
              </div>
              <p className="text-[14px] font-medium text-foreground">{s.title}</p>
              <p className="text-[12px] text-muted-foreground mt-1 leading-relaxed">{s.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
