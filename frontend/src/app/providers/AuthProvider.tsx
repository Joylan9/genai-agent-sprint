import React, { createContext, useContext, useEffect, useState } from "react";
import { type User } from "../auth/usePermission";

interface AuthContextType {
    user: User | null;
    setUser: (u: User | null) => void;
}

const AuthContext = createContext<AuthContextType>({
    user: null,
    setUser: () => { },
});

export function useAuth() {
    return useContext(AuthContext);
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(() => {
        // Bootstrap with mock admin user for development
        return {
            id: 'u-001',
            name: 'Admin User',
            role: 'admin',
        };
    });

    useEffect(() => {
        // Optional: session validation logic
    }, []);

    return <AuthContext.Provider value={{ user, setUser }}>{children}</AuthContext.Provider>;
}
