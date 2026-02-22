import type { ReactNode } from 'react';
import { usePermission, type UserRole } from './usePermission';
import { ShieldAlert } from 'lucide-react';
import { Button } from '../../shared/ui/Button';
import { Link } from 'react-router-dom';

interface RequireRoleProps {
    role: UserRole | UserRole[];
    children: ReactNode;
    fallback?: ReactNode;
    showFallback?: boolean;
}

export const RequireRole = ({ role, children, fallback, showFallback = true }: RequireRoleProps) => {
    const { hasRole } = usePermission();
    const isAuthorized = hasRole(role);

    if (!isAuthorized) {
        if (fallback) return <>{fallback}</>;

        if (!showFallback) return null;

        return (
            <div className="p-12 bg-white rounded-2xl border border-slate-200 text-center shadow-sm">
                <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center text-blue-600 mx-auto mb-4">
                    <ShieldAlert size={32} />
                </div>
                <h2 className="text-xl font-bold text-slate-900 mb-2">Access Restricted</h2>
                <p className="text-slate-500 mb-8 max-w-sm mx-auto">
                    You don't have the necessary permissions to view this section. Please contact your system administrator.
                </p>
                <Link to="/">
                    <Button variant="outline">Back to Dashboard</Button>
                </Link>
            </div>
        );
    }

    return <>{children}</>;
};
