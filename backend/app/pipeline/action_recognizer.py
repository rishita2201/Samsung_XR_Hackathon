"""Module C: Action Recognition with CLIP Pretrained Backbone & Lenient Class Vocabularies."""
import os
import glob
import json
import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional, Any


def _l2_normalize(x: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(x, axis=-1, keepdims=True)
    return x / (norm + 1e-8)


def _softmax(x: np.ndarray, temperature: float = 1.0) -> np.ndarray:
    x_scaled = (x - np.max(x)) / max(1e-5, temperature)
    exp_x = np.exp(x_scaled)
    return exp_x / np.sum(exp_x)


def _format_noun_phrase(n: str) -> str:
    """Format EPIC-KITCHENS compound nouns e.g. 'pan:frying' -> 'frying pan'."""
    if ":" in n:
        parts = n.split(":", 1)
        return f"{parts[1].replace(':', ' ')} {parts[0]}"
    return n.replace("_", " ")


def load_supported_classes(classes_path: Optional[str]) -> Tuple[List[str], List[str], List[str]]:
    """Lenient loader: handles strings or dicts from supported_classes.json."""
    if not classes_path or not os.path.exists(classes_path):
        return [], [], []

    try:
        with open(classes_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[warn] Failed to read classes json: {e}")
        return [], [], []

    def extract_names(items):
        res = []
        for it in items or []:
            if isinstance(it, str):
                res.append(it)
            elif isinstance(it, dict):
                val = it.get("key") or it.get("name") or it.get("class") or it.get("label")
                if val:
                    res.append(str(val))
        return res

    verbs = extract_names(data.get("verbs") or data.get("verb_classes"))
    nouns = extract_names(data.get("nouns") or data.get("noun_classes"))
    cats = extract_names(data.get("categories") or data.get("labels") or data.get("video_categories"))
    return verbs, nouns, cats


class VisualEmbedder:
    """CLIP (open_clip) visual embedding model with offline checkpoint support and fallback."""

    def __init__(self, weights_dir: Optional[str] = None):
        self.is_semantic = False
        self.model = None
        self.tokenizer = None
        self.torch = None

        if weights_dir and os.path.exists(weights_dir):
            ckpts = sorted(glob.glob(os.path.join(weights_dir, "clip_*.pt")))
            if ckpts:
                try:
                    import torch
                    import open_clip

                    # Create architecture
                    model, _, _ = open_clip.create_model_and_transforms(
                        "ViT-B-32-quickgelu", pretrained=ckpts[0]
                    )
                    self.model = model.eval()
                    self.tokenizer = open_clip.get_tokenizer("ViT-B-32-quickgelu")
                    self.torch = torch
                    self.mean = np.array([0.48145466, 0.4578275, 0.40821073], dtype=np.float32)
                    self.std = np.array([0.26862954, 0.26130258, 0.27577711], dtype=np.float32)
                    self.is_semantic = True
                    print(f"[info] Successfully initialized CLIP model from checkpoint: {ckpts[0]}")
                except Exception as e:
                    print(f"[warn] Failed to load local CLIP weights ({e}). Falling back to visual histograms.")
                    self.is_semantic = False

    def encode_images(self, frames_bgr: List[np.ndarray], batch_size: int = 64) -> np.ndarray:
        """Encode list of BGR frames into normalized feature representations."""
        if len(frames_bgr) == 0:
            return np.empty((0, 512), dtype=np.float32)

        if self.is_semantic and self.model is not None:
            embeddings = []
            with self.torch.no_grad():
                for i in range(0, len(frames_bgr), batch_size):
                    batch_frames = frames_bgr[i: i + batch_size]
                    # Convert BGR to RGB and normalize
                    rgb = np.stack([cv2.cvtColor(f, cv2.COLOR_BGR2RGB) for f in batch_frames])
                    rgb = (rgb.astype(np.float32) / 255.0 - self.mean) / self.std
                    tensor = self.torch.from_numpy(rgb).permute(0, 3, 1, 2).contiguous()
                    feat = self.model.encode_image(tensor).float().cpu().numpy()
                    embeddings.append(feat)
            return _l2_normalize(np.concatenate(embeddings, axis=0))

        # Visual histogram + spatial layout fallback
        features = []
        for f in frames_bgr:
            hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
            hist = cv2.calcHist([hsv], [0, 1, 2], None, [8, 4, 4], [0, 180, 0, 256, 0, 256]).ravel()
            hist_norm = _l2_normalize(hist.astype(np.float32))

            gray = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
            spatial_grid = cv2.resize(gray, (8, 8), interpolation=cv2.INTER_AREA).astype(np.float32).ravel()
            spatial_grid -= spatial_grid.mean()
            grid_norm = _l2_normalize(spatial_grid)

            features.append(np.concatenate([hist_norm, grid_norm]))
        return _l2_normalize(np.asarray(features, dtype=np.float32))

    def encode_text(self, text_list: List[str]) -> Optional[np.ndarray]:
        """Encode text prompts using CLIP text encoder."""
        if not self.is_semantic or self.model is None or not text_list:
            return None
        with self.torch.no_grad():
            tokens = self.tokenizer(text_list)
            text_features = self.model.encode_text(tokens).float().cpu().numpy()
        return _l2_normalize(text_features)


class ActionClassifier:
    """Zero-shot verb, noun, and video-level category classifier using egocentric prompt ensembles."""

    def __init__(self, embedder: VisualEmbedder, verbs: List[str], nouns: List[str], categories: List[str]):
        self.embedder = embedder
        self.verbs = verbs
        self.nouns = nouns
        self.categories = categories

        # Precompute text embeddings with prompt ensembles tailored for egocentric video
        if embedder.is_semantic:
            self.verb_embeddings = embedder.encode_text([
                f"a first-person view of hands about to {v.replace('-', ' ')} something"
                for v in verbs
            ]) if verbs else None

            self.noun_embeddings = embedder.encode_text([
                f"a first-person photo of {_format_noun_phrase(n)}"
                for n in nouns
            ]) if nouns else None

            self.category_embeddings = embedder.encode_text([
                f"a first-person video of {c.replace('_', ' ')}"
                for c in categories
            ]) if categories else None
        else:
            self.verb_embeddings = None
            self.noun_embeddings = None
            self.category_embeddings = None

    def predict_action(self, segment_embedding: np.ndarray) -> Tuple[str, str, float, List[Dict[str, Any]]]:
        """Predict top verb, noun, joint confidence, and alternative candidates for a segment."""
        verb, noun, confidence = "unknown", "unknown", 0.0
        p_verb_max = p_noun_max = 0.0
        top_candidates = []

        if self.verb_embeddings is not None and len(self.verbs) > 0:
            sims_v = 100.0 * (self.verb_embeddings @ segment_embedding)
            probs_v = _softmax(sims_v)
            best_v_idx = int(np.argmax(probs_v))
            verb = self.verbs[best_v_idx]
            p_verb_max = float(probs_v[best_v_idx])

        if self.noun_embeddings is not None and len(self.nouns) > 0:
            sims_n = 100.0 * (self.noun_embeddings @ segment_embedding)
            probs_n = _softmax(sims_n)
            best_n_idx = int(np.argmax(probs_n))
            noun = self.nouns[best_n_idx]
            p_noun_max = float(probs_n[best_n_idx])

        if p_verb_max > 0 and p_noun_max > 0:
            confidence = float(np.sqrt(p_verb_max * p_noun_max))
        elif p_verb_max > 0:
            confidence = float(p_verb_max)

        return verb, noun, confidence, top_candidates

    def predict_video_category(self, video_embedding: np.ndarray) -> str:
        """Predict video-level category for FPVSum evaluation (10% score)."""
        if self.category_embeddings is None or not self.categories:
            return "unknown"
        sims = self.category_embeddings @ video_embedding
        best_idx = int(np.argmax(sims))
        return self.categories[best_idx]

