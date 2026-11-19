#!/usr/bin/env python
"""Batch run runner for entire folders of validation videos."""
import argparse, glob, os, sys
from run_pipeline import process

ap = argparse.ArgumentParser()
ap.add_argument("--videos", required=True, help="Directory of MP4 videos")
ap.add_argument("--out", required=True, help="Output directory for JSONs")
ap.add_argument("--weights", default="weights")
ap.add_argument("--classes", default="weights/supported_classes.json")
ap.add_argument("--skip-existing", action="store_true", default=True)
a = ap.parse_args()

os.makedirs(a.out, exist_ok=True)
vids = sorted(glob.glob(os.path.join(a.videos, "*.mp4")))
print(f"Found {len(vids)} video(s) to process.")

for i, v in enumerate(vids):
    vid_id = os.path.splitext(os.path.basename(v))[0]
    out_json = os.path.join(a.out, f"{vid_id}.json")
    if a.skip_existing and os.path.exists(out_json):
        print(f"[{i+1}/{len(vids)}] Skipping {vid_id} (already exists)")
        continue
    print(f"[{i+1}/{len(vids)}] Processing {vid_id}...")
    try:
        import json
        res = process(v, a.weights, a.classes)
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)
    except Exception as e:
        print(f"ERROR processing {vid_id}: {e}", file=sys.stderr)

