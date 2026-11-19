import React, { useState, useRef, useEffect } from 'react';
import {
  UploadCloud, FileVideo, Play, CheckCircle2, AlertCircle,
  Clock, HardDrive, RefreshCw, ArrowRight, Loader2, Video
} from 'lucide-react';
import { api } from '../services/api';
import { VideoListItem, PipelineProgress } from '../types';

interface UploadWorkspaceProps {
  onVideoSelected: (videoId: string) => void;
  activeVideoId?: string;
  isProcessing: boolean;
  setIsProcessing: (v: boolean) => void;
  progress: PipelineProgress | null;
  setProgress: (p: PipelineProgress | null) => void;
}

export const UploadWorkspace: React.FC<UploadWorkspaceProps> = ({
  onVideoSelected,
  activeVideoId,
  isProcessing,
  setIsProcessing,
  progress,
  setProgress
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [recentVideos, setRecentVideos] = useState<VideoListItem[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchRecent = async () => {
    try {
      const list = await api.listVideos();
      setRecentVideos(list);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchRecent();
  }, []);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.name.toLowerCase().endsWith('.mp4')) {
        setSelectedFile(file);
        setErrorMessage(null);
      } else {
        setErrorMessage('Please select an MP4 first-person video file.');
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.name.toLowerCase().endsWith('.mp4')) {
        setSelectedFile(file);
        setErrorMessage(null);
      } else {
        setErrorMessage('Please select an MP4 first-person video file.');
      }
    }
  };

  const triggerUploadAndAnalyze = async () => {
    if (!selectedFile) return;
    try {
      setUploadLoading(true);
      setErrorMessage(null);
      setStatusMessage('Uploading video to workspace...');

      const uploadRes = await api.uploadVideo(selectedFile);
      const vidId = uploadRes.video_id;

      setStatusMessage('Starting MOMENTIQ pipeline analysis...');
      await api.startAnalysis(vidId);
      setIsProcessing(true);
      onVideoSelected(vidId);
      pollProgress(vidId);
    } catch (err: any) {
      setErrorMessage(err.message || 'Upload failed');
    } finally {
      setUploadLoading(false);
    }
  };

  const handleGenerateSynthetic = async () => {
    try {
      setUploadLoading(true);
      setErrorMessage(null);
      setStatusMessage('Generating synthetic egocentric test video...');

      const res = await api.uploadVideo(undefined, true);
      const vidId = res.video_id;

      setStatusMessage('Starting MOMENTIQ pipeline analysis...');
      await api.startAnalysis(vidId);
      setIsProcessing(true);
      onVideoSelected(vidId);
      pollProgress(vidId);
    } catch (err: any) {
      setErrorMessage(err.message || 'Generation failed');
    } finally {
      setUploadLoading(false);
    }
  };

  const pollProgress = (vidId: string) => {
    const timer = setInterval(async () => {
      try {
        const p = await api.getProgress(vidId);
        setProgress(p);
        if (p.status === 'completed') {
          clearInterval(timer);
          setIsProcessing(false);
          setStatusMessage('Analysis successfully completed!');
          fetchRecent();
        } else if (p.status === 'failed') {
          clearInterval(timer);
          setIsProcessing(false);
          setErrorMessage(p.error || 'Pipeline execution failed.');
        }
      } catch (e) {
        clearInterval(timer);
        setIsProcessing(false);
      }
    }, 1500);
  };

  return (
    <div className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8">
      {/* Top Banner */}
      <div>
        <div className="text-xs font-mono text-emerald-400 uppercase tracking-wider">Module A & B</div>
        <h1 className="text-xl font-bold text-slate-100 mt-1">Video Ingestion & Processing Workspace</h1>
        <p className="text-xs text-slate-400 mt-1">
          Upload egocentric first-person video (EPIC-KITCHENS-100 or FPVSum format) or initialize synthetic egocentric scenario.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Cols: Upload Area & Progress */}
        <div className="lg:col-span-2 space-y-6">
          {/* Dropzone */}
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`relative rounded border-2 border-dashed p-8 text-center transition ${
              dragActive
                ? 'border-emerald-500 bg-emerald-950/20'
                : 'border-[#222936] bg-[#0e1218] hover:border-[#313c4e]'
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".mp4,.mov,.avi"
              onChange={handleFileChange}
              className="hidden"
            />

            <div className="mx-auto w-12 h-12 rounded bg-[#161c26] border border-[#263140] flex items-center justify-center text-emerald-400 mb-4">
              <UploadCloud className="w-6 h-6" />
            </div>

            <h3 className="text-sm font-semibold text-slate-200">
              Drag and drop your egocentric MP4 video
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Supports standard 2–10 min first-person videos (EPIC-KITCHENS / FPVSum)
            </p>

            <div className="mt-5 flex items-center justify-center gap-3">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="px-4 py-2 rounded bg-[#18202c] hover:bg-[#202a3a] text-slate-200 border border-[#2d3a4e] text-xs font-semibold uppercase tracking-wider transition"
              >
                Browse MP4 File
              </button>

              <span className="text-xs text-slate-500">or</span>

              <button
                type="button"
                onClick={handleGenerateSynthetic}
                disabled={uploadLoading || isProcessing}
                className="px-4 py-2 rounded bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-semibold uppercase tracking-wider transition flex items-center space-x-1.5 shadow"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>Generate Egocentric Synthetic (40s)</span>
              </button>
            </div>

            {selectedFile && (
              <div className="mt-6 p-3 rounded bg-[#141922] border border-[#242d3d] text-left flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <FileVideo className="w-5 h-5 text-emerald-400" />
                  <div>
                    <div className="text-xs font-semibold text-slate-200">{selectedFile.name}</div>
                    <div className="text-[11px] font-mono text-slate-400">
                      {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB · video/mp4
                    </div>
                  </div>
                </div>

                <button
                  onClick={triggerUploadAndAnalyze}
                  disabled={uploadLoading || isProcessing}
                  className="px-4 py-1.5 rounded bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-xs uppercase tracking-wide transition flex items-center space-x-1"
                >
                  {uploadLoading ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <>
                      <span>Start Pipeline</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </>
                  )}
                </button>
              </div>
            )}
          </div>

          {/* Status and Error Banners */}
          {errorMessage && (
            <div className="p-3.5 rounded bg-rose-950/40 border border-rose-800/60 text-xs text-rose-300 flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <div>{errorMessage}</div>
            </div>
          )}

          {/* Live Progress Card */}
          {isProcessing && progress && (
            <div className="p-5 rounded bg-[#11151c] border border-[#212836] space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2.5">
                  <div className="w-3 h-3 rounded-full bg-emerald-400 animate-ping" />
                  <span className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
                    Pipeline Execution in Progress: <code className="text-emerald-400">{progress.video_id}</code>
                  </span>
                </div>
                <span className="text-xs font-mono font-bold text-emerald-400">
                  {progress.progress_pct}%
                </span>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-[#171c26] rounded-full h-2 overflow-hidden border border-[#252c3a]">
                <div
                  className="bg-emerald-500 h-2 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${progress.progress_pct}%` }}
                />
              </div>

              <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
                <div className="flex items-center space-x-1.5">
                  <Loader2 className="w-3 h-3 animate-spin text-emerald-400" />
                  <span>{progress.current_step}</span>
                </div>
                <span>FPS: 2.0 Target</span>
              </div>
            </div>
          )}
        </div>

        {/* Right Col: Video Catalog & Recently Analyzed */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-mono text-slate-300 uppercase tracking-wider">
              Workspace Videos ({recentVideos.length})
            </h2>
            <button
              onClick={fetchRecent}
              className="text-slate-400 hover:text-slate-200 p-1"
              title="Refresh list"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-2.5 max-h-[480px] overflow-y-auto pr-1">
            {recentVideos.length === 0 ? (
              <div className="p-6 text-center text-xs text-slate-500 rounded bg-[#10131a] border border-[#1e2430]">
                No videos in workspace yet.
              </div>
            ) : (
              recentVideos.map((v) => {
                const isCurrent = activeVideoId === v.video_id;
                return (
                  <div
                    key={v.video_id}
                    className={`p-3 rounded border text-left transition ${
                      isCurrent
                        ? 'bg-[#151c27] border-emerald-500/50'
                        : 'bg-[#10131a] border-[#1e2430] hover:border-[#2b3445]'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="text-xs font-semibold text-slate-200 truncate max-w-[170px]">
                        {v.video_id}
                      </div>
                      <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                        v.has_analysis
                          ? 'bg-emerald-950/80 border border-emerald-800/60 text-emerald-400'
                          : 'bg-amber-950/80 border border-amber-800/60 text-amber-400'
                      }`}>
                        {v.has_analysis ? 'Analyzed' : 'Pending'}
                      </span>
                    </div>

                    <div className="mt-2 text-[11px] font-mono text-slate-400 flex items-center justify-between">
                      <span>{v.file_size_mb} MB</span>
                      {v.duration && <span>{v.duration}s</span>}
                      {v.highlight_ratio !== undefined && (
                        <span className="text-emerald-400">
                          {(v.highlight_ratio * 100).toFixed(1)}% budget
                        </span>
                      )}
                    </div>

                    <div className="mt-3 flex items-center gap-2">
                      <button
                        onClick={() => onVideoSelected(v.video_id)}
                        className="flex-1 py-1 px-2 rounded bg-[#18202c] hover:bg-[#202b3b] border border-[#2d3a4e] text-[11px] font-medium text-slate-200 transition text-center"
                      >
                        Inspect in Studio
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

