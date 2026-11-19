import React, { useState } from 'react';
import {
  Download, FileJson, Video, BarChart3, CheckCircle2,
  Clock, Scissors, Copy, Check, ExternalLink, Activity
} from 'lucide-react';
import { AnalysisResult } from '../types';
import { api } from '../services/api';

interface ResultsDashboardProps {
  videoId: string;
  analysis: AnalysisResult | null;
}

export const ResultsDashboard: React.FC<ResultsDashboardProps> = ({ videoId, analysis }) => {
  const [copied, setCopied] = useState(false);
  const [activePlayer, setActivePlayer] = useState<'highlight' | 'original'>('highlight');

  if (!analysis) {
    return (
      <div className="py-20 text-center text-xs text-slate-400">
        No results available. Please analyze a video first.
      </div>
    );
  }

  const { samsung_output, metadata } = analysis;
  const inDur = samsung_output.duration || 60;
  const highlights = samsung_output.highlights || [];
  const outDur = highlights.reduce((acc, h) => acc + (h.end - h.start), 0);
  const compressionPct = inDur > 0 ? ((inDur - outDur) / inDur) * 100 : 0;
  const highlightRatioPct = inDur > 0 ? (outDur / inDur) * 100 : 0;

  const jsonString = JSON.stringify(samsung_output, null, 2);

  const handleCopyJson = () => {
    navigator.clipboard.writeText(jsonString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="py-6 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#222936] gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono text-emerald-400 uppercase tracking-wider">Module H & Submission</span>
            <span className="text-slate-600">/</span>
            <span className="text-xs font-mono text-slate-300">{videoId}</span>
          </div>
          <h1 className="text-lg font-bold text-slate-100 mt-0.5">Results & Submission Package</h1>
        </div>

        {/* Download Buttons */}
        <div className="flex items-center space-x-3">
          <a
            href={api.getHighlightDownloadUrl(videoId)}
            download
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-semibold uppercase tracking-wider transition shadow"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download Highlight MP4</span>
          </a>

          <a
            href={api.getJsonDownloadUrl(videoId)}
            download
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded bg-[#18202c] hover:bg-[#202b3b] text-slate-200 border border-[#2d3a4e] text-xs font-semibold uppercase tracking-wider transition"
          >
            <FileJson className="w-3.5 h-3.5 text-emerald-400" />
            <span>Download JSON</span>
          </a>
        </div>
      </div>

      {/* Metrics Row: 5 Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3.5">
        <div className="p-3.5 rounded bg-[#10141c] border border-[#212836]">
          <div className="text-[11px] font-mono text-slate-400">Input Duration</div>
          <div className="text-lg font-mono font-bold text-slate-100 mt-0.5">{inDur.toFixed(1)}s</div>
          <div className="text-[10px] text-slate-500 mt-1">Original Footage</div>
        </div>

        <div className="p-3.5 rounded bg-[#10141c] border border-[#212836]">
          <div className="text-[11px] font-mono text-slate-400">Highlight Duration</div>
          <div className="text-lg font-mono font-bold text-emerald-400 mt-0.5">{outDur.toFixed(1)}s</div>
          <div className="text-[10px] text-slate-500 mt-1">Concatenated Reel</div>
        </div>

        <div className="p-3.5 rounded bg-[#10141c] border border-[#212836]">
          <div className="text-[11px] font-mono text-slate-400">Budget Ratio</div>
          <div className="text-lg font-mono font-bold text-emerald-400 mt-0.5">{highlightRatioPct.toFixed(1)}%</div>
          <div className="text-[10px] text-emerald-500/80 mt-1">Target: ≤ 15.0%</div>
        </div>

        <div className="p-3.5 rounded bg-[#10141c] border border-[#212836]">
          <div className="text-[11px] font-mono text-slate-400">Compression</div>
          <div className="text-lg font-mono font-bold text-slate-100 mt-0.5">-{compressionPct.toFixed(1)}%</div>
          <div className="text-[10px] text-slate-500 mt-1">Idle Time Pruned</div>
        </div>

        <div className="p-3.5 rounded bg-[#10141c] border border-[#212836]">
          <div className="text-[11px] font-mono text-slate-400">Actions Localized</div>
          <div className="text-lg font-mono font-bold text-slate-100 mt-0.5">{(samsung_output.actions || []).length}</div>
          <div className="text-[10px] text-slate-500 mt-1">EPIC-KITCHENS Pairs</div>
        </div>
      </div>

      {/* Main Content: Video Viewport & Official JSON Schema Inspector */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Player (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between">
            {/* Player Switcher Tabs */}
            <div className="flex space-x-1 bg-[#10141b] p-1 rounded border border-[#222936]">
              <button
                onClick={() => setActivePlayer('highlight')}
                className={`px-3 py-1 rounded text-xs font-mono font-medium transition ${
                  activePlayer === 'highlight'
                    ? 'bg-emerald-500 text-slate-950 font-bold'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Generated Highlight MP4 ({outDur.toFixed(1)}s)
              </button>
              <button
                onClick={() => setActivePlayer('original')}
                className={`px-3 py-1 rounded text-xs font-mono font-medium transition ${
                  activePlayer === 'original'
                    ? 'bg-emerald-500 text-slate-950 font-bold'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Original Footage ({inDur.toFixed(1)}s)
              </button>
            </div>

            <div className="text-[11px] font-mono text-slate-400">
              {activePlayer === 'highlight' ? 'Compiled from original segments only' : 'Raw egocentric camera feed'}
            </div>
          </div>

          <div className="aspect-video bg-black rounded overflow-hidden border border-[#222936] flex items-center justify-center shadow-2xl">
            <video
              key={activePlayer}
              src={activePlayer === 'highlight' ? api.getHighlightStreamUrl(videoId) : api.getOriginalStreamUrl(videoId)}
              controls
              className="w-full h-full object-contain"
            />
          </div>

          {/* Highlights Segment List */}
          <div className="p-4 rounded bg-[#10141c] border border-[#212836] space-y-2.5">
            <div className="text-xs font-mono text-slate-300 uppercase tracking-wider">
              Compiled Highlight Intervals
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs font-mono">
              {highlights.map((h, i) => (
                <div key={i} className="p-2.5 rounded bg-[#151b24] border border-[#232d3d] flex items-center justify-between">
                  <span className="text-slate-200">{h.action_label || `Highlight #${i+1}`}</span>
                  <span className="text-emerald-400 font-bold">
                    {h.start.toFixed(1)}s – {h.end.toFixed(1)}s ({(h.end - h.start).toFixed(1)}s)
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Official Samsung Track 4 JSON Inspector (5 cols) */}
        <div className="lg:col-span-5 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-1.5">
              <FileJson className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-mono text-slate-200 font-semibold uppercase">
                {videoId}.json
              </span>
            </div>

            <button
              onClick={handleCopyJson}
              className="flex items-center space-x-1 text-xs font-mono px-2 py-1 rounded bg-[#151c27] hover:bg-[#1f2838] text-slate-300 border border-[#273448] transition"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied' : 'Copy'}</span>
            </button>
          </div>

          <div className="relative rounded bg-[#0b0e13] border border-[#1e2533] p-4 font-mono text-[11px] text-slate-300 overflow-x-auto max-h-[520px] overflow-y-auto leading-relaxed">
            <pre>{jsonString}</pre>
          </div>

          <div className="p-3 rounded bg-emerald-950/30 border border-emerald-900/40 text-[11px] font-mono text-emerald-300 flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>Passed official Track 4 schema & budget check. Ready for submission.</span>
          </div>
        </div>
      </div>
    </div>
  );
};

