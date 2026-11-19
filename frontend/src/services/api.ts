import {
  AnalysisResult,
  PipelineProgress,
  SamsungOutputSchema,
  SystemStatus,
  VideoListItem
} from '../types';

const API_BASE = '/api';

export const api = {
  async getSystemStatus(): Promise<SystemStatus> {
    const res = await fetch(`${API_BASE}/system/status`);
    if (!res.ok) throw new Error('Failed to fetch system status');
    return res.json();
  },

  async listVideos(): Promise<VideoListItem[]> {
    const res = await fetch(`${API_BASE}/videos`);
    if (!res.ok) throw new Error('Failed to fetch video list');
    return res.json();
  },

  async uploadVideo(file?: File, generateSynthetic = false): Promise<{ video_id: string; message: string; filename: string }> {
    const formData = new FormData();
    if (file) {
      formData.append('file', file);
    }
    if (generateSynthetic) {
      formData.append('generate_synthetic', 'true');
    }

    const res = await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Upload failed' }));
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },

  async startAnalysis(videoId: string): Promise<{ message: string; video_id: string }> {
    const res = await fetch(`${API_BASE}/analyze/${videoId}`, {
      method: 'POST',
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Analysis failed to start' }));
      throw new Error(err.detail || 'Analysis failed to start');
    }
    return res.json();
  },

  async getProgress(videoId: string): Promise<PipelineProgress> {
    const res = await fetch(`${API_BASE}/progress/${videoId}`);
    if (!res.ok) throw new Error('Failed to fetch progress');
    return res.json();
  },

  async getVideoDetails(videoId: string): Promise<AnalysisResult> {
    const res = await fetch(`${API_BASE}/videos/${videoId}`);
    if (!res.ok) throw new Error('Failed to fetch video analysis details');
    return res.json();
  },

  async updateHighlights(
    videoId: string,
    highlights: Array<{ start: number; end: number; importance: number; action_label?: string }>,
    renderVideo = true
  ): Promise<{ message: string; data: SamsungOutputSchema }> {
    const res = await fetch(`${API_BASE}/highlight/update/${videoId}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ highlights, render_video: renderVideo }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Update failed' }));
      throw new Error(err.detail || 'Update failed');
    }
    return res.json();
  },

  async runValidation(): Promise<{
    overall_valid: boolean;
    total_files: number;
    passed_count: number;
    failed_count: number;
    details: Array<{ video_id: string; filename: string; valid: boolean; errors: string[] }>;
  }> {
    const res = await fetch(`${API_BASE}/validate`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Validation execution failed');
    return res.json();
  },

  getOriginalStreamUrl(videoId: string): string {
    return `${API_BASE}/stream/original/${videoId}`;
  },

  getHighlightStreamUrl(videoId: string): string {
    return `${API_BASE}/stream/highlight/${videoId}`;
  },

  getJsonDownloadUrl(videoId: string): string {
    return `${API_BASE}/download/json/${videoId}`;
  },

  getHighlightDownloadUrl(videoId: string): string {
    return `${API_BASE}/download/highlight/${videoId}`;
  }
};

