export interface AuthResponse {
    access_token: string;
    refresh_token: string;
    token_type: "bearer";
    expires_in: number;
    user: {
        id: string;
        email: string;
        name: string;
        role: "admin" | "developer" | "viewer";
        created_at?: string | null;
    };
}

export interface RunSubmitRequest {
    session_id: string;
    goal: string;
    agent_id?: string;
}

export interface RunStatusResponse {
    run_id: string;
    status: "queued" | "running" | "completed" | "failed";
    goal?: string;
    agent_id?: string | null;
    agent_name?: string | null;
    started_at?: string | null;
    completed_at?: string | null;
    cache_hit?: boolean;
    latency_total?: number | null;
    error?: string | null;
    result?: string;
}

export class TraceAIClient {
    constructor(private readonly baseUrl: string, private accessToken: string | null = null) {}

    setAccessToken(token: string | null) {
        this.accessToken = token;
    }

    private async request<T>(path: string, init: RequestInit = {}): Promise<T> {
        const headers = new Headers(init.headers || {});
        headers.set("Content-Type", "application/json");
        if (this.accessToken) {
            headers.set("Authorization", `Bearer ${this.accessToken}`);
        }

        const response = await fetch(`${this.baseUrl}${path}`, { ...init, headers });
        if (!response.ok) {
            throw new Error(`${response.status} ${response.statusText}`);
        }
        return response.json() as Promise<T>;
    }

    async login(email: string, password: string): Promise<AuthResponse> {
        const response = await this.request<AuthResponse>("/api/auth/login", {
            method: "POST",
            body: JSON.stringify({ email, password }),
        });
        this.setAccessToken(response.access_token);
        return response;
    }

    async submitRun(payload: RunSubmitRequest): Promise<{ run_id: string; status: "queued" }> {
        return this.request("/api/runs/submit", {
            method: "POST",
            body: JSON.stringify(payload),
        });
    }

    async getRunStatus(runId: string): Promise<RunStatusResponse> {
        return this.request(`/api/runs/${runId}/status`);
    }

    async getTrace(runId: string) {
        return this.request(`/traces/${runId}`);
    }
}
