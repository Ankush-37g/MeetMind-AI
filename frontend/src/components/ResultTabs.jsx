import { useState } from 'react';
import SummaryTab from './SummaryTab';
import ActionItemsTab from './ActionItemsTab';
import DecisionsTab from './DecisionsTab';
import QuestionsTab from './QuestionsTab';
import TranscriptTab from './TranscriptTab';
import ChatPanel from './ChatPanel';

const tabs = [
  { id: 'summary', label: '📋 Summary' },
  { id: 'actions', label: '✅ Actions' },
  { id: 'decisions', label: '🔑 Decisions' },
  { id: 'questions', label: '❓ Questions' },
  { id: 'transcript', label: '📝 Transcript' },
  { id: 'chat', label: '💬 Chat' },
];

export default function ResultTabs({ data, meetingId }) {
  const [activeTab, setActiveTab] = useState('summary');

  return (
    <div className="animate-fade-in-up">
      {/* Tab Bar */}
      <div className="flex gap-1 bg-bg-secondary rounded-xl p-1 border border-border-subtle mb-5 overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'summary' && <SummaryTab summary={data.summary} />}
      {activeTab === 'actions' && <ActionItemsTab data={data.action_items} />}
      {activeTab === 'decisions' && <DecisionsTab data={data.key_decisions} />}
      {activeTab === 'questions' && <QuestionsTab data={data.open_questions} />}
      {activeTab === 'transcript' && <TranscriptTab transcript={data.transcript} />}
      {activeTab === 'chat' && <ChatPanel meetingId={meetingId} initialChats={data.chats || []} />}
    </div>
  );
}
