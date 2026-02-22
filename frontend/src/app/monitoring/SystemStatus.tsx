import React from 'react';
import { useHealthMonitor, type SystemStatus } from './useHealthMonitor';
import { StatCard } from '../../features/agent/components/StatCard';
import { Activity, Server, Cpu, Database, Globe } from 'lucide-react';
import { Badge } from '../../shared/ui/Badge';
import { cn } from '../../shared/lib/utils';

export const SystemStatusPage: React.FC = () => {
    const { data: status, isLoading, isError } = useHealthMonitor();

    if (isLoading) return <div className="p-8 text-center">Loading production health metrics...</div>;
    if (isError || !status) return <div className="p-8 text-center text-red-500">Failed to fetch health data.</div>;

    const getStatusBadge = (state: SystemStatus['frontend']) => {
        switch (state) {
            case 'ok': return <Badge variant="green">Operational</Badge>;
            case 'degraded': return <Badge variant="yellow">Degraded</Badge>;
            case 'down': return <Badge variant="red" className="animate-pulse">Outage</Badge>;
        }
    };

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div>
                <h1 className="text-3xl font-bold tracking-tight">System Reliability</h1>
                <p className="text-slate-500 mt-2">Real-time health monitoring of the GenAI Agent stack.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <StatCard
                    title="Avg Latency"
                    value={`${status.latency} ms`}
                    icon={Activity}
                    color="bg-blue-600"
                />
                <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between h-32">
                    <div className="flex justify-between items-start">
                        <span className="text-sm font-medium text-slate-500">API Gateway</span>
                        <Server size={20} className="text-blue-500" />
                    </div>
                    {getStatusBadge(status.api)}
                </div>
                <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between h-32">
                    <div className="flex justify-between items-start">
                        <span className="text-sm font-medium text-slate-500">LLM Inference</span>
                        <Cpu size={20} className="text-purple-500" />
                    </div>
                    {getStatusBadge(status.llm)}
                </div>
                <div className="bg-white dark:bg-slate-900 p-6 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm flex flex-col justify-between h-32">
                    <div className="flex justify-between items-start">
                        <span className="text-sm font-medium text-slate-500">Vector Storage</span>
                        <Database size={20} className="text-amber-500" />
                    </div>
                    {getStatusBadge(status.vector)}
                </div>
            </div>

            <div className="bg-slate-50 dark:bg-slate-950/50 rounded-2xl border border-slate-200 dark:border-slate-800 p-8">
                <h2 className="text-lg font-semibold mb-6 flex items-center gap-2">
                    <Globe size={20} className="text-slate-400" />
                    Global Topology Map
                </h2>

                <div className="relative h-64 border border-dashed border-slate-300 dark:border-slate-700 rounded-xl flex items-center justify-center">
                    <div className="flex flex-col items-center gap-4">
                        <div className={cn("px-4 py-2 rounded-lg border-2 font-mono text-xs",
                            status.frontend === 'ok' ? "border-green-500 bg-green-50 text-green-700" : "border-red-500 bg-red-50 text-red-700")}>
                            Traffic Edge (CDN)
                        </div>
                        <div className="h-4 w-0.5 bg-slate-300 dark:bg-slate-700" />
                        <div className={cn("px-6 py-3 rounded-lg border-2 font-mono text-sm",
                            status.api === 'ok' ? "border-blue-500 bg-blue-50 text-blue-700" : "border-red-500 bg-red-50 text-red-700")}>
                            FastAPI Cluster
                        </div>
                        <div className="flex gap-8 items-center mt-4">
                            <div className={cn("px-4 py-2 rounded-lg border-2 font-mono text-xs",
                                status.llm === 'ok' ? "border-purple-500 bg-purple-50 text-purple-700" : "border-red-500 bg-red-50 text-red-700")}>
                                Ollama Engine
                            </div>
                            <div className="px-4 py-2 rounded-lg border-2 border-amber-500 bg-amber-50 text-amber-700 font-mono text-xs">
                                Qdrant Search
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};
