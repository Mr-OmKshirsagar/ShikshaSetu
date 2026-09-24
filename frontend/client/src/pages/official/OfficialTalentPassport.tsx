import React, { useEffect, useState } from "react";
import {
  Shield,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Eye,
  Lock,
  Building,
  Briefcase,
  Compass,
  Award,
  Layers,
  CheckSquare,
  ArrowRight,
  Info,
  Calendar,
  MapPin,
  ExternalLink,
} from "lucide-react";
import {
  api,
  TalentProfile,
  UserOpportunity,
  OpportunityType,
  VisibilityLevel,
  MatchExplanation,
} from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { useTranslation } from "@/i18n";
import { toast } from "sonner";
import { AnimatedSection, ProgressBarFill, NumberReveal } from "@/components/motion/MotionUtils";

interface OfficialTalentPassportProps {
  onNavigate?: (page: string) => void;
}

const ALL_OPP_TYPES: { id: OpportunityType; label: string; desc: string }[] = [
  { id: "TRAINER", label: "Training Faculty", desc: "Conduct structured training modules & courses" },
  { id: "MENTOR", label: "Peer Mentoring", desc: "Guide junior officials in field & operational methods" },
  { id: "KNOWLEDGE_SHARING", label: "Knowledge Sharing", desc: "Share department case studies & best practices" },
  { id: "SUBJECT_MATTER_EXPERT", label: "Subject Matter Expert", desc: "SME panelist for curriculum & technical reviews" },
  { id: "CAPACITY_BUILDING", label: "Capacity Building", desc: "Institutional development programmes" },
  { id: "WORKSHOP", label: "Workshops & Seminars", desc: "Facilitate specialized hands-on workshops" },
  { id: "ADVISORY", label: "Advisory & Strategy", desc: "Methodology advice for government initiatives" },
];

