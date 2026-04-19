"use client";

import { useState } from "react";
import { Calendar, Clock, Loader2, Sparkles } from "lucide-react";
import { generateCalendar } from "@/lib/api";

const DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"] as const;
const DAY_SHORT: Record<string, string> = {
  monday: "Mon", tuesday: "Tue", wednesday: "Wed", thursday: "Thu",
  friday: "Fri", saturday: "Sat", sunday: "Sun",
};

const platformBadge: Record<string, { bg: string; text: string }> = {
  instagram: { bg: "bg-[#E1306C]/15", text: "text-[#E1306C]" },
  facebook: { bg: "bg-[#1877F2]/15", text: "text-[#1877F2]" },
  youtube: { bg: "bg-[#FF0000]/15", text: "text-[#FF0000]" },
  youtube_shorts: { bg: "bg-[#FF0000]/15", text: "text-[#FF0000]" },
  twitter: { bg: "bg-[#1DA1F2]/15", text: "text-[#1DA1F2]" },
  whatsapp: { bg: "bg-[#25D366]/15", text: "text-[#25D366]" },
  sharechat: { bg: "bg-[#FFD60A]/15", text: "text-[#FFD60A]" },
};

function PlatformTag({ platform }: { platform: string }) {
  const style = platformBadge[platform] || { bg: "bg-muted", text: "text-muted-foreground" };
  const label = platform.replace(/_/g, " ").replace("youtube shorts", "yt shorts");
  return (
    <span className={`text-[9px] font-medium px-1.5 py-0.5 rounded-full ${style.bg} ${style.text} capitalize`}>
      {label}
    </span>
  );
}

function PostCard({ post }: { post: any }) {
  const title = post.theme || post.title || post.content?.text?.slice(0, 40) || "Untitled";
  const format = (post.format || post.type || "post").replace(/_/g, " ");
  const time = post.scheduled_time || post.time || "—";
  const platform = post.platform || "instagram";

  return (
    <div className="rounded-lg glass-pill p-3 hover:shadow-md transition-all duration-150 group cursor-default">
      {/* Time + Platform */}
      <div className="flex items-center gap-2 mb-2">
        <div className="flex items-center gap-1 text-muted-foreground">
          <Clock className="h-3 w-3" />
          <span className="text-[11px] font-mono tabular-nums">{time}</span>
        </div>
        <PlatformTag platform={platform} />
      </div>
      {/* Title */}
      <p className="text-[13px] font-medium text-foreground leading-snug capitalize">{title}</p>
      {/* Format */}
      <p className="text-[11px] text-muted-foreground mt-1 capitalize">{format}</p>
    </div>
  );
}

export function CalendarView() {
  const [calendar, setCalendar] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    setLoading(true);
    setError("");
    try {
      const result = await generateCalendar();
      setCalendar(result.calendar);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const getDayPosts = (day: string): any[] => {
    if (!calendar?.calendar) return [];
    const dayData = calendar.calendar[day];
    return Array.isArray(dayData) ? dayData : [];
  };

  return (
    <div className="mx-auto max-w-[1440px] p-6">
      {/* Header */}
      <div className="flex items-end justify-between mb-8">
        <div>
          <h1 className="text-[22px] font-extrabold tracking-tight text-foreground">Content Calendar</h1>
          <p className="mt-1 text-[13px] text-muted-foreground">
            {calendar
              ? `Week of ${calendar.week_start || "—"} \u00B7 ${calendar.total_posts || 0} posts scheduled`
              : "Generate a weekly content calendar with optimized posting times"}
          </p>
        </div>
        <button
          type="button"
          onClick={handleGenerate}
          disabled={loading}
          className="flex items-center gap-2 rounded-lg accent-gradient text-white px-5 py-2.5 text-[13px] font-medium transition-all duration-150 hover:opacity-90 disabled:opacity-50 shadow-lg shadow-accent/20"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
          {loading ? "Generating..." : "Generate Week"}
        </button>
      </div>

      {error && (
        <div className="rounded-lg border border-destructive/30 bg-destructive/5 p-4 mb-6 text-[13px] text-destructive">
          {error}. Make sure the backend is running.
        </div>
      )}

      {/* Empty state */}
      {!calendar && !loading && (
        <div className="flex flex-col items-center justify-center min-h-[50vh] text-center">
          <div className="w-16 h-16 rounded-2xl bg-accent-muted flex items-center justify-center mb-5">
            <Calendar className="h-7 w-7 text-accent" />
          </div>
          <h3 className="text-[17px] font-semibold text-foreground mb-2">No calendar generated yet</h3>
          <p className="text-[13px] text-muted-foreground max-w-md leading-relaxed">
            Click &quot;Generate Week&quot; to create a 7-day content calendar with posts
            scheduled for optimal times across all platforms and audience segments.
          </p>
        </div>
      )}

      {/* Loading state */}
      {loading && (
        <div className="flex flex-col items-center justify-center min-h-[50vh]">
          <Loader2 className="h-10 w-10 text-accent animate-spin mb-5" />
          <p className="text-[14px] text-foreground font-medium">Generating weekly calendar...</p>
          <p className="text-[12px] text-muted-foreground mt-1">This may take 30–60 seconds</p>
        </div>
      )}

      {/* Calendar Grid */}
      {calendar && !loading && (
        <div className="space-y-4">
          <div className="rounded-xl border border-border bg-card overflow-hidden">
            <div className="grid grid-cols-7">
              {DAYS.map((day, idx) => {
                const posts = getDayPosts(day);
                const segment = calendar.audience_rotation?.[day];
                const isToday = false; // Could wire up real date check

                return (
                  <div
                    key={day}
                    className={`flex flex-col ${idx < 6 ? "border-r border-border" : ""}`}
                  >
                    {/* Day header */}
                    <div className={`px-4 py-3 text-center border-b border-border ${isToday ? "bg-accent-muted" : ""}`}>
                      <p className="text-[14px] font-bold text-foreground">{DAY_SHORT[day]}</p>
                      {segment && (
                        <p className="text-[10px] text-accent font-medium mt-0.5 capitalize">
                          {segment.replace(/_/g, " ")}
                        </p>
                      )}
                    </div>

                    {/* Posts */}
                    <div className="p-2 min-h-[280px] space-y-2 flex-1">
                      {posts.length > 0 ? (
                        posts.map((post: any, i: number) => (
                          <PostCard key={i} post={post} />
                        ))
                      ) : (
                        <div className="h-full flex items-center justify-center">
                          <span className="text-[11px] text-muted-foreground opacity-25">—</span>
                        </div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Themes strip */}
          {calendar.weekly_themes && calendar.weekly_themes.length > 0 && (
            <div className="flex items-center gap-2.5 flex-wrap px-1">
              <span className="text-[11px] font-medium text-muted-foreground">Themes:</span>
              {calendar.weekly_themes.map((t: string) => (
                <span
                  key={t}
                  className="text-[11px] font-medium bg-accent-muted text-accent px-3 py-1 rounded-full capitalize"
                >
                  {t}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
