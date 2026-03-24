import axios, { type AxiosError, type AxiosInstance, type InternalAxiosRequestConfig, type AxiosResponse } from 'axios';
import type {
    AgentRequest,
    AgentResponse,
    ApiError,
    HealthStatus,
    ReadinessStatus,
    Trace
} from '../types';

declare global {
    interface Window {
        __APP_CONFIG__?: {
            VITE_API_BASE?: string;
            APP_VERSION?: string;
            FEATURE_FLAGS_ENDPOINT?: string;
            FRONTEND_HEALTH_ENDPOINT?: string;
            REFRESH_ENDPOINT?: string;
            TELEMETRY_ENDPOINT?: string;
            ENABLE_AUTH_REFRESH?: string;
        };
    }
}

function getRuntimeConfig() {
    const cfg = (typeof window !== "undefined" && window.__APP_CONFIG__) || {};
    return {
        API_BASE_URL: cfg.VITE_API_BASE || import.meta.env.VITE_API_BASE || 'http://localhost:8000',
        APP_VERSION: cfg.APP_VERSION || '0.0.0-LOCAL',
        REFRESH_ENDPOINT: cfg.REFRESH_ENDPOINT || '/api/auth/refresh',
        TELEMETRY_ENDPOINT: cfg.TELEMETRY_ENDPOINT || undefined,
        ENABLE_AUTH_REFRESH: (cfg.ENABLE_AUTH_REFRESH || import.meta.env.VITE_ENABLE_AUTH_REFRESH || 'true') === 'true',
    };
}

const runtime = getRuntimeConfig();
const API_BASE_URL = runtime.API_BASE_URL;
const APP_VERSION = runtime.APP_VERSION;
const REFRESH_ENDPOINT = runtime.REFRESH_ENDPOINT;
const TELEMETRY_ENDPOINT = runtime.TELEMETRY_ENDPOINT;
const ENABLE_AUTH_REFRESH = runtime.ENABLE_AUTH_REFRESH;
const AUTH_STORAGE_KEY = 'auth';

type StoredAuth = {
    access_token: string | null;
    refresh_token: string | null;
    user?: any;
};

function readStoredAuth(): StoredAuth | null {
    if (typeof window === 'undefined') return null;
    const raw = window.localStorage.getItem(AUTH_STORAGE_KEY);
    if (!raw) return null;
    try {
        return JSON.parse(raw) as StoredAuth;
    } catch {
        window.localStorage.removeItem(AUTH_STORAGE_KEY);
        return null;
    }
}

function writeStoredAuth(payload: StoredAuth) {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(payload));
}

function clearStoredAuth() {
    if (typeof window === 'undefined') return;
    window.localStorage.removeItem(AUTH_STORAGE_KEY);
}

class AgentClient {
    public instance: AxiosInstance;
    private isRefreshing = false;
    private failedQueue: any[] = [];

    constructor() {
        this.instance = axios.create({
            baseURL: API_BASE_URL,
            timeout: 150000,
            withCredentials: true,
            headers: {
                'Content-Type': 'application/json',
                'X-App-Version': APP_VERSION
            },
        });

        this.setupInterceptors();

        const stored = readStoredAuth();
        if (stored?.access_token) {
            this.setAuthToken(stored.access_token);
        }
    }

