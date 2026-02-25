import { Command, Moon, Search, Sun, Zap, CheckCircle2, XCircle, X } from 'lucide-react';
import { type FormEvent, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { useHealth } from '../../features/agent/hooks/useAgent';
import { Button } from '../../shared/ui/Button';
import { cn } from '../../shared/lib/utils';
import { ActivityDrawer } from './ActivityDrawer';
import { agentClient } from '../../features/agent/api/agentClient';

function getInitialTheme() {
    if (typeof window === 'undefined') return false;
    const persisted = window.localStorage.getItem('theme');
    if (persisted === 'dark') return true;
    if (persisted === 'light') return false;
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
}

// Derive environment from URL or env variable
function getEnvironment(): 'LOCAL' | 'STAGING' | 'PRODUCTION' {
    const host = window.location.hostname;
    if (host === 'localhost' || host === '127.0.0.1') return 'LOCAL';
    if (host.includes('staging') || host.includes('dev')) return 'STAGING';
    return 'PRODUCTION';
}

const ENV_STYLES = {
    LOCAL: 'bg-amber-500/10 text-amber-600 border-amber-500/20 dark:text-amber-400',
    STAGING: 'bg-blue-500/10 text-blue-600 border-blue-500/20 dark:text-blue-400',
    PRODUCTION: 'bg-emerald-500/10 text-emerald-600 border-emerald-500/20 dark:text-emerald-400',
};

export const TopNav = () => {
    const navigate = useNavigate();
    const [searchTerm, setSearchTerm] = useState('');
    const [isDarkMode, setIsDarkMode] = useState(getInitialTheme);
    const { data: health } = useHealth();
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [activeRunCount, setActiveRunCount] = useState(0);
    const prevRunMap = useRef<Record<string, string>>({});
    const [toasts, setToasts] = useState<{ id: string; message: string; type: 'success' | 'error' }[]>([]);
    const toastTimeouts = useRef<Record<string, ReturnType<typeof setTimeout>>>({});

    const env = useMemo(() => getEnvironment(), []);

    // Show toast notification
    const showToast = useCallback((id: string, message: string, type: 'success' | 'error') => {
        setToasts(prev => [...prev.slice(-2), { id, message, type }]); // keep max 3
        toastTimeouts.current[id] = setTimeout(() => {
            setToasts(prev => prev.filter(t => t.id !== id));
            delete toastTimeouts.current[id];
        }, 4000);
    }, []);

    // Poll active runs count + detect completions/failures
    useEffect(() => {
        const fetchCount = async () => {
            try {
                const runs = await agentClient.listRuns();
                const all = runs || [];
                setActiveRunCount(all.filter((r: any) => r.status === 'running' || r.status === 'queued').length);

                // Detect state transitions
                const newMap: Record<string, string> = {};
                for (const r of all) {
                    newMap[r.id] = r.status;
                    const prevStatus = prevRunMap.current[r.id];
                    if (prevStatus && (prevStatus === 'running' || prevStatus === 'queued')) {
                        if (r.status === 'completed') {
                            showToast(r.id, `Run ${r.id?.slice(0, 8)} completed`, 'success');
                        } else if (r.status === 'failed') {
                            showToast(r.id, `Run ${r.id?.slice(0, 8)} failed`, 'error');
                        }
                    }
                }
                prevRunMap.current = newMap;
            } catch { /* ignore */ }
        };
        fetchCount();
        const interval = setInterval(fetchCount, 8000);
        return () => clearInterval(interval);
    }, [showToast]);

    const normalizedHealth = useMemo(
        () => (health?.status || '').toLowerCase(),
        [health?.status]
    );
    const isHealthy = normalizedHealth === 'ok' || normalizedHealth === 'healthy';

    useEffect(() => {
        const root = document.documentElement;
        root.classList.toggle('dark', isDarkMode);
        window.localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    }, [isDarkMode]);

    const openCommandPalette = () => {
        window.dispatchEvent(new Event('open-command-palette'));
    };

    const onSearchSubmit = (event: FormEvent) => {
        event.preventDefault();
        const query = searchTerm.trim();
        if (!query) {
            openCommandPalette();
            return;
        }
        navigate(`/agents?q=${encodeURIComponent(query)}`);
    };

    return (
        <header className="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between sticky top-0 z-40 dark:bg-slate-900 dark:border-slate-800">
            <div className="flex-1 max-w-xl">
                <form onSubmit={onSearchSubmit} className="relative group">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 group-hover:text-blue-500 transition-colors" size={18} />
                    <input
                        id="nav-search"
                        name="nav-search"
                        value={searchTerm}
                        onChange={(event) => setSearchTerm(event.target.value)}
                        placeholder="Search agents..."
                        aria-label="Search agents"
                        className="w-64 pl-10 pr-14 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-700 hover:bg-white hover:border-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all dark:bg-slate-800 dark:border-slate-700 dark:text-slate-200"
                    />
                    <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1 border border-slate-200 rounded px-1.5 py-0.5 bg-white text-[10px] text-slate-400 dark:bg-slate-800 dark:border-slate-700">
                        <Command size={10} />
                        <span>K</span>
                    </div>
                </form>
            </div>

            <div className="flex items-center gap-3">
                {/* Environment Badge */}
                <div className={cn(
                    'flex items-center gap-1.5 px-2.5 py-1 rounded-md border text-[10px] font-bold uppercase tracking-wider',
                    ENV_STYLES[env]
                )}>
                    {env}
                </div>

                {/* System Status */}
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-50 border border-slate-100 dark:bg-slate-800 dark:border-slate-700">
                    <span className="relative flex items-center justify-center">
                        {isHealthy && (
                            <span className="absolute h-4 w-4 rounded-full bg-green-400/40" style={{ animation: 'healthPulse 2.5s ease-in-out infinite' }} />
                        )}
                        <span className={cn(
                            'relative h-2 w-2 rounded-full',
                            isHealthy ? 'bg-green-500' : 'bg-red-500 animate-pulse'
                        )} />
                    </span>
                    <span className="text-xs font-medium text-slate-600 dark:text-slate-300">
                        {isHealthy ? 'System Ready' : 'Dependency Alert'}
                    </span>
                </div>

                <div className="h-8 w-px bg-slate-200 mx-1 dark:bg-slate-700" />

                {/* Activity Indicator — opens drawer */}
                <button
                    onClick={() => setDrawerOpen(true)}
                    className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-50 border border-blue-100 dark:bg-blue-950/30 dark:border-blue-900 hover:bg-blue-100 dark:hover:bg-blue-900/40 transition-colors relative"
                >
                    <Zap size={14} className="text-blue-500" />
                    <span className="text-xs font-semibold text-blue-600 dark:text-blue-400">
                        {activeRunCount > 0 ? `${activeRunCount} Active` : 'Activity'}
                    </span>
                    {activeRunCount > 0 && (
                        <span className="absolute -top-1 -right-1 w-4 h-4 bg-blue-600 text-white text-[9px] font-bold rounded-full flex items-center justify-center animate-pulse">
                            {activeRunCount}
                        </span>
                    )}
                </button>

                <Button
                    variant="ghost"
                    size="sm"
                    className="w-9 h-9 p-0 rounded-full"
                    onClick={() => setIsDarkMode((prev) => !prev)}
                    aria-label="Toggle theme"
                >
                    {isDarkMode ? (
                        <Moon size={18} className="text-slate-200" />
                    ) : (
                        <Sun size={18} className="text-slate-600" />
                    )}
                </Button>
            </div>

            <ActivityDrawer isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />

            {/* Toast Notifications */}
            <div className="fixed bottom-6 right-6 z-[60] flex flex-col gap-2 pointer-events-none">
                {toasts.map(toast => (
                    <div
                        key={toast.id}
                        className={cn(
                            'flex items-center gap-2.5 px-4 py-3 rounded-xl shadow-2xl border backdrop-blur-md pointer-events-auto',
                            'animate-in slide-in-from-right-5 fade-in duration-300',
                            toast.type === 'success'
                                ? 'bg-emerald-50/90 dark:bg-emerald-950/90 border-emerald-200 dark:border-emerald-800'
                                : 'bg-red-50/90 dark:bg-red-950/90 border-red-200 dark:border-red-800',
                        )}
                    >
                        {toast.type === 'success' ? (
                            <CheckCircle2 size={16} className="text-emerald-500" />
                        ) : (
                            <XCircle size={16} className="text-red-500" />
                        )}
                        <span className={cn(
                            'text-sm font-medium',
                            toast.type === 'success' ? 'text-emerald-700 dark:text-emerald-300' : 'text-red-700 dark:text-red-300',
                        )}>
                            {toast.message}
                        </span>
                        <button
                            onClick={() => setToasts(prev => prev.filter(t => t.id !== toast.id))}
                            className="ml-2 p-0.5 rounded hover:bg-black/5 dark:hover:bg-white/10 transition-colors"
                        >
                            <X size={12} className="text-slate-400" />
                        </button>
                    </div>
                ))}
            </div>
        </header>
    );
};
