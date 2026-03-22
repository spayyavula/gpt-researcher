import React, { useEffect, useRef, useMemo } from 'react';
import LogMessage from './elements/LogMessage';

interface Log {
  header: string;
  text: string;
  metadata: any;
  key: string;
}

interface OrderedLogsProps {
  logs: Log[];
}

type AgentType = 'planner' | 'researcher' | 'writer' | 'reviewer' | 'curator' | 'scraper' | 'system';

interface ClassifiedLog extends Log {
  agent: AgentType;
  agentLabel: string;
  agentIcon: string;
  agentColor: string;
}

const AGENT_CONFIG: Record<AgentType, { label: string; icon: string; color: string; bgColor: string; borderColor: string }> = {
  planner: { label: 'Planner', icon: '🧭', color: 'text-blue-400', bgColor: 'bg-blue-500/10', borderColor: 'border-blue-500/30' },
  researcher: { label: 'Researcher', icon: '🔍', color: 'text-cyan-400', bgColor: 'bg-cyan-500/10', borderColor: 'border-cyan-500/30' },
  writer: { label: 'Writer', icon: '✍️', color: 'text-teal-400', bgColor: 'bg-teal-500/10', borderColor: 'border-teal-500/30' },
  reviewer: { label: 'Reviewer', icon: '✅', color: 'text-emerald-400', bgColor: 'bg-emerald-500/10', borderColor: 'border-emerald-500/30' },
  curator: { label: 'Curator', icon: '📚', color: 'text-purple-400', bgColor: 'bg-purple-500/10', borderColor: 'border-purple-500/30' },
  scraper: { label: 'Scraper', icon: '🌐', color: 'text-amber-400', bgColor: 'bg-amber-500/10', borderColor: 'border-amber-500/30' },
  system: { label: 'System', icon: '⚙️', color: 'text-gray-400', bgColor: 'bg-gray-500/10', borderColor: 'border-gray-500/30' },
};

function classifyAgent(log: Log): AgentType {
  const text = (log.text || '').toLowerCase();
  const header = (log.header || '').toLowerCase();
  const combined = text + ' ' + header;

  if (combined.includes('planning') || combined.includes('generating search') || combined.includes('research_plan') || combined.includes('agent_generated')) {
    return 'planner';
  }
  if (combined.includes('scraping') || combined.includes('browsing') || combined.includes('fetching')) {
    return 'scraper';
  }
  if (combined.includes('curating') || combined.includes('evaluating') || combined.includes('ranking source') || combined.includes('curator')) {
    return 'curator';
  }
  if (combined.includes('searching') || combined.includes('researching') || combined.includes('source') || combined.includes('subquer') || combined.includes('finding')) {
    return 'researcher';
  }
  if (combined.includes('writing') || combined.includes('generating report') || combined.includes('report_generation') || combined.includes('composing')) {
    return 'writer';
  }
  if (combined.includes('reviewing') || combined.includes('revising') || combined.includes('editing') || combined.includes('quality')) {
    return 'reviewer';
  }
  return 'system';
}

const LogsSection = ({ logs }: OrderedLogsProps) => {
  const logsContainerRef = useRef<HTMLDivElement>(null);

  const classifiedLogs: ClassifiedLog[] = useMemo(() => {
    return logs.map(log => {
      const agent = classifyAgent(log);
      const config = AGENT_CONFIG[agent];
      return {
        ...log,
        agent,
        agentLabel: config.label,
        agentIcon: config.icon,
        agentColor: config.color,
      };
    });
  }, [logs]);

  useEffect(() => {
    if (logsContainerRef.current) {
      logsContainerRef.current.scrollTop = logsContainerRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="container h-auto w-full shrink-0 rounded-lg border border-solid border-gray-700/40 bg-black/30 backdrop-blur-md shadow-lg p-5 mt-5">
      <div className="flex items-center justify-between pb-3 lg:pb-3.5">
        <div className="flex items-center gap-3">
          <div className="w-6 h-6 rounded-md bg-teal-500/20 border border-teal-500/30 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" width="12" height="12" fill="currentColor" className="text-teal-400">
              <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
            </svg>
          </div>
          <h3 className="text-sm font-semibold text-white">Agent Activity Log</h3>
          <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-gray-700/50 text-gray-400">
            {logs.length} {logs.length === 1 ? 'event' : 'events'}
          </span>
        </div>
      </div>

      <div
        ref={logsContainerRef}
        className="overflow-y-auto min-h-[200px] max-h-[500px] scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-300/10 space-y-2"
      >
        {classifiedLogs.map((log, index) => {
          const config = AGENT_CONFIG[log.agent];
          const isLast = index === classifiedLogs.length - 1;

          // Skip accordion-type logs - delegate to LogMessage
          if (log.header === 'subquery_context_window' || log.header === 'differences') {
            return (
              <div key={log.key || index} className={`rounded-lg border ${config.borderColor} ${config.bgColor} overflow-hidden`}>
                <div className="flex items-center gap-2 px-3 py-1.5 border-b border-gray-700/20">
                  <span className="text-xs">{log.agentIcon}</span>
                  <span className={`text-[10px] font-semibold ${config.color}`}>{log.agentLabel}</span>
                </div>
                <div className="px-1">
                  <LogMessage logs={[log]} />
                </div>
              </div>
            );
          }

          if (log.header === 'selected_images' || log.header === 'scraping_images') {
            return null;
          }

          return (
            <div
              key={log.key || index}
              className={`group relative rounded-lg border transition-all duration-200 ${
                isLast
                  ? `${config.borderColor} ${config.bgColor} shadow-sm`
                  : 'border-gray-700/20 bg-gray-900/40 hover:bg-gray-900/60'
              }`}
            >
              {/* Timeline connector */}
              {index < classifiedLogs.length - 1 && (
                <div className="absolute left-[1.15rem] top-full w-px h-2 bg-gray-700/30" />
              )}

              <div className="flex items-start gap-3 px-3 py-2.5">
                {/* Agent icon with status ring */}
                <div className={`relative flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center border ${
                  isLast ? config.borderColor : 'border-gray-700/40'
                } ${isLast ? config.bgColor : 'bg-gray-800/50'}`}>
                  <span className="text-xs">{log.agentIcon}</span>
                  {isLast && (
                    <span className="absolute -bottom-0.5 -right-0.5 w-2 h-2 rounded-full bg-teal-400 omc-pulse-dot" />
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className={`text-[10px] font-bold uppercase tracking-wider ${config.color}`}>
                      {log.agentLabel}
                    </span>
                    <span className="text-[9px] text-gray-600">•</span>
                    <span className="text-[10px] text-gray-500">Step {index + 1}</span>
                  </div>
                  <p className="text-sm leading-relaxed text-gray-300">
                    {log.text}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default LogsSection;
