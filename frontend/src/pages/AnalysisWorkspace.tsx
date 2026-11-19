import React, { useState, useRef, useEffect } from 'react';
import {
  Play, Pause, RotateCcw, Volume2, VolumeX, FastForward,
  Clock, Tag, Eye, ChevronRight, Activity, Crosshair, Sparkles
} from 'lucide-react';
import { AnalysisResult, ActionItem } from '../types';
import { api } from '../services/api';

interface AnalysisWorkspaceProps {
  videoId: string;
  analysis: AnalysisResult | null;
  onNavigateToEditor: () => void;
}

export const AnalysisWorkspace: React.FC<AnalysisWorkspaceProps> = ({
  videoId,
  analysis,
  onNavigateToEditor
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const [selectedActionIndex, setSelectedActionIndex] = useState<number | null>(null);

  useEffect(() => {
    if (analysis?.samsung_output?.duration) {
      setDuration(analysis.samsung_output.duration);
    }
  }, [analysis]);

  const togglePlay = () => {
    if (!videoRef.current) return;
    if (isPlaying) {
      videoRef.current.pause();
      setIsPlaying(false);
    } else {
      videoRef.current.play();
      setIsPlaying(true);
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
    }
  };

  const handleSeek = (timeSec: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = timeSec;
      setCurrentTime(timeSec);
    }
  };

  const jumpToAction = (action: ActionItem, idx: number) => {
    setSelectedActionIndex(idx);
    handleSeek(action.start);
    if (videoRef.current && !isPlaying) {
      videoRef.current.play();
      setIsPlaying(true);
    }
  };

  const formatTime = (sec: number) => {
    const mins = Math.floor(sec / 60);
    const secs = Math.floor(sec % 60);
    const ms = Math.floor((sec % 1) * 100);
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}.${ms.toString().padStart(2, '0')}`;
  };

  if (!analysis) {
    return (
      <div className="py-20 text-center space-y-3">
        <div className="w-10 h-10 mx-auto rounded-full bg-[#18202c] border border-[#2e3b4f] flex items-center justify-center text-emerald-400">
          <Activity className="w-5 h-5 animate-pulse" />
        </div>
        <h3 className="text-sm font-semibold text-slate-200">No Video Analysis Loaded</h3>
        <p className="text-xs text-slate-400">Please select or upload a video from the Ingestion Workspace.</p>
      </div>
    );
  }

  const { samsung_output, metadata, thumbnails } = analysis;
  const actions = samsung_output.actions || [];
  const currentAction = actions.find(a => currentTime >= a.start && currentTime <= a.end);

  return (
    <div className="py-6 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-6">
      {/* Studio Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-[#222936] gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono text-emerald-400 uppercase tracking-wider">Module C & D · Studio</span>
            <span className="text-slate-600">/</span>
            <span className="text-xs font-mono text-slate-300">{videoId}</span>
          </div>
          <h1 className="text-lg font-bold text-slate-100 mt-0.5">Egocentric Analysis Studio</h1>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2 px-3 py-1 rounded bg-[#131720] border border-[#212938] text-xs">
            <span className="text-slate-400">Category Tag:</span>
            <span className="font-mono font-semibold text-emerald-400 uppercase">{samsung_output.label || 'unknown'}</span>
          </div>

          <button
            onClick={onNavigateToEditor}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-semibold uppercase tracking-wider transition shadow"
          >
            <span>Open Highlight Editor</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Main Studio Grid: Video Player + Telemetry (Left) and Action Detections (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Player & Timeline Scrubber (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          {/* Main Video Viewport */}
          <div className="relative rounded overflow-hidden bg-black border border-[#222936] aspect-video flex items-center justify-center group shadow-2xl">
            <video
              ref={videoRef}
              src={api.getOriginalStreamUrl(videoId)}
              onTimeUpdate={handleTimeUpdate}
              onEnded={() => setIsPlaying(false)}
              className="w-full h-full object-contain"
            />

            {/* Live Action Overlay Tag */}
            {currentAction && (
              <div className="absolute top-3 left-3 bg-[#0c1017]/90 backdrop-blur border border-emerald-500/60 px-2.5 py-1 rounded text-xs font-mono flex items-center space-x-2 shadow-lg">
                <Crosshair className="w-3.5 h-3.5 text-emerald-400 animate-spin" />
                <span className="text-slate-300">ACTIVE:</span>
                <span className="text-emerald-300 font-bold uppercase">{currentAction.verb} {currentAction.noun}</span>
                {currentAction.confidence && (
                  <span className="text-[10px] text-slate-400">({(currentAction.confidence * 100).toFixed(0)}%)</span>
                )}
              </div>
            )}

            {/* Big Play overlay when paused */}
            {!isPlaying && (
              <button
                onClick={togglePlay}
                className="absolute inset-0 m-auto w-14 h-14 rounded-full bg-black/60 border border-slate-700/80 flex items-center justify-center text-slate-100 hover:scale-105 hover:bg-emerald-500 hover:text-slate-950 transition"
              >
                <Play className="w-6 h-6 ml-0.5 fill-current" />
              </button>
            )}
          </div>

          {/* Player Controls Bar */}
          <div className="p-3 rounded bg-[#10141b] border border-[#212836] flex items-center justify-between gap-4">
            <div className="flex items-center space-x-2">
              <button
                onClick={togglePlay}
                className="p-1.5 rounded hover:bg-[#1a212d] text-slate-200 transition"
              >
                {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 fill-current" />}
              </button>
              <button
                onClick={() => handleSeek(0)}
                className="p-1.5 rounded hover:bg-[#1a212d] text-slate-400 hover:text-slate-200 transition"
                title="Reset to 00:00"
              >
                <RotateCcw className="w-4 h-4" />
              </button>
              <button
                onClick={() => {
                  if (videoRef.current) {
                    videoRef.current.muted = !isMuted;
                    setIsMuted(!isMuted);
                  }
                }}
                className="p-1.5 rounded hover:bg-[#1a212d] text-slate-400 hover:text-slate-200 transition"
              >
                {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
              </button>
            </div>

            {/* Timecode Readout */}
            <div className="text-xs font-mono font-medium text-slate-300 bg-[#161c26] px-2.5 py-1 rounded border border-[#283244]">
              <span className="text-emerald-400">{formatTime(currentTime)}</span>
              <span className="text-slate-500 mx-1">/</span>
              <span>{formatTime(duration || 0)}</span>
            </div>
          </div>

          {/* Extracted Frame Scrubber Strip */}
          {thumbnails && thumbnails.length > 0 && (
            <div className="space-y-1.5">
              <div className="text-[11px] font-mono text-slate-400 flex items-center justify-between">
                <span>Extracted Keyframe Scrubber</span>
                <span>Click thumbnail to jump</span>
              </div>

              <div className="flex space-x-1.5 overflow-x-auto pb-2 pt-1">
                {thumbnails.map((th, i) => {
                  const thumbTime = th.timestamp ?? ((duration * i) / (thumbnails.length - 1));
                  const isNear = Math.abs(currentTime - thumbTime) < (duration / thumbnails.length);
                  return (
                    <button
                      key={i}
                      onClick={() => handleSeek(thumbTime)}
                      className={`relative shrink-0 rounded overflow-hidden border transition ${
                        isNear ? 'border-emerald-400 ring-1 ring-emerald-400' : 'border-[#222936] opacity-70 hover:opacity-100'
                      }`}
                      style={{ width: '80px', height: '48px' }}
                    >
                      <img
                        src={th.relative_url}
                        alt={`thumb ${i}`}
                        className="w-full h-full object-cover"
                      />
                      <span className="absolute bottom-0 right-0 bg-black/80 text-[9px] font-mono text-slate-300 px-1">
                        {Math.floor(thumbTime)}s
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Interactive Multi-Track Timeline */}
          <div className="p-3.5 rounded bg-[#10141b] border border-[#212836] space-y-2">
            <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
              <span className="flex items-center space-x-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                <span>Action Interval Mapping (EPIC-KITCHENS)</span>
              </span>
              <span>{actions.length} Localized Actions</span>
            </div>

            {/* Visual timeline track */}
            <div
              onClick={(e) => {
                const rect = e.currentTarget.getBoundingClientRect();
                const pos = (e.clientX - rect.left) / rect.width;
                handleSeek(pos * (duration || 1));
              }}
              className="relative h-9 bg-[#161c26] rounded border border-[#263140] cursor-pointer overflow-hidden"
            >
              {/* Playhead Indicator */}
              <div
                className="absolute top-0 bottom-0 w-0.5 bg-white z-20 shadow-md"
                style={{ left: `${Math.min(100, Math.max(0, (currentTime / (duration || 1)) * 100))}%` }}
              >
                <div className="w-2.5 h-2.5 -ml-1 bg-white rounded-full shadow" />
              </div>

              {/* Action Blocks */}
              {actions.map((act, i) => {
                const left = (act.start / (duration || 1)) * 100;
                const width = Math.max(1.5, ((act.end - act.start) / (duration || 1)) * 100);
                const isSelected = selectedActionIndex === i;
                return (
                  <div
                    key={i}
                    style={{ left: `${left}%`, width: `${width}%` }}
                    className={`absolute top-1 bottom-1 rounded px-1 flex items-center justify-center text-[10px] font-mono truncate transition z-10 ${
                      isSelected
                        ? 'bg-emerald-500 text-slate-950 font-bold border border-white'
                        : 'bg-emerald-950/80 border border-emerald-700/60 text-emerald-300 hover:bg-emerald-900'
                    }`}
                    title={`${act.verb} ${act.noun} (${act.start}s - ${act.end}s)`}
                  >
                    {act.verb}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Column: Detected Action Instances Table (5 cols) */}
        <div className="lg:col-span-5 space-y-3">
          <div className="flex items-center justify-between pb-1">
            <h2 className="text-xs font-mono text-slate-300 uppercase tracking-wider">
              Detected Actions ({actions.length})
            </h2>
            <span className="text-[11px] font-mono text-slate-500">tIoU Merged</span>
          </div>

          <div className="space-y-2 max-h-[560px] overflow-y-auto pr-1">
            {actions.map((action, idx) => {
              const isCurrent = currentTime >= action.start && currentTime <= action.end;
              const isSelected = selectedActionIndex === idx;
              const dur = (action.end - action.start).toFixed(1);

              return (
                <div
                  key={idx}
                  onClick={() => jumpToAction(action, idx)}
                  className={`p-3 rounded border text-left cursor-pointer transition ${
                    isCurrent
                      ? 'bg-[#15212f] border-emerald-500'
                      : isSelected
                      ? 'bg-[#18202c] border-[#36465e]'
                      : 'bg-[#10141b] border-[#212836] hover:border-[#2f394c]'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-mono font-bold text-emerald-400 uppercase">
                        {action.verb}
                      </span>
                      <span className="text-xs font-semibold text-slate-200 capitalize">
                        {action.noun}
                      </span>
                    </div>

                    <div className="text-[11px] font-mono text-slate-400">
                      {action.start.toFixed(1)}s – {action.end.toFixed(1)}s ({dur}s)
                    </div>
                  </div>

                  <div className="mt-2 flex items-center justify-between text-[11px] font-mono text-slate-400 pt-1.5 border-t border-[#1b222e]">
                    <span className="flex items-center space-x-1">
                      <span>Conf:</span>
                      <span className="text-slate-200">
                        {action.confidence ? `${(action.confidence * 100).toFixed(0)}%` : 'N/A'}
                      </span>
                    </span>

                    <span className="text-emerald-400/90 text-[10px] uppercase font-semibold">
                      Click to Seek
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

