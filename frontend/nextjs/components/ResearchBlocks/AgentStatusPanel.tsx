import React, { useMemo } from 'react';

interface Log {
  header: string;
  text: string;
  metadata?: any;
}

interface AgentStatusPanelProps {
  logs: Log[];
  loading: boolean;
}

type Phase = 'planning' | 'researching' | 'writing' | 'reviewing' | 'complete';
type AgentStatus = 'idle' | 'working' | 'done';

interface AgentInfo {
  name: string;
  icon: string;
  status: AgentStatus;
  phase: Phase;
}

const PHASE_ORDER: Phase[] = ['planning', 'researching', 'writing', 'reviewing', 'complete'];

const PHASE_CONFIG: Record<Phase, { label: string; icon: string; color: string }> = {
  planning: { label: 'Planning', icon: '🧭', color: 'from-blue-500 to-cyan-500' },
  researching: { label: 'Researching', icon: '🔍', color: 'from-cyan-500 to-teal-500' },
  writing: { label: 'Writing', icon: '✍️', color: 'from-teal-500 to-emerald-500' },
  reviewing: { label: 'Reviewing', icon: '✅', color: 'from-emerald-500 to-green-500' },
  complete: { label: 'Complete', icon: '🎯', color: 'from-green-500 to-green-400' },
};

function detectPhase(logs: Log[]): Phase {
  if (!logs || logs.length === 0) return 'planning';

  const allText = logs.map(l => l.text?.toLowerCase() || '').join(' ');
  const allHeaders = logs.map(l => l.header?.toLowerCase() || '').join(' ');
  const combined = allText + ' ' + allHeaders;

  if (combined.includes('conclusion') || combined.includes('report generated') || combined.includes('report_complete')) {
    return 'complete';
  }
  if (combined.includes('reviewing') || combined.includes('revising') || combined.includes('quality')) {
    return 'reviewing';
  }
  if (combined.includes('writing report') || combined.includes('generating report') || combined.includes('report_generation') || combined.includes('writing section')) {
    return 'writing';
  }
  if (combined.includes('researching') || combined.includes('searching') || combined.includes('scraping') || combined.includes('browsing') || combined.includes('source') || combined.includes('subquer')) {
    return 'researching';
  }
  return 'planning';
}

function detectAgents(logs: Log[], currentPhase: Phase, loading: boolean): AgentInfo[] {
  const agents: AgentInfo[] = [];

  const plannerDone = PHASE_ORDER.indexOf(currentPhase) > PHASE_ORDER.indexOf('planning');
  agents.push({
    name: 'Planner',
    icon: '🧭',
    status: plannerDone ? 'done' : (currentPhase === 'planning' && loading ? 'working' : 'idle'),
    phase: 'planning',
  });

  const researcherDone = PHASE_ORDER.indexOf(currentPhase) > PHASE_ORDER.indexOf('researching');
  agents.push({
    name: 'Researcher',
    icon: '🔍',
    status: researcherDone ? 'done' : (currentPhase === 'researching' && loading ? 'working' : 'idle'),
    phase: 'researching',
  });

  const writerDone = PHASE_ORDER.indexOf(currentPhase) > PHASE_ORDER.indexOf('writing');
  agents.push({
    name: 'Writer',
    icon: '✍️',
    status: writerDone ? 'done' : (currentPhase === 'writing' && loading ? 'working' : 'idle'),
    phase: 'writing',
  });

  const reviewerDone = currentPhase === 'complete';
  agents.push({
    name: 'Reviewer',
    icon: '✅',
    status: reviewerDone ? 'done' : (currentPhase === 'reviewing' && loading ? 'working' : 'idle'),
    phase: 'reviewing',
  });

  return agents;
}

