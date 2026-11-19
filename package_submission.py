#!/usr/bin/env python
"""Creates the final Samsung XR Hackathon Track 4 submission bundle.
Usage:
    python package_submission.py --team-id CollegeName_TeamName
Outputs:
    CollegeName_TeamName.zip (containing the validated TEAM_ID submission folder)
"""
import argparse
import os
import shutil
import subprocess
import sys
import zipfile


def package(team_name: str, src_dir: str = "TEAM_ID"):
    if not os.path.exists(src_dir):
        print(f"[ERROR] Source submission folder '{src_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    print(f"==================================================")
    print(f" SAMSUNG XR HACKATHON 2026 — SUBMISSION PACKAGER")
    print(f" Team Name: {team_name}")
    print(f" Source:    {src_dir}/")
    print(f"==================================================\n")

    # 1. Run validator on outputs first
    val_script = os.path.join(src_dir, "validate.py")
    out_dir = os.path.join(src_dir, "outputs")
    manifest = os.path.join("datasets", "manifest.csv")

    cmd = [sys.executable, val_script, "--dir", out_dir]
    if os.path.exists(manifest):
        cmd.extend(["--manifest", manifest])

    print("Step 1: Running validation check...")
    ret = subprocess.call(cmd)
    if ret != 0:
        print("\n[ERROR] Validation failed. Fix errors before bundling.", file=sys.stderr)
        sys.exit(1)

    # 2. Create zip archive
    zip_filename = f"{team_name}.zip"
    print(f"\nStep 2: Packaging into '{zip_filename}'...")

    with zipfile.ZipFile(zip_filename, "w") as z:
        for root, dirs, files in os.walk(src_dir):
            if "__pycache__" in root:
                continue
            for f in files:
                if f.endswith(".pyc") or f.endswith(".log"):
                    continue
                fpath = os.path.join(root, f)
                rel_path = os.path.relpath(fpath, os.path.dirname(src_dir) if os.path.dirname(src_dir) else ".")
                compress_mode = zipfile.ZIP_STORED if f.endswith(".pt") else zipfile.ZIP_DEFLATED
                z.write(fpath, rel_path, compress_type=compress_mode)

    size_mb = os.path.getsize(zip_filename) / (1024 * 1024)
    print(f"\n[SUCCESS] Package successfully created: {zip_filename} ({size_mb:.1f} MB)")
    print(f"Ready for upload to Samsung Hackathon submission form!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--team-id", default="CollegeName_TeamName", help="Your official team name (e.g. IITB_Visionaries)")
    parser.add_argument("--src", default="TEAM_ID", help="Path to TEAM_ID directory")
    args = parser.parse_args()
    package(args.team_id, args.src)
