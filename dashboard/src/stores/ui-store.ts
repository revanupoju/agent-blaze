import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface ChatThread {
  id: string;
  agent: string;
  title: string;
  messages: { role: string; content: string }[];
  createdAt: string;
}

interface UIState {
  sidebarExpanded: boolean;
  mobileMenuOpen: boolean;
  activeAgent: string | null;
  pendingMessage: string | null;
  onboarded: boolean;
  loggedIn: boolean;
  userName: string;
  userEmail: string;
  isDemo: boolean;
  threads: ChatThread[];
  activeThreadId: string | null;
  toggleSidebar: () => void;
  setMobileMenuOpen: (open: boolean) => void;
  setActiveAgent: (agent: string | null, pendingMessage?: string) => void;
  setOnboarded: (v: boolean) => void;
  login: (name: string, email: string, isDemo: boolean) => void;
  logout: () => void;
  createThread: (agent: string, firstMessage: string) => string;
  updateThread: (id: string, messages: { role: string; content: string }[]) => void;
  setActiveThread: (id: string | null) => void;
  deleteThread: (id: string) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set, get) => ({
      sidebarExpanded: true,
      mobileMenuOpen: false,
      activeAgent: null,
      pendingMessage: null,
      onboarded: false,
      loggedIn: false,
      userName: "",
      userEmail: "",
      isDemo: false,
      threads: [],
      activeThreadId: null,

      toggleSidebar: () => set((s) => ({ sidebarExpanded: !s.sidebarExpanded })),
      setMobileMenuOpen: (open) => set({ mobileMenuOpen: open }),
      setActiveAgent: (agent, pendingMessage) => set({ activeAgent: agent, activeThreadId: null, pendingMessage: pendingMessage || null }),
      setOnboarded: (v) => set({ onboarded: v }),

      login: (name, email, isDemo) => set({ loggedIn: true, userName: name, userEmail: email, isDemo, onboarded: false }),
      logout: () => set({ loggedIn: false, userName: "", userEmail: "", isDemo: false, activeAgent: null, activeThreadId: null, threads: [], onboarded: false }),

      createThread: (agent, firstMessage) => {
        const id = crypto.randomUUID().slice(0, 8);
        const title = firstMessage.length > 40 ? firstMessage.slice(0, 40) + "..." : firstMessage;
        const thread: ChatThread = { id, agent, title, messages: [], createdAt: new Date().toISOString() };
        set((s) => ({ threads: [thread, ...s.threads], activeThreadId: id }));
        return id;
      },

      updateThread: (id, messages) =>
        set((s) => ({ threads: s.threads.map((t) => t.id === id ? { ...t, messages } : t) })),

      setActiveThread: (id) => {
        const thread = get().threads.find((t) => t.id === id);
        if (thread) set({ activeThreadId: id, activeAgent: thread.agent });
        else set({ activeThreadId: id });
      },

      deleteThread: (id) =>
        set((s) => ({
          threads: s.threads.filter((t) => t.id !== id),
          activeThreadId: s.activeThreadId === id ? null : s.activeThreadId,
        })),
    }),
    {
      name: "blaze-store",
      partialize: (state) => ({
        loggedIn: state.loggedIn,
        userName: state.userName,
        userEmail: state.userEmail,
        isDemo: state.isDemo,
        onboarded: state.onboarded,
        threads: state.threads,
        sidebarExpanded: state.sidebarExpanded,
      }),
    }
  )
);