const AgentStatusPanel: React.FC<AgentStatusPanelProps> = ({ logs, loading }) => {
  const currentPhase = useMemo(() => detectPhase(logs), [logs]);
  const agents = useMemo(() => detectAgents(logs, currentPhase, loading), [logs, currentPhase, loading]);
  const phaseIndex = PHASE_ORDER.indexOf(currentPhase);
  const progressPercent = currentPhase === 'complete' ? 100 : (phaseIndex / (PHASE_ORDER.length - 1)) * 100;

  return (
    <div className="container w-full shrink-0 rounded-lg border border-solid border-gray-700/40 bg-black/30 backdrop-blur-md shadow-lg p-5 mt-5">
      {/* Header */}
      <div className="flex items-center justify-between pb-4">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-teal-500/20 to-cyan-500/20 border border-teal-500/30 flex items-center justify-center">
              <span className="text-sm">🤖</span>
            </div>
            {loading && (
              <span className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-teal-400 omc-pulse-dot" />
            )}
          </div>
          <div>
            <h3 className="text-sm font-semibold text-white">Agent Orchestration</h3>
            <p className="text-xs text-gray-400">
              {loading ? (
                <span className="flex items-center gap-1.5">
                  <span className="inline-block w-1.5 h-1.5 rounded-full bg-teal-400 omc-pulse-dot" />
                  {PHASE_CONFIG[currentPhase].label} in progress...
                </span>
              ) : currentPhase === 'complete' ? (
                'Research complete'
              ) : (
                'Waiting to start'
              )}
            </p>
          </div>
        </div>
        {/* Phase badge */}
        <div className={`px-3 py-1 rounded-full text-xs font-medium border ${
          currentPhase === 'complete'
            ? 'bg-green-500/10 border-green-500/30 text-green-400'
            : loading
            ? 'bg-teal-500/10 border-teal-500/30 text-teal-400'
            : 'bg-gray-500/10 border-gray-500/30 text-gray-400'
        }`}>
          {PHASE_CONFIG[currentPhase].icon} {PHASE_CONFIG[currentPhase].label}
        </div>
      </div>

      {/* Phase Progress Bar */}
      <div className="mb-5">
        <div className="flex justify-between mb-2">
          {PHASE_ORDER.filter(p => p !== 'complete').map((phase, i) => {
            const isActive = phase === currentPhase;
            const isDone = PHASE_ORDER.indexOf(currentPhase) > i;
            return (
              <div key={phase} className="flex flex-col items-center flex-1">
                <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs border-2 transition-all duration-500 ${
                  isDone
                    ? 'bg-teal-500/20 border-teal-400 text-teal-300'
                    : isActive
                    ? 'bg-teal-500/10 border-teal-500 text-teal-400 omc-glow-ring'
                    : 'bg-gray-800 border-gray-600 text-gray-500'
                }`}>
                  {isDone ? '✓' : PHASE_CONFIG[phase].icon}
                </div>
                <span className={`text-[10px] mt-1 font-medium ${
                  isDone ? 'text-teal-400' : isActive ? 'text-teal-300' : 'text-gray-500'
                }`}>
                  {PHASE_CONFIG[phase].label}
                </span>
              </div>
            );
          })}
        </div>
        {/* Progress track */}
        <div className="relative h-1 bg-gray-700/50 rounded-full mx-8 -mt-[2.1rem] mb-8">
          <div
            className="absolute h-full rounded-full bg-gradient-to-r from-teal-500 to-cyan-400 transition-all duration-700 ease-out"
            style={{ width: `${Math.min(progressPercent, 100)}%` }}
          />
          {loading && progressPercent < 100 && (
            <div
              className="absolute h-full w-8 rounded-full omc-progress-shimmer"
              style={{ left: `${Math.max(progressPercent - 4, 0)}%` }}
            />
          )}
        </div>
      </div>

      {/* Agent Cards */}
      <div className="grid grid-cols-4 gap-3">
        {agents.map((agent) => (
          <div
            key={agent.name}
            className={`relative rounded-lg border p-3 transition-all duration-300 ${
              agent.status === 'working'
                ? 'bg-teal-500/5 border-teal-500/40 shadow-[0_0_15px_rgba(20,184,166,0.1)]'
                : agent.status === 'done'
                ? 'bg-green-500/5 border-green-500/30'
                : 'bg-gray-800/30 border-gray-700/30'
            }`}
          >
            {/* Working indicator */}
            {agent.status === 'working' && (
              <div className="absolute top-2 right-2">
                <span className="relative flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-teal-400 opacity-75" />
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-teal-500" />
                </span>
              </div>
            )}
            {agent.status === 'done' && (
              <div className="absolute top-2 right-2">
                <span className="inline-flex h-2.5 w-2.5 rounded-full bg-green-500" />
              </div>
            )}

            <div className="flex items-center gap-2 mb-1.5">
              <span className="text-lg">{agent.icon}</span>
              <span className="text-xs font-semibold text-white">{agent.name}</span>
            </div>
            <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full ${
              agent.status === 'working'
                ? 'bg-teal-500/15 text-teal-300'
                : agent.status === 'done'
                ? 'bg-green-500/15 text-green-300'
                : 'bg-gray-700/50 text-gray-500'
            }`}>
              {agent.status === 'working' ? 'Working...' : agent.status === 'done' ? 'Complete' : 'Standby'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AgentStatusPanel;
