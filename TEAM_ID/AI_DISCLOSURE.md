# AI Disclosure Statement — MOMENTIQ
### Samsung R&D Institute India XR Hackathon 2026 — Track 4: Action Aware Video Summarization

> **Team Name:** `VITChennai_RRR`  
> **Institution:** Vellore Institute of Technology, Chennai (VIT Chennai)  
> **Team Members:** Rishita R (`24bai1632`), Ryan Jain (`24brs1395`), Rhythm Rastogi (`24bai1508`)  
> **Date:** November 19, 2026  

---

## 1. Overview & Policy Compliance

In accordance with the **Samsung XR Hackathon 2026 Submission Guidelines**, this document outlines the complete disclosure of artificial intelligence foundation models, open-source weights, and developer assistance tools utilized in the design, development, and presentation of **MOMENTIQ**.

---

## 2. Foundation AI Models & Pretrained Weights

| Component / Model | Provider / Architecture | License | Purpose in MOMENTIQ | Offline Bundling |
| :--- | :--- | :--- | :--- | :--- |
| **CLIP ViT-B/32** | OpenAI / `open_clip_torch` (QuickGELU) | MIT License | Zero-shot vision-language feature extraction for 98 verbs, 301 nouns, and 14 egocentric sports categories. | Checkpoint (`clip_vitb32.pt`, 577 MB) is bundled locally in `weights/` for 100% offline execution. |
| **Farneback Optical Flow** | OpenCV (`cv2.calcOpticalFlowFarneback`) | Apache 2.0 | Classical dense pixel motion field calculation across 2 FPS sampled frame pairs. | Self-contained in OpenCV. |
| **Edge-TTS Neural Synthesizer** | Microsoft Edge Neural TTS | Public API | Studio audio narration for the 2:44 min demo video (`en-US-ChristopherNeural`). | Pre-rendered in `VITChennai_RRR_Demo_Video.mp4`. |

---

## 3. Original Algorithmic & Architectural Contributions

All pipeline reasoning, motion filtering, temporal boundary estimation, and highlight optimization algorithms were **designed, mathematically formulated, and implemented directly by Team VITChennai_RRR**:

1. **Egocentric Motion Decomposition:**
   * Mathematical formulation of global user head saccade isolation via spatial median vector calculation:
     $$\vec{v}_{\text{head}} = (\operatorname{median}(\Delta x), \operatorname{median}(\Delta y))$$
   * Subtraction of $\vec{v}_{\text{head}}$ to isolate the residual manipulation field $\vec{v}_{\text{manip}}(x, y)$, effectively eliminating false highlight spikes caused by user head turns.

2. **Spatial Hand-Object Interaction (HOI) Filter:**
   * Novel combination of YCbCr skin chrominance thresholding ($Y \in [80, 240], Cb \in [85, 135], Cr \in [135, 180]$) and foveal Canny edge gradient density focused on the lower manipulation quadrant.
   * Suppresses idle gaze, transit, and empty scene exploration without requiring expensive object bounding box anchors.

3. **Temporal Action Localization (TAL):**
   * Cosine distance change-point detection on consecutive CLIP frame embeddings to pinpoint action transitions.
   * Temporal Intersection-over-Union (tIoU $\ge 0.35$) segment clustering to assemble continuous, coherent action boundaries.

4. **Greedy MMR Highlight Optimizer with Distinct Action Bonus:**
   * Formulated a novel Distinct Action Bonus ($\beta = 0.40$) inside the Maximal Marginal Relevance objective:
     $$\arg\max_{s \in \mathcal{U}} \left[ S(s) - \lambda \max_{s' \in \mathcal{S}} \text{Sim}(s, s') + \beta \cdot \mathbf{1}_{[\text{action}(s) \notin \text{actions}(\mathcal{S})]} \right]$$
   * Explicitly designed to maximize the official **Action Coverage metric (40% jury weight)** while strictly enforcing the $\le 15.0\%$ duration ceiling and $\ge 4.0\text{ s}$ highlight segment constraint.

5. **Full-Stack Interactive Studio:**
   * Custom FastAPI backend and React 19 / TypeScript NLE-style timeline editor with real-time budget telemetry, keyframe inspection, and frame-accurate FFmpeg highlight video rendering.

---

## 4. Generative AI & Developer Assistance Disclosure

* **AI Coding Assistants:** Large Language Model tools (including Google DeepMind Antigravity / Gemini) were utilized for code formatting, documentation drafting, boilerplate schema typing, and test script scaffolding.
* **Human Verification:** All generated code, mathematical algorithms, JSON output schemas, and validation scripts were thoroughly reviewed, debugged, executed, and benchmarked by the team members.

---

## 5. Data Integrity & Academic Honesty Statement

* **Zero Hardcoding Policy:** None of the predictions in `TEAM_ID/outputs/` contain hardcoded ground truth labels or copied annotations. Every single output file was generated deterministically by executing our inference pipeline against the official `manifest.csv` target videos.
* **Reproducibility Guarantee:** The entire pipeline is completely reproducible using our submitted standalone entry points (`bash run.sh <video.mp4> <out.json>` and `run.bat <video.mp4> <out.json>`) in an isolated, offline environment.
