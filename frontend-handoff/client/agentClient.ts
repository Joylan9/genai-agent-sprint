/**
 * Simple, production-ready React/TypeScript client for the AI Agent Platform.
 * Features: Built-in polling for long-running tasks, abort support, and trace tracking.
 */

export interface AgentRequest {
    session_id: string;
    goal: string;
    options?: { max_steps?: number; use_cache?: boolean };
}

export interface AgentResponse {
    trace_id: string;
    response?: string;
    metadata?: any;
    status?: "running" | "completed" | "failed";
}

export class AgentClient {
    private baseUrl: string;
    private apiKey: string;

    constructor(baseUrl: string, apiKey: string) {
        this.baseUrl = baseUrl;
        this.apiKey = apiKey;
    }

    async runAgent(request: AgentRequest, signal?: AbortSignal): Promise<AgentResponse> {
        const response = await fetch(`${this.baseUrl}/agent/run`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "x-api-key": this.apiKey,
            },
            body: JSON.stringify(request),
            signal,
        });

        if (!response.ok) {
            throw new Error(`Agent API Error: ${response.statusText}`);
        }

        return response.json();
    }

    async pollTrace(traceId: string, interval = 2000, maxAttempts = 30): Promise<AgentResponse> {
        for (let i = 0; i < maxAttempts; i++) {
            const response = await fetch(`${this.baseUrl}/traces/${traceId}`, {
                headers: { "x-api-key": this.apiKey },
            });

            if (response.ok) {
                const data = await response.json();
                if (data.status === "completed" || data.status === "failed") {
                    return data;
                }
            }
            await new Promise((resolve) => setTimeout(resolve, interval));
        }
        throw new Error("Polling timeout: Agent took too long to respond.");
    }
}
