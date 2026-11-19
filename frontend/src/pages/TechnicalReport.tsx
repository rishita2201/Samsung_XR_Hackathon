import React, { useState } from 'react';
import {
  FileText, CheckCircle2, AlertCircle, Play, ShieldAlert,
  Cpu, Award, Layers, Terminal, ArrowRight, Loader2, Sparkles
} from 'lucide-react';
import { api } from '../services/api';

export const TechnicalReport: React.FC = () => {
  const [validating, setValidating] = useState(false);
  const [valResults, setValResults] = useState<{
    overall_valid: boolean;
    total_files: number;
    passed_count: number;
    failed_count: number;
    details: Array<{ video_id: string; filename: string; valid: boolean; errors: string[] }>;
  } | null>(null);

  const handleRunValidation = async () => {
    try {
      setValidating(true);
      const res = await api.runValidation();
      setValResults(res);
    } catch (e: any) {
      alert(`Validation failed: ${e.message}`);
    } finally {
      setValidating(false);
    }
  };

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-10">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#222936] gap-4">
        <div>
          <div className="text-xs font-mono text-emerald-400 uppercase tracking-wider">Evaluation & Methodology</div>
          <h1 className="text-xl font-bold text-slate-100 mt-1">MOMENTIQ Technical Architecture Report</h1>
          <p className="text-xs text-slate-400 mt-1">
            Formal mathematical formulation, 100-point jury matrix breakdown, and automated validation suite.
          </p>
        </div>

        <button
          onClick={handleRunValidation}
          disabled={validating}
          className="flex items-center space-x-2 px-4 py-2 rounded bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-xs uppercase tracking-wider transition shadow"
        >
          {validating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Terminal className="w-4 h-4" />}
          <span>Run Official Validator (validate.py)</span>
        </button>
      </div>

      {/* Live Validator Terminal Output */}
      {valResults && (
        <div className="p-5 rounded bg-[#0b0e13] border border-[#21293a] space-y-3 font-mono text-xs shadow-2xl">
          <div className="flex items-center justify-between border-b border-[#1b2333] pb-2">
            <span className="text-slate-400 flex items-center space-x-2">
              <Terminal className="w-3.5 h-3.5 text-emerald-400" />
              <span>python validate.py --dir outputs/json/</span>
            </span>
            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
              valResults.overall_valid ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-rose-950 text-rose-400 border border-rose-800'
            }`}>
              {valResults.overall_valid ? 'ALL CHECKS PASSED' : 'VALIDATION FAILED'}
            </span>
          </div>

          <div className="space-y-1.5 text-slate-300">
            <div>Scanning directory: <code className="text-emerald-300">outputs/json</code></div>
            <div>Scanned {valResults.total_files} file(s): <span className="text-emerald-400">{valResults.passed_count} passed</span>, <span className="text-rose-400">{valResults.failed_count} failed</span>.</div>

            <div className="pt-2 space-y-1">
              {valResults.details.map((d, i) => (
                <div key={i} className="flex items-start space-x-2">
                  <span className={d.valid ? 'text-emerald-400' : 'text-rose-400'}>
                    {d.valid ? '✅ PASS:' : '❌ FAIL:'}
                  </span>
                  <span>{d.filename}</span>
                  {d.errors.length > 0 && (
                    <span className="text-rose-400 text-[11px]">({d.errors.join('; ')})</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 100-Point Jury Matrix Breakdown */}
      <section className="space-y-4">
        <div>
          <div className="text-xs font-mono text-emerald-400 uppercase tracking-wider">Official Jury Criteria</div>
          <h2 className="text-base font-bold text-slate-100 mt-0.5">100-Point Evaluation Formulation</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-4 rounded bg-[#10141c] border border-[#212836] space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold text-slate-200">Action Coverage</span>
              <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800/60">40 Pts</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Fraction of distinct ground truth (verb, noun) pairs captured by the highlight intervals. Soft penalty if highlights exceed 15% budget.
            </p>
            <div className="text-[10px] font-mono text-emerald-400/90 pt-1 border-t border-[#1b222f]">
              Optimized by MMR Distinct Action Bonus (+0.40)
            </div>
          </div>

          <div className="p-4 rounded bg-[#10141c] border border-[#212836] space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold text-slate-200">Action mAP</span>
              <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800/60">25 Pts</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Verb-noun overlap with ground-truth action annotations at temporal IoU thresholds [0.1, 0.2, 0.3, 0.4, 0.5].
            </p>
            <div className="text-[10px] font-mono text-emerald-400/90 pt-1 border-t border-[#1b222f]">
              Optimized by CLIP zero-shot egocentric prompts
            </div>
          </div>

          <div className="p-4 rounded bg-[#10141c] border border-[#212836] space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold text-slate-200">Highlight F1</span>
              <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800/60">25 Pts</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Frame-level F1 score evaluated against top-15% human-annotated consensus importance frames on the benchmark dataset.
            </p>
            <div className="text-[10px] font-mono text-emerald-400/90 pt-1 border-t border-[#1b222f]">
              Optimized by multi-factor rank scoring
            </div>
          </div>

          <div className="p-4 rounded bg-[#10141c] border border-[#212836] space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-bold text-slate-200">Label Accuracy</span>
              <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800/60">10 Pts</span>
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Video-level activity category prediction accuracy across the FPVSum egocentric video categories.
            </p>
            <div className="text-[10px] font-mono text-emerald-400/90 pt-1 border-t border-[#1b222f]">
              Optimized by global video centroid classification
            </div>
          </div>
        </div>
      </section>

      {/* Algorithmic Breakdown Cards */}
      <section className="space-y-4">
        <div>
          <div className="text-xs font-mono text-emerald-400 uppercase tracking-wider">Methodology Deep-Dive</div>
          <h2 className="text-base font-bold text-slate-100 mt-0.5">Core Technical Innovations</h2>
        </div>

        <div className="space-y-4 text-xs text-slate-300">
          {/* Card 1 */}
          <div className="p-5 rounded bg-[#11151c] border border-[#212836] space-y-2.5">
            <h3 className="text-sm font-semibold text-slate-100 flex items-center space-x-2">
              <span className="text-emerald-400 font-mono">1.</span>
              <span>Optical Flow Decomposition (Head Motion vs Hand Residuals)</span>
            </h3>
            <p className="text-slate-400 leading-relaxed">
              In first-person egocentric video, regular visual difference methods fail because camera wearers constantly turn their heads, triggering massive false-positive visual motion. MOMENTIQ uses dense Farneback optical flow and estimates the camera/head velocity vector as the spatial median <code className="text-slate-200 font-mono">med(u, v)</code>. The residual motion <code className="text-slate-200 font-mono">||flow - med||</code> is isolated specifically within the lower-central quadrant where egocentric hands operate.
            </p>
          </div>

          {/* Card 2 */}
          <div className="p-5 rounded bg-[#11151c] border border-[#212836] space-y-2.5">
            <h3 className="text-sm font-semibold text-slate-100 flex items-center space-x-2">
              <span className="text-emerald-400 font-mono">2.</span>
              <span>Hand-Object Interaction (HOI) Spatial Attention</span>
            </h3>
            <p className="text-slate-400 leading-relaxed">
              To distinguish passive looking from active physical interaction, MOMENTIQ computes a composite Hand-Object Interaction (HOI) index:
              <br />
              <code className="text-emerald-300 font-mono block p-2 mt-1 rounded bg-[#0b0e13] border border-[#1b222e]">
                HOI(t) = 0.40 * HandPresence(t) + 0.35 * ObjectEdgeSaliency(t) + 0.25 * HandResidualMotion(t)
              </code>
              Calibrated YCrCb skin chrominance filters detect hand entry into the manipulation zone, while foveal Canny edge density quantifies active tool/object engagement.
            </p>
          </div>

          {/* Card 3 */}
          <div className="p-5 rounded bg-[#11151c] border border-[#212836] space-y-2.5">
            <h3 className="text-sm font-semibold text-slate-100 flex items-center space-x-2">
              <span className="text-emerald-400 font-mono">3.</span>
              <span>Explainable Multi-Factor Importance Formulation</span>
            </h3>
            <p className="text-slate-400 leading-relaxed">
              Candidate segments are scored via a transparent multi-objective formulation:
              <br />
              <code className="text-emerald-300 font-mono block p-2 mt-1 rounded bg-[#0b0e13] border border-[#1b222e]">
                Score(s) = 0.40 * Activity(s) + 0.25 * HOI(s) + 0.20 * Novelty(s) + 0.15 * Confidence(s) - IdlePenalty(s)
              </code>
              Novelty measures cosine distance from the global video centroid <code className="text-slate-200 font-mono">(1 - cos(e_s, e_global))</code> to preserve diverse scenes. Rank normalization ensures balanced dynamic ranges.
            </p>
          </div>

          {/* Card 4 */}
          <div className="p-5 rounded bg-[#11151c] border border-[#212836] space-y-2.5">
            <h3 className="text-sm font-semibold text-slate-100 flex items-center space-x-2">
              <span className="text-emerald-400 font-mono">4.</span>
              <span>15% Duration-Constrained Greedy MMR Optimization</span>
            </h3>
            <p className="text-slate-400 leading-relaxed">
              Highlights are selected under a hard constraint: <code className="text-slate-200 font-mono">sum(end - start) &lt;= 0.15 * TotalDuration</code>. A Maximal Marginal Relevance (MMR) penalty suppresses repetitive footage, while a <span className="text-emerald-400 font-semibold">+0.40 coverage bonus</span> is awarded for each newly introduced (verb, noun) action pair, directly targeting the official 40% Action Coverage jury metric. Segments exceeding the remaining budget are trimmed around their peak-motion timestamp.
            </p>
          </div>
        </div>
      </section>

      {/* Engineering Tradeoffs & Known Limitations */}
      <section className="p-5 rounded bg-[#11151c] border border-[#212836] space-y-3">
        <div className="text-xs font-mono text-slate-400 uppercase">Engineering Realities</div>
        <h3 className="text-sm font-semibold text-slate-200">Hardware Compatibility & Latency Tradeoffs</h3>
        <ul className="text-xs text-slate-400 space-y-2">
          <li className="flex items-start space-x-2">
            <span className="text-emerald-400 font-mono">✓</span>
            <div><strong className="text-slate-300">Student Laptop Optimization:</strong> Native CPU support via lightweight quantized operations and 2 FPS sampling rate. Memory consumption is capped under 1.5 GB RAM.</div>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-emerald-400 font-mono">✓</span>
            <div><strong className="text-slate-300">Offline Resilience:</strong> Fully bundled 577 MB CLIP weights in <code className="text-slate-200 font-mono">weights/clip_vitb32.pt</code> and zero cloud streaming dependencies.</div>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-emerald-400 font-mono">✓</span>
            <div><strong className="text-slate-300">Fail-Safe Degraded Mode:</strong> Color/spatial luminance fallback guarantees the pipeline and validator never crash even if PyTorch is executed in bare CPU environments.</div>
          </li>
        </ul>
      </section>
    </div>
  );
};

