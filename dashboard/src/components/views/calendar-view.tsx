"use client";

import { useState, useEffect } from "react";
import {
  Send, Plus, ExternalLink, Loader2, CheckCircle2, AlertCircle,
  ChevronLeft, ChevronRight, Clock, Trash2, MessageCircle, X,
  Video, AtSign, Share2, Globe, Mail, Image as ImageIcon,
} from "lucide-react";
import { cn } from "@/lib/utils";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const POSTIZ_URL = "https://srv1317892.hstgr.cloud";

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

// ── Platform SVG logos ──────────────────────────────────────────

function PlatformLogo({ name, className }: { name: string; className?: string }) {
  const key = name.toLowerCase();
  if (key === "x" || key === "twitter") return <svg className={className} viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>;
  if (key === "instagram") return <svg className={className} viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>;
  if (key === "facebook") return <svg className={className} viewBox="0 0 24 24" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>;
  if (key === "linkedin") return <svg className={className} viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>;
  if (key === "reddit") return <svg className={className} viewBox="0 0 24 24" fill="currentColor"><path d="M12 0A12 12 0 000 12a12 12 0 0012 12 12 12 0 0012-12A12 12 0 0012 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 01-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 01.042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 014.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 01.14-.197.35.35 0 01.238-.042l2.906.617a1.214 1.214 0 011.108-.701z"/></svg>;
  if (key === "youtube") return <svg className={className} viewBox="0 0 24 24" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>;
  return <Globe className={className} />;
}

const platformColors: Record<string, string> = {
  instagram: "text-pink-500",
  twitter: "text-sky-500",
  x: "text-foreground",
  facebook: "text-blue-600",
  youtube: "text-red-500",
  reddit: "text-orange-500",
  linkedin: "text-blue-700",
};

const availableChannels = [
  { name: "X (Twitter)", key: "x" },
  { name: "Instagram", key: "instagram" },
  { name: "Facebook Page", key: "facebook" },
  { name: "LinkedIn", key: "linkedin" },
  { name: "Reddit", key: "reddit" },
  { name: "YouTube", key: "youtube" },
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
  const [mediaFiles, setMediaFiles] = useState<File[]>([]);

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
              <div className="flex items-center justify-between mt-2">
                {/* Media upload */}
                <div className="flex items-center gap-2">
                  <label className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-border text-[12px] text-muted-foreground hover:text-foreground hover:border-accent/30 cursor-pointer transition-all">
                    <ImageIcon className="h-3.5 w-3.5" />
                    {mediaFiles.length > 0 ? `${mediaFiles.length} file(s)` : "Add Media"}
                    <input
                      type="file"
                      accept="image/*,video/*"
                      multiple
                      className="hidden"
                      onChange={(e) => {
                        if (e.target.files) setMediaFiles(Array.from(e.target.files));
                      }}
                    />
                  </label>
                  {mediaFiles.length > 0 && (
                    <button
                      onClick={() => setMediaFiles([])}
                      className="text-[11px] text-muted-foreground hover:text-destructive transition-colors"
                    >
                      Clear
                    </button>
                  )}
                </div>
                <p className="text-[11px] text-muted-foreground">{content.length} characters</p>
              </div>
              {/* Media preview */}
              {mediaFiles.length > 0 && (
                <div className="flex gap-2 mt-2 flex-wrap">
                  {mediaFiles.map((file, i) => (
                    <div key={i} className="relative w-16 h-16 rounded-lg overflow-hidden border border-border">
                      {file.type.startsWith("image/") ? (
                        <img src={URL.createObjectURL(file)} alt="" className="w-full h-full object-cover" />
                      ) : (
                        <div className="w-full h-full bg-muted flex items-center justify-center">
                          <Video className="h-5 w-5 text-muted-foreground" />
                        </div>
                      )}
                      <button
                        onClick={() => setMediaFiles(prev => prev.filter((_, j) => j !== i))}
                        className="absolute top-0.5 right-0.5 w-4 h-4 rounded-full bg-black/50 text-white flex items-center justify-center text-[8px]"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Select Channels */}
            <div>
              <p className="text-[12px] font-medium text-muted-foreground mb-2">Post to</p>
              {channels.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {channels.map((ch) => {
                    const pColor = platformColors[ch.providerName?.toLowerCase()] || "text-foreground";
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
                        <PlatformLogo name={ch.providerName || "x"} className={cn("h-3.5 w-3.5", pColor)} />
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

function AddChannelModal({ onClose, onChannelAdded }: { onClose: () => void; onChannelAdded: () => void }) {
  return (
    <>
      <div className="fixed inset-0 z-50 bg-black/20 backdrop-blur-sm" onClick={onClose} />
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="glass-tooltip w-full max-w-[640px] rounded-2xl overflow-hidden shadow-2xl">
          <div className="flex items-center justify-between px-6 py-4 border-b border-border">
            <h3 className="text-[17px] font-semibold text-foreground" style={{ fontFamily: "var(--font-serif)" }}>
              Connect a Channel
            </h3>
            <button onClick={onClose} className="text-muted-foreground hover:text-foreground">
              <X className="h-4 w-4" />
            </button>
          </div>
          <p className="px-6 pt-4 text-[13px] text-muted-foreground">
            Select a platform to connect. You'll be taken to Postiz to authenticate — once done, come back and your channel will appear.
          </p>
          <div className="p-6 grid grid-cols-3 gap-3">
            {availableChannels.map((ch) => (
              <button
                key={ch.key}
                onClick={() => window.open(`${POSTIZ_URL}/launches`, "_blank", "noopener,noreferrer")}
                className="glass rounded-xl p-5 text-center hover:shadow-md transition-all group cursor-pointer block w-full"
              >
                <PlatformLogo name={ch.key} className={cn("h-7 w-7 mx-auto mb-2", platformColors[ch.key] || "text-foreground", "opacity-70 group-hover:opacity-100 transition-opacity")} />
                <p className="text-[13px] font-medium text-foreground">{ch.name}</p>
                <p className="text-[10px] text-muted-foreground mt-0.5">Connect</p>
              </button>
            ))}
          </div>
          <div className="px-6 py-4 border-t border-border flex items-center justify-between">
            <p className="text-[11px] text-muted-foreground">
              Channels connect via secure OAuth — your credentials are never stored in Blaze
            </p>
            <button
              onClick={onChannelAdded}
              className="text-[12px] font-medium text-accent hover:underline"
            >
              Done
            </button>
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
          const pColor = platformColors[ch.providerName?.toLowerCase()] || "text-foreground";
          return (
            <div key={ch.id} className={cn("flex items-center gap-2 glass-pill px-3 py-2 rounded-xl shrink-0")}>
              <PlatformLogo name={ch.providerName || "x"} className={cn("h-4 w-4", pColor)} />
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
      {showAddChannel && <AddChannelModal onClose={() => setShowAddChannel(false)} onChannelAdded={() => { setShowAddChannel(false); fetchData(); }} />}
    </div>
  );
}
