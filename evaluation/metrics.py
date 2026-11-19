"""Official 100-Point Jury Evaluation Metrics for Samsung XR Hackathon Track 4.
Supports both the official Student Package schema and legacy format.
"""
import numpy as np
from typing import List, Dict, Any, Tuple


def _extract_span(item: Dict[str, Any]) -> Tuple[float, float]:
    """Extracts (start, end) tuple from either 'segment': [s, e] or 'start'/'end' keys."""
    if "segment" in item and isinstance(item["segment"], (list, tuple)) and len(item["segment"]) == 2:
        return float(item["segment"][0]), float(item["segment"][1])
    return float(item.get("start", 0.0)), float(item.get("end", 0.0))


def _extract_label(val: Any) -> str:
    """Extracts label name string from either dict {"name": ...} or direct string."""
    if isinstance(val, dict):
        return str(val.get("name", "")).strip().lower()
    return str(val).strip().lower()


def _extract_score(item: Dict[str, Any]) -> float:
    """Extracts confidence or score float."""
    if "score" in item and item["score"] is not None:
        try:
            return float(item["score"])
        except (ValueError, TypeError):
            pass
    return float(item.get("confidence", 0.5))


def compute_tiou(seg_a: Tuple[float, float], seg_b: Tuple[float, float]) -> float:
    """Computes temporal Intersection over Union (tIoU) between two time intervals."""
    start_a, end_a = seg_a
    start_b, end_b = seg_b
    intersection = max(0.0, min(end_a, end_b) - max(start_a, start_b))
    union = max(end_a, end_b) - min(start_a, start_b)
    if union <= 0.0:
        return 0.0
    return intersection / union


def compute_action_map(
    predictions: List[Dict[str, Any]],
    ground_truth: List[Dict[str, Any]],
    tiou_thresholds: List[float] = [0.1, 0.2, 0.3, 0.4, 0.5]
) -> float:
    """Computes Action Mean Average Precision (mAP) for verb-noun pairs at tIoU 0.1-0.5.
    Accounts for 25% of total evaluation score."""
    if not ground_truth or not predictions:
        return 0.0

    ap_per_threshold = []

    for thr in tiou_thresholds:
        matched_gt = set()
        tp = 0
        fp = 0

        # Sort predictions by score/confidence
        sorted_preds = sorted(predictions, key=_extract_score, reverse=True)

        for p in sorted_preds:
            p_span = _extract_span(p)
            p_verb = str(p.get("verb", "")).strip().lower()
            p_noun = str(p.get("noun", "")).strip().lower()

            best_match_idx = -1
            best_iou = -1.0

            for gt_idx, gt in enumerate(ground_truth):
                if gt_idx in matched_gt:
                    continue
                gt_verb = str(gt.get("verb", "")).strip().lower()
                gt_noun = str(gt.get("noun", "")).strip().lower()

                # Both verb and noun must match
                if p_verb == gt_verb and p_noun == gt_noun:
                    gt_span = _extract_span(gt)
                    iou = compute_tiou(p_span, gt_span)
                    if iou >= thr and iou > best_iou:
                        best_iou = iou
                        best_match_idx = gt_idx

            if best_match_idx >= 0:
                tp += 1
                matched_gt.add(best_match_idx)
            else:
                fp += 1

        precision = tp / max(1, tp + fp)
        recall = tp / max(1, len(ground_truth))
        ap = precision * recall
        ap_per_threshold.append(ap)

    return float(np.mean(ap_per_threshold)) if ap_per_threshold else 0.0


