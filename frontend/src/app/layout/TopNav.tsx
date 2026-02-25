import { Bell, Command, Moon, Search, Sun } from 'lucide-react';
import { type FormEvent, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { useHealth } from '../../features/agent/hooks/useAgent';
import { Button } from '../../shared/ui/Button';
import { cn } from '../../shared/lib/utils';

function getInitialTheme() {
    if (typeof window === 'undefined') return false;
    const persisted = window.localStorage.getItem('theme');
    if (persisted === 'dark') return true;
    if (persisted === 'light') return false;
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
}

export const TopNav = () => {
    const navigate = useNavigate();
    const [searchTerm, setSearchTerm] = useState('');
    const [isDarkMode, setIsDarkMode] = useState(getInitialTheme);
    const { data: health } = useHealth();

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

            <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-50 border border-slate-100 dark:bg-slate-800 dark:border-slate-700">
                    <span className={cn(
                        'h-2 w-2 rounded-full',
                        isHealthy ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                    )} />
                    <span className="text-xs font-medium text-slate-600 dark:text-slate-300">
                        {isHealthy ? 'System Ready' : 'Dependency Alert'}
                    </span>
                </div>

                <div className="h-8 w-px bg-slate-200 mx-2 dark:bg-slate-700" />

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

                <Button variant="ghost" size="sm" className="w-9 h-9 p-0 rounded-full relative" aria-label="Notifications">
                    <Bell size={18} className="text-slate-600 dark:text-slate-300" />
                    <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white dark:border-slate-900" />
                </Button>
            </div>
        </header>
    );
};
