"use client";

import { useState, useEffect } from "react";
import {
  Send, Plus, ExternalLink, Loader2, CheckCircle2, AlertCircle,
  ChevronLeft, ChevronRight, Clock, Trash2, MessageCircle, X,
  Video, AtSign, Share2, Globe, Mail,
} from "lucide-react";
import { cn } from "@/lib/utils";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const POSTIZ_URL = "http://72.60.200.15:4007";

// ── Types ──────────────────────────────────────────────────────

interface Channel {
  id: string;
  name: string;
  type: string;
  identifier: string;
  providerName: string;
  picture?: string;
}

interface ScheduledPost {
  id: string;
  content: string;
  date: string;
  status: string;
  platforms: string[];
}

// ── Platform icons ─────────────────────────────────────────────

const platformIcons: Record<string, { icon: any; color: string; bg: string }> = {
  instagram: { icon: AtSign, color: "text-pink-500", bg: "bg-pink-500/10" },
  twitter: { icon: Share2, color: "text-sky-500", bg: "bg-sky-500/10" },
  x: { icon: Share2, color: "text-foreground", bg: "bg-foreground/5" },
  facebook: { icon: Globe, color: "text-blue-600", bg: "bg-blue-600/10" },
  youtube: { icon: Video, color: "text-red-500", bg: "bg-red-500/10" },
  reddit: { icon: MessageCircle, color: "text-orange-500", bg: "bg-orange-500/10" },
  linkedin: { icon: Mail, color: "text-blue-500", bg: "bg-blue-500/10" },
};

const availableChannels = [
  { name: "X (Share2)", key: "x", icon: Share2, color: "text-foreground" },
  { name: "AtSign", key: "instagram", icon: AtSign, color: "text-pink-500" },
  { name: "Globe Page", key: "facebook", icon: Globe, color: "text-blue-600" },
  { name: "LinkedIn", key: "linkedin", icon: Mail, color: "text-blue-500" },
  { name: "Reddit", key: "reddit", icon: MessageCircle, color: "text-orange-500" },
  { name: "YouTube", key: "youtube", icon: Video, color: "text-red-500" },
];

// ── Compose Modal ──────────────────────────────────────────────

