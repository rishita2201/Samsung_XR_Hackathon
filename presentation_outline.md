# MOMENTIQ — Presentation & Pitch Deck Outline
### Samsung R&D Institute India XR Hackathon 2026
**Track 4:** Action-Aware Video Summarization  
**Product:** MOMENTIQ — Intelligent First-Person Video Understanding & Highlight Generation  
**Tagline:** *Understand every moment. Keep what matters.*  

---

## Slide 1: Title & Vision
- **Header:** MOMENTIQ
- **Subheader:** Action-Aware Egocentric Video Intelligence & Highlight Generation
- **Event:** Samsung XR Hackathon 2026 — Track 4
- **Speaker:** Team MOMENTIQ
- **Key Visual:** Sleek dark UI screenshot showing the synchronized egocentric video player with live action overlay and the $\le 15.0\%$ highlight budget indicator.
- **Talking Points:**
  - "XR headsets and smart glasses record life continuously from our point of view. But 90% of what is recorded is head sway, idle transit, or repetitive motion. MOMENTIQ transforms hours of raw egocentric video into a concise, intelligent 15% highlight based on *what actions actually happened*."

---

## Slide 2: The Problem — Why Traditional Summarization Fails on XR Video
- **Header:** The Egocentric Summarization Paradox
- **Key Challenges:**
  1. **Continuous Camera Instability:** Incessant user head movement creates huge global optical flow that tricks standard frame samplers into marking head turns as "important events".
  2. **Action Blindness:** Generic summarizers score frames using visual variance or background scene shifts, completely missing critical physical manipulation.
  3. **High Redundancy:** Egocentric videos contain prolonged periods of idle waiting and repetitive motor tasks (e.g., continuous stirring, slicing).
- **The Challenge Rule:** Strict $\le 15.0\%$ duration budget constraint. Every second must count.

---

## Slide 3: The MOMENTIQ Solution
- **Header:** Action-Aware Video Understanding
- **Three Core Pillars:**
  1. **Egocentric Motion Decomposition:** Farneback optical flow with spatial median subtraction cancels head motion and isolates the lower-central hand/tool manipulation zone.
  2. **Zero-Shot Action Recognition:** Pretrained CLIP ViT-B/32 prompt ensembles classify actions across EPIC-KITCHENS-100 & FPVSum verb/noun taxonomies without requiring supervised fine-tuning.
  3. **Diversity-Constrained Highlight Optimization:** Maximal Marginal Relevance (MMR) with a distinct action bonus (+0.40) directly maximizes the **Action Coverage metric (40% weight)** within the strict $15\%$ budget.

---

## Slide 4: System Architecture & Mathematical Pipeline
- **Header:** End-to-End Deep Learning Architecture
- **Diagram:**
  - Input Video $\rightarrow$ 2 FPS Adaptive Sampler $\rightarrow$ Dense Flow Decomposition $\rightarrow$ Egocentric HOI Spatial Filter $\rightarrow$ Zero-Shot CLIP $\rightarrow$ Temporal Change-Point Localization $\rightarrow$ Explainable Multi-Factor Scorer $\rightarrow$ Budget-Constrained MMR $\rightarrow$ Frame-Accurate FFmpeg Concat.
- **Mathematical Formulations:**
  - Residual Hand Flow: $\vec{v}_{\text{manip}}(x, y) = \|\vec{v}(x, y) - \vec{v}_{\text{head}}\|_2$
  - Multi-Factor Score: $S(s) = 0.30 A(s) + 0.25 H(s) + 0.20 N(s) + 0.15 C(s) - 0.20 I(s)$
  - Constrained MMR: $\arg\max_s [S(s) - \lambda \max_{s'} \text{Sim}(s, s') + \beta \mathbf{1}_{\text{distinct}}] \quad \text{s.t.} \quad \sum \text{dur} \le 0.15 T$

---

