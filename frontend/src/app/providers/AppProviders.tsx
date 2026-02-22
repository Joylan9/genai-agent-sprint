import React, { type ReactNode } from 'react';
import { QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { queryClient } from '../queryClient';
import { GlobalErrorBoundary } from '../errors/GlobalErrorBoundary';
import { AuthProvider } from './AuthProvider';
import { FeatureFlagProvider } from './FeatureFlagProvider';

interface AppProvidersProps {
    children: ReactNode;
}

export const AppProviders: React.FC<AppProvidersProps> = ({ children }) => {
    return (
        <GlobalErrorBoundary>
            <QueryClientProvider client={queryClient}>
                <AuthProvider>
                    <FeatureFlagProvider>
                        <BrowserRouter>
                            {children}
                        </BrowserRouter>
                    </FeatureFlagProvider>
                </AuthProvider>
            </QueryClientProvider>
        </GlobalErrorBoundary>
    );
};
