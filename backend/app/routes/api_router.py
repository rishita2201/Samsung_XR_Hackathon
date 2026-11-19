"""REST API Router for MOMENTIQ Video Understanding Platform."""
import os
import sys
import shutil
import glob
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Request, Response
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from pydantic import BaseModel

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ..services.video_service import VideoService
from ..schemas.video_schemas import PipelineProgress
from validate import validate_json_file
from backend.tests.make_synthetic_demo import create_synthetic_egocentric_video

router = APIRouter(prefix="/api")
service = VideoService()


class UpdateHighlightRequest(BaseModel):
    highlights: List[Dict[str, Any]]
    render_video: bool = True


@router.get("/system/status")
def get_system_status():
    """Returns technical environment diagnostic and model readiness."""
    clip_pt = os.path.join(service.weights_dir, "clip_vitb32.pt")
    has_clip = os.path.exists(clip_pt)
    classes_json = os.path.join(service.weights_dir, "supported_classes.json")
    has_classes = os.path.exists(classes_json)

    return {
        "status": "ready",
        "semantic_clip_ready": has_clip,
        "clip_checkpoint_size_mb": round(os.path.getsize(clip_pt) / (1024 * 1024), 2) if has_clip else 0,
        "classes_vocabulary_ready": has_classes,
        "ffmpeg_available": True,
        "model_architecture": "CLIP ViT-B/32 QuickGELU + Farneback Optical Flow + HOI Spatial Filter",
        "supported_datasets": ["EPIC-KITCHENS-100", "FPVSum"]
    }


@router.post("/upload")
async def upload_video(
    file: Optional[UploadFile] = File(None),
    generate_synthetic: Optional[bool] = Form(False)
):
    """Upload first-person MP4 video or generate a test egocentric scenario."""
    if generate_synthetic:
        synth_id = "synthetic_demo"
        synth_path = os.path.join(service.upload_dir, f"{synth_id}.mp4")
        create_synthetic_egocentric_video(synth_path, duration_sec=45, fps=15)
        return {
            "video_id": synth_id,
            "filename": f"{synth_id}.mp4",
            "message": "Synthetic egocentric video generated successfully",
            "is_synthetic": True
        }

    if not file:
        raise HTTPException(status_code=400, detail="No video file provided.")

    if not file.filename.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
        raise HTTPException(status_code=400, detail="Only MP4/video files are supported.")

    base_name = os.path.splitext(file.filename)[0]
    safe_name = "".join(c if c.isalnum() or c in "_-" else "_" for c in base_name)
    target_path = os.path.join(service.upload_dir, f"{safe_name}.mp4")

    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "video_id": safe_name,
        "filename": f"{safe_name}.mp4",
        "file_size_mb": round(os.path.getsize(target_path) / (1024 * 1024), 2),
        "message": "Upload successful"
    }


@router.post("/analyze/{video_id}")
def start_video_analysis(video_id: str):
    """Trigger the MOMENTIQ video understanding pipeline."""
    video_path = os.path.join(service.upload_dir, f"{video_id}.mp4")
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail=f"Video '{video_id}' not found.")

    service.start_analysis_async(video_id, video_path)
    return {"message": "Analysis started", "video_id": video_id}


@router.get("/progress/{video_id}", response_model=PipelineProgress)
def get_analysis_progress(video_id: str):
    """Get live processing state and percentage."""
    return service.get_progress(video_id)


@router.get("/videos/{video_id}")
def get_video_details(video_id: str):
    """Fetch complete analysis, actions, highlights, timeline points, and metadata."""
    res = service.get_analysis_result(video_id)
    if not res:
        raise HTTPException(status_code=404, detail="Analysis results not found.")
    return res


@router.get("/videos")
def list_videos():
    """List all available videos and their status."""
    return service.list_all_videos()


@router.post("/highlight/update/{video_id}")
def update_highlights(video_id: str, req: UpdateHighlightRequest):
    """Update highlight selection from the interactive editor."""
    try:
        updated = service.recompute_custom_highlights(video_id, req.highlights, req.render_video)
        return {"message": "Highlights updated successfully", "data": updated}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stream/{video_type}/{video_id}")
def stream_video(video_type: str, video_id: str, request: Request):
    """Stream original or highlight video with HTTP 206 byte-range seeking support."""
    if video_type == "highlight":
        file_path = os.path.join(service.highlight_dir, f"{video_id}_highlight.mp4")
    else:
        file_path = os.path.join(service.upload_dir, f"{video_id}.mp4")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Video file not found: {file_path}")

    file_size = os.path.getsize(file_path)
    range_header = request.headers.get("Range")

    if range_header:
        # Parse range header e.g. "bytes=0-1000"
        byte1, byte2 = 0, None
        match = range_header.replace("bytes=", "").split("-")
        if match[0]:
            byte1 = int(match[0])
        if len(match) > 1 and match[1]:
            byte2 = int(match[1])

        length = file_size - byte1 if byte2 is None else byte2 - byte1 + 1
        byte2 = byte1 + length - 1

        def iterfile():
            with open(file_path, "rb") as f:
                f.seek(byte1)
                remaining = length
                chunk_size = 1024 * 1024
                while remaining > 0:
                    read_len = min(remaining, chunk_size)
                    data = f.read(read_len)
                    if not data:
                        break
                    remaining -= len(data)
                    yield data

        headers = {
            "Content-Range": f"bytes {byte1}-{byte2}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(length),
            "Content-Type": "video/mp4",
        }
        return StreamingResponse(iterfile(), status_code=206, headers=headers)

    return FileResponse(file_path, media_type="video/mp4")


@router.get("/download/json/{video_id}")
def download_json(video_id: str):
    """Download official Samsung schema JSON."""
    json_path = os.path.join(service.json_dir, f"{video_id}.json")
    if not os.path.exists(json_path):
        raise HTTPException(status_code=404, detail="JSON output not found.")
    return FileResponse(json_path, media_type="application/json", filename=f"{video_id}.json")


@router.get("/download/highlight/{video_id}")
def download_highlight_video(video_id: str):
    """Download compiled MP4 highlight video."""
    video_path = os.path.join(service.highlight_dir, f"{video_id}_highlight.mp4")
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Highlight video not found.")
    return FileResponse(video_path, media_type="video/mp4", filename=f"{video_id}_highlight.mp4")


@router.post("/validate")
def run_validation():
    """Run the official Samsung Track 4 validator over the outputs directory."""
    json_files = sorted(glob.glob(os.path.join(service.json_dir, "*.json")))
    results = []
    overall_valid = True

    for jf in json_files:
        exp_id = os.path.splitext(os.path.basename(jf))[0]
        errs = validate_json_file(jf, exp_id)
        is_pass = len(errs) == 0
        if not is_pass:
            overall_valid = False
        results.append({
            "video_id": exp_id,
            "filename": os.path.basename(jf),
            "valid": is_pass,
            "errors": errs
        })

    return {
        "overall_valid": overall_valid,
        "total_files": len(json_files),
        "passed_count": sum(1 for r in results if r["valid"]),
        "failed_count": sum(1 for r in results if not r["valid"]),
        "details": results
    }

