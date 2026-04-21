"use client";

import { useEffect } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { MainContent } from "@/components/main-content";
import { CoachMarks } from "@/components/onboarding";
import { LoginPage } from "@/components/login";
import { cn } from "@/lib/utils";
import { useUIStore } from "@/stores/ui-store";

export default function Page() {
  const { sidebarExpanded, onboarded, setOnboarded, loggedIn, setActiveAgent } = useUIStore();

  // Handle ?agent=dispatch redirect after OAuth
  useEffect(() => {
    if (loggedIn && typeof window !== "undefined") {
      const params = new URLSearchParams(window.location.search);
      const agent = params.get("agent");
      if (agent) {
        setActiveAgent(agent);
        window.history.replaceState({}, "", "/");
      }
    }
  }, [loggedIn, setActiveAgent]);

  if (!loggedIn) {
    return <LoginPage />;
  }

  return (
    <div className="relative min-h-screen bg-background">
      <Sidebar />
      <main
        className={cn(
          "min-h-screen transition-all duration-300 ease-out",
          "ml-0",
          sidebarExpanded ? "lg:ml-[230px]" : "lg:ml-[64px]",
        )}
      >
        <MainContent />
      </main>
      {!onboarded && <CoachMarks onComplete={() => setOnboarded(true)} />}
    </div>
  );
}
