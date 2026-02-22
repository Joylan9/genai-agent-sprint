import { cn } from '../lib/utils';

interface InlineSpinnerProps {
    size?: 'sm' | 'md' | 'lg';
    className?: string;
}

export const InlineSpinner = ({ size = 'md', className }: InlineSpinnerProps) => {
    const sizeClasses = {
        sm: 'w-4 h-4 border-2',
        md: 'w-6 h-6 border-2',
        lg: 'w-8 h-8 border-3',
    };

    return (
        <div
            className={cn(
                "rounded-full border-blue-600/20 border-t-blue-600 animate-spin transition-all",
                sizeClasses[size],
                className
            )}
        />
    );
};
