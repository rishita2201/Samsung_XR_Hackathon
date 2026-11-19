"""Module D: Egocentric Hand-Object Interaction Understanding."""
import cv2
import numpy as np
from typing import List, Tuple, Dict


def detect_skin_regions(frame_bgr: np.ndarray) -> np.ndarray:
    """Detect human skin color probabilities in YCrCb and HSV color space.
    Calibrated for diverse skin tones under varying lighting conditions."""
    ycrcb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2YCrCb)
    # Standard biological ranges for skin tone in YCrCb: Cr in [133, 173], Cb in [77, 127]
    mask_ycrcb = cv2.inRange(ycrcb, np.array([0, 133, 77]), np.array([255, 173, 127]))

    # Cross-verify with HSV to suppress false positives
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    mask_hsv = cv2.inRange(hsv, np.array([0, 20, 50]), np.array([25, 255, 255]))

    skin_mask = cv2.bitwise_and(mask_ycrcb, mask_hsv)
    # Morphological opening and closing to remove noise and bridge contours
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel, iterations=1)
    skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel, iterations=1)
    return skin_mask


def analyze_hand_object_interactions(frames: List[np.ndarray], hand_residuals: np.ndarray) -> np.ndarray:
    """Analyze hand presence, object boundaries, and manipulation dynamics across all sampled frames.
    Returns per-frame Hand-Object Interaction (HOI) scores in [0, 1]."""
    n_frames = len(frames)
    if n_frames == 0:
        return np.array([], dtype=np.float64)

    hoi_scores = np.zeros(n_frames, dtype=np.float64)

    for i, frame in enumerate(frames):
        h, w = frame.shape[:2]
        # In egocentric video, hands operate in the lower 60% of the screen
        lower_region = frame[int(h * 0.4):, :]
        lh, lw = lower_region.shape[:2]

        # 1. Skin detection in manipulation zone
        skin_mask = detect_skin_regions(lower_region)
        skin_density = float(np.count_nonzero(skin_mask)) / float(lh * lw + 1e-6)
        hand_presence = float(np.clip(skin_density * 8.0, 0.0, 1.0))

        # 2. Object edge density (Canny) in center-of-gaze manipulation zone
        # Active objects usually reside in the central portion of the lower region
        center_zone = lower_region[:, int(lw * 0.25): int(lw * 0.75)]
        gray_center = cv2.cvtColor(center_zone, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray_center, 60, 180)
        edge_density = float(np.count_nonzero(edges)) / float(edges.size + 1e-6)
        object_saliency = float(np.clip(edge_density * 10.0, 0.0, 1.0))

        # 3. Residual motion in hand zone
        res_motion = float(hand_residuals[i]) if i < len(hand_residuals) else 0.0

        # 4. Synthesize composite HOI index
        # True hand-object interaction exhibits both hand presence/motion and high object boundary detail
        composite = 0.40 * hand_presence + 0.35 * object_saliency + 0.25 * min(1.0, res_motion * 0.3)
        hoi_scores[i] = composite

    # Normalize to [0, 1] with percentile clipping to prevent outlier spikes
    p95 = np.percentile(hoi_scores, 95) if n_frames > 1 else 1.0
    if p95 > 1e-4:
        hoi_scores = np.clip(hoi_scores / p95, 0.0, 1.0)
    else:
        hoi_scores = np.zeros(n_frames)

    return hoi_scores