function ComposeModal({
  channels,
  onClose,
  onPost,
}: {
  channels: Channel[];
  onClose: () => void;
  onPost: (content: string, platforms: string[], schedule: string) => void;
}) {
  const [content, setContent] = useState("");
  const [selectedChannels, setSelectedChannels] = useState<string[]>([]);
  const [scheduleDate, setScheduleDate] = useState("");
  const [scheduleTime, setScheduleTime] = useState("");
  const [posting, setPosting] = useState(false);

  const handlePost = async () => {
    if (!content.trim()) return;
    setPosting(true);
    const schedule = scheduleDate && scheduleTime ? `${scheduleDate}T${scheduleTime}:00Z` : "";
    await onPost(content, selectedChannels, schedule);
    setPosting(false);
    onClose();
  };

  return (
    <>
      <div className="fixed inset-0 z-50 bg-black/20 backdrop-blur-sm" onClick={onClose} />
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="glass-tooltip w-full max-w-[560px] rounded-2xl p-0 overflow-hidden shadow-2xl">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-border">
            <h3 className="text-[17px] font-semibold text-foreground" style={{ fontFamily: "var(--font-serif)" }}>
              Create Post
            </h3>
            <button onClick={onClose} className="text-muted-foreground hover:text-foreground">
              <X className="h-4 w-4" />
            </button>
          </div>

          <div className="p-6 space-y-5">
            {/* Content */}
            <div>
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Write your post content..."
                rows={5}
                className="w-full bg-background border border-border rounded-xl px-4 py-3 text-[14px] text-foreground placeholder:text-muted-foreground/40 focus:outline-none focus:border-accent/40 resize-none"
              />
              <p className="text-[11px] text-muted-foreground mt-1 text-right">{content.length} characters</p>
            </div>

            {/* Select Channels */}
            <div>
              <p className="text-[12px] font-medium text-muted-foreground mb-2">Post to</p>
              {channels.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {channels.map((ch) => {
                    const p = platformIcons[ch.providerName?.toLowerCase()] || platformIcons.x;
                    const selected = selectedChannels.includes(ch.id);
                    return (
                      <button
                        key={ch.id}
                        onClick={() => setSelectedChannels(prev =>
                          selected ? prev.filter(id => id !== ch.id) : [...prev, ch.id]
                        )}
                        className={cn(
                          "flex items-center gap-2 px-3 py-2 rounded-lg border text-[12px] transition-all",
                          selected
                            ? "border-accent bg-accent/8 text-foreground"
                            : "border-border text-muted-foreground hover:border-accent/30"
                        )}
                      >
                        <p.icon className={cn("h-3.5 w-3.5", p.color)} />
                        {ch.name || ch.identifier || ch.providerName}
                      </button>
                    );
                  })}
                </div>
              ) : (
                <a href={POSTIZ_URL} target="_blank" rel="noopener noreferrer"
                  className="block text-[12px] text-accent hover:underline">
                  No channels connected — click to add in Postiz
                </a>
              )}
            </div>

            {/* Schedule */}
            <div>
              <p className="text-[12px] font-medium text-muted-foreground mb-2">Schedule (optional)</p>
              <div className="flex gap-2">
                <input
                  type="date"
                  value={scheduleDate}
                  onChange={(e) => setScheduleDate(e.target.value)}
                  className="flex-1 bg-background border border-border rounded-lg px-3 py-2 text-[13px] text-foreground focus:outline-none focus:border-accent/40"
                />
                <input
                  type="time"
                  value={scheduleTime}
                  onChange={(e) => setScheduleTime(e.target.value)}
                  className="w-32 bg-background border border-border rounded-lg px-3 py-2 text-[13px] text-foreground focus:outline-none focus:border-accent/40"
                />
              </div>
              <p className="text-[11px] text-muted-foreground mt-1">Leave empty to publish immediately</p>
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-between px-6 py-4 border-t border-border">
            <button onClick={onClose} className="text-[13px] text-muted-foreground hover:text-foreground">
              Cancel
            </button>
            <button
              onClick={handlePost}
              disabled={!content.trim() || posting}
              className="flex items-center gap-2 accent-gradient text-[13px] font-medium px-5 py-2 rounded-lg disabled:opacity-50 hover:opacity-90 transition-all"
              style={{ color: "#FFF" }}
            >
              {posting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Send className="h-3.5 w-3.5" />}
              {scheduleDate ? "Schedule" : "Publish Now"}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

// ── Add Channel Modal ──────────────────────────────────────────

function AddChannelModal({ onClose }: { onClose: () => void }) {
  return (
    <>
      <div className="fixed inset-0 z-50 bg-black/20 backdrop-blur-sm" onClick={onClose} />
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="glass-tooltip w-full max-w-[640px] rounded-2xl overflow-hidden shadow-2xl">
          <div className="flex items-center justify-between px-6 py-4 border-b border-border">
            <h3 className="text-[17px] font-semibold text-foreground" style={{ fontFamily: "var(--font-serif)" }}>
              Add Channel
            </h3>
            <button onClick={onClose} className="text-muted-foreground hover:text-foreground">
              <X className="h-4 w-4" />
            </button>
          </div>
          <div className="p-6 grid grid-cols-3 gap-3">
            {availableChannels.map((ch) => (
              <a
                key={ch.key}
                href={`${POSTIZ_URL}/launches`}
                target="_blank"
                rel="noopener noreferrer"
                className="glass rounded-xl p-5 text-center hover:shadow-md transition-all group cursor-pointer"
              >
                <ch.icon className={cn("h-7 w-7 mx-auto mb-2", ch.color, "opacity-70 group-hover:opacity-100 transition-opacity")} />
                <p className="text-[13px] font-medium text-foreground">{ch.name}</p>
                <p className="text-[10px] text-muted-foreground mt-0.5">Connect</p>
              </a>
            ))}
          </div>
          <div className="px-6 py-3 border-t border-border text-center">
            <a href={POSTIZ_URL} target="_blank" rel="noopener noreferrer" className="text-[12px] text-accent hover:underline">
              View all integrations in Postiz →
            </a>
          </div>
        </div>
      </div>
    </>
  );
}

// ── Calendar Week View ─────────────────────────────────────────

function WeekCalendar({ posts }: { posts: ScheduledPost[] }) {
  const [weekOffset, setWeekOffset] = useState(0);

  const today = new Date();
  const startOfWeek = new Date(today);
  startOfWeek.setDate(today.getDate() - today.getDay() + 1 + weekOffset * 7);

  const days = Array.from({ length: 7 }, (_, i) => {
    const d = new Date(startOfWeek);
    d.setDate(startOfWeek.getDate() + i);
    return d;
  });

  const dayNames = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const isToday = (d: Date) => d.toDateString() === today.toDateString();

  const getPostsForDay = (d: Date) =>
    posts.filter((p) => {
      if (!p.date) return false;
      const pd = new Date(p.date);
      return pd.toDateString() === d.toDateString();
    });

  const formatRange = () => {
    const s = days[0];
    const e = days[6];
    return `${months[s.getMonth()]} ${s.getDate()} – ${months[e.getMonth()]} ${e.getDate()}, ${e.getFullYear()}`;
  };

  return (
    <div>
      {/* Week nav */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <button onClick={() => setWeekOffset(w => w - 1)} className="p-1.5 rounded-lg hover:bg-muted transition-colors">
            <ChevronLeft className="h-4 w-4 text-muted-foreground" />
          </button>
          <span className="text-[13px] font-medium text-foreground min-w-[200px] text-center">{formatRange()}</span>
          <button onClick={() => setWeekOffset(w => w + 1)} className="p-1.5 rounded-lg hover:bg-muted transition-colors">
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
          </button>
          <button onClick={() => setWeekOffset(0)} className="text-[11px] text-accent hover:underline ml-2">Today</button>
        </div>
      </div>

      {/* Week grid */}
      <div className="glass rounded-2xl overflow-hidden">
        <div className="grid grid-cols-7">
          {days.map((d, i) => (
            <div key={i} className={cn("border-r border-border last:border-r-0")}>
              {/* Day header */}
              <div className={cn("px-3 py-2.5 text-center border-b border-border", isToday(d) && "bg-accent/5")}>
                <p className="text-[11px] text-muted-foreground">{dayNames[i]}</p>
                <p className={cn("text-[15px] font-semibold", isToday(d) ? "text-accent" : "text-foreground")}>
                  {d.getDate()}
                </p>
              </div>
              {/* Posts */}
              <div className="min-h-[200px] p-2 space-y-1.5">
                {getPostsForDay(d).map((post) => (
                  <div key={post.id} className="rounded-lg bg-accent/5 border border-accent/10 p-2 text-[10px]">
                    <p className="text-foreground font-medium truncate">{post.content?.slice(0, 40)}</p>
                    <div className="flex items-center gap-1 mt-1 text-muted-foreground">
                      <Clock className="h-2.5 w-2.5" />
                      <span>{new Date(post.date).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── Main Publish View ──────────────────────────────────────────

export function CalendarView() {
  const [status, setStatus] = useState<any>(null);
  const [channels, setChannels] = useState<Channel[]>([]);
  const [posts, setPosts] = useState<ScheduledPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCompose, setShowCompose] = useState(false);
  const [showAddChannel, setShowAddChannel] = useState(false);
  const [tab, setTab] = useState<"calendar" | "posts">("calendar");

  const fetchData = () => {
    Promise.all([
      fetch(`${API}/api/postiz/status`).then(r => r.json()).catch(() => ({ connected: false })),
      fetch(`${API}/api/postiz/channels`).then(r => r.json()).catch(() => ({ channels: [] })),
      fetch(`${API}/api/postiz/posts`).then(r => r.json()).catch(() => ({ posts: [] })),
    ]).then(([s, c, p]) => {
      setStatus(s);
      setChannels(Array.isArray(c.channels) ? c.channels : []);
      setPosts(Array.isArray(p.posts) ? p.posts : []);
      setLoading(false);
    });
  };

  useEffect(() => { fetchData(); }, []);

  const handlePost = async (content: string, platforms: string[], schedule: string) => {
    try {
      await fetch(`${API}/api/postiz/post`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content, platforms, schedule }),
      });
      fetchData();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="mx-auto max-w-[1100px] px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-[26px] text-foreground" style={{ fontFamily: "var(--font-serif)" }}>Publish</h1>
          <p className="text-[13px] text-muted-foreground mt-0.5">Schedule and post content across all channels</p>
        </div>
        <div className="flex items-center gap-3">
          {status?.connected ? (
            <span className="flex items-center gap-1.5 text-[11px] text-green-600 bg-green-500/8 px-2.5 py-1 rounded-full">
              <CheckCircle2 className="h-3 w-3" /> Connected
            </span>
          ) : loading ? (
            <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
          ) : (
            <span className="flex items-center gap-1.5 text-[11px] text-red-500 bg-red-500/8 px-2.5 py-1 rounded-full">
              <AlertCircle className="h-3 w-3" /> Offline
            </span>
          )}
          <button
            onClick={() => setShowCompose(true)}
            className="flex items-center gap-2 accent-gradient px-4 py-2 rounded-lg text-[13px] font-medium hover:opacity-90 transition-all"
            style={{ color: "#FFF" }}
          >
            <Plus className="h-3.5 w-3.5" /> New Post
          </button>
        </div>
      </div>

      {/* Channels bar */}
      <div className="flex items-center gap-3 mb-6 overflow-x-auto pb-1">
        {channels.map((ch) => {
          const p = platformIcons[ch.providerName?.toLowerCase()] || platformIcons.x;
          return (
            <div key={ch.id} className={cn("flex items-center gap-2 glass-pill px-3 py-2 rounded-xl shrink-0")}>
              <p.icon className={cn("h-4 w-4", p.color)} />
              <span className="text-[12px] font-medium text-foreground">{ch.name || ch.identifier}</span>
            </div>
          );
        })}
        <button
          onClick={() => setShowAddChannel(true)}
          className="flex items-center gap-1.5 px-3 py-2 rounded-xl border border-dashed border-border text-[12px] text-muted-foreground hover:text-foreground hover:border-accent/30 transition-all shrink-0"
        >
          <Plus className="h-3 w-3" /> Add Channel
        </button>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-1 mb-6 border-b border-border">
        {[
          { id: "calendar" as const, label: "Calendar" },
          { id: "posts" as const, label: "Posts" },
        ].map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={cn(
              "px-4 py-2.5 text-[13px] font-medium border-b-2 -mb-px transition-colors",
              tab === t.id ? "border-accent text-foreground" : "border-transparent text-muted-foreground hover:text-foreground"
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Content */}
      {tab === "calendar" && <WeekCalendar posts={posts} />}

      {tab === "posts" && (
        <div className="space-y-2">
          {posts.length > 0 ? posts.map((post) => (
            <div key={post.id} className="glass rounded-xl p-4 flex items-start justify-between">
              <div className="flex-1 pr-4">
                <p className="text-[13px] text-foreground leading-relaxed">{post.content?.slice(0, 150)}{post.content?.length > 150 ? "..." : ""}</p>
                <div className="flex items-center gap-3 mt-2 text-[11px] text-muted-foreground">
                  <span className="flex items-center gap-1"><Clock className="h-3 w-3" />{post.date ? new Date(post.date).toLocaleString() : "—"}</span>
                  <span className={cn(
                    "px-1.5 py-0.5 rounded-full text-[10px]",
                    post.status === "published" ? "bg-green-500/10 text-green-600" : "bg-accent/10 text-accent"
                  )}>
                    {post.status || "scheduled"}
                  </span>
                </div>
              </div>
            </div>
          )) : (
            <div className="glass rounded-xl p-10 text-center">
              <Send className="h-8 w-8 mx-auto mb-3 text-muted-foreground/20" />
              <p className="text-[14px] font-medium text-foreground">No posts yet</p>
              <p className="text-[12px] text-muted-foreground mt-1">Generate content with an agent, then click Publish — or create a new post above.</p>
            </div>
          )}
        </div>
      )}

      {/* Modals */}
      {showCompose && <ComposeModal channels={channels} onClose={() => setShowCompose(false)} onPost={handlePost} />}
      {showAddChannel && <AddChannelModal onClose={() => setShowAddChannel(false)} />}
    </div>
  );
}