    private setupInterceptors() {
        // Request interceptor for API Key and per-request Correlation ID
        this.instance.interceptors.request.use(
            (config: InternalAxiosRequestConfig) => {
                config.headers = config.headers ?? {};
                const requestId = (
                    typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function'
                )
                    ? crypto.randomUUID()
                    : `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
                config.headers['X-Request-ID'] = requestId;
                return config;
            },
            (error) => Promise.reject(this.normalizeError(error))
        );

        // Response interceptor for error normalization, telemetry, and session expiry
        this.instance.interceptors.response.use(
            (response: AxiosResponse) => {
                if (response.config.url?.includes('/agent/run')) {
                    this.trackEvent('agent_run_success', { url: response.config.url });
                }
                return response.data;
            },
            async (error: AxiosError) => {
                const originalRequest = error.config as any;
                const shouldRefresh =
                    ENABLE_AUTH_REFRESH
                    && !!originalRequest
                    && !String(originalRequest?.url || '').includes(REFRESH_ENDPOINT);

                if (error.response?.status === 401 && shouldRefresh && !originalRequest._retry) {
                    const stored = readStoredAuth();
                    const refreshToken = stored?.refresh_token;
                    if (!refreshToken) {
                        clearStoredAuth();
                        this.setAuthToken(null);
                        return Promise.reject(this.normalizeError(error));
                    }

                    if (this.isRefreshing) {
                        return new Promise((resolve, reject) => {
                            this.failedQueue.push({ resolve, reject });
                        }).then(() => {
                            return this.instance(originalRequest);
                        }).catch(err => {
                            return Promise.reject(err);
                        });
                    }

                    originalRequest._retry = true;
                    this.isRefreshing = true;

                    try {
                        this.trackEvent('session_refresh_started', { url: originalRequest.url });
                        const refreshed = await this.instance.post<any, {
                            access_token: string;
                            refresh_token: string;
                            user?: any;
                        }>(REFRESH_ENDPOINT, { refresh_token: refreshToken });
                        this.setAuthToken(refreshed.access_token);
                        writeStoredAuth({
                            access_token: refreshed.access_token,
                            refresh_token: refreshed.refresh_token,
                            user: refreshed.user ?? stored?.user ?? null,
                        });
                        this.isRefreshing = false;
                        this.processQueue(null);
                        return this.instance(originalRequest);
                    } catch (refreshError) {
                        this.isRefreshing = false;
                        this.processQueue(refreshError);
                        clearStoredAuth();
                        this.setAuthToken(null);
                        this.trackEvent('session_expired_final', { url: originalRequest.url });
                        return Promise.reject(this.normalizeError(refreshError));
                    }
                }

                const normalized = this.normalizeError(error);
                this.trackEvent('api_error', {
                    status: normalized.status,
                    code: normalized.code,
                    url: error.config?.url,
                    requestId: originalRequest?.headers?.['X-Request-ID']
                });
                return Promise.reject(normalized);
            }
        );
    }

    private processQueue(error: any) {
        this.failedQueue.forEach((prom) => {
            if (error) {
                prom.reject(error);
            } else {
                prom.resolve();
            }
        });
        this.failedQueue = [];
    }

    private trackEvent(name: string, properties: Record<string, any> = {}) {
        const payload = {
            name,
            properties: {
                ...properties,
                timestamp: new Date().toISOString(),
                environment: import.meta.env.MODE,
                version: APP_VERSION
            }
        };

        if (TELEMETRY_ENDPOINT && typeof navigator !== 'undefined' && navigator.sendBeacon) {
            try {
                const blob = new Blob([JSON.stringify(payload)], { type: 'application/json' });
                navigator.sendBeacon(TELEMETRY_ENDPOINT, blob);
                return;
            } catch (e) {
                // fall through to console
            }
        }

        // Fallback
        console.debug('[TELEMETRY]', payload);
    }

    private normalizeError(error: any): ApiError {
        if (axios.isAxiosError(error)) {
            const data = error.response?.data as any;
            const message = data?.detail || data?.message || error.message;
            return {
                status: error.response?.status || 500,
                code: data?.code || error.code,
                message: message === 'Network Error'
                    ? 'Network Error (check backend URL, API key, and CORS settings)'
                    : message,
                details: data?.details || null,
            };
        }
        return {
            status: 500,
            message: error instanceof Error ? error.message : 'Unknown error occurred',
        };
    }

    // Core API Methods
    async checkHealth(): Promise<HealthStatus> {
        return this.instance.get('/health');
    }

    async checkReadiness(): Promise<ReadinessStatus> {
        return this.instance.get('/ready');
    }

    async runAgent(request: AgentRequest): Promise<AgentResponse> {
        return this.instance.post('/agent/run', request);
    }

    async getTrace(requestId: string): Promise<Trace> {
        return this.instance.get(`/traces/${requestId}`);
    }

    async listAgents(query?: string): Promise<any[]> {
        return this.instance.get('/api/agents', {
            params: query ? { q: query } : undefined
        });
    }

    async createAgent(agent: { name: string; version?: string; description?: string }): Promise<any> {
        return this.instance.post('/api/agents', agent);
    }

    async updateAgent(agentId: string, updates: { name?: string; version?: string; description?: string }): Promise<any> {
        return this.instance.patch(`/api/agents/${agentId}`, updates);
    }

    async getAgentVersions(agentId: string): Promise<any[]> {
        return this.instance.get(`/api/agents/${agentId}/versions`);
    }

    async createAgentVersion(agentId: string, request: { version: string; metadata?: Record<string, any> }): Promise<any> {
        return this.instance.post(`/api/agents/${agentId}/versions`, request);
    }

    async promoteAgentVersion(agentId: string, version: string): Promise<any> {
        return this.instance.post(`/api/agents/${agentId}/versions/${version}/promote`);
    }

    async listRuns(filters?: { q?: string; status?: string }): Promise<any[]> {
        return this.instance.get('/api/runs', {
            params: filters
        });
    }

    async getAgent(agentId: string): Promise<any> {
        return this.instance.get(`/api/agents/${agentId}`);
    }

    async deleteAgent(agentId: string): Promise<void> {
        return this.instance.delete(`/api/agents/${agentId}`);
    }

    async deleteRun(requestId: string): Promise<void> {
        return this.instance.delete(`/api/runs/${requestId}`);
    }

    // ============================================================
    // Async Run Submission (Celery-backed)
    // ============================================================

    async submitRun(request: { session_id: string; goal: string; agent_id?: string }): Promise<{ run_id: string; status: string }> {
        return this.instance.post('/api/runs/submit', request);
    }

    async pollRunStatus(runId: string): Promise<{
        run_id: string;
        status: string;
        goal?: string;
        result?: string;
        error?: string;
        started_at?: string;
        completed_at?: string;
        cache_hit?: boolean;
        latency_total?: number;
    }> {
        return this.instance.get(`/api/runs/${runId}/status`);
    }

    // ============================================================
    // Authentication (Phase 3)
    // ============================================================

    setAuthToken(token: string | null) {
        if (token) {
            this.instance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        } else {
            delete this.instance.defaults.headers.common['Authorization'];
        }
    }

    async login(email: string, password: string): Promise<any> {
        return this.instance.post('/api/auth/login', { email, password });
    }

    async register(email: string, password: string, name: string): Promise<any> {
        return this.instance.post('/api/auth/register', { email, password, name });
    }

    async refreshToken(refreshToken: string): Promise<any> {
        return this.instance.post('/api/auth/refresh', { refresh_token: refreshToken });
    }

    async getMe(): Promise<any> {
        return this.instance.get('/api/auth/me');
    }

    // ============================================================
    // Evaluation (Phase 5)
    // ============================================================

    async runEvalSuite(suiteName: string = 'default'): Promise<any> {
        return this.instance.post('/api/eval/run-suite', { suite_name: suiteName });
    }

    async listEvalSuites(): Promise<Array<{ name: string; path: string }>> {
        return this.instance.get('/api/eval/suites');
    }

    async getEvalResults(): Promise<any[]> {
        return this.instance.get('/api/eval/results');
    }

    async getEvalResult(suiteId: string): Promise<any> {
        return this.instance.get(`/api/eval/results/${suiteId}`);
    }

    // ============================================================
    // Password Reset / OTP
    // ============================================================

    async requestOtp(email: string): Promise<any> {
        return this.instance.post('/api/auth/request-otp', { email });
    }

    async verifyOtp(email: string, otp: string): Promise<any> {
        return this.instance.post('/api/auth/verify-otp', { email, otp });
    }

    async resetPassword(resetToken: string, newPassword: string): Promise<any> {
        return this.instance.post('/api/auth/reset-password', { reset_token: resetToken, new_password: newPassword });
    }

    getAccessToken(): string | null {
        return readStoredAuth()?.access_token ?? null;
    }

    getRunStreamUrl(runId: string): string {
        const token = this.getAccessToken();
        const url = new URL(`/api/runs/${runId}/stream`, API_BASE_URL);
        if (token) {
            url.searchParams.set('access_token', token);
        }
        return url.toString();
    }
}

export const agentClient = new AgentClient();
