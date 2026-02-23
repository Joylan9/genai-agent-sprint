import { QueryCache, MutationCache } from '@tanstack/react-query';
import { agentClient } from '../../features/agent/api/agentClient';

export const queryCache = new QueryCache({
    onError: (error, query) => {
        // Only log errors if the query has no custom error handler
        if (query.meta?.errorMessage) {
            console.error(`[Query Error] ${query.meta.errorMessage}:`, error);
        }

        // @ts-ignore - reaching into agentClient private trackEvent via window global or direct import wrapper
        if (typeof (agentClient as any).trackEvent === 'function') {
            (agentClient as any).trackEvent('query_error', {
                queryKey: query.queryKey,
                error: error.message,
                timestamp: new Date().toISOString()
            });
        }
    },
    onSuccess: (_data, query) => {
        // Capture latency via query metadata if we manually set start times
        const start = query.meta?.startTime as number | undefined;
        const latency = start ? Date.now() - start : undefined;

        if (typeof (agentClient as any).trackEvent === 'function' && latency && latency > 1000) {
            // Only track slow queries to avoid spam
            (agentClient as any).trackEvent('query_slow_success', {
                queryKey: query.queryKey,
                latencyMs: latency,
                timestamp: new Date().toISOString()
            });
        }
    }
});

export const mutationCache = new MutationCache({
    onError: (error, _variables, _context, mutation) => {
        if (typeof (agentClient as any).trackEvent === 'function') {
            (agentClient as any).trackEvent('mutation_error', {
                mutationKey: mutation.options.mutationKey,
                error: error.message,
            });
        }
    }
});
