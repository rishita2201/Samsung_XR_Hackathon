import React, { useState, useRef } from 'react';
import {
  Scissors, Play, Trash2, Plus, RefreshCw, CheckCircle2,
  AlertTriangle, Download, ArrowRight, Loader2, Sparkles
} from 'lucide-react';
import { AnalysisResult, HighlightItem, ActionItem } from '../types';
import { api } from '../services/api';

interface HighlightEditorProps {
  videoId: string;
  analysis: AnalysisResult | null;
  onRefreshAnalysis: () => void;
  onNavigateToResults: () => void;
}

export const HighlightEditor: React.FC<HighlightEditorProps> = ({
  videoId,
  analysis,
  onRefreshAnalysis,
  onNavigateToResults
}) => {
  if (!analysis) {
    return (
      <div className="py-20 text-center text-xs text-slate-400">
        No video loaded. Please analyze a video first.
      </div>
    );
  }

  const { samsung_output, metadata } = analysis;
  const totalDuration = samsung_output.duration || 60;
  const maxAllowedSeconds = totalDuration * 0.15;

  const [highlights, setHighlights] = useState<HighlightItem[]>(samsung_output.highlights || []);
  const [isRendering, setIsRendering] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [previewingIndex, setPreviewingIndex] = useState<number | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);

  // Compute selected total duration and percentage
  const totalSelectedSeconds = highlights.reduce((acc, h) => acc + (h.end - h.start), 0);
  const highlightPercentage = totalDuration > 0 ? (totalSelectedSeconds / totalDuration) * 100 : 0;
  const isOverBudget = totalSelectedSeconds > (maxAllowedSeconds + 1e-4);

  const handleRemove = (index: number) => {
    const updated = highlights.filter((_, i) => i !== index);
    setHighlights(updated);
  };

  const handleAddActionAsHighlight = (action: ActionItem) => {
    // Avoid exact duplicate
    const exists = highlights.some(h => Math.abs(h.start - action.start) < 0.2 && Math.abs(h.end - action.end) < 0.2);
    if (exists) return;

    const newH: HighlightItem = {
      start: action.start,
      end: action.end,
      importance: action.confidence || 0.75,
      action_label: `${action.verb} ${action.noun}`
    };

    const updated = [...highlights, newH].sort((a, b) => a.start - b.start);
    setHighlights(updated);
  };

  const handlePreviewSegment = (h: HighlightItem, idx: number) => {
    setPreviewingIndex(idx);
    if (videoRef.current) {
      videoRef.current.currentTime = h.start;
      videoRef.current.play();

      const checkTime = () => {
        if (videoRef.current && videoRef.current.currentTime >= h.end) {
          videoRef.current.currentTime = h.start;
        }
      };
      videoRef.current.ontimeupdate = checkTime;
    }
  };

  const stopPreview = () => {
    setPreviewingIndex(null);
    if (videoRef.current) {
      videoRef.current.ontimeupdate = null;
      videoRef.current.pause();
    }
  };

  const handleSaveAndRender = async () => {
    try {
      setIsRendering(true);
      setStatusMessage('Applying highlight modifications and re-rendering MP4...');
      await api.updateHighlights(videoId, highlights, true);
      setStatusMessage('Render complete! Highlight updated.');
      onRefreshAnalysis();
    } catch (e: any) {
      setStatusMessage(`Error: ${e.message}`);
    } finally {
      setIsRendering(false);
    }
  };

  const handleResetToAuto = () => {
    setHighlights(samsung_output.highlights || []);
  };

  return (
    <div className="py-6 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#222936] gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono text-emerald-400 uppercase tracking-wider">Module G & H · Editor</span>
            <span className="text-slate-600">/</span>
            <span className="text-xs font-mono text-slate-300">{videoId}</span>
          </div>
          <h1 className="text-lg font-bold text-slate-100 mt-0.5">Highlight Sequence Editor</h1>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleResetToAuto}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-[#18202c] hover:bg-[#202b3b] text-slate-300 border border-[#2d3a4e] text-xs font-medium transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Reset Algorithm Highlights</span>
          </button>

          <button
            onClick={handleSaveAndRender}
            disabled={isRendering || isOverBudget}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-slate-950 text-xs font-semibold uppercase tracking-wider transition shadow"
          >
            {isRendering ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Scissors className="w-3.5 h-3.5" />
            )}
            <span>Export & Render MP4</span>
          </button>
        </div>
      </div>

      {/* 15% Budget Telemetry Card */}
      <div className="p-4 rounded bg-[#10141c] border border-[#222936] space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <div className="text-xs font-mono text-slate-400 uppercase">Challenge Budget Contract</div>
            <div className="text-sm font-semibold text-slate-200 mt-0.5">
              Highlight Duration Budget Constraint (Max 15.00%)
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className="text-[11px] font-mono text-slate-400">Selected Time</div>
              <div className="text-sm font-mono font-bold text-slate-100">
                {totalSelectedSeconds.toFixed(2)}s <span className="text-slate-500 font-normal">/ max {maxAllowedSeconds.toFixed(2)}s</span>
              </div>
            </div>

            <div className={`px-3 py-1.5 rounded border text-xs font-mono font-bold flex items-center space-x-1.5 ${
              isOverBudget
                ? 'bg-rose-950/70 border-rose-800 text-rose-300'
                : 'bg-emerald-950/70 border-emerald-800 text-emerald-400'
            }`}>
              {isOverBudget ? (
                <AlertTriangle className="w-4 h-4 text-rose-400" />
              ) : (
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              )}
              <span>{highlightPercentage.toFixed(1)}% / 15.0%</span>
            </div>
          </div>
        </div>

        {/* Visual Budget Bar */}
        <div className="w-full bg-[#161c26] rounded-full h-2.5 overflow-hidden border border-[#252c3a] relative">
          {/* 15% Marker line */}
          <div className="absolute top-0 bottom-0 left-[15%] w-0.5 bg-slate-400 z-10" title="15% Hard Budget Ceiling" />
          <div
            className={`h-2.5 rounded-full transition-all duration-300 ${isOverBudget ? 'bg-rose-500' : 'bg-emerald-500'}`}
            style={{ width: `${Math.min(100, highlightPercentage)}%` }}
          />
        </div>

        {isOverBudget && (
          <div className="text-xs text-rose-400 flex items-center space-x-1.5">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>Warning: Total highlight duration exceeds official 15% limit. Validator will fail. Trim or remove segments.</span>
          </div>
        )}
      </div>

      {/* Interactive Timeline Track */}
      <div className="p-4 rounded bg-[#10141b] border border-[#212836] space-y-2">
        <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
          <span>Highlight Sequence Timeline Layout</span>
          <span>Duration: {totalDuration}s</span>
        </div>

        <div className="relative h-12 bg-[#161c26] rounded border border-[#263140] overflow-hidden">
          {/* 10-second tick marks */}
          {Array.from({ length: Math.ceil(totalDuration / 10) }).map((_, i) => (
            <div
              key={i}
              className="absolute top-0 bottom-0 border-l border-slate-800/80 text-[9px] font-mono text-slate-600 pl-1"
              style={{ left: `${((i * 10) / totalDuration) * 100}%` }}
            >
              {i * 10}s
            </div>
          ))}

          {/* Highlight Blocks */}
          {highlights.map((h, i) => {
            const left = (h.start / totalDuration) * 100;
            const width = Math.max(2, ((h.end - h.start) / totalDuration) * 100);
            const isPreviewing = previewingIndex === i;
            return (
              <div
                key={i}
                style={{ left: `${left}%`, width: `${width}%` }}
                className={`absolute top-1.5 bottom-1.5 rounded px-1.5 flex items-center justify-between text-[10px] font-mono transition shadow ${
                  isPreviewing
                    ? 'bg-emerald-400 text-slate-950 font-bold ring-2 ring-white z-20'
                    : 'bg-emerald-600 text-slate-950 font-semibold hover:bg-emerald-500 z-10'
                }`}
                title={`Segment #${i+1}: ${h.start}s - ${h.end}s (Imp: ${h.importance})`}
              >
                <span className="truncate">{h.action_label || `Highlight #${i+1}`}</span>
                <span className="hidden sm:inline text-[9px] opacity-80">{(h.end - h.start).toFixed(1)}s</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Main Grid: Segments List (Left) and Video Loop Preview / Quick Add (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left 7 cols: Highlight Segments List */}
        <div className="lg:col-span-7 space-y-3">
          <div className="flex items-center justify-between pb-1">
            <h2 className="text-xs font-mono text-slate-300 uppercase tracking-wider">
              Selected Highlight Segments ({highlights.length})
            </h2>
            <span className="text-[11px] font-mono text-slate-500">Chronologically Sorted</span>
          </div>

          <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
            {highlights.map((h, idx) => {
              const segDur = (h.end - h.start).toFixed(2);
              const isPreview = previewingIndex === idx;

              return (
                <div
                  key={idx}
                  className={`p-3.5 rounded border text-left transition flex items-center justify-between ${
                    isPreview
                      ? 'bg-[#162332] border-emerald-500'
                      : 'bg-[#10141b] border-[#212836] hover:border-[#2f394c]'
                  }`}
                >
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="w-5 h-5 rounded bg-[#18202c] border border-[#2d3a4e] flex items-center justify-center text-[10px] font-mono font-bold text-emerald-400">
                        {idx + 1}
                      </span>
                      <span className="text-xs font-semibold text-slate-200 uppercase">
                        {h.action_label || 'Active Interaction'}
                      </span>
                    </div>

                    <div className="flex items-center space-x-4 text-[11px] font-mono text-slate-400">
                      <span>Time: <strong className="text-slate-200">{h.start.toFixed(1)}s – {h.end.toFixed(1)}s</strong></span>
                      <span>Span: <strong className="text-slate-200">{segDur}s</strong></span>
                      <span>Importance: <strong className="text-emerald-400">{h.importance.toFixed(3)}</strong></span>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    {isPreview ? (
                      <button
                        onClick={stopPreview}
                        className="px-2.5 py-1 rounded bg-amber-500 text-slate-950 font-semibold text-[11px] transition"
                      >
                        Stop Loop
                      </button>
                    ) : (
                      <button
                        onClick={() => handlePreviewSegment(h, idx)}
                        className="p-1.5 rounded hover:bg-[#1a2230] text-slate-300 hover:text-emerald-400 transition"
                        title="Preview loop"
                      >
                        <Play className="w-4 h-4 fill-current" />
                      </button>
                    )}

                    <button
                      onClick={() => handleRemove(idx)}
                      className="p-1.5 rounded hover:bg-rose-950/60 text-slate-400 hover:text-rose-400 transition"
                      title="Remove segment"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right 5 cols: Video Preview Player & Add Detected Actions */}
        <div className="lg:col-span-5 space-y-4">
          {/* Segment Loop Video Player */}
          <div className="p-3 rounded bg-[#10141b] border border-[#212836] space-y-2">
            <div className="text-[11px] font-mono text-slate-400 flex items-center justify-between">
              <span>Original Footage Segment Preview</span>
              {previewingIndex !== null && (
                <span className="text-emerald-400 font-bold animate-pulse">Looping Segment #{previewingIndex + 1}</span>
              )}
            </div>

            <div className="aspect-video bg-black rounded overflow-hidden border border-[#222936] flex items-center justify-center">
              <video
                ref={videoRef}
                src={api.getOriginalStreamUrl(videoId)}
                controls
                className="w-full h-full object-contain"
              />
            </div>
          </div>

          {/* Quick-Add from Detected Actions */}
          <div className="p-3.5 rounded bg-[#10141c] border border-[#222936] space-y-2.5">
            <div className="text-xs font-mono text-slate-300 uppercase tracking-wider">
              Add Detected Action to Highlight
            </div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Incorporate valid ground-truth actions localized by the pipeline into the highlight reel:
            </p>

            <div className="space-y-1.5 max-h-[180px] overflow-y-auto pr-1">
              {(samsung_output.actions || []).map((act, i) => (
                <div
                  key={i}
                  className="flex items-center justify-between p-2 rounded bg-[#141922] border border-[#202735] text-xs font-mono"
                >
                  <span className="text-slate-200">
                    {act.verb} {act.noun} ({act.start}s-{act.end}s)
                  </span>

                  <button
                    onClick={() => handleAddActionAsHighlight(act)}
                    className="p-1 rounded bg-[#1b2332] hover:bg-emerald-600 hover:text-slate-950 text-emerald-400 transition"
                    title="Add segment"
                  >
                    <Plus className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
