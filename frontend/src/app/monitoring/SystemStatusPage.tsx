import { useHealthMonitor } from './useHealthMonitor';
import { AlertCircle, CheckCircle2, Clock, ServerCrash, RefreshCw } from 'lucide-react';
import { PageLoader } from '../../shared/ui/PageLoader';

type StatusLevel = 'ok' | 'degraded' | 'down';

export function SystemStatusPage() {
    const { data: status, isLoading, isError, refetch, isRefetching } = useHealthMonitor();

    if (isLoading) {
        return <PageLoader />;
    }

    if (isError || !status) {
        return (
            <div className="p-8 max-w-4xl mx-auto space-y-6">
                <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-md flex items-start space-x-3">
                    <ServerCrash className="text-red-500 mt-0.5" />
                    <div>
                        <h3 className="text-red-800 font-medium">Monitoring Unavailable</h3>
                        <p className="text-red-600 text-sm mt-1">
                            Unable to retrieve system health metrics. The control plane might be completely offline.
                        </p>
                        <button
                            onClick={() => refetch()}
                            className="mt-3 text-sm font-medium text-red-700 hover:text-red-900 flex items-center"
                        >
                            <RefreshCw className="w-4 h-4 mr-1" /> Retry Connection
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    const cards = [
        { name: 'Gateway (Frontend)', key: 'frontend', val: status.frontend },
        { name: 'API Services (FastAPI)', key: 'api', val: status.api },
        { name: 'Inference Engine (Ollama)', key: 'llm', val: status.llm },
        { name: 'Vector DB (MongoDB)', key: 'vector', val: status.vector },
        { name: 'Queue/Broker (Redis/Celery)', key: 'redis', val: status.redis },
        { name: 'Web Search Feature', key: 'webSearch', val: status.webSearch },
    ];

    const allOk = cards.every(c => c.val === 'ok');

    return (
        <div className="p-8 max-w-4xl mx-auto space-y-8 animate-in fade-in duration-500">
            <div>
                <h1 className="text-2xl font-bold text-gray-900 tracking-tight">System Status</h1>
                <p className="text-gray-500 mt-1">Real-time dependency health and latencies</p>
            </div>

            {/* Global Status Banner */}
            <div className={`p-4 rounded-lg flex items-center justify-between border ${allOk ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'}`}>
                <div className="flex items-center space-x-3">
                    {allOk ? (
                        <CheckCircle2 className="w-6 h-6 text-green-600" />
                    ) : (
                        <AlertCircle className="w-6 h-6 text-yellow-600" />
                    )}
                    <div>
                        <h2 className={`font-semibold ${allOk ? 'text-green-800' : 'text-yellow-800'}`}>
                            {allOk ? 'All Systems Operational' : 'Degraded Performance Detected'}
                        </h2>
                        <span className="text-sm flex items-center text-gray-600 mt-0.5">
                            <Clock className="w-3.5 h-3.5 mr-1" />
                    Global Latency: {status.latency}ms
                </span>
            </div>
        </div>
                <button
                    onClick={() => refetch()}
                    disabled={isRefetching}
                    className="p-2 text-gray-500 hover:bg-gray-100 rounded-md transition-colors disabled:opacity-50 inline-flex items-center"
                    title="Force refresh"
                >
                    <RefreshCw className={`w-5 h-5 ${isRefetching ? 'animate-spin' : ''}`} />
                </button>
            </div>

            {/* Individual Services Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {cards.map((service) => (
                    <StatusCard
                        key={service.key}
                        name={service.name}
                        status={service.val as StatusLevel}
                        remediation={getRemediation(service.key, service.val)}
                    />
                ))}
            </div>
        </div>
    );
}

function StatusCard({ name, status, remediation }: { name: string, status: StatusLevel, remediation: string | null }) {
    const config = {
        ok: { icon: CheckCircle2, color: 'text-green-500', bg: 'bg-green-50', border: 'border-green-200', text: 'Operational' },
        degraded: { icon: AlertCircle, color: 'text-yellow-500', bg: 'bg-yellow-50', border: 'border-yellow-200', text: 'Degraded' },
        down: { icon: ServerCrash, color: 'text-red-500', bg: 'bg-red-50', border: 'border-red-200', text: 'Outage' }
    }[status];

    const Icon = config.icon;

    return (
        <div className={`p-5 rounded-lg border ${config.border} bg-white shadow-sm flex flex-col justify-between`}>
            <div className="flex justify-between items-start mb-4">
                <h3 className="font-semibold text-gray-800">{name}</h3>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.bg} ${config.color}`}>
                    <Icon className="w-3 h-3 mr-1" />
                    {config.text}
                </span>
            </div>

            {status !== 'ok' && remediation && (
                <div className="mt-2 text-sm text-gray-600 border-t pt-3">
                    <span className="font-medium text-gray-700">Remediation: </span>
                    {remediation}
                </div>
            )}
        </div>
    );
}

function getRemediation(key: string, status: string): string | null {
    if (status === 'ok') return null;
    switch (key) {
        case 'frontend': return 'Verify `/health-frontend.json` is being served by the frontend host or nginx layer.';
        case 'api': return 'Check the API logs and confirm the canonical backend is running from `app.api_app:app` on port 8000.';
        case 'llm': return 'Ollama is unresponsive or missing the required model payload. Run `docker logs genai-api` for connection traces.';
        case 'vector': return 'MongoDB connection is failing. Verify `MONGODB_URI` and ensure `genai-mongo` is healthy.';
        case 'redis': return 'Redis or Celery is unavailable. Verify `CELERY_BROKER_URL` and ensure the queue worker is running.';
        case 'webSearch': return 'Web search is optional. Configure `SERPAPI_KEY` if you want online search enabled.';
        default: return 'Contact system administrator.';
    }
}
