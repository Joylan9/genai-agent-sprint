import { Activity, Filter, Play, Search, Trash2 } from 'lucide-react';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { EmptyState } from '../shared/ui/EmptyState';

import { useDeleteRun, useRuns } from '../features/agent/hooks/useAgent';
import { Button } from '../shared/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../shared/ui/Table';
import { TableSkeleton } from '../shared/ui/TableSkeleton';
import { usePermission } from '../app/auth/usePermission';

const StatusBadge = ({ status }: { status: string }) => {
    const styles = {
        queued: 'bg-amber-100 text-amber-700 border-amber-200',
        running: 'bg-blue-100 text-blue-700 border-blue-200',
        completed: 'bg-green-100 text-green-700 border-green-200',
        failed: 'bg-red-100 text-red-700 border-red-200',
    };

    const normalized = (status || 'queued').toLowerCase() as keyof typeof styles;
    return (
        <span className={`px-2 py-0.5 rounded-full text-xs font-semibold border ${styles[normalized] || styles.queued}`}>
            {normalized.charAt(0).toUpperCase() + normalized.slice(1)}
        </span>
    );
};

const FILTER_ORDER = ['all', 'queued', 'running', 'completed', 'failed'] as const;
type RunFilter = typeof FILTER_ORDER[number];

export const RunsListPage = () => {
    const navigate = useNavigate();
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState<RunFilter>('all');
    const { permissions } = usePermission();
    const deleteRun = useDeleteRun();
    const { data: runs, isLoading } = useRuns(
        {
            q: searchTerm.trim() || undefined,
            status: statusFilter === 'all' ? undefined : statusFilter,
        },
        5000,
    );

    const cycleFilterStatus = () => {
        const currentIndex = FILTER_ORDER.indexOf(statusFilter);
        const next = FILTER_ORDER[(currentIndex + 1) % FILTER_ORDER.length];
        setStatusFilter(next);
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Execution History</h1>
                    <p className="text-slate-500">Monitor and debug your agent runs in real-time.</p>
                </div>
                <Button className="flex items-center gap-2" onClick={() => navigate('/execute')}>
                    <Play size={18} />
                    <span>Execute New</span>
                </Button>
            </div>

            <div className="flex items-center gap-4 bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                    <input
                        id="run-search"
                        name="run-search"
                        type="text"
                        placeholder="Search runs by ID or agent..."
                        aria-label="Search runs"
                        className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                        value={searchTerm}
                        onChange={(event) => setSearchTerm(event.target.value)}
                    />
                </div>
                <Button variant="outline" className="flex items-center gap-2" onClick={cycleFilterStatus}>
                    <Filter size={18} />
                    <span>
                        {statusFilter === 'all'
                            ? 'Filter Status'
                            : `Status: ${statusFilter.charAt(0).toUpperCase() + statusFilter.slice(1)}`}
                    </span>
                </Button>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Run ID</TableHead>
                            <TableHead>Agent</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead>Latency</TableHead>
                            <TableHead>Started At</TableHead>
                            <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {(runs || []).map((run: any) => (
                            <TableRow key={run.id}>
                                <TableCell className="font-mono text-xs text-slate-600">{run.id}</TableCell>
                                <TableCell className="font-medium text-slate-900">
                                    {run.agent_name || run.agent_id || 'Default Agent'}
                                </TableCell>
                                <TableCell>
                                    <div className="flex items-center gap-1.5">
                                        <StatusBadge status={run.status} />
                                        {run.cache_hit && (
                                            <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-700 border border-amber-200" title="Served from cache">
                                                ⚡ Cache
                                            </span>
                                        )}
                                    </div>
                                </TableCell>
                                <TableCell className="text-slate-500 text-xs font-mono">
                                    {run.latency_total != null ? `${run.latency_total.toFixed(2)}s` : '-'}
                                </TableCell>
                                <TableCell className="text-slate-500 text-xs text-nowrap">
                                    {run.started_at ? new Date(run.started_at).toLocaleString() : '-'}
                                </TableCell>
                                <TableCell className="text-right">
                                    <Button variant="ghost" size="sm" className="text-blue-600" onClick={() => navigate(`/runs/${run.id}`)}>
                                        View Trace
                                    </Button>
                                    {permissions.canDeleteAgent && (
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            className="text-red-600"
                                            onClick={() => {
                                                if (window.confirm(`Delete run ${run.id}? This cannot be undone.`)) {
                                                    deleteRun.mutate(run.id);
                                                }
                                            }}
                                        >
                                            <Trash2 size={14} />
                                        </Button>
                                    )}
                                </TableCell>
                            </TableRow>
                        ))}
                        {(runs || []).length === 0 && !isLoading && (
                            <TableRow>
                                <TableCell colSpan={6} className="border-0 p-0">
                                    <EmptyState
                                        icon={Activity}
                                        title={searchTerm ? 'No runs match your search' : 'No execution history yet'}
                                        description={searchTerm ? 'Try a different search term or clear your filters.' : 'Execute an agent from the Playground to see run history and trace data here.'}
                                        actionLabel={searchTerm ? undefined : 'Go to Playground'}
                                        onAction={searchTerm ? undefined : () => navigate('/execute')}
                                        accentColor="green"
                                    />
                                </TableCell>
                            </TableRow>
                        )}
                        {isLoading && (
                            <TableRow>
                                <TableCell colSpan={6} className="p-0 border-0">
                                    <TableSkeleton rows={4} cols={6} hasHeader={false} />
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </div>
        </div>
    );
};
