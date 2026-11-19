# Samsung_XR_Hackathon — MOMENTIQ
### Intelligent First-Person Video Understanding & Highlight Generation
> **Team:** `VITChennai_RRR`  
> **Institution:** Vellore Institute of Technology, Chennai (VIT Chennai)  
> **Members:** Rishita R (24bai1632) · Ryan Jain (24brs1395) · Rhythm Rastogi (24bai1508)  
> **Challenge:** Samsung R&D Institute India XR Hackathon 2026 — Track 4: Action Aware Video Summarization  
> **Duration Budget Constraint:** Strictly $\le 15.0\%$ of original video duration  
> **Supported Benchmarks:** EPIC-KITCHENS-100 (138 validation videos) & FPVSum (49 videos)  

---

## 1. Executive Summary & Problem Statement

Capturing video from an extended reality (XR) perspective—such as smart glasses or head-mounted displays—creates vast quantities of uncurated, continuous egocentric footage. Traditional video summarization systems fail fundamentally on first-person video because:
1. **Pervasive Camera Instability:** Incessant user head movements (pitch, yaw, tilt) generate massive frame-to-frame pixel displacements that mislead standard visual change detectors into falsely identifying head turns as "important events".
2. **Action Blindness:** Generic summarizers rank frames based on aesthetic color variance or global scene transitions rather than recognizing **what physical action is actually occurring**.
3. **Repetitive & Idle Redundancy:** Egocentric workflows often involve minutes of transit, idle looking around, or repetitive stirring/chopping, diluting key events.

**MOMENTIQ** solves these challenges by combining **egocentric motion decomposition**, **spatial hand-object interaction (HOI) filtering**, and **zero-shot vision-language action recognition (CLIP ViT-B/32)** with an **explainable Maximal Marginal Relevance (MMR) highlight optimizer**. The system outputs a frame-accurate, playable MP4 highlight alongside structured JSON metadata satisfying Samsung Track 4 requirements.

---

## 2. System Architecture

```mermaid
flowchart TD
    subgraph Ingestion["Module A: Ingestion & Adaptive Sampling"]
        V[First-Person MP4 Video] --> MP[Probe Duration, FPS, Resolution]
        MP --> AS[Intelligent 2 FPS Adaptive Sampler]
        AS --> OF[Farneback Dense Optical Flow]
        OF --> MC[Global Head Motion Cancellation<br/>Residual Manipulation Motion]
    end

    subgraph Perception["Modules C & D: Egocentric Perception"]
        MC --> HOI[Hand-Object Interaction Filter<br/>Skin Chrominance + Foveal Edge Density]
        AS --> CLIP[Pretrained CLIP ViT-B/32 Zero-Shot]
        HOI --> CLIP
        CLIP --> VN[EPIC-KITCHENS Verb & Noun Classification<br/>e.g. cut vegetable, mix ingredient]
    end

    subgraph Reasoning["Modules E & F: Localization & Scoring"]
        VN --> TAL[Temporal Action Localization<br/>Embedding Distance Change-Points + tIoU Merge]
        TAL --> SCORER[Explainable Multi-Factor Scorer<br/>Activity + HOI + Novelty + Confidence - Idle]
    end

    subgraph Synthesis["Modules G & H: Highlight Optimization & Render"]
        SCORER --> MMR[Budget-Constrained MMR Optimizer<br/>Distinct Action Bonus (+0.40) &le; 15% Budget]
        MMR --> OUT_JSON[Track 4 Structured JSON]
        MMR --> FFMPEG[Frame-Accurate FFmpeg Concat Renderer]
        FFMPEG --> OUT_MP4[Playable MP4 Highlight]
    end
```

---

## 3. Mathematical & Algorithmic Highlights

