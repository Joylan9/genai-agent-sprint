import { useParams, Link, useNavigate } from 'react-router-dom';
import { useTrace } from '../features/agent/hooks/useAgent';
import { agentClient } from '../features/agent/api/agentClient';
import { Button } from '../shared/ui/Button';
import { Badge } from '../shared/ui/Badge';
import { ChevronLeft, Clock, CheckCircle2, XCircle, FileJson, List, Info, Activity, Zap, Copy, Check } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { cn } from '../shared/lib/utils';
import { useEffect, useState } from 'react';
import { RunTimeline } from '../shared/ui/RunTimeline';
import { ErrorPanel } from '../shared/ui/ErrorPanel';

// ============================================================
// Trace Step Component — renders one observation from the trace
// ============================================================
const TraceStep = ({ observation, index }: { observation: any; index: number }) => {
    const status = observation?.response?.status || 'unknown';
    const isSuccess = status === 'success';
    const toolName = observation?.tool || `Step ${index + 1}`;
    const query = observation?.query || '';

    return (
        <div className="flex gap-4 group">
            <div className="flex flex-col items-center">
                <div
                    className={cn(
                        'w-8 h-8 rounded-full flex items-center justify-center border-2 z-10 bg-white transition-colors duration-300',
                        isSuccess
                            ? 'border-green-500 text-green-500'
                            : status === 'error'
                                ? 'border-red-500 text-red-500'
                                : 'border-slate-200 text-slate-400'
                    )}
                >
                    {isSuccess ? (
                        <CheckCircle2 size={18} />
                    ) : status === 'error' ? (
                        <XCircle size={18} />
                    ) : (
                        <span>{index + 1}</span>
                    )}
                </div>
                <div className="flex-1 w-0.5 bg-slate-200 my-1 group-last:hidden" />
            </div>
            <div className="pb-8 flex-1">
                <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm transition-all duration-300 hover:border-blue-300 hover:shadow-md">
                    <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                            <h3 className="font-semibold text-slate-900">{toolName}</h3>
                            <Badge variant={isSuccess ? 'green' : 'red'}>{status}</Badge>
                        </div>
                    </div>
                    {query && (
                        <p className="text-sm text-slate-600 mb-3">
                            <span className="font-medium text-slate-500">Query:</span> {query}
                        </p>
                    )}
                    {observation?.response && (
                        <div className="rounded-md overflow-hidden text-xs">
                            <SyntaxHighlighter
                                language="json"
                                style={vscDarkPlus}
                                customStyle={{ margin: 0, maxHeight: '300px' }}
                            >
                                {JSON.stringify(observation.response, null, 2)}
                            </SyntaxHighlighter>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

// ============================================================
// Log Row Component — renders one observation as a log line
// ============================================================
const LogRow = ({ observation, index }: { observation: any; index: number }) => {
    const status = observation?.response?.status || 'unknown';
    const tool = observation?.tool || 'unknown';
    const query = observation?.query || '';
    const dataSnippet =
        typeof observation?.response?.data === 'string'
            ? observation.response.data.slice(0, 200)
            : JSON.stringify(observation?.response?.data || '').slice(0, 200);

    return (
        <div className="px-4 py-1 font-mono text-xs border-b border-slate-800 flex items-start gap-4 hover:bg-slate-800/50 transition-colors">
            <span className="text-slate-500 w-8 text-right select-none">{index + 1}</span>
            <span
                className={cn(
                    'w-16 shrink-0',
                    status === 'success' ? 'text-green-400' : status === 'error' ? 'text-red-400' : 'text-slate-400'
                )}
            >
                [{status.toUpperCase()}]
            </span>
            <span className="text-blue-400 w-24 shrink-0">{tool}</span>
            <span className="text-slate-400 shrink-0">→</span>
            <span className="text-slate-300 truncate">{query}</span>
            {dataSnippet && (
                <span className="text-slate-500 truncate ml-2">| {dataSnippet}</span>
            )}
        </div>
    );
};

// ============================================================
// Latency Breakdown Component
// ============================================================
const LatencyBreakdown = ({ latency }: { latency: any }) => {
    if (!latency) return null;

    const items = [
        { label: 'Planner', value: latency.planner, color: 'bg-blue-500' },
        { label: 'Tool Execution', value: latency.tool_wall_time, color: 'bg-amber-500' },
        { label: 'Synthesis', value: latency.synthesis, color: 'bg-purple-500' },
    ];

    const total = latency.total || 0;

    return (
        <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
            <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
                <Zap size={14} className="text-amber-500" />
                Latency Breakdown
            </h3>
            {/* Bar */}
            <div className="h-3 rounded-full bg-slate-100 overflow-hidden flex mb-3">
                {items.map((item) =>
                    item.value > 0 ? (
                        <div
                            key={item.label}
                            className={cn(item.color, 'h-full transition-all')}
                            style={{ width: `${Math.max((item.value / total) * 100, 2)}%` }}
                            title={`${item.label}: ${item.value.toFixed(2)}s`}
                        />
                    ) : null
                )}
            </div>
            {/* Legend */}
            <div className="flex flex-wrap gap-4 text-xs text-slate-600">
                {items.map((item) => (
                    <div key={item.label} className="flex items-center gap-1.5">
                        <div className={cn('w-2.5 h-2.5 rounded-full', item.color)} />
                        <span>
                            {item.label}: <strong>{(item.value || 0).toFixed(2)}s</strong>
                        </span>
                    </div>
                ))}
                <div className="flex items-center gap-1.5 ml-auto font-semibold text-slate-900">
                    Total: {total.toFixed(2)}s
                </div>
            </div>
        </div>
    );
};

// ============================================================
// Main RunDetails Page
// ============================================================
export const RunDetailsPage = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState<'trace' | 'logs' | 'artifacts'>('trace');
    const [linkCopied, setLinkCopied] = useState(false);
    const [traceData, setTraceData] = useState<any>(null);
    const [liveEvents, setLiveEvents] = useState<Array<{ type: string; data: Record<string, any>; at: string }>>([]);

    const { data: trace, isLoading, error } = useTrace(id || '');

    useEffect(() => {
        if (trace) {
            setTraceData(trace);
        }
    }, [trace]);

    useEffect(() => {
        if (!id || !traceData || !['queued', 'running'].includes(String(traceData.status || '').toLowerCase())) {
            return;
        }

        let cancelled = false;
        let pollHandle: number | null = null;
        const syncTrace = async () => {
            const latest = await agentClient.getTrace(id);
            if (!cancelled) {
                setTraceData(latest);
            }
        };

        const appendEvent = (type: string, data: Record<string, any>) => {
            if (cancelled) return;
            setLiveEvents((prev) => [...prev, { type, data, at: new Date().toISOString() }]);
        };

        const stream = new EventSource(agentClient.getRunStreamUrl(id));
        const eventTypes = ['status_change', 'planner_start', 'planner_complete', 'execution_start', 'tool_start', 'tool_complete', 'execution_complete', 'synthesis_start', 'synthesis_complete', 'result', 'error'];
        eventTypes.forEach((eventType) => {
            stream.addEventListener(eventType, async (event) => {
                const payload = JSON.parse(event.data);
                appendEvent(eventType, payload);
                if (eventType === 'status_change') {
                    setTraceData((prev: any) => ({ ...prev, status: payload.status || prev?.status, error: payload.error || prev?.error }));
                }
                if (eventType === 'result') {
                    setTraceData((prev: any) => ({ ...prev, final_answer: payload.result || prev?.final_answer }));
                }
                if (eventType === 'result' || (eventType === 'status_change' && ['completed', 'failed'].includes(payload.status))) {
                    await syncTrace();
                    stream.close();
                    if (pollHandle) {
                        window.clearInterval(pollHandle);
                    }
                }
            });
        });
        stream.onerror = () => {
            stream.close();
            if (pollHandle) return;
            pollHandle = window.setInterval(async () => {
                await syncTrace();
            }, 2000);
        };

        return () => {
            cancelled = true;
            stream.close();
            if (pollHandle) {
                window.clearInterval(pollHandle);
            }
        };
    }, [id, traceData?.status]);

    if (isLoading)
        return <div className="p-8 text-center text-slate-500">Loading trace data...</div>;
    if (error)
        return (
            <div className="p-8 text-center text-red-500 border border-red-200 rounded-lg bg-red-50">
                Error loading trace: {(error as any).message}
            </div>
        );

    const currentTrace = traceData || trace;
    const observations = currentTrace?.observations || [];
    const latency = currentTrace?.latency;
    const totalDuration = latency?.total ? `${latency.total.toFixed(2)}s` : 'N/A';
    const startedAt = currentTrace?.started_at || currentTrace?.timestamp
        ? new Date(currentTrace.started_at || currentTrace.timestamp).toLocaleString()
        : 'Unknown';
    const cacheHit = currentTrace?.cache_hit === true;

    return (
        <div className="space-y-6 max-w-5xl mx-auto pb-12">
            {/* Header */}
            <div className="flex items-center gap-4">
                <Link to="/runs">
                    <Button
                        variant="ghost"
                        size="sm"
                        className="p-2 h-auto text-slate-500 hover:text-blue-600"
                    >
                        <ChevronLeft size={20} />
                    </Button>
                </Link>
                <div>
                    <div className="flex items-center gap-3">
                        <h1 className="text-2xl font-bold text-slate-900">Run Details</h1>
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-700 border border-blue-200 uppercase tracking-wider">
                            {id?.slice(0, 8)}...
                        </span>
                        {cacheHit && (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-700 border border-amber-200 uppercase tracking-wider">
                                ⚡ Cache Hit
                            </span>
                        )}
                    </div>
                    <p className="text-slate-500 text-sm flex items-center gap-1.5 mt-0.5">
                        <Clock size={14} />
                        Started: {startedAt} • Duration: {totalDuration}
                    </p>
                </div>
                <div className="ml-auto flex items-center gap-2">
                    <button
                        onClick={() => {
                            const url = `${window.location.origin}/runs/${id}`;
                            navigator.clipboard.writeText(url).then(() => {
                                setLinkCopied(true);
                                setTimeout(() => setLinkCopied(false), 2000);
                            });
                        }}
                        className={cn(
                            'flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all border',
                            linkCopied
                                ? 'bg-emerald-50 border-emerald-200 text-emerald-600 dark:bg-emerald-950/30 dark:border-emerald-800 dark:text-emerald-400'
                                : 'bg-white border-slate-200 text-slate-600 hover:bg-blue-50 hover:border-blue-200 hover:text-blue-600 dark:bg-slate-800 dark:border-slate-700 dark:text-slate-400 dark:hover:bg-blue-950/30',
                        )}
                    >
                        {linkCopied ? <Check size={12} /> : <Copy size={12} />}
                        {linkCopied ? 'Copied!' : 'Share Run'}
                    </button>
                </div>
            </div>

            {/* Goal */}
            {currentTrace?.goal && (
                <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                    <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Goal</span>
                    <p className="text-slate-900 mt-1">{currentTrace.goal}</p>
                </div>
            )}

            {/* Error Panel for failed runs */}
            {(currentTrace?.status === 'failed' || currentTrace?.error) && (
                <ErrorPanel
                    error={currentTrace?.error || 'Unknown error'}
                    goal={currentTrace?.goal}
                    onRetry={() => navigate(`/execute${currentTrace?.goal ? `?goal=${encodeURIComponent(currentTrace.goal)}` : ''}`)}
                />
            )}

            {/* Execution Timeline */}
            <RunTimeline
                latency={latency}
                observations={observations}
                status={currentTrace?.status}
            />

            {/* Latency Breakdown */}
            <LatencyBreakdown latency={latency} />

            {/* Tab Bar */}
            <div className="flex items-center gap-1 bg-white p-1 rounded-lg border border-slate-200 shadow-sm">
                <button
                    onClick={() => setActiveTab('trace')}
                    className={cn(
                        'flex items-center gap-2 px-4 py-2 rounded-md transition-all text-sm font-medium',
                        activeTab === 'trace'
                            ? 'bg-blue-600 text-white shadow-sm'
                            : 'text-slate-500 hover:bg-slate-50'
                    )}
                >
                    <Activity size={16} />
                    Trace ({observations.length} steps)
                </button>
                <button
                    onClick={() => setActiveTab('logs')}
                    className={cn(
                        'flex items-center gap-2 px-4 py-2 rounded-md transition-all text-sm font-medium',
                        activeTab === 'logs'
                            ? 'bg-blue-600 text-white shadow-sm'
                            : 'text-slate-500 hover:bg-slate-50'
                    )}
                >
                    <List size={16} />
                    Raw Logs
                </button>
                <button
                    onClick={() => setActiveTab('artifacts')}
                    className={cn(
                        'flex items-center gap-2 px-4 py-2 rounded-md transition-all text-sm font-medium',
                        activeTab === 'artifacts'
                            ? 'bg-blue-600 text-white shadow-sm'
                            : 'text-slate-500 hover:bg-slate-50'
                    )}
                >
                    <FileJson size={16} />
                    Raw JSON
                </button>
            </div>

            {/* Tab Content */}
            <div className="min-h-[400px]">
                {activeTab === 'trace' && (
                    <div className="space-y-2 animate-in fade-in zoom-in-95 duration-300">
                        {observations.map((obs: any, i: number) => (
                            <TraceStep key={i} observation={obs} index={i} />
                        ))}
                        {observations.length === 0 && (
                            <div className="bg-white p-12 text-center rounded-xl border-2 border-dashed border-slate-200 text-slate-400">
                                No trace steps recorded for this run.
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'logs' && (
                    <div className="bg-slate-900 rounded-xl border border-slate-800 shadow-xl overflow-hidden animate-in fade-in duration-300">
                        <div className="bg-slate-800/80 px-4 py-2 flex items-center justify-between border-b border-slate-700">
                            <span className="text-[10px] font-mono text-slate-400">
                                OBSERVATION_LOG :: {observations.length} entries
                            </span>
                            <div className="flex gap-2">
                                <div className="h-1.5 w-1.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]" />
                                <span className="text-[10px] font-mono text-green-500 tracking-tighter">
                                    COMPLETE
                                </span>
                            </div>
                        </div>
                        <div className="h-[500px] overflow-auto scrollbar-thin scrollbar-thumb-slate-700 bg-slate-900">
                            {observations.length > 0 ? (
                                observations.map((obs: any, i: number) => (
                                    <LogRow key={i} observation={obs} index={i} />
                                ))
                            ) : (
                                <div className="p-8 text-center text-slate-500 font-mono text-xs">
                                    No observations recorded.
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {activeTab === 'artifacts' && (
                    <div className="bg-slate-900 rounded-xl border border-slate-800 shadow-xl overflow-hidden animate-in fade-in duration-300">
                        <div className="bg-slate-800/80 px-4 py-2 border-b border-slate-700">
                            <span className="text-[10px] font-mono text-slate-400">
                                RAW_TRACE_JSON
                            </span>
                        </div>
                        <div className="max-h-[600px] overflow-auto">
                            <SyntaxHighlighter
                                language="json"
                                style={vscDarkPlus}
                                customStyle={{ margin: 0 }}
                            >
                                {JSON.stringify(currentTrace, null, 2)}
                            </SyntaxHighlighter>
                        </div>
                    </div>
                )}
            </div>

            {liveEvents.length > 0 && (
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
                    <h3 className="text-sm font-semibold text-slate-700 mb-3">Live Event Feed</h3>
                    <div className="space-y-2">
                        {liveEvents.map((event, index) => (
                            <div key={`${event.type}-${index}`} className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs">
                                <div className="flex items-center justify-between text-slate-500">
                                    <span className="font-semibold uppercase tracking-wider">{event.type}</span>
                                    <span>{new Date(event.at).toLocaleTimeString()}</span>
                                </div>
                                <pre className="mt-2 whitespace-pre-wrap text-slate-700">{JSON.stringify(event.data, null, 2)}</pre>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Info Banner */}
            <div className="bg-blue-50 border border-blue-100 rounded-xl p-6 flex gap-4">
                <div className="bg-blue-600 p-2 h-fit rounded-lg text-white">
                    <Info size={20} />
                </div>
                <div>
                    <h4 className="text-blue-900 font-bold mb-1 italic tracking-tight">
                        System Notice
                    </h4>
                    <p className="text-blue-700/80 text-sm leading-relaxed">
                        Trace data is retained for 30 days. The Raw JSON tab displays the complete
                        trace document from MongoDB.
                    </p>
                </div>
            </div>
        </div>
    );
};
