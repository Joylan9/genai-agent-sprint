import { Routes, Route } from 'react-router-dom';
import { Dashboard } from './pages/Dashboard';
import { AgentListPage } from './features/agent/pages/AgentListPage';
import { AgentDetailPage } from './pages/AgentDetailPage';
import { RunsListPage } from './pages/Runs';
import { RunDetailsPage } from './pages/RunDetails';
import { PlaygroundPage } from './pages/Playground';
import { LoginPage } from './pages/LoginPage';
import { ForgotPasswordPage } from './pages/ForgotPasswordPage';
import { EvalPage } from './pages/EvalPage';
import { AppShell } from './app/layout/AppShell';
import { SystemStatusPage } from './app/monitoring/SystemStatusPage';
import { ProtectedRoute } from './app/auth/ProtectedRoute';

const App = () => {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route
        path="/*"
        element={
          <ProtectedRoute>
            <AppShell>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/agents" element={<AgentListPage />} />
                <Route path="/agents/:id" element={<AgentDetailPage />} />
                <Route path="/runs" element={<RunsListPage />} />
                <Route path="/runs/:id" element={<RunDetailsPage />} />
                <Route path="/execute" element={<PlaygroundPage />} />
                <Route path="/eval" element={<EvalPage />} />
                <Route path="/status" element={<SystemStatusPage />} />
              </Routes>
            </AppShell>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
};

export default App;
