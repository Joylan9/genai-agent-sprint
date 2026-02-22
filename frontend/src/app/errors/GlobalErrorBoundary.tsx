import { Component, type ErrorInfo, type ReactNode } from 'react';
import { Button } from '../../shared/ui/Button';
import { AlertCircle, RefreshCw, Home, ShieldAlert } from 'lucide-react';

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
}

export class GlobalErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null
    };

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('Uncaught error:', error, errorInfo);
        // TODO: Send to telemetry (Sentry)
    }

    private handleReset = () => {
        this.setState({ hasError: false, error: null });
        window.location.href = '/';
    };

    public render() {
        if (this.state.hasError) {
            if (this.props.fallback) return this.props.fallback;

            return (
                <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
                    <div className="max-w-md w-full bg-white rounded-2xl shadow-xl border border-slate-200 p-8 text-center animate-in fade-in zoom-in-95 duration-500">
                        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center text-red-600 mx-auto mb-6">
                            <ShieldAlert size={32} />
                        </div>

                        <h1 className="text-2xl font-bold text-slate-900 mb-2">Something went wrong</h1>
                        <p className="text-slate-500 mb-8 leading-relaxed">
                            The application encountered an unexpected error. Our systems have been notified and we're looking into it.
                        </p>

                        <div className="bg-slate-50 rounded-lg p-4 mb-8 text-left border border-slate-100">
                            <div className="flex items-center gap-2 text-red-700 font-mono text-xs font-bold mb-2 uppercase tracking-tight">
                                <AlertCircle size={14} />
                                <span>Error details</span>
                            </div>
                            <p className="text-xs text-slate-600 font-mono break-all leading-relaxed">
                                {this.state.error?.message || 'Unknown runtime error'}
                            </p>
                        </div>

                        <div className="flex flex-col gap-3">
                            <Button
                                onClick={() => window.location.reload()}
                                className="w-full flex items-center justify-center gap-2"
                            >
                                <RefreshCw size={18} />
                                <span>Reload Application</span>
                            </Button>
                            <Button
                                variant="ghost"
                                onClick={this.handleReset}
                                className="w-full flex items-center justify-center gap-2"
                            >
                                <Home size={18} />
                                <span>Back to Dashboard</span>
                            </Button>
                        </div>

                        <p className="mt-8 text-[10px] text-slate-400 font-medium">
                            AGENT_ENGINE_UI_ERR_HALT :: v1.0.4-PROD
                        </p>
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
