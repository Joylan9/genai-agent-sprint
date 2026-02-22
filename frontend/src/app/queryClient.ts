import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: 2,
            refetchOnWindowFocus: false,
            staleTime: 30_000,
            gcTime: 5 * 60_000, // Replacing deprecated cacheTime with gcTime for React Query v5
        },
        mutations: {
            retry: 1,
        },
    },
});
