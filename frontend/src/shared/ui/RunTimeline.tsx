import { cn } from '../lib/utils';
import { Brain, Wrench, Sparkles, CheckCircle2, XCircle, Clock } from 'lucide-react';
import { useState } from 'react';

interface Observation {
    tool?: string;
    query?: string;
    response?: { status?: string; data?: any };
}

interface Latency {
    planner?: number;
    tool_wall_time?: number;
    synthesis?: number;
    total?: number;
}

interface RunTimelineProps {
    latency: Latency | null | undefined;
    observations?: Observation[];
    status?: string;
    className?: string;
}

interface Segment {
    label: string;
    phase: 'planner' | 'tool' | 'synthesis';
    duration: number;
    status: 'success' | 'error' | 'running' | 'queued';
    color: string;
    bgColor: string;
    icon: typeof Brain;
}

export const RunTimeline = ({ latency, observations = [], status, className }: RunTimelineProps) => {
    const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);

    if (!latency) return null;

    const total = latency.total || 0;
    if (total <= 0) return null;

    // Build segments
    const segments: Segment[] = [];

    // Planner
    if (latency.planner && latency.planner > 0) {
        segments.push({
            label: 'Planner',
            phase: 'planner',
            duration: latency.planner,
            status: 'success',
            color: 'text-blue-600',
            bgColor: 'bg-blue-500',
            icon: Brain,
        });
    }

    // Tools — split from observations if available
    const toolObs = observations.filter(o => o.tool);
    if (toolObs.length > 0 && latency.tool_wall_time && latency.tool_wall_time > 0) {
        const perTool = latency.tool_wall_time / toolObs.length;
        toolObs.forEach((obs) => {
            const obsStatus = obs.response?.status === 'success' ? 'success' as const
                : obs.response?.status === 'error' ? 'error' as const
                    : 'success' as const;
            segments.push({
                label: obs.tool || 'Tool',
                phase: 'tool',
                duration: perTool,
                status: obsStatus,
                color: 'text-amber-600',
                bgColor: obsStatus === 'error' ? 'bg-red-500' : 'bg-amber-500',
                icon: Wrench,
            });
        });
    } else if (latency.tool_wall_time && latency.tool_wall_time > 0) {
        segments.push({
            label: 'Tool Execution',
            phase: 'tool',
            duration: latency.tool_wall_time,
            status: 'success',
            color: 'text-amber-600',
            bgColor: 'bg-amber-500',
            icon: Wrench,
        });
    }

    // Synthesis
    if (latency.synthesis && latency.synthesis > 0) {
        segments.push({
            label: 'Synthesis',
            phase: 'synthesis',
            duration: latency.synthesis,
            status: status === 'failed' ? 'error' : 'success',
            color: 'text-purple-600',
            bgColor: 'bg-purple-500',
            icon: Sparkles,
        });
    }

    if (segments.length === 0) return null;

    return (
        <div className={cn('bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm p-5', className)}>
            <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-200 mb-4 flex items-center gap-2">
                <Clock size={14} className="text-blue-500" />
                Execution Timeline
                <span className="ml-auto text-xs font-mono text-slate-400">{total.toFixed(2)}s total</span>
            </h3>

            {/* Timeline bar */}
            <div className="relative">
                <div className="h-10 rounded-lg bg-slate-100 dark:bg-slate-800 overflow-hidden flex">
                    {segments.map((seg, i) => {
                        const widthPercent = Math.max((seg.duration / total) * 100, 4);
                        return (
                            <div
                                key={`${seg.label}-${i}`}
                                className={cn(
                                    'h-full relative flex items-center justify-center cursor-pointer transition-all duration-200 group',
                                    seg.bgColor,
                                    hoveredIndex === i ? 'opacity-100 brightness-110' : 'opacity-85',
                                    i === 0 && 'rounded-l-lg',
                                    i === segments.length - 1 && 'rounded-r-lg',
                                )}
                                style={{
                                    width: `${widthPercent}%`,
                                    animation: `timeline-grow 0.6s ease-out ${i * 0.15}s both`,
                                }}
                                onMouseEnter={() => setHoveredIndex(i)}
                                onMouseLeave={() => setHoveredIndex(null)}
                            >
                                {/* Icon inside bar */}
                                {widthPercent > 8 && (
                                    <seg.icon size={14} className="text-white/80" />
                                )}

                                {/* Tooltip */}
                                {hoveredIndex === i && (
                                    <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 z-30 pointer-events-none">
                                        <div className="bg-slate-900 text-white rounded-lg px-3 py-2 text-xs whitespace-nowrap shadow-xl border border-slate-700">
                                            <p className="font-semibold">{seg.label}</p>
                                            <p className="text-slate-300 mt-0.5">
                                                {seg.duration.toFixed(2)}s ({((seg.duration / total) * 100).toFixed(0)}%)
                                            </p>
                                            <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-slate-900" />
                                        </div>
                                    </div>
                                )}

                                {/* Separator */}
                                {i < segments.length - 1 && (
                                    <div className="absolute right-0 top-1 bottom-1 w-px bg-white/30" />
                                )}
                            </div>
                        );
                    })}
                </div>

                {/* Phase flow arrow indicators */}
                <div className="flex items-center justify-between mt-1 px-1">
                    {segments.map((seg, i) => {
                        const widthPercent = Math.max((seg.duration / total) * 100, 4);
                        return (
                            <div
                                key={`label-${i}`}
                                className="flex items-center gap-1 overflow-hidden"
                                style={{ width: `${widthPercent}%` }}
                            >
                                {seg.status === 'success' ? (
                                    <CheckCircle2 size={10} className="text-emerald-500 shrink-0" />
                                ) : seg.status === 'error' ? (
                                    <XCircle size={10} className="text-red-500 shrink-0" />
                                ) : null}
                                <span className="text-[10px] text-slate-500 dark:text-slate-400 font-medium truncate">
                                    {seg.label}
                                </span>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Legend */}
            <div className="flex flex-wrap gap-4 mt-4 pt-3 border-t border-slate-100 dark:border-slate-800">
                {[
                    { label: 'Planner', color: 'bg-blue-500' },
                    { label: 'Tools', color: 'bg-amber-500' },
                    { label: 'Synthesis', color: 'bg-purple-500' },
                ].map(item => (
                    <div key={item.label} className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
                        <div className={cn('w-2.5 h-2.5 rounded-sm', item.color)} />
                        {item.label}
                    </div>
                ))}
            </div>

            <style>{`
                @keyframes timeline-grow {
                    from { transform: scaleX(0); opacity: 0; }
                    to { transform: scaleX(1); opacity: 1; }
                }
            `}</style>
        </div>
    );
};
