import { useState, useRef, useEffect } from 'react';
import { useRunAgent, useHealth } from '../features/agent/hooks/useAgent';
import { trackEvent } from '../app/telemetry/tracker';
import { Button } from '../shared/ui/Button';
import { Play, Square, Terminal, Settings, Copy, Check, Info } from 'lucide-react';
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
                setOutput(prev => [...prev, { text: `Error: ${message}${extra}`, role: 'agent' as const }]);
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
                {/* Left Column: Editor */}
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
                                output.map((msg, i) => (
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
                                ))
                            )}
                            {runAgent.isPending && (
                                <div className="flex items-center gap-2 text-blue-400">
                                    <span className="h-1.5 w-1.5 rounded-full bg-blue-500 animate-pulse" />
                                    <span className="animate-pulse">Agent is thinking...</span>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Input Area */}
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

                {/* Right Column: Sidebar */}
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
