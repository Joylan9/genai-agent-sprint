import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import { agentClient } from '../../features/agent/api/agentClient';

export type UserRole = 'admin' | 'developer' | 'viewer';

export interface AuthUser {
    id: string;
    email: string;
    name: string;
    role: UserRole;
    created_at?: string | null;
    dev_bypass?: boolean;
}

interface StoredAuth {
    access_token: string | null;
    refresh_token: string | null;
    user?: AuthUser | null;
}

interface AuthState {
    user: AuthUser | null;
    accessToken: string | null;
    refreshToken: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
}

interface AuthContextType extends AuthState {
    login: (email: string, password: string) => Promise<void>;
    register: (email: string, password: string, name: string) => Promise<void>;
    logout: () => void;
    refreshSession: () => Promise<void>;
}

const AUTH_STORAGE_KEY = 'auth';
const AuthContext = createContext<AuthContextType | null>(null);

function readStoredAuth(): StoredAuth | null {
    const stored = localStorage.getItem(AUTH_STORAGE_KEY);
    if (!stored) return null;
    try {
        const parsed = JSON.parse(stored) as StoredAuth;
        return {
            access_token: parsed.access_token ?? null,
            refresh_token: parsed.refresh_token ?? null,
            user: parsed.user ?? null,
        };
    } catch {
        localStorage.removeItem(AUTH_STORAGE_KEY);
        return null;
    }
}

export const useAuth = (): AuthContextType => {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth must be used within <AuthProvider>');
    return ctx;
};

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [state, setState] = useState<AuthState>({
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        isLoading: true,
    });

    const persistState = (payload: StoredAuth, user: AuthUser | null) => {
        const stored: StoredAuth = {
            access_token: payload.access_token ?? null,
            refresh_token: payload.refresh_token ?? null,
            user,
        };
        localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(stored));
        agentClient.setAuthToken(stored.access_token);
        setState({
            user,
            accessToken: stored.access_token,
            refreshToken: stored.refresh_token,
            isAuthenticated: !!user,
            isLoading: false,
        });
    };

    const clearState = () => {
        localStorage.removeItem(AUTH_STORAGE_KEY);
        agentClient.setAuthToken(null);
        setState({
            user: null,
            accessToken: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
        });
    };

    const refreshSession = async () => {
        const stored = readStoredAuth();
        const refreshToken = stored?.refresh_token;
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }
        const refreshed = await agentClient.refreshToken(refreshToken);
        const me = await agentClient.getMe();
        persistState(refreshed, me);
    };

    useEffect(() => {
        let cancelled = false;

        const bootstrap = async () => {
            const stored = readStoredAuth();
            if (stored?.access_token) {
                agentClient.setAuthToken(stored.access_token);
            } else {
                agentClient.setAuthToken(null);
            }

            try {
                if (stored?.access_token) {
                    const me = await agentClient.getMe();
                    if (!cancelled) persistState(stored, me);
                    return;
                }

                // Allow explicit dev-bypass bootstrap without a stored token.
                const me = await agentClient.getMe();
                if (!cancelled) {
                    persistState(
                        {
                            access_token: stored?.access_token ?? null,
                            refresh_token: stored?.refresh_token ?? null,
                        },
                        me,
                    );
                }
            } catch (error) {
                if (stored?.refresh_token) {
                    try {
                        const refreshed = await agentClient.refreshToken(stored.refresh_token);
                        const me = await agentClient.getMe();
                        if (!cancelled) persistState(refreshed, me);
                        return;
                    } catch {
                        // fall through to clear auth state
                    }
                }

                if (!cancelled) {
                    clearState();
                }
            }
        };

        bootstrap().finally(() => {
            if (!cancelled) {
                setState((current) => ({ ...current, isLoading: false }));
            }
        });

        return () => {
            cancelled = true;
        };
    }, []);

    const login = async (email: string, password: string) => {
        const response = await agentClient.login(email, password);
        const me = response.user ?? (await agentClient.getMe());
        persistState(response, me);
    };

    const register = async (email: string, password: string, name: string) => {
        const response = await agentClient.register(email, password, name);
        const me = response.user ?? (await agentClient.getMe());
        persistState(response, me);
    };

    const logout = () => {
        clearState();
    };

    const value = useMemo<AuthContextType>(
        () => ({
            ...state,
            login,
            register,
            logout,
            refreshSession,
        }),
        [state],
    );

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
