import { Search, Bell, Command, Sun } from 'lucide-react';
import { Button } from '../../shared/ui/Button';
import { useHealth } from '../../features/agent/hooks/useAgent';

export const TopNav = () => {
    const { data: health } = useHealth();
    const isHealthy = health?.status === 'ok';

    return (
        <header className="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between sticky top-0 z-40">
            {/* Search Trigger */}
            <div className="flex-1 max-w-xl">
                <div className="relative group">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 group-hover:text-blue-500 transition-colors" size={18} />
                    <div className="w-64 pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-500 flex items-center justify-between cursor-pointer hover:bg-white hover:border-slate-300 transition-all">
                        <span>Search agents...</span>
                        <div className="flex items-center gap-1 border border-slate-200 rounded px-1.5 py-0.5 bg-white text-[10px] text-slate-400">
                            <Command size={10} />
                            <span>K</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-4">
                {/* System Status Indicator */}
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-50 border border-slate-100">
                    <span className={cn(
                        "h-2 w-2 rounded-full",
                        isHealthy ? "bg-green-500 animate-pulse" : "bg-red-500"
                    )} />
                    <span className="text-xs font-medium text-slate-600">
                        {isHealthy ? "System Ready" : "Dependency Alert"}
                    </span>
                </div>

                <div className="h-8 w-px bg-slate-200 mx-2" />

                <Button variant="ghost" size="sm" className="w-9 h-9 p-0 rounded-full">
                    <Sun size={18} className="text-slate-600" />
                </Button>

                <Button variant="ghost" size="sm" className="w-9 h-9 p-0 rounded-full relative">
                    <Bell size={18} className="text-slate-600" />
                    <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-white" />
                </Button>
            </div>
        </header>
    );
};

// Helper for conditional classes since we are in a new file
function cn(...inputs: any[]) {
    return inputs.filter(Boolean).join(' ');
}
