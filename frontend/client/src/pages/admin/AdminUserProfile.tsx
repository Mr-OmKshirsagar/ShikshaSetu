/**
 * AdminUserProfile — User 360 / Individual Workforce Profile panel.
 *
 * Opened when Admin clicks a user row in AdminUsers.tsx.
 * Renders as a right-side slide-in panel with tabbed sections:
 *   Overview · Learning · Skill Gaps · Assessments · Evidence · Timeline
 *
 * RBAC: caller is already ADMIN (enforced at backend router level).
 * This component is read-only — no mutation operations.
 */
import React, { useEffect, useRef, useState } from "react";
import {
  AlertTriangle,
  Award,
  BookOpen,
  CheckCircle2,
  ChevronRight,
  ClipboardCheck,
  Clock,
  Loader2,
  MinusCircle,
  PlayCircle,
  RefreshCw,
  ShieldCheck,
  TrendingUp,
  X,
} from "lucide-react";
import { api } from "@/lib/api";
import { toast } from "sonner";
import {
  TabOverview,
  TabLearning,
  TabGaps,
  TabAssessments,
  TabEvidence,
  TabTimeline,
} from "./AdminUserProfileTabs";
import type { WorkforceProfile } from "./AdminUserProfileTabs";

// ─── Props ────────────────────────────────────────────────────────────────────

export interface AdminUserProfileProps {
  userId: string;
  userName: string;
  onClose: () => void;
}

// ─── Tab definitions ──────────────────────────────────────────────────────────

type Tab = "overview" | "learning" | "gaps" | "assessments" | "evidence" | "timeline";

const TABS: { id: Tab; label: string }[] = [
  { id: "overview",    label: "Overview"     },
  { id: "learning",    label: "Learning"     },
  { id: "gaps",        label: "Skill Gaps"   },
  { id: "assessments", label: "Assessments"  },
  { id: "evidence",    label: "Evidence"     },
  { id: "timeline",    label: "Timeline"     },
];

// ─── Panel shell (backdrop + slide-in drawer) ─────────────────────────────────

