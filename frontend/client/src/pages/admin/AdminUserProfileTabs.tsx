/**
 * AdminUserProfileTabs — tab content components for the Admin User 360 panel.
 * Exported and consumed by AdminUserProfile.tsx.
 */
import React from "react";
import {
  Award,
  BookOpen,
  CheckCircle2,
  ChevronRight,
  ClipboardCheck,
  Clock,
  MinusCircle,
  PlayCircle,
  ShieldCheck,
  TrendingUp,
} from "lucide-react";

// ─── Shared types (mirror backend AdminWorkforceProfileResponse) ──────────────

export interface AdminCapabilityItem {
  competency_code: string;
  competency_name: string;
  domain: string;
  current_level: number | null;
  required_level: number;
  gap: number;
  gap_category: string;
}

export interface AdminLearningActivityItem {
  activity_id: string;
  resource_id: string;
  resource_title: string | null;
  provider: string | null;
  competency_id: string;
  status: string;
  progress_percent: number;
  started_at: string | null;
  last_accessed_at: string | null;
  completed_at: string | null;
  duration_minutes: number;
}

export interface AdminAssessmentItem {
  assessment_id: string;
  assessment_type: string;
  competency_code: string | null;
  status: string | null;
  score: number | null;
  percentage: number | null;
  assessed_at: string | null;
  authoritative: boolean;
}

export interface AdminEvidenceItem {
  evidence_id: string;
  evidence_type: string;
  competency_code: string | null;
  confidence: number | null;
  source: string | null;
  recorded_at: string | null;
}

export interface EvidenceSummary {
  supporting_count: number;
  supporting_confidence: number;
  authoritative_count: number;
  authoritative_confidence: number;
  total_records: number;
  governance_note: string;
}

export interface LearningSummary {
  total_activities: number;
  completed: number;
  in_progress: number;
  not_started: number;
  abandoned: number;
  total_learning_hours: number;
  overall_learning_progress_pct: number | null;
  progress_note: string;
}

export interface TimelineEvent {
  timestamp: string | null;
  event_type: string;
  title: string;
  detail: string;
  icon: string;
}

