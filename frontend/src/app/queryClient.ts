import { QueryClient } from "@tanstack/react-query";
import { queryCache, mutationCache } from './telemetry/telemetryMiddleware';

export const queryClient = new QueryClient({
    queryCache,
    mutationCache,
    defaultOptions: {
        queries: {
            retry: 2,
            refetchOnWindowFocus: false,
            staleTime: 30_000,
            gcTime: 5 * 60_000,
        },
        mutations: {
            retry: 1,
        },
    },
});
