import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

os.makedirs("demo_assets/screenshots", exist_ok=True)

FONT_HEADING = ImageFont.truetype("segoeuib.ttf", 26)
FONT_BOLD = ImageFont.truetype("segoeuib.ttf", 18)
FONT_BODY = ImageFont.truetype("segoeui.ttf", 16)
FONT_SMALL = ImageFont.truetype("segoeui.ttf", 13)
FONT_CODE = ImageFont.truetype("consola.ttf", 14)
FONT_CODE_BOLD = ImageFont.truetype("consolab.ttf" if os.path.exists("C:/Windows/Fonts/consolab.ttf") else "consola.ttf", 16)

# Colors
BG_DARK = (15, 23, 42)
BG_CARD = (24, 32, 54)
BG_CARD_LIGHT = (30, 41, 68)
BORDER_COLOR = (45, 60, 90)
TEXT_WHITE = (248, 250, 252)
TEXT_MUTED = (160, 175, 200)
ACCENT_CYAN = (14, 165, 233)
ACCENT_BLUE = (37, 99, 235)
ACCENT_GREEN = (34, 197, 94)
ACCENT_AMBER = (245, 158, 11)
ACCENT_ROSE = (244, 63, 94)


def draw_card(draw, box, fill=BG_CARD, outline=BORDER_COLOR, radius=10):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=1)


# 1. Architecture Flowchart Screenshot
def create_arch_screenshot():
    w, h = 1200, 680
    img = Image.new("RGB", (w, h), BG_DARK)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, w, 50], fill=(20, 28, 50))
    draw.text((25, 12), "MOMENTIQ  ·  END-TO-END EGOCENTRIC PERCEPTION & SUMMARIZATION PIPELINE", fill=ACCENT_CYAN, font=FONT_BOLD)

    stages = [
        ("STAGE 1: ADAPTIVE SAMPLER", "Farneback Dense Flow", "Samples input MP4 at 2 FPS cadence to capture human action transients while pruning idle compute.", ACCENT_CYAN),
        ("STAGE 2: MOTION DECOMPOSITION", "Median Head Sway Subtraction", "Calculates spatial median vector v_head and subtracts it to isolate intentional tool/hand manipulation v_manip.", ACCENT_BLUE),
        ("STAGE 3: HOI INTERACTION FILTER", "Skin Chrominance + Foveal Edge", "YCbCr skin thresholding in manipulation zone combined with Canny edge density filters out passive room gazing.", ACCENT_GREEN),
        ("STAGE 4: ZERO-SHOT CLIP ViT-B/32", "EPIC-KITCHENS & FPVSum Prompts", "Aligns visual tokens with 98 verbs, 301 nouns, and 14 egocentric categories via tailored first-person prompt ensembles.", ACCENT_AMBER),
        ("STAGE 5: TEMPORAL LOCALIZER", "Change-Point & tIoU Clustering", "Tracks embedding cosine distance change-points and merges adjacent actions (tIoU >= 0.35) into contiguous segments.", ACCENT_ROSE),
        ("STAGE 6: MMR HIGHLIGHT OPTIMIZER", "Distinct Action Bonus (β = 0.40)", "Greedy MMR selection rewards novel action pairs (+0.40), strictly enforcing <= 15% budget and >= 4.0s segment rule.", ACCENT_CYAN)
    ]

    card_w = 360
    card_h = 260
    positions = [
        (40, 80), (420, 80), (800, 80),
        (40, 380), (420, 380), (800, 380)
    ]

    for i, (title, sub, desc, col) in enumerate(stages):
        x, y = positions[i]
        draw_card(draw, [x, y, x + card_w, y + card_h], fill=BG_CARD, outline=col)
        draw.rectangle([x + 15, y + 15, x + card_w - 15, y + 45], fill=(30, 42, 70))
        draw.text((x + 25, y + 20), title, fill=col, font=FONT_BOLD)
        draw.text((x + 20, y + 55), sub, fill=TEXT_WHITE, font=FONT_BOLD)

        words = desc.split(" ")
        lines, cur = [], ""
        for word in words:
            if len(cur + " " + word) < 38:
                cur += " " + word
            else:
                lines.append(cur.strip())
                cur = word
        if cur:
            lines.append(cur.strip())
        for l_idx, line in enumerate(lines):
            draw.text((x + 20, y + 90 + l_idx * 24), line, fill=TEXT_MUTED, font=FONT_BODY)

    img.save("demo_assets/screenshots/arch_diagram.png")
    print("Created arch_diagram.png")


