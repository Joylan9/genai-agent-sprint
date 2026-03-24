import { useMemo } from 'react';
import { useAuth, type AuthUser, type UserRole } from './AuthContext';

export type User = AuthUser;
export type { UserRole };

export const usePermission = () => {
    const { user } = useAuth();
    const normalizedUser: User = user ?? {
        id: 'anonymous',
        email: 'anonymous@traceai.local',
        name: 'Anonymous',
        role: 'viewer',
    };

    const permissions = useMemo(() => ({
        canCreateAgent: normalizedUser.role === 'admin' || normalizedUser.role === 'developer',
        canRunAgent: normalizedUser.role === 'admin' || normalizedUser.role === 'developer',
        canDeleteAgent: normalizedUser.role === 'admin',
        canViewTelemetry: normalizedUser.role !== 'viewer',
        isAdmin: normalizedUser.role === 'admin',
    }), [normalizedUser.role]);

    const hasRole = (role: UserRole | UserRole[]) => {
        const roles = Array.isArray(role) ? role : [role];
        return roles.includes(normalizedUser.role);
    };

    return { user: normalizedUser, permissions, hasRole };
};
