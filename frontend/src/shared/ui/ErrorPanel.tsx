import { useState } from 'react';
import {
    AlertTriangle, ChevronDown, ChevronUp,
    Lightbulb, RefreshCw, ExternalLink, XCircle,
} from 'lucide-react';
import { Button } from './Button';
import { cn } from '../lib/utils';

interface ErrorPanelProps {
    error: string;
    goal?: string;
    onRetry?: () => void;
    className?: string;
}

/* ── Smart fix suggestions based on error content ── */
function getSuggestions(error: string): { text: string; icon: typeof Lightbulb }[] {
    const lower = error.toLowerCase();
    const suggestions: { text: string; icon: typeof Lightbulb }[] = [];

    if (lower.includes('timeout') || lower.includes('timed out'))
        suggestions.push({ text: 'Increase TIMEOUT_SECONDS in .env or simplify the goal', icon: Lightbulb });
    if (lower.includes('ollama') || lower.includes('llm') || lower.includes('connection refused'))
        suggestions.push({ text: 'Check that Ollama is running: ollama serve', icon: Lightbulb });
    if (lower.includes('401') || lower.includes('unauthorized') || lower.includes('auth'))
        suggestions.push({ text: 'Re-authenticate or verify API_KEY matches between frontend and backend', icon: Lightbulb });
    if (lower.includes('rate limit') || lower.includes('429') || lower.includes('too many'))
        suggestions.push({ text: 'Wait a moment and try again — the API rate limit was exceeded', icon: Lightbulb });
    if (lower.includes('mongo') || lower.includes('database'))
        suggestions.push({ text: 'Verify MongoDB is online: docker compose up -d mongodb', icon: Lightbulb });
    if (lower.includes('redis') || lower.includes('celery'))
        suggestions.push({ text: 'Ensure Redis is running: docker compose up -d redis', icon: Lightbulb });
    if (lower.includes('not found') || lower.includes('404'))
        suggestions.push({ text: 'The requested resource may have been deleted or never existed', icon: Lightbulb });

    if (suggestions.length === 0)
        suggestions.push({ text: 'Check backend logs for the full stack trace', icon: Lightbulb });

    return suggestions;
}

function categorizeError(error: string): { what: string; why: string } {
    const lower = error.toLowerCase();

    if (lower.includes('timeout'))
        return { what: 'Execution Timeout', why: 'The agent took longer than the allowed time limit to produce a response.' };
    if (lower.includes('ollama') || lower.includes('connection refused'))
        return { what: 'LLM Service Unreachable', why: 'The language model backend (Ollama) could not be reached.' };
    if (lower.includes('401') || lower.includes('unauthorized'))
        return { what: 'Authentication Failed', why: 'The request lacked valid credentials or the API key is incorrect.' };
    if (lower.includes('rate limit') || lower.includes('429'))
        return { what: 'Rate Limit Exceeded', why: 'Too many requests were sent in a short period.' };
    if (lower.includes('mongo'))
        return { what: 'Database Error', why: 'MongoDB encountered an error while processing the request.' };

    return { what: 'Execution Failed', why: error.slice(0, 200) || 'An unexpected error occurred during agent execution.' };
}

export const ErrorPanel = ({ error, goal, onRetry, className }: ErrorPanelProps) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const { what, why } = categorizeError(error);
    const suggestions = getSuggestions(error);

    return (
        <div className={cn(
            'rounded-xl border border-red-200 dark:border-red-900/50 overflow-hidden shadow-sm',
            className,
        )}>
            {/* Header */}
            <div className="bg-gradient-to-r from-red-600 to-rose-600 px-5 py-3.5 flex items-center gap-3">
                <div className="bg-white/20 rounded-lg p-1.5">
                    <XCircle size={20} className="text-white" />
                </div>
                <div className="flex-1">
                    <h3 className="text-white font-semibold text-sm">{what}</h3>
                    <p className="text-red-100 text-xs mt-0.5">This run did not complete successfully</p>
                </div>
                {onRetry && (
                    <Button
                        size="sm"
                        onClick={onRetry}
                        className="bg-white/20 hover:bg-white/30 text-white border-0 backdrop-blur-sm text-xs"
                    >
                        <RefreshCw size={14} className="mr-1.5" />
                        Retry
                    </Button>
                )}
            </div>

            {/* Body */}
            <div className="bg-white dark:bg-slate-900 p-5 space-y-4">
                {/* Why */}
                <div>
                    <p className="text-[10px] font-bold uppercase tracking-widest text-red-500 mb-1.5">Why it failed</p>
                    <p className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">{why}</p>
                </div>

                {/* Goal context */}
                {goal && (
                    <div className="bg-slate-50 dark:bg-slate-800 rounded-lg px-4 py-2.5 border border-slate-200 dark:border-slate-700">
                        <p className="text-[10px] font-bold uppercase tracking-widest text-slate-400 mb-1">Original Goal</p>
                        <p className="text-sm text-slate-600 dark:text-slate-300">{goal}</p>
                    </div>
                )}

                {/* Suggestions */}
                <div>
                    <p className="text-[10px] font-bold uppercase tracking-widest text-amber-600 mb-2">Suggested Fixes</p>
                    <div className="space-y-2">
                        {suggestions.map((s, i) => (
                            <div
                                key={i}
                                className="flex items-start gap-2.5 text-sm text-slate-600 dark:text-slate-400 bg-amber-50 dark:bg-amber-950/20 border border-amber-100 dark:border-amber-900/30 rounded-lg px-3.5 py-2.5"
                            >
                                <Lightbulb size={14} className="text-amber-500 mt-0.5 shrink-0" />
                                <span>{s.text}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Raw error (collapsible) */}
                <div className="border-t border-slate-100 dark:border-slate-800 pt-3">
                    <button
                        onClick={() => setIsExpanded(!isExpanded)}
                        className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 transition-colors"
                    >
                        {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                        {isExpanded ? 'Hide' : 'Show'} raw error details
                    </button>
                    {isExpanded && (
                        <pre className="mt-2 bg-slate-900 text-slate-300 rounded-lg p-4 text-xs font-mono overflow-x-auto max-h-48 border border-slate-800">
                            {error}
                        </pre>
                    )}
                </div>

                {/* System Status link */}
                <div className="flex items-center gap-2 text-xs text-slate-400">
                    <AlertTriangle size={12} />
                    <span>Persistent errors? Check</span>
                    <a href="/status" className="text-blue-500 hover:text-blue-400 flex items-center gap-0.5">
                        System Status <ExternalLink size={10} />
                    </a>
                </div>
            </div>
        </div>
    );
};
