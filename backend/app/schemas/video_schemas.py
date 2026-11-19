"""Pydantic schemas for MOMENTIQ API and official Samsung Track 4 challenge format."""
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field


class LabelItem(BaseModel):
    name: str = Field(..., description="Video classification label (e.g. cooking, ski, bike)")
    score: float = Field(0.95, description="Classification confidence score in [0, 1]")


class ActionItem(BaseModel):
    segment: List[float] = Field(..., description="[start, end] timestamp interval in seconds")
    verb: str = Field(..., description="Action verb recognized (e.g. cut, pour, take)")
    noun: str = Field(..., description="Target object/noun recognized (e.g. knife, cup, pan)")
    score: float = Field(0.5, description="Recognition confidence in [0, 1]")
    # UI helper aliases
    start: Optional[float] = None
    end: Optional[float] = None
    confidence: Optional[float] = None

    def model_post_init(self, __context: Any) -> None:
        if self.start is None and len(self.segment) == 2:
            self.start = self.segment[0]
        if self.end is None and len(self.segment) == 2:
            self.end = self.segment[1]
        if self.confidence is None:
            self.confidence = self.score


class HighlightItem(BaseModel):
    segment: List[float] = Field(..., description="[start, end] timestamp interval in seconds")
    # UI helper aliases
    start: Optional[float] = None
    end: Optional[float] = None
    importance: Optional[float] = 0.8
    action_label: Optional[str] = None

    def model_post_init(self, __context: Any) -> None:
        if self.start is None and len(self.segment) == 2:
            self.start = self.segment[0]
        if self.end is None and len(self.segment) == 2:
            self.end = self.segment[1]


class SamsungOutputSchema(BaseModel):
    """Official required JSON schema for Samsung XR Hackathon Track 4."""
    team_id: str = "VITChennai_RRR"
    video_id: str
    duration_sec: float
    label: Union[LabelItem, Dict[str, Any], str]
    actions: List[ActionItem]
    highlights: List[HighlightItem]
    duration: Optional[float] = None
    highlight_ratio: Optional[float] = None


class FrameFeaturePoint(BaseModel):
    timestamp: float
    hand_residual_motion: float
    global_camera_motion: float
    interaction_score: float
    importance_score: float


class VideoMetadata(BaseModel):
    video_id: str
    filename: str
    filepath: str
    duration: float
    fps: float
    frame_count: int
    width: int
    height: int
    bitrate: Optional[int] = None
    created_at: str


class PipelineProgress(BaseModel):
    video_id: str
    status: str  # queued, sampling, analyzing_actions, localizing, scoring, rendering, completed, failed
    progress_pct: int
    current_step: str
    error: Optional[str] = None


class AnalysisResult(BaseModel):
    video_id: str
    label: str
    duration: float
    highlight_duration: float
    highlight_ratio: float
    actions_count: int
    highlights_count: int
    actions: List[ActionItem]
    highlights: List[HighlightItem]
    timeline_series: List[Dict[str, Any]]
    highlight_video_url: Optional[str] = None
    original_video_url: Optional[str] = None
    json_url: Optional[str] = None
    metrics_summary: Dict[str, Any]
