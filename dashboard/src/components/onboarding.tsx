"use client";

import { useState, useEffect, useRef } from "react";
import { ArrowRight, X } from "lucide-react";

interface CoachStep {
  selector: string;
  title: string;
  description: string;
  position: "right" | "bottom" | "left";
}

const STEPS: CoachStep[] = [
  {
    selector: '[data-coach="social"]',
    title: "Vortex — Social Media",
    description: "Your social content creator. Chat with Vortex to generate Instagram carousels, reel scripts, memes, Twitter threads, and WhatsApp forwards. It asks what you need before creating.",
    position: "right",
  },
  {
    selector: '[data-coach="seo"]',
    title: "Draft — SEO Writer",
    description: "Your blog article writer. Draft helps you target high-intent keywords like 'instant loan app India' and writes full SEO-optimized articles with proper structure and FAQs.",
    position: "right",
  },
  {
    selector: '[data-coach="community"]',
    title: "Rally — Community",
    description: "Your community voice. Rally finds real conversations on Reddit, Quora, and Twitter about money problems — then crafts authentic, helpful responses that build trust.",
    position: "right",
  },
  {
    selector: '[data-coach="research"]',
    title: "Freq — Research",
    description: "Your trend spotter. Freq analyzes what your audience is talking about, tracks competitor strategies, and recommends content adjustments based on engagement data.",
    position: "right",
  },
  {
    selector: '[data-coach="calendar"]',
    title: "Publish",
    description: "Schedule and auto-publish content to Instagram, Twitter, Facebook, Reddit, and more — powered by Postiz, self-hosted on your own server.",
    position: "right",
  },
  {
    selector: '[data-coach="pipeline"]',
    title: "Run All Agents",
    description: "Launch Vortex, Draft, and Rally together — generate social posts, articles, and community responses in a single run.",
    position: "bottom",
  },
];

export function CoachMarks({ onComplete }: { onComplete: () => void }) {
  const [step, setStep] = useState(0);
  const [targetRect, setTargetRect] = useState<DOMRect | null>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const current = STEPS[step];
    if (!current) return;

    // Small delay to let DOM settle
    const timer = setTimeout(() => {
      const el = document.querySelector(current.selector);
      if (el) {
        const rect = el.getBoundingClientRect();
        setTargetRect(rect);
        el.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    }, 150);

    return () => clearTimeout(timer);
  }, [step]);

  if (step >= STEPS.length) return null;

  const current = STEPS[step];
  const isLast = step === STEPS.length - 1;

  // Calculate tooltip position — keep within viewport
  let tooltipStyle: React.CSSProperties = {};
  if (targetRect) {
    const tooltipH = 200;
    const tooltipW = 380;
    const pad = 16;

    if (current.position === "right") {
      let top = targetRect.top + targetRect.height / 2 - 50;
      // Clamp to viewport
      top = Math.max(pad, Math.min(top, window.innerHeight - tooltipH - pad));
      tooltipStyle = { top, left: targetRect.right + pad };
    } else if (current.position === "bottom") {
      const spaceBelow = window.innerHeight - targetRect.bottom;
      if (spaceBelow < tooltipH + pad) {
        // Not enough space below — show above
        tooltipStyle = {
          bottom: window.innerHeight - targetRect.top + 12,
          left: Math.max(pad, targetRect.left + targetRect.width / 2 - tooltipW / 2),
        };
      } else {
        tooltipStyle = {
          top: targetRect.bottom + 12,
          left: Math.max(pad, targetRect.left + targetRect.width / 2 - tooltipW / 2),
        };
      }
    } else {
      let top = targetRect.top + targetRect.height / 2 - 50;
      top = Math.max(pad, Math.min(top, window.innerHeight - tooltipH - pad));
      tooltipStyle = { top, right: window.innerWidth - targetRect.left + pad };
    }
  }

  return (
    <div className="fixed inset-0 z-[100]">
      {/* Backdrop — semi-transparent with cutout */}
      <div className="absolute inset-0 bg-black/50" onClick={onComplete} />

      {/* Highlight cutout */}
      {targetRect && (
        <div
          className="absolute rounded-lg ring-2 ring-accent z-[101]"
          style={{
            top: targetRect.top - 4,
            left: targetRect.left - 4,
            width: targetRect.width + 8,
            height: targetRect.height + 8,
            boxShadow: "0 0 0 9999px rgba(0,0,0,0.5)",
            background: "transparent",
          }}
        />
      )}

      {/* Tooltip */}
      {targetRect && (
        <div
          ref={tooltipRef}
          className="fixed z-[102] w-[380px] rounded-2xl p-6 glass-tooltip animate-fade-up"
          style={tooltipStyle}
        >
          {/* Close */}
          <button
            type="button"
            onClick={onComplete}
            className="absolute top-3 right-3 text-muted-foreground hover:text-foreground transition-colors"
          >
            <X className="h-3.5 w-3.5" />
          </button>

          {/* Content */}
          <div className="flex items-center gap-2 mb-3">
            <div className="h-2 w-2 rounded-full accent-gradient" />
            <h3 className="text-[22px] font-semibold text-foreground" style={{ fontFamily: "var(--font-serif)" }}>{current.title}</h3>
          </div>
          <p className="text-[13px] text-muted-foreground leading-relaxed mb-5">
            {current.description}
          </p>

          {/* Actions */}
          <div className="flex items-center justify-between">
            <span className="text-[13px] text-muted-foreground">{step + 1} / {STEPS.length}</span>
            <div className="flex gap-3 items-center">
              <button
                type="button"
                onClick={onComplete}
                className="px-3 py-2 text-[14px] text-muted-foreground hover:text-foreground transition-colors"
              >
                Skip
              </button>
              <button
                type="button"
                onClick={() => isLast ? onComplete() : setStep(step + 1)}
                className="flex items-center gap-2 px-5 py-2.5 rounded-lg accent-gradient text-[14px] font-medium hover:opacity-90 transition-opacity"
                style={{ color: "#FFFFFF" }}
              >
                {isLast ? "Got it" : "Next"}
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