function PanelShell({
  userName,
  onClose,
  onRefresh,
  closeRef,
  loading,
  children,
}: {
  userName: string;
  onClose: () => void;
  onRefresh?: () => void;
  closeRef: React.RefObject<HTMLButtonElement | null>;
  loading?: boolean;
  children: React.ReactNode;
}) {
  return (
    <>
      <div
        className="fixed inset-0 z-40 bg-black/30 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-label={`Workforce profile: ${userName}`}
        className="fixed inset-y-0 right-0 z-50 flex w-full max-w-2xl flex-col bg-white shadow-2xl border-l border-[#e0daef] overflow-hidden"
        style={{ animation: "slideInRight 0.22s cubic-bezier(0.16,1,0.3,1)" }}
      >
        {/* Header bar */}
        <div className="flex items-center justify-between border-b border-[#e0daef] bg-white px-5 py-3 shrink-0">
          <div className="text-sm font-extrabold text-[#123057] truncate">
            Workforce Profile &middot; {userName}
          </div>
          <div className="flex items-center gap-1 shrink-0">
            {onRefresh && !loading && (
              <button
                onClick={onRefresh}
                className="flex items-center gap-1 rounded-xl border border-[#e0daef] px-3 py-1.5 text-xs font-semibold text-[#4b36a8] hover:bg-purple-50 transition"
                aria-label="Refresh profile"
              >
                <RefreshCw size={13} /> Refresh
              </button>
            )}
            <button
              ref={closeRef}
              onClick={onClose}
              className="ml-1 flex h-8 w-8 items-center justify-center rounded-xl border border-slate-200 text-slate-400 hover:bg-slate-100 transition focus:outline-none focus-visible:ring-2 focus-visible:ring-[#4b36a8]"
              aria-label="Close workforce profile panel"
            >
              <X size={15} />
            </button>
          </div>
        </div>
        {children}
      </div>
      <style>{`
        @keyframes slideInRight {
          from { transform: translateX(100%); opacity: 0.7; }
          to   { transform: translateX(0);    opacity: 1;   }
        }
      `}</style>
    </>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────

export function AdminUserProfile({ userId, userName, onClose }: AdminUserProfileProps) {
  const [profile, setProfile]   = useState<WorkforceProfile | null>(null);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState<string | null>(null);
  const [tab, setTab]           = useState<Tab>("overview");
  const closeRef                = useRef<HTMLButtonElement>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      // api.admin.userProfile is added in api.ts below
      const data = await (api.admin as any).userProfile(userId);
      setProfile(data as WorkforceProfile);
    } catch (err: any) {
      const msg = err?.message || "Failed to load workforce profile";
      setError(msg);
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [userId]);

  // Close on Escape key
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === "Escape") onClose(); };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  // Move focus to close button when loaded
  useEffect(() => {
    if (!loading) closeRef.current?.focus();
  }, [loading]);

  // ── Loading state ──────────────────────────────────────────────────────────
  if (loading) {
    return (
      <PanelShell userName={userName} onClose={onClose} closeRef={closeRef} loading>
        <div className="p-6 space-y-4">
          <div className="flex items-center gap-2 text-[#4b36a8] text-sm font-semibold">
            <Loader2 size={16} className="animate-spin" />
            Loading workforce profile&hellip;
          </div>
          {[1, 2, 3].map((n) => (
            <div key={n} className="h-20 rounded-2xl bg-slate-100 animate-pulse" />
          ))}
        </div>
      </PanelShell>
    );
  }

  // ── Error state ────────────────────────────────────────────────────────────
  if (error || !profile) {
    return (
      <PanelShell userName={userName} onClose={onClose} closeRef={closeRef}>
        <div className="flex flex-col items-center gap-4 p-12 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-red-50 text-red-400">
            <AlertTriangle size={24} />
          </div>
          <p className="text-sm font-bold text-slate-700">{error || "Profile unavailable"}</p>
          <button
            onClick={load}
            className="rounded-xl bg-[#4b36a8] px-4 py-2 text-xs font-bold text-white hover:bg-[#3d2b8a] transition"
          >
            Retry
          </button>
        </div>
      </PanelShell>
    );
  }

  const p = profile;

  return (
    <PanelShell userName={userName} onClose={onClose} closeRef={closeRef} onRefresh={load}>
      {/* ── Identity header ── */}
      <div className="bg-gradient-to-br from-[#f0edfc] to-[#e8f5f3] px-6 py-5 border-b border-[#e0daef] shrink-0">
        <div className="flex items-start gap-4">
          <div
            className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-[#4b36a8] text-white text-xl font-black"
            aria-hidden="true"
          >
            {p.user.full_name.charAt(0).toUpperCase()}
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-lg font-black text-[#123057] truncate">{p.user.full_name}</div>
            <div className="text-xs font-semibold text-[#4b36a8]">{p.user.professional_role}</div>
            <div className="text-xs text-slate-500 mt-0.5">
              {p.user.department} &middot; {p.user.designation}
            </div>
          </div>
          <div className="ml-auto flex flex-col items-end gap-1 shrink-0">
            <span
              className={`rounded-full px-2.5 py-0.5 text-[10px] font-extrabold ${
                p.user.access_role === "ADMIN"
                  ? "bg-purple-100 text-[#4b36a8]"
                  : p.user.access_role === "TRAINER"
                  ? "bg-orange-100 text-orange-800"
                  : "bg-teal-100 text-teal-800"
              }`}
            >
              {p.user.access_role}
            </span>
            <span className="rounded-full bg-emerald-50 px-2.5 py-0.5 text-[10px] font-extrabold text-emerald-700">
              {p.user.status}
            </span>
          </div>
        </div>
        <div className="mt-3 flex flex-wrap gap-x-4 gap-y-0.5 text-[10px] text-slate-500">
          <span>
            ID:{" "}
            <span className="font-mono font-semibold text-slate-700">{p.user.employee_id}</span>
          </span>
          <span>{p.user.email}</span>
          <span>
            Registered:{" "}
            {new Date(p.user.created_at).toLocaleDateString("en-IN", {
              day: "numeric", month: "short", year: "numeric",
            })}
          </span>
        </div>
      </div>

      {/* ── Tab bar ── */}
      <div
        className="flex overflow-x-auto border-b border-[#e0daef] bg-white px-2 pt-2 gap-0.5 shrink-0"
        role="tablist"
        aria-label="Profile sections"
      >
        {TABS.map((t) => (
          <button
            key={t.id}
            role="tab"
            aria-selected={tab === t.id}
            onClick={() => setTab(t.id)}
            className={`whitespace-nowrap rounded-t-xl px-4 py-2 text-xs font-bold transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-[#4b36a8] ${
              tab === t.id
                ? "bg-[#4b36a8] text-white shadow-sm"
                : "text-slate-500 hover:text-[#4b36a8] hover:bg-purple-50"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* ── Tab content ── */}
      <div className="flex-1 overflow-y-auto p-5" role="tabpanel">
        {tab === "overview"    && <TabOverview    profile={p} onViewGaps={() => setTab("gaps")} />}
        {tab === "learning"    && <TabLearning    activities={p.learning_activities} />}
        {tab === "gaps"        && <TabGaps        gaps={p.active_gaps} />}
        {tab === "assessments" && <TabAssessments assessments={p.assessments} />}
        {tab === "evidence"    && <TabEvidence    evidence={p.evidence} summary={p.evidence_summary} />}
        {tab === "timeline"    && <TabTimeline    timeline={p.timeline} />}
      </div>
    </PanelShell>
  );
}

export default AdminUserProfile;
