#!/usr/bin/env python
"""Official Samsung XR Hackathon Track 4 Submission Validator.
Conforming strictly to the Student Package specification and scoring constraints.

Usage:
    python validate.py --dir outputs/
    python validate.py --file outputs/P02_109.json -v
    python validate.py --dir outputs/ --manifest datasets/manifest.csv

Checks:
    1. Presence of all 6 required top-level fields:
       team_id, video_id, duration_sec, label, actions, highlights.
    2. Data types and bounds:
       - team_id: non-empty string.
       - video_id: non-empty string matching filename basename.
       - duration_sec: positive number (> 0), within +-0.5s of manifest if provided.
       - label: object {"name": str, "score": float in [0, 1]}.
       - actions: list of {"segment": [start, end], "verb": str, "noun": str, "score": float in [0, 1]}.
       - highlights: list of {"segment": [start, end]}.
    3. Chronological sorting and non-overlapping highlight segments.
    4. Duration budget constraint: total highlight <= 0.15 * duration_sec.
    5. Highlight segment validity: at least one segment >= 4.0s (warns if any < 4.0s).
"""
import argparse
import csv
import glob
import json
import os
import sys

REQUIRED_KEYS = ["team_id", "video_id", "duration_sec", "label", "actions", "highlights"]
BUDGET_CAP = 0.15


def load_manifest(manifest_path: str) -> dict:
    """Loads manifest.csv into {video_id: duration_sec} mapping."""
    if not manifest_path or not os.path.exists(manifest_path):
        return {}
    durations = {}
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                vid = row.get("video_id")
                dur = row.get("duration_sec")
                if vid and dur:
                    try:
                        durations[vid] = float(dur)
                    except ValueError:
                        pass
    except Exception as e:
        print(f"[WARN] Could not parse manifest: {e}", file=sys.stderr)
    return durations


