export default function QuestionsTab({ data }) {
  return (
    <div className="glass-card p-6 animate-fade-in-up">
      <div className="flex items-center gap-2.5 mb-4 pb-3 border-b border-border-subtle">
        <div className="w-8 h-8 rounded-lg bg-rose-400/15 flex items-center justify-center text-base text-rose-400">❓</div>
        <div>
          <div className="text-sm font-bold text-text-primary">Open Questions</div>
          <div className="text-xs text-text-muted">Unresolved topics needing follow-up</div>
        </div>
      </div>
      <div className="result-content whitespace-pre-wrap">{data || 'No open questions found.'}</div>
    </div>
  );
}