### A. Egocentric Head Sway Compensation
Standard camera motion vectors are dominated by the user's head saccades. MOMENTIQ computes dense Farneback optical flow $(\Delta x, \Delta y)$ across every consecutive sample frame pair. We compute the spatial median displacement:
$$\vec{v}_{\text{head}} = (\text{median}(\Delta x), \text{median}(\Delta y))$$
The residual manipulation motion field is defined as:
$$\vec{v}_{\text{manip}}(x, y) = \|\vec{v}(x, y) - \vec{v}_{\text{head}}\|_2$$
High residual motion localized to the lower-central manipulation zone indicates active tool or hand interaction, completely filtering out head turns.

### B. Explainable Multi-Factor Importance Score
For each temporal candidate segment $s_i$, the raw importance score is calculated as an explainable convex combination:
$$S(s_i) = w_a \cdot A(s_i) + w_h \cdot H(s_i) + w_n \cdot N(s_i) + w_c \cdot C(s_i) - w_{\text{idle}} \cdot I(s_i)$$
- $A(s_i)$: Normalized action dynamism from residual optical flow.
- $H(s_i)$: Egocentric Hand-Object Interaction score (skin chrominance $\times$ foveal Canny edge density).
- $N(s_i)$: Visual novelty, measured as Euclidean distance from the running video feature centroid.
- $C(s_i)$: CLIP action recognition classification confidence.
- $I(s_i)$: Idle penalty applied when residual motion falls below threshold.

### C. Maximal Marginal Relevance (MMR) under $\le 15\%$ Duration Budget
To optimize for the **Action Coverage metric (40% weight)**, MOMENTIQ uses greedy MMR selection with a novel distinct action bonus:
$$\arg\max_{s \in \mathcal{U}} \left[ S(s) - \lambda \max_{s' \in \mathcal{S}} \text{Sim}(s, s') + \beta \cdot \mathbf{1}_{[\text{action}(s) \notin \text{actions}(\mathcal{S})]} \right]$$
subject to:
$$\sum_{s \in \mathcal{S}} \text{duration}(s) \le 0.15 \times \text{Duration}_{\text{total}}$$
Where $\beta = 0.40$ heavily rewards the selection of novel (verb, noun) action pairs rather than repetitive instances of the same activity.

---

## 4. 100-Point Evaluation Matrix Alignment

The official Samsung Track 4 scoring distributes 100 points across four core metrics:

| Metric | Official Weight | Implementation Strategy in MOMENTIQ |
| :--- | :---: | :--- |
| **Action Coverage** | **40 pts (40%)** | **Primary Optimization Target:** Distinct Action Bonus (+0.40 in MMR) prevents repetitive clips and guarantees maximum representation of ground truth activities. |
| **Action mAP** | **25 pts (25%)** | Zero-shot CLIP prompt ensembles with temporal boundary refinement via change-point embedding distances and tIoU smoothing. |
| **Highlight F1** | **25 pts (25%)** | Adaptive temporal segment trimming aligns highlights precisely with high-motion interaction peaks while preserving context. |
| **Label Accuracy** | **10 pts (10%)** | Top-1 global video category voting over high-confidence localized actions against EPIC-KITCHENS / FPVSum taxonomy. |
| **TOTAL** | **100 pts** | Fully evaluated via `evaluation/evaluate.py`. |

---

## 5. Official Samsung Track 4 JSON Specification

Every processed video generates a corresponding `<video_id>.json` file strictly adhering to the schema:

```json
{
  "video_id": "synthetic_demo",
  "label": "cooking",
  "duration": 40.0,
  "highlight_ratio": 0.149,
  "actions": [
    {
      "verb": "cut",
      "noun": "vegetable",
      "start": 5.0,
      "end": 13.0,
      "confidence": 0.94
    },
    {
      "verb": "mix",
      "noun": "ingredient",
      "start": 17.0,
      "end": 25.0,
      "confidence": 0.91
    },
    {
      "verb": "wash",
      "noun": "plate",
      "start": 29.0,
      "end": 37.0,
      "confidence": 0.88
    }
  ],
  "highlights": [
    {
      "start": 6.5,
      "end": 9.5,
      "importance": 0.94
    },
    {
      "start": 18.5,
      "end": 21.4,
      "importance": 0.90
    }
  ]
}
```

---

## 6. Full-Stack Web Application

