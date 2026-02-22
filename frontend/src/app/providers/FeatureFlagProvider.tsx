import React, { createContext, useContext, useEffect, useState } from "react";

type Flags = Record<string, boolean>;

const FeatureFlagContext = createContext<{ flags: Flags; refresh: () => void }>({
    flags: {},
    refresh: () => { },
});

export function useFeatureFlags() {
    return useContext(FeatureFlagContext);
}

export function FeatureFlagProvider({ children }: { children: React.ReactNode }) {
    const [flags, setFlags] = useState<Flags>({});

    const fetchFlags = async () => {
        try {
            const config = (window as any).__APP_CONFIG__;
            const base = config?.VITE_API_BASE ?? "";
            const endpoint = config?.FEATURE_FLAGS_ENDPOINT ?? "/api/feature-flags";

            const res = await fetch(base + endpoint, { credentials: "include" });
            if (!res.ok) return;
            const json = await res.json();
            setFlags(json || {});
        } catch (err) {
            console.debug("feature flags fetch failed", err);
        }
    };

    useEffect(() => {
        fetchFlags();
    }, []);

    return (
        <FeatureFlagContext.Provider value={{ flags, refresh: fetchFlags }}>
            {children}
        </FeatureFlagContext.Provider>
    );
}
