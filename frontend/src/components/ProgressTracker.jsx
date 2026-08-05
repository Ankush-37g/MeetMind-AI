const steps = [
  { icon: '🎵', label: 'Processing audio' },
  { icon: '🎙️', label: 'Transcribing audio' },
  { icon: '📌', label: 'Generating title' },
  { icon: '📋', label: 'Summarizing transcript' },
  { icon: '✅', label: 'Extracting action items' },
  { icon: '🔑', label: 'Extracting key decisions' },
  { icon: '❓', label: 'Extracting open questions' },
  { icon: '🔗', label: 'Building knowledge base' },
];

export default function ProgressTracker({ currentStep, totalSteps }) {
  const progress = totalSteps > 0 ? (currentStep / totalSteps) * 100 : 0;

  return (
    <div className="glass-card p-6 max-w-2xl mx-auto animate-fade-in-up">
      <div className="flex items-center gap-2.5 mb-5 pb-3 border-b border-border-subtle">
        <div className="w-9 h-9 rounded-lg bg-amber-400/15 flex items-center justify-center text-lg text-amber-400">⚡</div>
        <div>
          <div className="text-base font-bold text-text-primary">Analyzing Meeting</div>
          <div className="text-xs text-text-muted">This may take a few minutes</div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full h-2 bg-bg-secondary rounded-full mb-5 overflow-hidden">
        <div className="progress-fill h-full" style={{ width: `${progress}%` }} />
      </div>

      {/* Steps */}
      <div className="space-y-1.5">
        {steps.map((step, i) => {
          const stepNum = i + 1;
          const isDone = stepNum < currentStep;
          const isActive = stepNum === currentStep;
          const isPending = stepNum > currentStep;

          return (
            <div
              key={i}
              className={`flex items-center gap-3 py-1.5 text-sm transition-all ${
                isDone ? 'text-emerald-400' : isActive ? 'text-violet-400' : 'text-text-muted opacity-40'
              }`}
            >
              <div
                className={`w-2 h-2 rounded-full flex-shrink-0 ${
                  isDone ? 'bg-emerald-400' : isActive ? 'bg-violet-500 pulse-glow' : 'bg-text-muted opacity-30'
                }`}
              />
              <span>{step.icon}</span>
              <span className={isActive ? 'font-medium' : ''}>{step.label}</span>
              {isDone && <span className="text-xs ml-auto">✓</span>}
            </div>
          );
        })}
      </div>
    </div>
  );
}
