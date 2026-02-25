import { Filter, Play, Search } from 'lucide-react';
import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { useRuns } from '../features/agent/hooks/useAgent';
import { Button } from '../shared/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../shared/ui/Table';
import { TableSkeleton } from '../shared/ui/TableSkeleton';

const StatusBadge = ({ status }: { status: string }) => {
    const styles = {
        running: 'bg-blue-100 text-blue-700 border-blue-200',
        completed: 'bg-green-100 text-green-700 border-green-200',
        failed: 'bg-red-100 text-red-700 border-red-200',
        pending: 'bg-slate-100 text-slate-700 border-slate-200',
    };

    const normalized = (status || 'pending').toLowerCase() as keyof typeof styles;
    return (
        <span className={`px-2 py-0.5 rounded-full text-xs font-semibold border ${styles[normalized] || styles.pending}`}>
            {normalized.charAt(0).toUpperCase() + normalized.slice(1)}
        </span>
    );
};

const FILTER_ORDER = ['all', 'running', 'completed', 'failed', 'pending'] as const;
type RunFilter = typeof FILTER_ORDER[number];

export const RunsListPage = () => {
    const navigate = useNavigate();
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState<RunFilter>('all');
    const { data: runs, isLoading } = useRuns();

    const filteredRuns = useMemo(() => {
        const source = Array.isArray(runs) ? runs : [];
        return source.filter((run: any) => {
            const runId = String(run.id || '').toLowerCase();
            const agentId = String(run.agent_id || '').toLowerCase();
            const status = String(run.status || '').toLowerCase();

            const matchesSearch = !searchTerm.trim()
                || runId.includes(searchTerm.toLowerCase())
                || agentId.includes(searchTerm.toLowerCase());

            const matchesStatus = statusFilter === 'all' || status === statusFilter;
            return matchesSearch && matchesStatus;
        });
    }, [runs, searchTerm, statusFilter]);

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
                            <TableHead>Started At</TableHead>
                            <TableHead className="text-right">Result</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {filteredRuns.map((run: any) => (
                            <TableRow key={run.id}>
                                <TableCell className="font-mono text-xs text-slate-600">{run.id}</TableCell>
                                <TableCell className="font-medium text-slate-900">Agent {run.agent_id}</TableCell>
                                <TableCell>
                                    <StatusBadge status={run.status} />
                                </TableCell>
                                <TableCell className="text-slate-500 text-xs text-nowrap">
                                    {run.started_at ? new Date(run.started_at).toLocaleString() : '-'}
                                </TableCell>
                                <TableCell className="text-right">
                                    <Button variant="ghost" size="sm" className="text-blue-600" onClick={() => navigate(`/runs/${run.id}`)}>
                                        View Trace
                                    </Button>
                                </TableCell>
                            </TableRow>
                        ))}
                        {filteredRuns.length === 0 && !isLoading && (
                            <TableRow>
                                <TableCell colSpan={5} className="h-32 text-center text-slate-400">
                                    No runs found in history.
                                </TableCell>
                            </TableRow>
                        )}
                        {isLoading && (
                            <TableRow>
                                <TableCell colSpan={5} className="p-0 border-0">
                                    <TableSkeleton rows={4} cols={5} hasHeader={false} />
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </div>
        </div>
    );
};
