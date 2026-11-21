# Samsung PRISM Hackathon 2026
## [ Track 04 ] Action-Aware Video Summarization
**XR Perception Group**

---

## 1. Objective

Build a system that understands actions and object interactions in typically 2–10 minute first-person videos, selects important temporal segments, and compiles a concise highlight from the original footage.

- **Input:** first-person MP4 (2–10 min); output ≈ 15% highlight compiled from original footage only.
- **Output:** one `<video_id>.json` per video; run via `run.sh <video.mp4> <out.json>`
- **Datasets:** EPIC-KITCHENS-100 (138 validation videos) & FPVSum (49 videos).
- **XR relevance:** first-person frames become thousands of visual tokens — pruning them optimises downstream XR use cases.

| Capability | Description |
|---|---|
| **Action Awareness** | Understand meaningful activities and hand–object interactions, not just visual scene changes. |
| **Importance & Redundancy** | Retain distinctive events and drop idle, repetitive, or irrelevant footage. |

---

## 2. Student Package Contents

```text
student_package/
├── manifest.csv             # 187 target videos (video_id, duration_sec, dataset)
├── supported_classes.json   # 16 labels, 98 verbs, 301 nouns
├── TEAM_README.md           # This guide
├── P02_109.json            # Sample output for an EPIC-KITCHENS-100 video
└── skiing_03.json          # Sample output for an FPVSum video
```

| File | Description |
|---|---|
| `manifest.csv` | 187 rows (`video_id, duration_sec, dataset`): **138** `epic_kitchens_100` + **49** `fpvsum`. Produce one JSON for every row. |
| `supported_classes.json` | Official class dictionary: **16 video labels** (`bike, bikepolo, boxing, cooking, horse, jumping, longboarding, motor, parkour, plane, rockclimbing, scuba, skate, ski, surfing, other`), **98 verb keys**, and **301 noun keys**. All class names must match exactly — capitalisation and spelling are significant (e.g. `"ski"` not `"skiing"`). |

---

## 3. Dataset Sourcing

Download the source videos using the video IDs in `manifest.csv` and submit one JSON file for each in the specified format. Raw video files are **not distributed** by the organisers.

### A. EPIC-KITCHENS-100 Validation Split (N = 138 Videos)

- **Official Dataset Page:** https://epic-kitchens.github.io/2020
- **Official Downloader Repository:** https://github.com/epic-kitchens/epic-kitchens-download-scripts

```bash
git clone https://github.com/epic-kitchens/epic-kitchens-download-scripts.git
cd epic-kitchens-download-scripts
python epic_downloader.py --videos \
      --specific-videos "<comma_separated_138_ids_from_manifest>" \
      --output-path ../EPIC-KITCHENS
```

Total size is approximately 184 GB. Downloads support resumption and MD5 verification. Start early.

### B. FPVSum Annotated Videos (M = 49 Videos)

- **Official Repository:** https://github.com/azuxmioy/fpvsum (or https://github.com/v-iashin/FPVSum)
- **Note:** Use `yt-dlp` in place of the retired `youtube-dl` utility in the crawler.

```bash
pip install yt-dlp
# then use the crawler from https://github.com/azuxmioy/fpvsum
```

Video IDs follow the format `<Category>_<YouTubeID>` (for example `Ski_-Z5a4UQmZLs`). The manifest lists only the 49 videos with active YouTube URLs and ground truth.

---

## 4. Output JSON Format & Field Reference

`<video_id>.json` — same schema for every dataset. Refer to the attached sample JSON files.

### Example

```json
{
  "team_id": "team_alpha",
  "video_id": "P02_109",
  "duration_sec": 512.3,
  "label": {
    "name": "cooking",
    "score": 0.96
  },
  "actions": [
    {
      "segment": [12.4, 18.2],
      "verb": "open",
      "noun": "fridge",
      "score": 0.88
    }
  ],
  "highlights": [
    {"segment": [11.0, 19.5]},
    {"segment": [45.2, 53.0]}
  ]
}
```

### Field Reference

