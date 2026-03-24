import { useQuery } from '@tanstack/react-query';

import { agentClient } from '../../features/agent/api/agentClient';

export interface SystemStatus {
    frontend: 'ok' | 'degraded' | 'down';
    api: 'ok' | 'degraded' | 'down';
    llm: 'ok' | 'degraded' | 'down';
    vector: 'ok' | 'degraded' | 'down';
    redis: 'ok' | 'degraded' | 'down';
    webSearch: 'ok' | 'degraded' | 'down';
    latency: number;
    checks?: Record<string, any>;
}

export function useHealthMonitor() {
    return useQuery({
        queryKey: ['system-health-monitor'],
        queryFn: async (): Promise<SystemStatus> => {
            const start = Date.now();
            let apiStatus: SystemStatus['api'] = 'down';
            let llmStatus: SystemStatus['llm'] = 'down';
            let vectorStatus: SystemStatus['vector'] = 'degraded';
            let redisStatus: SystemStatus['redis'] = 'degraded';
            let webSearchStatus: SystemStatus['webSearch'] = 'degraded';
            let frontendStatus: SystemStatus['frontend'] = 'ok';
            let checks: Record<string, any> = {};

            try {
                const config = (window as any).__APP_CONFIG__;
                const frontendHealthEndpoint = config?.FRONTEND_HEALTH_ENDPOINT ?? '/health-frontend.json';
                const [health, readiness, frontendHealth] = await Promise.all([
                    agentClient.checkHealth(),
                    agentClient.checkReadiness().catch(() => null),
                    fetch(frontendHealthEndpoint).then((response) => response.json()).catch(() => null),
                ]);

                const normalizedHealth = String(health?.status || '').toLowerCase();
                apiStatus = (normalizedHealth === 'ok' || normalizedHealth === 'healthy')
                    ? 'ok'
                    : 'degraded';
                llmStatus = health?.model ? 'ok' : 'degraded';

                checks = readiness?.checks || {};
                if (checks.mongodb?.status === 'ready') {
                    vectorStatus = 'ok';
                } else if (Object.keys(checks).length > 0) {
                    vectorStatus = 'degraded';
                }
                llmStatus = checks.ollama?.status === 'ready' ? 'ok' : (apiStatus === 'ok' ? 'degraded' : 'down');
                redisStatus = checks.redis?.status === 'ready' ? 'ok' : (checks.redis ? 'degraded' : 'down');
                webSearchStatus = checks.web_search?.status === 'ready' ? 'ok' : checks.web_search?.status === 'disabled' ? 'degraded' : 'down';
                frontendStatus = frontendHealth?.status === 'ok' ? 'ok' : 'degraded';
            } catch {
                apiStatus = 'down';
                llmStatus = 'down';
                vectorStatus = 'down';
                redisStatus = 'down';
                webSearchStatus = 'down';
                frontendStatus = 'down';
            }

            return {
                frontend: frontendStatus,
                api: apiStatus,
                llm: llmStatus,
                vector: vectorStatus,
                redis: redisStatus,
                webSearch: webSearchStatus,
                latency: Date.now() - start,
                checks,
            };
        },
        refetchInterval: 15000,
        staleTime: 10000,
    });
}
