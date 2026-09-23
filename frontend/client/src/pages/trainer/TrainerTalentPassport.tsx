import React, { useEffect, useState } from "react";
import {
  Award,
  BookOpen,
  Briefcase,
  Building,
  CheckCircle2,
  Compass,
  FileQuestion,
  Layers,
  PenTool,
  Shield,
  Sparkles,
  Users,
} from "lucide-react";
import {
  api,
  TalentProfile,
  VisibilityLevel,
  OpportunityType,
  UserOpportunity,
} from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";
import { AnimatedSection } from "@/components/motion/MotionUtils";

export function TrainerTalentPassport() {
  const { user } = useAuth();
  const [profile, setProfile] = useState<TalentProfile | null>(null);
  const [opportunities, setOpportunities] = useState<UserOpportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [savingPrefs, setSavingPrefs] = useState(false);

  // Preference Form State
  const [optIn, setOptIn] = useState(false);
  const [visibility, setVisibility] = useState<VisibilityLevel>("PRIVATE");
  const [available, setAvailable] = useState(false);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [profData, oppsData] = await Promise.all([
          api.talent.getProfile(),
          api.talent.getOpportunities().catch(() => ({ total: 0, opportunities: [] })),
        ]);
        setProfile(profData);
        setOpportunities(oppsData.opportunities || []);

        if (profData.preferences) {
          setOptIn(profData.preferences.opt_in_enabled);
          setVisibility(profData.preferences.visibility_level || "PRIVATE");
          setAvailable(profData.preferences.available_for_opportunities);
        }
      } catch (err: any) {
        toast.error("Failed to load Trainer Talent Passport");
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleSavePreferences = async () => {
    try {
      setSavingPrefs(true);
      const updated = await api.talent.updatePreferences({
        opt_in_enabled: optIn,
        visibility_level: visibility,
        available_for_opportunities: available,
        opportunity_types: ["TRAINER", "MENTOR", "SUBJECT_MATTER_EXPERT", "WORKSHOP"],
      });
      toast.success("Trainer opportunity visibility updated");
      setProfile((prev) => (prev ? { ...prev, preferences: updated } : null));
    } catch (err: any) {
      toast.error("Failed to save visibility settings");
    } finally {
      setSavingPrefs(false);
    }
  };

  if (loading && !profile) {
    return (
      <div className="space-y-6 animate-pulse p-6">
        <div className="h-44 rounded-3xl bg-slate-200/70" />
        <div className="grid gap-6 md:grid-cols-3">
          <div className="h-40 rounded-2xl bg-slate-200/50" />
          <div className="h-40 rounded-2xl bg-slate-200/50" />
          <div className="h-40 rounded-2xl bg-slate-200/50" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 anim-page-enter">
      {/* ── Trainer Hero Banner ── */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-[#c2510e] via-[#d96a27] to-[#123057] p-7 sm:p-8 text-white shadow-lg anim-fade-up">
        <div className="relative z-10 flex flex-col justify-between gap-6 md:flex-row md:items-center">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-[11px] font-bold uppercase tracking-wider backdrop-blur-md text-[#fed7aa]">
              <Sparkles size={12} className="text-[#fed7aa]" />
              Government Trainer Talent Passport
            </div>
            <h1 className="mt-2.5 text-2xl font-extrabold tracking-tight sm:text-3xl leading-tight">
              {profile?.full_name || user?.full_name || "Faculty Member"}
            </h1>
            <div className="mt-1.5 flex flex-wrap items-center gap-3 text-xs text-orange-100">
              <span className="flex items-center gap-1.5">
                <Briefcase size={14} className="text-[#fed7aa]" />
                {profile?.designation || "Lead Faculty · Statistical Sampling"}
              </span>
              <span>·</span>
              <span className="flex items-center gap-1.5">
                <Building size={14} className="text-[#fed7aa]" />
                {profile?.department || "National Statistical Systems Training Academy (NSSTA)"}
              </span>
            </div>
          </div>

          <div className="rounded-2xl border border-white/20 bg-white/10 p-4.5 backdrop-blur-md shrink-0 sm:w-64">
            <span className="text-xs font-semibold text-orange-100">Trainer Verification</span>
            <div className="mt-1 text-2xl font-black text-white">
              {profile?.trainer_experience ? "Certified Faculty" : "Associate Faculty"}
            </div>
            <p className="mt-1 text-[11px] text-orange-200">
              Verified through official authoring & assessment ledger
            </p>
          </div>
        </div>
      </div>

      {/* ── Verified Training Statistics ── */}
      <AnimatedSection className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-2xl border border-[#dfe7f0] bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase">
            <span>Training Materials</span>
            <BookOpen size={16} className="text-[#c2510e]" />
          </div>
          <div className="mt-3 text-3xl font-extrabold text-[#123057]">
            {profile?.training_materials_count || 0}
          </div>
          <span className="text-[11px] text-slate-500">Curricula & documents uploaded</span>
        </div>

        <div className="rounded-2xl border border-[#dfe7f0] bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase">
            <span>Quizzes Published</span>
            <PenTool size={16} className="text-[#c2510e]" />
          </div>
          <div className="mt-3 text-3xl font-extrabold text-[#123057]">
            {profile?.quizzes_authored_count || 0}
          </div>
          <span className="text-[11px] text-slate-500">Formal & practice assessments</span>
        </div>

        <div className="rounded-2xl border border-[#dfe7f0] bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase">
            <span>Learners Trained</span>
            <Users size={16} className="text-[#c2510e]" />
          </div>
          <div className="mt-3 text-3xl font-extrabold text-[#087f76]">
            {profile?.learners_trained_count || 0}
          </div>
          <span className="text-[11px] text-slate-500">Civil servants assessed</span>
        </div>

        <div className="rounded-2xl border border-[#dfe7f0] bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase">
            <span>Evidence Confidence</span>
            <Award size={16} className="text-[#c2510e]" />
          </div>
          <div className="mt-3 text-3xl font-extrabold text-[#123057]">
            {Math.round((profile?.average_confidence || 0.85) * 100)}%
          </div>
          <span className="text-[11px] text-slate-500">High authoritative reliability</span>
        </div>
      </AnimatedSection>

      {/* ── Trainer Availability & Opportunity Visibility ── */}
      <AnimatedSection className="rounded-2xl border border-[#dfe7f0] bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-2 pb-5 border-b border-slate-100 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-base font-bold text-[#123057]">
              Faculty Availability & Government Opportunity Visibility
            </h2>
            <p className="mt-1 text-xs text-slate-500">
              Govern your visibility for national training programmes, capacity-building workshops, and SME panels.
            </p>
          </div>
          <button
            onClick={handleSavePreferences}
            disabled={savingPrefs}
            className="inline-flex items-center justify-center rounded-xl bg-[#c2510e] px-5 py-2 text-xs font-bold text-white shadow-sm hover:bg-[#a64208] transition-all disabled:opacity-50"
          >
            {savingPrefs ? "Saving..." : "Save Settings"}
          </button>
        </div>

        <div className="mt-6 grid gap-6 md:grid-cols-3">
          <div className="rounded-xl border border-slate-200 bg-[#f8fafc] p-4">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Discovery Consent</span>
            <h3 className="mt-1.5 text-sm font-bold text-[#123057]">Faculty Talent Pool</h3>
            <p className="mt-1 text-xs text-slate-500 leading-relaxed">
              Opt into the authorized government trainer registry for cross-departmental deployment.
            </p>
            <label className="mt-4 flex items-center gap-2.5 cursor-pointer">
              <input
                type="checkbox"
                checked={optIn}
                onChange={(e) => setOptIn(e.target.checked)}
                className="h-4.5 w-4.5 rounded border-slate-300 text-[#c2510e] focus:ring-[#c2510e]"
              />
              <span className="text-xs font-semibold text-[#123057]">Opt in for training opportunities</span>
            </label>
          </div>

          <div className="rounded-xl border border-slate-200 bg-[#f8fafc] p-4">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Visibility Scope</span>
            <h3 className="mt-1.5 text-sm font-bold text-[#123057]">Deployment Reach</h3>
            <div className="mt-2.5 space-y-2">
              {[
                { id: "PRIVATE", label: "Private (Hidden)" },
                { id: "MY_DEPARTMENT", label: "My Academy / Department Only" },
                { id: "AUTHORIZED_DEPARTMENTS", label: "All Authorized Ministries" },
              ].map((vis) => (
                <label key={vis.id} className="flex items-center gap-2 text-xs text-slate-700 cursor-pointer">
                  <input
                    type="radio"
                    name="trainer_vis"
                    value={vis.id}
                    checked={visibility === vis.id}
                    onChange={() => setVisibility(vis.id as VisibilityLevel)}
                    className="text-[#c2510e] focus:ring-[#c2510e]"
                  />
                  <span>{vis.label}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-[#f8fafc] p-4">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Active Status</span>
            <h3 className="mt-1.5 text-sm font-bold text-[#123057]">Faculty Deployment</h3>
            <p className="mt-1 text-xs text-slate-500 leading-relaxed">
              Declare current availability to take on external training sessions.
            </p>
            <label className="mt-4 flex items-center gap-2.5 cursor-pointer">
              <input
                type="checkbox"
                checked={available}
                onChange={(e) => setAvailable(e.target.checked)}
                className="h-4.5 w-4.5 rounded border-slate-300 text-[#c2510e] focus:ring-[#c2510e]"
              />
              <span className="text-xs font-semibold text-[#123057]">Available for training roles</span>
            </label>
          </div>
        </div>
      </AnimatedSection>

      {/* ── Verified Competencies & Knowledge Domains ── */}
      <AnimatedSection className="rounded-2xl border border-[#dfe7f0] bg-white p-6 shadow-sm">
        <h2 className="text-base font-bold text-[#123057] pb-3 border-b border-slate-100">
          Faculty Competency Framework & Knowledge Domains
        </h2>
        <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {profile?.verified_competencies.map((c) => (
            <div key={c.competency_id} className="rounded-xl border border-slate-200 bg-[#f8fafc] p-4">
              <span className="text-[10px] font-bold uppercase text-[#c2510e]">{c.domain || "STATISTICAL"}</span>
              <h3 className="mt-1 text-sm font-bold text-[#123057]">{c.competency_name}</h3>
              <div className="mt-2 text-xl font-bold text-[#123057]">
                Level {c.current_level.toFixed(1)}{" "}
                <span className="text-xs font-normal text-slate-400">/ 5.0</span>
              </div>
              <span className="text-xs text-slate-500">{Math.round(c.confidence * 100)}% verified confidence</span>
            </div>
          ))}
        </div>
      </AnimatedSection>
    </div>
  );
}

export default TrainerTalentPassport;