| Field | Type | Constraints & Format Rules | Scored On |
|---|---|---|---|
| `team_id` | string | Non-empty string; must be identical across all submitted files. | — |
| `video_id` | string | Non-empty string; must match the filename (`<video_id>.json`) and `manifest.csv`. | — |
| `duration_sec` | number | Positive number (> 0); must be within ±0.5 s of the official `manifest.csv` duration. | Budget check |
| `label` | object | `{"name": string, "score": number}` with `score` in [0, 1]. Use `"cooking"` for EPIC videos, or one of the 14 FPVSum categories (or `"other"`) for FPVSum videos. | Label Accuracy (10%) |
| `actions` | array | 0–2000 items of `{"segment": [start, end], "verb": string, "noun": string, "score": number}`. `0 <= start < end <= duration_sec + 0.5`; `score` in [0, 1]. May be `[]` for FPVSum videos. | Action mAP (25%) |
| `highlights` | array | At least 1 item of `{"segment": [start, end]}`. Must be chronologically sorted, strictly non-overlapping, with at least one segment ≥ 4.0 s. Target total length ≤ 15% of `duration_sec`. | Action Coverage (40%) & Highlight F1 (25%) |

> **Note:** Timestamps should be in seconds (up to 2 decimal places).

**Additional notes:**
- Label names must be copied exactly from `supported_classes.json` (e.g. `"ski"`, not `"skiing"`).
- Verb and noun names must come from `supported_classes.json`. Use `"other"` when no matching kitchen class applies — this is common for FPVSum videos.
- The `actions` list may be `[]` for FPVSum videos.

---

## 5. Validating Your Outputs

Before submitting, manually verify that every `<video_id>.json` file satisfies the following:

- All six required fields are present: `team_id`, `video_id`, `duration_sec`, `label`, `actions`, `highlights`.
- `team_id` is a non-empty string, identical across all files.
- `video_id` matches the file name and an ID in `manifest.csv`.
- `duration_sec` is a positive number within ±0.5 s of the manifest value.
- `label.score` and all `actions[].score` values are in [0, 1].
- Action segments satisfy `0 ≤ start < end ≤ duration_sec + 0.5`.
- Highlights are chronologically sorted, strictly non-overlapping, each with `start < end` inside the video.
- At least one highlight is ≥ 4.0 s.
- Total highlight length is targeted at ≤ 15% of `duration_sec`.
- There are 187 output files in total, one for every row in `manifest.csv`.

**A missing or invalid file scores 0 on all metrics for that video.**

---

## 6. Evaluation Metrics (100 pts)

| Metric | Weight | Definition |
|---|---|---|
| **Action mAP** | **25%** | Verb–noun overlap with ground truth at tIoU 0.1–0.5. |
| **Action coverage** | **40%** | Distinct GT action pairs captured (soft penalty if highlights exceed the 15% budget). |
| **Highlight F1** | **25%** | Frame-level F1 vs top-15% human-annotated consensus importance frames. |
| **Label accuracy** | **10%** | Video-level category prediction on FPVSum videos. |

**How Action Coverage works:** an action is captured if at least 50% of its duration falls inside your highlights. Labels are not checked here — only timing matters. Exceeding the 15% total highlight length applies a soft penalty to coverage.

---

## 7. Submission Package

```text
TEAM_ID/
├── run.sh             # Single-video inference: ./run.sh <video.mp4> <out.json>
├── code/              # Complete inference source code
├── weights/           # Model weights / checkpoints
├── requirements.txt   # Exact Python dependencies
├── outputs/           # 187 validated <video_id>.json files (one per video in manifest)
└── README.md          # Environment setup, model architecture, and reproduction steps
```

---

## 8. Integrity & Verification Rules

- **Hidden Scored Subset:** Only a subset of the manifest videos is scored. The selection is committed to by a hash published at launch and revealed with the results.
- **Originality & Reproducibility:** Outputs must be generated by your submitted system and must be reproducible when organisers re-run `./run.sh <video.mp4> <out.json>` on sample videos in an isolated environment.
- **Zero Tolerance for Hardcoding:** Automated code scans and spot re-runs are conducted prior to final ranking. Copied ground truth, hardcoded video IDs, or non-reproducible outputs lead to immediate disqualification.

---

## 9. Common Questions

**Q: Do my action verb/noun labels need to match ground truth for Action Coverage?**  
No. Coverage checks only that the highlight timing captures the action. Labels matter only for Action mAP.

**Q: Can I submit an empty actions list for FPVSum videos?**  
Yes. `"actions": []` is valid for any video.

**Q: Which label should I use for EPIC-KITCHENS videos?**  
Use `"cooking"`. All EPIC-KITCHENS videos are kitchen recordings.

**Q: How do I find the correct label name for an FPVSum video?**  
Use the exact string from `supported_classes.json`. For example, skiing videos use `"ski"`, not `"skiing"`.

**Q: What happens if my highlights exceed 15% of the video?**  
The file is still valid, but your Action Coverage score is reduced by a soft penalty. Aim to stay within 15%.

**Q: What is the minimum highlight length?**  
At least one segment must be ≥ 4 s. If no highlight meets this requirement the file is invalid.