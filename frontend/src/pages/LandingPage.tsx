import React from 'react';
import { Play, UploadCloud, Cpu, Zap, CheckCircle2, ArrowRight, ShieldCheck, Video, Sparkles } from 'lucide-react';
import { ActiveTab } from '../components/Navbar';

interface LandingPageProps {
  onNavigate: (tab: ActiveTab) => void;
  onSelectSyntheticDemo: () => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onNavigate, onSelectSyntheticDemo }) => {
  return (
    <div className="space-y-16 py-10 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
      {/* Hero Header */}
      <section className="relative text-center max-w-3xl mx-auto pt-6 pb-2">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#141b24] border border-[#232f42] text-xs font-mono text-emerald-400 mb-6">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span>SAMSUNG R&D INSTITUTE INDIA · XR HACKATHON 2026</span>
        </div>

        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight text-slate-100 uppercase">
          MOMENT<span className="text-emerald-400">IQ</span>
        </h1>
        <p className="mt-3 text-lg font-medium text-slate-300">
          Intelligent First-Person Video Understanding & Highlight Generation
        </p>
        <p className="mt-2 text-sm text-slate-400 max-w-2xl mx-auto leading-relaxed">
          Unlike conventional summarizers that trigger on generic pixel changes, MOMENTIQ decodes <span className="text-slate-200 font-medium">WHAT is happening</span>: identifying human activities, hand-object interactions, and critical temporal events within egocentric footage.
        </p>

        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <button
            onClick={() => onNavigate('ingest')}
            className="flex items-center space-x-2 px-5 py-2.5 rounded bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-xs tracking-wide uppercase transition shadow-lg shadow-emerald-950/40"
          >
            <UploadCloud className="w-4 h-4" />
            <span>Open Ingestion Workspace</span>
          </button>

          <button
            onClick={onSelectSyntheticDemo}
            className="flex items-center space-x-2 px-5 py-2.5 rounded bg-[#161c26] hover:bg-[#1e2634] text-slate-200 border border-[#2b3545] font-semibold text-xs tracking-wide uppercase transition"
          >
            <Play className="w-4 h-4 text-emerald-400" />
            <span>Load Verified Demo Video</span>
          </button>
        </div>
      </section>

      {/* Official Challenge Specification Banner */}
      <section className="border border-[#222936] bg-[#0e1218] rounded p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="text-xs font-mono text-emerald-400 tracking-wider uppercase mb-1">Challenge Contract</div>
            <h2 className="text-base font-semibold text-slate-200">Track 4: Action-Aware Video Summarization</h2>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl">
              Pruning dense egocentric streams into concise, action-dense highlights for downstream XR headsets and wearables. Compiled strictly from original footage with a hard 15% duration ceiling.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-left">
            <div className="p-2.5 rounded bg-[#141820] border border-[#202733]">
              <div className="text-[11px] text-slate-400">Target Budget</div>
              <div className="text-sm font-mono font-bold text-emerald-400">≤ 15.0%</div>
            </div>
            <div className="p-2.5 rounded bg-[#141820] border border-[#202733]">
              <div className="text-[11px] text-slate-400">Action mAP</div>
              <div className="text-sm font-mono font-bold text-slate-200">25 Pts</div>
            </div>
            <div className="p-2.5 rounded bg-[#141820] border border-[#202733]">
              <div className="text-[11px] text-slate-400">Action Coverage</div>
              <div className="text-sm font-mono font-bold text-slate-200">40 Pts</div>
            </div>
            <div className="p-2.5 rounded bg-[#141820] border border-[#202733]">
              <div className="text-[11px] text-slate-400">Highlight F1</div>
              <div className="text-sm font-mono font-bold text-slate-200">25 Pts</div>
            </div>
          </div>
        </div>
      </section>

      {/* 3-Step Architecture Flow */}
      <section className="space-y-6">
        <div className="text-center">
          <div className="text-xs font-mono text-emerald-400 uppercase tracking-widest">End-to-End Pipeline</div>
          <h2 className="text-xl font-bold text-slate-200 mt-1">Algorithmic Workflow</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <div className="p-5 rounded bg-[#11151c] border border-[#212836] space-y-3">
            <div className="w-8 h-8 rounded bg-[#18202c] border border-[#2d3a4e] flex items-center justify-center text-emerald-400 font-mono text-xs font-bold">
              01
            </div>
            <h3 className="text-sm font-semibold text-slate-200">Ingest & Flow Decomposition</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              OpenCV adaptive frame sampling at 2 FPS. Dense Farneback optical flow splits global head motion from residual manipulation-zone velocity, eliminating false triggers caused by head swaying.
            </p>
            <div className="text-[11px] font-mono text-emerald-400/90 bg-emerald-950/40 p-2 rounded border border-emerald-900/40">
              Module A & B: Metadata + Optical Flow
            </div>
          </div>

          <div className="p-5 rounded bg-[#11151c] border border-[#212836] space-y-3">
            <div className="w-8 h-8 rounded bg-[#18202c] border border-[#2d3a4e] flex items-center justify-center text-emerald-400 font-mono text-xs font-bold">
              02
            </div>
            <h3 className="text-sm font-semibold text-slate-200">HOI Dynamics & Action Perception</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Dual-stage perception: spatial skin-color probability & foveal object edge density measure hand-object contact. Offline CLIP ViT-B/32 generates zero-shot EPIC-KITCHENS verb/noun predictions.
            </p>
            <div className="text-[11px] font-mono text-emerald-400/90 bg-emerald-950/40 p-2 rounded border border-emerald-900/40">
              Module C & D: Pretrained CLIP + HOI Filter
            </div>
          </div>

          <div className="p-5 rounded bg-[#11151c] border border-[#212836] space-y-3">
            <div className="w-8 h-8 rounded bg-[#18202c] border border-[#2d3a4e] flex items-center justify-center text-emerald-400 font-mono text-xs font-bold">
              03
            </div>
            <h3 className="text-sm font-semibold text-slate-200">15% Budget Highlight Selection</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Explainable multi-factor scoring (activity, novelty, interaction, confidence). Greedy MMR selection awards distinct action pair bonuses to optimize official 40% Action Coverage under hard 15% budget.
            </p>
            <div className="text-[11px] font-mono text-emerald-400/90 bg-emerald-950/40 p-2 rounded border border-emerald-900/40">
              Module E-H: MMR Knapsack + FFmpeg Concat
            </div>
          </div>
        </div>
      </section>

      {/* Dataset & Compliance Checklist */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-5 rounded bg-[#11151c] border border-[#212836] space-y-3">
          <div className="text-xs font-mono text-emerald-400 uppercase">Evaluation Datasets</div>
          <h3 className="text-sm font-semibold text-slate-200">Samsung Official Validation Benchmarks</h3>
          <ul className="text-xs text-slate-400 space-y-2 mt-2">
            <li className="flex items-start space-x-2">
              <span className="text-emerald-400 font-mono font-bold">▸</span>
              <div><strong className="text-slate-300">EPIC-KITCHENS-100:</strong> 138 validation videos with dense ground-truth verb-noun action annotations and timestamps.</div>
            </li>
            <li className="flex items-start space-x-2">
              <span className="text-emerald-400 font-mono font-bold">▸</span>
              <div><strong className="text-slate-300">FPVSum:</strong> 49 videos with human consensus importance frames and video-level category labels.</div>
            </li>
            <li className="flex items-start space-x-2">
              <span className="text-emerald-400 font-mono font-bold">▸</span>
              <div><strong className="text-slate-300">Deterministic Run Contract:</strong> One-line CLI: <code className="text-emerald-300 font-mono">./run.sh &lt;video.mp4&gt; &lt;out.json&gt;</code></div>
            </li>
          </ul>
        </div>

        <div className="p-5 rounded bg-[#11151c] border border-[#212836] space-y-3">
          <div className="text-xs font-mono text-emerald-400 uppercase">Submissions Compliance</div>
          <h3 className="text-sm font-semibold text-slate-200">Strict Track 4 Schema Enforcement</h3>
          <ul className="text-xs text-slate-400 space-y-2 mt-2">
            <li className="flex items-start space-x-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
              <span><strong className="text-slate-300">All 6 Required Schema Keys:</strong> <code className="text-slate-300 font-mono">video_id, label, actions, highlights, duration, highlight_ratio</code></span>
            </li>
            <li className="flex items-start space-x-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
              <span><strong className="text-slate-300">Temporal Validity:</strong> Non-overlapping, sorted chronologically, normalized importance in [0.0, 1.0].</span>
            </li>
            <li className="flex items-start space-x-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
              <span><strong className="text-slate-300">Real Original Footage:</strong> Zero synthetic hallucinated video frames — FFmpeg extracts original footage only.</span>
            </li>
          </ul>
        </div>
      </section>
    </div>
  );
};

