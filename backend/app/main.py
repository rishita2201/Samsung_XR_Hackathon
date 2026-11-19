"""FastAPI Backend Entry Point for MOMENTIQ."""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .routes.api_router import router as api_router

app = FastAPI(
    title="MOMENTIQ API",
    description="Intelligent First-Person Video Understanding & Highlight Generation API — Samsung XR Hackathon 2026",
    version="1.0.0"
)

# Enable CORS for local development and frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure PROJECT_ROOT points to workspace root (cheese_project)
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

# Mount thumbnails directory if present
thumbs_dir = os.path.abspath(os.path.join(PROJECT_ROOT, "outputs", "thumbnails"))
os.makedirs(thumbs_dir, exist_ok=True)
app.mount("/thumbnails", StaticFiles(directory=thumbs_dir), name="thumbnails")

# Mount API router
app.include_router(api_router)

# Mount compiled frontend dist if available for unified single-server deployment
frontend_dist = os.path.abspath(os.path.join(PROJECT_ROOT, "frontend", "dist"))
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/")
    def serve_frontend_root():
        index_file = os.path.join(frontend_dist, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"status": "MOMENTIQ backend operational"}

    @app.get("/{full_path:path}")
    def serve_frontend_spa(full_path: str):
        # Serve index.html for SPA routing if not api
        if not full_path.startswith("api"):
            index_file = os.path.join(frontend_dist, "index.html")
            if os.path.exists(index_file):
                return FileResponse(index_file)
        return {"status": "MOMENTIQ backend operational"}
else:
    @app.get("/")
    def root():
        return {
            "project": "MOMENTIQ",
            "description": "Action-Aware Video Summarization Platform",
            "hackathon": "Samsung XR Hackathon 2026 — Track 4",
            "status": "operational",
            "docs_url": "/docs"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
