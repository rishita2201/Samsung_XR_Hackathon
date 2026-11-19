"""Module B: Intelligent Frame Sampling & Egocentric Motion Dynamics."""
import cv2
import numpy as np
from typing import List, Tuple, Generator, Optional


class VideoSamples:
    """Encapsulates sampled frames, exact timestamps, and egocentric motion statistics."""
    def __init__(
        self,
        frames: List[np.ndarray],
        timestamps: np.ndarray,
        hand_residual_motion: np.ndarray,
        global_camera_motion: np.ndarray,
        interaction_scores: np.ndarray,
        duration: float,
        native_fps: float,
        sampled_fps: float
    ):
        self.frames = frames  # List of BGR resized frames (e.g. 224x224)
        self.timestamps = np.asarray(timestamps, dtype=np.float64)
        self.hand_residual_motion = np.asarray(hand_residual_motion, dtype=np.float64)
        self.global_camera_motion = np.asarray(global_camera_motion, dtype=np.float64)
        self.interaction_scores = np.asarray(interaction_scores, dtype=np.float64)
        self.duration = float(duration)
        self.native_fps = float(native_fps)
        self.sampled_fps = float(sampled_fps)

    def __len__(self) -> int:
        return len(self.frames)


def _compute_motion_cues(gray_prev: np.ndarray, gray_curr: np.ndarray) -> Tuple[float, float, float]:
    """Compute dense Farneback optical flow and decompose into global head vs hand-zone residual motion."""
    # Farneback optical flow on downscaled grayscale
    flow = cv2.calcOpticalFlowFarneback(
        gray_prev, gray_curr, None,
        pyr_scale=0.5, levels=2, winsize=15, iterations=2, poly_n=5, poly_sigma=1.1, flags=0
    )
    # Global head/camera motion = median flow across entire field of view
    med_flow = np.median(flow.reshape(-1, 2), axis=0)
    global_motion = float(np.linalg.norm(med_flow))

    # Residual independent motion
    residual = np.linalg.norm(flow - med_flow, axis=2)
    h, w = residual.shape

    # Egocentric hand zone: lower-central region (H//2 to H, W//5 to 4*W//5)
    hand_zone = residual[h // 2:, int(w * 0.2): int(w * 0.8)]
    hand_residual = float(hand_zone.mean()) if hand_zone.size > 0 else 0.0

    # Interaction cue: residual motion in hand zone scaled by stability of camera
    # Active manipulation has significant hand motion while camera is focused
    interaction_cue = float(hand_residual / (1.0 + 0.5 * global_motion))

    return global_motion, hand_residual, interaction_cue


def sample_video_stream(
    video_path: str,
    target_fps: float = 2.0,
    frame_size: int = 224,
    flow_size: int = 160,
    max_samples: int = 3600
) -> VideoSamples:
    """Stream-samples frames at target FPS without loading the uncompressed full video into memory."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"Failed to open video file for sampling: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps != fps or fps < 1.0:
        fps = 30.0

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    step = max(1, int(round(fps / target_fps)))
    lag = max(1, min(step - 1, int(round(fps * 0.15)))) if step > 1 else 1

    frames = []
    timestamps = []
    hand_res_list = []
    glob_mot_list = []
    interaction_list = []

    frame_idx = 0
    while len(frames) < max_samples:
        if not cap.grab():
            break

        if frame_idx % step == 0:
            ok, frame_a = cap.retrieve()
            if not ok or frame_a is None:
                frame_idx += 1
                continue

            t_stamp = frame_idx / fps

            # Retrieve paired lag frame for flow computation
            frame_b = frame_a
            for _ in range(lag):
                if not cap.grab():
                    break
                frame_idx += 1
            ok2, frame_b_cand = cap.retrieve()
            if ok2 and frame_b_cand is not None:
                frame_b = frame_b_cand

            # Resize main frame for feature embedding
            resized_a = cv2.resize(frame_a, (frame_size, frame_size), interpolation=cv2.INTER_AREA)

            # Downsample for fast optical flow
            gray_a = cv2.cvtColor(cv2.resize(frame_a, (flow_size, flow_size)), cv2.COLOR_BGR2GRAY)
            gray_b = cv2.cvtColor(cv2.resize(frame_b, (flow_size, flow_size)), cv2.COLOR_BGR2GRAY)

            glob_m, hand_r, inter_cue = _compute_motion_cues(gray_a, gray_b)

            frames.append(resized_a)
            timestamps.append(t_stamp)
            glob_mot_list.append(glob_m)
            hand_res_list.append(hand_r)
            interaction_list.append(inter_cue)

        frame_idx += 1

    cap.release()

    if not frames:
        raise IOError(f"No valid frames could be decoded from {video_path}")

    duration = total_frames / fps if total_frames > 0 else (timestamps[-1] + step / fps)
    duration = max(duration, timestamps[-1] + 0.25)
    actual_sampled_fps = len(frames) / duration if duration > 0 else target_fps

    return VideoSamples(
        frames=frames,
        timestamps=np.array(timestamps),
        hand_residual_motion=np.array(hand_res_list),
        global_camera_motion=np.array(glob_mot_list),
        interaction_scores=np.array(interaction_list),
        duration=duration,
        native_fps=fps,
        sampled_fps=actual_sampled_fps
    )

