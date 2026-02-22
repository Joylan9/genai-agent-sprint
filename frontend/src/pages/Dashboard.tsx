import { useHealth, useAgents, useRuns } from '../features/agent/hooks/useAgent';
import { StatCard } from '../features/agent/components/StatCard';
import { Button } from '../shared/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../shared/ui/Table';
import { Badge } from '../shared/ui/Badge';
import { Skeleton } from '../shared/ui/Skeleton';
import { Users, Activity, CheckCircle, Clock, Zap, Plus } from 'lucide-react';

export const Dashboard = () => {
    const { data: health } = useHealth();
    const { data: agents, isLoading: isLoadingAgents } = useAgents();
    const { data: runs, isLoading: isLoadingRuns } = useRuns();

    const stats = [
        { title: 'Total Agents', value: agents?.length.toString() || '0', icon: Users, color: 'bg-amber-500' },
        { title: 'Active Runs', value: runs?.filter((r: any) => r.status === 'running').length.toString() || '0', icon: Activity, color: 'bg-blue-500' },
        { title: 'Successful Runs', value: runs?.filter((r: any) => r.status === 'completed').length.toString() || '0', icon: CheckCircle, color: 'bg-green-500' },
        { title: 'Pending Runs', value: runs?.filter((r: any) => r.status === 'pending').length.toString() || '0', icon: Clock, color: 'bg-purple-500' },
    ];

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900">Dashboard</h1>
                    <p className="text-slate-500 mt-1">Welcome back. Here's what's happening with your agents.</p>
                </div>
                <Button className="space-x-2">
                    <Plus size={18} />
                    <span>New Agent</span>
                </Button>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {isLoadingAgents || isLoadingRuns ? (
                    Array.from({ length: 4 }).map((_, i) => (
                        <div key={i} className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                            <div className="flex items-center justify-between mb-4">
                                <Skeleton className="h-4 w-24" />
                                <Skeleton className="h-8 w-8 rounded-lg" />
                            </div>
                            <Skeleton className="h-8 w-16" />
                        </div>
                    ))
                ) : (
                    stats.map((stat, i) => (
                        <StatCard key={i} {...stat} />
                    ))
                )}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* System Health */}
                <div className="lg:col-span-1 space-y-6">
                    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
                        <div className="flex items-center space-x-2 mb-6">
                            <Zap className="text-blue-600" size={20} />
                            <h2 className="text-lg font-semibold text-slate-900">System Status</h2>
                        </div>
                        <div className="space-y-3">
                            {health ? (
                                <>
                                    <div className="flex items-center justify-between text-sm">
                                        <span className="text-slate-500 font-medium">API Status:</span>
                                        <Badge variant={health.status === 'ok' ? 'green' : 'red'}>
                                            {health.status}
                                        </Badge>
                                    </div>
                                    <div className="flex items-center justify-between text-sm">
                                        <span className="text-slate-500 font-medium">Version:</span>
                                        <span className="text-slate-900 font-bold">{health.version}</span>
                                    </div>
                                    <div className="flex items-center justify-between text-sm">
                                        <span className="text-slate-500 font-medium">Model:</span>
                                        <span className="text-slate-900 font-bold">{health.model || 'N/A'}</span>
                                    </div>
                                </>
                            ) : (
                                <>
                                    <div className="flex items-center justify-between text-sm">
                                        <Skeleton className="h-4 w-24" />
                                        <Skeleton className="h-6 w-16" />
                                    </div>
                                    <div className="flex items-center justify-between text-sm">
                                        <Skeleton className="h-4 w-20" />
                                        <Skeleton className="h-4 w-12" />
                                    </div>
                                    <div className="flex items-center justify-between text-sm">
                                        <Skeleton className="h-4 w-16" />
                                        <Skeleton className="h-4 w-20" />
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                </div>

                {/* Recent Agents */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
                            <h2 className="text-lg font-semibold text-slate-900">Recent Agents</h2>
                            <Button variant="ghost" size="sm">View All</Button>
                        </div>
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Agent Name</TableHead>
                                    <TableHead>Provider</TableHead>
                                    <TableHead>Model</TableHead>
                                    <TableHead>Created</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {isLoadingAgents ? (
                                    Array.from({ length: 3 }).map((_, i) => (
                                        <TableRow key={i}>
                                            <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                                            <TableCell><Skeleton className="h-4 w-12" /></TableCell>
                                            <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                                            <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                                        </TableRow>
                                    ))
                                ) : (
                                    agents?.slice(0, 5).map((agent: any) => (
                                        <TableRow key={agent.id}>
                                            <TableCell className="font-medium text-slate-900">{agent.name}</TableCell>
                                            <TableCell>
                                                <Badge variant="blue">{agent.provider}</Badge>
                                            </TableCell>
                                            <TableCell className="text-slate-500 font-mono text-xs">{agent.model}</TableCell>
                                            <TableCell className="text-slate-500 text-xs">
                                                {new Date(agent.created_at).toLocaleDateString()}
                                            </TableCell>
                                        </TableRow>
                                    ))
                                )}
                            </TableBody>
                        </Table>
                    </div>
                </div>
            </div>
        </div>
    );
};
