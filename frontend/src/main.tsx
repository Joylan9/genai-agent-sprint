import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.tsx';
import { AppProviders } from './app/providers/AppProviders';

async function enableMocking() {
  const useMsw = import.meta.env.VITE_USE_MSW === 'true';
  if (import.meta.env.MODE !== 'development' || !useMsw) {
    return;
  }

  const { worker } = await import('./mocks/browser');
  return worker.start({
    onUnhandledRequest: 'bypass',
  });
}

import { ErrorBoundary } from './app/errors/ErrorBoundary';

enableMocking().then(() => {
  createRoot(document.getElementById('root')!).render(
    <StrictMode>
      <ErrorBoundary>
        <AppProviders>
          <App />
        </AppProviders>
      </ErrorBoundary>
    </StrictMode>
  );
});
