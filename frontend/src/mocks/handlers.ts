import { delay, http, HttpResponse } from 'msw';

const API_BASE_URL = 'http://localhost:8000';

const agents: Array<{
    id: string;
    name: string;
    version: string;
    description?: string;
    status: string;
    created_at: string;
}> = [
    { id: '1', name: 'General Assistant', version: '1.0.0', status: 'active', created_at: new Date().toISOString() },
    { id: '2', name: 'Data Analyst', version: '1.1.0', status: 'active', created_at: new Date().toISOString() },
];

const runs: Array<{
    id: string;
    agent_id: string;
    status: string;
    started_at: string;
    completed_at?: string;
    result?: string;
}> = [];

export const handlers = [
    http.get(`${API_BASE_URL}/health`, async () => {
        await delay(200);
        return HttpResponse.json({
            status: 'ok',
            model: 'llama3:8b',
            version: '1.0.4-PROD',
        });
    }),

    http.get(`${API_BASE_URL}/ready`, async () => HttpResponse.json({
        status: 'ready',
        checks: { mongodb: 'ready', ollama: 'ready', redis: 'ready' },
    })),

    http.post(`${API_BASE_URL}/agent/run`, async ({ request }) => {
        await delay(900);
        const body = await request.json() as any;
        const requestId = `req_${Math.random().toString(36).slice(2, 11)}`;
        const startedAt = new Date().toISOString();
        const result = `Processed goal: ${body.goal}. This is a mocked response.`;

        runs.unshift({
            id: requestId,
            agent_id: body.session_id || 'default',
            status: 'completed',
            started_at: startedAt,
            completed_at: startedAt,
            result,
        });

        return HttpResponse.json({
            result,
            request_id: requestId,
        });
    }),

    http.get(`${API_BASE_URL}/traces/:id`, async ({ params }) => {
        const { id } = params;
        return HttpResponse.json({
            _id: 'mock_id',
            request_id: id,
            steps: [
                { name: 'Goal Analysis', status: 'completed' },
                { name: 'Tool Selection', status: 'completed' },
                { name: 'Execution', status: 'completed' },
            ],
            metadata: { duration_ms: 1250 },
        });
    }),

    http.get(`${API_BASE_URL}/api/agents`, ({ request }) => {
        const url = new URL(request.url);
        const q = (url.searchParams.get('q') || '').toLowerCase();
        const data = q
            ? agents.filter((agent) => agent.name.toLowerCase().includes(q))
            : agents;
        return HttpResponse.json(data);
    }),

    http.post(`${API_BASE_URL}/api/agents`, async ({ request }) => {
        const body = await request.json() as any;
        const newAgent = {
            id: `agent_${Math.random().toString(36).slice(2, 8)}`,
            name: body.name,
            version: body.version || '1.0.0',
            description: body.description || '',
            status: 'active',
            created_at: new Date().toISOString(),
        };
        agents.unshift(newAgent);
        return HttpResponse.json(newAgent, { status: 201 });
    }),

    http.get(`${API_BASE_URL}/api/runs`, ({ request }) => {
        const url = new URL(request.url);
        const q = (url.searchParams.get('q') || '').toLowerCase();
        const status = (url.searchParams.get('status') || 'all').toLowerCase();
        let data = [...runs];

        if (status !== 'all') {
            data = data.filter((run) => run.status.toLowerCase() === status);
        }

        if (q) {
            data = data.filter((run) =>
                run.id.toLowerCase().includes(q)
                || run.agent_id.toLowerCase().includes(q)
            );
        }

        return HttpResponse.json(data);
    }),
];
