"use client";

import { useState } from "react";
import { ArrowRight, Flame, Loader2 } from "lucide-react";
import Image from "next/image";

export function LoginPage({ onLogin }: { onLogin: () => void }) {
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleDemo = () => {
    setLoading(true);
    setEmail("demo@apollofinvest.com");
    setPassword("••••••••");
    setTimeout(() => onLogin(), 1200);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => onLogin(), 800);
  };

  return (
    <div className="min-h-screen bg-background flex">
      {/* Left panel — branding */}
      <div className="hidden lg:flex flex-1 flex-col justify-between p-12 bg-[#0A0A1A] text-white relative overflow-hidden">
        {/* Gradient orbs */}
        <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] rounded-full bg-accent/10 blur-[120px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[400px] h-[400px] rounded-full bg-[#2C3AAE]/15 blur-[100px]" />

        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-2">
            <Image src="/blaze-logo.png" alt="Blaze" width={32} height={32} />
            <span className="text-[22px]" style={{ fontFamily: "var(--font-serif)" }}>Blaze</span>
          </div>
          <p className="text-white/40 text-[13px]">by Apollo Finvest</p>
        </div>

        <div className="relative z-10 max-w-md">
          <h1 className="text-[38px] leading-[1.15] mb-6" style={{ fontFamily: "var(--font-serif)" }}>
            AI marketing agents that create content
            <span className="text-white/40"> your audience actually relates to.</span>
          </h1>
          <div className="flex gap-8 text-[13px] text-white/50">
            <div>
              <p className="text-[24px] font-semibold text-white mb-0.5" style={{ fontFamily: "var(--font-serif)" }}>4</p>
              <p>AI Agents</p>
            </div>
            <div>
              <p className="text-[24px] font-semibold text-white mb-0.5" style={{ fontFamily: "var(--font-serif)" }}>14</p>
              <p>Tools</p>
            </div>
            <div>
              <p className="text-[24px] font-semibold text-white mb-0.5" style={{ fontFamily: "var(--font-serif)" }}>5</p>
              <p>Platforms</p>
            </div>
          </div>
        </div>

        <div className="relative z-10 text-[11px] text-white/25">
          Apollo Finvest Limited &middot; BSE Listed NBFC &middot; AI Agent Operator Assignment
        </div>
      </div>

      {/* Right panel — login form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-[380px]">
          {/* Mobile logo */}
          <div className="flex items-center gap-3 mb-10 lg:hidden">
            <Image src="/blaze-logo.png" alt="Blaze" width={28} height={28} />
            <span className="text-[20px]" style={{ fontFamily: "var(--font-serif)" }}>Blaze</span>
          </div>

          <h2 className="text-[28px] text-foreground mb-2" style={{ fontFamily: "var(--font-serif)" }}>
            Welcome back
          </h2>
          <p className="text-[14px] text-muted-foreground mb-8">
            Sign in to access the marketing dashboard
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-[12px] font-medium text-muted-foreground block mb-1.5">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@company.com"
                className="w-full bg-background border border-border rounded-xl px-4 py-3 text-[14px] text-foreground placeholder:text-muted-foreground/40 focus:outline-none focus:border-accent/40 transition-colors"
              />
            </div>
            <div>
              <label className="text-[12px] font-medium text-muted-foreground block mb-1.5">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-background border border-border rounded-xl px-4 py-3 text-[14px] text-foreground placeholder:text-muted-foreground/40 focus:outline-none focus:border-accent/40 transition-colors"
              />
            </div>
            <button
              type="submit"
              disabled={loading || !email || !password}
              className="w-full accent-gradient text-white rounded-xl px-4 py-3 text-[14px] font-medium hover:opacity-90 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
              style={{ color: "#FFFFFF" }}
            >
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Sign In"}
            </button>
          </form>

          <div className="flex items-center gap-3 my-6">
            <div className="flex-1 h-px bg-border" />
            <span className="text-[11px] text-muted-foreground">or</span>
            <div className="flex-1 h-px bg-border" />
          </div>

          {/* Demo login */}
          <button
            type="button"
            onClick={handleDemo}
            disabled={loading}
            className="w-full border border-border rounded-xl px-4 py-3 text-[14px] font-medium text-foreground hover:bg-muted transition-all flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <>
                <span className="text-[10px] accent-gradient text-white px-2 py-0.5 rounded-full" style={{ color: "#FFFFFF" }}>DEMO</span>
                Try as Apollo Finvest Assessor
                <ArrowRight className="h-3.5 w-3.5 text-muted-foreground" />
              </>
            )}
          </button>

          <p className="text-[11px] text-muted-foreground/50 text-center mt-8">
            Built by Revanth Anupoju &middot; AI Agent Operator Assignment
          </p>
        </div>
      </div>
    </div>
  );
}
