export default function TranscriptTab({ transcript }) {
  const handleDownload = () => {
    const blob = new Blob([transcript], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'transcript.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="animate-fade-in-up">
      <div className="glass-card p-6">
        <div className="flex items-center gap-2.5 mb-4 pb-3 border-b border-border-subtle">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/15 flex items-center justify-center text-base text-indigo-500">📝</div>
          <div>
            <div className="text-sm font-bold text-text-primary">Full Transcript</div>
            <div className="text-xs text-text-muted">Raw transcription output</div>
          </div>
        </div>
        <div className="transcript-box max-h-96 overflow-y-auto bg-bg-primary/60 border border-border-subtle rounded-xl p-5">
          {transcript || 'No transcript available.'}
        </div>
      </div>

      <button
        onClick={handleDownload}
        className="mt-3 px-4 py-2 rounded-xl border border-border-subtle text-text-secondary text-sm font-medium hover:border-violet-500 hover:text-violet-400 transition-all"
      >
        ⬇️  Download Transcript
      </button>
    </div>
  );
}
