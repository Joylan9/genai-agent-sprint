import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { agentClient } from '../../features/agent/api/agentClient';
import {
    X, Zap, Clock, CheckCircle2, XCircle,
    Loader2, ChevronRight, Activity,
} from 'lucide-react';
import { cn } from '../../shared/lib/utils';

interface RunSummary {
    id: string;
    status: string;
    goal?: string;
    agent_name?: string;
    started_at?: string;
    latency_total?: number;
}

const STATUS_MAP: Record<string, { color: string; icon: typeof Zap; label: string }> = {
    running: { color: 'text-blue-500', icon: Loader2, label: 'Running' },
    queued: { color: 'text-amber-500', icon: Clock, label: 'Queued' },
    completed: { color: 'text-emerald-500', icon: CheckCircle2, label: 'Completed' },
    failed: { color: 'text-red-500', icon: XCircle, label: 'Failed' },
};

interface ActivityDrawerProps {
    isOpen: boolean;
    onClose: () => void;
}

export const ActivityDrawer = ({ isOpen, onClose }: ActivityDrawerProps) => {
    const [runs, setRuns] = useState<RunSummary[]>([]);
    const [loading, setLoading] = useState(false);

    const fetchRuns = useCallback(async () => {
        setLoading(true);
        try {
            const data = await agentClient.listRuns();
            setRuns((data || []).slice(0, 15));
        } catch {
            // silently fail
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        if (isOpen) fetchRuns();
    }, [isOpen, fetchRuns]);

    // Auto-refresh every 5s when open
    useEffect(() => {
        if (!isOpen) return;
        const interval = setInterval(fetchRuns, 5000);
        return () => clearInterval(interval);
    }, [isOpen, fetchRuns]);

    const activeRuns = runs.filter(r => r.status === 'running');
    const queuedRuns = runs.filter(r => r.status === 'queued');
    const recentRuns = runs.filter(r => r.status !== 'running' && r.status !== 'queued').slice(0, 8);

    return (
        <>
            {/* Backdrop */}
            {isOpen && (
                <div
                    className="fixed inset-0 bg-black/30 backdrop-blur-sm z-40 transition-opacity"
                    onClick={onClose}
                />
            )}

            {/* Drawer */}
            <div className={cn(
                'fixed right-0 top-0 h-full w-[400px] bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 shadow-2xl z-50 transition-transform duration-300',
                isOpen ? 'translate-x-0' : 'translate-x-full'
            )}>
                {/* Header */}
                <div className="flex items-center justify-between px-5 h-16 border-b border-slate-200 dark:border-slate-800">
                    <div className="flex items-center gap-2">
                        <Activity size={18} className="text-blue-500" />
                        <h2 className="font-semibold text-slate-800 dark:text-slate-100">Platform Activity</h2>
                    </div>
                    <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                        <X size={18} className="text-slate-400" />
                    </button>
                </div>

                {/* Stats Bar */}
                <div className="grid grid-cols-3 gap-px bg-slate-200 dark:bg-slate-800 border-b border-slate-200 dark:border-slate-800">
                    <div className="bg-white dark:bg-slate-900 p-3 text-center">
                        <p className="text-xl font-bold text-blue-600">{activeRuns.length}</p>
                        <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Active</p>
                    </div>
                    <div className="bg-white dark:bg-slate-900 p-3 text-center">
                        <p className="text-xl font-bold text-amber-500">{queuedRuns.length}</p>
                        <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Queued</p>
                    </div>
                    <div className="bg-white dark:bg-slate-900 p-3 text-center">
                        <p className="text-xl font-bold text-emerald-500">{recentRuns.filter(r => r.status === 'completed').length}</p>
                        <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Completed</p>
                    </div>
                </div>

                {/* Run List */}
                <div className="flex-1 overflow-y-auto p-4 space-y-2" style={{ maxHeight: 'calc(100vh - 180px)' }}>
                    {loading && runs.length === 0 && (
                        <div className="flex items-center justify-center py-12">
                            <Loader2 size={24} className="text-blue-500 animate-spin" />
                        </div>
                    )}

                    {/* Active Runs */}
                    {activeRuns.length > 0 && (
                        <>
                            <p className="text-[10px] font-bold text-blue-500 uppercase tracking-widest px-1 mb-1">⚡ Active</p>
                            {activeRuns.map(run => (
                                <RunCard key={run.id} run={run} />
                            ))}
                        </>
                    )}

                    {/* Queued Runs */}
                    {queuedRuns.length > 0 && (
                        <>
                            <p className="text-[10px] font-bold text-amber-500 uppercase tracking-widest px-1 mt-3 mb-1">⏳ Queued</p>
                            {queuedRuns.map(run => (
                                <RunCard key={run.id} run={run} />
                            ))}
                        </>
                    )}

                    {/* Recent */}
                    {recentRuns.length > 0 && (
                        <>
                            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest px-1 mt-3 mb-1">Recent</p>
                            {recentRuns.map(run => (
                                <RunCard key={run.id} run={run} />
                            ))}
                        </>
                    )}

                    {runs.length === 0 && !loading && (
                        <div className="text-center py-12">
                            <Activity size={32} className="text-slate-300 dark:text-slate-700 mx-auto mb-3" />
                            <p className="text-sm font-medium text-slate-500">No runs yet</p>
                            <p className="text-xs text-slate-400 mt-1">Execute an agent from the Playground</p>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="absolute bottom-0 left-0 right-0 border-t border-slate-200 dark:border-slate-800 px-5 py-3 bg-white dark:bg-slate-900">
                    <Link to="/runs" onClick={onClose} className="text-sm text-blue-600 hover:text-blue-500 font-medium flex items-center gap-1">
                        View All Runs <ChevronRight size={14} />
                    </Link>
                </div>
            </div>
        </>
    );
};

// ── Individual Run Card ──
const RunCard = ({ run }: { run: RunSummary }) => {
    const status = STATUS_MAP[run.status] || STATUS_MAP.completed;
    const StatusIcon = status.icon;

    return (
        <Link
            to={`/runs/${run.id}`}
            className="block p-3 rounded-xl border border-slate-100 dark:border-slate-800 hover:border-blue-200 dark:hover:border-blue-900 hover:bg-blue-50/30 dark:hover:bg-blue-950/20 transition-all group"
        >
            <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                    <StatusIcon
                        size={14}
                        className={cn(status.color, run.status === 'running' && 'animate-spin')}
                    />
                    <span className="text-xs font-semibold text-slate-600 dark:text-slate-300">{status.label}</span>
                </div>
                <span className="font-mono text-[10px] text-slate-400">{run.id?.slice(0, 8)}</span>
            </div>
            <p className="text-sm text-slate-800 dark:text-slate-200 truncate">
                {run.goal || 'Unnamed run'}
            </p>
            <div className="flex items-center gap-3 mt-1.5 text-[11px] text-slate-400">
                {run.agent_name && <span>🤖 {run.agent_name}</span>}
                {run.latency_total && <span>⏱ {run.latency_total.toFixed(1)}s</span>}
                {run.started_at && <span>{new Date(run.started_at).toLocaleTimeString()}</span>}
            </div>
        </Link>
    );
};
