import { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '../api';

export default function ChatPanel({ meetingId, initialChats = [] }) {
  const [messages, setMessages] = useState(initialChats);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    setMessages(initialChats);
  }, [meetingId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    const question = input.trim();
    if (!question || loading) return;

    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: question }]);
    setLoading(true);

    try {
      const res = await sendChatMessage(meetingId, question);
      setMessages((prev) => [...prev, { role: 'assistant', content: res.answer }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: 'assistant', content: `❌ Error: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="glass-card p-6 animate-fade-in-up flex flex-col" style={{ height: '500px' }}>
      {/* Header */}
      <div className="flex items-center gap-2.5 mb-4 pb-3 border-b border-border-subtle flex-shrink-0">
        <div className="w-8 h-8 rounded-lg bg-cyan-400/15 flex items-center justify-center text-base text-cyan-400">💬</div>
        <div>
          <div className="text-sm font-bold text-text-primary">Chat with Your Meeting</div>
          <div className="text-xs text-text-muted">Ask questions about the transcript using RAG</div>
        </div>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-3 mb-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-text-muted">
            <div className="text-3xl mb-3 opacity-40">💡</div>
            <div className="text-sm">Ask any question about your meeting transcript.</div>
            <div className="text-xs mt-1 text-text-muted">
              e.g. "What was discussed about the deadline?" or "Who is responsible for the demo?"
            </div>
          </div>
        ) : (
          messages.map((msg, i) => (
            <div
              key={i}
              className={`max-w-[85%] px-4 py-3 rounded-xl text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'chat-user ml-auto text-right'
                  : 'chat-assistant mr-auto'
              }`}
            >
              <div
                className={`text-[0.65rem] font-bold uppercase tracking-wider mb-1 ${
                  msg.role === 'user' ? 'text-violet-400' : 'text-cyan-400'
                }`}
              >
                {msg.role === 'user' ? 'You' : 'MeetMind AI'}
              </div>
              <div className="whitespace-pre-wrap">{msg.content}</div>
            </div>
          ))
        )}

        {loading && (
          <div className="chat-assistant mr-auto max-w-[85%] px-4 py-3 rounded-xl text-sm">
            <div className="text-[0.65rem] font-bold uppercase tracking-wider mb-1 text-cyan-400">MeetMind AI</div>
            <div className="text-text-muted animate-pulse">Thinking...</div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="flex gap-2 flex-shrink-0">
        <input
          type="text"
          placeholder="Ask a question about the meeting..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
          className="flex-1 bg-bg-secondary border border-border-subtle rounded-xl px-4 py-2.5 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/15 transition-all disabled:opacity-50"
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || loading}
          className="btn-gradient px-5 py-2.5 text-sm"
        >
          Send
        </button>
      </div>
    </div>
  );
}
