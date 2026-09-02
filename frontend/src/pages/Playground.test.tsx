import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act, fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { PlaygroundPage, QUEUED_STUCK_TIMEOUT_MS } from './Playground';
import { agentClient } from '../features/agent/api/agentClient';

vi.mock('../features/agent/api/agentClient', () => ({
    agentClient: {
        getRunStreamUrl: vi.fn(() => 'http://localhost:8000/api/runs/run-123/stream'),
        pollRunStatus: vi.fn(),
        submitRun: vi.fn(),
    },
}));

vi.mock('../features/agent/hooks/useAgent', () => ({
    useAgents: () => ({ data: [] }),
    useHealth: () => ({ data: { status: 'ok' }, isError: false }),
}));

vi.mock('../app/telemetry/tracker', () => ({
    trackEvent: vi.fn(),
}));

class MockEventSource {
    url: string;
    onerror: (() => void) | null = null;

    constructor(url: string) {
        this.url = url;
    }

    addEventListener = vi.fn();
    close = vi.fn();
}

describe('PlaygroundPage', () => {
    beforeEach(() => {
        vi.useFakeTimers();
        vi.stubGlobal('EventSource', MockEventSource);
        vi.mocked(agentClient.submitRun).mockResolvedValue({ run_id: 'run-123', status: 'queued' });
    });

    afterEach(() => {
        vi.clearAllTimers();
        vi.useRealTimers();
        vi.unstubAllGlobals();
        vi.clearAllMocks();
    });

    it('shows a worker availability warning when a run stays queued', async () => {
        render(
            <MemoryRouter initialEntries={['/execute']}>
                <PlaygroundPage />
            </MemoryRouter>,
        );

        const goalInput = screen.getByPlaceholderText(/enter a goal for the agent/i);
        fireEvent.change(goalInput, { target: { value: 'define AIML' } });
        fireEvent.keyDown(goalInput, { key: 'Enter', code: 'Enter', charCode: 13 });

        await act(async () => {
            await Promise.resolve();
        });

        expect(agentClient.submitRun).toHaveBeenCalledWith({
            session_id: expect.stringMatching(/^session_/),
            goal: 'define AIML',
            agent_id: undefined,
        });

        act(() => {
            vi.advanceTimersByTime(QUEUED_STUCK_TIMEOUT_MS);
        });

        expect(
            screen.getByText(/start the celery worker, then submit the question again/i),
        ).toBeInTheDocument();
    });
});
