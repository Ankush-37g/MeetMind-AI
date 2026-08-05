export default function MetricsBar({ data }) {
  const metrics = [
    { value: data.chunks_count ?? '—', label: 'Audio Chunks', icon: '🎵' },
    { value: (data.word_count ?? 0).toLocaleString(), label: 'Words', icon: '📝' },
    { value: (data.transcript?.length ?? 0).toLocaleString(), label: 'Characters', icon: '🔤' },
    { value: (data.language ?? 'english').charAt(0).toUpperCase() + (data.language ?? 'english').slice(1), label: 'Language', icon: '🌐' },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5 animate-fade-in-up">
      {metrics.map((m, i) => (
        <div
          key={i}
          className="glass-card px-4 py-4 text-center group cursor-default"
        >
          <div className="text-xs mb-1 opacity-60">{m.icon}</div>
          <div className="text-2xl font-extrabold gradient-text">{m.value}</div>
          <div className="text-[0.68rem] text-text-muted uppercase tracking-wider font-semibold mt-1">{m.label}</div>
        </div>
      ))}
    </div>
  );
}
