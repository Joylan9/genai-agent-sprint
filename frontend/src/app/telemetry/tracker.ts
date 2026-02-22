/**
 * Centralized telemetry tracker for enterprise observability.
 * This can be swapped with Sentry, Mixpanel, or custom segment event trackers.
 */

type TelemetryEvent =
    | 'agent_run_started'
    | 'agent_run_success'
    | 'agent_run_failed'
    | 'trace_opened'
    | 'agent_created'
    | 'api_error'
    | 'page_view';

export const trackEvent = (name: TelemetryEvent, properties: Record<string, any> = {}) => {
    const eventData = {
        event: name,
        properties: {
            ...properties,
            url: window.location.href,
            timestamp: new Date().toISOString(),
            userAgent: navigator.userAgent,
        }
    };

    // Log to console for development
    if (import.meta.env.DEV) {
        console.log(`[TELEMETRY] ${name}`, eventData.properties);
    }

    // TODO: Send to production observability system
    // Example: Sentry.captureMessage(name, { extra: properties });
};

/**
 * Hook for easy access to telemetry in components
 */
export const useTelemetry = () => {
    return { track: trackEvent };
};
