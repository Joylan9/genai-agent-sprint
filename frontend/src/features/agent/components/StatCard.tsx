import { cn } from '../../../shared/lib/utils';

interface StatCardProps {
    title: string;
    value: string;
    icon: any;
    color: string;
}

export const StatCard = ({ title, value, icon: Icon, color }: StatCardProps) => (
    <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-medium text-slate-500">{title}</span>
            <div className={cn("p-2 rounded-lg", color)}>
                <Icon size={20} className="text-white" />
            </div>
        </div>
        <div className="text-2xl font-bold text-slate-900 tracking-tight">{value}</div>
    </div>
);
