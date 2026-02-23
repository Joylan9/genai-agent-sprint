import { Search, Terminal } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

export const CommandPalette = () => {
    const navigate = useNavigate();
    const [isOpen, setIsOpen] = useState(false);
    const [query, setQuery] = useState('');

    useEffect(() => {
        const down = (event: KeyboardEvent) => {
            if (event.key === 'k' && (event.metaKey || event.ctrlKey)) {
                event.preventDefault();
                setIsOpen((open) => !open);
            }
            if (event.key === 'Escape') {
                setIsOpen(false);
            }
        };

        const openHandler = () => setIsOpen(true);
        document.addEventListener('keydown', down);
        window.addEventListener('open-command-palette', openHandler);
        return () => {
            document.removeEventListener('keydown', down);
            window.removeEventListener('open-command-palette', openHandler);
        };
    }, []);

    const executeSearch = () => {
        const term = query.trim();
        if (!term) return;
        navigate(`/agents?q=${encodeURIComponent(term)}`);
        setIsOpen(false);
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh] px-4">
            <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-300" onClick={() => setIsOpen(false)} />

            <div className="w-full max-w-2xl bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden relative animate-in slide-in-from-top-4 duration-300 dark:bg-slate-900 dark:border-slate-800">
                <div className="flex items-center px-4 py-3 border-b border-slate-100 dark:border-slate-800">
                    <Search className="mr-3 text-slate-400" size={20} />
                    <input
                        autoFocus
                        value={query}
                        onChange={(event) => setQuery(event.target.value)}
                        onKeyDown={(event) => {
                            if (event.key === 'Enter') {
                                event.preventDefault();
                                executeSearch();
                            }
                        }}
                        className="flex-1 bg-transparent border-none outline-none text-slate-900 placeholder:text-slate-400 text-base dark:text-slate-100"
                        placeholder="Type an agent name and press Enter..."
                    />
                    <div className="flex items-center gap-1 border border-slate-200 rounded px-1.5 py-0.5 bg-slate-50 text-[10px] text-slate-400 ml-2 dark:bg-slate-800 dark:border-slate-700">
                        <span>ESC</span>
                    </div>
                </div>

                <div className="p-2 max-h-[400px] overflow-auto">
                    <div className="px-3 py-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                        Quick Actions
                    </div>
                    <div className="space-y-1">
                        <button
                            onClick={() => {
                                navigate('/status');
                                setIsOpen(false);
                            }}
                            className="w-full flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 transition-colors group dark:hover:bg-slate-800"
                        >
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-slate-100 text-slate-500 group-hover:bg-blue-600 group-hover:text-white transition-colors dark:bg-slate-800">
                                    <Terminal size={18} />
                                </div>
                                <div className="text-left">
                                    <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">Open System Status</p>
                                    <p className="text-[10px] text-slate-400">Navigation</p>
                                </div>
                            </div>
                            <span className="text-[10px] font-mono text-slate-400">Ctrl+K</span>
                        </button>
                        <button
                            onClick={executeSearch}
                            className="w-full flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 transition-colors group dark:hover:bg-slate-800"
                        >
                            <div className="flex items-center gap-3">
                                <div className="p-2 rounded-lg bg-slate-100 text-slate-500 group-hover:bg-blue-600 group-hover:text-white transition-colors dark:bg-slate-800">
                                    <Search size={18} />
                                </div>
                                <div className="text-left">
                                    <p className="text-sm font-semibold text-slate-900 dark:text-slate-100">Search Agent Directory</p>
                                    <p className="text-[10px] text-slate-400">Navigation</p>
                                </div>
                            </div>
                            <span className="text-[10px] font-mono text-slate-400">Enter</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};