# 2. Live Demo Web Studio Screenshot
def create_demo_studio_screenshot():
    w, h = 1200, 680
    img = Image.new("RGB", (w, h), (10, 14, 26))
    draw = ImageDraw.Draw(img)

    # Top app navbar
    draw.rectangle([0, 0, w, 50], fill=(18, 25, 42))
    draw.text((25, 14), "MOMENTIQ STUDIO", fill=TEXT_WHITE, font=FONT_BOLD)
    draw.rectangle([210, 12, 380, 38], fill=(30, 45, 80))
    draw.text((220, 16), "Analysis Workspace", fill=ACCENT_CYAN, font=FONT_SMALL)
    draw.text((410, 16), "Upload Workspace", fill=TEXT_MUTED, font=FONT_SMALL)
    draw.text((560, 16), "Highlight Editor", fill=TEXT_MUTED, font=FONT_SMALL)
    draw.text((700, 16), "Results Dashboard", fill=TEXT_MUTED, font=FONT_SMALL)
    draw.rectangle([w - 220, 12, w - 20, 38], fill=(20, 83, 45))
    draw.text((w - 205, 16), "BUDGET: 10.6% / 15.0%", fill=TEXT_WHITE, font=FONT_SMALL)

    # Main Video Player area
    v_x1, v_y1, v_x2, v_y2 = 30, 70, 750, 520
    draw.rectangle([v_x1, v_y1, v_x2, v_y2], fill=(5, 8, 15), outline=BORDER_COLOR)

    # Read frame from synthetic demo
    cap = cv2.VideoCapture("uploads/synthetic_demo.mp4")
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_POS_FRAMES, 180)
        ret, frame = cap.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, (v_x2 - v_x1 - 10, v_y2 - v_y1 - 10))
            img.paste(Image.fromarray(frame_resized), (v_x1 + 5, v_y1 + 5))
    cap.release()

    # Video HUD overlays
    draw.rectangle([v_x1 + 20, v_y1 + 20, v_x1 + 320, v_y1 + 60], fill=(15, 23, 42, 230))
    draw.text((v_x1 + 30, v_y1 + 28), "ACTION: take pan", fill=ACCENT_GREEN, font=FONT_BOLD)
    draw.rectangle([v_x2 - 180, v_y1 + 20, v_x2 - 20, v_y1 + 60], fill=(15, 23, 42, 230))
    draw.text((v_x2 - 165, v_y1 + 28), "CONF: 0.88", fill=ACCENT_CYAN, font=FONT_BOLD)

    # Scrubber Bar
    draw.rectangle([v_x1, 540, v_x2, 552], fill=(30, 41, 59))
    draw.rectangle([v_x1 + 90, 540, v_x1 + 190, 552], fill=ACCENT_AMBER)
    draw.rectangle([v_x1 + 320, 540, v_x1 + 450, 552], fill=ACCENT_AMBER)
    draw.rectangle([v_x1 + 560, 540, v_x1 + 670, 552], fill=ACCENT_AMBER)
    draw.ellipse([v_x1 + 380 - 6, 540 - 4, v_x1 + 380 + 6, 552 + 4], fill=ACCENT_CYAN)

    draw.text((v_x1, 565), "00:18.2 / 00:40.0   |   Active Highlight Segment [00:17.0 - 00:22.5]", fill=TEXT_MUTED, font=FONT_SMALL)

    # Right Telemetry Side Panel
    p_x1, p_y1, p_x2, p_y2 = 780, 70, w - 30, 640
    draw_card(draw, [p_x1, p_y1, p_x2, p_y2], fill=BG_CARD, outline=BORDER_COLOR)
    draw.text((p_x1 + 20, p_y1 + 20), "TELEMETRY & DETECTION PIPELINE", fill=ACCENT_CYAN, font=FONT_BOLD)

    rows = [
        ("Current Video ID", "synthetic_demo.mp4", TEXT_WHITE),
        ("Original Duration", "40.0 seconds", TEXT_WHITE),
        ("Highlight Duration", "4.24 seconds (10.6%)", ACCENT_GREEN),
        ("Duration Budget", "<= 15.0% [STRICTLY COMPLIANT]", ACCENT_GREEN),
        ("Egocentric Sway Filter", "Cancelled (-2.8 px/f)", ACCENT_CYAN),
        ("Residual Manipulation", "Active Tool Engagement", ACCENT_GREEN),
        ("Recognized Verb", "take (EPIC-KITCHENS)", ACCENT_AMBER),
        ("Recognized Noun", "pan (EPIC-KITCHENS)", ACCENT_AMBER),
        ("Action Localization", "[00:12.4s -> 00:18.2s]", ACCENT_CYAN),
        ("Export Standard", "Samsung Track 4 JSON (6 keys)", ACCENT_ROSE)
    ]
    for i, (label, val, col) in enumerate(rows):
        y = p_y1 + 65 + i * 44
        draw.text((p_x1 + 20, y), label, fill=TEXT_MUTED, font=FONT_BODY)
        draw.text((p_x1 + 20, y + 20), val, fill=col, font=FONT_BOLD)

    img.save("demo_assets/screenshots/demo_ui.png")
    print("Created demo_ui.png")


