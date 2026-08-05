export default function DecisionsTab({ data }) {
  return (
    <div className="glass-card p-6 animate-fade-in-up">
      <div className="flex items-center gap-2.5 mb-4 pb-3 border-b border-border-subtle">
        <div className="w-8 h-8 rounded-lg bg-amber-400/15 flex items-center justify-center text-base text-amber-400">🔑</div>
        <div>
          <div className="text-sm font-bold text-text-primary">Key Decisions</div>
          <div className="text-xs text-text-muted">Important decisions made during the meeting</div>
        </div>
      </div>
      <div className="result-content whitespace-pre-wrap">{data || 'No key decisions found.'}</div>
    </div>
  );
}
