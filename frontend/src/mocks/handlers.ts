/*
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
*/

import { delay, http, HttpResponse } from 'msw';

const API_BASE_URL = 'http://localhost:8000';

const agents: Array<any> = [
    {
        id: '1',
        name: 'General Assistant',
        version: '1.0.0',
        current_version: '1.0.0',
        status: 'active',
        description: 'Default assistant',
        created_at: new Date().toISOString(),
        versions: [{ agent_id: '1', version: '1.0.0', created_at: new Date().toISOString(), metadata: { source: 'create' } }],
    },
];

const runs = new Map<string, any>();
const evalResults: any[] = [];
const authPayload = {
    access_token: 'mock-access-token',
    refresh_token: 'mock-refresh-token',
    user: {
        id: 'u-001',
        email: 'admin@traceai.dev',
        name: 'Admin User',
        role: 'admin',
        created_at: new Date().toISOString(),
    },
};

export const handlers = [
    http.get(`${API_BASE_URL}/health`, async () => {
        await delay(100);
        return HttpResponse.json({
            status: 'ok',
            model: 'llama3:8b',
            version: '1.0.0',
            features: {
                authDevBypassEnabled: false,
                webSearchAvailable: true,
                devEmailOtpEchoEnabled: true,
            },
        });
    }),

    http.get(`${API_BASE_URL}/ready`, async () =>
        HttpResponse.json({
            status: 'ready',
            checks: {
                mongodb: { status: 'ready', optional: false },
                ollama: { status: 'ready', optional: false },
                redis: { status: 'ready', optional: false },
                celery: { status: 'ready', optional: false },
                web_search: { status: 'ready', optional: true },
            },
            features: {
                authDevBypassEnabled: false,
                webSearchAvailable: true,
                devEmailOtpEchoEnabled: true,
            },
        }),
    ),

    http.post(`${API_BASE_URL}/api/auth/login`, async () => HttpResponse.json(authPayload)),
    http.post(`${API_BASE_URL}/api/auth/register`, async () => HttpResponse.json(authPayload)),
    http.post(`${API_BASE_URL}/api/auth/refresh`, async () => HttpResponse.json(authPayload)),
    http.get(`${API_BASE_URL}/api/auth/me`, async () => HttpResponse.json(authPayload.user)),
    http.post(`${API_BASE_URL}/api/auth/request-otp`, async () => HttpResponse.json({ message: 'sent', expires_in: 600, dev_otp: '123456' })),
    http.post(`${API_BASE_URL}/api/auth/verify-otp`, async () => HttpResponse.json({ message: 'verified', reset_token: 'reset-token' })),
    http.post(`${API_BASE_URL}/api/auth/reset-password`, async () => HttpResponse.json({ message: 'reset' })),

    http.get(`${API_BASE_URL}/api/feature-flags`, async () =>
        HttpResponse.json({
            authDevBypassEnabled: false,
            webSearchAvailable: true,
            devEmailOtpEchoEnabled: true,
        }),
    ),

    http.get(`${API_BASE_URL}/api/agents`, ({ request }) => {
        const url = new URL(request.url);
        const q = (url.searchParams.get('q') || '').toLowerCase();
        const data = q ? agents.filter((agent) => agent.name.toLowerCase().includes(q)) : agents;
        return HttpResponse.json(data);
    }),

    http.post(`${API_BASE_URL}/api/agents`, async ({ request }) => {
        const body = await request.json() as any;
        const newAgent = {
            id: `agent_${Math.random().toString(36).slice(2, 8)}`,
            name: body.name,
            version: body.version || '1.0.0',
            current_version: body.version || '1.0.0',
            description: body.description || '',
            status: body.status || 'active',
            metadata: body.metadata || {},
            created_at: new Date().toISOString(),
            versions: [] as Array<{
                agent_id: string;
                version: string;
                created_at: string;
                metadata: Record<string, unknown>;
            }>,
        };
        newAgent.versions.push({
            agent_id: newAgent.id,
            version: newAgent.current_version,
            created_at: new Date().toISOString(),
            metadata: { source: 'create' },
        });
        agents.unshift(newAgent);
        return HttpResponse.json(newAgent, { status: 201 });
    }),

    http.patch(`${API_BASE_URL}/api/agents/:id`, async ({ params, request }) => {
        const body = await request.json() as any;
        const agent = agents.find((item) => item.id === params.id);
        Object.assign(agent, body);
        return HttpResponse.json(agent);
    }),

    http.get(`${API_BASE_URL}/api/agents/:id`, async ({ params }) => {
        const agent = agents.find((item) => item.id === params.id);
        if (!agent) return HttpResponse.json({ detail: 'Not found' }, { status: 404 });
        return HttpResponse.json(agent);
    }),

    http.delete(`${API_BASE_URL}/api/agents/:id`, async ({ params }) => {
        const index = agents.findIndex((item) => item.id === params.id);
        if (index >= 0) agents.splice(index, 1);
        return new HttpResponse(null, { status: 204 });
    }),

    http.get(`${API_BASE_URL}/api/agents/:id/versions`, async ({ params }) => {
        const agent = agents.find((item) => item.id === params.id);
        return HttpResponse.json(agent?.versions || []);
    }),

    http.post(`${API_BASE_URL}/api/agents/:id/versions`, async ({ params, request }) => {
        const body = await request.json() as any;
        const agent = agents.find((item) => item.id === params.id);
        const version = {
            agent_id: agent.id,
            version: body.version,
            created_at: new Date().toISOString(),
            metadata: body.metadata || {},
        };
        agent.versions.unshift(version);
        agent.current_version = body.version;
        agent.version = body.version;
        return HttpResponse.json(version, { status: 201 });
    }),

    http.post(`${API_BASE_URL}/api/agents/:id/versions/:version/promote`, async ({ params }) => {
        const agent = agents.find((item) => item.id === params.id);
        agent.current_version = String(params.version);
        agent.version = String(params.version);
        return HttpResponse.json(agent);
    }),

    http.post(`${API_BASE_URL}/api/runs/submit`, async ({ request }) => {
        const body = await request.json() as any;
        const runId = `run_${Math.random().toString(36).slice(2, 10)}`;
        const startedAt = new Date().toISOString();
        const trace = {
            _id: `trace_${runId}`,
            request_id: runId,
            session_id: body.session_id,
            goal: body.goal,
            agent_id: body.agent_id || 'default',
            agent_name: agents.find((agent) => agent.id === body.agent_id)?.name,
            status: 'queued',
            observations: [],
            latency: {},
            started_at: startedAt,
            timestamp: startedAt,
        };
        runs.set(runId, trace);
        return HttpResponse.json({ run_id: runId, status: 'queued' }, { status: 202 });
    }),

    http.get(`${API_BASE_URL}/api/runs`, ({ request }) => {
        const url = new URL(request.url);
        const q = (url.searchParams.get('q') || '').toLowerCase();
        const status = (url.searchParams.get('status') || '').toLowerCase();
        let data = Array.from(runs.values()).map((trace) => ({
            id: trace.request_id,
            agent_id: trace.agent_id,
            agent_name: trace.agent_name,
            status: trace.status,
            goal: trace.goal,
            started_at: trace.started_at,
            completed_at: trace.completed_at,
            cache_hit: false,
            latency_total: trace.latency?.total,
            error: trace.error,
        }));
        if (q) {
            data = data.filter((item) => item.id.toLowerCase().includes(q) || String(item.agent_name || item.agent_id).toLowerCase().includes(q));
        }
        if (status) {
            data = data.filter((item) => item.status === status);
        }
        return HttpResponse.json(data);
    }),

    http.get(`${API_BASE_URL}/api/runs/:id/status`, async ({ params }) => {
        const run = runs.get(String(params.id));
        if (!run) return HttpResponse.json({ detail: 'Not found' }, { status: 404 });
        if (run.status === 'queued') {
            run.status = 'completed';
            run.final_answer = `Processed goal: ${run.goal}`;
            run.completed_at = new Date().toISOString();
            run.latency = { planner: 0.3, tool_wall_time: 0.8, synthesis: 0.2, total: 1.3 };
        }
        return HttpResponse.json({
            run_id: run.request_id,
            status: run.status,
            goal: run.goal,
            agent_id: run.agent_id,
            agent_name: run.agent_name,
            started_at: run.started_at,
            completed_at: run.completed_at,
            result: run.final_answer,
            latency_total: run.latency?.total,
            error: run.error,
        });
    }),

    http.delete(`${API_BASE_URL}/api/runs/:id`, async ({ params }) => {
        runs.delete(String(params.id));
        return new HttpResponse(null, { status: 204 });
    }),

    http.get(`${API_BASE_URL}/traces/:id`, async ({ params }) => {
        const run = runs.get(String(params.id));
        if (!run) return HttpResponse.json({ detail: 'Not found' }, { status: 404 });
        return HttpResponse.json({
            ...run,
            status: run.status,
            observations: run.observations || [],
            final_answer: run.final_answer,
            cache_hit: false,
            latency: run.latency || {},
        });
    }),

    http.get(`${API_BASE_URL}/api/eval/suites`, async () => HttpResponse.json([{ name: 'default', path: 'test_cases.json' }])),
    http.post(`${API_BASE_URL}/api/eval/run-suite`, async ({ request }) => {
        const body = await request.json() as any;
        const result = {
            suite_id: `suite_${Math.random().toString(36).slice(2, 8)}`,
            suite_name: body.suite_name || 'default',
            total: 1,
            passed: 1,
            failed: 0,
            avg_score: 96,
            avg_latency: 1.2,
            results: [{
                case_id: 'case-1',
                goal: 'Explain RAG simply',
                category: 'general',
                difficulty: 'easy',
                passed: true,
                score: 96,
                keyword_score: 100,
                tool_score: 90,
                llm_score: 95,
                latency: 1.2,
                tools_used: ['rag_search'],
            }],
            timestamp: new Date().toISOString(),
        };
        evalResults.unshift(result);
        return HttpResponse.json(result);
    }),
    http.get(`${API_BASE_URL}/api/eval/results`, async () => HttpResponse.json(evalResults)),
    http.get(`${API_BASE_URL}/api/eval/results/:suiteId`, async ({ params }) => {
        const found = evalResults.find((result) => result.suite_id === params.suiteId);
        return HttpResponse.json(found || {}, { status: found ? 200 : 404 });
    }),
];
