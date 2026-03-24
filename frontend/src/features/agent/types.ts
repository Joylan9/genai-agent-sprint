export interface AgentRequest {
    session_id: string;
    goal: string;
    agent_id?: string;
}

export interface AgentResponse {
    result: string;
    request_id?: string;
    status?: string;
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
    checks?: Record<string, { status: string; optional?: boolean; detail?: string } | string>;
    features?: Record<string, boolean>;
}

// Future-proofing for blueprint requirements (mocked for now)
export interface Agent {
    id: string;
    name: string;
    version: string;
    current_version?: string;
    description?: string;
    status?: string;
    metadata?: Record<string, any>;
    created_at: string;
    updated_at?: string | null;
    versions?: AgentVersion[];
}

export interface AgentVersion {
    agent_id: string;
    version: string;
    name?: string;
    description?: string;
    status?: string;
    metadata?: Record<string, any>;
    created_at?: string | null;
    snapshot?: Record<string, any>;
}

export interface Run {
    id: string;
    agent_id: string;
    agent_name?: string;
    status: 'queued' | 'running' | 'completed' | 'failed';
    goal?: string;
    started_at: string;
    completed_at?: string;
    cache_hit?: boolean;
    latency_total?: number;
    error?: string | null;
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
    started_at?: string;
    completed_at?: string;
    timestamp?: string;
    metadata?: Record<string, any>;
}
