"""Service layer managing video storage, background pipeline execution, and state caching."""
import os
import sys
import json
import glob
import threading
from typing import Dict, Any, Optional, List

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ..schemas.video_schemas import PipelineProgress
from ..pipeline.pipeline_orchestrator import MomentiqPipeline
from ..pipeline.video_ingest import extract_metadata, extract_keyframe_thumbnails
from ..pipeline.video_renderer import render_highlight_video
from evaluation.metrics import (
    compute_action_map, compute_action_coverage,
    compute_highlight_f1, compute_label_accuracy,
    calculate_100_point_score
)

# Global in-memory task progress and result cache
_PROGRESS_REGISTRY: Dict[str, PipelineProgress] = {}
_RESULTS_CACHE: Dict[str, Dict[str, Any]] = {}
_LOCK = threading.Lock()


class VideoService:
    def __init__(
        self,
        upload_dir: Optional[str] = None,
        output_dir: Optional[str] = None,
        weights_dir: Optional[str] = None
    ):
        self.upload_dir = os.path.abspath(upload_dir or os.path.join(PROJECT_ROOT, "uploads"))
        self.output_dir = os.path.abspath(output_dir or os.path.join(PROJECT_ROOT, "outputs"))
        self.weights_dir = os.path.abspath(weights_dir or os.path.join(PROJECT_ROOT, "backend", "weights"))
        self.json_dir = os.path.join(self.output_dir, "json")
        self.highlight_dir = os.path.join(self.output_dir, "highlights")
        self.thumbs_dir = os.path.join(self.output_dir, "thumbnails")

        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.json_dir, exist_ok=True)
        os.makedirs(self.highlight_dir, exist_ok=True)
        os.makedirs(self.thumbs_dir, exist_ok=True)

        self.pipeline = MomentiqPipeline(weights_dir=self.weights_dir)

    def get_progress(self, video_id: str) -> PipelineProgress:
        with _LOCK:
            if video_id in _PROGRESS_REGISTRY:
                return _PROGRESS_REGISTRY[video_id]
            # Check if json already exists on disk
            json_path = os.path.join(self.json_dir, f"{video_id}.json")
            if os.path.exists(json_path):
                return PipelineProgress(
                    video_id=video_id,
                    status="completed",
                    progress_pct=100,
                    current_step="Analysis ready"
                )
            return PipelineProgress(
                video_id=video_id,
                status="not_found",
                progress_pct=0,
                current_step="Video not processed yet"
            )

    def start_analysis_async(self, video_id: str, video_path: str):
        """Launches pipeline analysis in background worker thread."""
        with _LOCK:
            _PROGRESS_REGISTRY[video_id] = PipelineProgress(
                video_id=video_id,
                status="queued",
                progress_pct=5,
                current_step="Queued for analysis"
            )

        def worker():
            try:
                def on_progress(step_msg: str, pct: int):
                    with _LOCK:
                        _PROGRESS_REGISTRY[video_id] = PipelineProgress(
                            video_id=video_id,
                            status="analyzing",
                            progress_pct=pct,
                            current_step=step_msg
                        )

                out_json = os.path.join(self.json_dir, f"{video_id}.json")
                out_highlight = os.path.join(self.highlight_dir, f"{video_id}_highlight.mp4")

                res = self.pipeline.run(
                    video_path=video_path,
                    output_json_path=out_json,
                    output_highlight_video_path=out_highlight,
                    progress_callback=on_progress
                )

                # Extract scrubber thumbnails for frontend
                v_thumbs_dir = os.path.join(self.thumbs_dir, video_id)
                thumbs = extract_keyframe_thumbnails(video_path, v_thumbs_dir, num_thumbs=16)
                res["thumbnails"] = thumbs

                with _LOCK:
                    _RESULTS_CACHE[video_id] = res
                    _PROGRESS_REGISTRY[video_id] = PipelineProgress(
                        video_id=video_id,
                        status="completed",
                        progress_pct=100,
                        current_step="Analysis complete"
                    )
            except Exception as e:
                import traceback
                traceback.print_exc()
                with _LOCK:
                    _PROGRESS_REGISTRY[video_id] = PipelineProgress(
                        video_id=video_id,
                        status="failed",
                        progress_pct=0,
                        current_step="Failed",
                        error=str(e)
                    )

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def get_analysis_result(self, video_id: str) -> Optional[Dict[str, Any]]:
        with _LOCK:
            if video_id in _RESULTS_CACHE:
                return _RESULTS_CACHE[video_id]

        # Load from disk if available
        json_path = os.path.join(self.json_dir, f"{video_id}.json")
        if not os.path.exists(json_path):
            return None

        with open(json_path, "r", encoding="utf-8") as f:
            official_data = json.load(f)

        video_path = os.path.join(self.upload_dir, f"{video_id}.mp4")
        if not os.path.exists(video_path):
            # Look for any matching video
            cand = glob.glob(os.path.join(self.upload_dir, f"{video_id}.*"))
            if cand:
                video_path = cand[0]

        meta = {}
        thumbs = []
        if os.path.exists(video_path):
            try:
                meta = extract_metadata(video_path).model_dump()
                v_thumbs_dir = os.path.join(self.thumbs_dir, video_id)
                if not os.path.exists(v_thumbs_dir):
                    thumbs = extract_keyframe_thumbnails(video_path, v_thumbs_dir, num_thumbs=16)
                else:
                    thumb_files = sorted(glob.glob(os.path.join(v_thumbs_dir, "*.jpg")))
                    thumbs = [{
                        "filename": os.path.basename(tf),
                        "relative_url": f"/thumbnails/{video_id}/{os.path.basename(tf)}"
                    } for tf in thumb_files]
            except Exception:
                pass

        highlight_file = os.path.join(self.highlight_dir, f"{video_id}_highlight.mp4")

        result = {
            "samsung_output": official_data,
            "metadata": meta,
            "thumbnails": thumbs,
            "rendered_video_path": highlight_file if os.path.exists(highlight_file) else None,
            "timeline_series": [],
            "elapsed_seconds": 0.0
        }

        with _LOCK:
            _RESULTS_CACHE[video_id] = result
        return result

    def recompute_custom_highlights(
        self,
        video_id: str,
        highlight_intervals: List[Dict[str, Any]],
        render_video: bool = True
    ) -> Dict[str, Any]:
        """Allows user in Highlight Editor to adjust highlight segments while validating 15% budget."""
        json_path = os.path.join(self.json_dir, f"{video_id}.json")
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"JSON not found for {video_id}")

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        dur = data.get("duration", 60.0)
        tot = sum(float(h["end"]) - float(h["start"]) for h in highlight_intervals)

        data["highlights"] = highlight_intervals
        data["highlight_ratio"] = round(tot / dur, 4) if dur > 0 else 0.0

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        # Re-render highlight video
        if render_video:
            video_path = os.path.join(self.upload_dir, f"{video_id}.mp4")
            if os.path.exists(video_path):
                from ..schemas.video_schemas import HighlightItem
                h_items = [HighlightItem(**h) for h in highlight_intervals]
                out_highlight = os.path.join(self.highlight_dir, f"{video_id}_highlight.mp4")
                render_highlight_video(video_path, out_highlight, h_items)

        with _LOCK:
            if video_id in _RESULTS_CACHE:
                _RESULTS_CACHE[video_id]["samsung_output"] = data

        return data

    def list_all_videos(self) -> List[Dict[str, Any]]:
        """List all analyzed and uploaded videos."""
        videos = []
        uploaded = glob.glob(os.path.join(self.upload_dir, "*.mp4"))
        for up in uploaded:
            vid_id = os.path.splitext(os.path.basename(up))[0]
            json_p = os.path.join(self.json_dir, f"{vid_id}.json")
            has_json = os.path.exists(json_p)
            progress = self.get_progress(vid_id)

            item = {
                "video_id": vid_id,
                "filename": os.path.basename(up),
                "filepath": up,
                "has_analysis": has_json,
                "status": progress.status,
                "progress_pct": progress.progress_pct,
                "file_size_mb": round(os.path.getsize(up) / (1024 * 1024), 2)
            }
            if has_json:
                try:
                    with open(json_p, "r", encoding="utf-8") as f:
                        jd = json.load(f)
                    item["label"] = jd.get("label", "unknown")
                    item["duration"] = jd.get("duration", 0)
                    item["highlight_ratio"] = jd.get("highlight_ratio", 0)
                    item["actions_count"] = len(jd.get("actions", []))
                    item["highlights_count"] = len(jd.get("highlights", []))
                except Exception:
                    pass
            videos.append(item)
        return videos

