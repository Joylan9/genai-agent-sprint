import { AlertTriangle, Info, XCircle, X } from 'lucide-react';
import { cn } from '../lib/utils';
import { useState, useEffect } from 'react';

interface StatusBannerProps {
    message: string;
    type?: 'warning' | 'error' | 'info';
    onClose?: () => void;
}

export const StatusBanner = ({ message: initialMessage, type: initialType = 'warning', onClose }: StatusBannerProps) => {
    const [isVisible, setIsVisible] = useState(true);
    const [message, setMessage] = useState(initialMessage);
    const [type, setType] = useState(initialType);

    useEffect(() => {
        if (initialMessage) return; // Managed by props

        const fetchStatus = async () => {
            try {
                const config = (window as any).__APP_CONFIG__;
                const res = await fetch(`${config?.VITE_API_BASE ?? ""}/health`);
                const json = await res.json();

                if (json.status !== "ok") {
                    setMessage(`Partial outage: ${json.model || 'LLM Service'} is currenty degraded.`);
                    setType("warning");
                    setIsVisible(true);
                } else {
                    setIsVisible(false);
                }
            } catch {
                // ignore
            }
        };

        const t = setInterval(fetchStatus, 30_000);
        return () => clearInterval(t);
    }, [initialMessage]);

    if (!isVisible) return null;

    const styles = {
        warning: 'bg-amber-50 border-amber-200 text-amber-800',
        error: 'bg-red-50 border-red-200 text-red-800',
        info: 'bg-blue-50 border-blue-200 text-blue-800',
    };

    const icons = {
        warning: <AlertTriangle size={16} />,
        error: <XCircle size={16} />,
        info: <Info size={16} />,
    };

    return (
        <div className={cn(
            "px-4 py-2 border-b flex items-center justify-between animate-in slide-in-from-top duration-300",
            styles[type]
        )}>
            <div className="flex items-center gap-3 text-sm font-medium">
                {icons[type]}
                <span>{message}</span>
            </div>
            {onClose && (
                <button
                    onClick={() => {
                        setIsVisible(false);
                        onClose();
                    }}
                    className="p-1 hover:bg-black/5 rounded-full transition-colors"
                >
                    <X size={14} />
                </button>
            )}
        </div>
    );
};
