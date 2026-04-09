'use client';

import { useState, useEffect, useCallback } from 'react';
import { ChevronRight, ChevronLeft, Sparkles, Loader2, AlertCircle } from 'lucide-react';

export interface SymptomData {
  selected_symptoms: string[];
  duration: string;
  pain_level: number;
  risk_factors: string[];
  followup_answers: Record<string, string>;
  additional_notes: string;
}

interface Props {
  scanType: 'oral' | 'skin' | 'other';
  onChange: (data: SymptomData) => void;
}

const ORAL_SYMPTOMS = [
  'White patches', 'Red patches', 'Non-healing mouth sore',
  'Lump or thickening', 'Difficulty swallowing', 'Jaw or tongue pain',
  'Bleeding gums', 'Ear pain', 'Loose teeth', 'Voice changes',
  'Numbness in mouth', 'Persistent bad breath',
];

const SKIN_SYMPTOMS = [
  'New mole or growth', 'Existing mole changing', 'Irregular border',
  'Multiple colours in lesion', 'Spontaneous bleeding', 'Itching or burning',
  'Lesion larger than 6mm', 'Non-healing sore', 'Shiny or pearly bump',
  'Scaly or crusty patch', 'Dark streak under nail', 'Raised red patch',
];

const DURATIONS = [
  { value: '< 1 week', label: '< 1 week', sub: 'Just started' },
  { value: '1–4 weeks', label: '1–4 weeks', sub: 'A few weeks' },
  { value: '1–3 months', label: '1–3 months', sub: 'Several months' },
  { value: '> 3 months', label: '> 3 months', sub: 'Long-standing' },
];

const ORAL_RISKS = [
  'Tobacco / cigarettes', 'Alcohol use', 'Betel nut / paan',
  'Poor dental hygiene', 'HPV history', 'Family history of cancer',
];

const SKIN_RISKS = [
  'Heavy sun exposure', 'History of severe sunburns', 'Fair / light skin',
  'Family history of skin cancer', 'Previous skin cancer', 'Immunosuppression',
];

const PAIN_LABELS: Record<number, { label: string; color: string }> = {
  0: { label: 'None', color: 'text-success' },
  1: { label: 'Minimal', color: 'text-success' },
  2: { label: 'Mild', color: 'text-success' },
  3: { label: 'Mild', color: 'text-success' },
  4: { label: 'Moderate', color: 'text-warning' },
  5: { label: 'Moderate', color: 'text-warning' },
  6: { label: 'Moderate', color: 'text-warning' },
  7: { label: 'Severe', color: 'text-danger' },
  8: { label: 'Severe', color: 'text-danger' },
  9: { label: 'Very Severe', color: 'text-danger' },
  10: { label: 'Unbearable', color: 'text-danger' },
};