## Slide 5: Hand-Object Interaction (HOI) & Zero-Shot Perception
- **Header:** Understanding Physical Hands & Tools
- **Technical Breakdown:**
  - **Egocentric HOI:** Dual-color space skin chrominance (YCrCb + HSV) coupled with foveal Canny edge density in the manipulation quadrant. Identifies physical manipulation with zero GPU bounding box overhead.
  - **Zero-Shot Action Taxonomies:**
    - Verbs: `cut`, `mix`, `wash`, `open`, `take`, `pour`, `place`, `manipulate`
    - Nouns: `vegetable`, `ingredient`, `container`, `plate`, `cup`, `knife`, `tool`
  - Temporal boundary refinement via embedding cosine distance change-points and tIoU smoothing.

---

## Slide 6: Highlight Optimization & The 15% Budget Constraint
- **Header:** Budget-Constrained Optimization
- **Key Innovation — Distinct Action Bonus:**
  - Samsung's official evaluation rubric awards **40% of the entire score to Action Coverage** (vs 25% for mAP, 25% for F1, 10% for Label).
  - Standard greedy selection picks multiple segments of the highest-scoring single action (e.g. 3 clips of cutting).
  - MOMENTIQ injects a $+0.40$ bonus whenever a candidate segment introduces a previously unseen (verb, noun) action pair, ensuring maximum diversity of ground truth activities in the summary.
- **Strict Budget Guard:** Selection stops at $\le 0.15 \times \text{Duration} \times 0.995$ to guarantee 100% compliance on automated validators.

---

## Slide 7: Live Platform Showcase
- **Header:** Research-Grade User Experience
- **Features Highlighted:**
  - **Dual Synchronized Video Player:** Original full-length stream side-by-side with the 15% highlight.
  - **Interactive Multi-Track Timeline:** Keyframes, localized action spans, confidence bars, and HOI heatmap.
  - **Highlight Editor:** NLE-style controls with dynamic budget indicator, segment preview, and one-click re-rendering.
  - **Jury Compliance Validator:** Built-in validation runner ensuring every exported JSON meets Samsung's exact schema.

---

## Slide 8: Evaluation & Benchmark Results
- **Header:** Benchmark Performance
- **Rubric Breakdown (100 Points Total):**
  - **Action Coverage (40 pts):** Exceptional coverage through MMR diversity optimization.
  - **Action mAP (25 pts):** High temporal boundary alignment using tIoU smoothing.
  - **Highlight F1 (25 pts):** Precision trimming of peak action motion.
  - **Label Accuracy (10 pts):** Global video category consensus voting.
- **Offline Self-Sufficiency:**
  - All model weights (`clip_vitb32.pt`, 577 MB) bundled offline in `TEAM_ID/weights/`. Zero cloud API dependencies. Runs completely offline on standard CPUs or GPUs.

---

## Slide 9: XR Ecosystem Integration & Future Roadmap
- **Header:** The Future on Samsung Galaxy XR
- **Near-Term Hardware Alignment:**
  - On-device inference: Quantizing CLIP ViT-B/32 to INT8/FP16 for Samsung Exynos / Snapdragon XR2+ NPUs.
  - Real-time streaming summarization: Generating daily life highlights on-device with zero cloud latency and total privacy.
  - Spatial audio integration: Audio peak and speech localization to augment egocentric vision.

---

## Slide 10: Conclusion & Q&A
- **Header:** Understand Every Moment. Keep What Matters.
- **Summary:**
  - Complete, functional, mathematically grounded action-aware summarizer.
  - 100% compliant with Samsung Track 4 schema and 15% duration budget.
  - Research-grade web UI and fully automated CLI test harness.
- **Links & Deliverables:**
  - Submission Bundle: `TEAM_ID/`
  - Automated Validator: `python validate.py`
  - Evaluation Harness: `python evaluation/evaluate.py`
  - Interactive Application: `http://127.0.0.1:8000`
- **Q&A**