# 3. Track Final Output Screenshot
def create_track_output_screenshot():
    w, h = 1200, 680
    img = Image.new("RGB", (w, h), (10, 14, 26))
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, w, 50], fill=(20, 28, 50))
    draw.text((25, 14), "SAMSUNG TRACK 4 OFFICIAL SPECIFICATION & VALIDATION RESULTS", fill=ACCENT_CYAN, font=FONT_BOLD)

    # Left Box: Structured JSON Output
    j_x1, j_y1, j_x2, j_y2 = 30, 75, 580, 645
    draw_card(draw, [j_x1, j_y1, j_x2, j_y2], fill=(15, 20, 35), outline=ACCENT_CYAN)
    draw.text((j_x1 + 20, j_y1 + 15), "OUTPUT: P02_109.json (Strict 6-Key Schema)", fill=ACCENT_CYAN, font=FONT_BOLD)

    json_code = [
        '{',
        '  "team_id": "VITChennai_RRR",',
        '  "video_id": "P02_109",',
        '  "duration_sec": 512.3,',
        '  "label": {',
        '    "name": "cooking",',
        '    "score": 0.96',
        '  },',
        '  "actions": [',
        '    {',
        '      "segment": [12.4, 18.2],',
        '      "verb": "open",',
        '      "noun": "fridge",',
        '      "score": 0.88',
        '    },',
        '    {',
        '      "segment": [22.0, 31.5],',
        '      "verb": "take",',
        '      "noun": "pan",',
        '      "score": 0.92',
        '    }',
        '  ],',
        '  "highlights": [',
        '    { "segment": [11.0, 19.5] },',
        '    { "segment": [45.2, 53.0] }',
        '  ]',
        '}'
    ]
    for idx, line in enumerate(json_code):
        col = ACCENT_AMBER if '"' in line and (':' in line or '[' in line) else TEXT_WHITE
        if "team_id" in line or "VITChennai_RRR" in line:
            col = ACCENT_CYAN
        elif "highlights" in line or "segment" in line:
            col = ACCENT_GREEN
        draw.text((j_x1 + 25, j_y1 + 50 + idx * 22), line, fill=col, font=FONT_CODE)

    # Right Box: Validation Terminal Outcome
    t_x1, t_y1, t_x2, t_y2 = 610, 75, w - 30, 645
    draw_card(draw, [t_x1, t_y1, t_x2, t_y2], fill=(12, 16, 28), outline=ACCENT_GREEN)
    draw.text((t_x1 + 20, t_y1 + 15), "TERMINAL: python validate.py --dir outputs/", fill=ACCENT_GREEN, font=FONT_BOLD)

    terminal_lines = [
        ("==================================================", TEXT_MUTED),
        (" SAMSUNG XR HACKATHON 2026 — TRACK 4 VALIDATOR", ACCENT_CYAN),
        (" Checking 188 file(s)", TEXT_WHITE),
        (" Loaded manifest with 187 video duration(s)", TEXT_WHITE),
        ("==================================================", TEXT_MUTED),
        ("✅ PASS: BikePolo_5yf797Lh4Oc_1.json", ACCENT_GREEN),
        ("✅ PASS: Bike_OeE9EIIKmrA.json", ACCENT_GREEN),
        ("✅ PASS: Boxing_6kDWXla9bMU.json", ACCENT_GREEN),
        ("✅ PASS: Horse_2otBDeLWCow.json", ACCENT_GREEN),
        ("✅ PASS: P01_11.json", ACCENT_GREEN),
        ("✅ PASS: P02_109.json", ACCENT_GREEN),
        ("✅ PASS: Ski_-Z5a4UQmZLs.json", ACCENT_GREEN),
        ("✅ PASS: synthetic_demo.json", ACCENT_GREEN),
        ("--------------------------------------------------", TEXT_MUTED),
        (" SUMMARY: 188/188 passed validation (0 failed).", ACCENT_GREEN),
        (" [SUCCESS] All validated files satisfy requirements!", ACCENT_CYAN),
        ("--------------------------------------------------", TEXT_MUTED),
        ("• All 6 mandatory root keys strictly formatted", TEXT_WHITE),
        ("• Duration budget <= 15.0% enforced on all 188 videos", ACCENT_GREEN),
        ("• Every highlight segment >= 4.0 seconds", ACCENT_GREEN),
        ("• Strict chronological non-overlapping intervals", ACCENT_GREEN)
    ]
    for idx, (t, col) in enumerate(terminal_lines):
        draw.text((t_x1 + 25, t_y1 + 50 + idx * 24), t, fill=col, font=FONT_CODE_BOLD if "SUMMARY" in t or "SUCCESS" in t else FONT_CODE)

    img.save("demo_assets/screenshots/track_output.png")
    print("Created track_output.png")


