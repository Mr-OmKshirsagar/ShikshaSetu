import React, { useEffect, useState } from "react";
import {
  Award,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  Play,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  Minus,
  XCircle,
  AlertCircle,
  BookOpen,
  Target,
  BarChart2,
  ClipboardCheck,
  HelpCircle,
  Sparkles,
  X,
} from "lucide-react";
import {
  api,
  clearApiCache,
  type AssignedQuiz,
  type RecommendedQuizItem,
  type QuizFeedMeta,
  type QuizDetail,
  type QuizAttemptResult,
} from "@/lib/api";
import { toast } from "sonner";
import { useTranslation } from "@/i18n";
import { NumberReveal } from "@/components/motion/MotionUtils";

interface OfficialQuizzesProps {
  initialCompetencyCode?: string;
  onNavigate: (page: string, context?: { competencyCode?: string }) => void;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function ScoreBadge({ pct }: { pct: number }) {
  const colour =
    pct >= 80
      ? "bg-emerald-100 text-emerald-800 border-emerald-200"
      : pct >= 60
      ? "bg-teal-100 text-teal-800 border-teal-200"
      : pct >= 40
      ? "bg-amber-100 text-amber-800 border-amber-200"
      : "bg-red-100 text-red-800 border-red-200";
  return (
    <span className={`inline-flex rounded-lg border px-2.5 py-0.5 text-xs font-bold ${colour}`}>
      {Math.round(pct)}%
    </span>
  );
}

function LevelBar({ before, after, max = 5 }: { before: number; after: number; max?: number }) {
  const pctBefore = Math.min(100, (before / max) * 100);
  const pctAfter = Math.min(100, (after / max) * 100);
  return (
    <div className="space-y-1">
      <div className="flex items-center gap-2 text-[11px] text-slate-500">
        <span className="w-10 text-right">Before</span>
        <div className="flex-1 h-2 rounded-full bg-slate-100 overflow-hidden">
          <div className="h-full rounded-full bg-slate-300 transition-all" style={{ width: `${pctBefore}%` }} />
        </div>
        <span className="w-8 font-mono font-bold text-slate-600">{before.toFixed(1)}</span>
      </div>
      <div className="flex items-center gap-2 text-[11px] text-slate-500">
        <span className="w-10 text-right">After</span>
        <div className="flex-1 h-2 rounded-full bg-slate-100 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${after > before ? "bg-emerald-500" : after < before ? "bg-red-400" : "bg-slate-400"}`}
            style={{ width: `${pctAfter}%` }}
          />
        </div>
        <span className="w-8 font-mono font-bold text-[#123057]">{after.toFixed(1)}</span>
      </div>
    </div>
  );
}

function RelevanceBadge({ reason, gapSize }: { reason?: string; gapSize?: number }) {
  if (!reason) return null;

  switch (reason) {
    case "CRITICAL_GAP":
      return (
        <span className="inline-flex items-center gap-1.5 rounded-full border border-rose-200 bg-rose-50 px-2.5 py-0.5 text-[10px] font-bold text-rose-700 shadow-xs">
          <span className="h-1.5 w-1.5 rounded-full bg-rose-500 animate-pulse" />
          Critical Gap {gapSize ? `(-${gapSize.toFixed(1)})` : ""}
        </span>
      );
    case "HIGH_GAP":
      return (
        <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-200 bg-amber-50 px-2.5 py-0.5 text-[10px] font-bold text-amber-800">
          <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
          High Gap {gapSize ? `(-${gapSize.toFixed(1)})` : ""}
        </span>
      );
    case "IDENTIFIED_GAP":
      return (
        <span className="inline-flex items-center gap-1.5 rounded-full border border-orange-200 bg-orange-50 px-2.5 py-0.5 text-[10px] font-bold text-orange-700">
          <span className="h-1.5 w-1.5 rounded-full bg-orange-500" />
          Competency Gap
        </span>
      );
    case "ASSIGNED_BY_TRAINER":
      return (
        <span className="inline-flex items-center gap-1 rounded-full border border-purple-200 bg-purple-50 px-2.5 py-0.5 text-[10px] font-bold text-purple-700">
          <Award size={10} className="text-purple-600" />
          Trainer Assigned
        </span>
      );
    case "REQUIRED_COMPETENCY":
      return (
        <span className="inline-flex items-center gap-1 rounded-full border border-teal-200 bg-teal-50 px-2.5 py-0.5 text-[10px] font-bold text-teal-800">
          <Target size={10} className="text-teal-600" />
          Required Competency
        </span>
      );
    case "ROLE_TARGETED":
      return (
        <span className="inline-flex items-center gap-1 rounded-full border border-sky-200 bg-sky-50 px-2.5 py-0.5 text-[10px] font-bold text-sky-800">
          <BookOpen size={10} className="text-sky-600" />
          Role Targeted
        </span>
      );
    default:
      return null;
  }
}

// ─── Main Component ───────────────────────────────────────────────────────────

export function OfficialQuizzes({ initialCompetencyCode, onNavigate }: OfficialQuizzesProps) {
  const { t } = useTranslation();
  // List phase
  const [assignedQuizzes, setAssignedQuizzes] = useState<AssignedQuiz[]>([]);
  const [recommendedQuizzes, setRecommendedQuizzes] = useState<RecommendedQuizItem[]>([]);
  const [feedMeta, setFeedMeta] = useState<QuizFeedMeta | null>(null);
  const [listLoading, setListLoading] = useState(true);
  const [selectedWhyQuiz, setSelectedWhyQuiz] = useState<RecommendedQuizItem | null>(null);

  // Attempt phase
  const [activeQuiz, setActiveQuiz] = useState<QuizDetail | null>(null);
  const [quizLoading, setQuizLoading] = useState(false);
  const [currentQIdx, setCurrentQIdx] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});

  // Submit phase
  const [submitting, setSubmitting] = useState(false);

  // Result phase
  const [quizResult, setQuizResult] = useState<QuizAttemptResult | null>(null);

  // ── Data fetching ─────────────────────────────────────────────────────────

  const fetchQuizzes = async () => {
    clearApiCache();
    try {
      setListLoading(true);
      const feed = await api.quizzes.feed();
      setAssignedQuizzes(feed.assigned || []);
      setRecommendedQuizzes(feed.recommended || []);
      setFeedMeta(feed.meta || null);

      // Auto-start if navigated with a competency code
      if (initialCompetencyCode) {
        const matchAssigned = (feed.assigned || []).find(
          (q) => q.competency_code === initialCompetencyCode
        );
        if (matchAssigned) {
          const qid = matchAssigned._id || matchAssigned.quiz_id;
          if (qid) {
            startQuizSession(qid);
            return;
          }
        }
        const matchRec = (feed.recommended || []).find(
          (q) => q.competency_code === initialCompetencyCode
        );
        if (matchRec && matchRec._id) {
          startQuizSession(matchRec._id);
        }
      }
    } catch (err: any) {
      toast.error(err.message || "Failed to load quizzes");
    } finally {
      setListLoading(false);
    }
  };

  useEffect(() => {
    fetchQuizzes();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialCompetencyCode]);

  // ── Start quiz ────────────────────────────────────────────────────────────

  const startQuizSession = async (quizId: string) => {
    try {
      setQuizLoading(true);
      setQuizResult(null);
      const full = await api.quizzes.get(quizId);
      setActiveQuiz(full);
      setAnswers({});
      setCurrentQIdx(0);
    } catch (err: any) {
      toast.error(err.message || "Failed to load quiz questions");
    } finally {
      setQuizLoading(false);
    }
  };

  // ── Submit ────────────────────────────────────────────────────────────────

  const handleSubmit = async () => {
    if (!activeQuiz) return;
    const qid = activeQuiz._id;

    const payload = activeQuiz.questions.map((q) => ({
      question_id: q.question_id,
      selected_answer: answers[q.question_id] || "A",
    }));

    try {
      setSubmitting(true);
      const result = await api.quizzes.submit(qid, payload);
      setQuizResult(result);
      setActiveQuiz(null);
      toast.success("Quiz submitted! Results and competency update ready.");
      // Refresh the quiz list (status may have changed on the backend)
      fetchQuizzes();
    } catch (err: any) {
      if ((err as any).status === 409) {
        toast.error("This quiz has already been submitted.");
      } else {
        toast.error(err.message || "Failed to submit quiz");
      }
    } finally {
      setSubmitting(false);
    }
  };

  // ── Derived state ─────────────────────────────────────────────────────────

  const questions = activeQuiz?.questions ?? [];
  const totalQ = questions.length;
  const answeredCount = Object.keys(answers).length;
  const currentQ = questions[currentQIdx];
  const allAnswered = answeredCount === totalQ;
  const isLastQ = currentQIdx === totalQ - 1;
  const isFirstQ = currentQIdx === 0;

  // ── Phase: loading overlay ────────────────────────────────────────────────
  if (quizLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <RefreshCw size={28} className="animate-spin text-[#087f76]" />
        <p className="text-sm font-semibold text-slate-500">Loading quiz questions…</p>
      </div>
    );
  }

  // ── Phase: RESULT ─────────────────────────────────────────────────────────
  if (quizResult) {
    const { score, total_questions, percentage, competency, skill_gap, explanations } = quizResult;
    const improvement = competency?.improvement ?? 0;
    const ImpIcon = improvement > 0 ? TrendingUp : improvement < 0 ? TrendingDown : Minus;
    const impColour = improvement > 0 ? "text-emerald-600" : improvement < 0 ? "text-red-500" : "text-slate-500";

    return (
      <div className="space-y-6 anim-page-enter max-w-3xl mx-auto">
        {/* Result header */}
        <div className="rounded-3xl border border-teal-200 bg-white p-6 sm:p-8 shadow-sm space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 pb-5 border-b border-slate-100">
            <div>
              <div className="inline-flex items-center gap-1.5 rounded-full bg-emerald-100 px-3 py-1 text-xs font-bold text-emerald-900">
                <CheckCircle2 size={13} /> Quiz Completed
              </div>
              <h2 className="text-2xl font-bold tracking-tight text-[#123057] mt-2">Quiz Results</h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Supporting evidence recorded in your competency ledger.
              </p>
            </div>
            {/* Score pill */}
            <div className="rounded-2xl border border-teal-200 bg-teal-50/60 px-6 py-4 text-center shrink-0">
              <div className="text-[10px] font-bold text-teal-800 uppercase tracking-wider">Score</div>
              <div className="text-3xl font-extrabold tracking-tight text-[#123057] mt-1 font-mono">
                {score}
                <span className="text-lg text-slate-400 font-normal">/{total_questions}</span>
              </div>
              <ScoreBadge pct={percentage} />
            </div>
          </div>

          {/* Score summary row */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="rounded-xl bg-slate-50 border border-slate-100 p-3 text-center">
              <div className="text-xl font-bold font-mono text-emerald-600">{score}</div>
              <div className="text-[10px] font-bold text-slate-400 uppercase mt-0.5">Correct</div>
            </div>
            <div className="rounded-xl bg-slate-50 border border-slate-100 p-3 text-center">
              <div className="text-xl font-bold font-mono text-red-500">{total_questions - score}</div>
              <div className="text-[10px] font-bold text-slate-400 uppercase mt-0.5">Incorrect</div>
            </div>
            <div className="rounded-xl bg-slate-50 border border-slate-100 p-3 text-center">
              <div className="text-xl font-bold font-mono text-[#123057]">{Math.round(percentage)}%</div>
              <div className="text-[10px] font-bold text-slate-400 uppercase mt-0.5">Accuracy</div>
            </div>
            <div className="rounded-xl bg-slate-50 border border-slate-100 p-3 text-center">
              <div className={`text-xl font-bold font-mono ${impColour} flex items-center justify-center gap-1`}>
                <ImpIcon size={16} />
                {improvement > 0 ? "+" : ""}{improvement.toFixed(2)}
              </div>
              <div className="text-[10px] font-bold text-slate-400 uppercase mt-0.5">Level Change</div>
            </div>
          </div>
        </div>

        {/* Competency impact */}
        {competency && (
          <div className="rounded-2xl border border-[#dfe7f0] bg-white p-6 shadow-sm space-y-4">
            <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#e8f5f3]">
                <BarChart2 size={16} className="text-[#087f76]" />
              </div>
              <h3 className="text-sm font-bold text-[#123057]">Competency Impact</h3>
              <span className="rounded-md bg-teal-50 border border-teal-200 px-2 py-0.5 text-[10px] font-mono font-bold text-teal-800">
                {competency.competency_code}
              </span>
            </div>

            <LevelBar before={competency.competency_level_before} after={competency.competency_level_after} />

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-1">
              <div className="rounded-xl bg-slate-50 border border-slate-100 p-3">
                <div className="text-[10px] font-bold text-slate-400 uppercase">Before</div>
                <div className="text-lg font-bold font-mono text-slate-600 mt-0.5">
                  {competency.competency_level_before.toFixed(1)}<span className="text-xs text-slate-400 font-normal">/5</span>
                </div>
              </div>
              <div className="rounded-xl bg-[#e8f5f3] border border-teal-100 p-3">
                <div className="text-[10px] font-bold text-teal-700 uppercase">After</div>
                <div className="text-lg font-bold font-mono text-[#087f76] mt-0.5">
                  {competency.competency_level_after.toFixed(1)}<span className="text-xs text-teal-400 font-normal">/5</span>
                </div>
              </div>
              <div className="rounded-xl bg-slate-50 border border-slate-100 p-3">
                <div className="text-[10px] font-bold text-slate-400 uppercase">Confidence</div>
                <div className="text-lg font-bold font-mono text-[#123057] mt-0.5">
                  {Math.round(competency.confidence_after * 100)}%
                </div>
              </div>
              <div className="rounded-xl bg-slate-50 border border-slate-100 p-3">
                <div className="text-[10px] font-bold text-slate-400 uppercase">Evidence</div>
                <div className="text-sm font-bold text-slate-600 mt-0.5">AI Quiz (0.30)</div>
              </div>
            </div>

            <div className="rounded-xl bg-teal-50/60 border border-teal-100 p-3 text-xs text-teal-900">
              <strong>Governance notice:</strong> Quiz completion records <strong>Supporting Evidence (confidence 0.30)</strong> in your
              competency ledger. To formally update your competency rating, complete a{" "}
              <button
                onClick={() => onNavigate("Assessments", { competencyCode: competency.competency_code })}
                className="underline font-bold hover:text-teal-700"
              >
                Capability Assessment
              </button>.
            </div>
          </div>
        )}

        {/* Skill gap impact */}
        {skill_gap && (
          <div className="rounded-2xl border border-[#dfe7f0] bg-white p-6 shadow-sm space-y-3">
            <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#e8f5f3]">
                <Target size={16} className="text-[#087f76]" />
              </div>
              <h3 className="text-sm font-bold text-[#123057]">Skill Gap Status</h3>
            </div>
            <p className="text-xs text-slate-600">
              Your assessed level in{" "}
              <span className="font-mono font-bold text-[#123057]">{competency?.competency_code || "this competency"}</span> is now{" "}
              <span className="font-mono font-bold text-[#087f76]">{competency?.competency_level_after.toFixed(1)}</span>.
            </p>
          </div>
        )}

        {/* Question-by-question explanations */}
        {explanations && explanations.length > 0 && (
          <div className="rounded-2xl border border-[#dfe7f0] bg-white p-6 shadow-sm space-y-4">
            <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#e8f5f3]">
                <ClipboardCheck size={16} className="text-[#087f76]" />
              </div>
              <h3 className="text-sm font-bold text-[#123057]">Question Analysis</h3>
            </div>
            {explanations.map((qf, idx) => (
              <div
                key={qf.question_id}
                className={`rounded-xl border p-4 text-xs space-y-2 ${
                  qf.is_correct ? "border-emerald-200 bg-emerald-50/30" : "border-rose-200 bg-rose-50/30"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-slate-500">Question #{idx + 1}</span>
                  {qf.is_correct ? (
                    <span className="inline-flex items-center gap-1 font-bold text-emerald-700">
                      <CheckCircle2 size={13} /> Correct
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 font-bold text-rose-700">
                      <XCircle size={13} /> Incorrect — Correct: Option {qf.correct_answer}
                    </span>
                  )}
                </div>
                <p className="font-bold text-[#123057]">{qf.question}</p>

                {/* Show options with correct/wrong highlights */}
                <div className="space-y-1 pt-1">
                  {qf.options.map((opt, oi) => {
                    const letter = String.fromCharCode(65 + oi);
                    const isYours = qf.your_answer === letter;
                    const isCorrect = qf.correct_answer === letter;
                    const cls = isCorrect
                      ? "border-emerald-400 bg-emerald-50 font-bold text-emerald-900"
                      : isYours && !isCorrect
                      ? "border-rose-300 bg-rose-50 font-bold text-rose-800 line-through opacity-80"
                      : "border-slate-200 bg-white text-slate-600";
                    return (
                      <div key={oi} className={`flex items-center gap-2 rounded-lg border px-3 py-2 ${cls}`}>
                        <span className="h-5 w-5 shrink-0 flex items-center justify-center rounded bg-white/60 text-[10px] font-bold">
                          {letter}
                        </span>
                        <span>{opt}</span>
                      </div>
                    );
                  })}
                </div>

                <div className="rounded-lg bg-white/70 border border-slate-200/50 p-2.5">
                  <strong className="text-slate-600">Explanation:</strong> {qf.explanation}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Action buttons */}
        <div className="flex flex-wrap items-center gap-3 pb-8">
          <button
            onClick={() => onNavigate("Assessments", { competencyCode: competency?.competency_code })}
            className="inline-flex items-center gap-2 rounded-xl bg-[#087f76] px-5 py-2.5 text-xs font-bold text-white shadow hover:bg-[#06655e] transition-all"
          >
            <ClipboardCheck size={13} /> Take Capability Assessment
          </button>
          <button
            onClick={() => onNavigate("Skill Gaps")}
            className="inline-flex items-center gap-2 rounded-xl border border-[#dfe7f0] bg-white px-4 py-2.5 text-xs font-bold text-[#123057] hover:bg-slate-50 transition-all"
          >
            <Target size={13} /> View Skill Gaps
          </button>
          <button
            onClick={() => setQuizResult(null)}
            className="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-4 py-2.5 text-xs font-bold text-slate-600 hover:bg-slate-50 transition-all"
          >
            ← Back to Quizzes
          </button>
        </div>
      </div>
    );
  }

  // ── Phase: ACTIVE QUIZ (question-by-question) ─────────────────────────────
  if (activeQuiz && currentQ) {
    const progress = Math.round((answeredCount / totalQ) * 100);

    return (
      <div className="space-y-5 anim-page-enter max-w-3xl mx-auto">
        {/* Quiz header */}
        <div className="rounded-2xl border border-teal-200 bg-white p-5 shadow-sm">
          <div className="flex items-start justify-between gap-3 flex-wrap">
            <div className="min-w-0">
              <span className="inline-block rounded-md bg-teal-50 border border-teal-200 px-2.5 py-0.5 text-[10px] font-mono font-bold uppercase text-teal-800 mb-1.5">
                {activeQuiz.competency_code}
              </span>
              <h2 className="text-lg font-bold text-[#123057] leading-tight truncate max-w-md">
                {activeQuiz.title}
              </h2>
            </div>
            <div className="text-xs font-bold text-slate-400 shrink-0">
              {answeredCount}/{totalQ} answered
            </div>
          </div>

          {/* Progress bar */}
          <div className="mt-4">
            <div className="flex items-center justify-between text-[10px] font-bold text-slate-400 mb-1.5">
              <span>Progress</span>
              <span className="font-mono">{progress}%</span>
            </div>
            <div className="h-2 rounded-full bg-slate-100 overflow-hidden">
              <div
                className="h-full rounded-full bg-[#087f76] transition-all duration-300"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>

          {/* Question step pills */}
          <div className="flex flex-wrap gap-1.5 mt-4">
            {questions.map((q, i) => {
              const answered = !!answers[q.question_id];
              const isCurrent = i === currentQIdx;
              return (
                <button
                  key={q.question_id}
                  onClick={() => setCurrentQIdx(i)}
                  className={`h-7 w-7 rounded-lg text-[11px] font-bold font-mono transition-all ${
                    isCurrent
                      ? "bg-[#123057] text-white shadow"
                      : answered
                      ? "bg-teal-500 text-white"
                      : "bg-slate-100 text-slate-500 hover:bg-slate-200"
                  }`}
                  title={`Question ${i + 1}${answered ? " (answered)" : ""}`}
                >
                  {i + 1}
                </button>
              );
            })}
          </div>
        </div>

        {/* Current question */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm space-y-5">
          <div className="flex items-center justify-between text-xs text-slate-400 font-bold">
            <span>
              Question {currentQIdx + 1} of {totalQ}
            </span>
            <span className="rounded-md bg-slate-100 px-2 py-0.5 capitalize">
              {currentQ.difficulty?.toLowerCase()}
            </span>
          </div>

          <h3 className="text-base font-bold text-[#123057] leading-snug">{currentQ.question}</h3>

          {/* Answer options */}
          <div className="space-y-2.5">
            {currentQ.options.map((opt, oi) => {
              const letter = String.fromCharCode(65 + oi);
              const isSelected = answers[currentQ.question_id] === letter;
              return (
                <button
                  key={oi}
                  type="button"
                  onClick={() =>
                    setAnswers((prev) => ({ ...prev, [currentQ.question_id]: letter }))
                  }
                  className={`w-full flex items-center gap-3 rounded-xl border p-3.5 text-left text-sm transition-all ${
                    isSelected
                      ? "border-teal-400 bg-teal-50/70 font-bold text-[#123057] shadow-sm"
                      : "border-slate-200 bg-slate-50/50 text-slate-700 hover:border-teal-300 hover:bg-teal-50/30"
                  }`}
                >
                  <span
                    className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-lg text-[11px] font-bold transition-colors ${
                      isSelected ? "bg-teal-500 text-white" : "bg-slate-200 text-slate-700"
                    }`}
                  >
                    {letter}
                  </span>
                  <span>{opt}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between gap-3 pb-4">
          {/* Prev */}
          <button
            type="button"
            disabled={isFirstQ}
            onClick={() => setCurrentQIdx((i) => i - 1)}
            className="inline-flex items-center gap-1.5 rounded-xl border border-slate-200 px-4 py-2.5 text-xs font-bold text-slate-600 disabled:opacity-30 hover:bg-slate-50 transition-all"
          >
            <ArrowLeft size={13} /> Previous
          </button>

          <button
            type="button"
            onClick={() => { setActiveQuiz(null); setAnswers({}); setCurrentQIdx(0); }}
            className="text-xs font-bold text-slate-400 hover:text-slate-600 transition-colors"
          >
            Exit Quiz
          </button>

          {isLastQ ? (
            /* Submit button — only on last question */
            <button
              type="button"
              disabled={submitting || !allAnswered}
              onClick={handleSubmit}
              className="inline-flex items-center gap-2 rounded-xl bg-[#ef7e37] px-6 py-2.5 text-xs font-bold text-white shadow hover:bg-[#d96a27] disabled:opacity-40 transition-all active:scale-95"
              title={!allAnswered ? "Answer all questions before submitting" : ""}
            >
              {submitting ? (
                <>
                  <RefreshCw size={13} className="animate-spin" /> Submitting…
                </>
              ) : (
                <>
                  Submit Quiz <CheckCircle2 size={13} />
                </>
              )}
            </button>
          ) : (
            /* Next */
            <button
              type="button"
              onClick={() => setCurrentQIdx((i) => i + 1)}
              className="inline-flex items-center gap-2 rounded-xl bg-[#123057] px-5 py-2.5 text-xs font-bold text-white shadow hover:bg-[#0f2649] transition-all"
            >
              Next <ArrowRight size={13} />
            </button>
          )}
        </div>

        {/* Unanswered warning on last question */}
        {isLastQ && !allAnswered && (
          <div className="flex items-center gap-2 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-xs text-amber-800">
            <AlertCircle size={14} className="shrink-0" />
            <span>
              You have {totalQ - answeredCount} unanswered question{totalQ - answeredCount !== 1 ? "s" : ""}.
              Go back and answer all questions before submitting.
            </span>
          </div>
        )}
      </div>
    );
  }

  // ── Phase: QUIZ LIST ──────────────────────────────────────────────────────
  return (
    <div className="space-y-8 anim-page-enter max-w-4xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between border-b border-slate-200/80 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-[#123057]">{t("quizzes.assigned")}</h1>
          <p className="text-sm text-slate-500 mt-1">
            Assessments assigned by your trainers and AI-recommended quizzes tailored to your role and competency gaps.
          </p>
        </div>
        <button
          onClick={fetchQuizzes}
          disabled={listLoading}
          className="flex items-center gap-1.5 rounded-xl border border-[#dfe7f0] bg-white px-3.5 py-2 text-xs font-bold text-slate-600 hover:bg-slate-50 disabled:opacity-50 transition-colors shadow-xs"
        >
          <RefreshCw size={14} className={listLoading ? "animate-spin" : ""} />
          Refresh Quizzes
        </button>
      </div>

      {listLoading ? (
        <div className="space-y-4">
          <div className="h-40 rounded-2xl bg-white animate-pulse border border-slate-200" />
          <div className="h-40 rounded-2xl bg-white animate-pulse border border-slate-200" />
        </div>
      ) : (
        <div className="space-y-8">
          {/* ── Section 1: Assigned by Trainer ── */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-lg font-bold text-[#123057] flex items-center gap-2">
                    <Award size={18} className="text-purple-600" />
                    Assigned by Trainer
                  </h2>
                  <span className="rounded-full bg-purple-100 px-2.5 py-0.5 text-xs font-bold text-purple-800">
                    {assignedQuizzes.length}
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-0.5">
                  Mandatory and formal assessments assigned directly to you by department trainers.
                </p>
              </div>
            </div>

            {assignedQuizzes.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-slate-200 bg-white/70 p-8 text-center">
                <div className="mx-auto flex h-11 w-11 items-center justify-center rounded-xl bg-purple-50 text-purple-600">
                  <Award size={20} />
                </div>
                <h3 className="mt-3 text-sm font-bold text-slate-700">No trainer-assigned quizzes</h3>
                <p className="mt-1 text-xs text-slate-500 max-w-sm mx-auto">
                  When a trainer or administrator assigns formal evaluations to your profile, they will appear here.
                </p>
              </div>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2">
                {assignedQuizzes.map((q, idx) => {
                  const quizId = q._id || q.quiz_id || "";
                  const isSubmitted = q.status === "SUBMITTED" || q.status === "COMPLETED";

                  return (
                    <div
                      key={quizId || idx}
                      className="flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-5 shadow-xs hover:border-purple-300 hover:shadow-sm transition-all group"
                    >
                      <div>
                        <div className="flex items-center justify-between gap-2 flex-wrap">
                          <div className="flex items-center gap-1.5 flex-wrap">
                            <span className="rounded-full bg-purple-50 border border-purple-100 px-2.5 py-0.5 text-[10px] font-bold text-purple-700">
                              Trainer Assigned
                            </span>
                            <span className="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-bold text-slate-600 font-mono">
                              {q.question_count} Qs
                            </span>
                            {q.difficulty && (
                              <span className="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-bold text-slate-600 uppercase font-mono">
                                {q.difficulty}
                              </span>
                            )}
                          </div>
                          <div>
                            {isSubmitted ? (
                              <span className="rounded-full bg-emerald-100 px-2.5 py-0.5 text-[10px] font-bold text-emerald-800">
                                Completed
                              </span>
                            ) : (
                              <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-[10px] font-bold text-slate-600">
                                Available
                              </span>
                            )}
                          </div>
                        </div>

                        {q.is_also_recommended && (
                          <div className="mt-2.5 inline-flex items-center gap-1.5 rounded-lg border border-amber-200 bg-amber-50/90 px-2.5 py-1 text-[11px] font-semibold text-amber-800">
                            <Sparkles size={12} className="text-amber-600 shrink-0" />
                            <span>Also relevant to your competency gap</span>
                          </div>
                        )}

                        <h3 className="text-base font-bold text-[#123057] mt-2.5 group-hover:text-purple-800 transition-colors leading-snug">
                          {q.title}
                        </h3>

                        {q.competency_code && (
                          <div className="mt-2.5 flex items-center gap-2">
                            <span className="inline-block rounded-md bg-slate-100 px-2 py-0.5 font-mono text-[11px] font-bold text-slate-600">
                              {q.competency_code}
                            </span>
                          </div>
                        )}
                      </div>

                      <div className="mt-5 border-t border-slate-100 pt-3.5">
                        <button
                          onClick={() => startQuizSession(quizId)}
                          disabled={!quizId}
                          className={`w-full inline-flex items-center justify-center gap-2 rounded-xl py-2 text-xs font-bold text-white shadow-xs transition-all active:scale-95 ${
                            isSubmitted
                              ? "bg-slate-500 hover:bg-slate-600"
                              : "bg-purple-600 hover:bg-purple-700"
                          } disabled:opacity-40`}
                        >
                          <Play size={12} />
                          {isSubmitted ? "Retake Quiz" : "Attempt Quiz"}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* ── Section 2: Recommended for You ── */}
          <div className="space-y-4 pt-4 border-t border-slate-200/80">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-lg font-bold text-[#123057] flex items-center gap-2">
                    <Sparkles size={18} className="text-[#ef7e37]" />
                    Recommended for You
                  </h2>
                  <span className="rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-bold text-amber-800">
                    {recommendedQuizzes.length}
                  </span>
                </div>
                <p className="text-xs text-slate-500 mt-0.5">
                  Based on your role and competency gaps
                </p>
              </div>
            </div>

            {recommendedQuizzes.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-slate-200 bg-white/70 p-8 text-center">
                <div className="mx-auto flex h-11 w-11 items-center justify-center rounded-xl bg-teal-50 text-teal-600">
                  <CheckCircle2 size={20} />
                </div>
                <h3 className="mt-3 text-sm font-bold text-slate-700">No active gap recommendations</h3>
                <p className="mt-1 text-xs text-slate-500 max-w-sm mx-auto">
                  Your assessed competencies meet current role standards, or no targeted practice quizzes match your current profile gaps.
                </p>
              </div>
            ) : (
              <div className="grid gap-4 sm:grid-cols-2">
                {recommendedQuizzes.map((item, idx) => {
                  const quizId = item._id;
                  const matchPct = Math.round(item.recommendation_score * 100);

                  return (
                    <div
                      key={quizId || idx}
                      className="flex flex-col justify-between rounded-2xl border border-slate-200 bg-white p-5 shadow-xs hover:border-amber-300 hover:shadow-sm transition-all group"
                    >
                      <div>
                        <div className="flex items-center justify-between gap-2 flex-wrap">
                          <div className="flex items-center gap-1.5 flex-wrap">
                            <span className="rounded-full bg-amber-50 border border-amber-200 px-2.5 py-0.5 text-[10px] font-bold text-amber-800 flex items-center gap-1">
                              <Sparkles size={10} className="text-[#ef7e37]" />
                              Recommended
                            </span>
                            <span className="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-bold text-slate-600 font-mono">
                              {item.question_count} Qs
                            </span>
                            {item.difficulty && (
                              <span className="rounded bg-slate-100 px-2 py-0.5 text-[10px] font-bold text-slate-600 uppercase font-mono">
                                {item.difficulty}
                              </span>
                            )}
                          </div>
                          <span className="inline-flex items-center rounded-md bg-teal-50 border border-teal-200 px-2 py-0.5 text-[10px] font-bold text-teal-700 font-mono">
                            {matchPct}% Match
                          </span>
                        </div>

                        <h3 className="text-base font-bold text-[#123057] mt-3 group-hover:text-amber-800 transition-colors leading-snug">
                          {item.title}
                        </h3>

                        {/* Primary reason callout */}
                        {item.primary_reason && (
                          <div className="mt-2.5 text-xs text-slate-600 bg-amber-50/50 border border-amber-100 rounded-xl px-3 py-2 flex items-start gap-2 leading-relaxed">
                            <Target size={13} className="text-[#ef7e37] shrink-0 mt-0.5" />
                            <span>{item.primary_reason}</span>
                          </div>
                        )}

                        {/* Competency & Levels */}
                        <div className="mt-3 flex items-center gap-2 flex-wrap text-[11px]">
                          {item.competency_code && (
                            <span className="inline-block rounded-md bg-slate-100 px-2 py-0.5 font-mono font-bold text-slate-700">
                              {item.competency_code}
                            </span>
                          )}
                          <span className="text-slate-500 font-medium">
                            Level: <strong className="text-slate-700">{item.current_level.toFixed(1)}</strong> / Req: <strong className="text-slate-700">{item.required_level.toFixed(1)}</strong>
                          </span>
                          {item.gap_size > 0 && (
                            <span className="text-rose-600 font-bold">
                              (-{item.gap_size.toFixed(1)} gap)
                            </span>
                          )}
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="mt-5 border-t border-slate-100 pt-3.5 flex items-center gap-2">
                        <button
                          onClick={() => setSelectedWhyQuiz(item)}
                          className="flex-1 inline-flex items-center justify-center gap-1.5 rounded-xl border border-slate-200 bg-white py-2 text-xs font-bold text-slate-700 hover:bg-slate-50 hover:border-slate-300 transition-colors"
                        >
                          <HelpCircle size={13} className="text-slate-500" />
                          Why this quiz?
                        </button>
                        <button
                          onClick={() => startQuizSession(quizId)}
                          disabled={!quizId}
                          className="flex-1 inline-flex items-center justify-center gap-1.5 rounded-xl bg-[#ef7e37] hover:bg-[#d96a27] py-2 text-xs font-bold text-white shadow-xs transition-all active:scale-95 disabled:opacity-40"
                        >
                          <Play size={12} />
                          Start Practice
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── "Why this quiz?" Dialog / Modal ── */}
      {selectedWhyQuiz && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4 animate-in fade-in duration-200">
          <div className="relative w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl border border-slate-200">
            <button
              onClick={() => setSelectedWhyQuiz(null)}
              className="absolute right-4 top-4 rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700 transition-colors"
            >
              <X size={18} />
            </button>

            <div className="flex items-center gap-2.5">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-100 text-amber-700">
                <Sparkles size={20} />
              </div>
              <div>
                <h3 className="text-base font-bold text-[#123057]">Recommendation Rationale</h3>
                <p className="text-xs text-slate-500">How this assessment was matched to your profile</p>
              </div>
            </div>

            <div className="mt-5 space-y-4">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Target Assessment</span>
                <p className="text-sm font-bold text-[#123057] mt-0.5">{selectedWhyQuiz.title}</p>
              </div>

              <div className="grid grid-cols-2 gap-3 rounded-xl bg-slate-50 p-3.5 border border-slate-200/80">
                <div>
                  <span className="text-[11px] text-slate-500">Your Official Role</span>
                  <p className="text-xs font-bold text-[#123057] mt-0.5">
                    {selectedWhyQuiz.role_title || feedMeta?.role_title || "Official"}
                  </p>
                </div>
                <div>
                  <span className="text-[11px] text-slate-500">Competency Code</span>
                  <p className="text-xs font-mono font-bold text-teal-800 mt-0.5">
                    {selectedWhyQuiz.competency_code}
                  </p>
                </div>
                <div>
                  <span className="text-[11px] text-slate-500">Current Level</span>
                  <p className="text-xs font-bold text-slate-800 mt-0.5">
                    {selectedWhyQuiz.current_level.toFixed(1)} / 5.0
                  </p>
                </div>
                <div>
                  <span className="text-[11px] text-slate-500">Required Role Level</span>
                  <p className="text-xs font-bold text-slate-800 mt-0.5">
                    {selectedWhyQuiz.required_level.toFixed(1)} / 5.0
                  </p>
                </div>
              </div>

              {selectedWhyQuiz.gap_size > 0 && (
                <div className="flex items-center justify-between rounded-xl bg-rose-50 border border-rose-200/70 px-3.5 py-2.5">
                  <span className="text-xs font-bold text-rose-800">Assessed Competency Gap</span>
                  <span className="text-xs font-mono font-bold text-rose-700">
                    -{selectedWhyQuiz.gap_size.toFixed(1)} Level Gap
                  </span>
                </div>
              )}

              <div className="rounded-xl border border-slate-200 p-3.5 space-y-2">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">AI Scoring Analysis</span>
                <p className="text-xs text-slate-700 leading-relaxed font-medium">
                  {selectedWhyQuiz.primary_reason}
                </p>
                {selectedWhyQuiz.score_breakdown && (
                  <div className="pt-2 border-t border-slate-100 grid grid-cols-2 gap-2 text-[11px] text-slate-600">
                    <div>Role Alignment: <strong className="text-slate-800">{Math.round((selectedWhyQuiz.score_breakdown.role_score || 0) * 100)}%</strong></div>
                    <div>Gap Relevance: <strong className="text-slate-800">{Math.round((selectedWhyQuiz.score_breakdown.gap_score || 0) * 100)}%</strong></div>
                    <div>Severity Weight: <strong className="text-slate-800">{Math.round((selectedWhyQuiz.score_breakdown.severity_score || 0) * 100)}%</strong></div>
                    <div>Difficulty Fit: <strong className="text-slate-800">{Math.round((selectedWhyQuiz.score_breakdown.difficulty_score || 0) * 100)}%</strong></div>
                  </div>
                )}
              </div>
            </div>

            <div className="mt-6 flex items-center justify-end gap-2.5">
              <button
                onClick={() => setSelectedWhyQuiz(null)}
                className="rounded-xl border border-slate-200 px-4 py-2 text-xs font-bold text-slate-600 hover:bg-slate-50 transition-colors"
              >
                Close
              </button>
              <button
                onClick={() => {
                  const qid = selectedWhyQuiz._id;
                  setSelectedWhyQuiz(null);
                  startQuizSession(qid);
                }}
                className="rounded-xl bg-[#ef7e37] hover:bg-[#d96a27] px-4 py-2 text-xs font-bold text-white shadow-xs transition-colors flex items-center gap-1.5"
              >
                <Play size={12} />
                Start Practice Quiz
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default OfficialQuizzes;
