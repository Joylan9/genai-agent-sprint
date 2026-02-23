import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Bug } from 'lucide-react';

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
    eventId: string | null;
}

export class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null,
        errorInfo: null,
        eventId: null
    };

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error, errorInfo: null, eventId: null };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        // Generate a pseudo-trace ID for reporting
        const eventId = `err_${Math.random().toString(36).substring(2, 9)}`;
        this.setState({ errorInfo, eventId });

        // In a real Sentry setup, this would be: Sentry.captureException(error)
        console.error(`[ErrorBoundary] Caught error (Event ID: ${eventId}):`, error, errorInfo);

        // Attempt telemetry beacon if supported
        if (window.__APP_CONFIG__?.TELEMETRY_ENDPOINT) {
            try {
                const payload = JSON.stringify({
                    type: 'UNHANDLED_REACT_ERROR',
                    message: error.message,
                    stack: errorInfo.componentStack,
                    eventId,
                    timestamp: new Date().toISOString()
                });
                navigator.sendBeacon(window.__APP_CONFIG__.TELEMETRY_ENDPOINT, payload);
            } catch (e) {
                // Suppress beacon failure inside error boundary
            }
        }
    }

    private handleReset = () => {
        this.setState({ hasError: false, error: null, errorInfo: null, eventId: null });
        window.location.reload();
    };

    public render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return this.props.fallback;
            }

            return (
                <div className="min-h-[400px] flex items-center justify-center p-6 bg-gray-50 rounded-lg border border-gray-200 m-4">
                    <div className="max-w-xl w-full text-center space-y-5">
                        <div className="mx-auto w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
                            <AlertTriangle className="w-8 h-8 text-red-600" />
                        </div>

                        <div className="space-y-2">
                            <h2 className="text-xl font-bold text-gray-900 tracking-tight">Something went wrong</h2>
                            <p className="text-gray-600 text-sm">
                                An unexpected error occurred in the application leading to a crash. Our engineers have been notified.
                            </p>
                        </div>

                        {this.state.eventId && (
                            <div className="inline-flex items-center space-x-2 bg-gray-100 px-3 py-1.5 rounded text-xs font-mono text-gray-500">
                                <Bug className="w-3.5 h-3.5" />
                                <span>Reference ID: {this.state.eventId}</span>
                            </div>
                        )}

                        <div className="pt-4 flex justify-center space-x-3 border-t border-gray-100">
                            <button
                                onClick={this.handleReset}
                                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
                            >
                                <RefreshCw className="mr-2 h-4 w-4" />
                                Reload Application
                            </button>
                        </div>

                        {import.meta.env.MODE === 'development' && this.state.error && (
                            <div className="mt-8 text-left bg-gray-900 rounded p-4 overflow-x-auto text-xs font-mono text-gray-300">
                                <p className="text-red-400 font-bold">{this.state.error.toString()}</p>
                                <pre className="mt-2 text-gray-400 opacity-80 whitespace-pre-wrap">
                                    {this.state.errorInfo?.componentStack}
                                </pre>
                            </div>
                        )}
                    </div>
                </div>
            );
        }

        return this.props.children;
    }
}