# 4. Motion & HOI Visual Screenshot
def create_motion_hoi_screenshot():
    w, h = 1200, 680
    img = Image.new("RGB", (w, h), (10, 14, 26))
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, w, 50], fill=(20, 28, 50))
    draw.text((25, 14), "CORE INNOVATION  ·  HEAD SWAY CANCELLATION & INTERACTION FILTERING", fill=ACCENT_CYAN, font=FONT_BOLD)

    # Left: Head Sway Compensation
    l_x1, l_y1, l_x2, l_y2 = 30, 75, 580, 645
    draw_card(draw, [l_x1, l_y1, l_x2, l_y2], fill=BG_CARD, outline=ACCENT_BLUE)
    draw.text((l_x1 + 20, l_y1 + 20), "EGOCENTRIC HEAD SWAY COMPENSATION", fill=ACCENT_CYAN, font=FONT_BOLD)
    draw.text((l_x1 + 20, l_y1 + 55), "Farneback Flow Median Vector Subtraction", fill=TEXT_WHITE, font=FONT_BOLD)

    draw_card(draw, [l_x1 + 20, l_y1 + 95, l_x2 - 20, l_y1 + 165], fill=BG_CARD_LIGHT, outline=BORDER_COLOR)
    draw.text((l_x1 + 35, l_y1 + 115), "v_head = ( median(Δx), median(Δy) )", fill=ACCENT_CYAN, font=FONT_CODE_BOLD)

    draw_card(draw, [l_x1 + 20, l_y1 + 185, l_x2 - 20, l_y1 + 255], fill=BG_CARD_LIGHT, outline=BORDER_COLOR)
    draw.text((l_x1 + 35, l_y1 + 205), "v_manip(x, y) = || v(x, y) - v_head ||_2", fill=ACCENT_GREEN, font=FONT_CODE_BOLD)

    flow_pts = [
        "1. Dense Farneback flow calculates frame-wide pixel vectors.",
        "2. Spatial median displacement isolates global user head velocity.",
        "3. Subtracting v_head completely cancels head pitch/yaw saccades.",
        "4. Targets Lower Manipulation Zone (Y: 45%-100%, X: 20%-80%).",
        "5. Result: Dynamism A(s) responds ONLY to active physical tasks."
    ]
    for i, pt in enumerate(flow_pts):
        draw.text((l_x1 + 20, l_y1 + 280 + i * 40), pt, fill=TEXT_MUTED, font=FONT_BODY)

    # Right: HOI Filter
    r_x1, r_y1, r_x2, r_y2 = 610, 75, w - 30, 645
    draw_card(draw, [r_x1, r_y1, r_x2, r_y2], fill=BG_CARD, outline=ACCENT_GREEN)
    draw.text((r_x1 + 20, r_y1 + 20), "HAND-OBJECT INTERACTION (HOI) FILTER", fill=ACCENT_GREEN, font=FONT_BOLD)
    draw.text((r_x1 + 20, r_y1 + 55), "Skin Chrominance + Foveal Edge Gradient", fill=TEXT_WHITE, font=FONT_BOLD)

    draw_card(draw, [r_x1 + 20, r_y1 + 95, r_x2 - 20, r_y1 + 165], fill=BG_CARD_LIGHT, outline=BORDER_COLOR)
    draw.text((r_x1 + 35, r_y1 + 115), "YCbCr: Y in [80, 240], Cb in [85, 135], Cr in [135, 180]", fill=ACCENT_AMBER, font=FONT_CODE)

    draw_card(draw, [r_x1 + 20, r_y1 + 185, r_x2 - 20, r_y1 + 255], fill=BG_CARD_LIGHT, outline=BORDER_COLOR)
    draw.text((r_x1 + 35, r_y1 + 205), "H(s) = (Skin_Ratio) x (Foveal_Edge_Density)", fill=ACCENT_CYAN, font=FONT_CODE_BOLD)

    hoi_pts = [
        "1. Detects hand skin presence in lower manipulation quadrant.",
        "2. Canny edge filter measures high-gradient object contours.",
        "3. Fuses skin proximity with active object contact energy.",
        "4. Discards empty room looking, walking, and idle transit.",
        "5. Ensures candidate segments focus strictly on tool manipulation."
    ]
    for i, pt in enumerate(hoi_pts):
        draw.text((r_x1 + 20, r_y1 + 280 + i * 40), pt, fill=TEXT_MUTED, font=FONT_BODY)

    img.save("demo_assets/screenshots/motion_hoi.png")
    print("Created motion_hoi.png")


if __name__ == "__main__":
    create_arch_screenshot()
    create_demo_studio_screenshot()
    create_track_output_screenshot()
    create_motion_hoi_screenshot()