export interface WorkforceProfile {
  user: {
    id: string;
    email: string;
    full_name: string;
    employee_id: string;
    department: string;
    designation: string;
    access_role: string;
    professional_role: string;
    status: string;
    created_at: string;
    last_login_at: string | null;
  };
  capabilities: AdminCapabilityItem[];
  active_gaps: AdminCapabilityItem[];
  learning_summary: LearningSummary;
  learning_activities: AdminLearningActivityItem[];
  assessments: AdminAssessmentItem[];
  evidence_summary: EvidenceSummary;
  evidence: AdminEvidenceItem[];
  timeline: TimelineEvent[];
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

function fmtDate(d: string | null | undefined): string {
  if (!d) return "—";
  try {
    return new Date(d).toLocaleDateString("en-IN", {
      day: "numeric", month: "short", year: "numeric",
    });
  } catch { return d; }
}

function fmtDateTime(d: string | null | undefined): string {
  if (!d) return "—";
  try {
    return new Date(d).toLocaleDateString("en-IN", {
      day: "numeric", month: "short", year: "numeric",
      hour: "2-digit", minute: "2-digit",
    });
  } catch { return d; }
}

const GAP_PILL: Record<string, string> = {
  CRITICAL: "bg-red-100 text-red-800 border-red-200",
  HIGH:     "bg-orange-100 text-orange-800 border-orange-200",
  MEDIUM:   "bg-yellow-100 text-yellow-800 border-yellow-200",
  MET:      "bg-emerald-100 text-emerald-800 border-emerald-200",
  LOW:      "bg-blue-100 text-blue-800 border-blue-200",
};

const ACTIVITY_COLOR: Record<string, string> = {
  completed:   "bg-emerald-100 text-emerald-800",
  in_progress: "bg-blue-100 text-blue-800",
  not_started: "bg-slate-100 text-slate-600",
  abandoned:   "bg-red-50 text-red-600",
};

const ACTIVITY_LABEL: Record<string, string> = {
  completed:   "Completed",
  in_progress: "In Progress",
  not_started: "Not Started",
  abandoned:   "Abandoned",
};

const AUTH_TYPES = new Set(["CAPABILITY_ASSESSMENT", "ADAPTIVE_ASSESSMENT"]);

function StatusDot({ status }: { status: string }) {
  if (status === "completed")   return <CheckCircle2 size={12} className="text-emerald-600 shrink-0" aria-hidden />;
  if (status === "in_progress") return <PlayCircle   size={12} className="text-blue-600 shrink-0"    aria-hidden />;
  if (status === "abandoned")   return <MinusCircle  size={12} className="text-red-400 shrink-0"     aria-hidden />;
  return <Clock size={12} className="text-slate-400 shrink-0" aria-hidden />;
}

function SectionHead({ icon, label }: { icon: React.ReactNode; label: string }) {
  return (
    <div className="flex items-center gap-2 mb-3">
      <span className="text-[#4b36a8]">{icon}</span>
      <h3 className="text-sm font-extrabold text-[#123057]">{label}</h3>
    </div>
  );
}

function EmptyState({ icon, title, sub }: { icon: React.ReactNode; title: string; sub?: string }) {
  return (
    <div className="rounded-2xl border border-dashed border-slate-200 bg-white p-10 text-center">
      <div className="mx-auto mb-3 w-fit">{icon}</div>
      <p className="text-sm font-bold text-slate-500">{title}</p>
      {sub && <p className="text-xs text-slate-400 mt-1 max-w-xs mx-auto">{sub}</p>}
    </div>
  );
}

function InfoBanner({ children }: { children: React.ReactNode }) {
  return (
    <div className="rounded-xl bg-amber-50 border border-amber-100 px-3 py-2 text-[11px] text-amber-800">
      {children}
    </div>
  );
}

// ─── Tab: Overview ────────────────────────────────────────────────────────────

export function TabOverview({
  profile: p,
  onViewGaps,
}: {
  profile: WorkforceProfile;
  onViewGaps: () => void;
}) {
  const ls = p.learning_summary;
  const es = p.evidence_summary;

  const assessedCaps = p.capabilities.filter((c) => c.current_level !== null);
  const avgLevel =
    assessedCaps.length > 0
      ? assessedCaps.reduce((s, c) => s + (c.current_level ?? 0), 0) / assessedCaps.length
      : null;

  return (
    <div className="space-y-5">
      {/* KPI row */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {[
          { label: "Avg Capability",     value: avgLevel !== null ? avgLevel.toFixed(1) : "—", sub: "/ 5.0",           cls: "text-[#123057]",  bg: "bg-purple-50" },
          { label: "Active Gaps",        value: String(p.active_gaps.length),                  sub: "competencies",    cls: "text-orange-700", bg: "bg-orange-50" },
          { label: "Learning",           value: String(ls.total_activities),                   sub: `${ls.completed} done`, cls: "text-blue-700",   bg: "bg-blue-50"   },
          { label: "Evidence Records",   value: String(es.total_records),                      sub: `${es.authoritative_count} auth.`, cls: "text-emerald-700", bg: "bg-emerald-50" },
        ].map((c) => (
          <div key={c.label} className={`rounded-2xl ${c.bg} p-4 border border-white/80 shadow-sm`}>
            <div className="text-[10px] font-bold uppercase tracking-wide text-slate-500">{c.label}</div>
            <div className={`text-2xl font-black mt-1 ${c.cls}`}>
              {c.value}
              <span className="text-xs font-semibold text-slate-400 ml-1">{c.sub}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Learning progress */}
      <div className="rounded-2xl border border-[#e0daef] bg-white p-5">
        <SectionHead icon={<BookOpen size={15} />} label="Learning Progress" />
        <p className="text-[11px] text-slate-500 italic mb-3">
          Reflects learner-reported engagement only.{" "}
          <strong className="text-slate-700 not-italic">Not competency progress.</strong>{" "}
          Competency updates require formal assessment evidence.
        </p>
        <div className="grid grid-cols-4 gap-2 text-center text-xs mb-4">
          {[
            { label: "Total",      value: ls.total_activities, cls: "text-slate-700"  },
            { label: "Completed",  value: ls.completed,        cls: "text-emerald-700"},
            { label: "In Progress",value: ls.in_progress,      cls: "text-blue-700"  },
            { label: "Not Started",value: ls.not_started,      cls: "text-slate-400" },
          ].map((s) => (
            <div key={s.label} className="rounded-xl bg-slate-50 py-2.5 border border-slate-100">
              <div className={`text-xl font-black ${s.cls}`}>{s.value}</div>
              <div className="text-[10px] text-slate-400 mt-0.5">{s.label}</div>
            </div>
          ))}
        </div>
        {ls.overall_learning_progress_pct !== null ? (
          <>
            <div className="flex justify-between text-xs font-semibold mb-1">
              <span className="text-slate-600">Overall Learning Progress</span>
              <span className="text-[#4b36a8] font-extrabold">
                {ls.overall_learning_progress_pct.toFixed(0)}%
              </span>
            </div>
            <div
              className="h-2.5 w-full rounded-full bg-slate-100 overflow-hidden"
              role="progressbar"
              aria-valuenow={ls.overall_learning_progress_pct}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label="Overall learning progress"
            >
              <div
                className="h-full rounded-full bg-[#4b36a8] transition-all duration-500"
                style={{ width: `${Math.min(100, ls.overall_learning_progress_pct)}%` }}
              />
            </div>
            <div className="text-[10px] text-slate-400 mt-1.5">
              {ls.total_learning_hours.toFixed(1)} learning hours recorded
            </div>
          </>
        ) : (
          <div className="text-xs text-slate-400 italic">No learning activity recorded yet.</div>
        )}
      </div>

      {/* Evidence banners */}
      <div className="grid gap-3 sm:grid-cols-2">
        <div className="rounded-2xl border border-teal-200 bg-teal-50/40 p-4">
          <div className="flex items-center gap-2 text-teal-900 font-extrabold text-xs mb-1">
            <BookOpen size={13} /> Supporting Evidence
          </div>
          <div className="text-2xl font-black text-teal-800">{es.supporting_count}</div>
          <div className="text-[10px] text-teal-700 mt-1">
            Confidence {(es.supporting_confidence * 100).toFixed(0)}% &middot; learning completions
          </div>
          <div className="text-[10px] text-teal-600/70 mt-0.5">Does not update competency profile</div>
        </div>
        <div className="rounded-2xl border border-emerald-200 bg-emerald-50/40 p-4">
          <div className="flex items-center gap-2 text-emerald-900 font-extrabold text-xs mb-1">
            <ShieldCheck size={13} /> Authoritative Evidence
          </div>
          <div className="text-2xl font-black text-emerald-800">{es.authoritative_count}</div>
          <div className="text-[10px] text-emerald-700 mt-1">
            Confidence {(es.authoritative_confidence * 100).toFixed(0)}% &middot; capability assessments
          </div>
          <div className="text-[10px] text-emerald-600/70 mt-0.5">Directly updates competency profile</div>
        </div>
      </div>

      {/* Top gaps */}
      {p.active_gaps.length > 0 && (
        <div className="rounded-2xl border border-[#e0daef] bg-white p-5">
          <SectionHead icon={<TrendingUp size={15} />} label="Top Active Gaps" />
          <div className="space-y-2">
            {p.active_gaps.slice(0, 4).map((g) => (
              <div
                key={g.competency_code}
                className="flex items-center justify-between gap-2 rounded-xl bg-slate-50 px-3 py-2.5 border border-slate-100 text-xs"
              >
                <div className="min-w-0">
                  <span className="font-bold text-slate-800 block truncate">{g.competency_name}</span>
                  <span className="text-[10px] text-slate-400">{g.domain}</span>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span className="font-mono text-[11px] text-slate-500">
                    {g.current_level !== null ? g.current_level.toFixed(1) : "—"} / {g.required_level.toFixed(1)}
                  </span>
                  <span className={`rounded-full border px-2 py-0.5 text-[10px] font-extrabold ${GAP_PILL[g.gap_category] || GAP_PILL.MEDIUM}`}>
                    {g.gap_category}
                  </span>
                </div>
              </div>
            ))}
          </div>
          {p.active_gaps.length > 4 && (
            <button
              onClick={onViewGaps}
              className="mt-2 flex items-center gap-0.5 text-xs font-semibold text-[#4b36a8] hover:underline"
            >
              View all {p.active_gaps.length} gaps <ChevronRight size={12} />
            </button>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Tab: Learning ────────────────────────────────────────────────────────────

export function TabLearning({ activities }: { activities: AdminLearningActivityItem[] }) {
  if (activities.length === 0) {
    return (
      <EmptyState
        icon={<BookOpen size={26} className="text-slate-300" />}
        title="No learning activity recorded yet."
        sub="Learning activities appear here when this official starts any learning resource."
      />
    );
  }

  return (
    <div className="space-y-3">
      <InfoBanner>
        <strong>Note:</strong> Progress shown is learner-reported engagement (stored explicitly).
        It does not imply competency mastery.
      </InfoBanner>

      {activities.map((act) => (
        <div key={act.activity_id} className="rounded-2xl border border-[#e0daef] bg-white p-4 shadow-sm">
          {/* Top row */}
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0 flex-1">
              <div className="font-bold text-sm text-[#123057] truncate">
                {act.resource_title || act.resource_id}
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5 flex flex-wrap gap-x-3">
                {act.provider && (
                  <span className="text-purple-700 font-semibold">{act.provider}</span>
                )}
                <span className="font-mono">{act.competency_id}</span>
                {act.duration_minutes > 0 && (
                  <span className="flex items-center gap-0.5">
                    <Clock size={10} aria-hidden />
                    {act.duration_minutes >= 60
                      ? `${(act.duration_minutes / 60).toFixed(1)}h`
                      : `${Math.round(act.duration_minutes)}m`}
                  </span>
                )}
              </div>
            </div>
            <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-[10px] font-extrabold shrink-0 ${ACTIVITY_COLOR[act.status] || "bg-slate-100 text-slate-600"}`}>
              <StatusDot status={act.status} />
              {ACTIVITY_LABEL[act.status] || act.status}
            </span>
          </div>

          {/* Progress bar */}
          <div className="mt-3">
            <div className="flex justify-between text-[10px] font-semibold text-slate-500 mb-1">
              <span>Learning Progress</span>
              <span className="text-[#4b36a8] font-extrabold">{act.progress_percent.toFixed(0)}%</span>
            </div>
            <div
              className="h-2 w-full rounded-full bg-slate-100 overflow-hidden"
              role="progressbar"
              aria-valuenow={act.progress_percent}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label={`Learning progress for ${act.resource_title || act.resource_id}`}
            >
              <div
                className={`h-full rounded-full transition-all ${act.status === "completed" ? "bg-emerald-500" : "bg-[#4b36a8]"}`}
                style={{ width: `${Math.min(100, act.progress_percent)}%` }}
              />
            </div>
          </div>

          {/* Dates */}
          <div className="mt-2 flex flex-wrap gap-x-4 gap-y-0.5 text-[10px] text-slate-400">
            {act.started_at    && <span>Started: {fmtDate(act.started_at)}</span>}
            {act.last_accessed_at && <span>Last active: {fmtDate(act.last_accessed_at)}</span>}
            {act.completed_at  && (
              <span className="text-emerald-600 font-semibold">
                Completed: {fmtDate(act.completed_at)}
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

// ─── Tab: Skill Gaps ──────────────────────────────────────────────────────────

export function TabGaps({ gaps }: { gaps: AdminCapabilityItem[] }) {
  if (gaps.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-emerald-200 bg-emerald-50/30 p-10 text-center">
        <CheckCircle2 size={28} className="mx-auto text-emerald-500 mb-3" />
        <p className="text-sm font-bold text-emerald-800">
          All mapped competencies are at or above required levels.
        </p>
        <p className="text-xs text-emerald-600 mt-1">
          Based on authoritative competency profiles vs role requirements.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="rounded-xl bg-slate-50 border border-slate-100 px-3 py-2 text-[11px] text-slate-600">
        Gaps are derived from authoritative competency profiles vs stored role requirements.
        Competency level updates only through formal assessment evidence.
      </div>

      {gaps.map((g) => (
        <div
          key={g.competency_code}
          className={`rounded-2xl border bg-white p-4 shadow-sm ${
            g.gap_category === "CRITICAL" ? "border-red-200" :
            g.gap_category === "HIGH"     ? "border-orange-200" : "border-yellow-200"
          }`}
        >
          <div className="flex items-start justify-between gap-3">
            <div>
              <div className="font-bold text-sm text-[#123057]">{g.competency_name}</div>
              <div className="text-[11px] text-slate-400 mt-0.5">
                {g.domain} &middot; <span className="font-mono">{g.competency_code}</span>
              </div>
            </div>
            <span className={`rounded-full border px-2.5 py-0.5 text-[10px] font-extrabold shrink-0 ${GAP_PILL[g.gap_category] || GAP_PILL.MEDIUM}`}>
              {g.gap_category}
            </span>
          </div>

          <div className="mt-3 grid grid-cols-3 gap-2 text-center text-xs">
            <div className="rounded-xl bg-slate-50 py-2 border border-slate-100">
              <div className="text-lg font-black text-slate-700">
                {g.current_level !== null ? g.current_level.toFixed(1) : "—"}
              </div>
              <div className="text-[10px] text-slate-400">Current</div>
            </div>
            <div className="rounded-xl bg-slate-50 py-2 border border-slate-100">
              <div className="text-lg font-black text-[#123057]">{g.required_level.toFixed(1)}</div>
              <div className="text-[10px] text-slate-400">Required</div>
            </div>
            <div className={`rounded-xl py-2 border ${g.gap > 0 ? "bg-red-50 border-red-100" : "bg-emerald-50 border-emerald-100"}`}>
              <div className={`text-lg font-black ${g.gap > 0 ? "text-red-700" : "text-emerald-700"}`}>
                {g.gap > 0 ? `\u2212${g.gap.toFixed(1)}` : "\u2713"}
              </div>
              <div className="text-[10px] text-slate-400">Gap</div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

// ─── Tab: Assessments ────────────────────────────────────────────────────────

export function TabAssessments({ assessments }: { assessments: AdminAssessmentItem[] }) {
  if (assessments.length === 0) {
    return (
      <EmptyState
        icon={<ClipboardCheck size={26} className="text-slate-300" />}
        title="No formal assessments on record."
        sub="Formal capability assessments appear here once the official takes one."
      />
    );
  }

  return (
    <div className="space-y-3">
      <InfoBanner>
        Only formal capability assessments generate authoritative evidence.
        Practice quiz results are not shown here.
      </InfoBanner>

      {assessments.map((ass) => (
        <div key={ass.assessment_id} className="rounded-2xl border border-[#e0daef] bg-white p-4 shadow-sm">
          <div className="flex items-start justify-between gap-3">
            <div>
              <div className="font-bold text-sm text-[#123057]">
                {ass.competency_code || "Capability Assessment"}
              </div>
              <div className="text-[11px] text-slate-400 mt-0.5">{ass.assessment_type}</div>
            </div>
            {ass.authoritative ? (
              <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 border border-emerald-200 px-2.5 py-0.5 text-[10px] font-extrabold text-emerald-800 shrink-0">
                <ShieldCheck size={11} aria-hidden /> Authoritative
              </span>
            ) : (
              <span className="rounded-full bg-yellow-100 border border-yellow-200 px-2.5 py-0.5 text-[10px] font-extrabold text-yellow-700 shrink-0">
                In Progress
              </span>
            )}
          </div>

          {(ass.score !== null || ass.percentage !== null) && (
            <div className="mt-3 flex gap-3 flex-wrap text-xs">
              {ass.percentage !== null && (
                <div className="rounded-xl bg-purple-50 px-3 py-1.5 border border-purple-100">
                  <span className="font-black text-[#4b36a8]">{ass.percentage.toFixed(1)}%</span>
                  <span className="text-slate-400 ml-1">Score</span>
                </div>
              )}
              {ass.score !== null && (
                <div className="rounded-xl bg-slate-50 px-3 py-1.5 border border-slate-100">
                  <span className="font-black text-slate-700">{ass.score.toFixed(2)}</span>
                  <span className="text-slate-400 ml-1">Raw</span>
                </div>
              )}
            </div>
          )}

          <div className="mt-2 text-[10px] text-slate-400">
            {ass.assessed_at ? `Assessed: ${fmtDateTime(ass.assessed_at)}` : "Date unavailable"}
          </div>
        </div>
      ))}
    </div>
  );
}

// ─── Tab: Evidence ────────────────────────────────────────────────────────────

export function TabEvidence({
  evidence,
  summary,
}: {
  evidence: AdminEvidenceItem[];
  summary: EvidenceSummary;
}) {
  if (evidence.length === 0) {
    return (
      <EmptyState
        icon={<Award size={26} className="text-slate-300" />}
        title="No evidence records in ledger."
        sub="Evidence is generated by completing learning activities (supporting) or formal assessments (authoritative)."
      />
    );
  }

  const supporting   = evidence.filter((e) => !AUTH_TYPES.has(e.evidence_type));
  const authoritative = evidence.filter((e) =>  AUTH_TYPES.has(e.evidence_type));

  const renderItem = (ev: AdminEvidenceItem, isAuth: boolean) => (
    <div
      key={ev.evidence_id}
      className={`rounded-2xl border p-4 shadow-sm ${
        isAuth
          ? "border-emerald-200 bg-emerald-50/30"
          : "border-teal-200 bg-teal-50/20"
      }`}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            {isAuth ? (
              <span className="inline-flex items-center gap-1 text-[10px] font-extrabold text-emerald-800 bg-emerald-100 border border-emerald-200 rounded-full px-2 py-0.5">
                <ShieldCheck size={10} aria-hidden /> AUTHORITATIVE
              </span>
            ) : (
              <span className="inline-flex items-center gap-1 text-[10px] font-extrabold text-teal-800 bg-teal-100 border border-teal-200 rounded-full px-2 py-0.5">
                <BookOpen size={10} aria-hidden /> SUPPORTING
              </span>
            )}
            {ev.competency_code && (
              <span className="font-mono text-[10px] font-bold text-slate-600 bg-slate-100 rounded px-1.5 py-0.5">
                {ev.competency_code}
              </span>
            )}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">
            {ev.evidence_type.replace(/_/g, " ")}
            {ev.source && <span className="ml-2 text-slate-400">via {ev.source}</span>}
          </div>
        </div>
        {ev.confidence !== null && (
          <div className="shrink-0 text-right">
            <div className={`text-sm font-black ${isAuth ? "text-emerald-700" : "text-teal-700"}`}>
              {(ev.confidence * 100).toFixed(0)}%
            </div>
            <div className="text-[10px] text-slate-400">confidence</div>
          </div>
        )}
      </div>
      {ev.recorded_at && (
        <div className="mt-1.5 text-[10px] text-slate-400">{fmtDateTime(ev.recorded_at)}</div>
      )}
    </div>
  );

  return (
    <div className="space-y-4">
      <div className="rounded-xl bg-slate-50 border border-slate-100 px-3 py-2 text-[11px] text-slate-600 leading-relaxed">
        {summary.governance_note}
      </div>

      {authoritative.length > 0 && (
        <div className="space-y-2">
          <div className="text-xs font-extrabold text-emerald-800 flex items-center gap-1">
            <ShieldCheck size={13} aria-hidden /> Authoritative Evidence ({authoritative.length})
          </div>
          {authoritative.map((ev) => renderItem(ev, true))}
        </div>
      )}

      {supporting.length > 0 && (
        <div className="space-y-2">
          <div className="text-xs font-extrabold text-teal-800 flex items-center gap-1">
            <BookOpen size={13} aria-hidden /> Supporting Evidence ({supporting.length})
          </div>
          {supporting.map((ev) => renderItem(ev, false))}
        </div>
      )}
    </div>
  );
}

// ─── Tab: Timeline ────────────────────────────────────────────────────────────

const TIMELINE_ICON_COLOR: Record<string, string> = {
  LEARNING_STARTED:     "bg-blue-100 text-blue-700",
  LEARNING_COMPLETED:   "bg-emerald-100 text-emerald-700",
  SUPPORTING_EVIDENCE:  "bg-teal-100 text-teal-700",
  ASSESSMENT_STARTED:   "bg-purple-100 text-purple-700",
  ASSESSMENT_SUBMITTED: "bg-purple-200 text-purple-800",
  AUTHORITATIVE_EVIDENCE: "bg-emerald-200 text-emerald-900",
};

export function TabTimeline({ timeline }: { timeline: TimelineEvent[] }) {
  if (timeline.length === 0) {
    return (
      <EmptyState
        icon={<Clock size={26} className="text-slate-300" />}
        title="No timeline events yet."
        sub="Learning and assessment events will appear here chronologically once activity is recorded."
      />
    );
  }

  return (
    <div className="space-y-1">
      <div className="text-[11px] text-slate-500 italic mb-3">
        Chronological record of learning and assessment events. Only real recorded events shown.
      </div>
      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-4 top-0 bottom-0 w-px bg-slate-200" aria-hidden />

        <div className="space-y-4 pl-10">
          {timeline.map((evt, idx) => {
            const colorCls = TIMELINE_ICON_COLOR[evt.event_type] || "bg-slate-100 text-slate-600";
            return (
              <div key={idx} className="relative">
                {/* Dot on the line */}
                <div
                  className={`absolute -left-[26px] flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-black ${colorCls} border-2 border-white shadow-sm`}
                  aria-hidden
                >
                  {evt.icon === "shield"     ? "🛡" :
                   evt.icon === "check"      ? "✓"  :
                   evt.icon === "assessment" ? "📋" :
                   evt.icon === "evidence"   ? "📄" : "📖"}
                </div>

                <div className="rounded-2xl border border-[#e0daef] bg-white p-3.5 shadow-sm">
                  <div className="font-bold text-xs text-[#123057]">{evt.title}</div>
                  {evt.detail && (
                    <div className="text-[11px] text-slate-500 mt-0.5">{evt.detail}</div>
                  )}
                  {evt.timestamp && (
                    <div className="text-[10px] text-slate-400 mt-1">
                      {fmtDateTime(evt.timestamp)}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
