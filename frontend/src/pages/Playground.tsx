/*
import { useState, useRef, useEffect } from 'react';
import { useRunAgent, useHealth } from '../features/agent/hooks/useAgent';
import { trackEvent } from '../app/telemetry/tracker';
import { Button } from '../shared/ui/Button';
import { Play, Square, Terminal, Settings, Copy, Check, Info, AlertTriangle, Lightbulb } from 'lucide-react';
import { cn } from '../shared/lib/utils';
import { StatusBanner } from '../shared/ui/StatusBanner';

const createSessionId = () => `session_${Math.random().toString(36).slice(2, 7)}`;

export const PlaygroundPage = () => {
    const [goal, setGoal] = useState('');
    const [sessionId, setSessionId] = useState(createSessionId);
    const [output, setOutput] = useState<{ text: string; role: 'user' | 'agent' }[]>([]);
    const [isCopied, setIsCopied] = useState(false);
    const [topP, setTopP] = useState(0.6);
    const [maxTokens, setMaxTokens] = useState(2048);

    const scrollRef = useRef<HTMLDivElement>(null);
    const runAgent = useRunAgent();
    const { data: health, isError: isHealthError } = useHealth();

    const normalizedHealth = String(health?.status || '').toLowerCase();
    const isSystemDegraded = !!health && (normalizedHealth !== 'ok' && normalizedHealth !== 'healthy');
    const isExecutionDisabled = isHealthError;

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [output]);

    const handleRun = async () => {
        if (!goal.trim() || isExecutionDisabled) return;

        trackEvent('agent_run_started', { goal });

        const userMessage = { text: goal, role: 'user' as const };
        setOutput(prev => [...prev, userMessage]);

        const currentGoal = goal;
        setGoal('');

        runAgent.mutate({ goal: currentGoal, session_id: sessionId }, {
            onSuccess: (data) => {
                setOutput(prev => [...prev, { text: data.result, role: 'agent' as const }]);
            },
            onError: (error: any) => {
                const message = error?.message || 'Unknown API error';
                const extra = error?.status === 401
                    ? ' (check VITE_API_KEY/API_KEY match)'
                    : '';
                const lower = message.toLowerCase();
                const suggestion = lower.includes('timeout') ? 'Try simplifying the goal or increasing timeout'
                    : lower.includes('ollama') || lower.includes('connection refused') ? 'Check that Ollama is running: ollama serve'
                        : lower.includes('401') ? 'Verify API_KEY matches between frontend and backend'
                            : 'Check backend logs for the full error trace';
                setOutput(prev => [...prev, {
                    text: `__ERROR__|${message}${extra}|${suggestion}`,
                    role: 'agent' as const,
                }]);
            }
        });
    };

    const copyToClipboard = () => {
        const fullText = output.map(o => `${o.role}: ${o.text}`).join('\n');
        navigator.clipboard.writeText(fullText);
        setIsCopied(true);
        setTimeout(() => setIsCopied(false), 2000);
    };

    return (
        <div className="h-[calc(100vh-8rem)] flex flex-col gap-6">
            {isHealthError && (
                <StatusBanner
                    type="error"
                    message="Backend API is unreachable. Verify API_BASE/CORS and that backend is running on port 8000."
                />
            )}
            {isSystemDegraded && !isHealthError && (
                <StatusBanner
                    type="error"
                    message={`System Degradation: ${health?.model || 'LLM Service'} is currently unreachable. You can still run, but responses may fail until LLM is up.`}
                />
            )}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Agent Playground</h1>
                    <p className="text-slate-500">Test goals and observe agent execution logic.</p>
                </div>
                <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={() => setOutput([])} disabled={output.length === 0}>
                        Clear History
                    </Button>
                    <Button variant="outline" size="sm" onClick={copyToClipboard} disabled={output.length === 0}>
                        {isCopied ? <Check size={16} className="text-green-500" /> : <Copy size={16} />}
                    </Button>
                </div>
            </div>

            <div className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-4 gap-6">
                [Legacy left column editor]
                <div className="lg:col-span-3 flex flex-col gap-4">
                    <div className="flex-1 bg-slate-900 rounded-xl shadow-inner border border-slate-800 flex flex-col overflow-hidden">
                        <div className="bg-slate-800/50 px-4 py-2 border-b border-slate-700 flex items-center justify-between">
                            <div className="flex items-center gap-2 text-slate-300 text-xs font-mono">
                                <Terminal size={14} />
                                <span>output_stream.log</span>
                            </div>
                            <div className="flex items-center gap-4">
                                <span className="text-[10px] text-slate-500 font-mono">ENCODING: UTF-8</span>
                                <div className="flex gap-1">
                                    <div className="w-2.5 h-2.5 rounded-full bg-red-500/20 border border-red-500/40" />
                                    <div className="w-2.5 h-2.5 rounded-full bg-amber-500/20 border border-amber-500/40" />
                                    <div className="w-2.5 h-2.5 rounded-full bg-green-500/20 border border-green-500/40" />
                                </div>
                            </div>
                        </div>

                        <div
                            ref={scrollRef}
                            className="flex-1 p-6 overflow-auto font-mono text-sm space-y-4 scrollbar-thin scrollbar-thumb-slate-700"
                        >
                            {output.length === 0 ? (
                                <div className="h-full flex flex-col items-center justify-center text-slate-600 space-y-2 opacity-50">
                                    <Play size={40} strokeWidth={1} />
                                    <p>Ready for execution input...</p>
                                </div>
                            ) : (
                                output.map((msg, i) => {
                                    // Special rendering for error messages
                                    if (msg.role === 'agent' && msg.text.startsWith('__ERROR__')) {
                                        const parts = msg.text.split('|');
                                        const errorMsg = parts[1] || 'Unknown error';
                                        const suggestion = parts[2] || '';
                                        return (
                                            <div key={i} className="p-3 rounded-lg border border-red-500/30 bg-red-500/5">
                                                <div className="flex items-center gap-2 mb-2">
                                                    <AlertTriangle size={14} className="text-red-400" />
                                                    <span className="text-[10px] uppercase tracking-widest text-red-400 font-bold">Execution Error</span>
                                                </div>
                                                <p className="text-sm text-red-300 font-mono mb-2">{errorMsg}</p>
                                                {suggestion && (
                                                    <div className="flex items-start gap-2 text-xs text-amber-300/80 bg-amber-500/10 rounded px-2.5 py-2 border border-amber-500/20">
                                                        <Lightbulb size={12} className="text-amber-400 mt-0.5 shrink-0" />
                                                        <span>{suggestion}</span>
                                                    </div>
                                                )}
                                            </div>
                                        );
                                    }
                                    return (
                                        <div key={i} className={cn(
                                            "p-3 rounded-lg border",
                                            msg.role === 'user'
                                                ? "bg-slate-800/40 border-slate-700 text-blue-400"
                                                : "bg-blue-500/5 border-blue-500/20 text-slate-300"
                                        )}>
                                            <div className="text-[10px] uppercase tracking-widest mb-1 opacity-50">
                                                {msg.role}
                                            </div>
                                            <div className="whitespace-pre-wrap">{msg.text}</div>
                                        </div>
                                    );
                                })
                            )}
                            {runAgent.isPending && (
                                <div className="flex items-center gap-2 text-blue-400">
                                    <span className="h-1.5 w-1.5 rounded-full bg-blue-500 animate-pulse" />
                                    <span className="animate-pulse">Agent is thinking...</span>
                                </div>
                            )}
                        </div>
                    </div>

                    [Legacy input area]
                    <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                        <div className="flex items-end gap-4">
                            <div className="flex-1">
                                <textarea
                                    id="agent-goal"
                                    name="agent-goal"
                                    className="w-full min-h-[100px] max-h-[300px] p-4 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-900 resize-none"
                                    placeholder="Enter a goal for the agent (e.g. 'Analyze the current market trends for AI stocks')..."
                                    value={goal}
                                    onChange={(e) => setGoal(e.target.value)}
                                    onKeyDown={(e) => {
                                        if (e.key === 'Enter' && !e.shiftKey) {
                                            e.preventDefault();
                                            handleRun();
                                        }
                                    }}
                                />
                            </div>
                            <div className="flex flex-col gap-2">
                                <Button
                                    className="h-12 w-12 rounded-full p-0 flex items-center justify-center"
                                    onClick={handleRun}
                                    disabled={!goal.trim() || runAgent.isPending || isExecutionDisabled}
                                    isLoading={runAgent.isPending}
                                >
                                    <Play size={20} fill="currentColor" />
                                </Button>
                                <Button
                                    variant="destructive"
                                    className="h-12 w-12 rounded-full p-0 flex items-center justify-center"
                                    disabled={!runAgent.isPending}
                                >
                                    <Square size={20} fill="currentColor" />
                                </Button>
                            </div>
                        </div>
                        <p className="mt-2 text-[10px] text-slate-400 flex items-center gap-1">
                            <Info size={10} />
                            Press Enter to run, Shift+Enter for new line.
                        </p>
                    </div>
                </div>

                [Legacy right column sidebar]
                <div className="hidden lg:block space-y-6">
                    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-6">
                        <div className="flex items-center gap-2 font-semibold text-slate-900">
                            <Settings size={18} className="text-blue-600" />
                            <span>Session Config</span>
                        </div>

                        <div className="space-y-4">
                            <div className="space-y-2">
                                <label htmlFor="session-id" className="text-xs font-bold text-slate-500 uppercase tracking-wider">Session ID</label>
                                <input
                                    id="session-id"
                                    name="session-id"
                                    type="text"
                                    value={sessionId}
                                    onChange={(e) => setSessionId(e.target.value)}
                                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded text-sm font-mono"
                                />
                            </div>

                            <div className="space-y-2">
                                <label htmlFor="top-p" className="text-xs font-bold text-slate-500 uppercase tracking-wider">Top-P Sampling</label>
                                <input
                                    id="top-p"
                                    name="top-p"
                                    type="range"
                                    min={0}
                                    max={1}
                                    step={0.05}
                                    value={topP}
                                    onChange={(event) => setTopP(Number(event.target.value))}
                                    className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                                />
                                <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                                    <span>0.0</span>
                                    <span>{topP.toFixed(2)}</span>
                                    <span>1.0</span>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label htmlFor="max-tokens" className="text-xs font-bold text-slate-500 uppercase tracking-wider">Max Tokens</label>
                                <div className="flex items-center gap-2">
                                    <input
                                        id="max-tokens"
                                        name="max-tokens"
                                        type="number"
                                        value={maxTokens}
                                        min={256}
                                        max={8192}
                                        step={128}
                                        onChange={(event) => setMaxTokens(Number(event.target.value))}
                                        className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded text-sm"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="pt-6 border-t border-slate-100">
                            <div className="bg-blue-50 p-4 rounded-lg border border-blue-100 italic text-xs text-blue-700 leading-relaxed">
                                Session ID is sent to backend memory. Top-P and Max Tokens are UI presets for upcoming server-side tuning support.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
*/