export function OfficialTalentPassport({ onNavigate }: OfficialTalentPassportProps) {
  const { user } = useAuth();
  const { t } = useTranslation();

  const [profile, setProfile] = useState<TalentProfile | null>(null);
  const [opportunities, setOpportunities] = useState<UserOpportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [savingPrefs, setSavingPrefs] = useState(false);

  // Preference Form State
  const [optIn, setOptIn] = useState(false);
  const [visibility, setVisibility] = useState<VisibilityLevel>("PRIVATE");
  const [available, setAvailable] = useState(false);
  const [selectedTypes, setSelectedTypes] = useState<OpportunityType[]>([]);

  // Selected Explanation Modal
  const [activeExplanation, setActiveExplanation] = useState<{
    title: string;
    explanation: MatchExplanation;
  } | null>(null);

  const [loadingOpps, setLoadingOpps] = useState(true);

  const fetchProfileAndOpps = () => {
    // 1. Fetch Profile (renders hero, readiness, competencies, privacy settings)
    setLoading(true);
    api.talent.getProfile()
      .then((profData) => {
        setProfile(profData);
        if (profData.preferences) {
          setOptIn(profData.preferences.opt_in_enabled);
          setVisibility(profData.preferences.visibility_level || "PRIVATE");
          setAvailable(profData.preferences.available_for_opportunities);
          setSelectedTypes(profData.preferences.opportunity_types || []);
        }
      })
      .catch((err: any) => {
        toast.error(err.message || "Failed to load Talent Passport data");
      })
      .finally(() => {
        setLoading(false);
      });

    // 2. Fetch Opportunities independently without blocking the main passport UI
    setLoadingOpps(true);
    api.talent.getOpportunities()
      .then((oppsData) => {
        setOpportunities(oppsData.opportunities || []);
      })
      .catch(() => {
        setOpportunities([]);
      })
      .finally(() => {
        setLoadingOpps(false);
      });
  };

  useEffect(() => {
    fetchProfileAndOpps();
  }, []);

  const handleSavePreferences = async () => {
    try {
      setSavingPrefs(true);
      const updated = await api.talent.updatePreferences({
        opt_in_enabled: optIn,
        visibility_level: visibility,
        available_for_opportunities: available,
        opportunity_types: selectedTypes,
      });

      toast.success("Opportunity preferences and consent settings saved");
      setProfile((prev) => (prev ? { ...prev, preferences: updated } : null));

      // Refresh opportunities according to new consent
      const opps = await api.talent.getOpportunities();
      setOpportunities(opps.opportunities || []);
    } catch (err: any) {
      toast.error(err.message || "Failed to save preferences");
    } finally {
      setSavingPrefs(false);
    }
  };

  const toggleOppType = (typeId: OpportunityType) => {
    setSelectedTypes((prev) =>
      prev.includes(typeId) ? prev.filter((t) => t !== typeId) : [...prev, typeId]
    );
  };

  const readinessPct = Math.round((profile?.profile_readiness || 0) * 100);

  return (
    <div className="space-y-8 anim-page-enter">
      {/* ── Hero Banner (Stationary) ── */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#123057] via-[#1a3d6d] to-[#087f76] p-7 sm:p-8 text-white shadow-lg anim-fade-up">
        <div className="relative z-10 flex flex-col justify-between gap-6 md:flex-row md:items-center">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-[11px] font-bold uppercase tracking-wider backdrop-blur-md text-[#38d9c0]">
              <Shield size={12} className="text-[#38d9c0]" />
              Verified Government Talent Passport
            </div>
            <h1 className="mt-2.5 text-2xl font-extrabold tracking-tight sm:text-3xl leading-tight">
              {profile?.full_name || user?.full_name || "Government Official"}
            </h1>
            <div className="mt-1.5 flex flex-wrap items-center gap-3 text-xs text-slate-200">
              <span className="flex items-center gap-1.5">
                <Briefcase size={14} className="text-[#38d9c0]" />
                {profile?.designation || user?.designation || "Statistical Officer"}
              </span>
              <span>·</span>
              <span className="flex items-center gap-1.5">
                <Building size={14} className="text-[#38d9c0]" />
                {profile?.department || user?.department || "Ministry of Statistics & PI"}
              </span>
              <span>·</span>
              <span className="text-slate-300">ID: {profile?.employee_id || user?.employee_id || "GOV-OFFICIAL"}</span>
            </div>
          </div>

          {/* Profile Readiness Badge */}
          <div className="rounded-2xl border border-white/20 bg-white/10 p-4.5 backdrop-blur-md shrink-0 sm:w-64">
            <div className="flex items-center justify-between text-xs font-semibold text-slate-200">
              <span>Talent Profile Readiness</span>
              {loading && !profile ? (
                <span className="inline-block h-4 w-10 bg-white/20 rounded animate-pulse" />
              ) : (
                <span className="font-bold text-[#38d9c0] text-sm">
                  <NumberReveal value={readinessPct} suffix="%" />
                </span>
              )}
            </div>
            {loading && !profile ? (
              <div className="mt-2 h-2 w-full rounded-full bg-black/20 overflow-hidden">
                <div className="h-full w-2/3 rounded-full bg-white/30 animate-pulse" />
              </div>
            ) : (
              <ProgressBarFill
                percent={readinessPct}
                className="mt-2 h-2 w-full rounded-full bg-black/20 overflow-hidden"
                fillClassName="h-full rounded-full bg-gradient-to-r from-[#38d9c0] to-[#2dd4bf]"
                durationMs={800}
              />
            )}
            <div className="mt-2 flex items-center justify-between text-[11px] text-slate-300">
              {loading && !profile ? (
                <>
                  <span className="inline-block h-3 w-16 bg-white/20 rounded animate-pulse" />
                  <span className="inline-block h-3 w-16 bg-white/20 rounded animate-pulse" />
                </>
              ) : (
                <>
                  <span>
                    <NumberReveal value={profile?.verified_competencies?.length || 0} /> Competencies
                  </span>
                  <span>
                    <NumberReveal value={Math.round((profile?.average_confidence || 0) * 100)} suffix="%" /> Confidence
                  </span>
                </>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ── Privacy & Consent Configuration ── */}
      <AnimatedSection className="rounded-2xl border border-[#dfe7f0] bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-2 pb-5 border-b border-slate-100 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Shield className="text-[#087f76]" size={18} />
              <h2 className="text-base font-bold text-[#123057]">
                Opportunity Discovery & Consent Controls
              </h2>
            </div>
            <p className="mt-1 text-xs text-slate-500">
              ShikshaSetu respects your civil service privacy. You have full sovereign control over whether your verified profile is discoverable for government workforce opportunities.
            </p>
          </div>
          <button
            onClick={handleSavePreferences}
            disabled={savingPrefs}
            className="inline-flex items-center justify-center gap-1.5 rounded-xl bg-[#087f76] px-5 py-2.5 text-xs font-bold text-white shadow-sm hover:bg-[#06635c] transition-all disabled:opacity-50 shrink-0"
          >
            {savingPrefs ? "Saving..." : "Save Preferences"}
          </button>
        </div>

        <div className="mt-6 grid gap-6 md:grid-cols-3">
          {/* 1. Explicit Opt-In Toggle */}
          <div className="rounded-xl border border-slate-200 bg-[#f8fafc] p-4 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Opportunity Discovery
                </span>
                <span
                  className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-bold ${
                    optIn ? "bg-emerald-100 text-emerald-800" : "bg-slate-200 text-slate-700"
                  }`}
                >
                  {optIn ? "Opted In" : "Off (Default)"}
                </span>
              </div>
              <h3 className="mt-2 text-sm font-bold text-[#123057]">
                Consent to Opportunity Matching
              </h3>
              <p className="mt-1 text-xs text-slate-500 leading-relaxed">
                Allow authorized government departments to consider your verified competency profile for eligible workforce opportunities.
              </p>
            </div>
            <label className="mt-4 flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={optIn}
                onChange={(e) => setOptIn(e.target.checked)}
                className="h-4.5 w-4.5 rounded border-slate-300 text-[#087f76] focus:ring-[#087f76]"
              />
              <span className="text-xs font-semibold text-[#123057]">
                Enable opportunity discovery
              </span>
            </label>
          </div>

          {/* 2. Visibility Level */}
          <div className="rounded-xl border border-slate-200 bg-[#f8fafc] p-4 flex flex-col justify-between">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Department Visibility
              </span>
              <h3 className="mt-2 text-sm font-bold text-[#123057]">
                Scope of Discovery
              </h3>
              <p className="mt-1 text-xs text-slate-500 leading-relaxed">
                Specify which government administrative tiers can discover your verified credentials.
              </p>
            </div>
            <div className="mt-3 space-y-2">
              {[
                { id: "PRIVATE", label: "Private (Hidden from discovery)" },
                { id: "MY_DEPARTMENT", label: "My Department Only" },
                { id: "AUTHORIZED_DEPARTMENTS", label: "Authorized Government Departments" },
              ].map((vis) => (
                <label key={vis.id} className="flex items-center gap-2.5 text-xs text-slate-700 cursor-pointer">
                  <input
                    type="radio"
                    name="visibility"
                    value={vis.id}
                    checked={visibility === vis.id}
                    onChange={() => setVisibility(vis.id as VisibilityLevel)}
                    className="text-[#087f76] focus:ring-[#087f76]"
                  />
                  <span>{vis.label}</span>
                </label>
              ))}
            </div>
          </div>

          {/* 3. Availability Status */}
          <div className="rounded-xl border border-slate-200 bg-[#f8fafc] p-4 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Current Availability
                </span>
                <span
                  className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-bold ${
                    available ? "bg-teal-100 text-teal-800" : "bg-amber-100 text-amber-800"
                  }`}
                >
                  {available ? "Available" : "Not Available"}
                </span>
              </div>
              <h3 className="mt-2 text-sm font-bold text-[#123057]">
                Workforce Deployment Status
              </h3>
              <p className="mt-1 text-xs text-slate-500 leading-relaxed">
                Mark whether you are currently open to taking on approved government training, advisory, or SME roles.
              </p>
            </div>
            <label className="mt-4 flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={available}
                onChange={(e) => setAvailable(e.target.checked)}
                className="h-4.5 w-4.5 rounded border-slate-300 text-[#087f76] focus:ring-[#087f76]"
              />
              <span className="text-xs font-semibold text-[#123057]">
                Available for eligible opportunities
              </span>
            </label>
          </div>
        </div>

        {/* Opportunity Type Preferences */}
        <div className="mt-6 pt-5 border-t border-slate-100">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Preferred Government Opportunity Formats
          </h4>
          <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {ALL_OPP_TYPES.map((type) => {
              const isSelected = selectedTypes.includes(type.id);
              return (
                <div
                  key={type.id}
                  onClick={() => toggleOppType(type.id)}
                  className={`rounded-xl border p-3 cursor-pointer transition-all ${
                    isSelected
                      ? "border-[#087f76] bg-teal-50/50 shadow-xs"
                      : "border-slate-200 bg-white hover:border-slate-300"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-[#123057]">{type.label}</span>
                    <input
                      type="checkbox"
                      checked={isSelected}
                      readOnly
                      className="h-3.5 w-3.5 rounded text-[#087f76] focus:ring-[#087f76]"
                    />
                  </div>
                  <p className="mt-1 text-[11px] text-slate-500">{type.desc}</p>
                </div>
              );
            })}
          </div>
        </div>
      </AnimatedSection>

      {/* ── Matched Government Opportunities ── */}
      <AnimatedSection className="rounded-2xl border border-[#dfe7f0] bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-2">
              <Compass className="text-[#087f76]" size={18} />
              <h2 className="text-base font-bold text-[#123057]">
                Eligible Government Opportunities
              </h2>
            </div>
            <p className="mt-1 text-xs text-slate-500">
              Opportunities matched using deterministic, explainable rule-based capability evaluation. No hidden criteria or ungrounded AI predictions.
            </p>
          </div>
          <span className="rounded-full bg-teal-50 px-3 py-1 text-xs font-bold text-[#087f76]">
            <NumberReveal value={opportunities.length} /> Matched
          </span>
        </div>

        {loading && opportunities.length === 0 ? (
          <div className="mt-6 grid gap-4 lg:grid-cols-2">
            {[1, 2].map((i) => (
              <div
                key={i}
                className="rounded-2xl border border-slate-200 bg-[#f8fafc] p-5 space-y-3 animate-pulse"
              >
                <div className="flex items-center justify-between">
                  <div className="h-4 w-24 rounded bg-slate-200/80" />
                  <div className="h-4 w-16 rounded bg-slate-200/80" />
                </div>
                <div className="h-5 w-3/4 rounded bg-slate-200/80" />
                <div className="h-3 w-full rounded bg-slate-200/60" />
                <div className="h-3 w-1/2 rounded bg-slate-200/60" />
                <div className="pt-3 border-t border-slate-200 flex justify-between items-center">
                  <div className="h-3 w-32 rounded bg-slate-200/60" />
                  <div className="h-6 w-24 rounded-lg bg-slate-200/80" />
                </div>
              </div>
            ))}
          </div>
        ) : opportunities.length === 0 ? (
          <div className="mt-6 rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-8 text-center">
            <Info size={28} className="mx-auto text-slate-400" />
            <h3 className="mt-2 text-sm font-bold text-[#123057]">
              No active eligible opportunities found
            </h3>
            <p className="mt-1 text-xs text-slate-500 max-w-md mx-auto">
              {!optIn
                ? "You have currently opted out of opportunity discovery. Enable the discovery toggle above to find matched programs."
                : "Your verified competency profile does not currently match active opportunity minimum thresholds, or your department visibility filter is active."}
            </p>
          </div>
        ) : (
          <div className="mt-6 grid gap-4 lg:grid-cols-2">
            {opportunities.map((item) => {
              const opp = item.opportunity;
              const exp = item.match_explanation;
              const scorePct = Math.round((exp?.match_score || 0) * 100);

              return (
                <div
                  key={opp.id}
                  className="rounded-2xl border border-slate-200 bg-[#f8fafc] p-5 flex flex-col justify-between hover:border-[#087f76]/40 hover:shadow-md transition-all"
                >
                  <div>
                    <div className="flex items-center justify-between gap-2">
                      <span className="inline-flex items-center rounded-full bg-teal-100 px-2.5 py-0.5 text-[10px] font-bold text-[#087f76]">
                        {opp.opportunity_type.replace(/_/g, " ")}
                      </span>
                      {item.is_eligible && (
                        <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2 py-0.5 text-[11px] font-bold text-emerald-800">
                          <CheckCircle2 size={12} />
                          <NumberReveal value={scorePct} suffix="%" /> Match
                        </span>
                      )}
                    </div>

                    <h3 className="mt-2.5 text-base font-bold text-[#123057]">{opp.title}</h3>
                    <p className="mt-1 text-xs text-slate-600 line-clamp-2 leading-relaxed">
                      {opp.description}
                    </p>

                    <div className="mt-3 flex flex-wrap items-center gap-3 text-[11px] text-slate-500">
                      <span className="flex items-center gap-1">
                        <Building size={12} />
                        {opp.department_name}
                      </span>
                      {opp.location && (
                        <span className="flex items-center gap-1">
                          <MapPin size={12} />
                          {opp.location}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="mt-5 pt-4 border-t border-slate-200/80 flex items-center justify-between">
                    <span className="text-[11px] text-slate-500 font-medium">
                      <NumberReveal value={opp.required_competencies.length} /> Competencies Required
                    </span>
                    {exp && (
                      <button
                        onClick={() => setActiveExplanation({ title: opp.title, explanation: exp })}
                        className="inline-flex items-center gap-1 rounded-xl bg-white border border-slate-200 px-3 py-1.5 text-xs font-bold text-[#087f76] hover:bg-teal-50 transition-all shadow-2xs"
                      >
                        Why am I matched? <Info size={13} />
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </AnimatedSection>

      {/* ── Verified Competencies Grid ── */}
      <AnimatedSection className="rounded-2xl border border-[#dfe7f0] bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-2">
              <Award className="text-[#087f76]" size={18} />
              <h2 className="text-base font-bold text-[#123057]">
                Verified Competency Credentials
              </h2>
            </div>
            <p className="mt-1 text-xs text-slate-500">
              Only authentic, assessed civil service competencies verified via ShikshaSetu assessments and evidence ledgers are included in your Talent Passport.
            </p>
          </div>
          <button
            onClick={() => onNavigate?.("My Competencies")}
            className="text-xs font-bold text-[#087f76] hover:underline"
          >
            View Framework
          </button>
        </div>

        {loading && !profile ? (
          <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="rounded-xl border border-slate-200/80 bg-[#f8fafc] p-4 space-y-3 animate-pulse"
              >
                <div className="flex justify-between items-center">
                  <div className="h-3 w-20 rounded bg-slate-200/80" />
                  <div className="h-4 w-14 rounded-full bg-slate-200/80" />
                </div>
                <div className="h-4 w-36 rounded bg-slate-200/80" />
                <div className="flex justify-between items-baseline pt-2">
                  <div className="h-6 w-16 rounded bg-slate-200/80" />
                  <div className="h-3 w-20 rounded bg-slate-200/60" />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {profile?.verified_competencies?.map((comp) => {
              const confPct = Math.round(comp.confidence * 100);
              return (
                <div
                  key={comp.competency_id}
                  className="rounded-xl border border-slate-200/80 bg-[#f8fafc] p-4 hover:border-slate-300 transition-all"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-[#087f76]">
                      {comp.domain || "STATISTICAL"}
                    </span>
                    <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-bold text-emerald-700">
                      <CheckCircle2 size={11} />
                      Verified
                    </span>
                  </div>
                  <h3 className="mt-1 text-sm font-bold text-[#123057]">{comp.competency_name}</h3>
                  <div className="mt-3 flex items-baseline justify-between">
                    <span className="text-2xl font-bold text-[#123057]">
                      <NumberReveal value={comp.current_level} decimals={1} />{" "}
                      <span className="text-xs font-normal text-slate-400">/ 5.0</span>
                    </span>
                    <span className="text-xs text-slate-500">
                      <NumberReveal value={confPct} suffix="%" /> confidence
                    </span>
                  </div>
                  <ProgressBarFill
                    percent={(comp.current_level / 5.0) * 100}
                    className="mt-2 h-1.5 w-full rounded-full bg-slate-200 overflow-hidden"
                    fillClassName="h-full rounded-full bg-[#087f76]"
                    durationMs={800}
                  />
                  <div className="mt-2 text-[11px] text-slate-400">
                    <NumberReveal value={comp.evidence_count} /> evidence records on ledger
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </AnimatedSection>

      {/* ── Training & Knowledge Experience ── */}
      <AnimatedSection className="rounded-2xl border border-[#dfe7f0] bg-white p-6 shadow-sm">
        <div className="flex items-center gap-2 pb-4 border-b border-slate-100">
          <Layers className="text-[#087f76]" size={18} />
          <h2 className="text-base font-bold text-[#123057]">
            Professional Experience & Knowledge Ledger
          </h2>
        </div>
        <div className="mt-5 grid gap-4 sm:grid-cols-4">
          <div className="rounded-xl border border-slate-200 bg-[#f8fafc] p-4 text-center">
            <span className="text-xs font-bold text-slate-400 uppercase">Service Experience</span>
            <div className="mt-1 text-2xl font-extrabold text-[#123057]">
              {loading && !profile ? (
                <div className="h-7 w-16 mx-auto rounded bg-slate-200/80 animate-pulse mt-1" />
              ) : (
                <NumberReveal value={profile?.years_experience || 5} suffix=" Years" />
              )}
            </div>
            <span className="text-[11px] text-slate-500">Government service</span>
          </div>

          <div className="rounded-xl border border-slate-200 bg-[#f8fafc] p-4 text-center">
            <span className="text-xs font-bold text-slate-400 uppercase">Completed Learning</span>
            <div className="mt-1 text-2xl font-extrabold text-[#087f76]">
              {loading && !profile ? (
                <div className="h-7 w-12 mx-auto rounded bg-slate-200/80 animate-pulse mt-1" />
              ) : (
                <NumberReveal value={profile?.completed_learning_count || 0} />
              )}
            </div>
            <span className="text-[11px] text-slate-500">iGOT / NSSTA activities</span>
          </div>

          <div className="rounded-xl border border-slate-200 bg-[#f8fafc] p-4 text-center">
            <span className="text-xs font-bold text-slate-400 uppercase">Training Materials</span>
            <div className="mt-1 text-2xl font-extrabold text-[#123057]">
              {loading && !profile ? (
                <div className="h-7 w-12 mx-auto rounded bg-slate-200/80 animate-pulse mt-1" />
              ) : (
                <NumberReveal value={profile?.training_materials_count || 0} />
              )}
            </div>
            <span className="text-[11px] text-slate-500">Authored or reviewed</span>
          </div>

          <div className="rounded-xl border border-slate-200 bg-[#f8fafc] p-4 text-center">
            <span className="text-xs font-bold text-slate-400 uppercase">Learners Mentored</span>
            <div className="mt-1 text-2xl font-extrabold text-[#ef7e37]">
              {loading && !profile ? (
                <div className="h-7 w-12 mx-auto rounded bg-slate-200/80 animate-pulse mt-1" />
              ) : (
                <NumberReveal value={profile?.learners_trained_count || 0} />
              )}
            </div>
            <span className="text-[11px] text-slate-500">Through training quizzes</span>
          </div>
        </div>
      </AnimatedSection>

      {/* ── Explainability Drawer / Modal ── */}
      {activeExplanation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-xs anim-fade-in">
          <div className="w-full max-w-lg rounded-3xl bg-white p-6 shadow-2xl anim-scale-up">
            <div className="flex items-start justify-between pb-3 border-b border-slate-100">
              <div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-[#087f76]">
                  Match Explanation & Grounding
                </span>
                <h3 className="mt-1 text-lg font-bold text-[#123057]">
                  {activeExplanation.title}
                </h3>
              </div>
              <button
                onClick={() => setActiveExplanation(null)}
                className="rounded-full p-1 text-slate-400 hover:bg-slate-100"
              >
                ✕
              </button>
            </div>

            <div className="mt-4 space-y-4 max-h-[60vh] overflow-y-auto pr-1">
              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Eligibility Criteria Check
                </h4>
                <div className="mt-2 space-y-1.5">
                  {activeExplanation.explanation.eligibility_reasons.map((r, i) => (
                    <div key={i} className="flex items-start gap-2 text-xs text-slate-700">
                      <span className="text-emerald-600 font-bold shrink-0">✓</span>
                      <span>{r.replace(/^[✓\s]+/, "")}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Verified Capability Match
                </h4>
                <div className="mt-2 space-y-2">
                  {activeExplanation.explanation.matched_competencies.map((mc, idx) => (
                    <div
                      key={idx}
                      className="rounded-xl border border-slate-100 bg-[#f8fafc] p-2.5 flex items-center justify-between text-xs"
                    >
                      <span className="font-semibold text-[#123057]">{mc.competency_name}</span>
                      <span className="font-bold text-[#087f76]">
                        Level {mc.current_level.toFixed(1)} / Req: {mc.required_level.toFixed(1)}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Why you were matched
                </h4>
                <div className="mt-2 space-y-1.5">
                  {activeExplanation.explanation.match_reasons.map((mr, i) => (
                    <div key={i} className="flex items-start gap-2 text-xs text-slate-700">
                      <span className="text-[#087f76] font-bold shrink-0">•</span>
                      <span>{mr.replace(/^[✓\s]+/, "")}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setActiveExplanation(null)}
                className="rounded-xl bg-[#123057] px-4.5 py-2 text-xs font-bold text-white hover:bg-[#1a3d6d]"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default OfficialTalentPassport;
