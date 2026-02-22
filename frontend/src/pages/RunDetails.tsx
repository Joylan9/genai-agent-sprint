import { useParams, Link } from 'react-router-dom';
import { useTrace } from '../features/agent/hooks/useAgent';
import { Button } from '../shared/ui/Button';
import { ChevronLeft, Clock, CheckCircle2, FileJson, List, Info, Activity } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { cn } from '../shared/lib/utils';
import { useState } from 'react';

const TraceStep = ({ step, index }: { step: any, index: number }) => (
    <div className="flex gap-4 group">
        <div className="flex flex-col items-center">
            <div className={cn(
                "w-8 h-8 rounded-full flex items-center justify-center border-2 z-10 bg-white transition-colors duration-300",
                step.status === 'completed' ? "border-green-500 text-green-500" : "border-slate-200 text-slate-400 group-last:border-blue-500"
            )}>
                {step.status === 'completed' ? <CheckCircle2 size={18} /> : <span>{index + 1}</span>}
            </div>
            <div className="flex-1 w-0.5 bg-slate-200 my-1 group-last:hidden" />
        </div>
        <div className="pb-8 flex-1">
            <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-sm transition-all duration-300 hover:border-blue-300 hover:shadow-md">
                <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-slate-900">{step.name}</h3>
                    <span className="text-xs text-slate-400 font-mono">142ms</span>
                </div>
                <p className="text-sm text-slate-600 mb-3">{step.description || 'Executing agent logic step...'}</p>
                {step.output && (
                    <div className="rounded-md overflow-hidden text-xs">
                        <SyntaxHighlighter language="json" style={vscDarkPlus} customStyle={{ margin: 0 }}>
                            {JSON.stringify(step.output, null, 2)}
                        </SyntaxHighlighter>
                    </div>
                )}
            </div>
        </div>
    </div>
);

const LogRow = ({ line, index }: { line: string, index: number }) => (
    <div className="px-4 py-1 font-mono text-xs border-b border-slate-800 flex items-start gap-4 hover:bg-slate-800/50 transition-colors">
        <span className="text-slate-500 w-12 text-right select-none">{index + 1}</span>
        <span className="text-slate-300 whitespace-pre-wrap">{line}</span>
    </div>
);

