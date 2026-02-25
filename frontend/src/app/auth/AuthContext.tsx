import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import type { ReactNode } from 'react';
import { agentClient } from '../../features/agent/api/agentClient';

// ============================================================
// Types
// ============================================================

interface User {
    id: string;
    email: string;
    name: string;
}

interface AuthState {
    user: User | null;
    accessToken: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
}

interface AuthContextType extends AuthState {
    login: (email: string, password: string) => Promise<void>;
    register: (email: string, password: string, name: string) => Promise<void>;
    logout: () => void;
}

// ============================================================
// Context
// ============================================================

const AuthContext = createContext<AuthContextType | null>(null);

export const useAuth = (): AuthContextType => {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth must be used within <AuthProvider>');
    return ctx;
};

// ============================================================
// Provider
// ============================================================

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [state, setState] = useState<AuthState>({
        user: null,
        accessToken: null,
        isAuthenticated: false,
        isLoading: true,
    });

    // Restore session from localStorage on mount
    useEffect(() => {
        const stored = localStorage.getItem('auth');
        if (stored) {
            try {
                const parsed = JSON.parse(stored);
                setState({
                    user: parsed.user,
                    accessToken: parsed.access_token,
                    isAuthenticated: true,
                    isLoading: false,
                });
            } catch {
                localStorage.removeItem('auth');
                setState(s => ({ ...s, isLoading: false }));
            }
        } else {
            setState(s => ({ ...s, isLoading: false }));
        }
    }, []);

    const _persist = (data: any) => {
        localStorage.setItem('auth', JSON.stringify(data));
        setState({
            user: data.user,
            accessToken: data.access_token,
            isAuthenticated: true,
            isLoading: false,
        });
    };

    const login = useCallback(async (email: string, password: string) => {
        const res = await agentClient.login(email, password);
        _persist(res);
    }, []);

    const register = useCallback(async (email: string, password: string, name: string) => {
        const res = await agentClient.register(email, password, name);
        _persist(res);
    }, []);

    const logout = useCallback(() => {
        localStorage.removeItem('auth');
        setState({
            user: null,
            accessToken: null,
            isAuthenticated: false,
            isLoading: false,
        });
    }, []);

    return (
        <AuthContext.Provider value={{ ...state, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    );
};
