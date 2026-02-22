import { describe, it, expect, vi } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useAgents } from './useAgent';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { agentClient } from '../api/agentClient';

// Mock agentClient
vi.mock('../api/agentClient', () => ({
    agentClient: {
        listAgents: vi.fn()
    }
}));

const queryClient = new QueryClient({
    defaultOptions: {
        queries: { retry: false }
    }
});

const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
);

describe('useAgent hooks', () => {
    it('useAgents fetches data correctly', async () => {
        const mockData = [{ id: '1', name: 'Agent 1', version: '1.0' }];
        (agentClient.listAgents as any).mockResolvedValue(mockData);

        const { result } = renderHook(() => useAgents(), { wrapper });

        await waitFor(() => expect(result.current.isSuccess).toBe(true));
        expect(result.current.data).toEqual(mockData);
    });
});
