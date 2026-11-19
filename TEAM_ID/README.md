# SAMSUNG XR HACKATHON 2026 — TRACK 4 SUBMISSION
## Track: Action Aware Video Summarization
### Team Project: MOMENTIQ — Intelligent First-Person Video Understanding & Highlight Generation

> **Team Name:** `VITChennai_RRR`  
> **Institution:** Vellore Institute of Technology, Chennai (VIT Chennai)  
> **Team Members:**  
> - **Rishita R** (`24bai1632`)  
> - **Ryan Jain** (`24brs1395`)  
> - **Rhythm Rastogi** (`24bai1508`)  
> **GitHub Repository:** [https://github.com/rishita2201/Samsung_XR_Hackathon.git](https://github.com/rishita2201/Samsung_XR_Hackathon.git)

---

### 1. Overview
This submission package implements the complete, offline, action-aware video summarization pipeline for egocentric (first-person) video datasets including **EPIC-KITCHENS-100** and **FPVSum**.

The system identifies meaningful human actions, detects hand-object interactions (HOI), localizes temporal action boundaries, ranks segments via explainable multi-factor scoring, and produces a concise summary adhering strictly to the **$\le 15.0\%$ duration budget constraint** and the **$\ge 4.0\text{ s}$ minimum highlight segment constraint**.

---

### 2. Submission Directory Structure
```text
VITChennai_RRR/
├── run.sh                  # Official Linux execution script
├── run.bat                 # Official Windows execution script
├── requirements.txt        # Runtime dependencies
├── validate.py             # Official Track 4 schema and budget validator
├── README.md               # Reproduction and architecture documentation
├── code/                   # Self-contained pipeline source code
│   ├── run_pipeline.py     # Main CLI entrypoint
│   ├── features.py         # Farneback optical flow & HOI spatial filtering
│   ├── labeler.py          # Zero-shot CLIP ViT-B/32 action recognition
│   ├── summarizer.py       # Temporal localization & MMR highlight selection
│   ├── batch_run.py        # Directory-level batch processor
│   └── generate_manifest_predictions.py # Manifest prediction generator
├── weights/                # Offline model weights and vocabularies
│   ├── clip_vitb32.pt      # Pretrained CLIP ViT-B/32 QuickGELU (577 MB)
│   └── supported_classes.json # EPIC-KITCHENS & FPVSum verbs/nouns/categories
└── outputs/                # 187 manifest JSONs + synthetic demo (188 files total)
    ├── BikePolo_5yf797Lh4Oc_1.json
    ├── P01_11.json
    ├── Ski_-Z5a4UQmZLs.json
    └── ... (188 validated JSON files)
```

---

### 3. Requirements & Installation
The pipeline requires Python 3.9+ and standard computer vision/deep learning libraries. All model checkpoints are bundled **locally in `weights/`** — **no internet access is required during evaluation**.

```bash
pip install -r requirements.txt
```

#### Core dependencies:
- `torch >= 2.0.0`
- `torchvision >= 0.15.0`
- `open_clip_torch >= 2.20.0`
- `opencv-python-headless >= 4.7.0`
- `scipy >= 1.10.0`
- `numpy >= 1.24.0`

---

### 4. Running the Pipeline

#### Single Video Execution (Linux / macOS):
```bash
bash run.sh <path_to_video.mp4> <path_to_output.json>
```
*Example:*
```bash
bash run.sh ../uploads/synthetic_demo.mp4 outputs/synthetic_demo.json
```

#### Single Video Execution (Windows):
```cmd
run.bat <path_to_video.mp4> <path_to_output.json>
```
*Example:*
```cmd
run.bat ..\uploads\synthetic_demo.mp4 outputs\synthetic_demo.json
```

#### Batch Execution across a Directory:
```bash
python code/batch_run.py --input_dir /path/to/videos --output_dir outputs/ --weights weights/
```

---

### 5. Verification & Output Validation
An automated validation script is provided to verify that every output file strictly adheres to the official Samsung Track 4 Student Package contract:
- Validates all 6 required schema keys (`team_id`, `video_id`, `duration_sec`, `label`, `actions`, `highlights`).
- Validates timestamp ordering and non-overlapping highlight segments.
- Enforces the highlight duration constraint: $\text{highlight\_duration} \le 0.15 \times \text{duration\_sec}$.
- Verifies highlight segments are $\ge 4.0\text{ s}$ (official requirement for scored highlights).

```bash
python validate.py --dir outputs/ --manifest ../datasets/manifest.csv
```

**Validation outcome:**
```
==================================================
 SAMSUNG XR HACKATHON 2026 — TRACK 4 VALIDATOR
 Checking 188 file(s)
 Loaded manifest with 187 video duration(s)
==================================================

✅ PASS: BikePolo_5yf797Lh4Oc_1.json
✅ PASS: Bike_OeE9EIIKmrA.json
...
✅ PASS: P01_11.json
✅ PASS: P02_109.json
...
✅ PASS: Ski_-Z5a4UQmZLs.json
✅ PASS: synthetic_demo.json

--------------------------------------------------
 SUMMARY: 188/188 passed validation (0 failed).
 [SUCCESS] All validated files strictly satisfy Samsung Track 4 requirements!
--------------------------------------------------
```

---

### 6. Technical Methodology Summary
1. **Adaptive Sampling & Flow Decomposition**: Farneback dense optical flow separates egocentric camera sway (median background translation) from intentional hand/tool residual motion.
2. **Egocentric Hand-Object Interaction (HOI)**: Combines YCbCr skin chrominance segmentation in manipulation zones with foveal Canny edge density to identify physical manipulation without expensive bounding box anchors.
3. **Zero-Shot Action Recognition**: Uses CLIP ViT-B/32 prompt ensembles over EPIC-KITCHENS-100 verb and noun taxonomies, paired with visual flow histograms.
4. **Temporal Action Localization**: Segment boundaries are localized via embedding distance change-point detection and refined with temporal Intersection over Union (tIoU) merging.
5. **Diversity-Constrained MMR Selection**: Segments are selected using Maximal Marginal Relevance (MMR) with a distinct action bonus (+0.40) to explicitly maximize the **Action Coverage metric (40% weight)** while hard-capping total highlight duration at $\le 15.0\%$ and enforcing $\ge 4.0\text{ s}$ segments.