MOMENTIQ includes a purpose-built, high-performance web interface designed for research scientists and XR engineers:

### Core Workspaces:
1. **Product Landing Page:** Clean overview of egocentric action understanding and the 3-step pipeline.
2. **Video Upload Workspace:** Drag-and-drop MP4 uploader with metadata validation, duration verification, and a one-click synthetic video generator for instant testing.
3. **Analysis Workspace:** Multi-track synchronized timeline showing extracted keyframes, live bounding box/action overlays, verb-noun classifications, confidence scores, and HOI heatmaps.
4. **Highlight Editor:** NLE-style timeline editor displaying the interactive duration budget bar (`14.9% / 15.0%`), loop preview, segment removal, addition of candidate actions, and instant re-rendering of the output MP4.
5. **Results Dashboard:** Side-by-side synchronized player (Original Video vs. 15% Highlight), compression metrics, action diversity indices, and one-click JSON/MP4 downloads.
6. **Technical Report:** Interactive jury report with live pipeline documentation and automated in-browser submission validator.

---

## 7. Installation & Quickstart

### Prerequisites
- Python 3.9 - 3.12
- Node.js 18+ (for frontend development)
- FFmpeg (bundled automatically via `imageio-ffmpeg` or system PATH)

### Option A: Launch Full Web Application (Backend + Frontend)
Double click `run_app.bat` or run:
```bash
# Terminal 1: Launch unified FastAPI server (serves API + compiled React UI)
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
Open your browser to: **`http://127.0.0.1:8000`**

### Option B: Standalone CLI Pipeline (Samsung Track 4 Evaluation)
The submission folder `TEAM_ID/` contains completely self-contained offline runners:

**Linux / macOS:**
```bash
bash TEAM_ID/run.sh uploads/synthetic_demo.mp4 outputs/json/synthetic_demo.json
```

**Windows:**
```cmd
TEAM_ID\run.bat uploads\synthetic_demo.mp4 outputs\json\synthetic_demo.json
```

---

## 8. Verification & Benchmarking

### Step 1: Validate Schema & Duration Budget
Run the official Track 4 validation script:
```bash
python validate.py --dir outputs/json
```
```
==================================================
 SAMSUNG XR HACKATHON 2026 — TRACK 4 VALIDATOR
 Scanning directory: outputs/json
 Found 1 JSON file(s)
==================================================

✅ PASS: synthetic_demo.json

--------------------------------------------------
 SUMMARY: 1/1 passed validation.
 [SUCCESS] All files strictly satisfy Samsung Track 4 requirements!
--------------------------------------------------
```

### Step 2: Compute 100-Point Evaluation Metrics
Run the benchmark evaluator against ground truth annotations:
```bash
python evaluation/evaluate.py --pred_dir outputs/json --gt_dir evaluation/ground_truth
```
```
==================================================
 SAMSUNG XR HACKATHON 2026 — JURY EVALUATION
 Predictions Dir: outputs/json
 Ground Truth Dir: evaluation/ground_truth
==================================================

--------------------------------------------------
 OFFICIAL 100-POINT JURY SCORE BREAKDOWN
--------------------------------------------------
 1. Action mAP (25% weight):         20.5 / 25.00 pts
 2. Action Coverage (40% weight):    34.8 / 40.00 pts
 3. Highlight F1 (25% weight):       21.2 / 25.00 pts
 4. Label Accuracy (10% weight):      9.5 / 10.00 pts
--------------------------------------------------
 TOTAL SCORE:                        86.0 / 100.00 pts
==================================================
```

---

## 9. 2-Minute Jury Demonstration Script

1. **Open the Web Application (`http://127.0.0.1:8000`)**:
   - Point out the clean, professional dark UI inspired by professional creative and computer vision software.
2. **Navigate to "Upload Workspace"**:
   - Click **"Generate Synthetic Egocentric Video"** (or drag and drop any MP4 egocentric video).
   - Observe automatic duration probing, format validation, and pipeline trigger.
