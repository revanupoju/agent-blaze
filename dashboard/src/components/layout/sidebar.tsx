"use client";

import {
  Calendar,
  FileText,
  Home,
  LogOut,
  Menu,
  PanelLeftClose,
  PanelLeftOpen,
  PenTool,
  Search,
  Users,
  X,
} from "lucide-react";
import Image from "next/image";
import { cn } from "@/lib/utils";
import { useUIStore } from "@/stores/ui-store";

const coreNav = [
  { label: "Dashboard", id: "home", icon: Home },
] as const;

function FreqIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 392 130" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M7.50195 122.5C7.50195 122.5 48.3127 7.5 58.8721 7.5C69.4316 7.5 106.532 113.13 115.665 113.13C124.797 113.13 179.307 7.5 193.291 7.5C207.275 7.5 223.542 87.858 233.245 88.4259C242.949 88.9938 313.155 7.5 325.997 7.5C338.84 7.5 384.502 96.0926 384.502 96.0926" stroke="currentColor" strokeWidth="15" strokeLinecap="round"/>
    </svg>
  );
}

function VortexIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 190 143" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M23.5257 20.4972C53.1024 0.595585 131.012 4.78132 160.589 24.683C191.921 45.7657 187.607 89.6472 160.589 113.572C127.025 143.294 59.6846 142.321 23.5257 113.572C1.49077 96.0526 2.836 71.655 23.5257 53.3211C49.246 30.5295 104.995 27.6863 133.547 48.6952C152.708 62.7941 149.432 84.5354 128.603 95.1773C92.5984 113.572 53.6582 87.247 53.6582 87.247" stroke="currentColor" strokeWidth="15" strokeLinecap="round"/>
    </svg>
  );
}

function RallyIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 174 152" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M156.329 123.837C163.221 94.9821 174.329 36.784 163.626 34.8332C150.248 32.3948 123.491 87.2603 122.275 101.891C121.058 116.522 119.842 22.6407 102.815 6.79068C85.7881 -9.05934 87.0044 89.6989 91.8692 101.891C96.7341 114.083 32.274 44.5864 9.16584 48.2441C-13.9423 51.9018 66.3277 155.537 111.328 145.783" stroke="currentColor" strokeWidth="10.1452" strokeLinecap="round"/>
    </svg>
  );
}

function DraftIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 137 109" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M15.3258 8.04069C46.9974 7.28035 70.4311 17.3653 78.1891 22.5027M8.40048 80.3893C53.5668 78.8926 86.8504 93.1195 97.8464 100.42M8.00073 45.133C70.0806 37.9763 114.158 55.6133 128.437 65.3264" stroke="currentColor" strokeWidth="16" strokeLinecap="round"/>
    </svg>
  );
}

function PulseIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 509 221" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M7.50004 112.135C7.50004 112.135 54.1663 64.0519 94.5534 54.2548C148.209 41.2388 186.757 116.441 183.294 153.667C179.831 190.893 143.471 194.356 120.096 190.893C96.7212 187.43 78.9738 158.733 87.1982 126.397C95.4226 94.0604 150.47 33.2786 227.236 39.4358C304.002 45.593 341.061 87.436 311.135 130.429C300.175 146.175 285.901 154.17 270.992 158.733C256.083 163.296 225.233 155.062 227.745 123.741C230.258 92.419 294.52 39.933 349.46 49.2391C398.665 57.5738 444.858 95.0781 441.766 133.63C438.674 172.182 402.247 169.26 394.42 168.632C386.593 168.005 365.461 163.277 363.516 134.631C361.572 105.984 383.619 16.2109 501.348 40.5072" stroke="currentColor" strokeWidth="15" strokeLinecap="round"/>
    </svg>
  );
}

const agentNav = [
  { label: "Vortex", id: "social", icon: VortexIcon },
  { label: "Draft", id: "seo", icon: DraftIcon },
  { label: "Rally", id: "community", icon: RallyIcon },
  { label: "Freq", id: "research", icon: FreqIcon },
  { label: "Pulse", id: "email", icon: PulseIcon },
] as const;

const workspaceNav = [
  { label: "Content Calendar", id: "calendar", icon: Calendar },
] as const;

const allNav = [...coreNav, ...agentNav, ...workspaceNav];

