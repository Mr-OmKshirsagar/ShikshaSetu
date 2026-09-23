import React, { useEffect, useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  Award,
  BookOpen,
  Briefcase,
  Building2,
  CheckCircle2,
  Compass,
  FileBarChart,
  Gauge,
  GraduationCap,
  Layers,
  RefreshCw,
  ShieldCheck,
  Sparkles,
  Target,
  TrendingUp,
  Users,
} from "lucide-react";
import { api, clearApiCache, AdminDashboardResponse } from "@/lib/api";
import { DEPARTMENT_TAXONOMY } from "@/lib/departments";
import { toast } from "sonner";
import { NumberReveal, ProgressBarFill } from "@/components/motion/MotionUtils";
import { useTranslation } from "@/i18n";

interface AdminDashboardProps {
  onNavigate: (page: string) => void;
}

export function AdminDashboard({ onNavigate }: AdminDashboardProps) {
  const { t, isHindi } = useTranslation();
  const [data, setData] = useState<AdminDashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedDepartment, setSelectedDepartment] = useState<string>("ALL");

  const fetchDashboard = async (dept?: string) => {
    clearApiCache();
    try {
      setLoading(true);
      const targetDept = dept !== undefined ? dept : selectedDepartment;
      const res = await api.admin.dashboard(targetDept === "ALL" ? undefined : targetDept);
      setData(res);
    } catch (err: any) {
      toast.error(err?.message || "Failed to load admin dashboard data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard(selectedDepartment);
  }, [selectedDepartment]);

  // Priority skill gaps matching ShikshaSetu framework
  const prioritySkillGaps = [
    {
      code: "GOV_DIGITAL · STRATEGIC",
      name: "Digital Governance",
      current: 2.8,
      required: 4.0,
      gap: 1.2,
      confidence: 88,
      priority: 1,
    },
    {
      code: "STAT_DATA_ANALYSIS · TECHNICAL",
      name: "Data Analysis",
      current: 3.1,
      required: 4.0,
      gap: 0.9,
      confidence: 82,
      priority: 1,
    },
    {
      code: "STAT_METHODS · STATISTICAL",
      name: "Statistical Methods",
      current: 3.0,
      required: 4.0,
      gap: 1.0,
      confidence: 80,
      priority: 2,
    },
    {
      code: "SEC_GOV · COMPLIANCE",
      name: "Cybersecurity Awareness",
      current: 2.6,
      required: 4.0,
      gap: 1.4,
      confidence: 91,
      priority: 1,
    },
  ];

  // Ministry & Department breakdown data
  const ministryRows = [
    {
      name: "Ministry of Statistics & Programme Implementation",
      officials: 342,
      avgCapability: "3.2 / 5.0",
      skillGaps: 38,
      badge: "MoSPI",
    },
    {
      name: "Ministry of Education",
      officials: 286,
      avgCapability: "3.0 / 5.0",
      skillGaps: 34,
      badge: "MoE",
    },
    {
      name: "Ministry of Health & Family Welfare",
      officials: 245,
      avgCapability: "3.3 / 5.0",
      skillGaps: 26,
      badge: "MoHFW",
    },
    {
      name: "Ministry of Rural Development",
      officials: 198,
      avgCapability: "2.9 / 5.0",
      skillGaps: 29,
      badge: "MoRD",
    },
    {
      name: "Ministry of Finance",
      officials: 177,
      avgCapability: "3.4 / 5.0",
      skillGaps: 16,
      badge: "MoF",
    },
  ];

  // AI Insights matching ShikshaSetu platform analysis
  const aiInsights = [
    "MoSPI has the highest concentration of statistical competency gaps.",
    "23 officials are approaching their required competency level.",
    "12 trainers have expertise aligned with emerging capacity-building needs.",
    "Digital Governance competency improved across recently completed programmes.",
  ];

  // Action/Attention items
  const attentionItems = [
    {
      text: "37 officials below required competency level",
      color: "bg-rose-500",
      bgBadge: "bg-rose-50 text-rose-700 border-rose-200",
      action: "Review Officials",
      targetPage: "Workforce Overview",
    },
    {
      text: "12 assessments pending review",
      color: "bg-amber-500",
      bgBadge: "bg-amber-50 text-amber-700 border-amber-200",
      action: "Open Queue",
      targetPage: "Users",
    },
    {
      text: "8 training programmes with low completion",
      color: "bg-amber-500",
      bgBadge: "bg-amber-50 text-amber-700 border-amber-200",
      action: "View Courses",
      targetPage: "Training Effectiveness",
    },
    {
      text: "24 trainer profiles ready for opportunity matching",
      color: "bg-teal-500",
      bgBadge: "bg-teal-50 text-teal-700 border-teal-200",
      action: "Match Profiles",
      targetPage: "Opportunity Network",
    },
  ];

  // Top expertise areas for Trainer Intelligence
  const topExpertiseAreas = [
    "Statistical Methods",
    "Digital Governance",
    "Data Analytics",
    "Leadership",
    "Survey Design",
  ];

  if (loading && !data) {
    return (
      <div className="space-y-8 animate-fadeIn">
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-[#1e3a5f] via-[#2d1b4e] to-[#4a1d6f] p-7 sm:p-8 text-white shadow-lg">
          <div className="h-6 w-52 rounded-full bg-white/20 animate-pulse" />
          <div className="mt-3.5 h-9 w-80 rounded-xl bg-white/30 animate-pulse" />
          <div className="mt-2 h-4 w-96 rounded bg-white/20 animate-pulse" />
        </div>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-28 rounded-2xl bg-white border border-[#dfe7f0] p-5 shadow-xs animate-pulse" />
          ))}
        </div>
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="h-72 rounded-3xl bg-white border border-[#dfe7f0] p-6 shadow-xs animate-pulse" />
          <div className="h-72 rounded-3xl bg-white border border-[#dfe7f0] p-6 shadow-xs animate-pulse" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 anim-page-enter">
      {/* ── 4. Main Hero Section (ShikshaSetu Official Greeting Treatment) ── */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-[#1e3a5f] via-[#2d1b4e] to-[#4a1d6f] p-7 sm:p-8 text-white shadow-lg anim-fade-up">
        <div className="absolute inset-0 bg-gradient-to-br from-transparent via-purple-900/20 to-transparent opacity-50" />
        <div className="relative z-10 flex flex-col justify-between gap-6 md:flex-row md:items-center">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full bg-white/15 px-2.5 py-1 text-[11px] font-bold uppercase tracking-wider backdrop-blur-md anim-badge-pop text-purple-200">
              <Sparkles size={12} className="text-purple-200" />
              {isHindi ? "राष्ट्रीय कार्यबल क्षमता मंच" : "National Workforce Capability Platform"}
            </div>
            <h1 className="mt-2.5 text-2xl font-extrabold tracking-tight sm:text-[32px] leading-tight">
              National Workforce Capability
            </h1>
            <p className="mt-1.5 text-[13px] text-purple-100 max-w-2xl leading-relaxed">
              Monitor workforce capability, competency gaps, training effectiveness and capacity-building progress across government departments.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2.5 md:ml-auto md:flex-nowrap md:justify-end">
            {/* Department Dropdown */}
            <select
              value={selectedDepartment}
              onChange={(e) => setSelectedDepartment(e.target.value)}
              className="rounded-xl border border-white/20 bg-white/10 px-3.5 py-2.5 text-[13px] font-semibold text-white backdrop-blur-md focus:border-purple-300 focus:outline-none hover:bg-white/15 transition-all cursor-pointer"
              aria-label="Filter by department"
            >
              <option value="ALL" className="text-slate-800">
                All Ministries & Departments
              </option>
              {DEPARTMENT_TAXONOMY.slice(0, 10).map((d) => (
                <option key={d.department_code} value={d.department_name} className="text-slate-800">
                  {d.department_name}
                </option>
              ))}
            </select>

            {/* Refresh Button */}
            <button
              onClick={() => fetchDashboard()}
              className="inline-flex shrink-0 items-center gap-1.5 whitespace-nowrap rounded-xl bg-[#ef7e37] px-4 py-2.5 text-[13px] font-bold text-white shadow-md hover:bg-[#d96a27] transition-all cursor-pointer btn-interactive"
              title="Refresh Dashboard Data"
            >
              <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
              <span>Refresh</span>
            </button>
          </div>
        </div>
      </div>

      {/* ── 5. KPI Stat Cards (Matching Official Dashboard Card Treatment) ── */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {/* Total Officials */}
        <div className="rounded-2xl border border-[#dfe7f0] bg-white p-5 shadow-xs hover:shadow-md transition-shadow card-interactive anim-card-enter stagger-1 group">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Total Officials
            </span>
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-50 text-blue-700 icon-interactive">
              <Users size={18} />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-2xl sm:text-3xl font-bold tracking-tight text-[#123057]">
              {data?.total_officials != null ? (
                <NumberReveal value={data.total_officials} />
              ) : (
                "1,248"
              )}
            </span>
          </div>
          <div className="mt-2 text-[11px] text-slate-500 font-medium">
            Across government departments
          </div>
        </div>

        {/* Average Capability */}
        <div className="rounded-2xl border border-[#dfe7f0] bg-white p-5 shadow-xs hover:shadow-md transition-shadow card-interactive anim-card-enter stagger-2 group">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Average Capability
            </span>
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-teal-50 text-[#087f76] icon-interactive">
              <Gauge size={18} />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-1.5">
            <span className="text-2xl sm:text-3xl font-bold tracking-tight text-[#123057]">
              {data?.average_capability_level != null ? (
                <NumberReveal value={data.average_capability_level} decimals={1} />
              ) : (
                "3.1"
              )}
            </span>
            <span className="text-xs font-semibold text-slate-400">/ 5.0</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-500 font-medium">
            {data?.assessment_coverage_pct != null
              ? `${data.assessment_coverage_pct}% assessment coverage`
              : "73% assessment coverage"}
          </div>
        </div>

        {/* Critical Skill Gaps */}
        <div className="rounded-2xl border border-[#dfe7f0] bg-white p-5 shadow-xs hover:shadow-md transition-shadow card-interactive anim-card-enter stagger-3 group">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Critical Skill Gaps
            </span>
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-rose-50 text-rose-600 icon-interactive">
              <AlertTriangle size={18} />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-2xl sm:text-3xl font-bold tracking-tight text-rose-600">
              {data?.total_critical_gaps != null ? (
                <NumberReveal value={data.total_critical_gaps} />
              ) : (
                "143"
              )}
            </span>
          </div>
          <div className="mt-2 text-[11px] text-slate-500 font-medium">
            Deficiencies requiring attention
          </div>
        </div>

        {/* Training Effectiveness */}
        <div className="rounded-2xl border border-[#dfe7f0] bg-white p-5 shadow-xs hover:shadow-md transition-shadow card-interactive anim-card-enter stagger-4 group">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Training Effectiveness
            </span>
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-50 text-emerald-700 icon-interactive">
              <Award size={18} />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-1">
            <span className="text-2xl sm:text-3xl font-bold tracking-tight text-[#123057]">
              78
            </span>
            <span className="text-xs font-semibold text-slate-400">%</span>
          </div>
          <div className="mt-2 text-[11px] text-slate-500 font-medium">
            Based on completed programmes
          </div>
        </div>

        {/* Active Trainers */}
        <div className="rounded-2xl border border-[#dfe7f0] bg-white p-5 shadow-xs hover:shadow-md transition-shadow card-interactive anim-card-enter stagger-5 group col-span-2 sm:col-span-1">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Active Trainers
            </span>
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-50 text-indigo-700 icon-interactive">
              <GraduationCap size={18} />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-2xl sm:text-3xl font-bold tracking-tight text-[#123057]">
              86
            </span>
          </div>
          <div className="mt-2 text-[11px] text-slate-500 font-medium">
            Verified trainers
          </div>
        </div>
      </div>

      {/* ── 6. Main Admin Analytics (Two-Column Layout) ── */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Left: Workforce Capability Overview */}
        <div className="rounded-3xl border border-[#dfe7f0] bg-white p-6 shadow-xs anim-card-enter stagger-6">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Capability Distribution
              </span>
              <h2 className="text-lg font-bold text-[#123057] mt-0.5">
                Workforce Capability Overview
              </h2>
            </div>
            <span className="rounded-full bg-[#e8f5f3] px-3 py-1 text-xs font-semibold text-[#087f76]">
              5 Competency Tiers
            </span>
          </div>

          <p className="text-xs text-slate-500 mb-4 leading-relaxed">
            Distribution of competency levels across assessed government officials.
          </p>

          <div className="space-y-3">
            {/* Critical */}
            <div className="rounded-2xl border border-slate-100 bg-[#f8fafc]/70 p-3.5 space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-rose-700 flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-rose-500" />
                  Critical
                </span>
                <span className="font-bold text-[#123057]">18 officials <span className="text-slate-400 font-normal">(1.4%)</span></span>
              </div>
              <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                <div className="h-full rounded-full bg-rose-500" style={{ width: "1.4%" }} />
              </div>
            </div>

            {/* Needs Improvement */}
            <div className="rounded-2xl border border-slate-100 bg-[#f8fafc]/70 p-3.5 space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-amber-700 flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-amber-500" />
                  Needs Improvement
                </span>
                <span className="font-bold text-[#123057]">142 officials <span className="text-slate-400 font-normal">(11.4%)</span></span>
              </div>
              <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                <div className="h-full rounded-full bg-amber-500" style={{ width: "11.4%" }} />
              </div>
            </div>

            {/* Developing */}
            <div className="rounded-2xl border border-slate-100 bg-[#f8fafc]/70 p-3.5 space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-blue-700 flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-blue-500" />
                  Developing
                </span>
                <span className="font-bold text-[#123057]">487 officials <span className="text-slate-400 font-normal">(39.0%)</span></span>
              </div>
              <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                <div className="h-full rounded-full bg-blue-500" style={{ width: "39.0%" }} />
              </div>
            </div>

            {/* Proficient */}
            <div className="rounded-2xl border border-slate-100 bg-[#f8fafc]/70 p-3.5 space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-[#087f76] flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-[#087f76]" />
                  Proficient
                </span>
                <span className="font-bold text-[#123057]">524 officials <span className="text-slate-400 font-normal">(42.0%)</span></span>
              </div>
              <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                <div className="h-full rounded-full bg-[#087f76]" style={{ width: "42.0%" }} />
              </div>
            </div>

            {/* Advanced */}
            <div className="rounded-2xl border border-slate-100 bg-[#f8fafc]/70 p-3.5 space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="font-semibold text-emerald-700 flex items-center gap-1.5">
                  <span className="h-2 w-2 rounded-full bg-emerald-600" />
                  Advanced
                </span>
                <span className="font-bold text-[#123057]">77 officials <span className="text-slate-400 font-normal">(6.2%)</span></span>
              </div>
              <div className="h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                <div className="h-full rounded-full bg-emerald-600" style={{ width: "6.2%" }} />
              </div>
            </div>
          </div>

          <button
            onClick={() => onNavigate("Workforce Overview")}
            className="mt-5 w-full inline-flex items-center justify-center gap-1.5 rounded-xl bg-slate-50 hover:bg-[#e8f5f3] hover:text-[#087f76] px-4 py-2.5 text-xs font-semibold text-[#123057] border border-slate-200 hover:border-[#087f76]/30 transition-all cursor-pointer"
          >
            <span>View Workforce Overview</span>
            <ArrowRight size={13} />
          </button>
        </div>

        {/* Right: Workforce by Ministry / Department */}
        <div className="rounded-3xl border border-[#dfe7f0] bg-white p-6 shadow-xs anim-card-enter stagger-7">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Departmental Metrics
              </span>
              <h2 className="text-lg font-bold text-[#123057] mt-0.5">
                Workforce by Ministry / Department
              </h2>
            </div>
            <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
              5 Ministries Active
            </span>
          </div>

          <p className="text-xs text-slate-500 mb-4 leading-relaxed">
            Active officials, average capability benchmark, and open skill gaps by department.
          </p>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-100 text-slate-400 uppercase tracking-wider font-semibold text-[10px]">
                  <th className="pb-2.5">Ministry / Department</th>
                  <th className="pb-2.5 text-center">Officials</th>
                  <th className="pb-2.5 text-center">Avg. Capability</th>
                  <th className="pb-2.5 text-right">Skill Gaps</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {ministryRows.map((m, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-3 font-semibold text-[#123057]">
                      <div className="truncate max-w-[200px]" title={m.name}>
                        {m.name}
                      </div>
                      <span className="text-[10px] font-medium text-slate-400">{m.badge}</span>
                    </td>
                    <td className="py-3 text-center text-slate-600 font-medium">
                      {m.officials}
                    </td>
                    <td className="py-3 text-center">
                      <span className="inline-block rounded-md bg-[#e8f5f3] px-2 py-0.5 font-bold text-[#087f76] text-[11px]">
                        {m.avgCapability}
                      </span>
                    </td>
                    <td className="py-3 text-right">
                      <span className="font-bold text-rose-600">
                        {m.skillGaps}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <button
            onClick={() => onNavigate("Workforce Overview")}
            className="mt-5 w-full inline-flex items-center justify-center gap-1.5 rounded-xl bg-slate-50 hover:bg-[#e8f5f3] hover:text-[#087f76] px-4 py-2.5 text-xs font-semibold text-[#123057] border border-slate-200 hover:border-[#087f76]/30 transition-all cursor-pointer"
          >
            <span>View All Departments</span>
            <ArrowRight size={13} />
          </button>
        </div>
      </div>

      {/* ── 7. Competency Gap Section (Priority Skill Gaps matching Official Dashboard style) ── */}
      <div className="rounded-3xl border border-[#dfe7f0] bg-white p-6 shadow-xs anim-card-enter stagger-8">
        <div className="mb-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-xl font-bold text-[#123057]">Priority Skill Gaps</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Competency deficiencies requiring targeted capacity building.
            </p>
          </div>
          <button
            onClick={() => onNavigate("Skill Gap Analytics")}
            className="self-start sm:self-auto rounded-full bg-[#e8f5f3] px-3.5 py-1 text-xs font-semibold text-[#087f76] hover:bg-[#d4eee8] transition-all cursor-pointer"
          >
            Full Analysis
          </button>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          {prioritySkillGaps.map((gap, index) => {
            const pct = Math.min(100, Math.round((gap.current / gap.required) * 100));
            return (
              <div
                key={index}
                className="rounded-2xl border border-slate-100 bg-[#f8fafc]/50 p-4 transition-all hover:border-[#087f76]/30 hover:bg-white hover:shadow-xs group"
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold uppercase tracking-wider text-[#087f76]">
                    {gap.code}
                  </span>
                  <span className="rounded-full bg-[#fef3eb] px-2.5 py-0.5 text-xs font-bold text-[#ea580c]">
                    Gap: {gap.gap.toFixed(1)}
                  </span>
                </div>

                <h3 className="mt-1 text-sm font-bold text-[#123057]">
                  {gap.name}
                </h3>

                <div className="mt-3 flex items-center justify-between text-xs text-slate-500 font-medium">
                  <span>Current: {gap.current.toFixed(1)}</span>
                  <span>Required: {gap.required.toFixed(1)}</span>
                </div>

                {/* Progress bar matching Official Dashboard style */}
                <div className="mt-1.5 h-2 w-full rounded-full bg-slate-100 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-[#087f76] transition-all duration-500"
                    style={{ width: `${pct}%` }}
                  />
                </div>

                <div className="mt-3 flex items-center justify-between pt-2 border-t border-slate-100 text-[11px]">
                  <span className="text-slate-400 font-medium">
                    Priority {gap.priority} · {gap.confidence}% confidence
                  </span>
                  <button
                    onClick={() => onNavigate("Skill Gap Analytics")}
                    className="font-semibold text-[#ea580c] hover:underline flex items-center gap-1 cursor-pointer"
                  >
                    Target Interventions <ArrowRight size={11} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── 8 & 9. Training Effectiveness & Trainer Intelligence (Two-Column Layout) ── */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* 8. Training Effectiveness Card */}
        <div className="rounded-3xl border border-[#dfe7f0] bg-white p-6 shadow-xs anim-card-enter stagger-9">
          <div className="mb-4">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Capacity Building Metrics
            </span>
            <h2 className="text-lg font-bold text-[#123057] mt-0.5">
              Training Effectiveness
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Outcome measurements and completion performance from institutional academies.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3.5 mb-4">
            <div className="rounded-2xl bg-[#e8f5f3] p-4 border border-[#cbebe5]">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-[#087f76]">
                Training Programmes
              </span>
              <div className="mt-1 text-2xl font-bold text-[#123057]">142</div>
              <div className="mt-0.5 text-[11px] text-slate-500">Scheduled & completed</div>
            </div>

            <div className="rounded-2xl bg-blue-50/70 p-4 border border-blue-100">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-blue-800">
                Officials Trained
              </span>
              <div className="mt-1 text-2xl font-bold text-[#123057]">2,846</div>
              <div className="mt-0.5 text-[11px] text-slate-500">Across all batches</div>
            </div>

            <div className="rounded-2xl bg-emerald-50/70 p-4 border border-emerald-100">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-emerald-800">
                Completion Rate
              </span>
              <div className="mt-1 text-2xl font-bold text-emerald-700">82%</div>
              <div className="mt-0.5 text-[11px] text-slate-500">National average benchmark</div>
            </div>

            <div className="rounded-2xl bg-[#fef3eb] p-4 border border-orange-100">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-[#ea580c]">
                Avg. Improvement
              </span>
              <div className="mt-1 text-2xl font-bold text-[#ea580c]">+14.6%</div>
              <div className="mt-0.5 text-[11px] text-slate-500">Post-training competency</div>
            </div>
          </div>

          <div className="rounded-2xl bg-[#f8fafc] p-3.5 border border-slate-100 text-xs text-slate-600 flex items-center justify-between">
            <span className="flex items-center gap-2">
              <CheckCircle2 size={15} className="text-emerald-600 shrink-0" />
              <span>Institutional impact measured across 85 NSSTA & iGOT modules.</span>
            </span>
          </div>

          <button
            onClick={() => onNavigate("Training Effectiveness")}
            className="mt-4 flex items-center gap-1.5 text-xs font-semibold text-[#087f76] hover:underline cursor-pointer"
          >
            <span>View Analysis</span>
            <ArrowRight size={13} />
          </button>
        </div>

        {/* 9. Trainer Intelligence Card */}
        <div className="rounded-3xl border border-[#dfe7f0] bg-white p-6 shadow-xs anim-card-enter stagger-10">
          <div className="mb-4">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Faculty Ecosystem
            </span>
            <h2 className="text-lg font-bold text-[#123057] mt-0.5">
              Trainer Network
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Verified government trainers and faculty capacity across partner academies.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-3 mb-4">
            <div className="rounded-2xl bg-[#f8fafc] p-3.5 border border-slate-100 text-center">
              <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                Active Trainers
              </div>
              <div className="mt-1 text-2xl font-bold text-[#123057]">86</div>
              <div className="mt-0.5 text-[10px] text-slate-400">Accredited</div>
            </div>

            <div className="rounded-2xl bg-[#f8fafc] p-3.5 border border-slate-100 text-center">
              <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                Programmes
              </div>
              <div className="mt-1 text-2xl font-bold text-[#123057]">142</div>
              <div className="mt-0.5 text-[10px] text-slate-400">Conducted</div>
            </div>

            <div className="rounded-2xl bg-[#f8fafc] p-3.5 border border-slate-100 text-center">
              <div className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                Officials Trained
              </div>
              <div className="mt-1 text-2xl font-bold text-[#123057]">2,846</div>
              <div className="mt-0.5 text-[10px] text-slate-400">Graduates</div>
            </div>
          </div>

          {/* Top Expertise Areas */}
          <div className="rounded-2xl bg-[#f8fafc] p-4 border border-slate-100">
            <div className="text-xs font-bold text-[#123057] mb-2.5">
              Top Expertise Areas
            </div>
            <div className="flex flex-wrap gap-2">
              {topExpertiseAreas.map((area, idx) => (
                <span
                  key={idx}
                  className="rounded-full bg-white px-3 py-1 text-xs font-medium text-slate-700 border border-slate-200 shadow-2xs"
                >
                  {area}
                </span>
              ))}
            </div>
          </div>

          <button
            onClick={() => onNavigate("Opportunity Network")}
            className="mt-4 flex items-center gap-1.5 text-xs font-semibold text-[#087f76] hover:underline cursor-pointer"
          >
            <span>View Trainer Network</span>
            <ArrowRight size={13} />
          </button>
        </div>
      </div>

      {/* ── 10. Government Opportunity Network (ShikshaSetu USP) ── */}
      <div className="rounded-3xl border border-[#dfe7f0] bg-white p-6 sm:p-7 shadow-xs relative overflow-hidden anim-card-enter stagger-11">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-1.5 rounded-full bg-[#e8f5f3] px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-[#087f76] mb-2">
              <Compass size={12} className="text-[#087f76]" />
              ShikshaSetu Strategic USP
            </div>
            <h2 className="text-xl font-bold text-[#123057]">
              Government Opportunity Network
            </h2>
            <p className="mt-1 text-xs sm:text-[13px] text-slate-600 leading-relaxed">
              Connect verified government trainers and skilled officials with future capacity-building opportunities.
            </p>
          </div>

          <button
            onClick={() => onNavigate("Opportunity Network")}
            className="inline-flex shrink-0 items-center justify-center gap-1.5 whitespace-nowrap rounded-xl bg-[#ef7e37] px-4.5 py-2.5 text-[13px] font-bold text-white shadow-md hover:bg-[#d96a27] transition-all cursor-pointer btn-interactive self-start md:self-auto"
          >
            <span>Explore Opportunities</span>
            <ArrowRight size={14} />
          </button>
        </div>

        {/* 3 Metrics */}
        <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4 pt-5 border-t border-slate-100">
          <div className="rounded-2xl bg-[#f8fafc] p-4 border border-slate-100">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Verified Trainers
            </span>
            <div className="mt-1.5 text-2xl font-bold text-[#123057]">86</div>
            <div className="mt-0.5 text-xs text-slate-500">Verified and available for matching</div>
          </div>

          <div className="rounded-2xl bg-[#f8fafc] p-4 border border-slate-100">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Opportunity-Ready Profiles
            </span>
            <div className="mt-1.5 text-2xl font-bold text-[#087f76]">24</div>
            <div className="mt-0.5 text-xs text-slate-500">High-competency candidate pool</div>
          </div>

          <div className="rounded-2xl bg-[#f8fafc] p-4 border border-slate-100">
            <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              Potential Matches
            </span>
            <div className="mt-1.5 text-2xl font-bold text-[#ea580c]">91</div>
            <div className="mt-0.5 text-xs text-slate-500">Role & trainer alignment requests</div>
          </div>
        </div>
      </div>

      {/* ── 11 & 12. AI Insights & Attention Panel (Two-Column Layout) ── */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* 11. ShikshaSetu AI Insights */}
        <div className="rounded-3xl border border-[#dfe7f0] bg-white p-6 shadow-xs anim-card-enter stagger-12">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-[#e8f5f3] text-[#087f76]">
                <Sparkles size={16} />
              </div>
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Automated Intelligence
                </span>
                <h2 className="text-lg font-bold text-[#123057]">
                  ShikshaSetu AI Insights
                </h2>
              </div>
            </div>
          </div>

          <div className="space-y-2.5">
            {aiInsights.map((insight, idx) => (
              <div
                key={idx}
                className="flex items-start gap-3 rounded-2xl bg-[#f8fafc] p-3.5 border border-slate-100 hover:border-[#087f76]/25 transition-all"
              >
                <div className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-[#e8f5f3] text-[#087f76]">
                  <Sparkles size={11} />
                </div>
                <p className="text-xs text-slate-700 leading-relaxed font-medium">
                  {insight}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* 12. Requires Attention Panel */}
        <div className="rounded-3xl border border-[#dfe7f0] bg-white p-6 shadow-xs anim-card-enter stagger-13">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-amber-50 text-amber-600">
                <AlertTriangle size={16} />
              </div>
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                  Administrative Review
                </span>
                <h2 className="text-lg font-bold text-[#123057]">
                  Requires Attention
                </h2>
              </div>
            </div>
            <span className="rounded-full bg-rose-50 px-2.5 py-0.5 text-[11px] font-bold text-rose-700 border border-rose-200">
              4 Alerts
            </span>
          </div>

          <div className="space-y-2.5">
            {attentionItems.map((item, idx) => (
              <div
                key={idx}
                onClick={() => onNavigate(item.targetPage)}
                className="flex items-center justify-between gap-3 rounded-2xl bg-white p-3.5 border border-slate-200 hover:border-slate-300 hover:bg-slate-50 transition-all cursor-pointer group"
              >
                <div className="flex items-center gap-2.5 min-w-0">
                  <span className={`h-2.5 w-2.5 rounded-full shrink-0 ${item.color}`} />
                  <span className="text-xs font-semibold text-[#123057] truncate">
                    {item.text}
                  </span>
                </div>
                <span className="shrink-0 text-[11px] font-bold text-slate-400 group-hover:text-[#087f76] flex items-center gap-1 transition-colors">
                  {item.action} <ArrowRight size={11} />
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── National Framework Gateway (Official Integration Aesthetic) ── */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 rounded-2xl border border-slate-200/80 bg-white px-5 py-4 text-xs shadow-2xs anim-fade-up">
        <div className="flex items-start gap-3">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[#e8f5f3] text-[#087f76] font-bold text-[11px]">
            iGOT
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-[#123057] text-[13px]">
                iGOT Karmayogi National Competency Gateway
              </span>
              <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-bold text-emerald-800">
                Connected
              </span>
            </div>
            <p className="mt-0.5 text-xs text-slate-500">
              63 verified iGOT learning resources & 85 NSSTA modules active across departments.
            </p>
          </div>
        </div>

        <button
          onClick={() => onNavigate("Reports")}
          className="self-start sm:self-auto text-xs font-semibold text-[#087f76] hover:underline flex items-center gap-1 shrink-0 cursor-pointer"
        >
          <span>View Integration Audit</span>
          <ArrowRight size={12} />
        </button>
      </div>
    </div>
  );
}

export default AdminDashboard;
