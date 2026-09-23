import React, { useEffect, useState } from "react";
import {
  Compass,
  Plus,
  Users,
  CheckCircle2,
  Building,
  Briefcase,
  Award,
  Shield,
  FileText,
  Search,
  ExternalLink,
  ChevronRight,
  Filter,
  Lock,
  Trash2,
  RefreshCw,
} from "lucide-react";
import {
  api,
  GovernmentOpportunity,
  OpportunityType,
  OpportunityStatus,
  TalentMatch,
  TalentAuditLog,
} from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";
import { AnimatedSection } from "@/components/motion/MotionUtils";

export function AdminTalentNetwork() {
  const { user } = useAuth();
  const [opportunities, setOpportunities] = useState<GovernmentOpportunity[]>([]);
  const [auditLogs, setAuditLogs] = useState<TalentAuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  // Active Matches Drawer State
  const [selectedOpportunity, setSelectedOpportunity] = useState<GovernmentOpportunity | null>(null);
  const [matches, setMatches] = useState<TalentMatch[]>([]);
  const [matchesLoading, setMatchesLoading] = useState(false);

  // Selected Candidate for Match Explanation Modal
  const [selectedMatch, setSelectedMatch] = useState<TalentMatch | null>(null);

  // Create Opportunity Modal State
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [newDept, setNewDept] = useState("Ministry of Statistics & Programme Implementation (MoSPI)");
  const [newType, setNewType] = useState<OpportunityType>("TRAINER");
  const [newRoles, setNewRoles] = useState("Statistical Officer, Senior Statistical Officer");
  const [newCompCode, setNewCompCode] = useState("STAT_SAMPLING");
  const [newMinLevel, setNewMinLevel] = useState("2.5");
  const [newMinExp, setNewMinExp] = useState("2");
  const [creating, setCreating] = useState(false);

  // Active View Tab: 'opportunities' | 'audit'
  const [activeTab, setActiveTab] = useState<"opportunities" | "audit">("opportunities");

  const loadOpportunities = async () => {
    try {
      setLoading(true);
      const res = await api.talent.getManagedOpportunities();
      setOpportunities(res.opportunities || []);

      if (user?.access_role === "ADMIN") {
        const auditRes = await api.talent.getAuditLogs().catch(() => ({ total: 0, logs: [] }));
        setAuditLogs(auditRes.logs || []);
      }
    } catch (err: any) {
      toast.error("Failed to load opportunities");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadOpportunities();
  }, []);

  const handleViewMatches = async (opp: GovernmentOpportunity) => {
    setSelectedOpportunity(opp);
    try {
      setMatchesLoading(true);
      const res = await api.talent.getOpportunityMatches(opp.id);
      setMatches(res.matches || []);
    } catch (err: any) {
      toast.error(err.message || "Failed to load eligible talent matches");
      setMatches([]);
    } finally {
      setMatchesLoading(false);
    }
  };

  const handleDeleteOpportunity = async (opp: GovernmentOpportunity, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm(`Are you sure you want to permanently delete "${opp.title}"?`)) {
      return;
    }
    try {
      await api.talent.deleteOpportunity(opp.id);
      toast.success("Opportunity deleted successfully");
      if (selectedOpportunity?.id === opp.id) {
        setSelectedOpportunity(null);
        setMatches([]);
      }
      loadOpportunities();
    } catch (err: any) {
      toast.error(err.message || "Failed to delete opportunity");
    }
  };

  const handleCreateOpportunity = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || !newDesc.trim()) {
      toast.error("Please fill in opportunity title and description");
      return;
    }

    try {
      setCreating(true);
      const rolesArray = newRoles
        .split(",")
        .map((r) => r.trim())
        .filter(Boolean);

      const created = await api.talent.createOpportunity({
        title: newTitle.trim(),
        description: newDesc.trim(),
        department_name: newDept.trim(),
        opportunity_type: newType,
        required_roles: rolesArray,
        required_designations: rolesArray,
        required_competencies: [
          {
            competency_code: newCompCode.trim().toUpperCase(),
            minimum_level: parseFloat(newMinLevel) || 2.0,
            importance: 1.0,
          },
        ],
        minimum_experience_years: parseInt(newMinExp) || 0,
      });

      // Automatically publish to network
      await api.talent.publishOpportunity(created.id);

      toast.success("Government opportunity created and published");
      setShowCreateModal(false);
      setNewTitle("");
      setNewDesc("");
      loadOpportunities();
    } catch (err: any) {
      toast.error(err.message || "Failed to create opportunity");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="space-y-8 anim-page-enter">
      {/* ── Header ── */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#123057] via-[#241a4a] to-[#4b36a8] p-7 sm:p-8 text-white shadow-lg anim-fade-up">
        <div className="relative z-10 flex flex-col justify-between gap-6 md:flex-row md:items-center">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-[11px] font-bold uppercase tracking-wider backdrop-blur-md text-[#c4b5fd]">
              <Compass size={12} className="text-[#c4b5fd]" />
              Government Talent & Opportunity Network
            </div>
            <h1 className="mt-2.5 text-2xl font-extrabold tracking-tight sm:text-3xl leading-tight">
              Talent Discovery & Workforce Deployment
            </h1>
            <p className="mt-1 text-xs text-purple-200">
              Discover verified civil servants and faculty for approved government training, advisory, and SME panels.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center gap-2 rounded-xl bg-[#087f76] px-4.5 py-2.5 text-xs font-bold text-white shadow-md hover:bg-[#06635c] transition-all btn-interactive"
            >
              <Plus size={16} />
              Create Opportunity
            </button>
          </div>
        </div>
      </div>

      {/* ── View Switcher & Statistics ── */}
      <div className="flex items-center justify-between gap-4 border-b border-slate-200 pb-3">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setActiveTab("opportunities")}
            className={`rounded-xl px-4 py-2 text-xs font-bold transition-all ${
              activeTab === "opportunities"
                ? "bg-[#123057] text-white shadow-xs"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            Active Opportunities ({opportunities.length})
          </button>
          {user?.access_role === "ADMIN" && (
            <button
              onClick={() => setActiveTab("audit")}
              className={`rounded-xl px-4 py-2 text-xs font-bold transition-all ${
                activeTab === "audit"
                  ? "bg-[#123057] text-white shadow-xs"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              Audit Trail ({auditLogs.length})
            </button>
          )}
        </div>
      </div>

      {/* ── Active Opportunities View ── */}
      {activeTab === "opportunities" && (
        <div className="grid gap-6 lg:grid-cols-3">
          {/* Opportunities Column (2 cols) */}
          <div className="lg:col-span-2 space-y-4">
            {opportunities.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-slate-200 bg-white p-8 text-center">
                <Compass size={32} className="mx-auto text-slate-300" />
                <h3 className="mt-2 text-sm font-bold text-[#123057]">No opportunities published</h3>
                <p className="mt-1 text-xs text-slate-500">
                  Create an opportunity to discover eligible civil servants with verified competencies.
                </p>
              </div>
            ) : (
              opportunities.map((opp) => {
                const isSelected = selectedOpportunity?.id === opp.id;
                return (
                  <div
                    key={opp.id}
                    className={`rounded-2xl border p-5 transition-all ${
                      isSelected
                        ? "border-[#087f76] bg-teal-50/20 shadow-md"
                        : "border-slate-200 bg-white hover:border-slate-300 shadow-xs"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="inline-flex items-center rounded-full bg-slate-100 px-2.5 py-0.5 text-[10px] font-bold text-slate-700">
                        {opp.opportunity_type.replace(/_/g, " ")}
                      </span>
                      <span className="inline-flex items-center rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-bold text-emerald-700">
                        {opp.status}
                      </span>
                    </div>

                    <h3 className="mt-2 text-base font-bold text-[#123057]">{opp.title}</h3>
                    <p className="mt-1 text-xs text-slate-600 line-clamp-2">{opp.description}</p>

                    <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-slate-500">
                      <span className="flex items-center gap-1">
                        <Building size={13} />
                        {opp.department_name}
                      </span>
                      <span>·</span>
                      <span>{opp.required_competencies.length} Competencies Required</span>
                    </div>

                    <div className="mt-4 pt-4 border-t border-slate-100 flex items-center justify-between">
                      <span className="text-[11px] text-slate-400">
                        Deadline: {opp.application_deadline ? new Date(opp.application_deadline).toLocaleDateString() : "Ongoing"}
                      </span>
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          onClick={(e) => handleDeleteOpportunity(opp, e)}
                          title="Delete opportunity"
                          className="inline-flex items-center justify-center rounded-xl border border-rose-200 bg-rose-50/70 p-2 text-rose-600 hover:bg-rose-100 hover:text-rose-700 transition-all shadow-2xs"
                        >
                          <Trash2 size={14} />
                        </button>
                        <button
                          onClick={() => handleViewMatches(opp)}
                          className="inline-flex items-center gap-1.5 rounded-xl bg-[#123057] px-4 py-2 text-xs font-bold text-white hover:bg-[#1a3d6d] transition-all shadow-xs"
                        >
                          <Users size={13} />
                          View Matches
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Matches Column (1 col) */}
          <div className="space-y-4">
            <div className="rounded-2xl border border-[#dfe7f0] bg-white p-5 shadow-sm sticky top-6">
              <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                <h3 className="text-sm font-bold text-[#123057]">
                  {selectedOpportunity ? "Eligible Talent Matches" : "Select Opportunity"}
                </h3>
                {selectedOpportunity && (
                  <span className="rounded-full bg-teal-100 px-2.5 py-0.5 text-[11px] font-bold text-[#087f76]">
                    {matches.length} Eligible
                  </span>
                )}
              </div>

              {!selectedOpportunity ? (
                <div className="py-12 text-center text-xs text-slate-400">
                  Select an opportunity on the left to discover eligible, opted-in officials.
                </div>
              ) : matchesLoading ? (
                <div className="py-12 text-center text-xs text-slate-400 animate-pulse">
                  Evaluating verified competency profiles from database...
                </div>
              ) : matches.length === 0 ? (
                <div className="py-12 text-center text-xs text-slate-400">
                  No opted-in officials currently meet all required competency thresholds for this opportunity.
                </div>
              ) : (
                <div className="mt-4 space-y-3 max-h-[70vh] overflow-y-auto pr-1">
                  {matches.map((m) => {
                    const initials = m.full_name
                      .split(" ")
                      .map((n) => n[0])
                      .slice(0, 2)
                      .join("")
                      .toUpperCase();
                    const readinessPct = Math.round((m.profile_readiness || 0) * 100);
                    return (
                      <div
                        key={m.user_id}
                        className="rounded-xl border border-slate-200 bg-[#f8fafc] p-3.5 hover:border-teal-300 hover:shadow-xs transition-all space-y-2.5"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex items-center gap-2.5">
                            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-[#123057] text-[11px] font-bold text-white shrink-0 shadow-2xs">
                              {initials}
                            </div>
                            <div>
                              <div className="text-xs font-bold text-[#123057]">{m.full_name}</div>
                              <div className="text-[11px] text-slate-500 font-medium">
                                {m.designation || "Civil Servant"}
                              </div>
                            </div>
                          </div>
                          <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-bold text-emerald-800 shrink-0">
                            {Math.round(m.match_score * 100)}% Match
                          </span>
                        </div>

                        <div className="text-[11px] text-slate-500 flex items-center gap-1.5">
                          <Building size={12} className="text-slate-400 shrink-0" />
                          <span className="truncate">{m.department}</span>
                        </div>

                        <div className="flex flex-wrap items-center gap-1.5 pt-2 border-t border-slate-200/60 text-[10px]">
                          <span className="rounded-md bg-teal-50 border border-teal-200/60 px-1.5 py-0.5 font-bold text-[#087f76]">
                            {m.competency_match_count} Verified Comp.
                          </span>
                          {readinessPct > 0 && (
                            <span className="rounded-md bg-indigo-50 border border-indigo-200/60 px-1.5 py-0.5 font-semibold text-indigo-700">
                              {readinessPct}% Readiness
                            </span>
                          )}
                          <span className="rounded-md bg-slate-100 border border-slate-200 px-1.5 py-0.5 text-slate-600">
                            {Math.round(m.evidence_confidence * 100)}% Conf.
                          </span>
                        </div>

                        <div className="pt-1 flex justify-end">
                          <button
                            onClick={() => setSelectedMatch(m)}
                            className="inline-flex items-center gap-1 rounded-lg bg-white border border-slate-200 px-2.5 py-1 text-[11px] font-bold text-[#087f76] hover:bg-teal-50 transition-all shadow-2xs"
                          >
                            Explain Match <ChevronRight size={12} />
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ── Audit Trail View ── */}
      {activeTab === "audit" && (
        <AnimatedSection className="rounded-2xl border border-[#dfe7f0] bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100">
            <div>
              <h2 className="text-base font-bold text-[#123057]">
                Government Talent Network Audit Trail
              </h2>
              <p className="mt-0.5 text-xs text-slate-500">
                Every talent profile discovery, visibility change, and opportunity match access is logged for statutory compliance.
              </p>
            </div>
            <Shield size={18} className="text-[#087f76]" />
          </div>

          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-200 text-slate-400 uppercase font-semibold">
                  <th className="pb-3">Timestamp</th>
                  <th className="pb-3">Action</th>
                  <th className="pb-3">Officer</th>
                  <th className="pb-3">Department</th>
                  <th className="pb-3">Context Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {auditLogs.map((log, idx) => (
                  <tr key={idx} className="hover:bg-slate-50">
                    <td className="py-3 text-slate-400">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="py-3 font-semibold text-[#123057]">{log.action}</td>
                    <td className="py-3">{log.performed_by_name}</td>
                    <td className="py-3">{log.performed_by_department}</td>
                    <td className="py-3 text-slate-500">
                      {JSON.stringify(log.details)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </AnimatedSection>
      )}

      {/* ── Match Explanation Modal for Authorized Department Personnel ── */}
      {selectedMatch && selectedOpportunity && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-xs anim-fade-in">
          <div className="w-full max-w-lg rounded-3xl bg-white p-6 shadow-2xl anim-scale-up">
            <div className="flex items-start justify-between pb-3 border-b border-slate-100">
              <div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-[#087f76]">
                  Candidate Match Explanation
                </span>
                <h3 className="mt-1 text-base font-bold text-[#123057]">
                  {selectedMatch.full_name} · {selectedMatch.designation}
                </h3>
              </div>
              <button
                onClick={() => setSelectedMatch(null)}
                className="rounded-full p-1 text-slate-400 hover:bg-slate-100"
              >
                ✕
              </button>
            </div>

            <div className="mt-4 space-y-4 max-h-[60vh] overflow-y-auto pr-1">
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Opportunity
                </h4>
                <p className="mt-1 text-xs font-semibold text-[#123057]">
                  {selectedOpportunity.title}
                </p>
              </div>

              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Eligibility Verification
                </h4>
                <div className="mt-2 space-y-1.5">
                  {selectedMatch.explanation.eligibility_reasons.map((r, i) => (
                    <div key={i} className="flex items-start gap-2 text-xs text-slate-700">
                      <span className="text-emerald-600 font-bold shrink-0">✓</span>
                      <span>{r.replace(/^[✓\s]+/, "")}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Capability Match Breakdown
                </h4>
                <div className="mt-2 space-y-2">
                  {selectedMatch.explanation.matched_competencies.map((mc, idx) => (
                    <div
                      key={idx}
                      className="rounded-xl border border-slate-100 bg-[#f8fafc] p-2.5 flex items-center justify-between text-xs"
                    >
                      <span className="font-semibold text-[#123057]">{mc.competency_name}</span>
                      <span className="font-bold text-[#087f76]">
                        {mc.current_level.toFixed(1)} / 5.0 (Req: {mc.required_level.toFixed(1)})
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-xl bg-teal-50/60 border border-teal-100 p-3">
                <span className="text-xs font-bold text-[#087f76]">Why matched</span>
                <p className="mt-1 text-xs text-slate-600 leading-relaxed">
                  "Official's verified competency profile aligns with the opportunity's required competency framework and department eligibility boundaries."
                </p>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setSelectedMatch(null)}
                className="rounded-xl bg-[#123057] px-4.5 py-2 text-xs font-bold text-white hover:bg-[#1a3d6d]"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Create Opportunity Modal ── */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-xs anim-fade-in">
          <form
            onSubmit={handleCreateOpportunity}
            className="w-full max-w-lg rounded-3xl bg-white p-6 shadow-2xl anim-scale-up space-y-4"
          >
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="text-base font-bold text-[#123057]">
                Create Government Workforce Opportunity
              </h3>
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                className="rounded-full p-1 text-slate-400 hover:bg-slate-100"
              >
                ✕
              </button>
            </div>

            <div>
              <label className="text-xs font-bold text-[#123057]">Title</label>
              <input
                type="text"
                required
                value={newTitle}
                onChange={(e) => setNewTitle(e.target.value)}
                placeholder="e.g. Senior Faculty — Statistical Sampling"
                className="mt-1 w-full rounded-xl border border-slate-200 px-3.5 py-2 text-xs text-[#123057] focus:ring-[#087f76]"
              />
            </div>

            <div>
              <label className="text-xs font-bold text-[#123057]">Description</label>
              <textarea
                required
                rows={3}
                value={newDesc}
                onChange={(e) => setNewDesc(e.target.value)}
                placeholder="Describe role responsibilities, training scope, or advisory expectations..."
                className="mt-1 w-full rounded-xl border border-slate-200 px-3.5 py-2 text-xs text-[#123057] focus:ring-[#087f76]"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-bold text-[#123057]">Opportunity Type</label>
                <select
                  value={newType}
                  onChange={(e) => setNewType(e.target.value as OpportunityType)}
                  className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-xs text-[#123057]"
                >
                  <option value="TRAINER">Trainer</option>
                  <option value="MENTOR">Mentor</option>
                  <option value="SUBJECT_MATTER_EXPERT">Subject Matter Expert</option>
                  <option value="WORKSHOP">Workshop</option>
                  <option value="ADVISORY">Advisory</option>
                  <option value="CAPACITY_BUILDING">Capacity Building</option>
                </select>
              </div>

              <div>
                <label className="text-xs font-bold text-[#123057]">Department / Ministry</label>
                <select
                  value={newDept}
                  onChange={(e) => setNewDept(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-xs text-[#123057]"
                >
                  <option value="Ministry of Statistics & Programme Implementation (MoSPI)">
                    Ministry of Statistics & Programme Implementation (MoSPI)
                  </option>
                  <option value="National Statistical Systems Training Academy (NSSTA)">
                    National Statistical Systems Training Academy (NSSTA)
                  </option>
                  <option value="Department of Revenue & Land Records">
                    Department of Revenue & Land Records
                  </option>
                  <option value="Ministry of Finance">
                    Ministry of Finance
                  </option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="text-xs font-bold text-[#123057]">Required Competency</label>
                <select
                  value={newCompCode}
                  onChange={(e) => setNewCompCode(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-xs text-[#123057]"
                >
                  <option value="STAT_SAMPLING">STAT_SAMPLING (Sampling)</option>
                  <option value="STAT_SURVEY_DESIGN">STAT_SURVEY_DESIGN (Survey Design)</option>
                  <option value="STAT_DATA_QUALITY_FRAMEWORKS">STAT_DATA_QUALITY_FRAMEWORKS</option>
                  <option value="TECH_PYTHON">TECH_PYTHON (Python)</option>
                  <option value="TECH_DATA_VISUALIZATION">TECH_DATA_VISUALIZATION</option>
                  <option value="BEH_ETHICS">BEH_ETHICS (Ethics)</option>
                  <option value="REV_LAND_RECORDS">REV_LAND_RECORDS (Land Records)</option>
                </select>
              </div>
              <div>
                <label className="text-xs font-bold text-[#123057]">Min Level (1-5)</label>
                <input
                  type="number"
                  step="0.1"
                  min="1"
                  max="5"
                  value={newMinLevel}
                  onChange={(e) => setNewMinLevel(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-xs text-[#123057]"
                />
              </div>
              <div>
                <label className="text-xs font-bold text-[#123057]">Min Experience (Yrs)</label>
                <input
                  type="number"
                  min="0"
                  value={newMinExp}
                  onChange={(e) => setNewMinExp(e.target.value)}
                  className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-xs text-[#123057]"
                />
              </div>
            </div>

            <div>
              <label className="text-xs font-bold text-[#123057]">Eligible Roles (Comma separated)</label>
              <input
                type="text"
                value={newRoles}
                onChange={(e) => setNewRoles(e.target.value)}
                placeholder="Statistical Officer, Senior Statistical Officer"
                className="mt-1 w-full rounded-xl border border-slate-200 px-3 py-2 text-xs text-[#123057]"
              />
            </div>

            <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-3">
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                className="rounded-xl px-4 py-2 text-xs font-bold text-slate-600 hover:bg-slate-100"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={creating}
                className="rounded-xl bg-[#087f76] px-5 py-2 text-xs font-bold text-white shadow-sm hover:bg-[#06635c] disabled:opacity-50"
              >
                {creating ? "Creating..." : "Create & Publish"}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

export default AdminTalentNetwork;
