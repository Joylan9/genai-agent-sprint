import { useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Bot, Filter, Plus, RefreshCw, Search } from 'lucide-react';
import { EmptyState } from '../../../shared/ui/EmptyState';
import { TableSkeleton } from '../../../shared/ui/TableSkeleton';
import { useAgents, useCreateAgent, useUpdateAgent, useDeleteAgent } from '../hooks/useAgent';
import { Button } from '../../../shared/ui/Button';
import { Input } from '../../../shared/ui/Input';
import { Modal } from '../../../shared/ui/Modal';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../../shared/ui/Table';
import { useNavigate } from 'react-router-dom';

const agentSchema = z.object({
    name: z.string().min(3, 'Name must be at least 3 characters'),
    version: z.string().optional(),
    description: z.string().optional(),
});

type AgentFormValues = z.infer<typeof agentSchema>;

type AgentRecord = {
    id: string;
    name: string;
    version?: string;
    description?: string;
    status?: string;
    created_at?: string;
};

export const AgentListPage = () => {
    const [searchParams, setSearchParams] = useSearchParams();
    const [statusFilter, setStatusFilter] = useState<'all' | 'active'>('all');
    const [isModalManuallyOpen, setIsModalManuallyOpen] = useState(false);

    const query = searchParams.get('q') || '';
    const isModalOpen = isModalManuallyOpen || searchParams.get('create') === '1';

    const { data: agents, isLoading, refetch } = useAgents();
    const createAgent = useCreateAgent();
    const updateAgent = useUpdateAgent();
    const deleteAgentMutation = useDeleteAgent();
    const navigate = useNavigate();
    const [editingAgent, setEditingAgent] = useState<AgentRecord | null>(null);

    const {
        register,
        handleSubmit,
        reset,
        formState: { errors },
    } = useForm<AgentFormValues>({
        resolver: zodResolver(agentSchema),
        defaultValues: { version: '1.0.0' },
    });

    const closeModal = () => {
        setIsModalManuallyOpen(false);
        setEditingAgent(null);
        if (searchParams.get('create') === '1') {
            const next = new URLSearchParams(searchParams);
            next.delete('create');
            setSearchParams(next, { replace: true });
        }
    };

    const onSubmit = (values: AgentFormValues) => {
        if (editingAgent) {
            updateAgent.mutate(
                {
                    id: editingAgent.id,
                    updates: {
                        ...values,
                        version: (values.version || '').trim() || '1.0.0',
                    }
                },
                {
                    onSuccess: () => {
                        closeModal();
                        reset();
                    }
                }
            );
        } else {
            createAgent.mutate(
                {
                    ...values,
                    version: (values.version || '').trim() || '1.0.0',
                },
                {
                    onSuccess: () => {
                        closeModal();
                        reset();
                    },
                }
            );
        }
    };

    const onSearchChange = (value: string) => {
        const next = new URLSearchParams(searchParams);
        if (value.trim()) {
            next.set('q', value);
        } else {
            next.delete('q');
        }
        setSearchParams(next, { replace: true });
    };

    const filteredAgents = useMemo(() => {
        const source = (Array.isArray(agents) ? agents : []) as AgentRecord[];
        return source.filter((agent) => {
            const matchesSearch = (agent.name || '').toLowerCase().includes(query.toLowerCase());
            const matchesStatus = statusFilter === 'all' || (agent.status || 'active') === statusFilter;
            return matchesSearch && matchesStatus;
        });
    }, [agents, query, statusFilter]);

    const createErrorMessage = (() => {
        const err = createAgent.error || updateAgent.error;
        if (!err) return null;
        if (err instanceof Error) return err.message;
        if (typeof err === 'object' && err !== null && 'message' in err) {
            const value = (err as { message?: unknown }).message;
            if (typeof value === 'string' && value.trim()) return value;
        }
        return 'Unable to save agent. Check API key and backend status.';
    })();

    const handleEdit = (agent: AgentRecord) => {
        setEditingAgent(agent);
        reset({
            name: agent.name,
            version: agent.version,
            description: agent.description || '',
        });
        setIsModalManuallyOpen(true);
    };

    const handleDeploy = (agent: AgentRecord) => {
        navigate(`/execute?agentId=${agent.id}`);
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Agent Directory</h1>
                    <p className="text-slate-500">Manage and configure your AI agent fleet.</p>
                </div>
                <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={() => refetch()} className="hidden sm:flex">
                        <RefreshCw size={16} className={isLoading ? 'animate-spin' : ''} />
                    </Button>
                    <Button size="sm" onClick={() => {
                        setEditingAgent(null);
                        reset({ name: '', version: '1.0.0', description: '' });
                        setIsModalManuallyOpen(true);
                    }} className="flex items-center gap-2">
                        <Plus size={18} />
                        <span>Create Agent</span>
                    </Button>
                </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                    <input
                        id="agent-search"
                        name="agent-search"
                        type="text"
                        placeholder="Search agents by name..."
                        aria-label="Search agents"
                        className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                        value={query}
                        onChange={(event) => onSearchChange(event.target.value)}
                    />
                </div>
                <Button
                    variant="outline"
                    className="sm:w-auto flex items-center gap-2"
                    onClick={() => setStatusFilter((prev) => (prev === 'all' ? 'active' : 'all'))}
                >
                    <Filter size={18} />
                    <span>{statusFilter === 'all' ? 'Filters: All' : 'Filters: Active'}</span>
                </Button>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Name</TableHead>
                            <TableHead>Version</TableHead>
                            <TableHead>Created At</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {filteredAgents.map((agent) => (
                            <TableRow key={agent.id}>
                                <TableCell className="font-semibold text-slate-900">{agent.name}</TableCell>
                                <TableCell>
                                    <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-xs font-medium border border-slate-200">
                                        v{agent.version || '1.0.0'}
                                    </span>
                                </TableCell>
                                <TableCell className="text-slate-500 text-xs">
                                    {agent.created_at ? new Date(agent.created_at).toLocaleDateString() : '-'}
                                </TableCell>
                                <TableCell>
                                    <span className="flex items-center gap-1.5 text-xs font-semibold text-green-600 capitalize">
                                        <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
                                        {agent.status || 'active'}
                                    </span>
                                </TableCell>
                                <TableCell className="text-right space-x-1">
                                    <Button variant="ghost" size="sm" onClick={() => handleEdit(agent)}>Edit</Button>
                                    <Button variant="ghost" size="sm" className="text-blue-600" onClick={() => handleDeploy(agent)}>Deploy</Button>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        className="text-red-500 hover:text-red-700"
                                        onClick={() => {
                                            if (window.confirm(`Delete agent "${agent.name}"? This cannot be undone.`)) {
                                                deleteAgentMutation.mutate(agent.id);
                                            }
                                        }}
                                    >
                                        Delete
                                    </Button>
                                </TableCell>
                            </TableRow>
                        ))}
                        {filteredAgents.length === 0 && !isLoading && (
                            <TableRow>
                                <TableCell colSpan={5} className="border-0 p-0">
                                    <EmptyState
                                        icon={Bot}
                                        title={query ? 'No agents match your search' : 'No agents created yet'}
                                        description={query ? 'Try a different search term or clear your filters.' : 'Create your first AI agent to start orchestrating intelligent workflows.'}
                                        actionLabel={query ? undefined : 'Create Agent'}
                                        onAction={query ? undefined : () => {
                                            setEditingAgent(null);
                                            reset({ name: '', version: '1.0.0', description: '' });
                                            setIsModalManuallyOpen(true);
                                        }}
                                        accentColor="blue"
                                    />
                                </TableCell>
                            </TableRow>
                        )}
                        {isLoading && (
                            <TableRow>
                                <TableCell colSpan={5} className="p-0 border-0">
                                    <TableSkeleton rows={4} cols={5} hasHeader={false} />
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </div>

            <Modal
                isOpen={isModalOpen}
                onClose={closeModal}
                title={editingAgent ? "Edit Agent" : "Create New Agent"}
            >
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 pt-2">
                    <Input
                        id="agent-name"
                        label="Agent Name"
                        placeholder="e.g. Finance Analyzer"
                        {...register('name')}
                        error={errors.name?.message}
                    />
                    <Input
                        id="agent-version"
                        label="Version (optional)"
                        placeholder="Defaults to 1.0.0"
                        {...register('version')}
                        error={errors.version?.message}
                    />
                    <p className="text-xs text-slate-500 -mt-2">
                        Leave empty to auto-assign version `1.0.0`.
                    </p>
                    <div className="space-y-1.5">
                        <label htmlFor="agent-description" className="text-sm font-medium text-slate-700">Description</label>
                        <textarea
                            id="agent-description"
                            className="w-full min-h-[100px] rounded-md border border-slate-200 bg-white px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                            placeholder="What does this agent do?"
                            {...register('description')}
                        />
                    </div>
                    {createErrorMessage && (
                        <p className="text-sm text-red-600">{createErrorMessage}</p>
                    )}
                    <div className="flex justify-end gap-3 pt-4">
                        <Button variant="ghost" type="button" onClick={closeModal}>
                            Cancel
                        </Button>
                        <Button type="submit" isLoading={createAgent.isPending || updateAgent.isPending}>
                            {editingAgent ? "Save Changes" : "Create Agent"}
                        </Button>
                    </div>
                </form>
            </Modal>
        </div>
    );
};
