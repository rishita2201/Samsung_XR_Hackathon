"""Module A: Video Ingestion & Metadata Extraction."""
import os
import re
import datetime
import cv2
from typing import Dict, Any, Optional
from ..schemas.video_schemas import VideoMetadata


def sanitize_video_id(filename: str) -> str:
    """Generate a clean, reproducible video ID from filename."""
    base = os.path.splitext(os.path.basename(filename))[0]
    # Replace non-alphanumeric with underscore, keep hyphens
    clean = re.sub(r'[^a-zA-Z0-9_\-]', '_', base)
    clean = re.sub(r'_+', '_', clean).strip('_')
    return clean or "video_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def extract_metadata(video_path: str) -> VideoMetadata:
    """Validate video file integrity and extract technical metadata without full RAM loading."""
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found at: {video_path}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video stream or corrupted MP4: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps != fps or fps < 1.0 or fps > 240.0:
        fps = 30.0

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)

    # Calculate duration
    if frame_count > 0 and fps > 0:
        duration = round(frame_count / fps, 3)
    else:
        # Fallback duration probe
        count = 0
        while cap.grab():
            count += 1
        frame_count = count
        duration = round(count / fps, 3)
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    cap.release()

    video_id = sanitize_video_id(video_path)
    return VideoMetadata(
        video_id=video_id,
        filename=os.path.basename(video_path),
        filepath=os.path.abspath(video_path),
        duration=duration,
        fps=round(float(fps), 2),
        frame_count=frame_count,
        width=width,
        height=height,
        created_at=datetime.datetime.now().isoformat()
    )


def extract_keyframe_thumbnails(video_path: str, output_dir: str, num_thumbs: int = 12) -> list[dict]:
    """Extract equally spaced thumbnail previews for interactive timeline scrubber in UI."""
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    if total_frames <= 0:
        cap.release()
        return []

    indices = [int(i * (total_frames - 1) / max(1, num_thumbs - 1)) for i in range(num_thumbs)]
    thumbnails = []

    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, frame = cap.read()
        if not ok or frame is None:
            continue
        timestamp = round(idx / fps, 2)
        thumb_name = f"thumb_{idx}_{int(timestamp * 100)}.jpg"
        thumb_path = os.path.join(output_dir, thumb_name)
        # Resize to compact thumbnail for fast frontend loading
        h, w = frame.shape[:2]
        new_w = 240
        new_h = int(h * (240.0 / w))
        resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
        cv2.imwrite(thumb_path, resized, [cv2.IMWRITE_JPEG_QUALITY, 80])
        thumbnails.append({
            "frame_idx": idx,
            "timestamp": timestamp,
            "filename": thumb_name,
            "relative_url": f"/thumbnails/{thumb_name}"
        })

    cap.release()
    return thumbnails

