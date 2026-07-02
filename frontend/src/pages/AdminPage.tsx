import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { agentClient } from '../features/agent/api/agentClient';
import { Button } from '../shared/ui/Button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../shared/ui/Table';
import { Badge } from '../shared/ui/Badge';
import { Modal } from '../shared/ui/Modal';
import { Skeleton } from '../shared/ui/Skeleton';
import { EmptyState } from '../shared/ui/EmptyState';
import { useAuth } from '../app/auth/AuthContext';
import { usePermission } from '../app/auth/usePermission';
import { useNavigate } from 'react-router-dom';
import {
    Users,
    Shield,
    Terminal,
    Eye,
    Activity,
    Trash2,
    Edit2,
    Search,
    AlertTriangle,
    Crown,
    UserMinus,
    RefreshCw
} from 'lucide-react';


export const AdminPage = () => {
    const queryClient = useQueryClient();
    const navigate = useNavigate();
    const { logout, user: currentUser } = useAuth();
    const { permissions } = usePermission();

    const [searchTerm, setSearchTerm] = useState('');
    const [selectedUser, setSelectedUser] = useState<any | null>(null);
    const [editRoleOpen, setEditRoleOpen] = useState(false);
    const [targetRole, setTargetRole] = useState<string>('');
    const [clearAllConfirmOpen, setClearAllConfirmOpen] = useState(false);
    const [deleteUserConfirmOpen, setDeleteUserConfirmOpen] = useState(false);
    const [errorMsg, setErrorMsg] = useState('');

    // Fetch administrative users
    const { data: users, isLoading: isLoadingUsers, refetch: refetchUsers } = useQuery({
        queryKey: ['admin_users'],
        queryFn: () => agentClient.listUsers(),
        enabled: permissions.isAdmin
    });

    // Fetch admin stats
    const { data: stats, isLoading: isLoadingStats } = useQuery({
        queryKey: ['admin_stats'],
        queryFn: () => agentClient.getAdminStats(),
        enabled: permissions.isAdmin,
        refetchInterval: 15000
    });

    // Mutations
    const updateRoleMutation = useMutation({
        mutationFn: ({ userId, role }: { userId: string; role: string }) =>
            agentClient.updateUserRole(userId, role),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin_users'] });
            queryClient.invalidateQueries({ queryKey: ['admin_stats'] });
            setEditRoleOpen(false);
            setSelectedUser(null);
            setErrorMsg('');
        },
        onError: (err: any) => {
            setErrorMsg(err.message || "Failed to update user's role");
        }
    });

    const deleteUserMutation = useMutation({
        mutationFn: (userId: string) => agentClient.deleteUser(userId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin_users'] });
            queryClient.invalidateQueries({ queryKey: ['admin_stats'] });
            setDeleteUserConfirmOpen(false);
            setSelectedUser(null);
            setErrorMsg('');
        },
        onError: (err: any) => {
            setErrorMsg(err.message || 'Failed to delete user');
        }
    });

    const clearAllMutation = useMutation({
        mutationFn: () => agentClient.clearAllData(),
        onSuccess: () => {
            // Logs out and redirects as all users (except currently logged in admin) are wiped, but we force logout to be safe
            logout();
            navigate('/login');
        },
        onError: (err: any) => {
            setErrorMsg(err.message || 'Failed to perform platform wipe');
        }
    });

    if (!permissions.isAdmin) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-center p-6">
                <div className="w-16 h-16 bg-red-50 text-red-600 rounded-full flex items-center justify-center mb-4 border border-red-100 shadow-sm animate-pulse">
                    <Shield size={32} />
                </div>
                <h1 className="text-2xl font-bold text-slate-900 mb-2">Restricted Section</h1>
                <p className="text-slate-500 max-w-md mb-6">
                    This module is reserved exclusively for System Administrators. You do not hold the required credentials to access this area.
                </p>
                <Button variant="outline" onClick={() => navigate('/')}>Return to Safety</Button>
            </div>
        );
    }

    const filteredUsers = (users || []).filter(u =>
        u.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        u.email.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const handleRoleUpdateSave = () => {
        if (!selectedUser || !targetRole) return;
        updateRoleMutation.mutate({ userId: selectedUser.id, role: targetRole });
    };

    const handleDeleteUserConfirm = () => {
        if (!selectedUser) return;
        deleteUserMutation.mutate(selectedUser.id);
    };

    const getRoleBadge = (role: string) => {
        switch (role.toLowerCase()) {
            case 'admin':
                return (
                    <Badge variant="red" className="flex items-center gap-1 w-fit bg-red-50 text-red-700 border-red-100 font-semibold px-2 py-0.5">
                        <Crown size={12} />
                        <span>Admin</span>
                    </Badge>
                );
            case 'developer':
                return (
                    <Badge variant="blue" className="flex items-center gap-1 w-fit bg-blue-50 text-blue-700 border-blue-100 font-semibold px-2 py-0.5">
                        <Terminal size={12} />
                        <span>Developer</span>
                    </Badge>
                );
            default:
                return (
                    <Badge variant="slate" className="flex items-center gap-1 w-fit bg-slate-50 text-slate-655 border-slate-200 font-semibold px-2 py-0.5">
                        <Eye size={12} />
                        <span>Viewer</span>
                    </Badge>
                );
        }
    };

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {/* Header */}
            <div className="flex items-center justify-between pb-2">
                <div>
                    <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 flex items-center gap-2">
                        <Shield className="text-blue-600 animate-pulse" size={32} />
                        <span>System Administration</span>
                    </h1>
                    <p className="text-slate-500 mt-1">
                        Review system-wide metrics, handle access control rights, and reset platform historical logs.
                    </p>
                </div>
                <div className="flex gap-3">
                    <Button
                        variant="outline"
                        className="flex items-center gap-2 hover:bg-slate-50"
                        onClick={() => { refetchUsers(); }}
                    >
                        <RefreshCw size={16} />
                        <span>Refresh Panel</span>
                    </Button>
                </div>
            </div>

            {/* Metrics cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
                {isLoadingStats ? (
                    Array.from({ length: 5 }).map((_, i) => (
                        <div key={i} className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm animate-pulse">
                            <Skeleton className="h-4 w-20 mb-3" />
                            <Skeleton className="h-8 w-12" />
                        </div>
                    ))
                ) : (
                    <>
                        <div className="bg-white p-6 rounded-2xl border border-slate-250/60 shadow-sm hover:shadow-md transition-all duration-200 relative overflow-hidden group">
                            <div className="absolute right-0 top-0 h-16 w-16 bg-blue-500/5 rounded-bl-full flex items-center justify-center group-hover:scale-110 transition-transform">
                                <Users size={18} className="text-blue-500" />
                            </div>
                            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Total Users</span>
                            <span className="text-3xl font-bold text-slate-900 block mt-2">{stats?.users?.total || 0}</span>
                        </div>
                        <div className="bg-white p-6 rounded-2xl border border-slate-250/60 shadow-sm hover:shadow-md transition-all duration-200 relative overflow-hidden group">
                            <div className="absolute right-0 top-0 h-16 w-16 bg-red-500/5 rounded-bl-full flex items-center justify-center group-hover:scale-110 transition-transform">
                                <Crown size={18} className="text-red-500" />
                            </div>
                            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Administrators</span>
                            <span className="text-3xl font-bold text-slate-900 block mt-2">{stats?.users?.admin || 0}</span>
                        </div>
                        <div className="bg-white p-6 rounded-2xl border border-slate-250/60 shadow-sm hover:shadow-md transition-all duration-200 relative overflow-hidden group">
                            <div className="absolute right-0 top-0 h-16 w-16 bg-indigo-500/5 rounded-bl-full flex items-center justify-center group-hover:scale-110 transition-transform">
                                <Terminal size={18} className="text-indigo-500" />
                            </div>
                            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Developers</span>
                            <span className="text-3xl font-bold text-slate-900 block mt-2">{stats?.users?.developer || 0}</span>
                        </div>
                        <div className="bg-white p-6 rounded-2xl border border-slate-250/60 shadow-sm hover:shadow-md transition-all duration-200 relative overflow-hidden group">
                            <div className="absolute right-0 top-0 h-16 w-16 bg-emerald-500/5 rounded-bl-full flex items-center justify-center group-hover:scale-110 transition-transform">
                                <Eye size={18} className="text-emerald-500" />
                            </div>
                            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Viewers</span>
                            <span className="text-3xl font-bold text-slate-900 block mt-2">{stats?.users?.viewer || 0}</span>
                        </div>
                        <div className="bg-white p-6 rounded-2xl border border-slate-250/60 shadow-sm hover:shadow-md transition-all duration-200 relative overflow-hidden group">
                            <div className="absolute right-0 top-0 h-16 w-16 bg-amber-500/5 rounded-bl-full flex items-center justify-center group-hover:scale-110 transition-transform">
                                <Activity size={18} className="text-amber-500" />
                            </div>
                            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Total Runs</span>
                            <span className="text-3xl font-bold text-slate-900 block mt-2">{stats?.runs?.total || 0}</span>
                        </div>
                    </>
                )}
            </div>

            {/* Users section */}
            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                <div className="p-6 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <h2 className="text-lg font-bold text-slate-900">User Directory</h2>
                        <p className="text-slate-400 text-xs mt-0.5">Manage details and authorization roles of all team members.</p>
                    </div>
                    <div className="relative w-full md:w-80">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
                        <input
                            type="text"
                            placeholder="Find member by name or email..."
                            className="w-full pl-9 pr-4 py-2 bg-slate-50/50 border border-slate-250 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition-all text-sm"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <Table>
                        <TableHeader>
                            <TableRow className="bg-slate-50/70 border-b border-slate-200">
                                <TableHead className="font-semibold text-slate-700 py-3.5">Name</TableHead>
                                <TableHead className="font-semibold text-slate-700">Email Address</TableHead>
                                <TableHead className="font-semibold text-slate-700">Assigned Role</TableHead>
                                <TableHead className="font-semibold text-slate-700">Signup Date</TableHead>
                                <TableHead className="font-semibold text-slate-700 text-right pr-6">Manage Access</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {isLoadingUsers ? (
                                Array.from({ length: 4 }).map((_, i) => (
                                    <TableRow key={i}>
                                        <TableCell><Skeleton className="h-4 w-32" /></TableCell>
                                        <TableCell><Skeleton className="h-4 w-44" /></TableCell>
                                        <TableCell><Skeleton className="h-6 w-20 rounded" /></TableCell>
                                        <TableCell><Skeleton className="h-4 w-28" /></TableCell>
                                        <TableCell className="text-right pr-6"><Skeleton className="h-8 w-16 ml-auto rounded" /></TableCell>
                                    </TableRow>
                                ))
                            ) : filteredUsers.length === 0 ? (
                                <TableRow>
                                    <TableCell colSpan={5} className="p-0">
                                        <EmptyState
                                            icon={Users}
                                            title="No group members found"
                                            description="No registered user profiles fit the current search term query."
                                            accentColor="blue"
                                            className="py-12"
                                        />
                                    </TableCell>
                                </TableRow>
                            ) : (
                                filteredUsers.map((user: any) => (
                                    <TableRow key={user.id} className="hover:bg-slate-50/40 transition-colors">
                                        <TableCell className="font-semibold text-slate-900 py-3.5 flex items-center gap-2">
                                            <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center text-xs font-bold text-slate-655 uppercase border border-slate-200/50">
                                                {user.name.slice(0, 2)}
                                            </div>
                                            <span>{user.name}</span>
                                            {user.id === currentUser?.id && (
                                                <Badge variant="green" className="bg-emerald-50 text-emerald-700 border-emerald-100 text-[10px] py-0">You</Badge>
                                            )}
                                        </TableCell>
                                        <TableCell className="text-slate-600 font-mono text-xs">{user.email}</TableCell>
                                        <TableCell>{getRoleBadge(user.role)}</TableCell>
                                        <TableCell className="text-slate-450 text-xs">
                                            {user.created_at ? new Date(user.created_at).toLocaleDateString(undefined, {
                                                year: 'numeric',
                                                month: 'short',
                                                day: 'numeric'
                                            }) : 'N/A'}
                                        </TableCell>
                                        <TableCell className="text-right pr-6 flex justify-end gap-2 py-3.5">
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                className="text-blue-650 hover:bg-blue-50/50"
                                                onClick={() => {
                                                    setSelectedUser(user);
                                                    setTargetRole(user.role);
                                                    setEditRoleOpen(true);
                                                }}
                                                title="Change Authority Role"
                                            >
                                                <Edit2 size={14} className="mr-1" />
                                                <span>Authorize</span>
                                            </Button>

                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                className="text-red-600 hover:bg-red-50/50"
                                                disabled={user.id === currentUser?.id}
                                                onClick={() => {
                                                    setSelectedUser(user);
                                                    setDeleteUserConfirmOpen(true);
                                                }}
                                                title="Remove Account"
                                            >
                                                <Trash2 size={14} />
                                            </Button>
                                        </TableCell>
                                    </TableRow>
                                ))
                            )}
                        </TableBody>
                    </Table>
                </div>
            </div>

            {/* Caution Zone */}
            <div className="bg-red-50/40 rounded-2xl border border-red-200/60 p-6 flex flex-col md:flex-row md:items-center justify-between gap-6 shadow-sm">
                <div className="flex gap-4">
                    <div className="w-12 h-12 bg-red-100 border border-red-200 rounded-xl flex items-center justify-center text-red-600 shrink-0">
                        <AlertTriangle size={24} className="animate-bounce" />
                    </div>
                    <div>
                        <h3 className="text-lg font-bold text-red-950">Danger / Security Control Panel</h3>
                        <p className="text-sm text-red-700/80 mt-1 max-w-2xl">
                            Wiping platform records is permanent and cannot be undone. This operation logs out all active logins, destroys all transaction history, execution records, users database, and resets parameters to default.
                        </p>
                    </div>
                </div>
                <Button
                    variant="destructive"
                    className="shrink-0 bg-red-650 hover:bg-red-700 text-white font-semibold py-2.5 px-5 shadow-lg shadow-red-150 flex items-center gap-2"
                    onClick={() => setClearAllConfirmOpen(true)}
                >
                    <Trash2 size={16} />
                    <span>Wipe Platform Credentials & History</span>
                </Button>
            </div>

            {/* Edit Role Modal */}
            <Modal
                isOpen={editRoleOpen}
                onClose={() => { setEditRoleOpen(false); setSelectedUser(null); setErrorMsg(''); }}
                title="Change Authority Role"
            >
                <div className="space-y-4 py-2">
                    {selectedUser && (
                        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl flex items-center gap-3">
                            <div className="w-9 h-9 bg-blue-50 border border-blue-100 text-blue-600 flex items-center justify-center text-sm font-bold rounded-lg uppercase">
                                {selectedUser.name.slice(0, 2)}
                            </div>
                            <div>
                                <p className="text-sm font-semibold text-slate-800">{selectedUser.name}</p>
                                <p className="text-xs text-slate-500 font-mono">{selectedUser.email}</p>
                            </div>
                        </div>
                    )}
                    <div>
                        <label className="block text-sm font-semibold text-slate-700 mb-2">Authority Role</label>
                        <select
                            id="role-select"
                            name="role-select"
                            className="w-full bg-white border border-slate-250 rounded-xl p-2.5 outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                            value={targetRole}
                            onChange={(e) => setTargetRole(e.target.value)}
                        >
                            <option value="viewer">Viewer</option>
                            <option value="developer">Developer</option>
                            <option value="admin">Admin</option>
                        </select>
                    </div>

                    {errorMsg && (
                        <p className="text-xs text-red-500 bg-red-50 p-2.5 border border-red-100 rounded-lg">{errorMsg}</p>
                    )}

                    <div className="flex justify-end gap-3 pt-2">
                        <Button
                            variant="outline"
                            onClick={() => { setEditRoleOpen(false); setSelectedUser(null); setErrorMsg(''); }}
                        >
                            Cancel
                        </Button>
                        <Button
                            onClick={handleRoleUpdateSave}
                            disabled={updateRoleMutation.isPending}
                            className="bg-blue-600 hover:bg-blue-700"
                        >
                            {updateRoleMutation.isPending ? 'Updating...' : 'Save Authority'}
                        </Button>
                    </div>
                </div>
            </Modal>

            {/* Delete Confirmation Modal */}
            <Modal
                isOpen={deleteUserConfirmOpen}
                onClose={() => { setDeleteUserConfirmOpen(false); setSelectedUser(null); setErrorMsg(''); }}
                title="Wipe User Profile"
            >
                <div className="space-y-4 py-2">
                    <div className="flex items-center gap-3 text-red-650 bg-red-50 border border-red-100 p-4 rounded-xl">
                        <UserMinus size={24} className="shrink-0" />
                        <p className="text-sm font-semibold">Are you absolutely sure you want to remove this account?</p>
                    </div>
                    {selectedUser && (
                        <div className="p-3 border border-slate-200 rounded-xl bg-slate-50">
                            <p className="text-sm font-semibold text-slate-800">{selectedUser.name}</p>
                            <p className="text-xs font-mono text-slate-540">{selectedUser.email}</p>
                        </div>
                    )}
                    <p className="text-xs text-slate-500 leading-relaxed">
                        This user will lose access immediately and all user profile information is deleted. Action is permanent.
                    </p>

                    {errorMsg && (
                        <p className="text-xs text-red-500 bg-red-50 p-2.5 border border-red-100 rounded-lg">{errorMsg}</p>
                    )}

                    <div className="flex justify-end gap-3 pt-2">
                        <Button
                            variant="outline"
                            onClick={() => { setDeleteUserConfirmOpen(false); setSelectedUser(null); setErrorMsg(''); }}
                        >
                            Cancel
                        </Button>
                        <Button
                            variant="destructive"
                            onClick={handleDeleteUserConfirm}
                            disabled={deleteUserMutation.isPending}
                        >
                            {deleteUserMutation.isPending ? 'Removing...' : 'Delete Permanently'}
                        </Button>
                    </div>
                </div>
            </Modal>

            {/* Clear All Confirmation Modal */}
            <Modal
                isOpen={clearAllConfirmOpen}
                onClose={() => { setClearAllConfirmOpen(false); setErrorMsg(''); }}
                title="Complete System Resets & Cleanse"
            >
                <div className="space-y-4 py-2">
                    <div className="flex gap-3 text-red-650 bg-red-50 border border-red-100 p-4 rounded-xl">
                        <AlertTriangle size={28} className="shrink-0 mt-0.5 animate-bounce" />
                        <div>
                            <p className="font-bold text-sm">Dangerous / Security Action Warning</p>
                            <p className="text-xs text-red-700/80 mt-0.5 leading-relaxed">
                                You are about to initiate a complete system reset. Everyone will be logged out, all developers/viewers delete entirely, all history traces clear.
                            </p>
                        </div>
                    </div>
                    <p className="text-xs text-slate-500 leading-relaxed">
                        Only your currently active admin user account will remain seeded, with default configured settings from `.env`.
                    </p>

                    {errorMsg && (
                        <p className="text-xs text-red-500 bg-red-50 p-2.5 border border-red-100 rounded-lg">{errorMsg}</p>
                    )}

                    <div className="flex justify-end gap-3 pt-2">
                        <Button
                            variant="outline"
                            onClick={() => { setClearAllConfirmOpen(false); setErrorMsg(''); }}
                        >
                            Cancel
                        </Button>
                        <Button
                            variant="destructive"
                            onClick={() => clearAllMutation.mutate()}
                            disabled={clearAllMutation.isPending}
                            className="bg-red-600 hover:bg-red-700 text-white"
                        >
                            {clearAllMutation.isPending ? 'Reseating & Wiping...' : 'Destroy All Data & Logout'}
                        </Button>
                    </div>
                </div>
            </Modal>
        </div>
    );
};
