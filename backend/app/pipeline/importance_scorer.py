"""Module F: Explainable Multi-Factor Importance Scoring."""
import numpy as np
from typing import List, Tuple, Optional
from .temporal_localizer import TemporalSegment
from .intelligent_sampler import VideoSamples
from .action_recognizer import ActionClassifier


def rank_normalize(values: np.ndarray) -> np.ndarray:
    """Normalize array of values to uniform rank percentiles in [0, 1]."""
    x = np.asarray(values, dtype=np.float64)
    n = len(x)
    if n < 2:
        return np.full(n, 0.5)
    ranks = np.empty(n, dtype=np.float64)
    ranks[np.argsort(x, kind="stable")] = np.arange(n, dtype=np.float64)
    return ranks / (n - 1.0)


def temporal_smooth(x: np.ndarray, window_size: int = 3) -> np.ndarray:
    """Apply moving average smoothing with edge padding."""
    if window_size <= 1 or len(x) < window_size:
        return np.asarray(x, dtype=np.float64)
    pad = window_size // 2
    padded = np.pad(x, pad, mode="edge")
    return np.convolve(padded, np.ones(window_size) / window_size, mode="valid")


def compute_segment_importance(
    samples: VideoSamples,
    embeddings: np.ndarray,
    boundaries: List[Tuple[int, int]],
    classifier: Optional[ActionClassifier] = None,
    hoi_scores: Optional[np.ndarray] = None,
    weights: Tuple[float, float, float, float] = (0.40, 0.25, 0.20, 0.15)
) -> List[TemporalSegment]:
    """Score importance across all candidate segments using an explainable multi-cue model.
    Weights: (activity, interaction, novelty, confidence)."""
    t = samples.timestamps
    total_dur = samples.duration

    # Composite frame-level activity: hand residual motion + moderate global camera motion
    raw_activity = samples.hand_residual_motion + 0.25 * samples.global_camera_motion
    frame_act = rank_normalize(temporal_smooth(raw_activity, window_size=3))

    # Hand-Object Interaction (HOI) scores
    if hoi_scores is None or len(hoi_scores) != len(samples):
        frame_hoi = frame_act
    else:
        frame_hoi = rank_normalize(temporal_smooth(hoi_scores, window_size=3))

    # Global video centroid representation for novelty computation
    global_centroid = embeddings.mean(axis=0)
    global_centroid /= (np.linalg.norm(global_centroid) + 1e-8)

    segments: List[TemporalSegment] = []

    for idx_start, idx_end in boundaries:
        seg = TemporalSegment()
        seg.idx_start = idx_start
        seg.idx_end = idx_end
        seg.t_start = float(t[idx_start]) if idx_start > 0 else 0.0
        seg.t_end = float(t[idx_end - 1]) if idx_end <= len(t) else float(total_dur)
        if seg.t_end <= seg.t_start:
            seg.t_end = min(total_dur, seg.t_start + 1.0)

        # Pooled segment embedding
        seg_emb = embeddings[idx_start:idx_end].mean(axis=0)
        seg.embedding = seg_emb / (np.linalg.norm(seg_emb) + 1e-8)

        # Activity and interaction cues
        seg.activity_score = float(frame_act[idx_start:idx_end].mean())
        seg.interaction_score = float(frame_hoi[idx_start:idx_end].mean())

        # Peak motion timestamp within this segment (for peak-centered trimming)
        rel_peak_idx = int(frame_act[idx_start:idx_end].argmax())
        seg.peak_timestamp = float(t[idx_start + rel_peak_idx])

        # Semantic novelty: visual distance from the overall video centroid
        seg.novelty_score = float(1.0 - (seg.embedding @ global_centroid))

        # Predict verb and noun
        seg.verb = "unknown"
        seg.noun = "unknown"
        seg.confidence = 0.0
        if classifier is not None:
            seg.verb, seg.noun, seg.confidence, _ = classifier.predict_action(seg.embedding)

        segments.append(seg)

    # Rank-normalize cross-segment features for balanced multi-factor scoring
    nov_ranks = rank_normalize([s.novelty_score for s in segments])
    conf_ranks = rank_normalize([s.confidence for s in segments]) if classifier is not None else np.zeros(len(segments))
    inter_ranks = rank_normalize([s.interaction_score for s in segments])

    w_act, w_inter, w_nov, w_conf = weights if classifier is not None else (0.50, 0.30, 0.20, 0.0)

    # Compute final explainable importance score
    for s, n_rank, c_rank, i_rank in zip(segments, nov_ranks, conf_ranks, inter_ranks):
        score = (w_act * s.activity_score +
                 w_inter * i_rank +
                 w_nov * n_rank +
                 w_conf * c_rank)
        # Idle penalty: heavy suppression for segments with minimal movement
        if s.activity_score < 0.20 and s.interaction_score < 0.20:
            score *= 0.5

        s.importance = float(np.clip(score, 0.0, 1.0))

    # Diversity clustering key for MMR highlight selection
    visual_cluster_centers = []
    for s in segments:
        if classifier is not None and s.verb != "unknown":
            s.cluster_key = (s.verb, s.noun)
        else:
            # Fallback visual cluster
            matched_cluster = None
            for c_id, center in enumerate(visual_cluster_centers):
                if float(center @ s.embedding) > 0.88:
                    matched_cluster = c_id
                    break
            if matched_cluster is None:
                visual_cluster_centers.append(s.embedding)
                matched_cluster = len(visual_cluster_centers) - 1
            s.cluster_key = ("cluster", str(matched_cluster))

    return segments

