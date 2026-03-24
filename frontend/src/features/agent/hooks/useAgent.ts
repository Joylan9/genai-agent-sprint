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

export const useAgentVersions = (agentId: string) => {
    return useQuery({
        queryKey: ['agents', agentId, 'versions'],
        queryFn: () => agentClient.getAgentVersions(agentId),
        enabled: !!agentId,
    });
};

export const useCreateAgent = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (newAgent: any) => agentClient.createAgent(newAgent),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['agents'] });
        },
    });
};

export const useUpdateAgent = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ id, updates }: { id: string, updates: any }) => agentClient.updateAgent(id, updates),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['agents'] });
        },
    });
};

export const useCreateAgentVersion = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ agentId, version, metadata }: { agentId: string; version: string; metadata?: Record<string, any> }) =>
            agentClient.createAgentVersion(agentId, { version, metadata }),
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: ['agents'] });
            queryClient.invalidateQueries({ queryKey: ['agents', variables.agentId, 'versions'] });
        },
    });
};

export const usePromoteAgentVersion = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: ({ agentId, version }: { agentId: string; version: string }) =>
            agentClient.promoteAgentVersion(agentId, version),
        onSuccess: (_, variables) => {
            queryClient.invalidateQueries({ queryKey: ['agents'] });
            queryClient.invalidateQueries({ queryKey: ['agents', variables.agentId, 'versions'] });
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

export const useRuns = (filters?: { q?: string; status?: string }, refetchInterval?: number | false) => {
    return useQuery({
        queryKey: ['runs', filters],
        queryFn: () => agentClient.listRuns(filters),
        refetchInterval,
    });
};

export const useTrace = (requestId: string) => {
    return useQuery({
        queryKey: ['trace', requestId],
        queryFn: () => agentClient.getTrace(requestId),
        enabled: !!requestId,
    });
};

export const useDeleteAgent = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (agentId: string) => agentClient.deleteAgent(agentId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['agents'] });
        },
    });
};

export const useDeleteRun = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (requestId: string) => agentClient.deleteRun(requestId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['runs'] });
        },
    });
};
