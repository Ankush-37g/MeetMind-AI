import { useState, useRef } from 'react';

export default function InputPanel({ onSubmit, disabled }) {
  const [inputMethod, setInputMethod] = useState('url');
  const [url, setUrl] = useState('');
  const [language, setLanguage] = useState('english');
  const [file, setFile] = useState(null);
  const fileRef = useRef(null);

  const handleSubmit = () => {
    if (disabled) return;

    const formData = new FormData();
    formData.append('language', language);

    if (inputMethod === 'url') {
      if (!url.trim()) return;
      formData.append('source', url.trim());
    } else {
      if (!file) return;
      formData.append('file', file);
    }

    onSubmit(formData);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !disabled) handleSubmit();
  };

  return (
    <div className="glass-card p-6 max-w-2xl mx-auto animate-fade-in-up">
      {/* Section Header */}
      <div className="flex items-center gap-2.5 mb-5 pb-3 border-b border-border-subtle">
        <div className="w-9 h-9 rounded-lg bg-violet-500/15 flex items-center justify-center text-lg text-violet-400">🎯</div>
        <div>
          <div className="text-base font-bold text-text-primary">Analyze a Meeting</div>
          <div className="text-xs text-text-muted">Paste a YouTube URL or upload an audio file</div>
        </div>
      </div>

      {/* Input Method Toggle */}
      <div className="flex gap-2 mb-4">
        {['url', 'file'].map((method) => (
          <button
            key={method}
            onClick={() => setInputMethod(method)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all border ${
              inputMethod === method
                ? 'bg-violet-500/15 border-violet-500/30 text-violet-400'
                : 'bg-transparent border-border-subtle text-text-muted hover:text-text-primary hover:border-violet-500/20'
            }`}
          >
            {method === 'url' ? '🔗  YouTube URL' : '📁  Upload File'}
          </button>
        ))}
      </div>

      {/* URL Input */}
      {inputMethod === 'url' ? (
        <input
          type="text"
          placeholder="https://www.youtube.com/watch?v=..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          className="w-full bg-bg-secondary border border-border-subtle rounded-xl px-4 py-3 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/15 transition-all disabled:opacity-50"
        />
      ) : (
        <div
          onClick={() => !disabled && fileRef.current?.click()}
          className={`w-full border border-dashed rounded-xl px-4 py-6 text-center cursor-pointer transition-all ${
            file
              ? 'border-emerald-400/30 bg-emerald-400/5'
              : 'border-violet-500/25 bg-violet-500/5 hover:border-violet-500/40 hover:bg-violet-500/8'
          } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          <input
            ref={fileRef}
            type="file"
            accept=".mp3,.mp4,.wav,.m4a,.ogg,.webm"
            onChange={(e) => setFile(e.target.files[0])}
            className="hidden"
            disabled={disabled}
          />
          {file ? (
            <div className="text-emerald-400 text-sm font-medium">📁 {file.name}</div>
          ) : (
            <>
              <div className="text-2xl mb-1 opacity-50">📤</div>
              <div className="text-sm text-text-muted">Click to upload audio/video</div>
              <div className="text-xs text-text-muted mt-1">MP3, MP4, WAV, M4A, OGG, WebM</div>
            </>
          )}
        </div>
      )}

      {/* Language + Submit */}
      <div className="flex items-center gap-3 mt-4">
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          disabled={disabled}
          className="bg-bg-secondary border border-border-subtle rounded-xl px-4 py-3 text-sm text-text-primary focus:outline-none focus:border-violet-500 transition-all disabled:opacity-50 cursor-pointer"
        >
          <option value="english">🇬🇧  English</option>
          <option value="hinglish">🇮🇳  Hinglish</option>
        </select>

        <button
          onClick={handleSubmit}
          disabled={disabled || (inputMethod === 'url' ? !url.trim() : !file)}
          className="btn-gradient flex-1 py-3 text-sm flex items-center justify-center gap-2"
        >
          {disabled ? (
            <>
              <span className="animate-spin">⏳</span> Processing...
            </>
          ) : (
            <>🚀  Analyze Meeting</>
          )}
        </button>
      </div>
    </div>
  );
}
