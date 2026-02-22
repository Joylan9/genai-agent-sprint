import { Search, Filter, Play } from 'lucide-react';
import { useRuns } from '../features/agent/hooks/useAgent';
import { useNavigate } from 'react-router-dom';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../shared/ui/Table';
import { Button } from '../shared/ui/Button';

const StatusBadge = ({ status }: { status: string }) => {
    const styles = {
        running: 'bg-blue-100 text-blue-700 border-blue-200',
        completed: 'bg-green-100 text-green-700 border-green-200',
        failed: 'bg-red-100 text-red-700 border-red-200',
        pending: 'bg-slate-100 text-slate-700 border-slate-200',
    };

    return (
        <span className={`px-2 py-0.5 rounded-full text-xs font-semibold border ${styles[status as keyof typeof styles] || styles.pending}`}>
            {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
    );
};

export const RunsListPage = () => {
    const { data: runs, isLoading } = useRuns();
    const navigate = useNavigate();

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Execution History</h1>
                    <p className="text-slate-500">Monitor and debug your agent runs in real-time.</p>
                </div>
                <Button className="flex items-center gap-2">
                    <Play size={18} />
                    <span>Execute New</span>
                </Button>
            </div>

            <div className="flex items-center gap-4 bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                    <input
                        type="text"
                        placeholder="Search runs by ID or agent..."
                        className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                    />
                </div>
                <Button variant="outline" className="flex items-center gap-2">
                    <Filter size={18} />
                    <span>Filter Status</span>
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
                        {runs?.map((run: any) => (
                            <TableRow key={run.id}>
                                <TableCell className="font-mono text-xs text-slate-600">{run.id}</TableCell>
                                <TableCell className="font-medium text-slate-900">Agent {run.agent_id}</TableCell>
                                <TableCell>
                                    <StatusBadge status={run.status} />
                                </TableCell>
                                <TableCell className="text-slate-500 text-xs text-nowrap">
                                    {new Date(run.started_at).toLocaleString()}
                                </TableCell>
                                <TableCell className="text-right">
                                    <Button variant="ghost" size="sm" className="text-blue-600" onClick={() => navigate(`/runs/${run.id}`)}>
                                        View Trace
                                    </Button>
                                </TableCell>
                            </TableRow>
                        ))}
                        {(!runs || runs.length === 0) && !isLoading && (
                            <TableRow>
                                <TableCell colSpan={5} className="h-32 text-center text-slate-400">
                                    No runs found in history.
                                </TableCell>
                            </TableRow>
                        )}
                        {isLoading && (
                            <TableRow>
                                <TableCell colSpan={5} className="h-32 text-center text-slate-400">
                                    Loading runs...
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </div>
        </div>
    );
};