import { useEffect, useMemo, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { agentClient } from '../features/agent/api/agentClient';
import { useAgents, useHealth } from '../features/agent/hooks/useAgent';
import { trackEvent } from '../app/telemetry/tracker';
import { Button } from '../shared/ui/Button';
import { Play, Terminal, Copy, Check, Info, AlertTriangle, Lightbulb, Cpu, RadioTower } from 'lucide-react';
import { cn } from '../shared/lib/utils';
import { StatusBanner } from '../shared/ui/StatusBanner';

const createSessionId = () => `session_${Math.random().toString(36).slice(2, 7)}`;

type OutputMessage = { text: string; role: 'user' | 'agent' };
type RunEvent = { type: string; data: Record<string, any>; at: string };

export const PlaygroundPage = () => {
    const [searchParams] = useSearchParams();
    const [goal, setGoal] = useState(searchParams.get('goal') || '');
    const [sessionId, setSessionId] = useState(createSessionId);
    const [selectedAgentId, setSelectedAgentId] = useState(searchParams.get('agentId') || '');
    const [output, setOutput] = useState<OutputMessage[]>([]);
    const [eventLog, setEventLog] = useState<RunEvent[]>([]);
    const [activeRunId, setActiveRunId] = useState<string | null>(null);
    const [runStatus, setRunStatus] = useState<'idle' | 'queued' | 'running' | 'completed' | 'failed'>('idle');
    const [isCopied, setIsCopied] = useState(false);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const scrollRef = useRef<HTMLDivElement>(null);
    const streamRef = useRef<EventSource | null>(null);
    const pollRef = useRef<number | null>(null);
    const { data: health, isError: isHealthError } = useHealth();
    const { data: agents = [] } = useAgents();

    const normalizedHealth = String(health?.status || '').toLowerCase();
    const isSystemDegraded = !!health && (normalizedHealth !== 'ok' && normalizedHealth !== 'healthy');
    const isExecutionDisabled = isHealthError;

    const selectedAgent = useMemo(
        () => agents.find((agent: any) => agent.id === selectedAgentId || agent.name === searchParams.get('agent')),
        [agents, searchParams, selectedAgentId],
    );

    useEffect(() => {
        const deepLinkedAgentName = searchParams.get('agent');
        const deepLinkedAgentId = searchParams.get('agentId');
        if (deepLinkedAgentId) {
            setSelectedAgentId(deepLinkedAgentId);
            return;
        }
        if (deepLinkedAgentName && agents.length > 0) {
            const matched = agents.find((agent: any) => agent.name === deepLinkedAgentName);
            if (matched) {
                setSelectedAgentId(matched.id);
            }
        }
    }, [agents, searchParams]);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [eventLog, output]);

    useEffect(() => () => {
        streamRef.current?.close();
        if (pollRef.current) {
            window.clearInterval(pollRef.current);
        }
    }, []);

    const appendEvent = (type: string, data: Record<string, any> = {}) => {
        setEventLog((prev) => [...prev, { type, data, at: new Date().toISOString() }]);
    };

    const stopPolling = () => {
        if (pollRef.current) {
            window.clearInterval(pollRef.current);
            pollRef.current = null;
        }
    };

    const beginPolling = (runId: string) => {
        stopPolling();
        pollRef.current = window.setInterval(async () => {
            try {
                const status = await agentClient.pollRunStatus(runId);
                setRunStatus((status.status as typeof runStatus) || 'running');
                if (status.status === 'completed') {
                    stopPolling();
                    setOutput((prev) => [...prev, { text: status.result || '', role: 'agent' }]);
                }
                if (status.status === 'failed') {
                    stopPolling();
                    setOutput((prev) => [...prev, { text: `__ERROR__|${status.error || 'Run failed'}|Check the run details trace for the full failure context.`, role: 'agent' }]);
                }
            } catch {
                stopPolling();
            }
        }, 2000);
    };

    const beginStream = (runId: string) => {
        streamRef.current?.close();
        const source = new EventSource(agentClient.getRunStreamUrl(runId));
        streamRef.current = source;

        source.addEventListener('status_change', (event) => {
            const payload = JSON.parse(event.data);
            setRunStatus(payload.status || 'running');
            appendEvent('status_change', payload);
            if (payload.status === 'completed' || payload.status === 'failed') {
                source.close();
                stopPolling();
            }
        });

        source.addEventListener('planner_start', (event) => appendEvent('planner_start', JSON.parse(event.data)));
        source.addEventListener('planner_complete', (event) => appendEvent('planner_complete', JSON.parse(event.data)));
        source.addEventListener('execution_start', (event) => appendEvent('execution_start', JSON.parse(event.data)));
        source.addEventListener('tool_start', (event) => appendEvent('tool_start', JSON.parse(event.data)));
        source.addEventListener('tool_complete', (event) => appendEvent('tool_complete', JSON.parse(event.data)));
        source.addEventListener('execution_complete', (event) => appendEvent('execution_complete', JSON.parse(event.data)));
        source.addEventListener('synthesis_start', (event) => appendEvent('synthesis_start', JSON.parse(event.data)));
        source.addEventListener('synthesis_complete', (event) => appendEvent('synthesis_complete', JSON.parse(event.data)));
        source.addEventListener('result', (event) => {
            const payload = JSON.parse((event as MessageEvent<string>).data);
            appendEvent('result', payload);
            if (payload.result) {
                setOutput((prev) => [...prev, { text: payload.result, role: 'agent' }]);
            }
        });
        source.addEventListener('error', (event) => {
            const payload = JSON.parse((event as MessageEvent<string>).data);
            appendEvent('error', payload);
            setOutput((prev) => [...prev, { text: `__ERROR__|${payload.error || 'Run failed'}|Check the run details trace for the full failure context.`, role: 'agent' }]);
        });
        source.onerror = () => {
            source.close();
            beginPolling(runId);
        };
    };

    const handleRun = async () => {
        if (!goal.trim() || isExecutionDisabled) return;

        setIsSubmitting(true);
        setRunStatus('queued');
        setEventLog([]);
        trackEvent('agent_run_started', { goal, agentId: selectedAgentId || undefined });

        const currentGoal = goal;
        setOutput((prev) => [...prev, { text: currentGoal, role: 'user' }]);
        setGoal('');

        try {
            const submitted = await agentClient.submitRun({
                session_id: sessionId,
                goal: currentGoal,
                agent_id: selectedAgentId || undefined,
            });

            setActiveRunId(submitted.run_id);
            appendEvent('status_change', { status: submitted.status, run_id: submitted.run_id });
            beginStream(submitted.run_id);
        } catch (error: any) {
            const message = error?.message || 'Unknown API error';
            const suggestion = message.toLowerCase().includes('unauthorized')
                ? 'Sign in again or enable the explicit dev bypass if you are in local development.'
                : 'Check backend logs for the full error trace.';
            setOutput((prev) => [...prev, { text: `__ERROR__|${message}|${suggestion}`, role: 'agent' }]);
            setRunStatus('failed');
        } finally {
            setIsSubmitting(false);
        }
    };

    const copyToClipboard = () => {
        const fullText = output.map((item) => `${item.role}: ${item.text}`).join('\n');
        navigator.clipboard.writeText(fullText);
        setIsCopied(true);
        setTimeout(() => setIsCopied(false), 2000);
    };

    return (
        <div className="h-[calc(100vh-8rem)] flex flex-col gap-6">
            {isHealthError && (
                <StatusBanner
                    type="error"
                    message="Backend API is unreachable. Verify API_BASE/CORS and that backend is running on port 8000."
                />
            )}
            {isSystemDegraded && !isHealthError && (
                <StatusBanner
                    type="error"
                    message="System dependencies are degraded. Runs may queue but completion can still fail until readiness recovers."
                />
            )}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Agent Playground</h1>
                    <p className="text-slate-500">Submit queued runs, stream planner/tool events, and inspect live execution state.</p>
                </div>
                <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={() => setOutput([])} disabled={output.length === 0}>
                        Clear History
                    </Button>
                    <Button variant="outline" size="sm" onClick={copyToClipboard} disabled={output.length === 0}>
                        {isCopied ? <Check size={16} className="text-green-500" /> : <Copy size={16} />}
                    </Button>
                </div>
            </div>

            <div className="flex-1 min-h-0 grid grid-cols-1 lg:grid-cols-4 gap-6">
                <div className="lg:col-span-3 flex flex-col gap-4">
                    <div className="flex-1 bg-slate-900 rounded-xl shadow-inner border border-slate-800 flex flex-col overflow-hidden">
                        <div className="bg-slate-800/50 px-4 py-2 border-b border-slate-700 flex items-center justify-between">
                            <div className="flex items-center gap-2 text-slate-300 text-xs font-mono">
                                <Terminal size={14} />
                                <span>run_stream.log</span>
                            </div>
                            <div className="flex items-center gap-3 text-[10px] font-mono text-slate-400">
                                <span>{activeRunId ? `RUN ${activeRunId.slice(0, 8)}` : 'NO ACTIVE RUN'}</span>
                                <span className="uppercase">{runStatus}</span>
                            </div>
                        </div>

                        <div ref={scrollRef} className="flex-1 p-6 overflow-auto font-mono text-sm space-y-4">
                            {output.length === 0 && eventLog.length === 0 ? (
                                <div className="h-full flex flex-col items-center justify-center text-slate-600 space-y-2 opacity-50">
                                    <Play size={40} strokeWidth={1} />
                                    <p>Ready for queued execution...</p>
                                </div>
                            ) : (
                                <>
                                    {output.map((msg, index) => {
                                        if (msg.role === 'agent' && msg.text.startsWith('__ERROR__')) {
                                            const parts = msg.text.split('|');
                                            return (
                                                <div key={index} className="p-3 rounded-lg border border-red-500/30 bg-red-500/5">
                                                    <div className="flex items-center gap-2 mb-2">
                                                        <AlertTriangle size={14} className="text-red-400" />
                                                        <span className="text-[10px] uppercase tracking-widest text-red-400 font-bold">Execution Error</span>
                                                    </div>
                                                    <p className="text-sm text-red-300 font-mono mb-2">{parts[1] || 'Unknown error'}</p>
                                                    {parts[2] && (
                                                        <div className="flex items-start gap-2 text-xs text-amber-300/80 bg-amber-500/10 rounded px-2.5 py-2 border border-amber-500/20">
                                                            <Lightbulb size={12} className="text-amber-400 mt-0.5 shrink-0" />
                                                            <span>{parts[2]}</span>
                                                        </div>
                                                    )}
                                                </div>
                                            );
                                        }

                                        return (
                                            <div
                                                key={index}
                                                className={cn(
                                                    'p-3 rounded-lg border',
                                                    msg.role === 'user'
                                                        ? 'bg-slate-800/40 border-slate-700 text-blue-400'
                                                        : 'bg-blue-500/5 border-blue-500/20 text-slate-300',
                                                )}
                                            >
                                                <div className="text-[10px] uppercase tracking-widest mb-1 opacity-50">{msg.role}</div>
                                                <div className="whitespace-pre-wrap">{msg.text}</div>
                                            </div>
                                        );
                                    })}
                                    {eventLog.map((event, index) => (
                                        <div key={`${event.type}-${index}`} className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-xs text-slate-400">
                                            <div className="flex items-center justify-between">
                                                <span className="uppercase tracking-widest text-slate-500">{event.type}</span>
                                                <span>{new Date(event.at).toLocaleTimeString()}</span>
                                            </div>
                                            <pre className="mt-2 whitespace-pre-wrap text-slate-300">{JSON.stringify(event.data, null, 2)}</pre>
                                        </div>
                                    ))}
                                </>
                            )}
                            {(isSubmitting || runStatus === 'queued' || runStatus === 'running') && (
                                <div className="flex items-center gap-2 text-blue-400">
                                    <span className="h-1.5 w-1.5 rounded-full bg-blue-500 animate-pulse" />
                                    <span className="animate-pulse">Run is {runStatus === 'idle' ? 'submitting' : runStatus}...</span>
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                        <div className="flex items-end gap-4">
                            <div className="flex-1">
                                <textarea
                                    id="agent-goal"
                                    name="agent-goal"
                                    className="w-full min-h-[100px] max-h-[300px] p-4 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-900 resize-none"
                                    placeholder="Enter a goal for the agent (for example: Analyze the current market trends for AI stocks)..."
                                    value={goal}
                                    onChange={(event) => setGoal(event.target.value)}
                                    onKeyDown={(event) => {
                                        if (event.key === 'Enter' && !event.shiftKey) {
                                            event.preventDefault();
                                            handleRun();
                                        }
                                    }}
                                />
                            </div>
                            <Button
                                className="h-12 w-12 rounded-full p-0 flex items-center justify-center"
                                onClick={handleRun}
                                disabled={!goal.trim() || isSubmitting || isExecutionDisabled}
                                isLoading={isSubmitting}
                            >
                                <Play size={20} fill="currentColor" />
                            </Button>
                        </div>
                        <p className="mt-2 text-[10px] text-slate-400 flex items-center gap-1">
                            <Info size={10} />
                            Press Enter to queue a run, Shift+Enter for new line.
                        </p>
                    </div>
                </div>

                <div className="hidden lg:block space-y-6">
                    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-6">
                        <div className="flex items-center gap-2 font-semibold text-slate-900">
                            <Cpu size={18} className="text-blue-600" />
                            <span>Run Config</span>
                        </div>

                        <div className="space-y-4">
                            <div className="space-y-2">
                                <label htmlFor="session-id" className="text-xs font-bold text-slate-500 uppercase tracking-wider">Session ID</label>
                                <input
                                    id="session-id"
                                    name="session-id"
                                    type="text"
                                    value={sessionId}
                                    onChange={(event) => setSessionId(event.target.value)}
                                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded text-sm font-mono"
                                />
                            </div>

                            <div className="space-y-2">
                                <label htmlFor="agent-select" className="text-xs font-bold text-slate-500 uppercase tracking-wider">Agent</label>
                                <select
                                    id="agent-select"
                                    value={selectedAgentId}
                                    onChange={(event) => setSelectedAgentId(event.target.value)}
                                    className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded text-sm"
                                >
                                    <option value="">Default runtime</option>
                                    {agents.map((agent: any) => (
                                        <option key={agent.id} value={agent.id}>
                                            {agent.name} ({agent.current_version || agent.version})
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div className="rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
                                <div className="flex items-center gap-2 font-semibold text-slate-800">
                                    <RadioTower size={14} className="text-blue-600" />
                                    Live Run Status
                                </div>
                                <p className="mt-2">Current status: <span className="font-semibold uppercase">{runStatus}</span></p>
                                {activeRunId && <p className="mt-1 font-mono text-xs text-slate-500">Run ID: {activeRunId}</p>}
                                {selectedAgent && <p className="mt-1 text-xs text-slate-500">Selected agent: {selectedAgent.name}</p>}
                            </div>
                        </div>

                        <div className="pt-6 border-t border-slate-100">
                            <div className="bg-blue-50 p-4 rounded-lg border border-blue-100 italic text-xs text-blue-700 leading-relaxed">
                                The primary UX is queued execution with SSE streaming and polling fallback. Unsupported tuning controls were removed until the backend exposes them explicitly.
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
