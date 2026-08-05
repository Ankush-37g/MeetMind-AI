import { useState } from 'react';
import Hero from './components/Hero';
import Sidebar from './components/Sidebar';
import InputPanel from './components/InputPanel';
import ProgressTracker from './components/ProgressTracker';
import MetricsBar from './components/MetricsBar';
import ResultTabs from './components/ResultTabs';
import { analyzeMeeting, getMeetingDetails } from './api';

export default function App() {
  // ── State ────────────────────────────────────────────────
  const [view, setView] = useState('input'); // 'input' | 'processing' | 'results'
  const [result, setResult] = useState(null);
  const [meetingId, setMeetingId] = useState(null);
  const [progress, setProgress] = useState({ step: 0, total: 8, message: '' });
  const [error, setError] = useState(null);

  // ── Handlers ─────────────────────────────────────────────
  const handleSubmit = (formData) => {
    setView('processing');
    setError(null);
    setProgress({ step: 0, total: 8, message: 'Starting...' });

    analyzeMeeting(
      formData,
      // onProgress
      (p) => setProgress(p),
      // onComplete
      (data) => {
        setResult(data);
        setMeetingId(data.meeting_id);
        setView('results');
      },
      // onError
      (msg) => {
        setError(msg);
        setView('input');
      }
    );
  };

  const handleSelectMeeting = async (id) => {
    try {
      setView('processing');
      setProgress({ step: 8, total: 8, message: 'Loading meeting...' });
      const data = await getMeetingDetails(id);
      setResult(data);
      setMeetingId(data.id);
      setView('results');
    } catch (err) {
      setError(err.message);
      setView('input');
    }
  };

  const handleNewAnalysis = () => {
    setView('input');
    setResult(null);
    setMeetingId(null);
    setError(null);
  };

  // ── Render ───────────────────────────────────────────────
  return (
    <div className="flex min-h-screen bg-bg-primary">
      {/* Ambient Glow */}
      <div className="ambient-glow" />

      {/* Sidebar */}
      <Sidebar
        onSelectMeeting={handleSelectMeeting}
        onNewAnalysis={handleNewAnalysis}
        activeMeetingId={meetingId}
      />

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto relative z-10">
        <div className="max-w-4xl mx-auto px-6 pb-12">
          <Hero />

          {/* Error Alert */}
          {error && (
            <div className="glass-card p-4 mb-5 border-rose-400/30 animate-fade-in-up">
              <div className="flex items-center gap-2 text-rose-400 text-sm font-medium">
                <span>❌</span>
                <span>{error}</span>
                <button
                  onClick={() => setError(null)}
                  className="ml-auto text-text-muted hover:text-text-primary transition-colors"
                >
                  ✕
                </button>
              </div>
            </div>
          )}

          {/* Input View */}
          {view === 'input' && (
            <InputPanel onSubmit={handleSubmit} disabled={false} />
          )}

          {/* Processing View */}
          {view === 'processing' && (
            <ProgressTracker
              currentStep={progress.step}
              totalSteps={progress.total}
            />
          )}

          {/* Results View */}
          {view === 'results' && result && (
            <>
              {/* Title Card */}
              <div className="glass-card px-5 py-4 text-center mb-5 animate-fade-in-up">
                <div className="text-[0.68rem] text-text-muted uppercase font-bold tracking-widest mb-1">
                  Generated Title
                </div>
                <div className="text-xl font-bold text-text-primary">
                  📌 {result.title || 'Untitled Meeting'}
                </div>
              </div>

              <MetricsBar data={result} />

              <ResultTabs data={result} meetingId={meetingId} />
            </>
          )}
        </div>
      </main>
    </div>
  );
}
