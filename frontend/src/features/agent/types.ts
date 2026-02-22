export interface AgentRequest {
    session_id: string;
    goal: string;
}

export interface AgentResponse {
    result: string;
    request_id?: string;
}

export interface ApiError {
    status: number;
    code?: string;
    message: string;
    details?: any;
}

export interface HealthStatus {
    status: string;
    model: string;
    version: string;
}

export interface ReadinessStatus {
    status: 'ready' | 'degraded';
    checks: Record<string, 'ready' | 'unavailable'>;
}

// Future-proofing for blueprint requirements (mocked for now)
export interface Agent {
    id: string;
    name: string;
    version: string;
    description?: string;
    created_at: string;
}

export interface Run {
    id: string;
    agent_id: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    started_at: string;
    completed_at?: string;
    result?: string;
}

export interface Trace {
    _id: string;
    request_id: string;
    steps: any[];
    metadata: Record<string, any>;
}
