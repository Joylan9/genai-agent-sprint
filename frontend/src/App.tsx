import { Routes, Route } from 'react-router-dom';
import { Dashboard } from './pages/Dashboard';
import { AgentListPage } from './features/agent/pages/AgentListPage';
import { RunsListPage } from './pages/Runs';
import { RunDetailsPage } from './pages/RunDetails';
import { PlaygroundPage } from './pages/Playground';
import { AppShell } from './app/layout/AppShell';

const App = () => {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/agents" element={<AgentListPage />} />
        <Route path="/runs" element={<RunsListPage />} />
        <Route path="/runs/:id" element={<RunDetailsPage />} />
        <Route path="/execute" element={<PlaygroundPage />} />
      </Routes>
    </AppShell>
  );
};

export default App;