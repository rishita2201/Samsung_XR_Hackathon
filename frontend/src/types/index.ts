export interface ActionItem {
  verb: string;
  noun: string;
  start: number;
  end: number;
  confidence?: number;
}

export interface HighlightItem {
  start: number;
  end: number;
  importance: number;
  action_label?: string;
}

export interface SamsungOutputSchema {
  video_id: string;
  label: string;
  actions: ActionItem[];
  highlights: HighlightItem[];
  duration: number;
  highlight_ratio: number;
}

export interface VideoMetadata {
  video_id: string;
  filename: string;
  filepath: string;
  duration: number;
  fps: number;
  frame_count: number;
  width: number;
  height: number;
  bitrate?: number;
  created_at: string;
}

export interface ThumbnailItem {
  frame_idx?: number;
  timestamp?: number;
  filename: string;
  relative_url: string;
}

export interface TimelineDataPoint {
  time: number;
  activity: number;
  camera_motion: number;
  interaction: number;
}

export interface AnalysisResult {
  samsung_output: SamsungOutputSchema;
  metadata: VideoMetadata;
  thumbnails?: ThumbnailItem[];
  rendered_video_path?: string;
  timeline_series?: TimelineDataPoint[];
  elapsed_seconds?: number;
}

export interface PipelineProgress {
  video_id: string;
  status: 'queued' | 'sampling' | 'analyzing' | 'localizing' | 'scoring' | 'rendering' | 'completed' | 'failed' | 'not_found';
  progress_pct: number;
  current_step: string;
  error?: string;
}

export interface VideoListItem {
  video_id: string;
  filename: string;
  filepath: string;
  has_analysis: boolean;
  status: string;
  progress_pct: number;
  file_size_mb: number;
  label?: string;
  duration?: number;
  highlight_ratio?: number;
  actions_count?: number;
  highlights_count?: number;
}

export interface SystemStatus {
  status: string;
  semantic_clip_ready: boolean;
  clip_checkpoint_size_mb: number;
  classes_vocabulary_ready: boolean;
  ffmpeg_available: boolean;
  model_architecture: string;
  supported_datasets: string[];
}
