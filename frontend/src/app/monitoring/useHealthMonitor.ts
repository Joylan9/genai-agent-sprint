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
            let apiStatus: 'ok' | 'degraded' | 'down' = 'ok';
            let llmStatus: 'ok' | 'degraded' | 'down' = 'ok';

            try {
                const health = await agentClient.checkHealth();
                // health.status is the overall API status
                if (health.status !== 'ok') apiStatus = 'degraded';
                // health.model is the name of the LLM model, if it's empty or null, we consider LLM degraded
                if (!health.model) llmStatus = 'degraded';
            } catch {
                apiStatus = 'down';
                llmStatus = 'down';
            }

            return {
                frontend: 'ok',
                api: apiStatus,
                llm: llmStatus,
                vector: 'ok', // Mocked as RAG is backend-managed
                latency: Date.now() - start
            };
        },
        refetchInterval: 15000,
        staleTime: 10000
    });
}
