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
            VITE_API_KEY?: string;
            APP_VERSION?: string;
            FEATURE_FLAGS_ENDPOINT?: string;
            FRONTEND_HEALTH_ENDPOINT?: string;
            REFRESH_ENDPOINT?: string;
            TELEMETRY_ENDPOINT?: string;
        };
    }
}

function getRuntimeConfig() {
    const cfg = (typeof window !== "undefined" && window.__APP_CONFIG__) || {};
    return {
        API_BASE_URL: cfg.VITE_API_BASE || import.meta.env.VITE_API_BASE || 'http://localhost:8000',
        API_KEY: cfg.VITE_API_KEY || import.meta.env.VITE_API_KEY,
        APP_VERSION: cfg.APP_VERSION || '0.0.0-LOCAL',
        REFRESH_ENDPOINT: cfg.REFRESH_ENDPOINT || '/api/auth/refresh',
        TELEMETRY_ENDPOINT: cfg.TELEMETRY_ENDPOINT || undefined
    };
}

const runtime = getRuntimeConfig();
const API_BASE_URL = runtime.API_BASE_URL;
const API_KEY = runtime.API_KEY;
const APP_VERSION = runtime.APP_VERSION;
const REFRESH_ENDPOINT = runtime.REFRESH_ENDPOINT;
const TELEMETRY_ENDPOINT = runtime.TELEMETRY_ENDPOINT;

class AgentClient {
    public instance: AxiosInstance;
    private isRefreshing = false;
    private failedQueue: any[] = [];

    constructor() {
        this.instance = axios.create({
            baseURL: API_BASE_URL,
            timeout: 60000,
            withCredentials: true,
            headers: {
                'Content-Type': 'application/json',
                'X-App-Version': APP_VERSION
            },
        });

        this.setupInterceptors();
    }

    private setupInterceptors() {
        // Request interceptor for API Key and per-request Correlation ID
        this.instance.interceptors.request.use(
            (config: InternalAxiosRequestConfig) => {
                if (API_KEY) {
                    config.headers['X-API-KEY'] = API_KEY;
                }
                // Generate a unique X-Request-ID per outgoing request
                config.headers['X-Request-ID'] = crypto?.randomUUID?.() || `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
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

                if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
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
                        await this.instance.post(REFRESH_ENDPOINT);
                        this.isRefreshing = false;
                        this.processQueue(null);
                        return this.instance(originalRequest);
                    } catch (refreshError) {
                        this.isRefreshing = false;
                        this.processQueue(refreshError);
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
            return {
                status: error.response?.status || 500,
                code: data?.code || error.code,
                message: data?.detail || data?.message || error.message,
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

    async listAgents(): Promise<any[]> {
        return this.instance.get('/api/agents');
    }

    async listRuns(): Promise<any[]> {
        return this.instance.get('/api/runs');
    }
}

export const agentClient = new AgentClient();
