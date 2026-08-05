import { useEffect, useState } from 'react';
import { getMeetings, deleteMeeting } from '../api';

export default function Sidebar({ onSelectMeeting, onNewAnalysis, activeMeetingId }) {
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchMeetings = async () => {
    try {
      const data = await getMeetings();
      setMeetings(data);
    } catch (err) {
      console.error('Failed to load meetings:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMeetings();
  }, [activeMeetingId]);

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (!confirm('Delete this meeting?')) return;
    try {
      await deleteMeeting(id);
      setMeetings((prev) => prev.filter((m) => m.id !== id));
      if (activeMeetingId === id) onNewAnalysis();
    } catch (err) {
      console.error('Delete failed:', err);
    }
  };

  const formatDate = (dateStr) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
  };

  return (
    <aside className="w-72 min-h-screen bg-bg-secondary border-r border-border-subtle flex flex-col flex-shrink-0">
      {/* Logo */}
      <div className="text-center py-6 px-4 border-b border-border-subtle">
        <span className="text-3xl">🧠</span>
        <div className="text-lg font-bold gradient-text mt-1">MeetMind AI</div>
        <div className="text-[0.7rem] text-text-muted mt-0.5">Intelligent Meeting Assistant</div>
      </div>

      {/* New Analysis Button */}
      <div className="px-4 py-4">
        <button
          onClick={onNewAnalysis}
          className="btn-gradient w-full py-2.5 text-sm flex items-center justify-center gap-2"
        >
          <span>＋</span> New Analysis
        </button>
      </div>

      {/* Meeting History */}
      <div className="px-4 pb-2">
        <div className="flex items-center gap-2 mb-3">
          <div className="w-7 h-7 rounded-lg bg-violet-500/15 flex items-center justify-center text-sm text-violet-400">📂</div>
          <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">History</span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-3 pb-4 space-y-1">
        {loading ? (
          <div className="text-center py-6 text-text-muted text-sm">Loading...</div>
        ) : meetings.length === 0 ? (
          <div className="text-center py-6 text-text-muted text-sm">
            <div className="text-2xl mb-2 opacity-40">📭</div>
            No meetings yet
          </div>
        ) : (
          meetings.map((m) => (
            <div
              key={m.id}
              onClick={() => onSelectMeeting(m.id)}
              className={`sidebar-item group flex items-start gap-2 ${activeMeetingId === m.id ? 'active' : ''}`}
            >
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-text-primary truncate">
                  {m.title || 'Untitled Meeting'}
                </div>
                <div className="text-[0.7rem] text-text-muted mt-0.5 flex items-center gap-2">
                  <span>{formatDate(m.created_at)}</span>
                  <span>·</span>
                  <span>{m.word_count?.toLocaleString()} words</span>
                </div>
              </div>
              <button
                onClick={(e) => handleDelete(e, m.id)}
                className="opacity-0 group-hover:opacity-100 text-text-muted hover:text-rose-400 text-sm transition-opacity p-1"
                title="Delete"
              >
                🗑
              </button>
            </div>
          ))
        )}
      </div>
    </aside>
  );
}