export const RunDetailsPage = () => {
    const { id } = useParams<{ id: string }>();
    const [activeTab, setActiveTab] = useState<'trace' | 'logs' | 'artifacts'>('trace');

    const { data: trace, isLoading, error } = useTrace(id || '');

    const mockLogs = Array.from({ length: 1000 }).map((_, i) =>
        `[${new Date().toISOString()}] INFO: Step ${i % 5} processing with worker node-${Math.floor(i / 100)}...`
    );

    if (isLoading) return <div className="p-8 text-center text-slate-500">Loading trace data...</div>;
    if (error) return <div className="p-8 text-center text-red-500 border border-red-200 rounded-lg bg-red-50">Error loading trace: {(error as any).message}</div>;

    return (
        <div className="space-y-6 max-w-5xl mx-auto pb-12">
            <div className="flex items-center gap-4">
                <Link to="/runs">
                    <Button variant="ghost" size="sm" className="p-2 h-auto text-slate-500 hover:text-blue-600">
                        <ChevronLeft size={20} />
                    </Button>
                </Link>
                <div>
                    <div className="flex items-center gap-3">
                        <h1 className="text-2xl font-bold text-slate-900">Run Details</h1>
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-700 border border-blue-200 uppercase tracking-wider">
                            RequestId: {id?.slice(0, 8)}...
                        </span>
                    </div>
                    <p className="text-slate-500 text-sm flex items-center gap-1.5 mt-0.5">
                        <Clock size={14} />
                        Started: {new Date().toLocaleString()} • Duration: 2.4s
                    </p>
                </div>
            </div>

            <div className="flex items-center gap-1 bg-white p-1 rounded-lg border border-slate-200 shadow-sm">
                <button
                    onClick={() => setActiveTab('trace')}
                    className={cn(
                        "flex items-center gap-2 px-4 py-2 rounded-md transition-all text-sm font-medium",
                        activeTab === 'trace' ? "bg-blue-600 text-white shadow-sm" : "text-slate-500 hover:bg-slate-50"
                    )}
                >
                    <Activity size={16} />
                    Trace Overview
                </button>
                <button
                    onClick={() => setActiveTab('logs')}
                    className={cn(
                        "flex items-center gap-2 px-4 py-2 rounded-md transition-all text-sm font-medium",
                        activeTab === 'logs' ? "bg-blue-600 text-white shadow-sm" : "text-slate-500 hover:bg-slate-50"
                    )}
                >
                    <List size={16} />
                    Raw Logs
                </button>
                <button
                    onClick={() => setActiveTab('artifacts')}
                    className={cn(
                        "flex items-center gap-2 px-4 py-2 rounded-md transition-all text-sm font-medium",
                        activeTab === 'artifacts' ? "bg-blue-600 text-white shadow-sm" : "text-slate-500 hover:bg-slate-50"
                    )}
                >
                    <FileJson size={16} />
                    Artifacts
                </button>
            </div>

            <div className="min-h-[400px]">
                {activeTab === 'trace' && (
                    <div className="space-y-2 animate-in fade-in zoom-in-95 duration-300">
                        {trace?.steps.map((step: any, i: number) => (
                            <TraceStep key={i} step={step} index={i} />
                        ))}
                        {(!trace?.steps || trace.steps.length === 0) && (
                            <div className="bg-white p-12 text-center rounded-xl border-2 border-dashed border-slate-200 text-slate-400">
                                No trace steps recorded for this run.
                            </div>
                        )}
                    </div>
                )}

                {activeTab === 'logs' && (
                    <div className="bg-slate-900 rounded-xl border border-slate-800 shadow-xl overflow-hidden animate-in fade-in duration-300">
                        <div className="bg-slate-800/80 px-4 py-2 flex items-center justify-between border-b border-slate-700">
                            <span className="text-[10px] font-mono text-slate-400">VIRTUALIZED_RENDERER::LOG_STREAM</span>
                            <div className="flex gap-2">
                                <div className="h-1.5 w-1.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]" />
                                <span className="text-[10px] font-mono text-green-500 tracking-tighter">STREAMING_ACTIVE</span>
                            </div>
                        </div>
                        <div className="h-[500px] overflow-auto scrollbar-thin scrollbar-thumb-slate-700 bg-slate-900">
                            {mockLogs.map((line, i) => (
                                <LogRow key={i} line={line} index={i} />
                            ))}
                        </div>
                    </div>
                )}

                {activeTab === 'artifacts' && (
                    <div className="bg-white p-12 rounded-xl border-2 border-dashed border-slate-200 text-center animate-in fade-in duration-300">
                        <div className="mx-auto w-12 h-12 bg-slate-50 rounded-full flex items-center justify-center text-slate-300 mb-4">
                            <FileJson size={24} />
                        </div>
                        <h3 className="text-slate-900 font-semibold mb-1">No Artifacts Found</h3>
                        <p className="text-slate-500 text-sm">This run did not produce any external assets or files.</p>
                    </div>
                )}
            </div>

            <div className="bg-blue-50 border border-blue-100 rounded-xl p-6 flex gap-4">
                <div className="bg-blue-600 p-2 h-fit rounded-lg text-white">
                    <Info size={20} />
                </div>
                <div>
                    <h4 className="text-blue-900 font-bold mb-1 italic tracking-tight">System Notice</h4>
                    <p className="text-blue-700/80 text-sm leading-relaxed">
                        Trace data is retained for 30 days. You can export this run's full telemetry in the settings panel.
                    </p>
                </div>
            </div>
        </div>
    );
};
