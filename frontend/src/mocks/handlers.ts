import { http, HttpResponse, delay } from 'msw';

const API_BASE_URL = 'http://localhost:8000';

export const handlers = [
    // Health & Readiness
    http.get(`${API_BASE_URL}/health`, async () => {
        await delay(500);
        return HttpResponse.json({
            status: 'ok',
            model: 'llama3:8b',
            version: '1.0.4-PROD'
        });
    }),

    http.get(`${API_BASE_URL}/ready`, async () => {
        return HttpResponse.json({
            status: 'ready',
            checks: { mongodb: 'ready', ollama: 'ready', redis: 'ready' },
        });
    }),

    // Agent Execution
    http.post(`${API_BASE_URL}/agent/run`, async ({ request }) => {
        await delay(1500);
        const body = await request.json() as any;
        return HttpResponse.json({
            result: `Processed goal: ${body.goal}. This is a mocked response.`,
            request_id: `req_${Math.random().toString(36).slice(2, 11)}`,
        });
    }),

    // Trace
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

    // Mocked Blueprints Endpoints (not yet in backend)
    http.get(`${API_BASE_URL}/api/agents`, () => {
        return HttpResponse.json([
            { id: '1', name: 'General Assistant', version: '1.0.0', created_at: new Date().toISOString() },
            { id: '2', name: 'Data Analyst', version: '1.1.0', created_at: new Date().toISOString() },
        ]);
    }),

    http.get(`${API_BASE_URL}/api/runs`, () => {
        return HttpResponse.json([
            { id: 'run_1', agent_id: '1', status: 'completed', started_at: new Date().toISOString(), result: 'Success' },
            { id: 'run_2', agent_id: '2', status: 'running', started_at: new Date().toISOString() },
        ]);
    }),
];