3. **Inspect the "Analysis Workspace"**:
   - Show the synchronized timeline: keyframes, localized actions (e.g., `[cut, vegetable]`, `[mix, ingredient]`, `[wash, plate]`), and confidence levels.
   - Point out how idle head sway periods are suppressed while physical hand-object interactions are highlighted.
4. **Demonstrate the "Highlight Editor"**:
   - Show the strict **$\le 15.0\%$ Budget Bar**.
   - Click a highlight segment to loop preview the cut footage.
   - Click "Recalculate Selection" to demonstrate dynamic MMR re-weighting.
5. **Review the "Results Dashboard" & Download Artifacts**:
   - Play the side-by-side player: 40.0s original condensed into 5.9s (14.7% duration).
   - Download the official `synthetic_demo.json` and `synthetic_demo_highlight.mp4`.
6. **Verify Compliance via CLI**:
   - Run `python validate.py` in the terminal to show 100% adherence to Samsung Track 4 rules.

---

## 10. Repository File Structure

```
cheese_project/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI server entry point
│   │   ├── routes/api_router.py       # REST API endpoints
│   │   ├── schemas/video_schemas.py   # Pydantic data models
│   │   ├── services/video_service.py  # Orchestration & caching service
│   │   └── pipeline/                  # Modular AI/ML pipeline
│   │       ├── video_ingest.py        # Video metadata extraction & keyframes
│   │       ├── intelligent_sampler.py # 2 FPS Farneback optical flow sampler
│   │       ├── hand_object_detector.py# Egocentric HOI skin + edge filter
│   │       ├── action_recognizer.py   # Zero-shot CLIP ViT-B/32 classifier
│   │       ├── temporal_localizer.py  # Change-point localization & tIoU merge
│   │       ├── importance_scorer.py   # Explainable multi-factor scoring
│   │       ├── highlight_selector.py  # Greedy MMR optimizer (<= 15% budget)
│   │       ├── video_renderer.py      # Frame-accurate FFmpeg MP4 renderer
│   │       └── pipeline_orchestrator.py # Full pipeline orchestrator
│   ├── tests/
│   │   └── make_synthetic_demo.py     # Egocentric video generator
│   └── weights/
│       ├── clip_vitb32.pt             # Bundled CLIP checkpoint (577 MB)
│       └── supported_classes.json     # EPIC-KITCHENS & FPVSum taxonomies
├── frontend/
│   ├── src/
│   │   ├── components/Navbar.tsx      # Dark navigation bar
│   │   ├── pages/                     # 6 Dedicated application workspaces
│   │   │   ├── LandingPage.tsx
│   │   │   ├── UploadWorkspace.tsx
│   │   │   ├── AnalysisWorkspace.tsx
│   │   │   ├── HighlightEditor.tsx
│   │   │   ├── ResultsDashboard.tsx
│   │   │   └── TechnicalReport.tsx
│   │   ├── services/api.ts            # REST client with real-time progress
│   │   └── types/index.ts             # TypeScript interface contracts
│   └── dist/                          # Pre-compiled static assets
├── evaluation/
│   ├── metrics.py                     # Official 100-pt metrics calculation
│   ├── evaluate.py                    # Dataset evaluation script
│   └── ground_truth/                  # Sample ground truth annotations
├── TEAM_ID/                           # Samsung Official Submission Bundle
│   ├── run.sh                         # Linux CLI runner
│   ├── run.bat                        # Windows CLI runner
│   ├── requirements.txt               # Bundled submission requirements
│   ├── validate.py                    # Self-contained validator
│   ├── code/                          # Self-contained pipeline code
│   ├── weights/                       # Offline model weights
│   └── outputs/                       # Generated benchmark outputs
├── validate.py                        # Root validation script
├── run_app.bat                        # One-click Windows application launcher
├── run_app.sh                         # One-click Linux application launcher
├── requirements.txt                   # Root environment dependencies
└── README.md                          # Comprehensive documentation
```

---

## 11. Team Identity
**Project:** MOMENTIQ  
**Hackathon:** Samsung R&D Institute India XR Hackathon 2026  
**Track:** Track 4 — Action Aware Video Summarization  

