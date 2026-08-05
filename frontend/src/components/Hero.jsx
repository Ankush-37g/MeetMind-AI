export default function Hero() {
  return (
    <div className="text-center py-8 mb-4">
      <div className="inline-flex items-center gap-1.5 bg-violet-500/10 border border-violet-500/25 text-violet-400 px-4 py-1.5 rounded-full text-xs font-semibold tracking-wide uppercase mb-4 animate-fade-in-up">
        🧠 AI-Powered
      </div>
      <h1 className="text-5xl font-extrabold gradient-text leading-tight mb-3 animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
        MeetMind AI
      </h1>
      <p className="text-text-secondary text-base font-normal max-w-xl mx-auto leading-relaxed animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
        Transform any meeting recording into actionable insights.<br />
        Summarize, extract decisions, and chat with your transcript.
      </p>
    </div>
  );
}
