"""Generates realistic synthetic egocentric video clips for testing and offline demonstration.
Simulates an egocentric kitchen task with idle segments, object manipulations, and hand interactions."""
import os
import sys
import numpy as np
import cv2


def create_synthetic_egocentric_video(
    output_path: str = "uploads/synthetic_demo.mp4",
    duration_sec: int = 40,
    fps: int = 15,
    width: int = 640,
    height: int = 480
):
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    total_frames = duration_sec * fps
    # Ground truth active manipulation intervals in seconds
    active_windows = [
        (4.0, 9.0, "cut", "knife"),
        (14.0, 19.0, "pour", "cup"),
        (25.0, 31.0, "wash", "pan")
    ]

    rng = np.random.default_rng(42)

    # Kitchen counter background color palettes
    bg_counter = np.array([210, 220, 225], dtype=np.uint8)  # Marble counter
    cutting_board = (120, 160, 200)  # Wood board

    print(f"Generating synthetic video: {output_path} ({duration_sec}s at {fps} fps)...")

    for f in range(total_frames):
        t = f / float(fps)

        # Base frame: counter surface with mild natural head sway
        sway_x = int(6.0 * np.sin(t * 1.5))
        sway_y = int(3.0 * np.cos(t * 1.2))

        frame = np.full((height, width, 3), bg_counter, dtype=np.uint8)

        # Counter grain texture
        noise = (rng.random((height, width)) * 12).astype(np.uint8)
        frame = cv2.add(frame, cv2.merge([noise] * 3))

        # Cutting board / prep station in center
        board_x1 = 180 + sway_x
        board_y1 = 200 + sway_y
        board_x2 = 460 + sway_x
        board_y2 = 420 + sway_y
        cv2.rectangle(frame, (board_x1, board_y1), (board_x2, board_y2), cutting_board, -1)
        cv2.rectangle(frame, (board_x1, board_y1), (board_x2, board_y2), (80, 120, 160), 3)

        # Check if current timestamp is inside an active interaction window
        active_action = None
        for a_start, a_end, verb, noun in active_windows:
            if a_start <= t < a_end:
                active_action = (verb, noun, a_start, a_end)
                break

        if active_action:
            verb, noun, _, _ = active_action
            # Hand enters frame and manipulates object
            hand_progress = np.sin((t * 4.0))

            # Left hand (holding object)
            lh_x = int(240 + 20 * hand_progress + sway_x)
            lh_y = int(340 + 10 * np.cos(t * 3.0) + sway_y)
            # Skin tone color in BGR (approx 140, 170, 215)
            cv2.circle(frame, (lh_x, lh_y), 38, (140, 175, 225), -1)
            cv2.circle(frame, (lh_x, lh_y), 38, (110, 145, 195), 2)

            # Object being manipulated (e.g. pan, knife, cup)
            if noun == "knife":
                # Cutting motion
                kx = int(340 + 40 * hand_progress + sway_x)
                ky = int(310 + 15 * np.sin(t * 8.0) + sway_y)
                cv2.line(frame, (kx, ky), (kx + 60, ky - 40), (80, 80, 90), 8)
                cv2.circle(frame, (kx + 70, ky - 45), 36, (140, 175, 225), -1)  # Right hand
            elif noun == "cup":
                # Pouring motion
                cx = int(320 + sway_x)
                cy = int(290 + sway_y)
                cv2.rectangle(frame, (cx - 20, cy - 35), (cx + 20, cy + 35), (200, 100, 50), -1)
                cv2.circle(frame, (cx + 35, cy), 35, (140, 175, 225), -1)  # Right hand
            else:
                # Washing / sponge
                wx = int(320 + 35 * np.cos(t * 6.0) + sway_x)
                wy = int(320 + 25 * np.sin(t * 6.0) + sway_y)
                cv2.circle(frame, (wx, wy), 28, (60, 180, 240), -1)
                cv2.circle(frame, (wx + 30, wy), 35, (140, 175, 225), -1)  # Right hand

            # Status label on frame (simulating camera timestamp/telemetry)
            cv2.putText(frame, f"EGOCENTRIC CAMERA: {t:.1f}s", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 50, 50), 2)
        else:
            # Idle footage - natural head drift, no hands in interaction zone
            cv2.putText(frame, f"EGOCENTRIC CAMERA: {t:.1f}s [IDLE]", (20, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (120, 120, 120), 2)

        writer.write(frame)

    writer.release()
    print(f"Generated synthetic egocentric test video: {output_path} ({os.path.getsize(output_path)} bytes)")
    return output_path, active_windows


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "uploads/synthetic_demo.mp4"
    create_synthetic_egocentric_video(out)