def compute_action_coverage(
    highlights: List[Dict[str, Any]],
    ground_truth_actions: List[Dict[str, Any]],
    video_duration: float,
    budget_cap: float = 0.15
) -> float:
    """Computes Action Coverage (40% official weight):
    Fraction of distinct ground truth (verb, noun) action pairs captured by highlights.
    Soft penalty is applied if highlights exceed the 15% budget."""
    if not ground_truth_actions:
        return 1.0

    distinct_gt_pairs = set(
        (str(gt.get("verb", "")).strip().lower(), str(gt.get("noun", "")).strip().lower())
        for gt in ground_truth_actions
    )
    if not distinct_gt_pairs:
        return 1.0

    captured_pairs = set()

    for gt in ground_truth_actions:
        gt_pair = (str(gt.get("verb", "")).strip().lower(), str(gt.get("noun", "")).strip().lower())
        gt_start, gt_end = _extract_span(gt)

        # Check if any highlight interval overlaps this action instance
        for h in highlights:
            h_start, h_end = _extract_span(h)
            overlap = max(0.0, min(gt_end, h_end) - max(gt_start, h_start))
            if overlap >= 0.5:  # At least 0.5s overlap
                captured_pairs.add(gt_pair)
                break

    raw_coverage = len(captured_pairs) / len(distinct_gt_pairs)

    # Calculate budget penalty if highlights exceed 15%
    total_highlight_time = sum(_extract_span(h)[1] - _extract_span(h)[0] for h in highlights)
    allowed_time = budget_cap * video_duration
    if total_highlight_time > allowed_time + 1e-4:
        overage_ratio = (total_highlight_time - allowed_time) / allowed_time
        penalty = min(0.5, overage_ratio * 0.5)
        raw_coverage = max(0.0, raw_coverage - penalty)

    return float(np.clip(raw_coverage, 0.0, 1.0))


def compute_highlight_f1(
    predicted_highlights: List[Dict[str, Any]],
    ground_truth_highlights: List[Dict[str, Any]],
    video_duration: float,
    sample_rate_hz: int = 2
) -> float:
    """Computes frame-level F1 score against top-15% human consensus (25% weight)."""
    if video_duration <= 0:
        return 0.0
    n_frames = max(1, int(round(video_duration * sample_rate_hz)))
    pred_mask = np.zeros(n_frames, dtype=bool)
    gt_mask = np.zeros(n_frames, dtype=bool)

    # Rasterize predicted highlights
    for h in predicted_highlights:
        s, e = _extract_span(h)
        idx_s = max(0, min(n_frames - 1, int(round(s * sample_rate_hz))))
        idx_e = max(0, min(n_frames, int(round(e * sample_rate_hz))))
        pred_mask[idx_s:idx_e] = True

    # Rasterize ground truth highlights
    for h in ground_truth_highlights:
        s, e = _extract_span(h)
        idx_s = max(0, min(n_frames - 1, int(round(s * sample_rate_hz))))
        idx_e = max(0, min(n_frames, int(round(e * sample_rate_hz))))
        gt_mask[idx_s:idx_e] = True

    tp = np.logical_and(pred_mask, gt_mask).sum()
    fp = np.logical_and(pred_mask, np.logical_not(gt_mask)).sum()
    fn = np.logical_and(np.logical_not(pred_mask), gt_mask).sum()

    precision = tp / max(1, tp + fp)
    recall = tp / max(1, tp + fn)
    if (precision + recall) == 0:
        return 0.0
    f1 = 2.0 * (precision * recall) / (precision + recall)
    return float(f1)


def compute_label_accuracy(pred_label: Any, gt_label: Any) -> float:
    """Computes categorical accuracy for video-level category tag (10% weight)."""
    p = _extract_label(pred_label)
    g = _extract_label(gt_label)
    if not p or not g:
        return 0.0
    return 1.0 if p == g else 0.0


def calculate_100_point_score(
    action_map: float,
    action_coverage: float,
    highlight_f1: float,
    label_accuracy: float
) -> Dict[str, Any]:
    """Official 100-point rubric calculation:
    - Action mAP: 25 pts (25%)
    - Action Coverage: 40 pts (40%)
    - Highlight F1: 25 pts (25%)
    - Label Accuracy: 10 pts (10%)
    """
    pts_map = round(action_map * 25.0, 2)
    pts_cov = round(action_coverage * 40.0, 2)
    pts_f1 = round(highlight_f1 * 25.0, 2)
    pts_label = round(label_accuracy * 10.0, 2)
    total = round(pts_map + pts_cov + pts_f1 + pts_label, 2)

    return {
        "points_action_map": pts_map,
        "points_action_coverage": pts_cov,
        "points_highlight_f1": pts_f1,
        "points_label_accuracy": pts_label,
        "total_score_100": total,
        "action_map_pct": round(action_map * 100, 1),
        "action_coverage_pct": round(action_coverage * 100, 1),
        "highlight_f1_pct": round(highlight_f1 * 100, 1),
        "label_accuracy_pct": round(label_accuracy * 100, 1),
    }
