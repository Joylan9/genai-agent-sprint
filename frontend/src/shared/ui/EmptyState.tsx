import { type LucideIcon } from 'lucide-react';
import { Button } from './Button';
import { cn } from '../lib/utils';

interface EmptyStateProps {
    icon: LucideIcon;
    title: string;
    description: string;
    actionLabel?: string;
    onAction?: () => void;
    accentColor?: string;
    className?: string;
}

export const EmptyState = ({
    icon: Icon,
    title,
    description,
    actionLabel,
    onAction,
    accentColor = 'blue',
    className,
}: EmptyStateProps) => {
    const colorMap: Record<string, { bg: string; ring: string; icon: string; btn: string }> = {
        blue: { bg: 'bg-blue-50 dark:bg-blue-950/30', ring: 'ring-blue-200 dark:ring-blue-800', icon: 'text-blue-500', btn: 'bg-blue-600 hover:bg-blue-700' },
        purple: { bg: 'bg-purple-50 dark:bg-purple-950/30', ring: 'ring-purple-200 dark:ring-purple-800', icon: 'text-purple-500', btn: 'bg-purple-600 hover:bg-purple-700' },
        amber: { bg: 'bg-amber-50 dark:bg-amber-950/30', ring: 'ring-amber-200 dark:ring-amber-800', icon: 'text-amber-500', btn: 'bg-amber-600 hover:bg-amber-700' },
        green: { bg: 'bg-emerald-50 dark:bg-emerald-950/30', ring: 'ring-emerald-200 dark:ring-emerald-800', icon: 'text-emerald-500', btn: 'bg-emerald-600 hover:bg-emerald-700' },
    };

    const colors = colorMap[accentColor] || colorMap.blue;

    return (
        <div className={cn('flex flex-col items-center justify-center py-16 px-6', className)}>
            {/* Animated icon container */}
            <div className="relative mb-6">
                {/* Outer glow ring */}
                <div className={cn(
                    'absolute inset-0 rounded-full opacity-40 animate-ping',
                    colors.bg,
                )} style={{ animationDuration: '3s' }} />
                {/* Icon circle */}
                <div className={cn(
                    'relative w-20 h-20 rounded-full flex items-center justify-center ring-2',
                    colors.bg,
                    colors.ring,
                )} style={{ animation: 'float 4s ease-in-out infinite' }}>
                    <Icon size={36} className={colors.icon} strokeWidth={1.5} />
                </div>
            </div>

            <h3 className="text-lg font-semibold text-slate-700 dark:text-slate-200 mb-1.5 text-center">
                {title}
            </h3>
            <p className="text-sm text-slate-500 dark:text-slate-400 max-w-sm text-center leading-relaxed mb-5">
                {description}
            </p>

            {actionLabel && onAction && (
                <Button
                    onClick={onAction}
                    className={cn('text-white shadow-lg transition-transform hover:scale-105', colors.btn)}
                >
                    {actionLabel}
                </Button>
            )}

            {/* Float keyframe injection */}
            <style>{`
                @keyframes float {
                    0%, 100% { transform: translateY(0); }
                    50% { transform: translateY(-8px); }
                }
            `}</style>
        </div>
    );
};
