import { Link, useLocation } from 'react-router-dom';
import {
    LayoutDashboard,
    Users,
    PlayCircle,
    Terminal,
    Activity,
    ChevronLeft,
    ChevronRight
} from 'lucide-react';
import { cn } from '../../shared/lib/utils';
import { useState } from 'react';

const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Agents', href: '/agents', icon: Users },
    { name: 'Runs', href: '/runs', icon: PlayCircle },
    { name: 'Playground', href: '/execute', icon: Terminal },
    { name: 'Status', href: '/status', icon: Activity },
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
                'flex items-center gap-3 px-3 py-2 rounded-lg transition-colors group relative',
                isActive
                    ? 'bg-slate-100 dark:bg-slate-800 text-blue-600 dark:text-blue-400 font-medium'
                    : 'text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800/50'
            )}
        >
            <Icon size={20} className={cn('shrink-0', isActive ? 'text-blue-600' : 'text-slate-400 group-hover:text-slate-600')} />
            {!isCollapsed && <span className="text-sm truncate">{label}</span>}
            {isCollapsed && (
                <div className="absolute left-full ml-2 px-2 py-1 bg-slate-900 text-white text-xs rounded opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all whitespace-nowrap z-50">
                    {label}
                </div>
            )}
        </Link>
    );
};

export const Sidebar = () => {
    const [isCollapsed, setIsCollapsed] = useState(false);

    return (
        <aside
            className={cn(
                'flex flex-col border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 transition-all duration-300 relative',
                isCollapsed ? 'w-16' : 'w-64'
            )}
        >
            <div className="flex items-center gap-3 px-4 h-16 border-bottom mb-4">
                <div className="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center shrink-0">
                    <Activity size={20} className="text-white" />
                </div>
                {!isCollapsed && <span className="font-bold text-lg bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">TraceAI</span>}
            </div>

            <nav className="flex-1 px-2 space-y-1">
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

            <div className="p-2 border-t border-slate-200 dark:border-slate-800">
                <button
                    onClick={() => setIsCollapsed(!isCollapsed)}
                    className="w-full flex items-center justify-center p-2 text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-lg transition-colors"
                >
                    {isCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
                </button>
            </div>

            {/* User Info */}
            <div className="px-5 py-6 bg-slate-50/50 border-t border-slate-100">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold shrink-0">
                        A
                    </div>
                    {!isCollapsed && (
                        <div className="min-w-0">
                            <p className="text-sm font-semibold text-slate-900 truncate">Admin User</p>
                            <p className="text-[10px] text-blue-600 uppercase font-bold tracking-widest">Master Node</p>
                        </div>
                    )}
                </div>
            </div>
        </aside>
    );
};
