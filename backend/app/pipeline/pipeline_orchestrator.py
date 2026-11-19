"""MOMENTIQ End-to-End Video Understanding & Highlight Pipeline Orchestrator."""
import os
import json
import time
import numpy as np
from typing import Dict, Any, Optional, Callable

from ..schemas.video_schemas import (
    SamsungOutputSchema, ActionItem, HighlightItem, AnalysisResult
)
from .video_ingest import extract_metadata, extract_keyframe_thumbnails
from .intelligent_sampler import sample_video_stream
from .hand_object_detector import analyze_hand_object_interactions
from .action_recognizer import VisualEmbedder, ActionClassifier, load_supported_classes
from .temporal_localizer import detect_change_points, localize_actions
from .importance_scorer import compute_segment_importance
from .highlight_selector import select_optimal_highlights
from .video_renderer import render_highlight_video


class MomentiqPipeline:
    def __init__(self, weights_dir: Optional[str] = None, classes_path: Optional[str] = None):
        self.weights_dir = weights_dir or os.path.abspath("backend/weights")
        self.classes_path = classes_path or os.path.join(self.weights_dir, "supported_classes.json")

        # Load vocabulary
        self.verbs, self.nouns, self.categories = load_supported_classes(self.classes_path)

        # Initialize visual embedder with weights
        self.embedder = VisualEmbedder(self.weights_dir)
        self.classifier = ActionClassifier(self.embedder, self.verbs, self.nouns, self.categories)

    def run(
        self,
        video_path: str,
        output_json_path: Optional[str] = None,
        output_highlight_video_path: Optional[str] = None,
        progress_callback: Optional[Callable[[str, int], None]] = None,
        target_budget: float = 0.15
    ) -> Dict[str, Any]:
        """Execute end-to-end MOMENTIQ pipeline on an input video."""
        t_start = time.time()
        video_id = os.path.splitext(os.path.basename(video_path))[0]

        def report(msg: str, pct: int):
            if progress_callback:
                progress_callback(msg, pct)
            print(f"[{video_id}] {pct}% - {msg}")

        # 1. Ingestion
        report("Extracting video metadata and verifying stream...", 10)
        metadata = extract_metadata(video_path)
        video_id = metadata.video_id

        # 2. Intelligent Frame Sampling & Flow
        report("Sampling frames & computing egocentric motion dynamics...", 25)
        samples = sample_video_stream(video_path, target_fps=2.0)

        # 3. Hand-Object Interaction Detection
        report("Detecting hand-object interactions in manipulation zones...", 40)
        hoi_scores = analyze_hand_object_interactions(samples.frames, samples.hand_residual_motion)

        # 4. Feature Encoding
        report("Extracting spatio-temporal CLIP visual representations...", 55)
        embeddings = self.embedder.encode_images(samples.frames)

        # 5. Video Category Classification (FPVSum)
        report("Classifying global video context...", 65)
        video_mean_feat = embeddings.mean(axis=0)
        video_mean_feat /= (np.linalg.norm(video_mean_feat) + 1e-8)
        video_category = self.classifier.predict_video_category(video_mean_feat)

        # 6. Change-Point Segmentation & Importance Scoring
        report("Segmenting activities and computing explainable importance...", 75)
        dt = float(np.median(np.diff(samples.timestamps))) if len(samples.timestamps) > 1 else 0.5
        change_boundaries = detect_change_points(embeddings, dt=dt)
        scored_segments = compute_segment_importance(
            samples, embeddings, change_boundaries, self.classifier, hoi_scores
        )

        # 7. Temporal Action Localization
        report("Localizing human actions and refining temporal boundaries...", 85)
        localized_actions = localize_actions(scored_segments)

        # 8. Budget-Constrained Highlight Selection (<= 15%)
        report("Selecting optimal non-redundant highlights under 15% budget...", 90)
        selected_highlights = select_optimal_highlights(
            scored_segments,
            video_duration=samples.duration,
            budget_ratio=target_budget
        )

        # Compute actual duration and compression
        total_highlight_duration = sum(h.end - h.start for h in selected_highlights)
        actual_ratio = round(total_highlight_duration / samples.duration, 4) if samples.duration > 0 else 0.0

        # Construct official Samsung output schema
        cat_name = video_category if isinstance(video_category, str) else str(video_category.get("name", "other"))
        label_obj = {
            "name": cat_name,
            "score": 0.95
        }
        official_output = {
            "team_id": "VITChennai_RRR",
            "video_id": video_id,
            "duration_sec": round(float(samples.duration), 2),
            "label": label_obj,
            "actions": [
                {
                    "segment": [round(float(a.start), 2), round(float(a.end), 2)],
                    "verb": a.verb,
                    "noun": a.noun,
                    "score": round(float(a.confidence or 0.85), 3)
                } for a in localized_actions
            ],
            "highlights": [
                {
                    "segment": [round(float(h.start), 2), round(float(h.end), 2)]
                } for h in selected_highlights
            ]
        }

        # 9. Optional Highlight Video Rendering
        rendered_video_path = None
        if output_highlight_video_path:
            report("Rendering playable MP4 highlight video from original footage...", 95)
            try:
                rendered_video_path = render_highlight_video(
                    video_path, output_highlight_video_path, selected_highlights
                )
            except Exception as e:
                print(f"[warn] Highlight rendering error: {e}")

        # Save JSON output if requested
        if output_json_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_json_path)), exist_ok=True)
            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(official_output, f, indent=2)

        # Generate timeline series for visualization in frontend
        timeline_series = []
        for i, t_val in enumerate(samples.timestamps):
            timeline_series.append({
                "time": round(float(t_val), 2),
                "activity": round(float(samples.hand_residual_motion[i]), 3),
                "camera_motion": round(float(samples.global_camera_motion[i]), 3),
                "interaction": round(float(hoi_scores[i]), 3) if i < len(hoi_scores) else 0.0
            })

        report("Pipeline complete!", 100)
        elapsed = round(time.time() - t_start, 2)
        print(f"[{video_id}] Finished in {elapsed}s: {len(localized_actions)} actions, "
              f"{len(selected_highlights)} highlights ({100*actual_ratio:.1f}% duration)")

        return {
            "samsung_output": official_output,
            "metadata": metadata.model_dump(),
            "rendered_video_path": rendered_video_path,
            "timeline_series": timeline_series,
            "elapsed_seconds": elapsed
        }

