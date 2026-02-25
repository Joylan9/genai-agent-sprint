import { useState, useRef, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { agentClient } from '../features/agent/api/agentClient';
import { Button } from '../shared/ui/Button';
import { Input } from '../shared/ui/Input';
import {
    Zap, Mail, Lock, ArrowRight, ArrowLeft,
    Shield, CheckCircle2, KeyRound, RefreshCw,
    Eye, EyeOff, Clock,
} from 'lucide-react';

type Step = 'email' | 'otp' | 'reset' | 'success';

export const ForgotPasswordPage = () => {
    const navigate = useNavigate();

    const [step, setStep] = useState<Step>('email');
    const [email, setEmail] = useState('');
    const [otp, setOtp] = useState(['', '', '', '', '', '']);
    const [resetToken, setResetToken] = useState('');
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [countdown, setCountdown] = useState(0);
    const [canResend, setCanResend] = useState(false);
    const [devNotice, setDevNotice] = useState('');

    const otpRefs = useRef<(HTMLInputElement | null)[]>([]);

    // Countdown timer for resend
    useEffect(() => {
        if (countdown <= 0) {
            setCanResend(true);
            return;
        }
        setCanResend(false);
        const timer = setTimeout(() => setCountdown(c => c - 1), 1000);
        return () => clearTimeout(timer);
    }, [countdown]);

    // ── Step 1: Request OTP ──
    const handleRequestOtp = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setDevNotice('');
        setLoading(true);
        try {
            const res = await agentClient.requestOtp(email);
            setStep('otp');
            setCountdown(60);
            // Dev mode: auto-fill OTP when SMTP is not configured
            if (res?.dev_otp) {
                const digits = String(res.dev_otp).split('');
                setOtp(digits);
                setDevNotice(`Dev mode: SMTP not configured. OTP auto-filled: ${res.dev_otp}`);
            }
        } catch (err: any) {
            setError(err?.response?.data?.detail || err?.message || 'Failed to send code');
        } finally {
            setLoading(false);
        }
    };

    // ── Resend OTP ──
    const handleResend = async () => {
        setError('');
        setDevNotice('');
        setLoading(true);
        try {
            const res = await agentClient.requestOtp(email);
            setCountdown(60);
            setOtp(['', '', '', '', '', '']);
            // Dev mode: auto-fill OTP
            if (res?.dev_otp) {
                const digits = String(res.dev_otp).split('');
                setOtp(digits);
                setDevNotice(`Dev mode: SMTP not configured. OTP auto-filled: ${res.dev_otp}`);
            }
        } catch (err: any) {
            setError(err?.message || 'Failed to resend');
        } finally {
            setLoading(false);
        }
    };

    // ── Step 2: Verify OTP ──
    const handleVerifyOtp = async () => {
        const code = otp.join('');
        if (code.length < 6) { setError('Please enter the full 6-digit code'); return; }
        setError('');
        setLoading(true);
        try {
            const res = await agentClient.verifyOtp(email, code);
            setResetToken(res.reset_token);
            setStep('reset');
        } catch (err: any) {
            setError(err?.response?.data?.detail || err?.message || 'Invalid code');
        } finally {
            setLoading(false);
        }
    };

    // ── Step 3: Reset Password ──
    const handleResetPassword = async (e: React.FormEvent) => {
        e.preventDefault();
        if (newPassword !== confirmPassword) { setError('Passwords do not match'); return; }
        setError('');
        setLoading(true);
        try {
            await agentClient.resetPassword(resetToken, newPassword);
            setStep('success');
        } catch (err: any) {
            setError(err?.response?.data?.detail || err?.message || 'Failed to reset password');
        } finally {
            setLoading(false);
        }
    };

    // ── OTP Input Handler ──
    const handleOtpChange = (idx: number, value: string) => {
        if (!/^\d*$/.test(value)) return;
        const next = [...otp];
        next[idx] = value.slice(-1);
        setOtp(next);
        if (value && idx < 5) otpRefs.current[idx + 1]?.focus();
    };

    const handleOtpKeyDown = (idx: number, e: React.KeyboardEvent) => {
        if (e.key === 'Backspace' && !otp[idx] && idx > 0) {
            otpRefs.current[idx - 1]?.focus();
        }
    };

    const handleOtpPaste = (e: React.ClipboardEvent) => {
        const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
        if (pasted.length === 6) {
            setOtp(pasted.split(''));
            otpRefs.current[5]?.focus();
        }
    };

    // ── Step Progress ──
    const steps = [
        { id: 'email', label: 'Email', num: 1 },
        { id: 'otp', label: 'Verify', num: 2 },
        { id: 'reset', label: 'Reset', num: 3 },
    ];
    const currentStepIdx = steps.findIndex(s => s.id === step);

    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-950 px-4 relative overflow-hidden">
            {/* Background effects */}
            <div className="absolute top-0 left-1/3 w-[500px] h-[500px] bg-blue-500/[0.07] rounded-full blur-[120px]" />
            <div className="absolute bottom-0 right-1/4 w-[400px] h-[400px] bg-indigo-500/[0.07] rounded-full blur-[100px]" />

            <div className="w-full max-w-[460px] relative z-10">
                {/* Logo */}
                <div className="text-center mb-8">
                    <Link to="/login" className="inline-flex items-center gap-2.5 mb-4 group">
                        <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
                            <Zap size={20} className="text-white" />
                        </div>
                        <span className="text-xl font-bold text-white tracking-tight">TraceAI</span>
                    </Link>
                </div>

                {/* Step Progress Indicator (hidden on success) */}
                {step !== 'success' && (
                    <div className="flex items-center justify-center gap-2 mb-8">
                        {steps.map((s, i) => (
                            <div key={s.id} className="flex items-center gap-2">
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-300 ${i < currentStepIdx
                                    ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/30'
                                    : i === currentStepIdx
                                        ? 'bg-gradient-to-br from-blue-500 to-indigo-600 text-white shadow-lg shadow-blue-500/30 scale-110'
                                        : 'bg-white/[0.06] text-slate-600 border border-white/[0.08]'
                                    }`}>
                                    {i < currentStepIdx ? <CheckCircle2 size={14} /> : s.num}
                                </div>
                                <span className={`text-xs font-medium hidden sm:block ${i === currentStepIdx ? 'text-white' : 'text-slate-600'
                                    }`}>{s.label}</span>
                                {i < steps.length - 1 && (
                                    <div className={`w-8 h-px mx-1 ${i < currentStepIdx ? 'bg-emerald-500' : 'bg-white/[0.08]'
                                        }`} />
                                )}
                            </div>
                        ))}
                    </div>
                )}

                {/* Card */}
                <div className="bg-white/[0.04] backdrop-blur-2xl border border-white/[0.08] rounded-2xl p-8 shadow-2xl">

                    {/* ============================== */}
                    {/* STEP 1: Enter Email            */}
                    {/* ============================== */}
                    {step === 'email' && (
                        <>
                            <div className="text-center mb-6">
                                <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-blue-500/10 border border-blue-500/20 mb-4">
                                    <Mail size={24} className="text-blue-400" />
                                </div>
                                <h2 className="text-xl font-bold text-white mb-1">Forgot Password?</h2>
                                <p className="text-sm text-slate-400">Enter your email and we'll send a verification code</p>
                            </div>
                            <form onSubmit={handleRequestOtp} className="space-y-4">
                                <div className="relative">
                                    <Input
                                        id="reset-email"
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        placeholder="admin@company.com"
                                        className="bg-white/[0.06] border-white/[0.1] text-white placeholder:text-slate-600 h-12 pl-10 rounded-xl"
                                        required
                                    />
                                    <Mail size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                                </div>
                                {error && <p className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg p-2.5">{error}</p>}
                                <Button type="submit" disabled={loading} className="w-full h-11 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold rounded-xl flex items-center justify-center gap-2">
                                    {loading ? <RefreshCw size={16} className="animate-spin" /> : <><span>Send Verification Code</span><ArrowRight size={16} /></>}
                                </Button>
                            </form>
                        </>
                    )}

                    {/* ============================== */}
                    {/* STEP 2: Enter OTP               */}
                    {/* ============================== */}
                    {step === 'otp' && (
                        <>
                            <div className="text-center mb-6">
                                <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 mb-4">
                                    <KeyRound size={24} className="text-indigo-400" />
                                </div>
                                <h2 className="text-xl font-bold text-white mb-1">Enter Verification Code</h2>
                                <p className="text-sm text-slate-400">
                                    We sent a 6-digit code to <span className="text-blue-400 font-medium">{email}</span>
                                </p>
                            </div>

                            {/* OTP Input Grid */}
                            <div className="flex justify-center gap-3 mb-5" onPaste={handleOtpPaste}>
                                {otp.map((digit, idx) => (
                                    <input
                                        key={idx}
                                        ref={el => { otpRefs.current[idx] = el; }}
                                        type="text"
                                        inputMode="numeric"
                                        maxLength={1}
                                        value={digit}
                                        onChange={(e) => handleOtpChange(idx, e.target.value)}
                                        onKeyDown={(e) => handleOtpKeyDown(idx, e)}
                                        className={`w-12 h-14 text-center text-xl font-bold rounded-xl border transition-all duration-200 outline-none ${digit
                                            ? 'bg-blue-500/10 border-blue-500/40 text-white shadow-lg shadow-blue-500/10'
                                            : 'bg-white/[0.04] border-white/[0.1] text-white'
                                            } focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20`}
                                    />
                                ))}
                            </div>

                            {error && <p className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg p-2.5 mb-4 text-center">{error}</p>}

                            {/* Dev mode notice */}
                            {devNotice && (
                                <div className="text-sm text-amber-300 bg-amber-500/10 border border-amber-500/20 rounded-lg p-2.5 mb-4 text-center">
                                    ⚠️ {devNotice}
                                </div>
                            )}

                            <Button onClick={handleVerifyOtp} disabled={loading || otp.join('').length < 6} className="w-full h-11 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold rounded-xl flex items-center justify-center gap-2 mb-4">
                                {loading ? <RefreshCw size={16} className="animate-spin" /> : <><span>Verify Code</span><ArrowRight size={16} /></>}
                            </Button>

                            {/* Resend / Timer */}
                            <div className="text-center">
                                {canResend ? (
                                    <button onClick={handleResend} disabled={loading} className="text-sm text-blue-400 hover:text-blue-300 transition-colors">
                                        Resend Code
                                    </button>
                                ) : (
                                    <span className="text-sm text-slate-500 flex items-center justify-center gap-1.5">
                                        <Clock size={12} /> Resend in {countdown}s
                                    </span>
                                )}
                            </div>
                        </>
                    )}

                    {/* ============================== */}
                    {/* STEP 3: New Password            */}
                    {/* ============================== */}
                    {step === 'reset' && (
                        <>
                            <div className="text-center mb-6">
                                <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 mb-4">
                                    <Lock size={24} className="text-emerald-400" />
                                </div>
                                <h2 className="text-xl font-bold text-white mb-1">Create New Password</h2>
                                <p className="text-sm text-slate-400">Your identity has been verified. Set your new password.</p>
                            </div>
                            <form onSubmit={handleResetPassword} className="space-y-4">
                                <div className="space-y-2">
                                    <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">New Password</label>
                                    <div className="relative">
                                        <Input
                                            id="new-password"
                                            type={showPassword ? 'text' : 'password'}
                                            value={newPassword}
                                            onChange={(e) => setNewPassword(e.target.value)}
                                            placeholder="••••••••••"
                                            className="bg-white/[0.06] border-white/[0.1] text-white placeholder:text-slate-600 h-12 pl-10 pr-10 rounded-xl"
                                            required
                                            minLength={6}
                                        />
                                        <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                                        <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300">
                                            {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                                        </button>
                                    </div>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Confirm Password</label>
                                    <div className="relative">
                                        <Input
                                            id="confirm-password"
                                            type="password"
                                            value={confirmPassword}
                                            onChange={(e) => setConfirmPassword(e.target.value)}
                                            placeholder="••••••••••"
                                            className="bg-white/[0.06] border-white/[0.1] text-white placeholder:text-slate-600 h-12 pl-10 rounded-xl"
                                            required
                                            minLength={6}
                                        />
                                        <Lock size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                                    </div>
                                </div>
                                {/* Password strength indicator */}
                                <div className="space-y-1">
                                    <div className="flex gap-1">
                                        {[1, 2, 3, 4].map(i => (
                                            <div key={i} className={`h-1 flex-1 rounded-full transition-all ${newPassword.length >= i * 3
                                                ? newPassword.length >= 12 ? 'bg-emerald-500' : newPassword.length >= 8 ? 'bg-amber-500' : 'bg-red-500'
                                                : 'bg-white/[0.06]'
                                                }`} />
                                        ))}
                                    </div>
                                    <p className="text-[11px] text-slate-500">{
                                        newPassword.length === 0 ? '' :
                                            newPassword.length < 6 ? 'Too short' :
                                                newPassword.length < 8 ? 'Fair' :
                                                    newPassword.length < 12 ? 'Good' : 'Strong'
                                    }</p>
                                </div>
                                {error && <p className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg p-2.5">{error}</p>}
                                <Button type="submit" disabled={loading} className="w-full h-11 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-semibold rounded-xl flex items-center justify-center gap-2">
                                    {loading ? <RefreshCw size={16} className="animate-spin" /> : <><Shield size={16} /><span>Reset Password</span></>}
                                </Button>
                            </form>
                        </>
                    )}

                    {/* ============================== */}
                    {/* STEP 4: Success                 */}
                    {/* ============================== */}
                    {step === 'success' && (
                        <div className="text-center py-4">
                            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 mb-5">
                                <CheckCircle2 size={32} className="text-emerald-400" />
                            </div>
                            <h2 className="text-xl font-bold text-white mb-2">Password Reset Complete</h2>
                            <p className="text-sm text-slate-400 mb-6">Your password has been updated successfully. You can now sign in with your new credentials.</p>
                            <Button onClick={() => navigate('/login')} className="w-full h-11 bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold rounded-xl flex items-center justify-center gap-2">
                                <ArrowRight size={16} /> Sign In Now
                            </Button>
                        </div>
                    )}
                </div>

                {/* Back to login link */}
                {step !== 'success' && (
                    <div className="mt-6 text-center">
                        <Link to="/login" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-300 transition-colors">
                            <ArrowLeft size={14} /> Back to Sign In
                        </Link>
                    </div>
                )}

                {/* Security footer */}
                <div className="mt-4 flex items-center justify-center gap-4 text-[11px] text-slate-700">
                    <span className="flex items-center gap-1"><Shield size={10} /> Secure Authentication</span>
                    <span className="flex items-center gap-1"><Lock size={10} /> Encrypted Sessions</span>
                </div>
            </div>
        </div>
    );
};
