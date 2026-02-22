import { Link, useLocation } from 'react-router-dom';
import { Home, Users, Activity, Play, Layout, Settings, HelpCircle, ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '../../shared/lib/utils';
import { useState } from 'react';

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
                "flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200 group relative",
                isActive
                    ? "bg-blue-600 text-white shadow-md shadow-blue-500/20"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
            )}
        >
            <Icon size={20} className={cn("shrink-0", isActive ? "text-white" : "text-slate-400 group-hover:text-blue-600")} />
            {!isCollapsed && <span className="font-medium truncate">{label}</span>}
            {isCollapsed && (
                <div className="absolute left-full ml-2 px-2 py-1 bg-slate-900 text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity z-50 whitespace-nowrap">
                    {label}
                </div>
            )}
        </Link>
    );
};

export const Sidebar = () => {
    const [isCollapsed, setIsCollapsed] = useState(false);

    return (
        <aside className={cn(
            "h-screen bg-white border-r border-slate-200 flex flex-col transition-all duration-300 relative",
            isCollapsed ? "w-20" : "w-64"
        )}>
            {/* Brand */}
            <div className="p-6 flex items-center gap-3">
                <div className="bg-blue-600 p-2 rounded-lg text-white">
                    <Layout size={20} strokeWidth={2.5} />
                </div>
                {!isCollapsed && <span className="text-xl font-bold tracking-tight text-slate-900">AgentEngine</span>}
            </div>

            {/* Nav */}
            <nav className="flex-1 px-4 py-4 space-y-1">
                <SidebarItem to="/" icon={Home} label="Dashboard" isCollapsed={isCollapsed} />
                <SidebarItem to="/agents" icon={Users} label="Agents" isCollapsed={isCollapsed} />
                <SidebarItem to="/runs" icon={Activity} label="Runs" isCollapsed={isCollapsed} />
                <SidebarItem to="/execute" icon={Play} label="Playground" isCollapsed={isCollapsed} />
            </nav>

            {/* Bottom Actions */}
            <div className="px-4 py-4 border-t border-slate-100 space-y-1">
                <SidebarItem to="/settings" icon={Settings} label="Settings" isCollapsed={isCollapsed} />
                <SidebarItem to="/support" icon={HelpCircle} label="Help & Support" isCollapsed={isCollapsed} />

                <button
                    onClick={() => setIsCollapsed(!isCollapsed)}
                    className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-slate-500 hover:bg-slate-100 transition-colors mt-4"
                >
                    {isCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
                    {!isCollapsed && <span className="text-sm font-medium">Collapse</span>}
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
