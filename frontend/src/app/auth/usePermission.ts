import { useMemo } from 'react';

export type UserRole = 'admin' | 'developer' | 'viewer';

export interface User {
    id: string;
    name: string;
    role: UserRole;
}

export const usePermission = () => {
    // Mock logged-in user
    const user: User = {
        id: 'u-001',
        name: 'Admin User',
        role: 'admin',
    };

    const permissions = useMemo(() => ({
        canCreateAgent: user.role === 'admin' || user.role === 'developer',
        canRunAgent: user.role === 'admin' || user.role === 'developer',
        canDeleteAgent: user.role === 'admin',
        canViewTelemetry: user.role !== 'viewer',
        isAdmin: user.role === 'admin',
    }), [user.role]);

    const hasRole = (role: UserRole | UserRole[]) => {
        const roles = Array.isArray(role) ? role : [role];
        return roles.includes(user.role);
    };

    return { user, permissions, hasRole };
};
