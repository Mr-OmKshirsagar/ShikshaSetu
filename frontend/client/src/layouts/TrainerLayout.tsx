import React, { useState } from "react";
import {
  BarChart2,
  BookOpen,
  CheckSquare,
  FileQuestion,
  FilePlus,
  Layers,
  LayoutDashboard,
  Menu,
  PenTool,
  Users,
  UserRound,
  X,
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { useTranslation } from "@/i18n";
import { LanguageToggle } from "@/components/LanguageToggle";

// ─── Props ────────────────────────────────────────────────────────────────────

interface TrainerLayoutProps {
  children: React.ReactNode;
  activePage: string;
  onNavigate: (page: string) => void;
}

// ─── Component ────────────────────────────────────────────────────────────────

export function TrainerLayout({ children, activePage, onNavigate }: TrainerLayoutProps) {
  const { user, logout } = useAuth();
  const { t } = useTranslation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navItems = [
    { id: "Dashboard", label: t("nav.dashboard"), icon: LayoutDashboard },
    { id: "Learning Materials", label: t("nav.materials"), icon: BookOpen },
    { id: "Upload Material", label: t("nav.uploadMaterial"), icon: FilePlus },
    { id: "AI Question Generator", label: t("nav.aiGenerator"), icon: FileQuestion },
    { id: "Question Review", label: t("nav.questionReview"), icon: CheckSquare },
    { id: "Quiz Studio", label: t("nav.quizStudio"), icon: PenTool },
    { id: "Published Quizzes", label: t("nav.publishedQuizzes"), icon: Layers },
    { id: "Learner Results", label: t("nav.learnerResults"), icon: BarChart2 },
    { id: "Profile", label: t("nav.profile"), icon: UserRound },
  ];

  const handleNav = (page: string) => {
    onNavigate(page);
    setSidebarOpen(false);
  };

  return (
    <div className="min-h-screen bg-[#fdf5ee] text-[#1a2744]">
      {/* ── Sidebar ── */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-[264px] border-r border-[#f0ddd0] bg-white flex flex-col transition-transform lg:translate-x-0 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-5 py-6">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#ef7e37] text-white text-lg font-bold select-none shadow-xs">
            T
          </div>
          <div>
            <div className="text-base font-bold text-[#c2510e] tracking-tight">ShikshaSetu</div>
            <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
              {t("shell.trainerRole")}
            </div>
          </div>
        </div>

        {/* Section label */}
        <div className="px-7 mb-2 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
          {t("shell.trainerWorkspace")}
        </div>

        {/* Nav items */}
        <nav className="flex-1 px-4 overflow-y-auto">
          {navItems.map(({ id, label, icon: Icon }) => {
            const isActive = activePage === id;
            return (
              <button
                key={id}
                onClick={() => handleNav(id)}
                className={`mb-1 flex w-full items-center gap-3 rounded-xl px-3.5 py-2.5 text-left text-xs transition-all duration-180 active:scale-[0.98] group ${
                  isActive
                    ? "bg-[#fff2e8] text-[#ef7e37] shadow-xs font-semibold nav-pill-active"
                    : "text-slate-600 font-medium hover:bg-orange-50 hover:text-[#c2510e]"
                }`}
              >
                <Icon size={17} className={`transition-transform duration-160 ${isActive ? "scale-105 text-[#ef7e37]" : "text-slate-400 group-hover:scale-110 group-hover:text-[#c2510e]"}`} />
                <span>{label}</span>
              </button>
            );
          })}
        </nav>

        {/* User footer */}
        <div className="border-t border-[#f0ddd0] px-5 py-4">
          <div className="mb-0.5 text-xs font-semibold text-[#c2510e] truncate">
            {user?.full_name ?? "—"}
          </div>
          <div className="text-[11px] font-normal text-slate-400 truncate mb-3">
            {user?.designation ?? user?.department ?? t("shell.trainerRole")}
          </div>
        </div>
      </aside>

      {/* ── Mobile overlay ── */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/20 lg:hidden backdrop-blur-xs transition-opacity"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* ── Hamburger ── */}
      <button
        className="fixed left-4 top-4 z-50 rounded-lg bg-white p-2 shadow border border-[#f0ddd0] lg:hidden btn-interactive"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        aria-label={sidebarOpen ? t("common.closeSidebar") : t("common.openSidebar")}
      >
        {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* ── Main content ── */}
      <main className="lg:ml-[264px]">
        <header className="flex h-[68px] items-center justify-between border-b border-[#f0ddd0] bg-white px-6 lg:px-9">
          <div>
            <div className="text-[10px] font-bold uppercase tracking-[.14em] text-slate-400">
              {t("shell.trainerWorkspace")}
            </div>
            <h1 className="text-lg font-bold text-[#c2510e]">
              {navItems.find((n) => n.id === activePage)?.label || activePage}
            </h1>
          </div>
          <div className="flex items-center gap-3">
            <LanguageToggle />
            <span className="hidden text-xs font-semibold text-slate-500 sm:block truncate max-w-[160px]">
              {user?.full_name}
            </span>
            <button
              onClick={logout}
              className="rounded-lg border border-[#f0ddd0] px-3 py-1.5 text-xs font-bold text-[#c2510e] hover:bg-orange-50 transition-colors btn-interactive"
            >
              {t("common.logout")}
            </button>
          </div>
        </header>
        <div className="mx-auto max-w-[1240px] p-6 lg:p-9 anim-page-enter">{children}</div>
      </main>
    </div>
  );
}

export default TrainerLayout;
