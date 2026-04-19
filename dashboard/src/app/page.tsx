"use client";

import { Sidebar } from "@/components/layout/sidebar";
import { MainContent } from "@/components/main-content";
import { CoachMarks } from "@/components/onboarding";
import { cn } from "@/lib/utils";
import { useUIStore } from "@/stores/ui-store";

export default function Page() {
  const { sidebarExpanded, onboarded, setOnboarded } = useUIStore();

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
