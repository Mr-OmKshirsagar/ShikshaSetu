import React, { useEffect, useState } from "react";
import {
  ArrowRight,
  Award,
  BookOpen,
  Briefcase,
  Building,
  CheckCircle2,
  ChevronRight,
  ClipboardCheck,
  FileCheck,
  Gauge,
  GraduationCap,
  Layers,
  Lightbulb,
  ShieldCheck,
  Sparkles,
  Target,
  TrendingUp,
} from "lucide-react";
import {
  api,
  SkillGapResponse,
  Competency,
  Recommendation,
  RecommendationResponse,
  LearningActivityListResponse,
  AssignedQuiz,
} from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { useTranslation } from "@/i18n";
import { NumberReveal, ProgressBarFill, AnimatedSection } from "@/components/motion/MotionUtils";

interface OfficialDashboardProps {
  onNavigate: (page: string, context?: { competencyCode?: string }) => void;
}

export function getRecommendationTitle(rec?: Recommendation | null): string {
  if (!rec) return "";
  const resource = rec.resource;
  if (resource && typeof resource === "object") {
    if (typeof resource.title === "string" && resource.title.trim()) {
      return resource.title.trim();
    }
    if (typeof resource.name === "string" && resource.name.trim()) {
      return resource.name.trim();
    }
    if (typeof resource.course_title === "string" && resource.course_title.trim()) {
      return resource.course_title.trim();
    }
    if (typeof resource.resource_id === "string" && resource.resource_id.trim()) {
      return resource.resource_id.trim();
    }
  }
  if (typeof rec.resource_title === "string" && rec.resource_title.trim()) {
    return rec.resource_title.trim();
  }
  if (typeof rec.title === "string" && rec.title.trim()) {
    return rec.title.trim();
  }
  if (typeof resource === "string" && resource.trim()) {
    return resource.trim();
  }
  return "Targeted Capability Course";
}

export function getRecommendationProvider(rec?: Recommendation | null): string {
  if (!rec) return "iGOT";
  if (typeof rec.provider === "string" && rec.provider.trim()) {
    return rec.provider.trim();
  }
  const resource = rec.resource;
  if (
    resource &&
    typeof resource === "object" &&
    typeof resource.provider === "string" &&
    resource.provider.trim()
  ) {
    return resource.provider.trim();
  }
  return "iGOT";
}

/**
 * Transforms raw competency codes (e.g. BEH_ETHICS, STAT_SAMPLING) into
 * clean, human-readable labels that respect government domain taxonomies.
 */
