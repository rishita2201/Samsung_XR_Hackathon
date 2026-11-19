#!/usr/bin/env python
"""Evaluation CLI script: computes official 100-point metrics across dataset manifests.
Supports both Student Package schema and legacy JSONs.
"""
import argparse
import glob
import json
import os
import sys
import numpy as np

from metrics import (
    compute_action_map, compute_action_coverage,
    compute_highlight_f1, compute_label_accuracy,
    calculate_100_point_score, _extract_label
)


def evaluate_directories(pred_dir: str, gt_dir: str):
    """Compares predicted JSON outputs against ground truth JSON annotations."""
    pred_files = sorted(glob.glob(os.path.join(pred_dir, "*.json")))
    if not pred_files:
        print(f"[ERROR] No predicted JSON files found in: {pred_dir}")
        sys.exit(1)

    print(f"\n==================================================")
    print(f" SAMSUNG XR HACKATHON 2026 — JURY EVALUATION")
    print(f" Predictions Dir: {pred_dir}")
    print(f" Ground Truth Dir: {gt_dir}")
    print(f" Found {len(pred_files)} prediction file(s)")
    print(f"==================================================\n")

    maps = []
    coverages = []
    f1s = []
    label_accs = []

    for pf in pred_files:
        vid_id = os.path.splitext(os.path.basename(pf))[0]
        gt_file = os.path.join(gt_dir, f"{vid_id}.json")
        if not os.path.exists(gt_file):
            print(f"[WARN] No ground truth file for {vid_id}, skipping.")
            continue

        with open(pf, "r", encoding="utf-8") as f:
            pred = json.load(f)
        with open(gt_file, "r", encoding="utf-8") as f:
            gt = json.load(f)

        dur = gt.get("duration_sec", gt.get("duration", pred.get("duration_sec", pred.get("duration", 60.0))))
        m_ap = compute_action_map(pred.get("actions", []), gt.get("actions", []))
        cov = compute_action_coverage(pred.get("highlights", []), gt.get("actions", []), dur)
        f1 = compute_highlight_f1(pred.get("highlights", []), gt.get("highlights", []), dur)
        l_acc = compute_label_accuracy(pred.get("label", ""), gt.get("label", ""))

        maps.append(m_ap)
        coverages.append(cov)
        f1s.append(f1)
        label_accs.append(l_acc)

        print(f"[{vid_id}] Action mAP: {m_ap*100:.1f}% | Coverage: {cov*100:.1f}% | Highlight F1: {f1*100:.1f}% | Label: {int(l_acc*100)}%")

    if not maps:
        print("\n[NOTE] No matching ground-truth files found to evaluate against.")
        return

    mean_map = float(np.mean(maps))
    mean_cov = float(np.mean(coverages))
    mean_f1 = float(np.mean(f1s))
    mean_lacc = float(np.mean(label_accs))

    summary = calculate_100_point_score(mean_map, mean_cov, mean_f1, mean_lacc)

    print("\n--------------------------------------------------")
    print(" OFFICIAL 100-POINT JURY SCORE BREAKDOWN")
    print("--------------------------------------------------")
    print(f" 1. Action mAP (25% weight):         {summary['points_action_map']} / 25.00 pts  ({summary['action_map_pct']}%)")
    print(f" 2. Action Coverage (40% weight):    {summary['points_action_coverage']} / 40.00 pts  ({summary['action_coverage_pct']}%)")
    print(f" 3. Highlight F1 (25% weight):       {summary['points_highlight_f1']} / 25.00 pts  ({summary['highlight_f1_pct']}%)")
    print(f" 4. Label Accuracy (10% weight):     {summary['points_label_accuracy']} / 10.00 pts  ({summary['label_accuracy_pct']}%)")
    print("--------------------------------------------------")
    print(f" TOTAL SCORE:                         {summary['total_score_100']} / 100.00 pts")
    print("==================================================\n")


if __name__ == "__main__":
    default_pred = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "TEAM_ID", "outputs")
    default_gt = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ground_truth")

    parser = argparse.ArgumentParser(description="Evaluate predicted summarization JSONs against ground truth.")
    parser.add_argument("--pred_dir", default=default_pred, help="Path to prediction JSON directory")
    parser.add_argument("--gt_dir", default=default_gt, help="Path to ground truth JSON directory")
    args = parser.parse_args()
    evaluate_directories(args.pred_dir, args.gt_dir)
