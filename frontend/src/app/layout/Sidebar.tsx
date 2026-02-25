import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
    LayoutDashboard,
    Users,
    PlayCircle,
    Terminal,
    Activity,
    ChevronLeft,
    ChevronRight,
    BarChart3,
    LogOut,
    Shield,
    Crown,
    Zap,
} from 'lucide-react';
import { cn } from '../../shared/lib/utils';
import { useState } from 'react';
import { useAuth } from '../auth/AuthContext';

const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Agents', href: '/agents', icon: Users },
    { name: 'Runs', href: '/runs', icon: PlayCircle },
    { name: 'Playground', href: '/execute', icon: Terminal },
    { name: 'Evaluations', href: '/eval', icon: BarChart3 },
    { name: 'System Status', href: '/status', icon: Activity },
];

interface SidebarItemProps {
    to: string;
    icon: any;
    label: string;
    isCollapsed: boolean;
}

const SidebarItem = ({ to, icon: Icon, label, isCollapsed }: SidebarItemProps) => {
    const location = useLocation();
    const isActive = location.pathname === to || (to !== '/' && location.pathname.startsWith(to));

    return (
        <Link
            to={to}
            className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative',
                isActive
                    ? 'bg-gradient-to-r from-blue-600/10 to-indigo-600/10 text-blue-600 dark:text-blue-400 font-semibold shadow-sm border border-blue-500/10'
                    : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100/80 dark:hover:bg-slate-800/50 hover:text-slate-700'
            )}
        >
            <div className={cn(
                'flex items-center justify-center w-8 h-8 rounded-lg transition-all shrink-0',
                isActive
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/30'
                    : 'bg-transparent text-slate-400 group-hover:text-slate-600 group-hover:bg-slate-200/50'
            )}>
                <Icon size={18} />
            </div>
            {!isCollapsed && <span className="text-[13px] truncate">{label}</span>}
            {isCollapsed && (
                <div className="absolute left-full ml-3 px-3 py-1.5 bg-slate-900 text-white text-xs rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all whitespace-nowrap z-50 shadow-xl">
                    {label}
                    <div className="absolute left-0 top-1/2 -translate-x-1 -translate-y-1/2 w-2 h-2 bg-slate-900 rotate-45" />
                </div>
            )}
            {isActive && !isCollapsed && (
                <div className="absolute right-2 w-1.5 h-1.5 rounded-full bg-blue-600 animate-pulse" />
            )}
        </Link>
    );
};

export const Sidebar = () => {
    const [isCollapsed, setIsCollapsed] = useState(false);
    const { user, isAuthenticated, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    // Derive initials and display name
    const displayName = user?.name || 'Admin User';
    const initials = displayName
        .split(' ')
        .map((w: string) => w[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);
    const roleLabel = isAuthenticated ? 'Authenticated' : 'Master Node';

    return (
        <aside
            className={cn(
                'flex flex-col border-r border-slate-200/80 dark:border-slate-800 bg-white dark:bg-slate-900 transition-all duration-300 relative',
                isCollapsed ? 'w-[72px]' : 'w-[260px]'
            )}
        >
            {/* Logo Section */}
            <div className="flex items-center gap-3 px-4 h-16 border-b border-slate-200/80 dark:border-slate-800">
                <div className="h-9 w-9 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl flex items-center justify-center shrink-0 shadow-lg shadow-blue-600/20">
                    <Zap size={18} className="text-white" />
                </div>
                {!isCollapsed && (
                    <div className="min-w-0">
                        <span className="font-bold text-base bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600 block leading-tight">
                            TraceAI
                        </span>
                        <span className="text-[10px] text-slate-400 font-medium tracking-wider uppercase">
                            Agent Platform
                        </span>
                    </div>
                )}
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
                {!isCollapsed && (
                    <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest px-3 mb-3">
                        Platform
                    </p>
                )}
                {navigation.map((item) => (
                    <SidebarItem
                        key={item.href}
                        to={item.href}
                        icon={item.icon}
                        label={item.name}
                        isCollapsed={isCollapsed}
                    />
                ))}
            </nav>

            {/* Collapse Toggle */}
            <div className="px-3 py-2 border-t border-slate-200/60 dark:border-slate-800">
                <button
                    onClick={() => setIsCollapsed(!isCollapsed)}
                    className="w-full flex items-center justify-center p-2 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl transition-all hover:text-slate-600"
                >
                    {isCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
                </button>
            </div>

            {/* User Profile Section */}
            <div className={cn(
                'border-t border-slate-200/60 dark:border-slate-800 transition-all',
                isCollapsed ? 'px-3 py-3' : 'px-4 py-4'
            )}>
                <div className={cn(
                    'flex items-center gap-3 rounded-xl transition-all',
                    !isCollapsed && 'bg-gradient-to-r from-slate-50 to-blue-50/50 dark:from-slate-800/50 dark:to-blue-950/30 p-3 border border-slate-200/50 dark:border-slate-700/50'
                )}>
                    {/* Avatar */}
                    <div className="relative shrink-0 group">
                        <div className={cn(
                            'w-9 h-9 rounded-xl flex items-center justify-center font-bold text-sm transition-all',
                            isAuthenticated
                                ? 'bg-gradient-to-br from-emerald-500 to-teal-600 text-white shadow-lg shadow-emerald-500/30'
                                : 'bg-gradient-to-br from-blue-500 to-indigo-600 text-white shadow-lg shadow-blue-500/30'
                        )}>
                            {initials}
                        </div>
                        {/* Online indicator */}
                        <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full bg-emerald-500 border-2 border-white dark:border-slate-900" />
                    </div>

                    {/* User Info */}
                    {!isCollapsed && (
                        <div className="min-w-0 flex-1">
                            <div className="flex items-center gap-1.5">
                                <p className="text-sm font-semibold text-slate-800 dark:text-slate-100 truncate">
                                    {displayName}
                                </p>
                                <Crown size={12} className="text-amber-500 shrink-0" />
                            </div>
                            <div className="flex items-center gap-1.5 mt-0.5">
                                <Shield size={10} className="text-blue-500" />
                                <p className="text-[10px] font-bold text-blue-600 dark:text-blue-400 uppercase tracking-wider">
                                    {roleLabel}
                                </p>
                            </div>
                        </div>
                    )}

                    {/* Logout */}
                    {!isCollapsed && isAuthenticated && (
                        <button
                            onClick={handleLogout}
                            className="p-1.5 rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30 transition-all"
                            title="Sign out"
                        >
                            <LogOut size={14} />
                        </button>
                    )}

                    {/* Login button when not authenticated */}
                    {!isCollapsed && !isAuthenticated && (
                        <Link
                            to="/login"
                            className="px-2.5 py-1 text-[11px] font-semibold rounded-lg bg-blue-600 text-white hover:bg-blue-700 transition-all shadow-sm"
                        >
                            Sign In
                        </Link>
                    )}
                </div>

                {/* Collapsed: show user icon with tooltip */}
                {isCollapsed && isAuthenticated && (
                    <button
                        onClick={handleLogout}
                        className="w-full mt-2 flex items-center justify-center p-2 text-slate-400 hover:text-red-500 hover:bg-red-50/80 dark:hover:bg-red-950/30 rounded-xl transition-all group relative"
                        title="Sign out"
                    >
                        <LogOut size={16} />
                        <div className="absolute left-full ml-3 px-3 py-1.5 bg-slate-900 text-white text-xs rounded-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all whitespace-nowrap z-50 shadow-xl">
                            Sign Out
                        </div>
                    </button>
                )}
            </div>
        </aside>
    );
};
