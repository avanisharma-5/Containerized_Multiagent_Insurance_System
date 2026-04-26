from __future__ import annotations

import traceback
import uuid
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .comparison_agents import ComparisonResult, PolicyComparisonPipeline
from .config import BASE_DIR, load_settings

router = APIRouter()

settings = load_settings()
_uploads_dir = (BASE_DIR / settings.uploads_dir).resolve()
_uploads_dir.mkdir(parents=True, exist_ok=True)
_charts_dir = (BASE_DIR / "data" / "comparison_charts").resolve()
_charts_dir.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic models
# ─────────────────────────────────────────────────────────────────────────────

class PolicyData(BaseModel):
    policy_name: str
    premium: float
    coverage: float
    claim_ratio: float


class ComparisonResponse(BaseModel):
    comparison_id: str
    policy_a: dict
    policy_b: dict
    report: str
    status: str = "completed"


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _save_upload(filename: str, content: bytes) -> str:
    fid = str(uuid.uuid4())
    safe_name = Path(filename or "upload.pdf").name
    target = _uploads_dir / f"{fid}__{safe_name}"
    target.write_bytes(content)
    return str(target)


def _extract_policy_data(raw: dict, key: str) -> PolicyData:
    p = raw.get(key, {})
    return PolicyData(
        policy_name=str(p.get("policy_name", key)),
        premium=float(p.get("premium", 0) or 0),
        coverage=float(p.get("coverage", 0) or 0),
        claim_ratio=float(p.get("claim_ratio", 0) or 0),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/health")
def comparison_health() -> dict:
    return {"status": "ok", "feature": "policy_comparison"}


@router.post("/run", response_model=ComparisonResponse)
async def run_comparison(
    pdf_a: UploadFile = File(...),
    pdf_b: UploadFile = File(...),
) -> ComparisonResponse:
    """
    Accepts two PDF uploads (multipart fields: pdf_a, pdf_b).
    Runs Analyzer → Plotter → Writer pipeline and returns structured JSON.
    """
    # ── validate ──────────────────────────────────────────────────────────────
    for label, f in [("pdf_a", pdf_a), ("pdf_b", pdf_b)]:
        if not f.filename:
            raise HTTPException(400, detail=f"{label}: no filename received.")
        if not f.filename.lower().endswith(".pdf"):
            raise HTTPException(400, detail=f"{label} must be a PDF file, got: {f.filename}")

    # ── read & save uploads ───────────────────────────────────────────────────
    content_a = await pdf_a.read()
    content_b = await pdf_b.read()

    if not content_a:
        raise HTTPException(400, detail="pdf_a is empty.")
    if not content_b:
        raise HTTPException(400, detail="pdf_b is empty.")

    path_a = _save_upload(pdf_a.filename, content_a)
    path_b = _save_upload(pdf_b.filename, content_b)

    comparison_id = str(uuid.uuid4())

    # ── run pipeline ──────────────────────────────────────────────────────────
    try:
        pipeline = PolicyComparisonPipeline()
        result: ComparisonResult = pipeline.run(pdf_path_a=path_a, pdf_path_b=path_b)
        
        # Clean up uploaded files after processing
        try:
            Path(path_a).unlink(missing_ok=True)
            Path(path_b).unlink(missing_ok=True)
        except Exception:
            pass  # Ignore cleanup errors
            
    except Exception as exc:
        # Print full traceback to uvicorn console so you can see the real error
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline error: {type(exc).__name__}: {exc}",
        ) from exc

    return ComparisonResponse(
        comparison_id=comparison_id,
        policy_a=result.structured_data.get("policy_a", {}),
        policy_b=result.structured_data.get("policy_b", {}),
        report=result.report,
        status="completed",
    )


@router.get("/charts/{filename}")
def serve_chart(filename: str):
    # Prevent path traversal
    chart_path = (_charts_dir / Path(filename).name).resolve()
    if not chart_path.exists():
        raise HTTPException(status_code=404, detail=f"Chart not found: {filename}")
    return FileResponse(path=str(chart_path), media_type="image/png")