import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { agentClient } from '../api/agentClient';
import type { AgentRequest } from '../types';

export const useHealth = () => {
    return useQuery({
        queryKey: ['health'],
        queryFn: () => agentClient.checkHealth(),
        refetchInterval: 10000,
    });
};

export const useReadiness = () => {
    return useQuery({
        queryKey: ['readiness'],
        queryFn: () => agentClient.checkReadiness(),
        refetchInterval: 30000,
    });
};

export const useAgents = () => {
    return useQuery({
        queryKey: ['agents'],
        queryFn: () => agentClient.listAgents(),
    });
};

export const useCreateAgent = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (newAgent: any) => agentClient.instance.post('/api/agents', newAgent),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['agents'] });
        },
    });
};

export const useRunAgent = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (request: AgentRequest) => agentClient.runAgent(request),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['runs'] });
        },
    });
};

export const useRuns = () => {
    return useQuery({
        queryKey: ['runs'],
        queryFn: () => agentClient.listRuns(),
    });
};

export const useTrace = (requestId: string) => {
    return useQuery({
        queryKey: ['trace', requestId],
        queryFn: () => agentClient.getTrace(requestId),
        enabled: !!requestId,
    });
};