def validate_json_file(file_path: str, expected_id: str, manifest: dict = None, verbose: bool = False) -> tuple[list[str], list[str]]:
    """Inspects a single output JSON file.
    Returns:
        (errors, warnings) lists.
    """
    errors = []
    warnings = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return [f"Malformed JSON: {e}"], []

    if not isinstance(data, dict):
        return ["Root JSON element must be an object (dictionary)"], []

    # 1. Required keys presence
    for k in REQUIRED_KEYS:
        if k not in data:
            errors.append(f"Missing required key '{k}'")
    if errors:
        return errors, warnings

    # 2. team_id
    team_id = data.get("team_id")
    if not isinstance(team_id, str) or not team_id.strip():
        errors.append("Field 'team_id' must be a non-empty string")

    # 3. video_id matches file basename
    video_id = data.get("video_id")
    if not isinstance(video_id, str) or not video_id.strip():
        errors.append("Field 'video_id' must be a non-empty string")
    elif expected_id and str(video_id) != expected_id:
        errors.append(f"video_id '{video_id}' != expected filename basename '{expected_id}'")

    # 4. duration_sec
    duration_sec = data.get("duration_sec")
    if not isinstance(duration_sec, (int, float)) or duration_sec <= 0:
        errors.append(f"Invalid duration_sec: {duration_sec} (must be a positive number)")
        return errors, warnings

    if manifest and video_id in manifest:
        expected_dur = manifest[video_id]
        if abs(duration_sec - expected_dur) > 0.5:
            warnings.append(
                f"duration_sec {duration_sec} differs from official manifest ({expected_dur}s) by > 0.5s"
            )

    # 5. label: {"name": str, "score": float in [0, 1]}
    label = data.get("label")
    if not isinstance(label, dict):
        errors.append("Field 'label' must be an object {'name': string, 'score': number}")
    else:
        lname = label.get("name")
        lscore = label.get("score")
        if not isinstance(lname, str) or not lname.strip():
            errors.append("Field 'label.name' must be a non-empty string")
        if not isinstance(lscore, (int, float)) or not (0.0 <= lscore <= 1.0):
            errors.append(f"Field 'label.score' must be a number in [0.0, 1.0], got {lscore}")

    # 6. actions: list of {"segment": [start, end], "verb": str, "noun": str, "score": float}
    actions = data.get("actions")
    if not isinstance(actions, list):
        errors.append("Field 'actions' must be a list")
    else:
        for idx, act in enumerate(actions):
            if not isinstance(act, dict):
                errors.append(f"actions[{idx}] must be an object")
                continue
            seg = act.get("segment")
            if not isinstance(seg, (list, tuple)) or len(seg) != 2:
                errors.append(f"actions[{idx}] missing valid 'segment': [start, end] list")
            else:
                s_start, s_end = seg[0], seg[1]
                if not (isinstance(s_start, (int, float)) and isinstance(s_end, (int, float))):
                    errors.append(f"actions[{idx}] segment boundaries must be numeric")
                elif not (0.0 <= s_start < s_end <= duration_sec + 0.5):
                    errors.append(f"actions[{idx}] invalid interval [{s_start}, {s_end}] for duration {duration_sec}")

            verb = act.get("verb")
            noun = act.get("noun")
            score = act.get("score")
            if not (isinstance(verb, str) and isinstance(noun, str)):
                errors.append(f"actions[{idx}] 'verb' and 'noun' must be strings")
            if score is not None and (not isinstance(score, (int, float)) or not (0.0 <= score <= 1.0)):
                errors.append(f"actions[{idx}] 'score' must be a number in [0.0, 1.0], got {score}")

    # 7. highlights: list of {"segment": [start, end]}
    highlights = data.get("highlights")
    if not isinstance(highlights, list):
        errors.append("Field 'highlights' must be a list")
    elif len(highlights) == 0:
        errors.append("Field 'highlights' must contain at least 1 segment")
    else:
        prev_end = -1.0
        total_highlight_sec = 0.0
        has_segment_ge_4 = False

        for idx, h in enumerate(highlights):
            if not isinstance(h, dict):
                errors.append(f"highlights[{idx}] must be an object")
                continue
            seg = h.get("segment")
            if not isinstance(seg, (list, tuple)) or len(seg) != 2:
                errors.append(f"highlights[{idx}] missing valid 'segment': [start, end] list")
                continue
            h_start, h_end = seg[0], seg[1]
            if not (isinstance(h_start, (int, float)) and isinstance(h_end, (int, float))):
                errors.append(f"highlights[{idx}] segment boundaries must be numeric")
                continue
            if not (0.0 <= h_start < h_end <= duration_sec + 0.5):
                errors.append(f"highlights[{idx}] invalid interval [{h_start}, {h_end}] for duration {duration_sec}")

            # Chronological sorting and non-overlap
            if h_start < prev_end - 1e-3:
                errors.append(
                    f"highlights[{idx}] overlaps previous segment or unsorted (start {h_start} < prev_end {prev_end})"
                )

            seg_len = h_end - h_start
            if seg_len >= 4.0:
                has_segment_ge_4 = True
            else:
                warnings.append(
                    f"highlights[{idx}] segment [{h_start}, {h_end}] duration is {seg_len:.2f}s (< 4.0s). "
                    f"Official evaluation will ignore segments shorter than 4.0s."
                )

            prev_end = h_end
            total_highlight_sec += seg_len

        # Duration budget enforcement (<= 15.0%)
        allowed_max = (BUDGET_CAP * duration_sec) + 0.05
        if total_highlight_sec > allowed_max:
            ratio_pct = (100.0 * total_highlight_sec / duration_sec)
            errors.append(
                f"Highlight duration ({total_highlight_sec:.2f}s = {ratio_pct:.1f}%) exceeds "
                f"15% budget cap ({allowed_max:.2f}s)"
            )

        if not has_segment_ge_4 and duration_sec >= 27.0:
            warnings.append(
                "No highlight segment is >= 4.0s in length. The official evaluator may ignore all segments."
            )

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Official Samsung XR Hackathon Track 4 Submission Validator")
    parser.add_argument("--dir", default=None, help="Directory containing <video_id>.json files")
    parser.add_argument("--file", default=None, help="Path to a single <video_id>.json file to validate")
    parser.add_argument("--manifest", default=None, help="Optional path to official manifest.csv")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print detailed warnings and progress")
    args = parser.parse_args()

    if not args.dir and not args.file:
        print("[ERROR] Specify either --dir <path> or --file <path>.", file=sys.stderr)
        sys.exit(1)

    manifest = load_manifest(args.manifest) if args.manifest else {}
    files_to_check = []

    if args.file:
        if not os.path.exists(args.file):
            print(f"[ERROR] File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        files_to_check.append(args.file)
    else:
        files_to_check = sorted(glob.glob(os.path.join(args.dir, "*.json")))
        if not files_to_check:
            print(f"[ERROR] No JSON files found in {args.dir}", file=sys.stderr)
            sys.exit(1)

    print("==================================================")
    print(" SAMSUNG XR HACKATHON 2026 — TRACK 4 VALIDATOR")
    print(f" Checking {len(files_to_check)} file(s)")
    if args.manifest:
        print(f" Loaded manifest with {len(manifest)} video duration(s)")
    print("==================================================\n")

    passed = 0
    failed = 0

    for fpath in files_to_check:
        bname = os.path.splitext(os.path.basename(fpath))[0]
        errs, warns = validate_json_file(fpath, expected_id=bname, manifest=manifest, verbose=args.verbose)
        if not errs:
            passed += 1
            print(f"✅ PASS: {os.path.basename(fpath)}")
            if args.verbose and warns:
                for w in warns:
                    print(f"   ⚠️  [WARN] {w}")
        else:
            failed += 1
            print(f"❌ FAIL: {os.path.basename(fpath)}")
            for e in errs:
                print(f"   🚫 {e}")
            if args.verbose and warns:
                for w in warns:
                    print(f"   ⚠️  [WARN] {w}")

    print("\n--------------------------------------------------")
    print(f" SUMMARY: {passed}/{len(files_to_check)} passed validation ({failed} failed).")
    if failed == 0:
        print(" [SUCCESS] All validated files strictly satisfy Samsung Track 4 requirements!")
        print("--------------------------------------------------\n")
        sys.exit(0)
    else:
        print(" [FAILURE] Validation errors detected. Fix before submitting.")
        print("--------------------------------------------------\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
