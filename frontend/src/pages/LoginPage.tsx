import { useState } from 'react';
import { useAuth } from '../app/auth/AuthContext';
import { useFeatureFlags } from '../app/providers/FeatureFlagProvider';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '../shared/ui/Button';
import { Input } from '../shared/ui/Input';
import {
    Zap, Mail, Lock, User, ArrowRight,
    Shield, Activity, BarChart3, Cpu,
    GitBranch, Layers, Eye, EyeOff,
} from 'lucide-react';

const PLATFORM_FEATURES = [
    { icon: Cpu, label: 'Distributed Agent Runtime', desc: 'Celery-backed async execution' },
    { icon: Shield, label: 'Enterprise Security', desc: 'Guardrails, policy engine, JWT auth' },
    { icon: Activity, label: 'Real-Time Observability', desc: 'SSE streaming, Prometheus metrics' },
    { icon: BarChart3, label: 'Evaluation Engine', desc: 'LLM-as-judge benchmarking' },
    { icon: GitBranch, label: 'Smart Tool Routing', desc: 'Confidence-based fallback chains' },
    { icon: Layers, label: 'Memory-Informed Planning', desc: 'Contextual agent cognition' },
];

export const LoginPage = () => {
    const { login, register } = useAuth();
    const { flags } = useFeatureFlags();
    const navigate = useNavigate();

    const [mode, setMode] = useState<'login' | 'register'>('login');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [name, setName] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            if (mode === 'login') {
                await login(email, password);
            } else {
                await register(email, password, name);
            }
            navigate('/');
        } catch (err: any) {
            setError(err?.message || 'Authentication failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex bg-slate-950 overflow-hidden">
            {/* ========================================= */}
            {/* LEFT PANEL — Platform Branding            */}
            {/* ========================================= */}
            <div className="hidden lg:flex lg:w-[55%] relative flex-col justify-between p-12 overflow-hidden">
                {/* Animated gradient background */}
                <div className="absolute inset-0 bg-gradient-to-br from-blue-950 via-indigo-950 to-slate-950" />
                <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-blue-500/10 rounded-full blur-[120px] -translate-x-1/2 -translate-y-1/2" />
                <div className="absolute bottom-0 right-0 w-[400px] h-[400px] bg-indigo-500/10 rounded-full blur-[100px] translate-x-1/3 translate-y-1/3" />
                <div className="absolute top-1/2 left-1/2 w-[300px] h-[300px] bg-purple-500/5 rounded-full blur-[80px] -translate-x-1/2 -translate-y-1/2" />

                {/* Grid pattern overlay */}
                <div
                    className="absolute inset-0 opacity-[0.03]"
                    style={{
                        backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
                        backgroundSize: '60px 60px',
                    }}
                />

                {/* Content */}
                <div className="relative z-10">
                    {/* Logo */}
                    <div className="flex items-center gap-3 mb-16">
                        <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-2xl shadow-blue-500/30">
                            <Zap size={24} className="text-white" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold tracking-tight text-white">TraceAI</h1>
                            <p className="text-xs text-blue-400/80 font-medium tracking-wider uppercase">Agent Platform</p>
                        </div>
                    </div>

                    {/* Hero text */}
                    <div className="max-w-lg">
                        <h2 className="text-4xl font-bold text-white leading-tight mb-4">
                            Distributed Agent
                            <span className="block bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400">
                                Runtime Platform
                            </span>
                        </h2>
                        <p className="text-lg text-slate-400 leading-relaxed">
                            Enterprise-grade AI orchestration with real-time observability,
                            intelligent routing, and automated quality evaluation.
                        </p>
                    </div>
                </div>

                {/* Feature Grid */}
                <div className="relative z-10">
                    <div className="grid grid-cols-2 gap-3">
                        {PLATFORM_FEATURES.map((feat) => (
                            <div
                                key={feat.label}
                                className="flex items-start gap-3 p-3.5 rounded-xl bg-white/[0.03] border border-white/[0.06] backdrop-blur-sm hover:bg-white/[0.06] transition-all group"
                            >
                                <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center shrink-0 group-hover:bg-blue-500/20 transition-colors">
                                    <feat.icon size={16} className="text-blue-400" />
                                </div>
                                <div className="min-w-0">
                                    <p className="text-sm font-semibold text-white/90 truncate">{feat.label}</p>
                                    <p className="text-[11px] text-slate-500 mt-0.5">{feat.desc}</p>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Version badge */}
                    <div className="mt-6 flex items-center gap-2">
                        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                            Production Ready Platform
                        </span>
                    </div>
                </div>
            </div>

            {/* ========================================= */}
            {/* RIGHT PANEL — Auth Form                   */}
            {/* ========================================= */}
            <div className="flex-1 flex items-center justify-center px-6 lg:px-12 relative">
                {/* Subtle glow */}
                <div className="absolute top-1/4 right-1/4 w-64 h-64 bg-blue-500/5 rounded-full blur-[80px]" />

                <div className="w-full max-w-[420px] relative z-10">
                    {/* Mobile logo (hidden on lg) */}
                    <div className="lg:hidden text-center mb-8">
                        <div className="inline-flex items-center gap-2.5 mb-3">
                            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
                                <Zap size={20} className="text-white" />
                            </div>
                            <h1 className="text-2xl font-bold text-white tracking-tight">TraceAI</h1>
                        </div>
                    </div>

                    {/* Header */}
                    <div className="mb-8">
                        <h2 className="text-2xl font-bold text-white mb-2">
                            {mode === 'login' ? 'Welcome back' : 'Create account'}
                        </h2>
                        <p className="text-sm text-slate-400">
                            {mode === 'login'
                                ? 'Enter your credentials to access the platform'
                                : 'Set up your enterprise account'}
                        </p>
                    </div>

                    {/* Form Card */}
                    <div className="bg-white/[0.04] backdrop-blur-2xl border border-white/[0.08] rounded-2xl p-7 shadow-2xl">
                        <form onSubmit={handleSubmit} className="space-y-5">
                            {mode === 'register' && (
                                <div className="space-y-2">
                                    <label htmlFor="auth-name" className="text-xs font-semibold text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
                                        <User size={12} /> Full Name
                                    </label>
                                    <div className="relative">
                                        <Input
                                            id="auth-name"
                                            value={name}
                                            onChange={(e) => setName(e.target.value)}
                                            placeholder="John Doe"
                                            className="bg-white/[0.06] border-white/[0.1] text-white placeholder:text-slate-600 h-11 pl-10 rounded-xl focus:border-blue-500/50 focus:ring-blue-500/20"
                                            required
                                        />
                                        <User size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                                    </div>
                                </div>
                            )}

                            <div className="space-y-2">
                                <label htmlFor="auth-email" className="text-xs font-semibold text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
                                    <Mail size={12} /> Email Address
                                </label>
                                <div className="relative">
                                    <Input
                                        id="auth-email"
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        placeholder="admin@company.com"
                                        className="bg-white/[0.06] border-white/[0.1] text-white placeholder:text-slate-600 h-11 pl-10 rounded-xl focus:border-blue-500/50 focus:ring-blue-500/20"
                                        required
                                    />
                                    <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label htmlFor="auth-password" className="text-xs font-semibold text-slate-300 flex items-center gap-1.5 uppercase tracking-wider">
                                    <Lock size={12} /> Password
                                </label>
                                <div className="relative">
                                    <Input
                                        id="auth-password"
                                        type={showPassword ? 'text' : 'password'}
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        placeholder="••••••••••"
                                        className="bg-white/[0.06] border-white/[0.1] text-white placeholder:text-slate-600 h-11 pl-10 pr-10 rounded-xl focus:border-blue-500/50 focus:ring-blue-500/20"
                                        required
                                        minLength={6}
                                    />
                                    <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                                    <button
                                        type="button"
                                        onClick={() => setShowPassword(!showPassword)}
                                        className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                                    >
                                        {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                                    </button>
                                </div>
                            </div>

                            {mode === 'login' && (
                                <div className="text-right">
                                    <Link to="/forgot-password" className="text-xs text-blue-400 hover:text-blue-300 transition-colors">
                                        Forgot password?
                                    </Link>
                                </div>
                            )}

                            {error && (
                                <div className="flex items-center gap-2 bg-red-500/10 border border-red-500/20 rounded-xl p-3">
                                    <Shield size={14} className="text-red-400 shrink-0" />
                                    <p className="text-sm text-red-300">{error}</p>
                                </div>
                            )}

                            <Button
                                type="submit"
                                className="w-full h-11 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold flex items-center justify-center gap-2 rounded-xl shadow-lg shadow-blue-600/20 transition-all hover:shadow-blue-600/30 hover:-translate-y-0.5"
                                disabled={loading}
                            >
                                {loading ? (
                                    <div className="flex items-center gap-2">
                                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                        Authenticating...
                                    </div>
                                ) : (
                                    <>
                                        {mode === 'login' ? 'Sign In to Platform' : 'Create Enterprise Account'}
                                        <ArrowRight size={16} />
                                    </>
                                )}
                            </Button>
                        </form>

                        {/* Divider */}
                        <div className="flex items-center gap-3 my-6">
                            <div className="flex-1 h-px bg-white/[0.08]" />
                            <span className="text-[11px] text-slate-600 uppercase tracking-wider font-medium">or</span>
                            <div className="flex-1 h-px bg-white/[0.08]" />
                        </div>

                        {/* Mode Toggle */}
                        <button
                            type="button"
                            onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(''); }}
                            className="w-full h-11 rounded-xl border border-white/[0.08] text-sm text-slate-400 hover:text-white hover:border-white/20 hover:bg-white/[0.03] transition-all flex items-center justify-center gap-2"
                        >
                            {mode === 'login'
                                ? "Don't have an account? Create one"
                                : 'Already have an account? Sign in'}
                        </button>
                    </div>

                    {/* Dev mode skip */}
                    {flags.authDevBypassEnabled && (
                        <div className="mt-6 text-center">
                            <button
                                type="button"
                                onClick={() => navigate('/')}
                                className="inline-flex items-center gap-1.5 text-xs text-slate-600 hover:text-slate-400 transition-colors group"
                            >
                                <span className="w-1 h-1 rounded-full bg-slate-700 group-hover:bg-amber-500 transition-colors" />
                                Continue without authentication (dev bypass)
                            </button>
                        </div>
                    )}

                    {/* Security badge */}
                    <div className="mt-4 flex items-center justify-center gap-4 text-[11px] text-slate-700">
                        <span className="flex items-center gap-1">
                            <Shield size={10} /> Secure Authentication
                        </span>
                        <span className="flex items-center gap-1">
                            <Lock size={10} /> Encrypted Sessions
                        </span>
                        <span className="flex items-center gap-1">
                            <Activity size={10} /> Enterprise Guardrails
                        </span>
                    </div>
                </div>
            </div>
        </div>
    );
};
