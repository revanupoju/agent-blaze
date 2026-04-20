"use client";

import { ExternalLink } from "lucide-react";

const POSTIZ_URL = "http://72.60.200.15:4007";

export function CalendarView() {
  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-border shrink-0">
        <div>
          <h1 className="text-[22px] text-foreground" style={{ fontFamily: "var(--font-serif)" }}>
            Content Calendar
          </h1>
          <p className="text-[13px] text-muted-foreground mt-0.5">
            Schedule, publish, and manage content across all channels — powered by Postiz
          </p>
        </div>
        <a
          href={POSTIZ_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 text-[12px] text-muted-foreground hover:text-foreground transition-colors"
        >
          Open in full view
          <ExternalLink className="h-3.5 w-3.5" />
        </a>
      </div>

      {/* Postiz iframe */}
      <div className="flex-1 relative">
        <iframe
          src={POSTIZ_URL}
          className="absolute inset-0 w-full h-full border-0"
          allow="clipboard-write"
          title="Postiz - Content Calendar & Publishing"
        />
      </div>
    </div>
  );
}
