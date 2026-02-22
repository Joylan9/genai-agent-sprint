import { Terminal, Search } from 'lucide-react';
import { useState, useEffect } from 'react';

export const CommandPalette = () => {
    const [isOpen, setIsOpen] = useState(false);

    useEffect(() => {
        const down = (e: KeyboardEvent) => {
            if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                setIsOpen((open) => !open);
            }
        };
        document.addEventListener('keydown', down);
        return () => document.removeEventListener('keydown', down);
    }, []);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh] px-4">
            <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-300" onClick={() => setIsOpen(false)} />

            <div className="w-full max-w-2xl bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden relative animate-in slide-in-from-top-4 duration-300">
                <div className="flex items-center px-4 py-3 border-b border-slate-100">
                    <Search className="mr-3 text-slate-400" size={20} />
                    <input
                        autoFocus
                        className="flex-1 bg-transparent border-none outline-none text-slate-900 placeholder:text-slate-400 text-base"
                        placeholder="Type a command or search..."
                    />
                    <div className="flex items-center gap-1 border border-slate-200 rounded px-1.5 py-0.5 bg-slate-50 text-[10px] text-slate-400 ml-2">
                        <span>ESC</span>
                    </div>
                </div>

                <div className="p-2 max-h-[400px] overflow-auto">
                    <div className="px-3 py-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                        Recent Searches
                    </div>
                    <div className="space-y-1">
                        {[
                            { icon: Terminal, label: 'Run Health Check', category: 'System', shortcut: '⌘H' },
                            { icon: Search, label: 'Search Agents', category: 'Navigation', shortcut: '⌘S' },
                        ].map((item, i) => (
                            <button key={i} className="w-full flex items-center justify-between p-3 rounded-xl hover:bg-slate-50 transition-colors group">
                                <div className="flex items-center gap-3">
                                    <div className="p-2 rounded-lg bg-slate-100 text-slate-500 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                                        <item.icon size={18} />
                                    </div>
                                    <div className="text-left">
                                        <p className="text-sm font-semibold text-slate-900">{item.label}</p>
                                        <p className="text-[10px] text-slate-400">{item.category}</p>
                                    </div>
                                </div>
                                <span className="text-[10px] font-mono text-slate-400">{item.shortcut}</span>
                            </button>
                        ))}
                    </div>
                </div>

                <div className="p-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
                            <span className="border border-slate-200 bg-white rounded-md px-1 py-0.5 text-slate-700 font-mono">↑↓</span>
                            <span>to navigate</span>
                        </div>
                        <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
                            <span className="border border-slate-200 bg-white rounded-md px-1 py-0.5 text-slate-700 font-mono">ENTER</span>
                            <span>to select</span>
                        </div>
                    </div>
                    <div className="flex items-center gap-1 text-[10px] text-slate-400 italic">
                        <span>AGENT_CMDP_v1.0</span>
                    </div>
                </div>
            </div>
        </div>
    );
};
