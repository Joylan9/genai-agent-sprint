import { useState } from 'react';
import { useAgents, useCreateAgent } from '../hooks/useAgent';
import { Button } from '../../../shared/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../../shared/ui/Table';
import { Modal } from '../../../shared/ui/Modal';
import { Input } from '../../../shared/ui/Input';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Search, Filter, Plus, RefreshCw } from 'lucide-react';

const agentSchema = z.object({
    name: z.string().min(3, 'Name must be at least 3 characters'),
    version: z.string().min(1, 'Version is required'),
    description: z.string().optional(),
});

type AgentFormValues = z.infer<typeof agentSchema>;

export const AgentListPage = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [isModalOpen, setIsModalOpen] = useState(false);

    const { data: agents, isLoading, refetch } = useAgents();
    const createAgent = useCreateAgent();

    const { register, handleSubmit, reset, formState: { errors } } = useForm<AgentFormValues>({
        resolver: zodResolver(agentSchema),
        defaultValues: { version: '1.0.0' }
    });

    const onSubmit = (data: AgentFormValues) => {
        createAgent.mutate(data, {
            onSuccess: () => {
                setIsModalOpen(false);
                reset();
            }
        });
    };

    const filteredAgents = agents?.filter((a: any) =>
        a.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

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
                    <Button size="sm" onClick={() => setIsModalOpen(true)} className="flex items-center gap-2">
                        <Plus size={18} />
                        <span>Create Agent</span>
                    </Button>
                </div>
            </div>

            {/* Filters Bar */}
            <div className="flex flex-col sm:flex-row gap-4 bg-white p-4 rounded-lg border border-slate-200 shadow-sm">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                    <input
                        type="text"
                        placeholder="Search agents by name..."
                        className="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
                <Button variant="outline" className="sm:w-auto flex items-center gap-2">
                    <Filter size={18} />
                    <span>Filters</span>
                </Button>
            </div>

            {/* Agents Table */}
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
                        {filteredAgents?.map((agent: any) => (
                            <TableRow key={agent.id}>
                                <TableCell className="font-semibold text-slate-900">{agent.name}</TableCell>
                                <TableCell>
                                    <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-xs font-medium border border-slate-200">
                                        v{agent.version}
                                    </span>
                                </TableCell>
                                <TableCell className="text-slate-500 text-xs">
                                    {new Date(agent.created_at).toLocaleDateString()}
                                </TableCell>
                                <TableCell>
                                    <span className="flex items-center gap-1.5 text-xs font-semibold text-green-600">
                                        <span className="h-1.5 w-1.5 rounded-full bg-green-500" />
                                        Active
                                    </span>
                                </TableCell>
                                <TableCell className="text-right">
                                    <Button variant="ghost" size="sm">Edit</Button>
                                    <Button variant="ghost" size="sm" className="text-blue-600">Deploy</Button>
                                </TableCell>
                            </TableRow>
                        ))}
                        {(!filteredAgents || filteredAgents.length === 0) && !isLoading && (
                            <TableRow>
                                <TableCell colSpan={5} className="h-32 text-center text-slate-500">
                                    <div className="flex flex-col items-center justify-center space-y-2">
                                        <p className="font-medium text-slate-600">No agents found matching your search.</p>
                                        <p className="text-xs">Try a different search term or create a new agent.</p>
                                    </div>
                                </TableCell>
                            </TableRow>
                        )}
                        {isLoading && (
                            <TableRow>
                                <TableCell colSpan={5} className="h-32 text-center">
                                    <div className="flex justify-center">
                                        <RefreshCw className="animate-spin text-blue-600" size={24} />
                                    </div>
                                </TableCell>
                            </TableRow>
                        )}
                    </TableBody>
                </Table>
            </div>

            {/* Create Agent Modal */}
            <Modal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                title="Create New Agent"
            >
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 pt-2">
                    <Input
                        label="Agent Name"
                        placeholder="e.g. Finance Analyzer"
                        {...register('name')}
                        error={errors.name?.message}
                    />
                    <Input
                        label="Version"
                        placeholder="1.0.0"
                        {...register('version')}
                        error={errors.version?.message}
                    />
                    <div className="space-y-1.5">
                        <label className="text-sm font-medium text-slate-700">Description</label>
                        <textarea
                            className="w-full min-h-[100px] rounded-md border border-slate-200 bg-white px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                            placeholder="What does this agent do?"
                            {...register('description')}
                        />
                    </div>
                    <div className="flex justify-end gap-3 pt-4">
                        <Button variant="ghost" type="button" onClick={() => setIsModalOpen(false)}>
                            Cancel
                        </Button>
                        <Button type="submit" isLoading={createAgent.isPending}>
                            Create Agent
                        </Button>
                    </div>
                </form>
            </Modal>
        </div>
    );
};
