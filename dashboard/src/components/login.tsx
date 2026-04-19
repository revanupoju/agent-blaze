"use client";

import { useState } from "react";
import { ArrowRight, Loader2 } from "lucide-react";
import Image from "next/image";
import { useUIStore } from "@/stores/ui-store";

export function LoginPage() {
  const { login } = useUIStore();
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleDemo = () => {
    setLoading(true);
    setTimeout(() => login("Demo User", "demo@apollofinvest.com", true), 1000);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;
    setLoading(true);
    const name = email.split("@")[0].replace(/[^a-zA-Z]/g, " ").trim();
    setTimeout(() => login(name || "User", email, false), 800);
  };

  return (
    <div className="min-h-screen bg-background flex">
      {/* Left panel */}
      <div className="hidden lg:flex flex-1 flex-col justify-between p-12 bg-[#0A0A1A] text-white relative overflow-hidden">
        <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] rounded-full bg-accent/10 blur-[120px]" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[400px] h-[400px] rounded-full bg-[#2C3AAE]/15 blur-[100px]" />

        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-3">
            <Image src="/blaze-logo.png" alt="Blaze" width={32} height={32} />
            <span className="text-[22px]" style={{ fontFamily: "var(--font-serif)" }}>Blaze</span>
          </div>
          <div className="flex items-center gap-2 ml-1">
            <Image src="/af-logo.png" alt="Apollo Finvest" width={18} height={18} />
            <p className="text-white/40 text-[12px]">by Apollo Finvest</p>
          </div>
        </div>

        <div className="relative z-10 max-w-md">
          <h1 className="text-[38px] leading-[1.15] mb-10" style={{ fontFamily: "var(--font-serif)" }}>
            AI marketing agents that create content
            <span className="text-white/40"> your audience actually relates to.</span>
          </h1>

          {/* Agent logos */}
          <div className="grid grid-cols-2 gap-4">
            {[
              { name: "Vortex", desc: "Social Media", icon: "/vortex.svg" },
              { name: "Draft", desc: "SEO Writer", icon: "/draft.svg" },
              { name: "Rally", desc: "Community", icon: "/rally.svg" },
              { name: "Freq", desc: "Research", icon: "/freq.svg" },
            ].map((agent) => (
              <div key={agent.name} className="flex items-center gap-3 bg-white/[0.04] rounded-xl px-4 py-3 border border-white/[0.06]">
                <img src={agent.icon} alt={agent.name} className="h-5 w-5 invert opacity-70" />
                <div>
                  <p className="text-[13px] font-medium text-white/90">{agent.name}</p>
                  <p className="text-[11px] text-white/35">{agent.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="relative z-10 text-[11px] text-white/20">
          Apollo Finvest Limited &middot; BSE Listed NBFC
        </div>
      </div>

      {/* Right panel */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-[380px]">
          <div className="flex items-center gap-3 mb-10 lg:hidden">
            <Image src="/blaze-logo.png" alt="Blaze" width={28} height={28} />
            <span className="text-[20px]" style={{ fontFamily: "var(--font-serif)" }}>Blaze</span>
          </div>

          <h2 className="text-[28px] text-foreground mb-2" style={{ fontFamily: "var(--font-serif)" }}>
            Welcome
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
              className="w-full accent-gradient rounded-xl px-4 py-3 text-[14px] font-medium hover:opacity-90 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
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
                Continue with Demo Access
                <ArrowRight className="h-3.5 w-3.5 text-muted-foreground" />
              </>
            )}
          </button>

          <p className="text-[11px] text-muted-foreground/50 text-center mt-8">
            Built by Revanth Anupoju for Apollo Finvest
          </p>
        </div>
      </div>
    </div>
  );
}
