/**
 * MeetMind AI — API Helper
 * Handles REST calls and SSE streaming for the React frontend.
 */

const API_BASE = '/api';

/**
 * Start meeting analysis with SSE progress streaming.
 * @param {FormData} formData - Contains source/file and language
 * @param {Function} onProgress - Called with { step, total, message }
 * @param {Function} onComplete - Called with full meeting result
 * @param {Function} onError - Called with error message
 */
export function analyzeMeeting(formData, onProgress, onComplete, onError) {
  const eventSource = fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    body: formData,
  });

  eventSource
    .then(async (response) => {
      if (!response.ok) {
        const err = await response.json();
        onError(err.detail || 'Failed to start analysis');
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop(); // Keep incomplete line in buffer

        let eventType = '';
        let eventData = '';

        for (const line of lines) {
          if (line.startsWith('event: ')) {
            eventType = line.slice(7).trim();
          } else if (line.startsWith('data: ')) {
            eventData = line.slice(6).trim();
          } else if (line === '' && eventType && eventData) {
            try {
              const parsed = JSON.parse(eventData);
              if (eventType === 'progress') {
                onProgress(parsed);
              } else if (eventType === 'complete') {
                onComplete(parsed);
              } else if (eventType === 'error') {
                onError(parsed.message);
              }
            } catch (e) {
              console.error('SSE parse error:', e);
            }
            eventType = '';
            eventData = '';
          }
        }
      }
    })
    .catch((err) => {
      onError(err.message || 'Connection failed');
    });
}

/**
 * Send a chat message to a meeting's RAG chain.
 */
export async function sendChatMessage(meetingId, question) {
  const res = await fetch(`${API_BASE}/chat/${meetingId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });

  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Chat failed');
  }

  return res.json();
}

/**
 * Get all past meetings.
 */
export async function getMeetings() {
  const res = await fetch(`${API_BASE}/meetings`);
  if (!res.ok) throw new Error('Failed to fetch meetings');
  return res.json();
}

/**
 * Get a specific meeting's full details + chat history.
 */
export async function getMeetingDetails(meetingId) {
  const res = await fetch(`${API_BASE}/meetings/${meetingId}`);
  if (!res.ok) throw new Error('Failed to fetch meeting');
  return res.json();
}

/**
 * Delete a meeting.
 */
export async function deleteMeeting(meetingId) {
  const res = await fetch(`${API_BASE}/meetings/${meetingId}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete meeting');
  return res.json();
}
