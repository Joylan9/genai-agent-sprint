import type { ReactNode } from 'react';
import { cn } from '../lib/utils';

interface BadgeProps {
    children: ReactNode;
    variant?: 'blue' | 'green' | 'red' | 'yellow' | 'slate';
    className?: string;
}

export const Badge = ({ children, variant = 'slate', className }: BadgeProps) => {
    const variants = {
        blue: 'bg-blue-50 text-blue-700 border-blue-200',
        green: 'bg-green-50 text-green-700 border-green-200',
        red: 'bg-red-50 text-red-700 border-red-200',
        yellow: 'bg-yellow-50 text-yellow-700 border-yellow-200',
        slate: 'bg-slate-50 text-slate-700 border-slate-200',
    };

    return (
        <span className={cn(
            "px-2 py-0.5 rounded text-[10px] font-bold border uppercase tracking-wider",
            variants[variant],
            className
        )}>
            {children}
        </span>
    );
};
