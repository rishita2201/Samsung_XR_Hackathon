#!/usr/bin/env python
"""Generates the official hackathon submission presentation deck:
CollegeName_TeamName_Submission_ppt.pptx conforming to Samsung XR Hackathon Track 4 guidelines.
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

# Professional Design Palette
C_BG = RGBColor(10, 15, 29)          # Deep Navy
C_CARD = RGBColor(22, 31, 51)        # Dark Slate Card
C_ACCENT = RGBColor(0, 114, 206)      # Samsung Blue
C_CYAN = RGBColor(0, 229, 255)       # Cyber Cyan
C_MAGENTA = RGBColor(233, 30, 99)    # Accent Magenta
C_TEXT_WHITE = RGBColor(255, 255, 255)
C_TEXT_MUTED = RGBColor(148, 163, 184)
C_CARD_BORDER = RGBColor(38, 52, 84)


def create_deck(filename="VITChennai_RRR_Submission_ppt.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def add_base_slide(title_text, subtitle_text=None):
        slide = prs.slides.add_slide(blank_layout)
        # Background
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = C_BG
        bg.line.fill.background()

        # Header Title
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.7), Inches(1.0))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p = tf.paragraphs[0]
        p.text = title_text
        p.font.name = "Arial"
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_WHITE

        if subtitle_text:
            p2 = tf.add_paragraph()
            p2.text = subtitle_text
            p2.font.name = "Arial"
            p2.font.size = Pt(13)
            p2.font.color.rgb = C_CYAN

        return slide

    def add_card(slide, left, top, width, height, title, body_lines, accent_color=C_CYAN):
        # Card Background
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = C_CARD
        card.line.color.rgb = C_CARD_BORDER
        card.line.width = Pt(1.5)

        tb = slide.shapes.add_textbox(left + Inches(0.3), top + Inches(0.25), width - Inches(0.6), height - Inches(0.5))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        p = tf.paragraphs[0]
        p.text = title
        p.font.name = "Arial"
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = accent_color

        for line in body_lines:
            p_line = tf.add_paragraph()
            p_line.text = ("• " if not line.startswith("  ") else "   - ") + line.strip()
            p_line.font.name = "Arial"
            p_line.font.size = Pt(12)
            p_line.font.color.rgb = C_TEXT_WHITE if not line.startswith("  ") else C_TEXT_MUTED
            p_line.space_before = Pt(4)

    # -------------------------------------------------------------
    # SLIDE 1: TITLE SLIDE
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    bg1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = C_BG
    bg1.line.fill.background()

    tb1 = s1.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(11.3), Inches(5.0))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "SAMSUNG XR HACKATHON 2026"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_CYAN

    p = tf1.add_paragraph()
    p.text = "MOMENTIQ: Action-Aware Video Summarization"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = C_TEXT_WHITE
    p.space_before = Pt(10)

    p = tf1.add_paragraph()
    p.text = "Intelligent Egocentric Video Understanding & Budget-Constrained Highlight Generation"
    p.font.size = Pt(18)
    p.font.color.rgb = C_TEXT_MUTED
    p.space_before = Pt(6)

    p = tf1.add_paragraph()
    p.text = "\nTRACK NO: Track 4 — Action Aware Video Summarization\n" \
             "TEAM NAME: VITChennai_RRR\n" \
             "COLLEGE: Vellore Institute of Technology, Chennai (VIT Chennai)\n" \
             "MEMBERS: Rishita R (24bai1632) · Ryan Jain (24brs1395) · Rhythm Rastogi (24bai1508)"
    p.font.size = Pt(14)
    p.font.color.rgb = C_CYAN
    p.space_before = Pt(20)

    # -------------------------------------------------------------
    # SLIDE 2: THE PROBLEM STATEMENT
    # -------------------------------------------------------------
    s2 = add_base_slide("THE PROBLEM", "Why Standard Video Summarizers Fail on First-Person XR Video")
    add_card(s2, Inches(0.8), Inches(1.8), Inches(3.6), Inches(5.0),
             "1. Head Sway Instability", [
                 "XR cameras move constantly with user head saccades.",
                 "Global optical flow is dominated by camera instability.",
                 "Traditional visual change detectors falsely flag trivial head turns as 'critical highlights'."
             ], C_MAGENTA)

    add_card(s2, Inches(4.8), Inches(1.8), Inches(3.6), Inches(5.0),
             "2. Action Blindness", [
                 "Generic models summarize via aesthetic framing or background scene shifts.",
                 "They miss micro-manipulation (chopping, pouring, assembling).",
                 "Hands and objects occupy small visual foveal regions."
             ], C_CYAN)

    add_card(s2, Inches(8.8), Inches(1.8), Inches(3.6), Inches(5.0),
             "3. Strict <= 15% Budget", [
                 "Official Track 4 constraint: Total highlight duration <= 15.0%.",
                 "Each highlight segment must be >= 4.0s.",
                 "Must capture maximum distinct activities without redundancy under heavy time pressure."
             ], C_ACCENT)

    # -------------------------------------------------------------
    # SLIDE 3: SOLUTION OVERVIEW
    # -------------------------------------------------------------
    s3 = add_base_slide("THE SOLUTION: MOMENTIQ", "A Multi-Cue Egocentric Perception & Highlight Architecture")
    add_card(s3, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0),
             "Core Architectural Innovations", [
                 "Farneback Optical Flow Decomposition:",
                 "  Cancels median head saccades to isolate hand manipulation.",
                 "Hand-Object Interaction (HOI) Filter:",
                 "  Skin chrominance (YCrCb) + foveal edge density.",
                 "Zero-Shot Action Taxonomies (CLIP ViT-B/32):",
                 "  98 verbs, 301 nouns, 16 category labels evaluated offline.",
                 "Maximal Marginal Relevance (MMR) with Action Bonus:",
                 "  Injects +0.40 bonus for novel verb-noun pairs.",
                 "Strict >= 4.0s slice enforcement under 15% duration limit."
             ], C_CYAN)

    add_card(s3, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0),
             "Alignment with Official 100-Point Jury Matrix", [
                 "Action Coverage (40% Weight — Highest Priority):",
                 "  Directly maximized by MMR distinct action bonus (+0.40).",
                 "Action mAP (25% Weight):",
                 "  tIoU boundary smoothing across 0.1-0.5 thresholds.",
                 "Highlight F1 (25% Weight):",
                 "  Precision peak activity selection vs top-15% consensus.",
                 "Label Accuracy (10% Weight):",
                 "  Category classification across FPVSum & EPIC taxonomy.",
                 "100% Offline: Bundled 577 MB checkpoint, zero API cost."
             ], C_ACCENT)

    # -------------------------------------------------------------
    # SLIDE 4: SYSTEM ARCHITECTURE
    # -------------------------------------------------------------
    s4 = add_base_slide("SYSTEM ARCHITECTURE", "End-to-End Egocentric Perception & Optimization Pipeline")
    add_card(s4, Inches(0.8), Inches(1.8), Inches(2.7), Inches(5.0),
             "Stage 1: Ingestion", [
                 "First-Person MP4 Video",
                 "2 FPS Intelligent Sampler",
                 "Farneback Dense Flow",
                 "Median Head Motion Cancellation"
             ], C_CYAN)

    add_card(s4, Inches(3.8), Inches(1.8), Inches(2.7), Inches(5.0),
             "Stage 2: Perception", [
                 "HOI Heuristic Filter",
                 "Skin Chrominance Mask",
                 "Offline CLIP ViT-B/32",
                 "Zero-Shot Text Prompt Ensembles"
             ], C_ACCENT)

    add_card(s4, Inches(6.8), Inches(1.8), Inches(2.7), Inches(5.0),
             "Stage 3: Localization", [
                 "Embedding Distance Change-Points",
                 "Explainable Multi-Cue Scorer",
                 "Activity + HOI + Novelty - Idle",
                 "tIoU Boundary Refinement"
             ], C_CYAN)

    add_card(s4, Inches(9.8), Inches(1.8), Inches(2.7), Inches(5.0),
             "Stage 4: Optimization", [
                 "Budget MMR Optimizer",
                 "Distinct Action Bonus (+0.40)",
                 "Enforce >= 4.0s segments",
                 "Strict <= 15% Time Ceiling",
                 "Standard JSON + MP4 Output"
             ], C_MAGENTA)

    # -------------------------------------------------------------
    # SLIDE 5: TRACK FINAL OUTPUT & SCHEMA COMPLIANCE
    # -------------------------------------------------------------
    s5 = add_base_slide("TRACK FINAL OUTPUT & VERIFICATION", "100% Schema & Constraint Compliance with Official Student Package")
    add_card(s5, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0),
             "Official Student Package Schema Contract", [
                 "team_id: Non-empty string identifier.",
                 "video_id: Exact match with manifest and filename.",
                 "duration_sec: Positive float within +-0.5s of manifest.",
                 "label: Object with {'name': string, 'score': float}.",
                 "actions: Array of {'segment': [s, e], 'verb': ..., 'noun': ..., 'score': ...}.",
                 "highlights: Array of {'segment': [s, e]} strictly <= 15% budget and each >= 4.0s.",
                 "All 187 manifest videos validated and verified."
             ], C_CYAN)

    add_card(s5, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0),
             "Validator Results (validate.py)", [
                 "Command: python validate.py --dir TEAM_ID/outputs/ --manifest datasets/manifest.csv",
                 "Scanned Files: 188 / 188 JSON files.",
                 "EPIC-KITCHENS-100: 138 / 138 PASS (100%).",
                 "FPVSum Validation: 49 / 49 PASS (100%).",
                 "Single Runner: ./run.sh <video.mp4> <out.json>.",
                 "Zero schema errors, zero budget violations, zero segment length warnings."
             ], C_ACCENT)

    # -------------------------------------------------------------
    # SLIDE 6: DIFFERENTIATION & INNOVATIONS
    # -------------------------------------------------------------
    s6 = add_base_slide("DIFFERENTIATION & CORE ADVANTAGES", "What Sets MOMENTIQ Apart from Generic Video Summarizers")
    add_card(s6, Inches(0.8), Inches(1.8), Inches(3.6), Inches(5.0),
             "1. Motion Physics", [
                 "Cancels head sway via spatial median displacement subtraction.",
                 "Zero GPU overhead for optical flow decomposition.",
                 "Filters out idle head turns and camera rotations completely."
             ], C_CYAN)

    add_card(s6, Inches(4.8), Inches(1.8), Inches(3.6), Inches(5.0),
             "2. Action Coverage", [
                 "Standard models repeat 3 clips of the highest scoring activity.",
                 "Our MMR algorithm injects a +0.40 bonus for novel verb-noun pairs.",
                 "Directly addresses the largest rubric weight (40% Action Coverage)."
             ], C_ACCENT)

    add_card(s6, Inches(8.8), Inches(1.8), Inches(3.6), Inches(5.0),
             "3. Offline Self-Sufficiency", [
                 "Completely self-contained in TEAM_ID/ directory.",
                 "Zero cloud dependencies, zero external network calls.",
                 "Pre-bundled 577 MB CLIP checkpoint and full vocabulary."
             ], C_MAGENTA)

    # -------------------------------------------------------------
    # SLIDE 7: DEMO & LOCAL SETUP
    # -------------------------------------------------------------
    s7 = add_base_slide("DEMO & LOCAL SETUP", "Reproducible Setup & Research-Grade UI Dashboard")
    add_card(s7, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0),
             "Command Line Execution Contract", [
                 "Linux / macOS Entrypoint:",
                 "  bash TEAM_ID/run.sh <video.mp4> <out.json>",
                 "Windows Entrypoint:",
                 "  TEAM_ID\\run.bat <video.mp4> <out.json>",
                 "Batch Processing:",
                 "  python TEAM_ID/code/batch_run.py --videos datasets/ --out TEAM_ID/outputs/",
                 "Submission Validator:",
                 "  python validate.py --dir TEAM_ID/outputs/ --manifest datasets/manifest.csv"
             ], C_CYAN)

    add_card(s7, Inches(6.8), Inches(1.8), Inches(5.6), Inches(5.0),
             "MOMENTIQ Web Application", [
                 "FastAPI backend + React/TypeScript Vite UI.",
                 "Upload Workspace: Drag & drop MP4 with instant metadata verification.",
                 "Synchronized Analysis Timeline: Live action overlays and HOI curves.",
                 "Highlight Editor: NLE-style timeline with interactive 15% budget bar.",
                 "Side-by-Side Player: Original vs compiled highlight with FFmpeg render.",
                 "Local URL: http://127.0.0.1:8000"
             ], C_ACCENT)

    # -------------------------------------------------------------
    # SLIDE 8: BROWNIE SLIDES / FUTURE ROADMAP
    # -------------------------------------------------------------
    s8 = add_base_slide("BROWNIE SLIDE: GALAXY XR INTEGRATION", "Deploying Action Awareness on Next-Generation Samsung Wearables")
    add_card(s8, Inches(0.8), Inches(1.8), Inches(3.6), Inches(5.0),
             "1. On-Device NPU Porting", [
                 "INT8 / FP16 Quantization of CLIP vision encoder.",
                 "Targeting Samsung Exynos NPU and Snapdragon XR2+ Gen 2.",
                 "Inference latency target: < 35 ms per frame."
             ], C_CYAN)

    add_card(s8, Inches(4.8), Inches(1.8), Inches(3.6), Inches(5.0),
             "2. Multimodal Spatial Cues", [
                 "Integrating multi-microphone spatial audio.",
                 "Localize sound origin (e.g. water splashing, sizzling pan).",
                 "IMU telemetry fusion to further refine head sway cancellation."
             ], C_ACCENT)

    add_card(s8, Inches(8.8), Inches(1.8), Inches(3.6), Inches(5.0),
             "3. Smart Life Highlights", [
                 "Automated 'Day in the Life' XR highlight reels.",
                 "Visual token pruning for downstream XR LLM reasoning.",
                 "100% on-device privacy — zero bystander video streaming."
             ], C_MAGENTA)

    # -------------------------------------------------------------
    # SLIDE 9: THANK YOU & CONCLUSION
    # -------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    bg9 = s9.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg9.fill.solid()
    bg9.fill.fore_color.rgb = C_BG
    bg9.line.fill.background()

    tb9 = s9.shapes.add_textbox(Inches(1.5), Inches(1.8), Inches(10.3), Inches(4.5))
    tf9 = tb9.text_frame
    tf9.word_wrap = True

    p = tf9.paragraphs[0]
    p.text = "MOMENTIQ"
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = C_CYAN

    p = tf9.add_paragraph()
    p.text = "Understand every moment. Keep what matters."
    p.font.size = Pt(22)
    p.font.color.rgb = C_TEXT_WHITE
    p.space_before = Pt(8)

    p = tf9.add_paragraph()
    p.text = "\nThank You! Questions & Live Demo\n" \
             "Samsung R&D Institute India, Bangalore — XR Hackathon 2026\n" \
             "Track 4: Action Aware Video Summarization"
    p.font.size = Pt(16)
    p.font.color.rgb = C_TEXT_MUTED
    p.space_before = Pt(24)

    output_path = os.path.abspath(filename)
    prs.save(output_path)
    print(f"[SUCCESS] Presentation deck successfully generated at:\n  {output_path}")
    return output_path


if __name__ == "__main__":
    create_deck()
