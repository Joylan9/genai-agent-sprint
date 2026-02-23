import { Skeleton } from './Skeleton';

interface TableSkeletonProps {
    rows?: number;
    cols?: number;
    hasHeader?: boolean;
}

export const TableSkeleton = ({ rows = 5, cols = 4, hasHeader = true }: TableSkeletonProps) => {
    return (
        <div className="w-full rounded-md border border-slate-200 bg-white overflow-hidden shadow-sm animate-in fade-in duration-300">
            {hasHeader && (
                <div className="border-b border-slate-200 bg-slate-50 p-4 flex gap-4">
                    {Array.from({ length: cols }).map((_, i) => (
                        <div key={`th-${i}`} className="flex-1">
                            <Skeleton className="h-5 w-24 bg-slate-300/60" />
                        </div>
                    ))}
                </div>
            )}
            <div className="divide-y divide-slate-100">
                {Array.from({ length: rows }).map((_, rowIndex) => (
                    <div key={`tr-${rowIndex}`} className="p-4 flex gap-4 items-center">
                        {Array.from({ length: cols }).map((_, colIndex) => (
                            <div key={`td-${rowIndex}-${colIndex}`} className="flex-1">
                                {colIndex === 0 ? (
                                    <div className="space-y-2">
                                        <Skeleton className="h-4 w-3/4" />
                                        <Skeleton className="h-3 w-1/2 opacity-60" />
                                    </div>
                                ) : (
                                    <Skeleton className={`h-4 w-${colIndex % 2 === 0 ? '1/2' : 'full'} opacity-80`} />
                                )}
                            </div>
                        ))}
                    </div>
                ))}
            </div>
        </div>
    );
};
