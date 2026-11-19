"""Module E: Temporal Action Localization & Boundary Refinement."""
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from ..schemas.video_schemas import ActionItem


class TemporalSegment:
    """Represents a localized temporal video chunk."""
    __slots__ = (
        "idx_start", "idx_end", "t_start", "t_end",
        "embedding", "activity_score", "interaction_score",
        "novelty_score", "confidence", "verb", "noun",
        "importance", "peak_timestamp", "cluster_key"
    )

    def __init__(self):
        self.idx_start: int = 0
        self.idx_end: int = 0
        self.t_start: float = 0.0
        self.t_end: float = 0.0
        self.embedding: Optional[np.ndarray] = None
        self.activity_score: float = 0.0
        self.interaction_score: float = 0.0
        self.novelty_score: float = 0.0
        self.confidence: float = 0.0
        self.verb: str = "unknown"
        self.noun: str = "unknown"
        self.importance: float = 0.0
        self.peak_timestamp: float = 0.0
        self.cluster_key: Tuple[str, str] = ("unknown", "unknown")


def detect_change_points(
    embeddings: np.ndarray,
    dt: float,
    min_duration: float = 2.0,
    max_duration: float = 8.0
) -> List[Tuple[int, int]]:
    """Detect visual transition boundaries using cosine distance change-points."""
    n_samples = len(embeddings)
    min_steps = max(1, int(round(min_duration / dt)))
    max_steps = max(2, int(round(max_duration / dt)))

    if n_samples <= min_steps:
        return [(0, n_samples)]

    # Cosine distance between consecutive frames
    cosine_diffs = 1.0 - np.sum(embeddings[1:] * embeddings[:-1], axis=1)
    threshold = float(cosine_diffs.mean() + 0.85 * cosine_diffs.std())

    boundaries = [0]
    for i in range(1, n_samples):
        elapsed = i - boundaries[-1]
        if (cosine_diffs[i - 1] > threshold and elapsed >= min_steps) or elapsed >= max_steps:
            boundaries.append(i)

    # Merge small tail segment if necessary
    if n_samples - boundaries[-1] < min_steps and len(boundaries) > 1:
        boundaries.pop()
    boundaries.append(n_samples)

    return list(zip(boundaries[:-1], boundaries[1:]))


def localize_actions(
    segments: List[TemporalSegment],
    min_activity_threshold: float = 0.30,
    merge_gap: float = 0.75
) -> List[ActionItem]:
    """Formulate localized action instances with boundary smoothing and merge adjacent identical actions."""
    raw_actions = []

    for s in segments:
        # Ignore idle / static video segments
        if s.activity_score < min_activity_threshold:
            continue

        raw_actions.append(ActionItem(
            verb=s.verb,
            noun=s.noun,
            start=round(s.t_start, 2),
            end=round(s.t_end, 2),
            confidence=round(s.confidence, 3)
        ))

    # Merge contiguous actions sharing same (verb, noun)
    merged_actions: List[ActionItem] = []
    for act in raw_actions:
        if not merged_actions:
            merged_actions.append(act)
            continue

        prev = merged_actions[-1]
        if (prev.verb == act.verb and prev.noun == act.noun and (act.start - prev.end) <= merge_gap):
            # Extend duration and update confidence
            prev.end = max(prev.end, act.end)
            if act.confidence and prev.confidence:
                prev.confidence = round(max(prev.confidence, act.confidence), 3)
        else:
            merged_actions.append(act)

    return merged_actions

