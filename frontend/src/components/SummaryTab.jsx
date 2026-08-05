export default function SummaryTab({ summary }) {
  const handleDownload = () => {
    const blob = new Blob([summary], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'meeting_summary.md';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="animate-fade-in-up">
      <div className="glass-card p-6">
        <div className="flex items-center gap-2.5 mb-4 pb-3 border-b border-border-subtle">
          <div className="w-8 h-8 rounded-lg bg-violet-500/15 flex items-center justify-center text-base text-violet-400">📋</div>
          <div>
            <div className="text-sm font-bold text-text-primary">Meeting Summary</div>
            <div className="text-xs text-text-muted">AI-generated concise summary</div>
          </div>
        </div>
        <div className="result-content whitespace-pre-wrap">{summary || 'No summary available.'}</div>
      </div>

      <button
        onClick={handleDownload}
        className="mt-3 px-4 py-2 rounded-xl border border-border-subtle text-text-secondary text-sm font-medium hover:border-violet-500 hover:text-violet-400 transition-all"
      >
        ⬇️  Download Summary
      </button>
    </div>
  );
}
