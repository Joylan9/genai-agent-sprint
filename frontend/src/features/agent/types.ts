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
    model?: string;
    version?: string;
    error?: string;
}

export interface ReadinessStatus {
    status: 'ready' | 'degraded' | 'not_ready' | string;
    checks?: Record<string, 'ready' | 'unavailable' | string>;
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
    session_id?: string;
    goal?: string;
    plan?: string;
    status?: 'queued' | 'running' | 'completed' | 'failed' | string;
    error?: string;
    steps?: any[];
    observations?: Array<{
        step: number;
        tool: string;
        query: string;
        response: {
            status: string;
            data: any;
            metadata?: Record<string, any>;
        };
    }>;
    final_answer?: string;
    cache_hit?: boolean;
    latency?: {
        planner: number;
        tool_total: number;
        tool_wall_time: number;
        synthesis: number;
        total: number;
    };
    timestamp?: string;
    metadata?: Record<string, any>;
}
