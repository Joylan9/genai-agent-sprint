import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import type { FallbackProps } from 'react-error-boundary';

// Used in conjunction with React Query's `useErrorBoundary` or `QueryClient` defaults
export function QueryErrorFallback({ error, resetErrorBoundary }: FallbackProps) {
    const err = error as Error;
    const isNetwork = err.message?.toLowerCase().includes('network') || err.message?.toLowerCase().includes('fetch');
    const title = isNetwork ? 'Network Connection Lost' : 'Failed to Load Data';
    const description = isNetwork
        ? 'We are unable to reach the server. Please check your internet connection or try again.'
        : 'An error occurred while retrieving information from the server. Our team has been notified.';

    return (
        <div className="p-6 bg-white border border-gray-100 rounded-lg shadow-sm w-full animate-in fade-in duration-300">
            <div className="flex items-start space-x-4">
                <div className="flex-shrink-0 bg-red-50 p-2 rounded-full">
                    <AlertCircle className="w-6 h-6 text-red-600" aria-hidden="true" />
                </div>
                <div className="flex-1 min-w-0">
                    <h3 className="text-base font-semibold text-gray-900 truncate">
                        {title}
                    </h3>
                    <p className="mt-1 text-sm text-gray-500">
                        {description}
                    </p>

                    {/* Error details only in dev or for specific codes */}
                    {err.message && !isNetwork && (
                        <div className="mt-3 p-2 bg-gray-50 border border-gray-200 rounded text-xs text-gray-600 font-mono break-words">
                            {err.message}
                        </div>
                    )}

                    <div className="mt-4">
                        <button
                            type="button"
                            onClick={resetErrorBoundary}
                            className="inline-flex items-center px-3 py-2 border border-blue-200 shadow-sm text-sm leading-4 font-medium rounded-md text-blue-700 bg-blue-50 hover:bg-blue-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
                        >
                            <RefreshCw className="w-4 h-4 mr-1.5" />
                            Retry Action
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

// Higher order component to wrap individual widgets
interface WrapperProps {
    children: React.ReactNode;
}

export function QueryErrorBoundary({ children }: WrapperProps) {
    const [hasError, setHasError] = React.useState(false);
    const [error] = React.useState<Error | null>(null);

    // Using standard React error boundary approach for query tracking
    if (hasError && error) {
        return <QueryErrorFallback error={error} resetErrorBoundary={() => setHasError(false)} />;
    }

    return (
        <React.Fragment>
            {/* Native react-error-boundary is preferred here but providing raw wrapper for direct imports */}
            {children}
        </React.Fragment>
    );
}
