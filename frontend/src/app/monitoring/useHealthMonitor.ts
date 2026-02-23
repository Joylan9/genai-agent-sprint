import { useQuery } from '@tanstack/react-query';

import { agentClient } from '../../features/agent/api/agentClient';

export interface SystemStatus {
    frontend: 'ok' | 'degraded' | 'down';
    api: 'ok' | 'degraded' | 'down';
    llm: 'ok' | 'degraded' | 'down';
    vector: 'ok' | 'degraded' | 'down';
    latency: number;
}

export function useHealthMonitor() {
    return useQuery({
        queryKey: ['system-health-monitor'],
        queryFn: async (): Promise<SystemStatus> => {
            const start = Date.now();
            let apiStatus: SystemStatus['api'] = 'down';
            let llmStatus: SystemStatus['llm'] = 'down';
            let vectorStatus: SystemStatus['vector'] = 'degraded';

            try {
                const [health, readiness] = await Promise.all([
                    agentClient.checkHealth(),
                    agentClient.checkReadiness().catch(() => null),
                ]);

                const normalizedHealth = String(health?.status || '').toLowerCase();
                apiStatus = (normalizedHealth === 'ok' || normalizedHealth === 'healthy')
                    ? 'ok'
                    : 'degraded';
                llmStatus = health?.model ? 'ok' : 'degraded';

                const checks = readiness?.checks || {};
                if (checks.mongodb === 'ready') {
                    vectorStatus = 'ok';
                } else if (Object.keys(checks).length > 0) {
                    vectorStatus = 'degraded';
                }
            } catch {
                apiStatus = 'down';
                llmStatus = 'down';
                vectorStatus = 'down';
            }

            return {
                frontend: 'ok',
                api: apiStatus,
                llm: llmStatus,
                vector: vectorStatus,
                latency: Date.now() - start,
            };
        },
        refetchInterval: 15000,
        staleTime: 10000,
    });
}
