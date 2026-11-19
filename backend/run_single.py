#!/usr/bin/env python
"""CLI Single Video Runner: <video.mp4> -> <video_id>.json.
Fulfills the official Track 4 execution contract."""
import argparse
import os
import sys

# Ensure backend package is in pythonpath
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.pipeline.pipeline_orchestrator import MomentiqPipeline


def main():
    parser = argparse.ArgumentParser(description="MOMENTIQ Track 4 Action-Aware Video Summarizer")
    parser.add_argument("--video", required=True, help="Path to input first-person MP4 video")
    parser.add_argument("--out", required=True, help="Path to output JSON")
    parser.add_argument("--render-highlight", default=None, help="Optional path to render highlight MP4")
    parser.add_argument("--weights", default=None, help="Directory containing model weights")
    parser.add_argument("--classes", default=None, help="Path to supported_classes.json")
    parser.add_argument("--budget", type=float, default=0.15, help="Highlight duration budget ratio (default 0.15)")
    args = parser.parse_args()

    # Determine default weights directory
    weights_dir = args.weights
    if not weights_dir:
        candidate_weights = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "weights"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "weights"),
            os.path.abspath("backend/weights"),
            os.path.abspath("weights"),
        ]
        for w in candidate_weights:
            if os.path.exists(w):
                weights_dir = w
                break

    pipeline = MomentiqPipeline(weights_dir=weights_dir, classes_path=args.classes)
    res = pipeline.run(
        video_path=args.video,
        output_json_path=args.out,
        output_highlight_video_path=args.render_highlight,
        target_budget=args.budget
    )
    print(f"Output successfully written to: {args.out}")


if __name__ == "__main__":
    main()