export default function SymptomQuestionnaire({ scanType, onChange }: Props) {
  const [step, setStep] = useState(1);
  const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([]);
  const [duration, setDuration] = useState('');
  const [painLevel, setPainLevel] = useState(0);
  const [riskFactors, setRiskFactors] = useState<string[]>([]);
  const [followupQuestions, setFollowupQuestions] = useState<string[]>([]);
  const [followupAnswers, setFollowupAnswers] = useState<Record<string, string>>({});
  const [additionalNotes, setAdditionalNotes] = useState('');
  const [loadingFollowup, setLoadingFollowup] = useState(false);
  const [followupError, setFollowupError] = useState(false);

  const symptoms = scanType === 'skin' ? SKIN_SYMPTOMS : ORAL_SYMPTOMS;
  const risks = scanType === 'skin' ? SKIN_RISKS : ORAL_RISKS;
  const painInfo = PAIN_LABELS[painLevel];

  const toggleSymptom = (s: string) =>
    setSelectedSymptoms((prev) => prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s]);

  const toggleRisk = (r: string) =>
    setRiskFactors((prev) => prev.includes(r) ? prev.filter((x) => x !== r) : [...prev, r]);

  const notifyParent = useCallback(() => {
    onChange({
      selected_symptoms: selectedSymptoms,
      duration,
      pain_level: painLevel,
      risk_factors: riskFactors,
      followup_answers: followupAnswers,
      additional_notes: additionalNotes,
    });
  }, [selectedSymptoms, duration, painLevel, riskFactors, followupAnswers, additionalNotes, onChange]);

  useEffect(() => { notifyParent(); }, [notifyParent]);

  const fetchFollowup = async () => {
    setLoadingFollowup(true);
    setFollowupError(false);
    try {
      const res = await fetch('http://localhost:8000/api/v1/symptoms/followup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          scan_type: scanType,
          selected_symptoms: selectedSymptoms,
          duration,
          pain_level: painLevel,
          risk_factors: riskFactors,
        }),
      });
      const data = await res.json();
      setFollowupQuestions(data.questions ?? []);
    } catch {
      setFollowupError(true);
      setFollowupQuestions([
        'Have you seen a doctor about these symptoms before?',
        'Are these symptoms getting worse, better, or staying the same?',
      ]);
    } finally {
      setLoadingFollowup(false);
    }
  };

  const goToStep3 = async () => {
    setStep(3);
    if (followupQuestions.length === 0) await fetchFollowup();
  };

  const totalSelected = selectedSymptoms.length + riskFactors.length + (duration ? 1 : 0);

  return (
    <div className="space-y-4">
      {/* Progress bar */}
      <div className="flex items-center gap-2 mb-1">
        {[1, 2, 3].map((s) => (
          <div key={s} className="flex-1 flex flex-col items-center gap-1">
            <div
              className={`h-1.5 w-full rounded-full transition-all duration-500 ${
                step > s ? 'bg-accent' : step === s ? 'bg-accent/60' : 'bg-border'
              }`}
            />
          </div>
        ))}
      </div>
      <div className="flex justify-between text-xs text-muted mb-3">
        <span className={step === 1 ? 'text-accent font-medium' : ''}>Symptoms</span>
        <span className={step === 2 ? 'text-accent font-medium' : ''}>Details</span>
        <span className={step === 3 ? 'text-accent font-medium' : ''}>AI Questions</span>
      </div>

      {/* ── STEP 1: Symptom chips ── */}
      {step === 1 && (
        <div className="space-y-4">
          <div>
            <p className="text-sm font-medium text-white mb-0.5">Which symptoms are you experiencing?</p>
            <p className="text-xs text-muted mb-3">Tap all that apply — or skip if unsure</p>
            <div className="flex flex-wrap gap-2">
              {symptoms.map((s) => {
                const active = selectedSymptoms.includes(s);
                return (
                  <button
                    key={s}
                    type="button"
                    onClick={() => toggleSymptom(s)}
                    className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-all duration-200 ${
                      active
                        ? 'bg-accent/20 border-accent text-accent shadow-sm shadow-accent/20'
                        : 'bg-background-secondary border-border text-muted hover:border-border-light hover:text-white'
                    }`}
                  >
                    {active && <span className="mr-1">✓</span>}
                    {s}
                  </button>
                );
              })}
            </div>
          </div>

          {selectedSymptoms.length > 0 && (
            <div className="flex items-center gap-2 text-xs text-accent bg-accent/5 border border-accent/20 rounded-lg px-3 py-2">
              <span className="font-semibold">{selectedSymptoms.length}</span> symptom{selectedSymptoms.length !== 1 ? 's' : ''} selected
            </div>
          )}

          <button
            type="button"
            onClick={() => setStep(2)}
            className="w-full flex items-center justify-center gap-2 bg-accent/10 hover:bg-accent/20 border border-accent/30 text-accent rounded-xl py-2.5 text-sm font-medium transition-all"
          >
            {selectedSymptoms.length === 0 ? 'Skip / No symptoms' : 'Next'}
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* ── STEP 2: Duration, Pain, Risk Factors ── */}
      {step === 2 && (
        <div className="space-y-5">
          {/* Duration */}
          <div>
            <p className="text-sm font-medium text-white mb-2">How long have you had this?</p>
            <div className="grid grid-cols-2 gap-2">
              {DURATIONS.map((d) => (
                <button
                  key={d.value}
                  type="button"
                  onClick={() => setDuration(d.value)}
                  className={`p-3 rounded-xl border text-left transition-all duration-200 ${
                    duration === d.value
                      ? 'border-accent bg-accent/10'
                      : 'border-border bg-background-secondary hover:border-border-light'
                  }`}
                >
                  <div className={`text-sm font-semibold ${duration === d.value ? 'text-accent' : 'text-white'}`}>{d.label}</div>
                  <div className="text-xs text-muted mt-0.5">{d.sub}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Pain slider */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm font-medium text-white">Pain / discomfort level</p>
              <span className={`text-sm font-bold ${painInfo.color}`}>
                {painLevel}/10 — {painInfo.label}
              </span>
            </div>
            <div className="relative">
              <input
                type="range"
                min={0}
                max={10}
                value={painLevel}
                onChange={(e) => setPainLevel(Number(e.target.value))}
                className="w-full h-2 rounded-full appearance-none cursor-pointer accent-accent"
                style={{
                  background: `linear-gradient(to right, #3B82F6 ${painLevel * 10}%, #1F2937 ${painLevel * 10}%)`,
                }}
              />
              <div className="flex justify-between text-xs text-muted mt-1">
                <span>0 — None</span>
                <span>5 — Moderate</span>
                <span>10 — Severe</span>
              </div>
            </div>
          </div>

          {/* Risk factors */}
          <div>
            <p className="text-sm font-medium text-white mb-0.5">Known risk factors</p>
            <p className="text-xs text-muted mb-2">Select all that apply to you</p>
            <div className="flex flex-wrap gap-2">
              {risks.map((r) => {
                const active = riskFactors.includes(r);
                return (
                  <button
                    key={r}
                    type="button"
                    onClick={() => toggleRisk(r)}
                    className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-all duration-200 ${
                      active
                        ? 'bg-warning/20 border-warning/60 text-warning'
                        : 'bg-background-secondary border-border text-muted hover:border-border-light hover:text-white'
                    }`}
                  >
                    {active && <span className="mr-1">✓</span>}
                    {r}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="flex gap-2 pt-1">
            <button
              type="button"
              onClick={() => setStep(1)}
              className="flex items-center gap-1 px-4 py-2.5 rounded-xl border border-border text-muted hover:text-white text-sm transition-all"
            >
              <ChevronLeft className="h-4 w-4" /> Back
            </button>
            <button
              type="button"
              onClick={goToStep3}
              className="flex-1 flex items-center justify-center gap-2 bg-gradient-to-r from-accent/20 to-purple-500/10 hover:from-accent/30 hover:to-purple-500/20 border border-accent/30 text-accent rounded-xl py-2.5 text-sm font-medium transition-all"
            >
              <Sparkles className="h-4 w-4" />
              Get AI Follow-up Questions
            </button>
          </div>
        </div>
      )}

      {/* ── STEP 3: Gemini follow-up ── */}
      {step === 3 && (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-accent/20 flex items-center justify-center shrink-0">
              <Sparkles className="h-4 w-4 text-accent" />
            </div>
            <div>
              <p className="text-sm font-medium text-white">Gemini AI Follow-up</p>
              <p className="text-xs text-muted">Personalised questions based on your symptom profile</p>
            </div>
          </div>

          {followupError && (
            <div className="flex items-center gap-2 text-xs text-warning bg-warning/5 border border-warning/20 rounded-lg px-3 py-2">
              <AlertCircle className="h-3.5 w-3.5 shrink-0" />
              Backend offline — showing default questions
            </div>
          )}

          {loadingFollowup ? (
            <div className="flex flex-col items-center gap-3 py-8">
              <Loader2 className="h-6 w-6 text-accent animate-spin" />
              <p className="text-sm text-muted">Gemini is analysing your symptom profile...</p>
              <div className="flex gap-1 mt-1">
                {['Parsing symptoms', 'Assessing risk', 'Generating questions'].map((t, i) => (
                  <span key={t} className="text-xs px-2 py-0.5 rounded-full bg-accent/10 text-accent/60 border border-accent/10"
                    style={{ animationDelay: `${i * 0.3}s` }}>
                    {t}
                  </span>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              {followupQuestions.map((q, i) => (
                <div key={i} className="bg-background-secondary rounded-xl p-3 border border-border">
                  <label className="text-xs font-medium text-accent/80 block mb-1.5">
                    Q{i + 1}: {q}
                  </label>
                  <input
                    value={followupAnswers[`q${i}`] ?? ''}
                    onChange={(e) => setFollowupAnswers((prev) => ({ ...prev, [`q${i}`]: e.target.value }))}
                    className="w-full bg-background-card border border-border rounded-lg px-3 py-2 text-sm text-white placeholder:text-muted focus:outline-none focus:border-accent transition-colors"
                    placeholder="Type your answer..."
                  />
                </div>
              ))}

              <div className="bg-background-secondary rounded-xl p-3 border border-border">
                <label className="text-xs font-medium text-muted block mb-1.5">
                  Anything else you'd like the doctor to know?
                </label>
                <textarea
                  value={additionalNotes}
                  onChange={(e) => setAdditionalNotes(e.target.value)}
                  rows={2}
                  className="w-full bg-background-card border border-border rounded-lg px-3 py-2 text-sm text-white placeholder:text-muted focus:outline-none focus:border-accent transition-colors resize-none"
                  placeholder="Any additional context..."
                />
              </div>
            </div>
          )}

          {/* Symptom summary */}
          {!loadingFollowup && totalSelected > 0 && (
            <div className="bg-background-secondary rounded-xl p-3 border border-border/60">
              <p className="text-xs text-muted mb-2 font-medium uppercase tracking-wide">Your profile summary</p>
              <div className="flex flex-wrap gap-1.5">
                {selectedSymptoms.map((s) => (
                  <span key={s} className="text-xs px-2 py-0.5 rounded-full bg-accent/10 text-accent border border-accent/20">
                    {s}
                  </span>
                ))}
                {duration && (
                  <span className="text-xs px-2 py-0.5 rounded-full bg-border text-white border border-border-light">
                    {duration}
                  </span>
                )}
                {painLevel > 0 && (
                  <span className={`text-xs px-2 py-0.5 rounded-full border ${painLevel >= 7 ? 'bg-danger/10 text-danger border-danger/20' : 'bg-warning/10 text-warning border-warning/20'}`}>
                    Pain {painLevel}/10
                  </span>
                )}
                {riskFactors.map((r) => (
                  <span key={r} className="text-xs px-2 py-0.5 rounded-full bg-warning/10 text-warning border border-warning/20">
                    {r}
                  </span>
                ))}
              </div>
            </div>
          )}

          <button
            type="button"
            onClick={() => setStep(2)}
            className="flex items-center gap-1 px-4 py-2 rounded-xl border border-border text-muted hover:text-white text-sm transition-all"
          >
            <ChevronLeft className="h-4 w-4" /> Back
          </button>
        </div>
      )}
    </div>
  );
}
