import React, { useState } from "react";
import { LogOut, Menu, X } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useTranslation } from "@/i18n";
import { LanguageToggle } from "@/components/LanguageToggle";
import { ShikshaSetuLogo } from "@/components/brand/ShikshaSetuLogo";

export interface DashboardNavItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  badge?: string | number;
}

export interface DashboardRoleTheme {
  activeNavBg: string;
  activeNavText: string;
  activeIndicator: string;
  hoverNavBg?: string;
  avatarBg: string;
  avatarText?: string;
  badgeDotBg?: string;
  headerTitleColor?: string;
  workspaceLabelColor?: string;
}

export interface DashboardShellProps {
  children: React.ReactNode;
  activePage: string;
  onNavigate: (page: string) => void;
  navItems: DashboardNavItem[];
  workspaceTitle: string;
  headerWorkspaceLabel?: string;
  headerTitle?: string;
  headerActions?: React.ReactNode;
  logoHref?: string;
  roleBadgeText?: string;
  userDisplayName?: string;
  userRoleSubtitle?: string;
  roleTheme?: DashboardRoleTheme;
  bgClassName?: string;
}

export function DashboardShell({
  children,
  activePage,
  onNavigate,
  navItems,
  workspaceTitle,
  headerWorkspaceLabel,
  headerTitle,
  headerActions,
  logoHref = "/",
  roleBadgeText,
  userDisplayName,
  userRoleSubtitle,
  roleTheme,
  bgClassName = "bg-[#f4f7fb]",
}: DashboardShellProps) {
  const { user, logout } = useAuth();
  const { t } = useTranslation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const activeItem = navItems.find((n) => n.id === activePage);
  const resolvedHeaderTitle = headerTitle || activeItem?.label || activePage;

  const handleNavClick = (pageId: string) => {
    onNavigate(pageId);
    setSidebarOpen(false);
  };

  return (
    <div className={`min-h-screen ${bgClassName} text-[#1a2744]`}>
      {/* ── 1. Left Sidebar (Fixed 220px width, full viewport height) ── */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-[220px] min-w-[220px] max-w-[220px] h-screen bg-white border-r border-[#dfe7f0] flex flex-col transition-transform duration-200 lg:translate-x-0 ${
          sidebarOpen ? "translate-x-0 shadow-2xl" : "-translate-x-full"
        }`}
      >
        {/* Sidebar Brand Header (72px fixed height, perfectly level with Top Header) */}
        <div className="h-[72px] min-h-[72px] max-h-[72px] px-5 flex items-center justify-between border-b border-[#dfe7f0]">
          <ShikshaSetuLogo variant="compact" size="sm" href={logoHref} priority />
          {/* Mobile close button inside sidebar */}
          <button
            type="button"
            onClick={() => setSidebarOpen(false)}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 lg:hidden focus:outline-hidden"
            aria-label="Close sidebar"
          >
            <X size={18} />
          </button>
        </div>

        {/* Workspace Category Label */}
        <div className="px-5 pt-3 pb-1.5 text-[9px] font-bold uppercase tracking-[0.14em] text-slate-400 truncate">
          {workspaceTitle}
        </div>

        {/* Sidebar Navigation Items */}
        <nav className="flex-1 px-3 py-1.5 overflow-y-auto space-y-0.5">
          {navItems.map(({ id, label, icon: Icon, badge }) => {
            const isActive = activePage === id;
            return (
              <button
                key={id}
                onClick={() => handleNavClick(id)}
                className={`relative flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-left text-[11px] transition-all duration-150 active:scale-[0.98] group ${
                  isActive
                    ? `${roleTheme?.activeNavBg || "bg-[#e8f5f3]"} ${
                        roleTheme?.activeNavText || "text-[#087f76]"
                      } font-semibold shadow-2xs pl-3.5`
                    : `text-slate-600 font-medium ${
                        roleTheme?.hoverNavBg || "hover:bg-slate-50 hover:text-[#123057]"
                      }`
                }`}
                aria-current={isActive ? "page" : undefined}
              >
                {isActive && (
                  <span
                    className={`absolute left-0 top-2 bottom-2 w-1 rounded-r-full ${
                      roleTheme?.activeIndicator || "bg-[#087f76]"
                    }`}
                  />
                )}
                <Icon
                  size={15}
                  className={`shrink-0 transition-transform duration-150 ${
                    isActive
                      ? `scale-105 ${roleTheme?.activeNavText || "text-[#087f76]"}`
                      : "text-slate-400 group-hover:scale-110 group-hover:text-[#123057]"
                  }`}
                />
                <span className="truncate flex-1">{label}</span>
                {badge != null && (
                  <span className="shrink-0 px-2 py-0.5 text-[10px] font-bold rounded-full bg-slate-100 text-slate-600">
                    {badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Bottom Profile Card */}
        <div className="border-t border-[#dfe7f0] p-3.5 bg-slate-50/70 shrink-0">
          <div className="flex items-center gap-2.5 px-2.5 py-2 rounded-xl bg-white border border-[#dfe7f0] shadow-2xs">
            <div
              className={`flex h-8 w-8 items-center justify-center rounded-lg font-bold text-xs shrink-0 ${
                roleTheme?.avatarBg || "bg-teal-100 text-[#087f76]"
              }`}
            >
              {(userDisplayName || user?.full_name || "System Administrator").charAt(0).toUpperCase()}
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-[11px] font-bold text-[#123057] truncate">
                {userDisplayName || user?.full_name || "System Administrator"}
              </div>
              <div className="text-[9px] font-medium text-slate-500 truncate">
                {userRoleSubtitle || user?.designation || user?.department || roleBadgeText || "User"}
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* ── 2. Mobile Backdrop ── */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-slate-900/40 backdrop-blur-xs lg:hidden transition-opacity"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* ── 3. Main Workspace Layout (Offset by sidebar width: lg:pl-[220px]) ── */}
      <div className="lg:pl-[220px] min-h-screen flex flex-col">
        {/* Top Header (72px fixed height, matching sidebar brand bar height) */}
        <header className="sticky top-0 z-20 h-[72px] min-h-[72px] max-h-[72px] w-full bg-white/95 backdrop-blur-md border-b border-[#dfe7f0]">
          <div className="h-full w-full max-w-[1360px] mx-auto px-6 lg:px-9 flex items-center justify-between">
            {/* Left: Hamburger (mobile) + Workspace label & Page title */}
            <div className="flex items-center gap-3 min-w-0">
              <button
                type="button"
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden p-2 -ml-1.5 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 focus:outline-hidden cursor-pointer"
                aria-label="Open sidebar"
              >
                <Menu size={20} />
              </button>

              <div className="min-w-0">
                <div className="text-[10px] font-bold uppercase tracking-[0.14em] text-slate-400 truncate">
                  {headerWorkspaceLabel || "SHIKSHASETU WORKSPACE"}
                </div>
                <h1
                  className={`text-lg font-bold tracking-tight truncate leading-tight ${
                    roleTheme?.headerTitleColor || "text-[#123057]"
                  }`}
                >
                  {resolvedHeaderTitle}
                </h1>
              </div>
            </div>

            {/* Right: AI Assistant, Language Toggle, User Badge, Logout Button */}
            <div className="flex items-center gap-2.5 sm:gap-3 shrink-0">
              {headerActions}
              <LanguageToggle />
              
              {/* User badge matching ShikshaSetu official header */}
              <div className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-50 text-xs font-semibold text-[#123057] border border-slate-200">
                <span className={`h-2 w-2 rounded-full ${roleTheme?.badgeDotBg || "bg-emerald-500"}`} />
                <span className="truncate max-w-[150px]">{userDisplayName || user?.full_name || "System Administrator"}</span>
              </div>

              {/* Logout Button */}
              <button
                onClick={logout}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-600 hover:text-red-700 hover:bg-red-50 border border-slate-200 hover:border-red-200 transition-all duration-150 shadow-2xs"
                title={t("common.logout")}
                aria-label={t("common.logout")}
              >
                <LogOut size={14} className="shrink-0" />
                <span className="hidden sm:inline">{t("common.logout")}</span>
              </button>
            </div>
          </div>
        </header>

        {/* Main Content Area (Shares the exact same container & padding grid as Header) */}
        <main className="flex-1 w-full">
          <div className="w-full max-w-[1360px] mx-auto px-6 lg:px-9 py-6 anim-page-enter">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}

export default DashboardShell;
