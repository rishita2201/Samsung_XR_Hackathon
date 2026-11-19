"""Egocentric motion extraction, optical flow dynamics, and visual embeddings."""
import glob
import os
import cv2
import numpy as np


class Sampled:
    def __init__(self, frames, times, hand_res, glob_mot, hoi_scores, duration, fps):
        self.frames = frames
        self.times = np.asarray(times, dtype=np.float64)
        self.hand_res = np.asarray(hand_res, dtype=np.float64)   # residual motion in hand zone
        self.glob_mot = np.asarray(glob_mot, dtype=np.float64)   # head / camera motion
        self.hoi_scores = np.asarray(hoi_scores, dtype=np.float64) # hand-object interaction cues
        self.duration = float(duration)
        self.fps = float(fps)


def _flow_stats(ga, gb):
    flow = cv2.calcOpticalFlowFarneback(ga, gb, None, 0.5, 2, 15, 2, 5, 1.1, 0)
    med = np.median(flow.reshape(-1, 2), axis=0)          # camera (head) motion
    res = np.linalg.norm(flow - med, axis=2)              # what moves independently of the head
    H, W = res.shape
    hand_zone = res[H // 2:, W // 5: 4 * W // 5]          # lower-centre = where egocentric hands live
    hand_r = float(hand_zone.mean()) if hand_zone.size > 0 else 0.0
    return float(np.linalg.norm(med)), hand_r


def sample_video(path, fps_target=2.0, size=224, max_samples=3600):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise IOError(f"cannot open video: {path}")
    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps != fps or fps < 1:
        fps = 30.0
    n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    step = max(1, int(round(fps / fps_target)))
    lag = max(1, min(step - 1, int(round(fps * 0.15)))) if step > 1 else 1
    frames, times, hand, glob_m, hoi_list = [], [], [], [], []
    idx = 0
    while len(frames) < max_samples:
        if not cap.grab():
            break
        if idx % step == 0:
            ok, a = cap.retrieve()
            if not ok or a is None:
                idx += 1
                continue
            t = idx / fps
            b = a
            for _ in range(lag):
                if not cap.grab():
                    break
                idx += 1
            ok2, b2 = cap.retrieve()
            if ok2 and b2 is not None:
                b = b2
            a = cv2.resize(a, (size, size), interpolation=cv2.INTER_AREA)
            b = cv2.resize(b, (size, size), interpolation=cv2.INTER_AREA)
            ga = cv2.cvtColor(cv2.resize(a, (160, 160)), cv2.COLOR_BGR2GRAY)
            gb = cv2.cvtColor(cv2.resize(b, (160, 160)), cv2.COLOR_BGR2GRAY)
            g, h = _flow_stats(ga, gb)

            # Egocentric Hand-Object Interaction (HOI) cue
            lower = a[int(size * 0.45):, :]
            ycrcb = cv2.cvtColor(lower, cv2.COLOR_BGR2YCrCb)
            skin = cv2.inRange(ycrcb, np.array([0, 133, 77]), np.array([255, 173, 127]))
            skin_density = float(np.count_nonzero(skin)) / float(skin.size + 1e-6)
            hoi_cue = 0.5 * min(1.0, skin_density * 6.0) + 0.5 * min(1.0, h * 0.35)

            frames.append(a); times.append(t); hand.append(h); glob_m.append(g); hoi_list.append(hoi_cue)
        idx += 1
    cap.release()
    if not frames:
        raise IOError("no frames decoded")
    duration = n_frames / fps if n_frames > 0 else times[-1] + step / fps
    duration = max(duration, times[-1] + 0.25)
    return Sampled(frames, times, hand, glob_m, hoi_list, duration, fps)


def _l2(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


class Embedder:
    """CLIP (open_clip) when weights are available, otherwise a color/layout fallback."""

    def __init__(self, weights_dir=None, use_clip=True):
        self.clip = None
        if not use_clip or not weights_dir:
            return
        ckpts = sorted(glob.glob(os.path.join(weights_dir, "clip_*.pt")))
        if not ckpts:
            return
        try:
            import torch, open_clip
            model, _, _ = open_clip.create_model_and_transforms(
                "ViT-B-32-quickgelu", pretrained=ckpts[0])
            self.model = model.eval()
            self.tok = open_clip.get_tokenizer("ViT-B-32-quickgelu")
            self.torch = torch
            self.mean = np.array([0.48145466, 0.4578275, 0.40821073], dtype=np.float32)
            self.std = np.array([0.26862954, 0.26130258, 0.27577711], dtype=np.float32)
            self.clip = True
        except Exception as e:
            print(f"[warn] CLIP unavailable ({e}); using fallback embeddings")
            self.clip = None

    @property
    def semantic(self):
        return bool(self.clip)

    def encode_images(self, frames_bgr, batch=64):
        if self.clip:
            out = []
            with self.torch.no_grad():
                for i in range(0, len(frames_bgr), batch):
                    x = np.stack([cv2.cvtColor(f, cv2.COLOR_BGR2RGB) for f in frames_bgr[i:i + batch]])
                    x = (x.astype(np.float32) / 255.0 - self.mean) / self.std
                    x = self.torch.from_numpy(x).permute(0, 3, 1, 2).contiguous()
                    out.append(self.model.encode_image(x).float().cpu().numpy())
            return _l2(np.concatenate(out))
        feats = []
        for f in frames_bgr:
            hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
            h = cv2.calcHist([hsv], [0, 1, 2], None, [8, 4, 4], [0, 180, 0, 256, 0, 256]).ravel()
            g = cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), (8, 8), interpolation=cv2.INTER_AREA)
            g = g.astype(np.float32).ravel()
            g -= g.mean()
            feats.append(np.concatenate([_l2(h.astype(np.float32)), _l2(g)]))
        return _l2(np.asarray(feats, dtype=np.float32))

    def encode_text(self, texts):
        with self.torch.no_grad():
            t = self.model.encode_text(self.tok(texts)).float().cpu().numpy()
        return _l2(t)