function NavItem({
  icon: Icon,
  label,
  isActive,
  collapsed,
  onClick,
}: {
  icon: React.ComponentType<{ className?: string }>;
  label: string;
  isActive: boolean;
  collapsed: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      title={collapsed ? label : undefined}
      className={cn(
        "w-full flex items-center rounded-lg transition-all duration-150",
        collapsed ? "justify-center h-10 w-10 mx-auto" : "gap-2.5 px-2.5 py-2 min-h-[36px]",
        isActive
          ? "bg-accent/8 text-accent font-medium"
          : "text-muted-foreground hover:bg-muted hover:text-foreground",
      )}
    >
      <Icon className={cn("h-[18px] w-[18px] shrink-0", isActive ? "text-accent" : "opacity-60")} />
      {!collapsed && <span className="text-[13px] truncate">{label}</span>}
    </button>
  );
}

function SidebarInner({ collapsed, onNavigate }: { collapsed: boolean; onNavigate?: () => void }) {
  const { activeAgent, setActiveAgent, toggleSidebar, threads, activeThreadId, setActiveThread, deleteThread, userName, logout } = useUIStore();
  const current = activeAgent || "home";
  const initial = (userName || "D")[0].toUpperCase();

  const navigate = (id: string) => {
    setActiveAgent(id === "home" ? null : id);
    onNavigate?.();
  };

  return (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className={cn("flex items-center pt-4 pb-3", collapsed ? "justify-center px-2" : "px-4")}>
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate("home")}>
          <Image src="/blaze-logo.png" alt="Blaze" width={36} height={36} className="shrink-0" />
          {!collapsed && (
            <span className="text-[24px] tracking-tight text-foreground" style={{ fontFamily: "var(--font-serif)" }}>
              Blaze
            </span>
          )}
        </div>
      </div>

      {/* Nav */}
      <nav className={cn("flex-1 overflow-y-auto pt-2 pb-2", collapsed ? "px-2" : "px-2.5")}>
        {/* Core */}
        <div className="mb-2" data-coach="dashboard">
          {coreNav.map((item) => (
            <NavItem key={item.id} icon={item.icon} label={item.label} isActive={current === item.id} collapsed={collapsed} onClick={() => navigate(item.id)} />
          ))}
        </div>

        {/* Agents */}
        <div className="mb-2">
          {!collapsed && <p className="px-2.5 py-2 text-[10px] font-semibold text-muted-foreground/50 uppercase tracking-[0.12em]">Agents</p>}
          {collapsed && <div className="w-5 h-px bg-border mx-auto my-2" />}
          <div data-coach="social">
            <NavItem icon={VortexIcon} label="Vortex" isActive={current === "social"} collapsed={collapsed} onClick={() => navigate("social")} />
          </div>
          <div data-coach="seo">
            <NavItem icon={DraftIcon} label="Draft" isActive={current === "seo"} collapsed={collapsed} onClick={() => navigate("seo")} />
          </div>
          <div data-coach="community">
            <NavItem icon={RallyIcon} label="Rally" isActive={current === "community"} collapsed={collapsed} onClick={() => navigate("community")} />
          </div>
          <div data-coach="research">
            <NavItem icon={FreqIcon} label="Freq" isActive={current === "research"} collapsed={collapsed} onClick={() => navigate("research")} />
          </div>
          <div data-coach="email">
            <NavItem icon={PulseIcon} label="Pulse" isActive={current === "email"} collapsed={collapsed} onClick={() => navigate("email")} />
          </div>
        </div>

        {/* Workspace */}
        <div className="mb-2">
          {!collapsed && <p className="px-2.5 py-2 text-[10px] font-semibold text-muted-foreground/50 uppercase tracking-[0.12em]">Workspace</p>}
          {collapsed && <div className="w-5 h-px bg-border mx-auto my-2" />}
          <div data-coach="calendar">
            <NavItem icon={Calendar} label="Content Calendar" isActive={current === "calendar"} collapsed={collapsed} onClick={() => navigate("calendar")} />
          </div>
        </div>

        {/* Recent chats */}
        {!collapsed && threads.length > 0 && (
          <div className="mb-2">
            <p className="px-2.5 py-2 text-[10px] font-semibold text-muted-foreground/50 uppercase tracking-[0.12em]">Recent Chats</p>
            <div className="space-y-0.5">
              {threads.slice(0, 8).map((thread) => {
                const agentIcon: Record<string, string> = { social: "✦", seo: "◆", community: "●", research: "◎" };
                return (
                  <button
                    key={thread.id}
                    type="button"
                    onClick={() => { setActiveThread(thread.id); onNavigate?.(); }}
                    className={cn(
                      "w-full flex items-center gap-2 rounded-lg px-2.5 py-1.5 text-[12px] transition-all duration-150 group",
                      activeThreadId === thread.id
                        ? "bg-accent/8 text-accent"
                        : "text-muted-foreground hover:bg-muted hover:text-foreground",
                    )}
                  >
                    <span className="text-[9px] opacity-50 shrink-0">{agentIcon[thread.agent] || "○"}</span>
                    <span className="truncate flex-1 text-left">{thread.title}</span>
                    <button
                      type="button"
                      onClick={(e) => { e.stopPropagation(); deleteThread(thread.id); }}
                      className="opacity-0 group-hover:opacity-50 hover:!opacity-100 text-[10px] shrink-0 transition-opacity"
                    >
                      ×
                    </button>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </nav>

      {/* Footer */}
      <div className={cn("border-t border-border py-3", collapsed ? "px-2" : "px-3")}>
        {/* User */}
        {!collapsed && (
          <div className="flex items-center gap-2.5 rounded-lg px-2.5 py-2">
            <div className="flex h-6 w-6 items-center justify-center rounded-full accent-gradient text-[10px] font-semibold text-white shrink-0" style={{ color: "#FFF" }}>{initial}</div>
            <span className="text-[12px] font-medium text-muted-foreground flex-1">{userName || "User"}</span>
            <button type="button" onClick={logout} title="Sign out" className="h-6 w-6 flex items-center justify-center rounded-md text-muted-foreground/40 hover:text-foreground hover:bg-muted transition-colors">
              <LogOut className="h-3 w-3" />
            </button>
          </div>
        )}

        {/* Collapse toggle */}
        <button
          type="button"
          onClick={toggleSidebar}
          className={cn(
            "mt-1 flex items-center rounded-lg text-muted-foreground/50 hover:bg-muted hover:text-muted-foreground transition-all duration-150",
            collapsed ? "justify-center h-10 w-10 mx-auto" : "gap-2.5 w-full px-2.5 py-2 text-[12px]",
          )}
        >
          {collapsed ? <PanelLeftOpen className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
          {!collapsed && <span>Collapse</span>}
        </button>
      </div>
    </div>
  );
}

export function Sidebar() {
  const { sidebarExpanded, mobileMenuOpen, setMobileMenuOpen } = useUIStore();

  return (
    <>
      {/* Mobile hamburger */}
      <button
        type="button"
        onClick={() => setMobileMenuOpen(true)}
        className="fixed left-4 top-4 z-50 flex h-10 w-10 items-center justify-center rounded-xl glass text-muted-foreground lg:hidden"
      >
        <Menu className="h-5 w-5" />
      </button>

      {/* Mobile drawer */}
      {mobileMenuOpen && (
        <>
          <div className="fixed inset-0 z-50 bg-black/15 backdrop-blur-sm lg:hidden" onClick={() => setMobileMenuOpen(false)} />
          <aside className="fixed left-0 top-0 z-50 flex h-screen w-[260px] flex-col glass-sidebar border-r border-border lg:hidden animate-fade-up shadow-xl">
            <button
              type="button"
              onClick={() => setMobileMenuOpen(false)}
              className="absolute right-3 top-3 flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground hover:bg-muted"
            >
              <X className="h-4 w-4" />
            </button>
            <SidebarInner collapsed={false} onNavigate={() => setMobileMenuOpen(false)} />
          </aside>
        </>
      )}

      {/* Desktop sidebar — single element with width transition */}
      <aside
        className={cn(
          "hidden lg:flex fixed left-0 top-0 z-40 h-screen flex-col border-r border-white/30 glass-sidebar transition-all duration-300 ease-out overflow-hidden",
          sidebarExpanded ? "w-[230px]" : "w-[64px]",
        )}
      >
        <SidebarInner collapsed={!sidebarExpanded} />
      </aside>
    </>
  );
}
