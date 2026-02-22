import { Layout } from 'lucide-react';

export const PageLoader = () => {
    return (
        <div className="fixed inset-0 bg-white/80 backdrop-blur-md z-[100] flex flex-col items-center justify-center animate-in fade-in duration-500">
            <div className="relative">
                <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center text-white shadow-xl shadow-blue-500/20 animate-bounce">
                    <Layout size={32} strokeWidth={2.5} />
                </div>
                <div className="absolute inset-0 rounded-2xl border-4 border-blue-600/30 animate-ping" />
            </div>
            <div className="mt-8 flex flex-col items-center gap-2">
                <h2 className="text-lg font-bold text-slate-900 tracking-tight">AgentEngine</h2>
                <div className="flex gap-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-600 animate-pulse [animation-delay:-0.3s]" />
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-600 animate-pulse [animation-delay:-0.15s]" />
                    <div className="w-1.5 h-1.5 rounded-full bg-blue-600 animate-pulse" />
                </div>
            </div>
        </div>
    );
};
