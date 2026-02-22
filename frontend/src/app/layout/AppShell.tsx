import type { ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { TopNav } from './TopNav';
import { CommandPalette } from './CommandPalette';

interface AppShellProps {
    children: ReactNode;
}

export const AppShell = ({ children }: AppShellProps) => {
    return (
        <div className="flex h-screen bg-slate-50 overflow-hidden font-sans">
            {/* Persistent Sidebar */}
            <Sidebar />

            {/* Vertical Content Stack */}
            <div className="flex-1 flex flex-col min-w-0 relative">
                {/* Persistent Topbar */}
                <TopNav />

                {/* Scrollable Main Content */}
                <main className="flex-1 overflow-auto">
                    <div className="p-8 pb-16 max-w-7xl mx-auto">
                        {children}
                    </div>
                </main>

                {/* Global Overlays */}
                <CommandPalette />

                {/* Subtle Background Decoration */}
                <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/5 blur-[120px] rounded-full -mr-48 -mt-48 pointer-events-none" />
                <div className="absolute bottom-0 left-0 w-64 h-64 bg-indigo-500/5 blur-[100px] rounded-full -ml-32 -mb-32 pointer-events-none" />
            </div>
        </div>
    );
};
