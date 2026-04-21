"use client";

import { useUIStore } from "@/stores/ui-store";
import { DashboardHome } from "@/components/views/dashboard-home";
import { AgentChat } from "@/components/chat/agent-chat";
import { CalendarView } from "@/components/views/calendar-view";

const agentConfig: Record<string, { name: string; description: string; color: string; icon?: string; suggestions: string[]; apiEndpoint: string }> = {
  social: {
    name: "Vortex",
    description: "Generate relatable social content across Instagram, YouTube, Facebook, WhatsApp, and Twitter for Apollo Cash",
    color: "#4256FF",
    icon: "/vortex.svg",
    apiEndpoint: "/api/social/generate",
    suggestions: [
      "Write a reel script about bike repair emergencies for gig workers",
      "Generate 5 Instagram carousel posts about salary delay problems",
      "Create a Twitter thread busting myths about personal loans",
    ],
  },
  seo: {
    name: "Draft",
    description: "Write blog articles targeting high-intent personal finance keywords in India for Apollo Cash",
    color: "#2C3AAE",
    icon: "/draft.svg",
    apiEndpoint: "/api/seo/article",
    suggestions: [
      "Write an article targeting 'instant personal loan app India'",
      "Create a guide on 'how to get a loan without CIBIL score'",
      "Generate a comparison article: borrowing from friends vs loan apps",
    ],
  },
  community: {
    name: "Rally",
    description: "Find relevant conversations and respond authentically across Reddit, Quora, Twitter for Apollo Cash",
    color: "#5A6FFF",
    icon: "/rally.svg",
    apiEndpoint: "/api/community/responses",
    suggestions: [
      "Generate responses for Reddit threads about emergency loans",
      "Write Quora answers about getting loans without credit history",
      "Create Twitter replies for people complaining about salary delays",
    ],
  },
  dispatch: {
    name: "Dispatch",
    description: "Post content to Instagram, Twitter, Facebook, Reddit — schedule or publish instantly",
    color: "#10B981",
    icon: "/dispatch.svg",
    apiEndpoint: "/api/chat",
    suggestions: [
      "What channels are connected right now?",
      "Connect my Twitter",
      "Post this on X: Just shipped something cool. More details soon!",
    ],
  },
  email: {
    name: "Pulse",
    description: "Write email campaigns, newsletters, and drip sequences for Apollo Cash users",
    color: "#E44D8A",
    icon: "/pulse.svg",
    apiEndpoint: "/api/chat",
    suggestions: [
      "Write a welcome email for new Apollo Cash users",
      "Create a 3-email drip sequence for gig workers",
      "Draft a monthly newsletter about smart borrowing",
    ],
  },
  research: {
    name: "Freq",
    description: "Analyze trends, audience sentiment, and adapt Apollo Cash content strategy based on engagement data",
    color: "#30D158",
    icon: "/freq.svg",
    apiEndpoint: "/api/research/trends",
    suggestions: [
      "Research trending topics for our target audience this month",
      "Analyze what gig workers are talking about online right now",
      "What content formats are performing best on Indian Instagram?",
    ],
  },
};

export function MainContent() {
  const { activeAgent } = useUIStore();

  if (!activeAgent) return <DashboardHome />;
  if (activeAgent === "calendar") return <CalendarView />;

  const config = agentConfig[activeAgent];
  if (config) return <AgentChat agent={activeAgent} config={config} />;

  return <DashboardHome />;
}
