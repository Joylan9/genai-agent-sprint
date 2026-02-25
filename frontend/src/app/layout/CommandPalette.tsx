import {
    Search, Bot, Play, BarChart3, Activity, Settings, Terminal,
    LayoutDashboard, Users, Keyboard, ArrowRight,
} from 'lucide-react';
import { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { cn } from '../../shared/lib/utils';

interface CommandItem {
    id: string;
    label: string;
    description: string;
    icon: typeof Search;
    shortcut?: string;
    category: 'navigation' | 'action' | 'search';
    action: () => void;
}

export const CommandPalette = () => {
    const navigate = useNavigate();
    const [isOpen, setIsOpen] = useState(false);
    const [query, setQuery] = useState('');
    const [selectedIndex, setSelectedIndex] = useState(0);
    const inputRef = useRef<HTMLInputElement>(null);
    const listRef = useRef<HTMLDivElement>(null);

    // All available commands
    const allCommands: CommandItem[] = useMemo(() => [
        // Navigation
        { id: 'dashboard', label: 'Dashboard', description: 'Overview & stats', icon: LayoutDashboard, shortcut: 'D', category: 'navigation' as const, action: () => navigate('/') },
        { id: 'agents', label: 'Agent Directory', description: 'Manage AI agents', icon: Bot, shortcut: 'A', category: 'navigation' as const, action: () => navigate('/agents') },
        { id: 'runs', label: 'Run History', description: 'View execution traces', icon: Activity, shortcut: 'R', category: 'navigation' as const, action: () => navigate('/runs') },
        { id: 'playground', label: 'Playground', description: 'Execute agent goals', icon: Play, shortcut: 'P', category: 'navigation' as const, action: () => navigate('/execute') },
        { id: 'evals', label: 'Evaluation Lab', description: 'Benchmark & test agents', icon: BarChart3, shortcut: 'E', category: 'navigation' as const, action: () => navigate('/eval') },
        { id: 'status', label: 'System Status', description: 'Health & diagnostics', icon: Terminal, category: 'navigation' as const, action: () => navigate('/status') },
        // Actions
        { id: 'create-agent', label: 'Create Agent', description: 'Register a new AI agent', icon: Users, category: 'action' as const, action: () => navigate('/agents?create=1') },
        { id: 'run-agent', label: 'Run Agent', description: 'Open playground & execute', icon: Play, category: 'action' as const, action: () => navigate('/execute') },
        { id: 'run-evals', label: 'Run Test Suite', description: 'Execute evaluation benchmark', icon: BarChart3, category: 'action' as const, action: () => navigate('/eval?run=1') },
        { id: 'settings', label: 'Settings', description: 'Configuration & preferences', icon: Settings, category: 'action' as const, action: () => navigate('/status') },
    ], [navigate]);

    // Fuzzy search filter
    const filtered = useMemo(() => {
        const q = query.toLowerCase().trim();
        if (!q) return allCommands;
        return allCommands.filter(cmd =>
            cmd.label.toLowerCase().includes(q) ||
            cmd.description.toLowerCase().includes(q) ||
            cmd.category.includes(q)
        );
    }, [query, allCommands]);

    // Group by category
    const grouped = useMemo(() => {
        const nav = filtered.filter(c => c.category === 'navigation');
        const act = filtered.filter(c => c.category === 'action');
        const groups: { label: string; items: CommandItem[] }[] = [];
        if (nav.length) groups.push({ label: 'Navigation', items: nav });
        if (act.length) groups.push({ label: 'Actions', items: act });
        return groups;
    }, [filtered]);

    // Reset selection when query changes
    useEffect(() => { setSelectedIndex(0); }, [query]);

    // Ctrl+K listener + Global shortcuts
    useEffect(() => {
        const down = (e: KeyboardEvent) => {
            // Ctrl+K toggle
            if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                setIsOpen(o => !o);
                setQuery('');
                setSelectedIndex(0);
                return;
            }
            // ESC close
            if (e.key === 'Escape' && isOpen) {
                setIsOpen(false);
                return;
            }

            // Global shortcuts (only when not in input/textarea)
            const tag = (e.target as HTMLElement)?.tagName;
            if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
            if (e.metaKey || e.ctrlKey || e.altKey) return;

            const map: Record<string, string> = { r: '/execute', a: '/agents', e: '/eval', d: '/' };
            if (map[e.key]) {
                e.preventDefault();
                navigate(map[e.key]);
            }
        };

        const openHandler = () => {
            setIsOpen(true);
            setQuery('');
            setSelectedIndex(0);
        };

        document.addEventListener('keydown', down);
        window.addEventListener('open-command-palette', openHandler);
        return () => {
            document.removeEventListener('keydown', down);
            window.removeEventListener('open-command-palette', openHandler);
        };
    }, [isOpen, navigate]);

    // Keyboard navigation within palette
    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            setSelectedIndex(i => Math.min(i + 1, filtered.length - 1));
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            setSelectedIndex(i => Math.max(i - 1, 0));
        } else if (e.key === 'Enter') {
            e.preventDefault();
            const item = filtered[selectedIndex];
            if (item) {
                item.action();
                setIsOpen(false);
                setQuery('');
            }
        }
    };

    // Scroll selected item into view
    useEffect(() => {
        const el = listRef.current?.querySelector(`[data-index="${selectedIndex}"]`);
        el?.scrollIntoView({ block: 'nearest' });
    }, [selectedIndex]);

    if (!isOpen) return null;

    let flatIndex = -1;

    return (
        <div className="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh] px-4">
            {/* Backdrop */}
            <div
                className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm"
                style={{ animation: 'fadeIn 0.15s ease-out' }}
                onClick={() => setIsOpen(false)}
            />

            {/* Palette */}
            <div
                className="w-full max-w-[640px] bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 overflow-hidden relative"
                style={{ animation: 'slideDown 0.2s ease-out' }}
            >
                {/* Search input */}
                <div className="flex items-center gap-3 px-5 py-3.5 border-b border-slate-100 dark:border-slate-800">
                    <Search size={18} className="text-slate-400 shrink-0" />
                    <input
                        ref={inputRef}
                        id="command-search"
                        autoFocus
                        value={query}
                        onChange={e => setQuery(e.target.value)}
                        onKeyDown={handleKeyDown}
                        className="flex-1 bg-transparent border-none outline-none text-slate-900 dark:text-slate-100 placeholder:text-slate-400 text-[15px]"
                        placeholder="Search commands, pages, actions..."
                    />
                    <kbd className="hidden sm:inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-[10px] text-slate-400 font-mono">
                        ESC
                    </kbd>
                </div>

                {/* Results */}
                <div ref={listRef} className="max-h-[360px] overflow-auto p-2">
                    {grouped.length === 0 ? (
                        <div className="py-12 text-center text-slate-400">
                            <Search size={32} className="mx-auto mb-3 opacity-40" />
                            <p className="text-sm">No results for "{query}"</p>
                        </div>
                    ) : (
                        grouped.map(group => (
                            <div key={group.label}>
                                <div className="px-3 py-2 text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">
                                    {group.label}
                                </div>
                                <div className="space-y-0.5">
                                    {group.items.map(item => {
                                        flatIndex++;
                                        const idx = flatIndex;
                                        return (
                                            <button
                                                key={item.id}
                                                data-index={idx}
                                                onClick={() => {
                                                    item.action();
                                                    setIsOpen(false);
                                                    setQuery('');
                                                }}
                                                onMouseEnter={() => setSelectedIndex(idx)}
                                                className={cn(
                                                    'w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-100 group',
                                                    idx === selectedIndex
                                                        ? 'bg-blue-50 dark:bg-blue-950/40'
                                                        : 'hover:bg-slate-50 dark:hover:bg-slate-800/50',
                                                )}
                                            >
                                                <div className={cn(
                                                    'p-2 rounded-lg transition-colors',
                                                    idx === selectedIndex
                                                        ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20'
                                                        : 'bg-slate-100 dark:bg-slate-800 text-slate-500',
                                                )}>
                                                    <item.icon size={16} />
                                                </div>
                                                <div className="flex-1 text-left min-w-0">
                                                    <p className={cn(
                                                        'text-sm font-medium truncate',
                                                        idx === selectedIndex
                                                            ? 'text-blue-700 dark:text-blue-300'
                                                            : 'text-slate-800 dark:text-slate-200',
                                                    )}>
                                                        {item.label}
                                                    </p>
                                                    <p className="text-[11px] text-slate-400 truncate">{item.description}</p>
                                                </div>
                                                {item.shortcut && (
                                                    <kbd className="hidden sm:inline-flex px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-[10px] text-slate-400 font-mono">
                                                        {item.shortcut}
                                                    </kbd>
                                                )}
                                                {idx === selectedIndex && (
                                                    <ArrowRight size={14} className="text-blue-500 shrink-0" />
                                                )}
                                            </button>
                                        );
                                    })}
                                </div>
                            </div>
                        ))
                    )}
                </div>

                {/* Footer */}
                <div className="px-4 py-2.5 border-t border-slate-100 dark:border-slate-800 flex items-center gap-4 text-[10px] text-slate-400">
                    <span className="flex items-center gap-1">
                        <Keyboard size={10} />
                        <kbd className="font-mono">↑↓</kbd> navigate
                    </span>
                    <span className="flex items-center gap-1">
                        <kbd className="font-mono">↵</kbd> select
                    </span>
                    <span className="flex items-center gap-1">
                        <kbd className="font-mono">esc</kbd> close
                    </span>
                    <span className="ml-auto flex items-center gap-1">
                        Shortcuts: <kbd className="font-mono">R</kbd> run <kbd className="font-mono">A</kbd> agents <kbd className="font-mono">E</kbd> evals
                    </span>
                </div>
            </div>

            <style>{`
                @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
                @keyframes slideDown { from { opacity: 0; transform: translateY(-12px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
            `}</style>
        </div>
    );
};
