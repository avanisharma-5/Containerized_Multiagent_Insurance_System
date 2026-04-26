from __future__ import annotations

from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import BASE_DIR, load_settings
from .crew_system import run_insurance_agents
from .image_gen import generate_insurance_image
from .comparison_routes import router as comparison_router
from .models import (
    HandoffEvent,
    ImageRequest,
    ImageResponse,
    QueryRequest,
    UploadResponse,
    WorkflowResponse,
)


app = FastAPI(title="Insurance Multi-Agent API", version="2.0.0")
settings = load_settings()
uploads_dir = (BASE_DIR / settings.uploads_dir).resolve()
uploads_dir.mkdir(parents=True, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount comparison router AFTER app is created                      # ← NEW
app.include_router(comparison_router, prefix="/comparison", tags=["comparison"])


@app.get("/")
def root() -> dict:
    return {
        "message": "Insurance multi-agent backend is running.",
        "health": "/health",
        "workflow_run": "/workflow/run",
        "file_upload": "/files/upload",
        "image_generate": "/images/generate",
        "comparison": "/comparison/run",
    }


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/files/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)) -> UploadResponse:
    file_id = str(uuid4())
    safe_name = Path(file.filename or "upload.bin").name
    target = uploads_dir / f"{file_id}__{safe_name}"
    content = await file.read()
    target.write_bytes(content)
    return UploadResponse(
        file_id=file_id,
        filename=safe_name,
        content_type=file.content_type,
        size=len(content),
    )


@app.delete("/files/{file_id}")
def delete_file(file_id: str) -> dict:
    deleted = 0
    for match in uploads_dir.glob(f"{file_id}__*"):
        try:
            match.unlink(missing_ok=True)
            deleted += 1
        except Exception:
            continue
    return {"deleted": deleted}


@app.post("/workflow/run", response_model=WorkflowResponse)
def run_workflow(request: QueryRequest) -> WorkflowResponse:
    session_id = str(uuid4())  # Generate temporary session ID

    answer = run_insurance_agents(
        question=request.question,
        session_id=session_id,
        file_ids=request.file_ids,
    )

    image_url = None
    if request.generate_image:
        try:
            image_url = generate_insurance_image(request.question)
        except Exception:
            image_url = None

    status = "completed"
    if answer.startswith("I can help with insurance questions"):
        status = "blocked"
    elif "could not find grounded" in answer.lower():
        status = "no_info"

    state = {
        "request_id": str(uuid4()),
        "question": request.question,
        "retrieved_facts": [],
        "draft": None,
        "final_output": answer,
        "status": status,
    }
    handoff = HandoffEvent(
        from_agent="Insurance Researcher",
        to_agent="Insurance Writer",
        reason="Research evidence was gathered and then synthesized.",
        payload_preview=request.question[:80],
    )
    return WorkflowResponse(
        request_id=state["request_id"],
        session_id=session_id,
        status=status,
        handoffs=[handoff],
        state=state,
        image_url=image_url,
    )


@app.post("/workflow/run-inline", response_model=WorkflowResponse)
async def run_workflow_inline(
    question: str = Form(...),
    generate_image: bool = Form(False),
    file: UploadFile | None = File(None),
) -> WorkflowResponse:
    session_id = str(uuid4())  # Generate temporary session ID

    inline_pdf: tuple[str, bytes] | None = None
    if file is not None:
        content = await file.read()
        inline_pdf = (Path(file.filename or "upload.pdf").name, content)

    answer = run_insurance_agents(
        question=question,
        session_id=session_id,
        file_ids=[],
        inline_pdf=inline_pdf,
    )

    image_url = None
    if generate_image:
        try:
            image_url = generate_insurance_image(question)
        except Exception:
            image_url = None

    status = "completed"
    if answer.startswith("I can help with insurance questions"):
        status = "blocked"
    elif "could not find grounded" in answer.lower():
        status = "no_info"

    state = {
        "request_id": str(uuid4()),
        "question": question,
        "retrieved_facts": [],
        "draft": None,
        "final_output": answer,
        "status": status,
    }
    handoff = HandoffEvent(
        from_agent="Insurance Researcher",
        to_agent="Insurance Writer",
        reason="Research evidence was gathered and then synthesized.",
        payload_preview=question[:80],
    )
    return WorkflowResponse(
        request_id=state["request_id"],
        session_id=session_id,
        status=status,
        handoffs=[handoff],
        state=state,
        image_url=image_url,
    )


@app.post("/images/generate", response_model=ImageResponse)
def generate_image(payload: ImageRequest) -> ImageResponse:
    try:
        url = generate_insurance_image(payload.prompt)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ImageResponse(image_url=url)


@app.get("/images/{filename}")
def serve_image(filename: str):
    image_path = (BASE_DIR / "data" / "generated_images" / filename).resolve()
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(path=str(image_path), media_type="image/png")