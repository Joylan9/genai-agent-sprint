import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { agentClient } from '../features/agent/api/agentClient';
import { Button } from '../shared/ui/Button';
import { Badge } from '../shared/ui/Badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../shared/ui/Table';
import {
    Bot, ArrowLeft, Clock, CheckCircle2, XCircle,
    Play, Trash2, Calendar, Tag, Activity, TrendingUp,
    Zap, BarChart3,
} from 'lucide-react';

interface AgentDetail {
    id: string;
    name: string;
    description?: string;
    version?: string;
    status?: string;
    created_at?: string;
    tools?: string[];
}

interface Run {
    id: string;
    status: string;
    final_answer?: string;
    created_at?: string;
    latency_total?: number;
    cache_hit?: boolean;
}

export const AgentDetailPage = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [agent, setAgent] = useState<AgentDetail | null>(null);
    const [runs, setRuns] = useState<Run[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        if (!id) return;
        loadData();
    }, [id]);

    const loadData = async () => {
        setLoading(true);
        try {
            const agentData = await agentClient.getAgent(id!);
            setAgent(agentData);

            // Load runs for this agent
            const allRuns = await agentClient.listRuns();
            const agentRuns = (allRuns || [])
                .filter((r: any) => r.agent_id === id || r.agent_name === agentData?.name)
                .slice(0, 20);
            setRuns(agentRuns);
        } catch (err: any) {
            setError(err?.message || 'Failed to load agent');
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async () => {
        if (!id || !confirm('Delete this agent? This action cannot be undone.')) return;
        try {
            await agentClient.deleteAgent(id);
            navigate('/agents');
        } catch {
            // ignore
        }
    };

    // Stats
    const totalRuns = runs.length;
    const successfulRuns = runs.filter(r => r.status === 'completed').length;
    const failedRuns = runs.filter(r => r.status === 'failed').length;
    const avgLatency = runs.length > 0
        ? runs.reduce((sum, r) => sum + (r.latency_total || 0), 0) / runs.length
        : 0;
    const successRate = totalRuns > 0 ? (successfulRuns / totalRuns) * 100 : 0;

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

    if (error || !agent) {
        return (
            <div className="text-center py-16">
                <Bot size={48} className="text-slate-300 mx-auto mb-4" />
                <h2 className="text-lg font-semibold text-slate-600 mb-2">Agent Not Found</h2>
                <p className="text-sm text-slate-400 mb-4">{error || 'No agent found with this ID.'}</p>
                <Link to="/agents" className="text-blue-600 text-sm hover:underline">← Back to Agents</Link>
            </div>
        );
    }

    return (
        <div className="space-y-6 max-w-6xl mx-auto">
            {/* Breadcrumb + Actions */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <Link to="/agents" className="text-slate-400 hover:text-slate-600 transition-colors">
                        <ArrowLeft size={20} />
                    </Link>
                    <div>
                        <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
                            <Bot className="text-blue-600" size={24} />
                            {agent.name}
                        </h1>
                        <p className="text-sm text-slate-500 mt-0.5">
                            {agent.description || 'No description'}
                        </p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => navigate(`/execute?agent=${agent.name}`)}
                        className="flex items-center gap-1.5"
                    >
                        <Play size={14} /> Run Agent
                    </Button>
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={handleDelete}
                        className="text-red-500 hover:bg-red-50 flex items-center gap-1.5"
                    >
                        <Trash2 size={14} /> Delete
                    </Button>
                </div>
            </div>

            {/* Agent Info Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
                    <div className="flex items-center gap-2 text-xs text-slate-500 mb-2">
                        <Tag size={12} /> Version
                    </div>
                    <p className="text-lg font-bold text-slate-800">{agent.version || 'v1.0.0'}</p>
                </div>
                <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
                    <div className="flex items-center gap-2 text-xs text-slate-500 mb-2">
                        <Activity size={12} /> Status
                    </div>
                    <Badge variant={agent.status === 'active' ? 'green' : 'slate'} className="text-sm">
                        {agent.status || 'ACTIVE'}
                    </Badge>
                </div>
                <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
                    <div className="flex items-center gap-2 text-xs text-slate-500 mb-2">
                        <Calendar size={12} /> Created
                    </div>
                    <p className="text-sm font-medium text-slate-700">
                        {agent.created_at ? new Date(agent.created_at).toLocaleDateString() : '-'}
                    </p>
                </div>
                <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
                    <div className="flex items-center gap-2 text-xs text-slate-500 mb-2">
                        <Zap size={12} /> Tools
                    </div>
                    <p className="text-lg font-bold text-slate-800">
                        {agent.tools?.length || 0}
                    </p>
                </div>
            </div>

            {/* Performance Stats */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-100 rounded-xl p-4">
                    <p className="text-xs text-blue-600 font-semibold uppercase tracking-wider mb-1">Total Runs</p>
                    <p className="text-3xl font-bold text-blue-700">{totalRuns}</p>
                </div>
                <div className="bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-100 rounded-xl p-4">
                    <p className="text-xs text-emerald-600 font-semibold uppercase tracking-wider mb-1">Success Rate</p>
                    <p className="text-3xl font-bold text-emerald-700">{successRate.toFixed(0)}%</p>
                </div>
                <div className="bg-gradient-to-br from-red-50 to-orange-50 border border-red-100 rounded-xl p-4">
                    <p className="text-xs text-red-600 font-semibold uppercase tracking-wider mb-1">Failed</p>
                    <p className="text-3xl font-bold text-red-700">{failedRuns}</p>
                </div>
                <div className="bg-gradient-to-br from-purple-50 to-violet-50 border border-purple-100 rounded-xl p-4">
                    <p className="text-xs text-purple-600 font-semibold uppercase tracking-wider mb-1">Avg Latency</p>
                    <p className="text-3xl font-bold text-purple-700 flex items-center gap-1">
                        <Clock size={18} /> {avgLatency.toFixed(1)}s
                    </p>
                </div>
            </div>

            {/* Recent Runs */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
                    <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                        <TrendingUp size={16} className="text-blue-500" /> Recent Runs
                    </h3>
                    <Link to="/runs" className="text-sm text-blue-600 hover:underline">View All</Link>
                </div>
                {runs.length === 0 ? (
                    <div className="p-8 text-center text-slate-400">
                        <BarChart3 size={32} className="mx-auto mb-2 text-slate-300" />
                        <p className="text-sm">No runs yet. Execute this agent from the Playground.</p>
                    </div>
                ) : (
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Run ID</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead>Latency</TableHead>
                                <TableHead>Cache</TableHead>
                                <TableHead>Date</TableHead>
                                <TableHead className="text-right">Details</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {runs.map((run) => (
                                <TableRow key={run.id}>
                                    <TableCell className="font-mono text-xs">{run.id?.slice(0, 8)}...</TableCell>
                                    <TableCell>
                                        {run.status === 'completed' ? (
                                            <Badge variant="green" className="flex items-center gap-1 w-fit">
                                                <CheckCircle2 size={12} /> Completed
                                            </Badge>
                                        ) : run.status === 'failed' ? (
                                            <Badge variant="red" className="flex items-center gap-1 w-fit">
                                                <XCircle size={12} /> Failed
                                            </Badge>
                                        ) : (
                                            <Badge variant="slate">{run.status}</Badge>
                                        )}
                                    </TableCell>
                                    <TableCell className="font-mono text-xs">
                                        {run.latency_total ? `${run.latency_total.toFixed(1)}s` : '-'}
                                    </TableCell>
                                    <TableCell>
                                        {run.cache_hit && <span className="text-amber-500">⚡</span>}
                                    </TableCell>
                                    <TableCell className="text-xs text-slate-500">
                                        {run.created_at ? new Date(run.created_at).toLocaleString() : '-'}
                                    </TableCell>
                                    <TableCell className="text-right">
                                        <Link to={`/runs/${run.id}`} className="text-blue-600 text-sm hover:underline">
                                            View →
                                        </Link>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                )}
            </div>
        </div>
    );
};
