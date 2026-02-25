import { useState, useEffect } from 'react';
import { agentClient } from '../features/agent/api/agentClient';
import { Button } from '../shared/ui/Button';
import { Badge } from '../shared/ui/Badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../shared/ui/Table';
import { Play, CheckCircle2, XCircle, Clock, BarChart3, RefreshCw, Zap } from 'lucide-react';

interface EvalCase {
    case_id: string;
    goal: string;
    category: string;
    difficulty: string;
    passed: boolean;
    score: number;
    keyword_score: number;
    tool_score: number;
    llm_score: number;
    latency: number;
    tools_used: string[];
    error?: string;
}

interface EvalSuite {
    suite_id: string;
    suite_name: string;
    total: number;
    passed: number;
    failed: number;
    avg_score: number;
    avg_latency: number;
    results: EvalCase[];
    timestamp: string;
}

const ScoreBar = ({ score, label }: { score: number; label: string }) => (
    <div className="space-y-1">
        <div className="flex justify-between text-xs">
            <span className="text-slate-500">{label}</span>
            <span className="font-mono font-bold text-slate-700">{score.toFixed(0)}%</span>
        </div>
        <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
            <div
                className={`h-full rounded-full transition-all duration-500 ${score >= 70 ? 'bg-green-500' : score >= 40 ? 'bg-amber-500' : 'bg-red-500'
                    }`}
                style={{ width: `${Math.max(score, 2)}%` }}
            />
        </div>
    </div>
);