export function getCleanCompetencyName(name?: string | null, code?: string | null): string {
  if (name && typeof name === "string") {
    const trimmed = name.trim();
    if (!trimmed.includes("_") && trimmed.length > 2) {
      return trimmed;
    }
  }
  const raw = (code || name || "").trim();
  if (!raw) return "General Capability";
  const stripped = raw
    .replace(/^(STAT|TECH|BEH|DOMAIN|DIGOV|GOV|FIN|LAW)_/i, "")
    .replace(/_/g, " ");
  return stripped
    .toLowerCase()
    .split(" ")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

function getGreeting(name?: string): string {
  const hour = new Date().getHours();
  const timeOfDay = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";
  const firstName = name?.split(" ")[0] || "Officer";
  return `${timeOfDay}, ${firstName}`;
}

export function OfficialDashboard({ onNavigate }: OfficialDashboardProps) {
  const { user } = useAuth();
  const { t, isHindi } = useTranslation();
  const [skillGaps, setSkillGaps] = useState<SkillGapResponse | null>(null);
  const [competencies, setCompetencies] = useState<Competency[]>([]);
  const [recommendations, setRecommendations] = useState<RecommendationResponse | null>(null);
  const [activities, setActivities] = useState<LearningActivityListResponse | null>(null);
  const [assignedQuizzes, setAssignedQuizzes] = useState<AssignedQuiz[]>([]);
  const [evidenceList, setEvidenceList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setLoading(true);

    // 1. Primary data: Skill Gaps
    api.skillGaps
      .me()
      .then((res) => {
        if (active) {
          setSkillGaps(res);
          setLoading(false);
        }
      })
      .catch(() => {
        if (active) setLoading(false);
      });

    // 2. Framework Competencies
    api.competencies
      .me()
      .then((res) => {
        if (active) {
          setCompetencies(res as any);
          setLoading(false);
        }
      })
      .catch(() => {});

    // 3. Learning Activities
    api.learningActivities
      .list()
      .then((res) => {
        if (active) setActivities(res);
      })
      .catch(() => {});

    // 4. Personalized Recommendations
    api.recommendations
      .me()
      .then((res) => {
        if (active) setRecommendations(res);
      })
      .catch(() => {});

    // 5. Assigned Quizzes
    api.quizzes
      .assigned()
      .then((res) => {
        if (active) setAssignedQuizzes(res || []);
      })
      .catch(() => {});

    // 6. Evidence Ledger
    api.evidence
      .list()
      .then((res) => {
        if (active) setEvidenceList(res || []);
      })
      .catch(() => {});

    return () => {
      active = false;
    };
  }, []);

  const assessedGaps = skillGaps?.gaps?.filter((g) => g.current_level != null) || [];
  const priorityGaps =
    skillGaps?.gaps?.filter(
      (g) => g.gap_category === "CRITICAL" || g.gap_category === "HIGH" || g.gap > 0
    ) || [];

  const averageLevel =
    assessedGaps.length > 0
      ? assessedGaps.reduce((acc, g) => acc + (g.current_level || 0), 0) / assessedGaps.length
      : null;

  const averageConfidence =
    assessedGaps.length > 0
      ? assessedGaps.reduce((acc, g) => acc + (g.confidence || 0), 0) / assessedGaps.length
      : null;

  const topGap = priorityGaps[0] || skillGaps?.gaps?.[0];
  const topRec = recommendations?.recommendations?.[0];
  const activeRecs = recommendations?.recommendations?.slice(0, 3) || [];

  const completedActivities = activities?.activities?.filter((a) => a.status === "completed") || [];
  const inProgressActivities = activities?.activities?.filter((a) => a.status === "in_progress") || [];

  // Continuous Learning Loop definitions
  const learningLoopSteps = [
    { id: "Assessments", num: "01", label: "Assess", desc: "Role Framework", icon: ClipboardCheck, color: "text-teal-700 bg-teal-50" },
    { id: "Skill Gaps", num: "02", label: "Identify Gap", desc: "AI Gap Engine", icon: Target, color: "text-amber-700 bg-amber-50" },
    { id: "Recommendations", num: "03", label: "Recommend", desc: "iGOT & NSSTA", icon: Sparkles, color: "text-blue-700 bg-blue-50" },
    { id: "My Learning", num: "04", label: "Learn", desc: "Targeted Courses", icon: BookOpen, color: "text-indigo-700 bg-indigo-50" },
    { id: "Quizzes", num: "05", label: "Quiz", desc: "AI Verification", icon: CheckCircle2, color: "text-purple-700 bg-purple-50" },
    { id: "Evidence Ledger", num: "06", label: "Evidence", desc: "Tamper-Evident", icon: Award, color: "text-emerald-700 bg-emerald-50" },
    { id: "Progress Tracking", num: "07", label: "Improve", desc: "Updated Profile", icon: TrendingUp, color: "text-teal-800 bg-teal-100" },
  ];

  if (loading && !skillGaps && !competencies.length) {
    return (
      <div className="space-y-8 animate-fadeIn" role="status" aria-label="Loading dashboard">
        {/* Header Skeleton */}
        <div className="h-44 rounded-3xl bg-slate-200/70 animate-pulse" />
        {/* KPI Grid Skeleton */}
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-28 rounded-2xl bg-slate-200/60 animate-pulse" />
          ))}
        </div>
        {/* Content Skeleton */}
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="h-80 rounded-2xl bg-slate-200/50 animate-pulse lg:col-span-2" />
          <div className="h-80 rounded-2xl bg-slate-200/50 animate-pulse" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 anim-page-enter">
      {/* ── 1. Page Eyebrow & Intelligent Header ── */}
      <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="text-[10px] font-bold uppercase tracking-[0.14em] text-[#087f76]">
            {isHindi ? "क्षमता अवलोकन" : "Civil Service Capability Overview"}
          </div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[#123057] mt-0.5">
            {getGreeting(user?.full_name)}
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            {isHindi
              ? "यहाँ आपका वर्तमान क्षमता अवलोकन और सीखने की प्रगति है।"
              : "Here is your verified capability overview and role-grounded learning progress."}
          </p>
        </div>

        <div className="mt-2 flex items-center gap-2 sm:mt-0">
          <span className="inline-flex items-center gap-1.5 rounded-full border border-teal-200 bg-teal-50/80 px-2.5 py-0.5 text-[10px] font-semibold text-teal-800 shadow-2xs">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Active Assessment Cycle
          </span>
        </div>
      </div>

      {/* ── 2. Hero Capability Summary ── */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-[#123057] via-[#163866] to-[#087f76] p-5 sm:p-6 text-white shadow-md anim-fade-up">
        <div className="absolute -right-16 -top-16 h-64 w-64 rounded-full border border-white/10 pointer-events-none" />
        <div className="absolute -bottom-20 -left-12 h-56 w-56 rounded-full border border-[#38d9c0]/15 pointer-events-none" />

        <div className="relative z-10 flex flex-col justify-between gap-5 lg:flex-row lg:items-center">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-1.5 rounded-full bg-white/10 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider backdrop-blur-md anim-badge-pop text-[#8ce9dc]">
              <Sparkles size={12} className="text-[#38d9c0]" />
              Civil Service Competency Standard
            </div>

            <h2 className="mt-2 text-lg sm:text-xl font-bold tracking-tight leading-snug">
              Build the capability your role demands.
            </h2>

            <div className="mt-1.5 flex flex-wrap items-center gap-2 text-xs text-blue-100">
              <span className="flex items-center gap-1 font-medium">
                <Briefcase size={13} className="text-[#38d9c0]" />
                {user?.designation || "Statistical Officer"}
              </span>
              <span>·</span>
              <span className="flex items-center gap-1 font-medium">
                <Building size={13} className="text-[#38d9c0]" />
                {user?.department || "Ministry of Statistics & Programme Implementation"}
              </span>
            </div>

            {/* Quick Metrics in Hero */}
            <div className="mt-4 flex flex-wrap items-center gap-5 border-t border-white/15 pt-4">
              <div>
                <div className="text-[10px] font-bold uppercase tracking-wider text-blue-200">
                  Current Capability
                </div>
                <div className="mt-0.5 text-xl font-bold text-white">
                  {averageLevel != null ? (
                    <NumberReveal value={averageLevel} decimals={1} suffix=" / 5.0" />
                  ) : (
                    <span className="text-base text-amber-300">Pending Assessment</span>
                  )}
                </div>
              </div>

              <div className="h-7 w-px bg-white/20 hidden sm:block" />

              <div>
                <div className="text-[10px] font-bold uppercase tracking-wider text-blue-200">
                  Evidence Confidence
                </div>
                <div className="mt-0.5 text-xl font-bold text-[#38d9c0]">
                  {averageConfidence != null ? (
                    <NumberReveal value={Math.round(averageConfidence * 100)} suffix="%" />
                  ) : (
                    <span className="text-base text-slate-300">—</span>
                  )}
                </div>
              </div>

              <div className="h-7 w-px bg-white/20 hidden sm:block" />

              <div>
                <div className="text-[10px] font-bold uppercase tracking-wider text-blue-200">
                  Priority Gaps
                </div>
                <div className="mt-0.5 text-xl font-bold text-[#ef7e37]">
                  <NumberReveal value={priorityGaps.length} suffix=" Gaps" />
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col gap-2 sm:flex-row lg:flex-col lg:items-stretch lg:min-w-[180px] shrink-0">
            <button
              onClick={() => onNavigate("Assessments")}
              className="inline-flex items-center justify-center gap-1.5 rounded-xl bg-[#ef7e37] px-4 py-2.5 text-xs font-bold text-white shadow-sm hover:bg-[#d96a27] transition-all active:scale-[0.98] btn-interactive"
            >
              <ClipboardCheck size={15} />
              Take Assessment
            </button>
            <button
              onClick={() => onNavigate("My Competencies")}
              className="inline-flex items-center justify-center gap-1.5 rounded-xl border border-white/25 bg-white/10 px-4 py-2 text-xs font-semibold text-white backdrop-blur-md hover:bg-white/20 transition-all active:scale-[0.98] btn-interactive"
            >
              <Layers size={15} />
              View Competencies
            </button>
            <button
              onClick={() => onNavigate("Recommendations")}
              className="inline-flex items-center justify-center gap-1.5 rounded-xl border border-white/15 bg-white/5 px-4 py-1.5 text-[11px] font-medium text-slate-200 hover:bg-white/10 transition-all"
            >
              <BookOpen size={13} />
              Browse Courses
            </button>
          </div>
        </div>
      </div>

      {/* ── 3. Core Dashboard KPI Cards (5 compact cards) ── */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        {/* Card 1: Overall Capability */}
        <div
          onClick={() => onNavigate("Progress Tracking")}
          className="cursor-pointer rounded-xl border border-[#dfe7f0] bg-white p-3.5 sm:p-4 shadow-2xs hover:shadow-sm hover:border-teal-300 transition-all card-interactive group"
        >
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Capability
            </span>
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-teal-50 text-[#087f76] group-hover:scale-110 transition-transform">
              <Gauge size={15} />
            </div>
          </div>
          <div className="mt-2">
            <div className="text-lg font-bold text-[#123057]">
              {averageLevel != null ? (
                <NumberReveal value={averageLevel} decimals={1} suffix=" / 5.0" />
              ) : (
                <span className="text-sm text-amber-600">Pending</span>
              )}
            </div>
            <div className="mt-0.5 text-[10px] font-medium text-slate-500 truncate">
              {averageConfidence != null
                ? `${Math.round(averageConfidence * 100)}% confidence`
                : "Assessment required"}
            </div>
          </div>
        </div>

        {/* Card 2: Priority Skill Gaps */}
        <div
          onClick={() => onNavigate("Skill Gaps")}
          className="cursor-pointer rounded-xl border border-[#dfe7f0] bg-white p-3.5 sm:p-4 shadow-2xs hover:shadow-sm hover:border-amber-300 transition-all card-interactive group"
        >
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Skill Gaps
            </span>
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-amber-50 text-[#ef7e37] group-hover:scale-110 transition-transform">
              <Target size={15} />
            </div>
          </div>
          <div className="mt-2">
            <div className="text-lg font-bold text-[#ef7e37]">
              <NumberReveal value={priorityGaps.length} />
            </div>
            <div className="mt-0.5 text-[10px] font-medium text-slate-500 truncate">
              {priorityGaps.length > 0
                ? `${priorityGaps.filter((g) => g.gap_category === "CRITICAL").length} critical priority`
                : "No active gaps"}
            </div>
          </div>
        </div>

        {/* Card 3: Recommended Learning */}
        <div
          onClick={() => onNavigate("Recommendations")}
          className="cursor-pointer rounded-xl border border-[#dfe7f0] bg-white p-3.5 sm:p-4 shadow-2xs hover:shadow-sm hover:border-blue-300 transition-all card-interactive group"
        >
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Recommended
            </span>
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-50 text-blue-700 group-hover:scale-110 transition-transform">
              <BookOpen size={15} />
            </div>
          </div>
          <div className="mt-2">
            <div className="text-lg font-bold text-[#123057]">
              <NumberReveal value={recommendations?.total ?? activeRecs.length} />
            </div>
            <div className="mt-0.5 text-[10px] font-medium text-slate-500 truncate">
              iGOT & NSSTA programmes
            </div>
          </div>
        </div>

        {/* Card 4: Learning Progress */}
        <div
          onClick={() => onNavigate("My Learning")}
          className="cursor-pointer rounded-xl border border-[#dfe7f0] bg-white p-3.5 sm:p-4 shadow-2xs hover:shadow-sm hover:border-purple-300 transition-all card-interactive group"
        >
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Learning
            </span>
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-purple-50 text-purple-700 group-hover:scale-110 transition-transform">
              <GraduationCap size={15} />
            </div>
          </div>
          <div className="mt-2">
            <div className="text-lg font-bold text-[#123057]">
              <NumberReveal value={completedActivities.length} />
            </div>
            <div className="mt-0.5 text-[10px] font-medium text-slate-500 truncate">
              completed · {inProgressActivities.length} active
            </div>
          </div>
        </div>

        {/* Card 5: Quizzes & Evidence */}
        <div
          onClick={() => onNavigate("Quizzes")}
          className="cursor-pointer rounded-xl border border-[#dfe7f0] bg-white p-3.5 sm:p-4 shadow-2xs hover:shadow-sm hover:border-emerald-300 transition-all card-interactive group col-span-2 sm:col-span-1"
        >
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Quizzes & Evidence
            </span>
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-emerald-50 text-emerald-700 group-hover:scale-110 transition-transform">
              <ClipboardCheck size={15} />
            </div>
          </div>
          <div className="mt-2">
            <div className="text-lg font-bold text-[#123057]">
              <NumberReveal value={assignedQuizzes.length} />
            </div>
            <div className="mt-0.5 text-[10px] font-medium text-slate-500 truncate">
              {assignedQuizzes.length} assigned · {evidenceList.length} verified
            </div>
          </div>
        </div>
      </div>

      {/* ── 4. Continuous Learning Loop (Core Architecture Visual) ── */}
      <div className="rounded-2xl border border-[#dfe7f0] bg-white p-5 sm:p-6 shadow-2xs">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-slate-100 gap-2">
          <div>
            <div className="text-[10px] font-bold uppercase tracking-wider text-[#087f76]">
              ShikshaSetu Closed-Loop Framework
            </div>
            <h3 className="text-base font-bold text-[#123057]">
              The Capability Intelligence Lifecycle
            </h3>
          </div>
          <span className="text-[11px] font-medium text-slate-400">
            Click any phase to navigate directly
          </span>
        </div>

        <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-4 lg:grid-cols-7">
          {learningLoopSteps.map((step, idx) => {
            const Icon = step.icon;
            return (
              <button
                key={step.id}
                onClick={() => onNavigate(step.id)}
                className="flex flex-col items-start p-3 rounded-xl border border-slate-100 bg-[#f8fafc] hover:bg-teal-50/60 hover:border-teal-200 transition-all text-left group active:scale-[0.98]"
              >
                <div className="flex items-center justify-between w-full">
                  <span className="text-[10px] font-extrabold text-slate-400 font-mono">
                    {step.num}
                  </span>
                  <div className={`p-1 rounded-lg ${step.color} group-hover:scale-110 transition-transform`}>
                    <Icon size={14} />
                  </div>
                </div>
                <div className="mt-2 text-xs font-bold text-[#123057] group-hover:text-[#087f76] transition-colors">
                  {step.label}
                </div>
                <div className="text-[10px] text-slate-500 truncate w-full mt-0.5">
                  {step.desc}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* ── 5. Main Middle Grid: Priority Skill Gaps & Recommended Learning ── */}
      <AnimatedSection className="grid gap-6 lg:grid-cols-3">
        {/* Priority Skill Gaps Section (2 Columns) */}
        <div className="rounded-2xl border border-[#dfe7f0] bg-white p-6 shadow-2xs lg:col-span-2 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <div>
                <h2 className="text-lg font-bold text-[#123057]">Priority Skill Gaps</h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Focus on the competencies that need the most improvement for your official role.
                </p>
              </div>
              <button
                onClick={() => onNavigate("Skill Gaps")}
                className="inline-flex items-center gap-1 rounded-lg bg-teal-50 px-3 py-1.5 text-xs font-bold text-teal-800 hover:bg-teal-100 transition-colors btn-interactive"
              >
                Full Analysis <ArrowRight size={12} />
              </button>
            </div>

            <div className="mt-5 space-y-3.5">
              {priorityGaps.length === 0 ? (
                <div className="rounded-xl border border-dashed border-emerald-200 bg-emerald-50/40 p-8 text-center anim-fade-in">
                  <CheckCircle2 size={28} className="mx-auto text-emerald-600 anim-badge-pop" />
                  <h3 className="mt-2 text-sm font-bold text-emerald-900">
                    No active skill gaps identified
                  </h3>
                  <p className="mt-1 text-xs text-emerald-700 max-w-md mx-auto">
                    You are currently meeting all proficiency benchmarks for your role. Take an assessment to unlock higher mastery levels.
                  </p>
                  <button
                    onClick={() => onNavigate("Assessments")}
                    className="mt-4 inline-flex items-center gap-2 rounded-xl bg-[#087f76] px-4 py-2 text-xs font-bold text-white shadow-xs hover:bg-[#06635c] transition-all"
                  >
                    Take Assessment
                  </button>
                </div>
              ) : (
                priorityGaps.slice(0, 3).map((gap, idx) => {
                  const current = gap.current_level || 0;
                  const required = gap.required_level || 4.0;
                  const pct = Math.min(100, Math.round((current / required) * 100));
                  const cleanName = getCleanCompetencyName(gap.competency_name, gap.competency_code);

                  const isCritical = gap.gap_category === "CRITICAL";

                  return (
                    <div
                      key={gap.competency_id || idx}
                      className="rounded-xl border border-slate-100 bg-[#f8fafc] p-4.5 transition-all hover:border-teal-200 hover:shadow-2xs group"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-teal-700">
                              {gap.domain || "STATISTICAL"}
                            </span>
                            <span className="text-[9px] font-mono text-slate-400">
                              {gap.competency_code}
                            </span>
                          </div>
                          <h4 className="text-sm font-bold text-[#123057] mt-0.5">
                            {cleanName}
                          </h4>
                        </div>

                        <span
                          className={`rounded-full px-2.5 py-0.5 text-[10px] font-bold shrink-0 ${
                            isCritical
                              ? "bg-red-50 text-red-700 border border-red-200"
                              : "bg-orange-50 text-orange-700 border border-orange-200"
                          }`}
                        >
                          Gap: {gap.gap.toFixed(1)} {isCritical ? "· Critical" : ""}
                        </span>
                      </div>

                      {/* Level Progress Indicator */}
                      <div className="mt-3">
                        <div className="flex justify-between text-[11px] font-semibold text-slate-500 mb-1">
                          <span>
                            Current: <strong className="text-[#123057]">{current.toFixed(1)}</strong>
                          </span>
                          <span>
                            Required: <strong className="text-[#123057]">{required.toFixed(1)}</strong>
                          </span>
                        </div>
                        <ProgressBarFill
                          percent={pct}
                          className="h-2 w-full overflow-hidden rounded-full bg-slate-200"
                          fillClassName={`h-full rounded-full ${
                            isCritical ? "bg-[#ef7e37]" : "bg-[#087f76]"
                          }`}
                          durationMs={650}
                        />
                      </div>

                      <div className="mt-3 flex items-center justify-between border-t border-slate-200/60 pt-2.5 text-xs">
                        <span className="text-[11px] text-slate-400">
                          Priority {gap.priority} · {Math.round((gap.confidence ?? 0.8) * 100)}% evidence confidence
                        </span>
                        <button
                          onClick={() =>
                            onNavigate("Recommendations", { competencyCode: gap.competency_code })
                          }
                          className="font-bold text-[#ef7e37] hover:text-[#d96a27] inline-flex items-center gap-1 transition-colors"
                        >
                          View Recommendations <ArrowRight size={11} />
                        </button>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>

        {/* Next Best Action Card (1 Column) */}
        <div className="flex flex-col justify-between rounded-2xl bg-[#123057] p-6 text-white shadow-md relative overflow-hidden">
          <div className="relative z-10">
            <div className="inline-flex items-center gap-1.5 rounded-full bg-white/10 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-[#38d9c0] anim-badge-pop">
              <TrendingUp size={12} /> Next Best Action
            </div>

            <h3 className="mt-3 text-lg font-bold">
              {topGap
                ? `Close your ${getCleanCompetencyName(topGap.competency_name, topGap.competency_code)} gap`
                : "Verify Core Competencies"}
            </h3>

            {(() => {
              const resourceTitle = getRecommendationTitle(topRec);
              const provider = getRecommendationProvider(topRec);

              return (
                <p className="mt-2 text-xs text-slate-200 leading-relaxed">
                  {topRec
                    ? `Recommended curriculum: "${resourceTitle}" from ${provider}. Specifically curated to close your highest priority deficit.`
                    : "Engage in recommended learning resources from iGOT Karmayogi and NSSTA to update your capability score."}
                </p>
              );
            })()}

            {topGap && (
              <div className="mt-5 rounded-xl bg-white/10 p-3.5 backdrop-blur-sm border border-white/10">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-slate-300">Target Proficiency:</span>
                  <span className="text-[#38d9c0] font-bold">Level {topGap.required_level.toFixed(1)} / 5.0</span>
                </div>
                <div className="mt-1 text-[11px] text-slate-300">
                  Priority deficit: <strong>{topGap.gap.toFixed(1)} points</strong>
                </div>
              </div>
            )}
          </div>

          <div className="relative z-10 mt-6 pt-4 border-t border-white/10 flex flex-col gap-2">
            <button
              onClick={() => onNavigate("Recommendations")}
              className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-[#ef7e37] py-2.5 text-xs font-bold text-white shadow hover:bg-[#d96a27] transition-all active:scale-[0.98] btn-interactive"
            >
              Start Recommended Learning <ArrowRight size={13} />
            </button>
            <button
              onClick={() => onNavigate("Assessments")}
              className="w-full inline-flex items-center justify-center gap-1 rounded-xl bg-white/10 py-2 text-xs font-bold text-white hover:bg-white/20 transition-all active:scale-[0.98] btn-interactive"
            >
              Take Capability Assessment
            </button>
          </div>
        </div>
      </AnimatedSection>

      {/* ── 6. Recommended Learning Preview (With Clear "WHY RECOMMENDED") ── */}
      <div className="rounded-2xl border border-[#dfe7f0] bg-white p-6 shadow-2xs">
        <div className="flex items-center justify-between border-b border-slate-100 pb-4">
          <div>
            <h3 className="text-lg font-bold text-[#123057]">Recommended For You</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Targeted learning resources matched to your competency gaps, role, and required proficiency.
            </p>
          </div>
          <button
            onClick={() => onNavigate("Recommendations")}
            className="inline-flex items-center gap-1 rounded-lg bg-teal-50 px-3 py-1.5 text-xs font-bold text-teal-800 hover:bg-teal-100 transition-colors btn-interactive"
          >
            All Courses ({recommendations?.total ?? activeRecs.length}) <ArrowRight size={12} />
          </button>
        </div>

        <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {activeRecs.length === 0 ? (
            <div className="col-span-3 text-center py-8 text-slate-400 text-xs">
              No recommended courses found. Check back once your capability assessment is submitted.
            </div>
          ) : (
            activeRecs.map((rec, i) => {
              const title = getRecommendationTitle(rec);
              const provider = getRecommendationProvider(rec);
              const compName = getCleanCompetencyName(rec.competency_name, rec.competency_code);

              return (
                <div
                  key={i}
                  className="flex flex-col justify-between rounded-xl border border-slate-100 bg-[#f8fafc] p-4.5 hover:border-teal-200 hover:shadow-2xs transition-all group"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="rounded-md bg-teal-100/80 px-2 py-0.5 text-[10px] font-bold text-[#087f76]">
                        {provider}
                      </span>
                      <span className="text-[10px] font-semibold text-slate-400">
                        {rec.resource && typeof rec.resource === "object" && (rec.resource as any).metadata?.duration_hours
                          ? `${(rec.resource as any).metadata.duration_hours}h · Course`
                          : "Curriculum"}
                      </span>
                    </div>

                    <h4 className="text-sm font-bold text-[#123057] group-hover:text-[#087f76] transition-colors line-clamp-2">
                      {title}
                    </h4>

                    {/* Explanatory "Why Recommended" checklist */}
                    <div className="mt-3.5 space-y-1.5 border-t border-slate-200/60 pt-3 text-[11px] text-slate-600">
                      <div className="flex items-start gap-1.5">
                        <CheckCircle2 size={13} className="text-emerald-600 mt-0.5 shrink-0" />
                        <span>
                          Targeted to close <strong>{compName}</strong> gap
                        </span>
                      </div>
                      <div className="flex items-start gap-1.5">
                        <CheckCircle2 size={13} className="text-emerald-600 mt-0.5 shrink-0" />
                        <span>Aligned to {user?.designation || "official role"} requirements</span>
                      </div>
                      <div className="flex items-start gap-1.5">
                        <CheckCircle2 size={13} className="text-emerald-600 mt-0.5 shrink-0" />
                        <span>Target proficiency: Level {(rec as any).required_level != null ? Number((rec as any).required_level).toFixed(1) : "4.0"}</span>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-200/50 flex items-center justify-between">
                    <span className="text-[10px] font-semibold text-slate-400">
                      Score: {Math.round(((rec.score ?? rec.relevance_score ?? 0.85) * 100))}% match
                    </span>
                    <button
                      onClick={() => onNavigate("Recommendations")}
                      className="inline-flex items-center gap-1 text-xs font-bold text-[#ef7e37] hover:underline"
                    >
                      View Course <ArrowRight size={11} />
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* ── 7. Two Column Row: Learning & Quizzes + Recent Activity Timeline ── */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Column 1: Continue Learning & Assigned Quizzes */}
        <div className="rounded-2xl border border-[#dfe7f0] bg-white p-6 shadow-2xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <div>
                <h3 className="text-base font-bold text-[#123057]">Your Learning & Quizzes</h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Assigned tests and ongoing courses ready for your engagement.
                </p>
              </div>
              <button
                onClick={() => onNavigate("Quizzes")}
                className="text-xs font-bold text-teal-700 hover:underline"
              >
                View All Quizzes
              </button>
            </div>

            <div className="mt-4 space-y-3">
              {assignedQuizzes.length > 0 ? (
                assignedQuizzes.slice(0, 2).map((quiz, i) => (
                  <div
                    key={quiz._id || i}
                    className="flex items-center justify-between p-3.5 rounded-xl border border-slate-100 bg-[#f8fafc] hover:border-teal-200 transition-all"
                  >
                    <div className="min-w-0 flex-1 pr-3">
                      <div className="flex items-center gap-2">
                        <span className="rounded bg-purple-100 px-1.5 py-0.5 text-[9px] font-bold text-purple-800">
                          QUIZ
                        </span>
                        <span className="text-[10px] text-slate-400 font-medium">
                          {quiz.question_count || 5} Questions
                        </span>
                      </div>
                      <h5 className="text-xs font-bold text-[#123057] mt-1 truncate">
                        {quiz.title}
                      </h5>
                    </div>
                    <button
                      onClick={() => onNavigate("Quizzes")}
                      className="shrink-0 rounded-lg bg-[#087f76] px-3 py-1.5 text-xs font-bold text-white hover:bg-[#06635c] transition-colors shadow-2xs"
                    >
                      Take Quiz
                    </button>
                  </div>
                ))
              ) : null}

              {inProgressActivities.length > 0 ? (
                inProgressActivities.slice(0, 2).map((act, i) => (
                  <div
                    key={act.activity_id || i}
                    className="flex items-center justify-between p-3.5 rounded-xl border border-slate-100 bg-[#f8fafc] hover:border-teal-200 transition-all"
                  >
                    <div className="min-w-0 flex-1 pr-3">
                      <div className="flex items-center gap-2">
                        <span className="rounded bg-teal-100 px-1.5 py-0.5 text-[9px] font-bold text-teal-800">
                          IN PROGRESS
                        </span>
                        <span className="text-[10px] text-slate-400 font-medium">
                          {act.progress_percent || 0}% Complete
                        </span>
                      </div>
                      <h5 className="text-xs font-bold text-[#123057] mt-1 truncate">
                        {act.resource_id}
                      </h5>
                    </div>
                    <button
                      onClick={() => onNavigate("My Learning")}
                      className="shrink-0 rounded-lg bg-teal-50 px-3 py-1.5 text-xs font-bold text-teal-800 hover:bg-teal-100 transition-colors"
                    >
                      Resume
                    </button>
                  </div>
                ))
              ) : null}

              {assignedQuizzes.length === 0 && inProgressActivities.length === 0 && (
                <div className="text-center py-6 text-slate-400 text-xs">
                  No pending quizzes or active learning sessions.
                </div>
              )}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
            <span className="text-slate-400">Total Assigned: {assignedQuizzes.length}</span>
            <button
              onClick={() => onNavigate("My Learning")}
              className="text-xs font-bold text-[#ef7e37] hover:underline inline-flex items-center gap-1"
            >
              Open Learning Tracker <ArrowRight size={11} />
            </button>
          </div>
        </div>

        {/* Column 2: Recent Activity Timeline */}
        <div className="rounded-2xl border border-[#dfe7f0] bg-white p-6 shadow-2xs flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-slate-100 pb-4">
              <div>
                <h3 className="text-base font-bold text-[#123057]">Recent Activity</h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Verified assessment submissions and evidence records.
                </p>
              </div>
              <button
                onClick={() => onNavigate("Evidence Ledger")}
                className="text-xs font-bold text-teal-700 hover:underline"
              >
                Evidence Ledger
              </button>
            </div>

            <div className="mt-4 space-y-3">
              {evidenceList.length > 0 ? (
                evidenceList.slice(0, 3).map((item, idx) => {
                  const compName = getCleanCompetencyName(item.competency_name, item.competency_code);
                  const isAuthoritative = item.type === "AUTHORITATIVE";

                  return (
                    <div
                      key={item.id || idx}
                      className="flex items-start gap-3 p-3 rounded-xl border border-slate-100 bg-[#f8fafc]"
                    >
                      <div className="mt-0.5 p-1.5 rounded-lg bg-teal-50 text-[#087f76] shrink-0">
                        <FileCheck size={15} />
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between gap-2">
                          <h5 className="text-xs font-bold text-[#123057] truncate">
                            {item.title || `Competency: ${compName}`}
                          </h5>
                          <span className="text-[10px] font-mono text-slate-400 shrink-0">
                            {item.date ? item.date.slice(0, 10) : "Verified"}
                          </span>
                        </div>
                        <div className="mt-1 flex items-center gap-2 text-[11px] text-slate-500">
                          <span className="font-semibold text-teal-800">
                            Level {item.normalized_level || item.score || 3.0}
                          </span>
                          <span>·</span>
                          <span>{Math.round((item.confidence || 0.7) * 100)}% Confidence</span>
                          <span>·</span>
                          <span className="rounded bg-slate-100 px-1 py-0.2 text-[9px] font-bold text-slate-600">
                            {isAuthoritative ? "Authoritative" : "Supporting"}
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="text-center py-6 text-slate-400 text-xs">
                  No verified activity records yet. Complete a capability assessment to log evidence.
                </div>
              )}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
            <span className="text-slate-400">Total Evidence: {evidenceList.length}</span>
            <button
              onClick={() => onNavigate("Evidence Ledger")}
              className="text-xs font-bold text-[#ef7e37] hover:underline inline-flex items-center gap-1"
            >
              Inspect Audit Records <ArrowRight size={11} />
            </button>
          </div>
        </div>
      </div>

      {/* ── 8. Civic Capability Integrity Principle Notice ── */}
      <div className="rounded-2xl border border-teal-100 bg-teal-50/50 p-5 flex items-start gap-4">
        <div className="mt-0.5 text-teal-800 shrink-0">
          <ShieldCheck size={22} />
        </div>
        <div className="text-xs text-slate-600 leading-relaxed">
          <strong className="text-[#123057] font-semibold">
            Civic Capability Integrity Principle:
          </strong>{" "}
          Completing learning courses and practice quizzes logs{" "}
          <span className="font-bold text-teal-800">Supporting Evidence (0.30 confidence)</span>. To formally validate mastery and update your official civil service competency profile, complete a standardized{" "}
          <span className="font-bold text-[#123057]">Capability Assessment (1.00 confidence)</span>.
        </div>
      </div>
    </div>
  );
}

export default OfficialDashboard;