export const EvalPage = () => {
    const [suiteHistory, setSuiteHistory] = useState<any[]>([]);
    const [activeResult, setActiveResult] = useState<EvalSuite | null>(null);
    const [running, setRunning] = useState(false);
    const [loading, setLoading] = useState(true);

    // Load past results
    useEffect(() => {
        loadHistory();
    }, []);

    const loadHistory = async () => {
        try {
            const data = await agentClient.getEvalResults();
            setSuiteHistory(data);
        } catch {
            // empty
        } finally {
            setLoading(false);
        }
    };

    const runSuite = async () => {
        setRunning(true);
        try {
            const result = await agentClient.runEvalSuite('manual-run');
            setActiveResult(result);
            await loadHistory();
        } catch (e: any) {
            alert(`Eval failed: ${e.message}`);
        } finally {
            setRunning(false);
        }
    };

    const loadDetail = async (suiteId: string) => {
        try {
            const result = await agentClient.getEvalResult(suiteId);
            setActiveResult(result);
        } catch {
            // empty
        }
    };

    return (
        <div className="space-y-6 max-w-6xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
                        <BarChart3 className="text-purple-600" /> Evaluation Engine
                    </h1>
                    <p className="text-sm text-slate-500 mt-1">
                        Run test suites to measure agent quality, accuracy, and performance
                    </p>
                </div>
                <Button
                    onClick={runSuite}
                    disabled={running}
                    className="flex items-center gap-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white"
                >
                    {running ? (
                        <>
                            <RefreshCw size={16} className="animate-spin" /> Running...
                        </>
                    ) : (
                        <>
                            <Play size={16} /> Run Test Suite
                        </>
                    )}
                </Button>
            </div>

            {/* Active Result */}
            {activeResult && (
                <div className="space-y-4">
                    {/* Summary Cards */}
                    <div className="grid grid-cols-4 gap-4">
                        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
                            <p className="text-xs text-slate-500 uppercase tracking-wider">Overall Score</p>
                            <p className={`text-3xl font-bold mt-1 ${activeResult.avg_score >= 70 ? 'text-green-600' :
                                    activeResult.avg_score >= 40 ? 'text-amber-600' : 'text-red-600'
                                }`}>
                                {activeResult.avg_score.toFixed(1)}%
                            </p>
                        </div>
                        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
                            <p className="text-xs text-slate-500 uppercase tracking-wider">Passed</p>
                            <p className="text-3xl font-bold text-green-600 mt-1">
                                {activeResult.passed}
                                <span className="text-sm text-slate-400 font-normal">/{activeResult.total}</span>
                            </p>
                        </div>
                        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
                            <p className="text-xs text-slate-500 uppercase tracking-wider">Failed</p>
                            <p className="text-3xl font-bold text-red-600 mt-1">{activeResult.failed}</p>
                        </div>
                        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm">
                            <p className="text-xs text-slate-500 uppercase tracking-wider">Avg Latency</p>
                            <p className="text-3xl font-bold text-blue-600 mt-1 flex items-center gap-1">
                                <Clock size={20} /> {activeResult.avg_latency.toFixed(1)}s
                            </p>
                        </div>
                    </div>

                    {/* Per-Case Results */}
                    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                        <div className="p-4 border-b border-slate-200 bg-slate-50">
                            <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                                <Zap size={16} className="text-amber-500" />
                                Test Case Results — {activeResult.suite_name}
                            </h3>
                        </div>
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Case</TableHead>
                                    <TableHead>Goal</TableHead>
                                    <TableHead>Status</TableHead>
                                    <TableHead>Score</TableHead>
                                    <TableHead>Breakdown</TableHead>
                                    <TableHead>Latency</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {activeResult.results.map((r) => (
                                    <TableRow key={r.case_id}>
                                        <TableCell className="font-mono text-xs">{r.case_id}</TableCell>
                                        <TableCell className="max-w-xs truncate text-sm">{r.goal}</TableCell>
                                        <TableCell>
                                            {r.passed ? (
                                                <Badge variant="green" className="flex items-center gap-1 w-fit">
                                                    <CheckCircle2 size={12} /> Pass
                                                </Badge>
                                            ) : (
                                                <Badge variant="red" className="flex items-center gap-1 w-fit">
                                                    <XCircle size={12} /> Fail
                                                </Badge>
                                            )}
                                        </TableCell>
                                        <TableCell>
                                            <span className={`font-bold ${r.score >= 70 ? 'text-green-600' :
                                                    r.score >= 40 ? 'text-amber-600' : 'text-red-600'
                                                }`}>
                                                {r.score.toFixed(0)}%
                                            </span>
                                        </TableCell>
                                        <TableCell className="min-w-[200px]">
                                            <div className="space-y-1">
                                                <ScoreBar score={r.keyword_score} label="Keywords" />
                                                <ScoreBar score={r.tool_score} label="Tools" />
                                                <ScoreBar score={r.llm_score} label="LLM Judge" />
                                            </div>
                                        </TableCell>
                                        <TableCell className="font-mono text-xs">{r.latency}s</TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </div>
                </div>
            )}

            {/* History */}
            {suiteHistory.length > 0 && (
                <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                    <div className="p-4 border-b border-slate-200 bg-slate-50">
                        <h3 className="font-semibold text-slate-800">Past Evaluation Runs</h3>
                    </div>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Suite</TableHead>
                                <TableHead>Score</TableHead>
                                <TableHead>Pass/Fail</TableHead>
                                <TableHead>Avg Latency</TableHead>
                                <TableHead>Date</TableHead>
                                <TableHead className="text-right">Actions</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {suiteHistory.map((s: any) => (
                                <TableRow key={s.suite_id}>
                                    <TableCell className="font-medium">{s.suite_name}</TableCell>
                                    <TableCell className="font-bold">{s.avg_score?.toFixed(1)}%</TableCell>
                                    <TableCell>
                                        <span className="text-green-600">{s.passed}</span> /
                                        <span className="text-red-600 ml-1">{s.failed}</span>
                                    </TableCell>
                                    <TableCell>{s.avg_latency?.toFixed(1)}s</TableCell>
                                    <TableCell className="text-xs text-slate-500">
                                        {s.timestamp ? new Date(s.timestamp).toLocaleString() : '-'}
                                    </TableCell>
                                    <TableCell className="text-right">
                                        <Button variant="ghost" size="sm" onClick={() => loadDetail(s.suite_id)}>
                                            View Details
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </div>
            )}

            {!activeResult && !loading && suiteHistory.length === 0 && (
                <div className="bg-white border-2 border-dashed border-slate-200 rounded-xl p-16 text-center">
                    <BarChart3 size={48} className="text-slate-300 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-slate-600 mb-2">No evaluations yet</h3>
                    <p className="text-sm text-slate-400 mb-4">
                        Click "Run Test Suite" to execute your first agent evaluation benchmark.
                    </p>
                </div>
            )}
        </div>
    );
};
